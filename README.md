# <img src="https://github.com/astridos2go/PyCurrentWindow/blob/main/images/icon.svg" width="25px"> PyCurrentWindow
[![made-with-python](https://img.shields.io/badge/Made%20with-Python-blue.svg)](https://www.python.org/) [![license-mit](https://img.shields.io/github/license/astridos2go/pycurrentwindow?color=gre&label=License)](https://github.com/astridos2go/PyCurrentWindow/blob/main/LICENSE) [![latest-version](https://img.shields.io/github/v/release/astridos2go/pycurrentwindow?display_name=tag&include_prereleases&label=Version)](https://github.com/astridos2go/PyCurrentWindow/releases/latest) ![made-for-windows](https://img.shields.io/badge/Platform-Windows-blueviolet)


A python-based program that links with a CircuitPython board via serial, and reports the currently running program to it.

## :book: Background
I recently purchased the [Adafruit MacroPad RP2040](https://learn.adafruit.com/adafruit-macropad-rp2040). I plan on using this nifty little thing, as... a Macropad.

To do this, I have utilized the guide on Adafruit called [MACROPAD Hotkeys](https://learn.adafruit.com/macropad-hotkeys). This is a great starting point, but I want MORE. 

I want _my_ MacroPad to be able to switch macro sets **automatically**. As mentioned in the [guide](https://learn.adafruit.com/macropad-hotkeys/going-further)...

> Could there be some way to _automatically_ switch based on the current application in use? CircuitPython can receive serial messages while also emulating a keyboard, so there’s ways to send information to MACROPAD. The host-side implementation though, that gets complex, and would vary with all the myriad system types and their particular scripting or development options, which is why it’s not done here. Food for thought!

Food for thought indeed... Which is what has driven me to create [PyCurrentWindow](https://github.com/astridos2go/PycurrentWindow)

## :thought_balloon: So what exactly does it do?
I'm so glad you asked. Well, for the Macropad to be able to switch macro profiles automatically, it would have to know which program was currently in focus. 

As mentioned in the guide excerpt from earlier:
> CircuitPython can receive serial messages while also emulating a keyboard

So, PyCurrentWindow, naturally, is designed to run quietly in the background, and send the current program name (i.e. `firefox.exe`) to the MacroPad via serial (COM).

## :arrow_down: Installation and Usage
:warning: Right now, this project is far from finished!

:information_source: This assumes you have the latest version of Python installed, and basic understanding of how to use virtual enviroments.

### To use this project it in it's current state:

#### On your computer
1. Clone the repo onto your computer
2. Navigate to the cloned repo
3. Create and activate a [virtual enviroment](https://docs.python.org/3/library/venv.html)
4. Run `pip install -r requirements.txt`
5. Run `python main.py` 

#### On your CircuitPython Macropad

If using `main.py` without modification, you need to tell your Macropad to identify itself and listen for COM messages. Below is an example of a `code.py` that listens for the messages, but also sends a message if it recieves an 'IDENTIFY' message. 

(For a different circuit board, you can edit `main.py` to search for a different identifier or no identifier at all...)

This code is provided without any guarantee that it will work. 

```python
import usb_cdc
import time

in_data = bytearray()
program = ""
new_program = ""
while True:
    serial = usb_cdc.data
    if serial.in_waiting > 0:
        new_program = serial.read(serial.in_waiting).decode("utf-8")

    if new_program != program:
        program = new_program
        print(program)

    if program == "IDENTIFY":
        program = ""
        serial.write(str.encode("ADAFRUIT MACROPAD"))
        time.sleep(9)

    time.sleep(1)
```

## :warning: Issues
This app is in the early stages of it's development. It is intended to be run on a Windows computer, with the latest version of Python. You're free to raise an issue, but keep in mind that this is in rapid development, and mainly going to focus on _my_ use case.

## :wrench: Development
1. Clone the repo onto your computer
2. Navigate to the cloned repo
3. Create and activate a [virtual enviroment](https://docs.python.org/3/library/venv.html)
4. Run `pip install -r requirements.txt`
5. Happy Developing!

## Contributing
I don't expect this repo to get much attention, nor do I have much expertise in running repos, but if you would like to contribute to this project, feel free to open a PR.
