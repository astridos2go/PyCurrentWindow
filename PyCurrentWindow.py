__version__ = 1.0

import os
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

LOCATION = dirname(__file__)

 
def main(verbose=False):
    print('[INFO]: Welcome to PyCurrentWindow!')
    
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
    App = Icon('PyCurrentWindow', icon=icon, menu=Menu(MenuItem('Quit', stop), MenuItem("Check for Updates", updateCheck)))
    App.run_detached()
    main(True)
