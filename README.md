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

### Setup
1. Create and activate a virtual environment:
   ```bash
   # Create virtual environment
   python -m venv venv

   # Activate virtual environment
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Use `serial_midi_bridge.py`
    ```bash
    python serial_midi_bridge.py --device {serial device name} --midi_in {midi input device name} --midi_out {midi output device name}

    # If you want to list available devices, use `-l` option
    python serial_midi_bridge.py -l
    ```

### Virtual MIDI Setup
For instructions on setting up a virtual MIDI device, see [Ableton's "Setting up a virtual MIDI bus"](https://help.ableton.com/hc/en-us/articles/209774225-Setting-up-a-virtual-MIDI-bus) guide

### Dependencies
- Python 3
- [python-rtmidi](https://pypi.org/project/python-rtmidi/)
- [PySerial](https://pypi.org/project/pyserial/)

## Quickstart
### macOS
```bash
python3 serial_midi_bridge.py -d /dev/tty.usbserial -i "IAC Driver Bus 1" -o "IAC Driver Bus 2"
```

### Windows
```bash
python.exe .\serial_midi_bridge.py -d COM4 -i "loopMIDI Port IN 0" -o "loopMIDI Port OUT 2"
```

## Usage
```
$ python3 serial_midi_bridge.py -h
usage: serial_midi_bridge.py [-h] -d DEVICE [-b BAUD]
                             [--midi_in {IAC Driver Bus 1,IAC Driver Bus 2,GarageBand Virtual In}]
                             [--midi_out {IAC Driver Bus 1,IAC Driver Bus 2,GarageBand Virtual In}] [--debug]

Serial to MIDI bridge

options:
  -h, --help            show this help message and exit
  -d DEVICE, --device DEVICE
                        Serial port name
  -b BAUD, --baudrate BAUD
                        baud rate
  --midi_in MIDI_IN     MIDI input device name
  --midi_out MIDI_OUT   MIDI output device name
  -l, --list            List available USB devices and MIDI devices
  -v, --verbose         Print all MIDI messages
```

To run the bridge, `device`, `baudrate`, `midi_in`, and `midi_out` are required. You can use `--list` (or `-l`) option to list available devices.

## Issues
1. **MIDI or Serial Device Not Found**
   - Ensure your devices are properly connected and recognized by your system
   - Use the `-l` option to list available devices
   - Verify the exact names of your devices

2. **MIDI Messages Not Being Sent/Received**
   - Enable verbose mode with `-v` flag to see all MIDI messages
   - Check if your MIDI devices are properly configured
   - Verify that your MIDI routing is set up correctly

3. **Baud Rate Mismatch**
   - Ensure the baud rate matches your device's configuration (default is 9600)
   - Use `-v` flag to see all MIDI messages; if they are are all `\x00` the baud rate is most likely incorrect

If you find a bug, please create an issue and contributions are always welcome!







