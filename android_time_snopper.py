import subprocess
import datetime


def get_time(time):
    date = datetime.datetime.strptime(time, "%H:%M:%S,%j,%Y,%z\n")
    return date


if __name__ == "__main__":
    print(subprocess.check_output(['adb', 'devices', '-l']).decode('UTF-8'))

    sys_time = get_time(subprocess.check_output(['date', '-u', '+%H:%M:%S,%j,%Y,%z']).decode('UTF-8'))
    target_time = get_time(subprocess.check_output(['adb', 'shell', 'date', '-u', '+%H:%M:%S,%j,%Y,%z']).decode('UTF-8'))

    print("System time: %s" % sys_time)
    print("Android time: %s" % target_time)

    if sys_time != target_time:
        print("\nTime shift found!")
        print("Time shift: %s\n" % (sys_time - target_time))

        sys_time = int(subprocess.check_output(['date', '-u', '+%s']).decode('UTF-8'))
        target_time = int(subprocess.check_output(['adb', 'shell', 'date', '-u', '+%s']).decode('UTF-8'))
        print("Unix Time shift: %s\n" % (sys_time - target_time))
    else:
        print("\nTimes match!\n")


    time_settings = subprocess.check_output(['adb', 'shell', 'settings', "list", "GLOBAL", "|", "grep", "auto_time"]).decode('UTF-8')

    print("\nAndroid time Settings:")
    print(time_settings)



