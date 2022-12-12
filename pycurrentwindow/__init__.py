__version__ = 1.1

import logging
import os
import sys
import webbrowser
from configparser import ConfigParser
from ctypes import windll
from logging import info
from os import path
from threading import Thread
from time import sleep

from PIL import Image
from pystray import Icon, Menu, MenuItem

from pycurrentwindow.listener import ObservableWindowChange, SerialWindowObserver
from pycurrentwindow.port_finder import findDevicePort
from pycurrentwindow.utils.app_data import app_data

# Determine if the app is frozen
FROZEN = getattr(sys, "frozen", False)

# Get location of file
LOCATION = path.dirname(__file__) if not FROZEN else path.dirname(sys.executable)

# Initialize app data
APPDATA = app_data()

# Define the config file
CONFIG_FILE = path.join(APPDATA, "config.ini")

# Define the default config
DEFAULT_CONFIG_OPTS = {"LOGGING": {"toFile": "True"}}

# Define the config
CONFIG_INFO = ConfigParser()

# Load default config and user config
CONFIG_INFO.read_dict(DEFAULT_CONFIG_OPTS)
CONFIG_INFO.read(CONFIG_FILE)


# Configure logging
def configure_logging(to_file) -> bool:
    """Configures the logging for the program

    Args:
        to_file (bool): Whether or not to initialize the file logging

    Returns:
        bool: Whether the configuration was successful
    """
    root = logging.getLogger()
    if to_file:

        file = logging.FileHandler(filename=path.join(APPDATA, "latest.log"), mode="w")
        file.setLevel(logging.DEBUG)

        fformat = logging.Formatter(
            fmt="[%(asctime)s] %(name)8s %(levelname)8s: %(message)s",
            datefmt="%H:%M:%S",
        )
        file.setFormatter(fformat)

        root.addHandler(file)

    # Console output for debugging code
    if not FROZEN:
        console = logging.StreamHandler()
        console.setLevel(logging.DEBUG)

        cformat = logging.Formatter("[%(name)s] %(levelname)s: %(message)s")
        console.setFormatter(cformat)

        root.addHandler(console)

    return True


def main():
    """The main body of the program.
    This configures logging, finds the serial device, and runs the listener.
    """
    log_config = CONFIG_INFO["LOGGING"]

    if not configure_logging(log_config.getboolean("toFile")):
        print("Logging setup failed!")

    info("Welcome to PyCurrentWindow!")

    # Find the device
    serial = findDevicePort("ADAFRUIT MACROPAD")

    if serial is None:
        pass

    def run():
        # Create an observable and an observer observing it
        subject = ObservableWindowChange()
        _ = SerialWindowObserver(subject, serial)

        # Listen for window changes
        subject.start_event_listener()

    # Start the 'run' method in a daemonized thread.
    t = Thread(target=run)
    t.daemon = True
    t.start()

    # Keep the main thread running in a sleep loop until ended
    while True:
        try:
            sleep(0.1)
        except Exception:
            break


def stop() -> None:
    """Stops the App icon loading, saves the config, and exits the program"""
    # Save the changes to the config to a file
    with open(CONFIG_FILE, "w") as file:
        CONFIG_INFO.write(file)

    # Get the global app
    global APP
    # Stop the app
    APP.stop()

    # Exit the application
    os._exit(0)


if __name__ == "__main__":
    windll.shcore.SetProcessDpiAwareness(2)

    def updateCheck() -> None:
        webbrowser.open(
            "https://github.com/astridos2go/PyCurrentWindow/releases/latest"
        )

    global APP
    icon = Image.open(path.join(LOCATION, "images", "icon.png"))
    APP = Icon(
        "PyCurrentWindow",
        icon=icon,
        menu=Menu(MenuItem("Quit", stop), MenuItem("Check for Updates", updateCheck)),
    )
    APP.run_detached()
    main()
