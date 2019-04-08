"""
Digital Forensics Final Project Spring 2019

Android Time Forensics using ADB
"""

import datetime
from adb.client import Client as AdbClient
import argparse
import pytz

# Command line arguments
parser = argparse.ArgumentParser(description="Android Time Forensics Tool")
parser.add_argument('--adb_port', metavar='p', type=int, nargs='+', help='adb port number', default=5037)
parser.add_argument('--adb_addr', metavar='a', type=str, nargs='+', help='adb address', default="127.0.0.1")


def get_time(time):
    """
    Parses a time string of the format "%H:%M:%S,%j,%Y,%z" to get a date
    :param time: time string
    :return: datetime object of that string
    """
    date = datetime.datetime.strptime(time, "%H:%M:%S,%j,%Y,%z\n")
    return date


def get_device(client):
    """
    Gets the Android Device section from the user
    :param client: adb client
    :return: adb device object
    """

    devices = client.devices()
    done = False
    device = None

    # get device selection from the user
    while not done:
        if len(devices) == 0:
            print("No Android Devices Found!")
            exit(1)

        print("Select a device:")
        print("Choice\tSerial #")
        ndx = 0
        for device in devices:
            print("%d\t\t%s" % (ndx, device.get_properties()["ro.kernel.androidboot.serialno"]))

        choice = input("\nEnter Choice: ")

        try:
            device = devices[int(choice)]
            done = True
        except Exception as e:
            print(e)
            print("Invalid choice, please try again")

    return device


def print_properties(device):
    """
    Prints a devices properties
    :param device:
    :return:
    """
    properties = device.get_properties()

    for property in properties:
        print(property, properties[property])


if __name__ == "__main__":
    args = parser.parse_args()

    # Open up ADB client
    client = AdbClient(args.adb_addr, port=args.adb_port)

    # Get the device selection from the user
    device = get_device(client)
    # print out all device properties
    properties = device.get_properties()

    target_time = get_time(device.shell("date -u +%H:%M:%S,%j,%Y,%z"))
    system_time = datetime.datetime.now(tz=pytz.utc)

    if target_time.timestamp() != system_time.timestamp():

        # print out times
        print("\nTime Shift Detected on Target Device:")
        print("Target Time: ", target_time.strftime("%x %X"))
        print("Workstation Time:", system_time.strftime("%x %X"))

        # get time time shift
        if system_time > target_time:
            print("Time Delta: ", system_time - target_time)
        else:
            print("Time Delta: ", target_time - system_time)
    else:
        print("No time shift found")
