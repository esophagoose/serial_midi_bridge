# Serial MIDI Bridge

A lightweight Python-based Serial to MIDI bridge that enables devices to communicate via MIDI-over-serial

## Features
- Low latency (< 5ms) bidirectional MIDI message processing
- Cross-platform compatibility (Windows, macOS, Linux)
- Support for standard MIDI messages
- Simple command-line interface
- Auto-reconnects to serial device if device drops out
- No threading, asyncio, or event loops


## Installation
```bash
pip3 install serial-midi-bridge
```

## Quickstart
### macOS
```bash
serial-midi-bridge -d /dev/tty.usbserial -i "IAC Driver Bus 1" -o "IAC Driver Bus 2"
```

### Windows
```bash
serial-midi-bridge -d COM4 -i "loopMIDI Port IN 0" -o "loopMIDI Port OUT 2"
```

## Virtual MIDI Setup
For instructions on setting up a virtual MIDI device, see [Ableton's "Setting up a virtual MIDI bus"](https://help.ableton.com/hc/en-us/articles/209774225-Setting-up-a-virtual-MIDI-bus) guide

## Usage
```
usage: serial-midi-bridge [-h] [-d DEVICE] [-b BAUDRATE]
                          [-i Input MIDI device]
                          [-o Output MIDI device] [-v] [-l]

Serial to MIDI bridge

options:
  -h, --help            show this help message and exit
  -d, --device DEVICE   Serial port name
  -b, --baudrate BAUDRATE
                        baud rate
  -i, --midi_in         Input MIDI device
  -o, --midi_out        Output MIDI device
  -v, --verbose         Print all MIDI messages
  -l, --list            List available USB devices and MIDI devices
```
To run the bridge, `device`, `baudrate`, `midi_in`, and `midi_out` are required. You can use `--list` (or `-l`) option to list available devices.

## Issues
1. **MIDI or Serial Device Not Found**
   - Ensure your devices are properly connected and recognized by your system
   - Use the `-l` option to list available devices

2. **MIDI Messages Not Being Sent/Received**
   - Ensure the baud rate matches your device's configuration (default is 9600)
   - Enable verbose mode with `-v` flag to see all MIDI messages
     - If messages are all `\x00`, the baud rate is most likely incorrect
     - If no messages are being sent/received, it is likely a hardware issue

If you find a bug, please create an issue and contributions are always welcome!







