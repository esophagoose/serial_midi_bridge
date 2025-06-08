import argparse
import enum
import logging
import os
import time
from typing import Optional

import rtmidi
import serial
import serial.tools.list_ports as list_ports


class SystemMessage(enum.IntEnum):
    SYSEX = 0xF0
    TIME_CODE = 0xF1
    SONG_POSITION = 0xF2
    SONG_SELECT = 0xF3
    TUNE_REQUEST = 0xF6
    SYSEX_END = 0xF7


class ChannelMessage(enum.IntEnum):
    # Also called Data Messages
    NOTE_OFF = 0x80
    NOTE_ON = 0x90
    POLY_PRESSURE = 0xA0
    CONTROL_CHANGE = 0xB0
    PROGRAM_CHANGE = 0xC0
    CHANNEL_PRESSURE = 0xD0
    PITCH_BEND = 0xE0


is_status_byte = lambda byte: byte >= 0x80
is_data_byte = lambda byte: byte < 0x80


def bytes_to_hex(message: bytes) -> str:
    hex_str = " ".join(f"{byte:02X}" for byte in message)
    return f"[{hex_str}]"


class SerialMidiBridge:
    def __init__(self, device_name: str, baudrate: int, midi_in: str, midi_out: str):
        self.name = device_name
        self.baudrate = baudrate
        self.midi_in = rtmidi.MidiIn()
        self.midi_out = rtmidi.MidiOut()
        in_port = self.midi_in.get_ports().index(midi_in)
        out_port = self.midi_out.get_ports().index(midi_out)
        self.midi_in.open_port(in_port)
        self.midi_out.open_port(out_port)
        self.midi_in.ignore_types(sysex=False, timing=False, active_sense=False)
        self.midi_in.set_callback(lambda message, _: self.write(message))
        self._input_buffer = b""
        print(
            f"Starting bridge: {device_name} at {baudrate} baud with input {midi_in} and output {midi_out}"
        )

    def _get_system_message_length(self, status_byte: int) -> Optional[int]:
        if status_byte == SystemMessage.SYSEX:  # System exclusive
            index = self._input_buffer.find(SystemMessage.SYSEX_END)
            return None if index == -1 else index
        elif status_byte >= SystemMessage.TUNE_REQUEST:
            return 1
        elif status_byte in [SystemMessage.TIME_CODE, SystemMessage.SONG_SELECT]:
            return 2
        elif status_byte == SystemMessage.SONG_POSITION:
            return 3
        else:
            logging.error(f"Unknown system message: {status_byte}")
            return 1

    def get_valid_message(self) -> Optional[bytes]:
        if not self._input_buffer:
            return None
        status_byte = self._input_buffer[0]

        # Flush non-status bytes
        if not is_status_byte(status_byte):
            self._input_buffer = self._input_buffer[1:]
            return self.get_valid_message()
        # System messages
        if status_byte in SystemMessage:
            index = self._get_system_message_length(status_byte)
        else:
            # Handle channel messages
            status_byte = status_byte & 0xF0  # Strip channel number
            index = 3
            if status_byte in [
                ChannelMessage.PROGRAM_CHANGE,
                ChannelMessage.CHANNEL_PRESSURE,
            ]:
                index = 2
        if index is None or len(self._input_buffer) < index:
            return None
        message = self._input_buffer[:index]
        self._input_buffer = self._input_buffer[index:]
        return message

    def write(self, message: bytes) -> None:
        logging.debug(f"MIDI -> Serial: {bytes_to_hex(message)}")
        self.device.write(bytearray(message))

    def wait_for_device(self) -> None:
        while not os.path.exists(self.name):
            time.sleep(0.25)
        self.device = serial.Serial(self.name, self.baudrate, timeout=0.4)

    def run(self) -> None:
        self.device = serial.Serial(self.name, self.baudrate, timeout=0.4)

        while True:
            try:
                self._input_buffer += self.device.read()
                message = self.get_valid_message()
                if not message:
                    continue
                logging.debug(f"Serial -> MIDI: {bytes_to_hex(message)}")
                self.midi_out.send_message(message)
            except serial.serialutil.SerialException:
                print("Serial device disconnected! Waiting for reconnect ...")
                self.wait_for_device()
                print("Reconnected.")


def handle_args(parser: argparse.ArgumentParser) -> bool:
    args = parser.parse_args()
    if args.list:
        parser.print_usage()
        print("\nAvailable Serial Ports:")
        for port in list_ports.comports():
            print(f" - {port.device} : {port.description}")
        print("\nAvailable MIDI Input Devices:")
        for port in rtmidi.MidiIn().get_ports():
            print(f" - {port}")
        print("\nAvailable MIDI Output Devices:")
        for port in rtmidi.MidiOut().get_ports():
            print(f" - {port}")
        return False
    if args.device is None:
        parser.print_usage()
        print("\nNo serial port specified. Available ports:")
        for port in list_ports.comports():
            print(f" - {port.device} : {port.description}")
        return False
    if not os.path.exists(args.device):
        parser.print_usage()
        print("\nSerial port not found. Available ports:")
        for port in list_ports.comports():
            print(f" - {port.device} : {port.description}")
        return False
    return True


def main():
    in_ports = rtmidi.MidiIn().get_ports()
    out_ports = rtmidi.MidiOut().get_ports()
    parser = argparse.ArgumentParser(description="Serial to MIDI bridge")
    parser.add_argument("-d", "--device", help="Serial port name")
    parser.add_argument("-b", "--baudrate", type=int, default=9600, help="baud rate")
    parser.add_argument("-i", "--midi_in", type=str, choices=in_ports)
    parser.add_argument("-o", "--midi_out", type=str, choices=out_ports)
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Print all MIDI messages"
    )
    parser.add_argument(
        "-l",
        "--list",
        action="store_true",
        help="List available USB devices and MIDI devices",
    )
    args = parser.parse_args()
    ready = handle_args(parser)
    if not ready:
        exit(0)
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=level)
    bridge = SerialMidiBridge(args.device, args.baudrate, args.midi_in, args.midi_out)
    bridge.run()


if __name__ == "__main__":
    main()
