__version__ = 1.1

import logging
from logging import info
import os
import sys
import webbrowser
from ctypes import windll
from os.path import dirname
from os.path import join as join_path
from threading import Thread
from time import sleep

from PIL import Image
from pystray import Icon, Menu, MenuItem

from src.listener import ObservableWindowChange, SerialWindowObserver
from src.port_finder import findDevicePort

FROZEN = getattr(sys, "frozen", False)

# Get location of file
LOCATION = dirname(__file__) if not FROZEN else dirname(sys.executable)

# Initialize app data
APPDATA = os.path.join(os.getenv('APPDATA'), 'PyCurrentWindow')
if not os.path.exists(APPDATA):
    os.makedirs(APPDATA)


def main(verbose=False):
    # Configure logging
    logging.basicConfig(filename=os.path.join(APPDATA, "latest.log"),
                        filemode="w",
                        format='[%(asctime)s] %(levelname)s: %(message)s',
                        datefmt='%H:%M:%S',
                        level=logging.INFO)
    
    # Console output for debugging code
    if not FROZEN:
        logging.getLogger().addHandler(logging.StreamHandler())
    
    info('Welcome to PyCurrentWindow!')

    # Find the device
    serial = findDevicePort('ADAFRUIT MACROPAD')

    def run():
        # Create an observable and an observer observing it
        subject = ObservableWindowChange()
        _ = SerialWindowObserver(subject, serial, verbose)

        # Listen for window changes
        subject.start_event_listener()

    # Start the 'run' method in a daemonized thread.
    t = Thread(target=run)
    t.daemon = True
    t.start()

    # Keep the main thread running in a sleep loop until ctrl+c (SIGINT) is caught.
    # Once the main thread terminates, all daemon threads will automatically
    # terminate.
    while True:
        try:
            sleep(0.1)
        except Exception:
            break


if __name__ == "__main__":
    windll.shcore.SetProcessDpiAwareness(2)

    def stop() -> None:
        App.stop()
        os._exit(0)

    def updateCheck() -> None:
        webbrowser.open("https://github.com/astridos2go/PyCurrentWindow/releases/latest")

    icon = Image.open(join_path(LOCATION, 'images', 'icon.png'))
    App = Icon('PyCurrentWindow', icon=icon, menu=Menu(
        MenuItem('Quit', stop), MenuItem("Check for Updates", updateCheck)))
    App.run_detached()
    main(True)
