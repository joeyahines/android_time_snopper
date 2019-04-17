import datetime
from adb.client import Client as AdbClient
from adb.device import Device
from pathlib import Path


def get_time(device: Device):
    """
    Gets the time from an android device
    :param device: Target Device
    :return:
    """
    time_str = device.shell("date -u +%H:%M:%S,%j,%Y,%z")
    return parse_time(time_str)


def parse_time(time):
    """
    Parses a time string of the format "%H:%M:%S,%j,%Y,%z" to get a date
    :param time: time string
    :return: datetime object of that string
    """
    date = datetime.datetime.strptime(time, "%H:%M:%S,%j,%Y,%z\n")
    return date


def get_device(client: AdbClient):
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
            print("%d\t\t%s" % (ndx, get_serial_number(device)))

        choice = input("\nEnter Choice: ")

        try:
            device = devices[int(choice)]
            done = True
        except Exception as e:
            print(e)
            print("Invalid choice, please try again")

    return device


def get_serial_number(device: Device):
    return device.get_properties()["ro.kernel.androidboot.serialno"]


def print_properties(device: Device):
    """
    Prints a device's properties
    :param device: android device
    :return:
    """
    properties = device.get_properties()

    for property in properties:
        print(property, properties[property])


def print_settings(device: Device):
    """
    Prints the settings of the device
    :param device: Android device
    """

    results = device.shell("settings list GLOBAL")

    print(results)


def print_time_settings(device: Device):
    """
    Print auto_time settings
    :param device: Android device
    """
    results = device.shell("settings list GLOBAL | grep auto_time")

    print(results)


def print_time_properties(device: Device):
    """
    Prints the time properties
    :param device: android device
    :return:
    """
    properties = device.get_properties()

    print("Timezone: ", properties["persist.sys.timezone"])
    print("Time of Last Boot:", properties["ro.runtime.firstboot"])


def pull_callog(device: Device):
    """
    Gets the sqlite3 db call log from the devce
    :param device: Android device
    """

    pull_file(device, "/data/data/com.android.providers.contacts/databases/calllog.db")


def pull_file(device: Device, path: str):
    """
    Gets a file from the target device
    :param device: Android Device
    :param path: Path of the file to get
    :return str: name of the file
    """

    timestamp = datetime.datetime.now().timestamp()
    db_name = Path(path).name
    file_name = "%s-%s" % (timestamp, db_name)
    device.pull(path, file_name)

    return file_name
