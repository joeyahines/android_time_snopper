"""
Digital Forensics Final Project Spring 2019

Android Time Forensics using ADB
"""

import argparse
import pytz
from adb_interface import *
from sqlite3_interface import DataBaseInterface

# Command line arguments
parser = argparse.ArgumentParser(description="Android Time Forensics Tool")
parser.add_argument('--adb_port', metavar='p', type=int, nargs='+', help='adb port number', default=5037)
parser.add_argument('--adb_addr', metavar='a', type=str, nargs='+', help='adb address', default="127.0.0.1")


def detect_timeshift(target_time: datetime, system_time: datetime):
    """
    Detect time shift
    :param target_time: time on the android device
    :param system_time: time on the workstation
    :return:
    """
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


def fix_database_timeshift(device: Device, target_time: datetime, system_time: datetime, database_path: str):
    """
    fixes the timeshift in a database, prints out results and then saves the changes to file
    :param device: device to grab the database from
    :param target_time: device time
    :param system_time: workstation time
    :param database_path: path to the database
    """

    # Get shift time
    shift = target_time.timestamp() - system_time.timestamp()

    # Get the database from the device
    file_name = pull_file(device, database_path)

    try:
        # Open database
        database_interface = DataBaseInterface(file_name)

        # Get table and column
        table = get_table_choice(database_interface)

        column = get_column_to_time_shift(database_interface, table)

        # Preform Time shift
        print("Old Time")
        database_interface.print_table(table, column)
        database_interface.shift_time_column(table, column, shift)
        print("New Time")
        database_interface.print_table(table, column)

        # Close database
        database_interface.conn.close()

    except Exception as e:
        print(e)


def get_table_choice(database_interface: DataBaseInterface):
    """
    Get which table the user wants to manipulate
    :param database_interface: database
    :return: table selection
    """
    table_list = database_interface.get_tables()

    return get_option_from_list(table_list, "Select a table")


def get_column_to_time_shift(database_interface: DataBaseInterface, table: str):
    """
    Get which column from a table to manipulate
    :param database_interface: database
    :param table: table get a column from
    :return: column selection
    """
    header = database_interface.get_table_header(table)

    return get_option_from_list(header, "Pick time column to shift")


def get_option_from_list(list: list, selection_text: str):
    """
    Select an option from a list
    :param list: list of options
    :param selection_text: text to display above the list
    :return: list option selected
    """
    while True:
        print(selection_text + ": ")
        ndx = 0
        for option in list:
            print("%d ) %s" % (ndx, option))
            ndx += 1

        try:
            selection = input("\nSelection: ")

            return list[int(selection)]
        except ValueError:
            print("Options are numbers, please try again")
        except IndexError:
            print("That value is not in range, please try again")

        input("Press enter to continue")


if __name__ == "__main__":
    args = parser.parse_args()

    try:
        # Open up ADB client
        client = AdbClient(args.adb_addr, port=args.adb_port)
        device = get_device(client)

        # Try to root the device
        try:
            device.root()
        except Exception as e:
            # If we are here, we are hopefully rooted
            print("Error rooting device: " + e.__str__())


        done = False
        while not done:
            # Print Header
            print("------------------------------")
            print("Android Time Snooper Main Menu")
            print("Device: %s" % get_serial_number(device))

            # Print Menu
            print("a) Get Time Shift")
            print("b) Time Correct Database")
            print("c) Time Correct Call Log")
            print("d) Print Time Properties")
            print("e) Get Device Properties")
            print("x) Exit")

            # Do user selection
            menu_select = input("Selection: ")[0].lower()
            target_time = get_time(device)
            system_time = datetime.datetime.now(tz=pytz.utc)

            # get timeshift
            if menu_select == "a":
                detect_timeshift(target_time, system_time)
            # fix database time shift
            elif menu_select == "b":
                db_path = input("Database path: ")
                fix_database_timeshift(device, target_time, system_time, db_path)
            # fix call log time shift
            elif menu_select == "c":
                fix_database_timeshift(device, target_time, system_time,
                                       "/data/data/com.android.providers.contacts/databases/calllog.db")
            # get time properties
            elif menu_select == "d":
                print_time_properties(device)

            # print device properties
            elif menu_select == "e":
                print_properties(device)
            # exit
            elif menu_select == "x":
                print("Bye!")
                done = True

            if not done:
                input("\nPress Enter To Continue")

    except (RuntimeError, ConnectionError) as e:
        print("Error with ADB: %s" % e.__str__())
        exit(1)
    except KeyboardInterrupt:
        print("Bye!")
        exit(0)
