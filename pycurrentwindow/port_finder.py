import os
import re
from configparser import ConfigParser
from logging import error, info, warning
from time import sleep

from serial import Serial
from serial.serialutil import SerialException
from serial.tools import list_ports

from .utils import app_data


def findDevicePort(identifier: str | None = None, wait: int = 5) -> Serial:
    def _getPortDict() -> dict:
        # Get all USB ports
        port_list = sorted(list_ports.grep("USB"))

        # Create a dictionary with the port name and HWID of all ports
        ports = {}
        for port, _, hwid in port_list:
            regex_match = re.search(r"VID:PID=([0-9A-F]{4}:[0-9A-F]{4})", hwid)

            if regex_match is not None:
                hwid = regex_match.groups(1)[0]
                ports.update({port: hwid})

        return ports

    # Try to connect to provided port
    def _tryPort(port_id: str) -> Serial | None:
        info(f"Trying {port_id}...")
        # Create new serial on passed port
        try:
            _serial = Serial(port_id)
            # If an identifier was passed
            if identifier is not None:
                # Send out identify message
                _serial.write(str.encode("IDENTIFY"))

                # Get response from serial
                for _ in range(wait * 2):
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
                        info(f"{port_id} has identified itself as {who}.")
                    return None

            # If no identifier to verify, just return the serial port.
            else:
                return _serial

        # The port is closed
        except SerialException:
            error(f"{port_id} is closed!")
            return None

    # Recursively call tryPort with all potential values
    def _tryAllPorts(port_dict: dict) -> tuple:
        found_port = False
        _serial = None
        for port in port_dict.keys():
            _serial = _tryPort(port)
            if _serial is not None:
                found_port = True
                break

        if found_port:
            return port, port_dict[port], _serial
        else:
            return None, None, None

    info("Finding device port...")

    # Warn if no identifier
    if identifier is None:
        warning(
            "Without an identifier, the serial port cannot be validated. We will still try to return a port, but no one may be listening on the other end..."
        )

    ini_file = os.path.join(app_data(), "device.ini")

    # Get configuration
    device_info = ConfigParser()
    # Read existing device.ini if it exists
    device_info.read(ini_file)

    # Initialize serial
    SERIAL = None

    # If there is no existing device info
    if device_info.sections() == []:
        # Initialize config
        device_info["DEVICE"] = {"PORT": "", "HWID": ""}

    PORT = device_info["DEVICE"]["PORT"]  # Get last used port
    HWID = device_info["DEVICE"]["HWID"]  # Get Hardware Identifier

    iterations = 0

    while SERIAL is None:
        iterations += 1

        ports = _getPortDict()

        # If there is an existing port in the history, try it first
        if PORT != "" and PORT in ports.keys():
            best_port = PORT
            # Check if the HWID from history matches
            if HWID != "" and ports[best_port] == HWID:
                # Try the port
                SERIAL = _tryPort(best_port)
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
                    SERIAL = _tryPort(p)
                    if SERIAL is not None:
                        # Save the port and hwid
                        PORT = p
                        HWID = ports[p]
                        break

        # If the optimized routes didn't work... brute force baby
        if SERIAL is None:
            # Check every port
            PORT, HWID, SERIAL = _tryAllPorts(ports)
            if SERIAL is None:
                warning(f"The {identifier} was not found. Will recheck for 30 minutes.")

        if SERIAL is None:
            # After an 30 minutes, give up and exit.
            if iterations == 30:
                error(f"The {identifier} was not able to be found, exiting.")
                return None

            # Sleep for a minute
            sleep(60)

    # Save the PORT and HWID
    device_info["DEVICE"]["PORT"] = PORT  # Get last used port
    device_info["DEVICE"]["HWID"] = HWID  # Get Hardware Identifier

    # Save the configuration
    with open(ini_file, "w") as device_file:
        device_info.write(device_file)

    # Return the serial
    return SERIAL
