import os
import re
from configparser import ConfigParser
from logging import error, info, warning
from time import sleep

from serial import Serial
from serial.serialutil import SerialException
from serial.tools import list_ports


def findDevicePort(identifier=None, waitForResponse=5):
    info('Finding device port...')

    # Try to connect to provided port
    def tryPort(port_id):
        info(f'Trying {port_id}...')
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
                    info(f"Successfully connected to {identifier} on {port_id}.")
                    return _serial

                # No message was returned or the wrong identifier
                else:
                    # Return none
                    error(f"There is no properly configured {identifier} on {port_id}.")
                    if who != "":
                        info(f'{port_id} has identified itself as {who}.')
                    return None

            # If no identifier to verify, just return the serial port.
            else:
                return _serial

        # The port is closed
        except SerialException:
            error(f"{port_id} is closed!")
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
        warning("Without an identifier, the serial port cannot be validated. We will still try to return a port, but no one may be listening on the other end...")

    app_data = os.path.join(os.getenv('APPDATA'), 'PyCurrentWindow')
    if not os.path.exists(app_data):
        os.makedirs(app_data)

    ini_file = os.path.join(app_data, 'device.ini')

    # Get configuration
    device_info = ConfigParser()
    # Read existing device.ini if it exists
    device_info.read(ini_file)

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
            error(f'The {identifier} was not found :(')
            info('PyCurrentWindow will now terminate')
            os._exit(0)

    # Save the PORT and HWID
    device_info['DEVICE']['PORT'] = PORT    # Get last used port
    device_info['DEVICE']['HWID'] = HWID    # Get Hardware Identifier

    # Save the configuration
    with open(ini_file, 'w') as device_file:
        device_info.write(device_file)

    # Return the serial
    return SERIAL
