import re
import sys
from pystray import Icon, Menu, MenuItem
from time import sleep
from win32gui import GetForegroundWindow
from win32process import GetWindowThreadProcessId
from psutil import Process

from configparser import ConfigParser

from serial import Serial
from serial.serialutil import SerialException
from serial.tools import list_ports

from ctypes import windll

from PIL import Image


def findDevicePort(identifier=None, waitForResponse=5):
    print('[INFO]: Finding device port...')
    
    # Try to connect to provided port
    def tryPort(port_id):
        print(f'[INFO]: Trying {port_id}...')
        # Create new serial on passed port
        try:
            _serial = Serial(port_id)
            # If an identifier was passed
            if identifier is not None:
                # Send out identify message
                _serial.write(str.encode("IDENTIFY"))
                
                # Get response from serial
                for _ in range(waitForResponse * 2):
                    # Listen to serial
                    who = _serial.read(_serial.in_waiting).decode()
                    
                    # Message received
                    if who != "":
                        break
                    
                    # No message, wait 30 seconds and try again
                    sleep(0.5)
                
                # If response matches identifier
                if who == identifier:
                    # Return the serial port.
                    print(f"[SUCCESS]: Successfully connected to {identifier} on {port_id}.")
                    return _serial
                
                # No message was returned or the wrong identifier
                else:
                    # Return none
                    print(f"[ERROR]: There is no properly configured {identifier} on {port_id}.")
                    if who != "":
                        print(f'[INFO]: {port_id} has identified itself as {who}.')
                    return None
            
            # If no identifier to verify, just return the serial port.
            else:
                return _serial
        
        # The port is closed
        except SerialException:
            print(f"[ERROR]: {port_id} is closed!")
            return None
    
    # Recursively call tryPort with all potential values
    def tryAllPorts(port_dict):
        nonlocal PORT
        _serial = None
        for port in port_dict.keys():
            _serial = tryPort(port)
            if _serial is not None:
                break
                
        return port, port_dict[port], _serial
    
    # Warn if no identifier
    if identifier is None:
        print("[WARN]: Without an identifier, the serial port cannot be validated. We will still try to return a port, but no one may be listening on the other end...")
    
    # Get configuration
    device_info = ConfigParser()
    # Read existing device.ini if it exists
    device_info.read('device.ini')
    
    # Initialize serial
    SERIAL = None
    
    # If there is no existing device info
    if device_info.sections() == []:
        # Initialize config
        device_info['DEVICE'] = {'PORT': '', 'HWID': ''}
    
    PORT = device_info['DEVICE']['PORT']    # Get last used port
    HWID = device_info['DEVICE']['HWID']    # Get Hardware Identifier
    
    # Get all USB ports
    port_list = sorted(list_ports.grep('USB'))
    
    # Create a dictionary with the port name and HWID of all ports
    ports = {}
    for port, _, hwid in port_list:
        hwid = re.search(r"VID:PID=([0-9A-F]{4}:[0-9A-F]{4})", hwid).groups(1)[0]
        ports.update({port: hwid})
    
    # If there is an existing port in the history, try it first
    if PORT != "" and PORT in ports.keys():
        best_port = PORT
        # Check if the HWID from history matches
        if HWID != "" and ports[best_port] == HWID:
            # Try the port
            SERIAL = tryPort(best_port)
            # Save the port and hwid
            if SERIAL is not None:
                PORT = best_port
                HWID = ports[best_port]
        
        # Try matching HWID next
        if SERIAL is None:
            # Get all ports with a matching HWID
            best_ports = sorted([k for k, v in ports.items() if v == HWID])
            # Iterate through all of them
            for p in best_ports:
                # Try the port
                SERIAL = tryPort(p)
                if SERIAL is not None:
                    # Save the port and hwid
                    PORT = p
                    HWID = ports[p]
                    break
    
    # If the optimized routes didn't work..., brute force baby
    if SERIAL is None:
        PORT, HWID, SERIAL = tryAllPorts(ports)
        if SERIAL is None:
            print(f'[ERROR]: The {identifier} was not found :(')
            print('[INFO]: PyCurrentWindow will now terminate')
            exit(0)
    
    # Save the PORT and HWID
    device_info['DEVICE']['PORT'] = PORT    # Get last used port
    device_info['DEVICE']['HWID'] = HWID    # Get Hardware Identifier
    
    # Save the configuration
    with open('device.ini', 'w') as device_file:
        device_info.write(device_file)
    
    # Return the serial
    return SERIAL
        

def getCurrentProcess() -> str | None:
    try:
        window = GetForegroundWindow()
        PID = GetWindowThreadProcessId(window)
        return Process(PID[-1]).name()
    except Exception:
        return None


def main():
    # Perhaps a better implementation than "while True"
    # https://github.com/Danesprite/windows-fun/blob/master/window%20change%20listener.py
    
    print('[INFO]: Welcome to PyCurrentWindow!')
    
    serial = findDevicePort('ADAFRUIT MACROPAD')
    
    process = getCurrentProcess()
    while True:
        new_process = getCurrentProcess()
        if new_process is not None and new_process != process:
            process = new_process   # Update process
            serial.write(str.encode(process))   # Send the update
            
        sleep(1)    # Sleep, and repeat


if __name__ == "__main__":
    
    windll.shcore.SetProcessDpiAwareness(2)
    
    def stop() -> None:
        App.stop()
        sys.exit()
    
    icon = Image.open('icon.png')
    App = Icon('PyCurrentWindow', icon=icon, menu=Menu(MenuItem('Quit', stop, default=True)))
    App.run_detached()
    main()
