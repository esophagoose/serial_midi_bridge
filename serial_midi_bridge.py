import time
import collections
import logging
import argparse
import os

import rtmidi
import serial


class SerialMidiBridge:
    def __init__(self, device_name, baudrate, midi_in_name, midi_out_name, debug=False):
        self.name = device_name
        self.baudrate = baudrate
        self.input_queue = collections.deque()
        self.output_queue = collections.deque()

        self.midi_in = rtmidi.MidiIn()
        self.midi_out = rtmidi.MidiOut()
        in_port = self.midi_out.get_ports().index(midi_in_name)
        out_port = self.midi_out.get_ports().index(midi_out_name)
        self.midi_in.open_port(in_port)
        self.midi_out.open_port(out_port)
        self.midi_in.ignore_types(sysex=False, timing=False, active_sense=False)
        self.midi_in.set_callback(MidiInputHandler(self))

    def get_midi_length(self, message):
        opcode = message[0]
        if opcode >= 0xF4:
            return 1
        if opcode in [0xF1, 0xF3]:
            return 2
        if opcode == 0xF2:
            return 3
        if opcode == 0xF0:
            if message[-1] == 0xF7:
                return len(message)

        opcode = opcode & 0xF0
        if opcode in [0x80, 0x90, 0xA0, 0xB0, 0xE0]:
            return 3
        if opcode in [0xC0, 0xD0]:
            return 2

        return 100

    def write(self, message):
        logging.debug(f"MIDI -> Serial: {message}")
        self.device.write(bytearray(message))

    def wait_for_device(self):
        while not os.path.exists(self.name):
            time.sleep(0.25)
        self.device = serial.Serial(self.name, self.baudrate, timeout=0.4)

    def run(self):
        self.device = serial.Serial(self.name, self.baudrate, timeout=0.4)

        input_buffer = b""
        while True:
            try:
                input_buffer += self.device.read()
                if not input_buffer:
                    continue

                message_length = self.get_midi_length(input_buffer)
                if len(input_buffer) >= message_length:
                    logging.debug(f"Serial -> MIDI: {input_buffer}")
                    self.midi_out.send_message(input_buffer[:message_length])
                    input_buffer = input_buffer[message_length:]
            except serial.serialutil.SerialException:
                print("Serial device disconnected! Waiting for reconnect ...")
                self.wait_for_device()
                print("Reconnected.")


class MidiInputHandler(object):
    def __init__(self, bridge):
        self.bridge = bridge

    def __call__(self, event, data=None):
        message, _ = event
        self.bridge.write(message)


if __name__ == "__main__":
    in_ports = rtmidi.MidiOut().get_ports()
    out_ports = rtmidi.MidiOut().get_ports()
    parser = argparse.ArgumentParser(description="Serial to MIDI bridge")
    parser.add_argument("--serial_name", required=True, help="Serial port name")
    parser.add_argument("--baud", type=int, default=115200, help="baud rate")
    parser.add_argument("--midi_in", type=str, choices=in_ports, default=in_ports[0])
    parser.add_argument("--midi_out", type=str, choices=out_ports, default=out_ports[0])
    parser.add_argument("--debug", action="store_true", help="Print all MIDI messages")
    args = parser.parse_args()
    bridge = SerialMidiBridge(args.serial_name, args.baud, args.midi_in, args.midi_out)
    level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(level=level)
    bridge.run()
