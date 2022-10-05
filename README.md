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

### On any computer you wish to use the MacroPad with...
See the [latest release](https://github.com/astridos2go/PyCurrentWindow/releases/latest)

### On your CircuitPython Macropad
You have two options:
1. Copy and paste the following `code.py` [here](https://gist.github.com/astridos2go/89059bc435260294aadce79624f41a97) into your `CIRCUITPY` drive.
- Once running, you can modify any of the existing Macro files by adding a dictionary key `program`. Set the value to the program name you'd like to use with those Macro keys. 
- The `program` key and value are NOT required! Existing macros still work!
- Even if the Macropad switches automatically, you can still manually cycle through the profiles. (Note that if a bound program window refocuses, it will switch back to that macro)

2. Modify your `code.py` yourself.
- PyCurrentWindow will send `"IDENTIFY"` over serial to any USB devices.
- Your MacroPad needs to **recieve** this message, and **respond** back `"ADAFRUIT MACROPAD"`.
- Additionally, you will need to listen for messages telling the MacroPad which program is running

## :warning: Issues
This app is in the early stages of it's development. Please let me know if you encounter any errors, or if there's any functionality you'd like to see implemented!

## :wrench: Development
1. Clone the repo onto your computer
2. Navigate to the cloned repo
3. Create and activate a [virtual enviroment](https://docs.python.org/3/library/venv.html)
4. Run `pip install -r requirements.txt`
5. Happy Developing!

## Contributing
I don't expect this repo to get much attention, nor do I have much expertise in running repos, but if you would like to contribute to this project, feel free to open a PR.
