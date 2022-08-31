import os
import subprocess
import sys
from PyQt5.QtCore import QObject
from mymodules import GDBModule as gdb


def getFileEncoding(file):
    if 'linux' in sys.platform:
        command = f'file --mime-encoding "{file}" | ' + "awk '{print $NF}'"
        response = subprocess.Popen(command, shell=True, stdin=None, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        lines = response.stdout.readlines()
        encoding = lines[0].decode('ascii').strip()
        if encoding == 'us-ascii':
            return 'utf-8'
        return encoding
    if 'win' in sys.platform:
        print("Please implement SystemModule.getFileEncoding")


def getFileData(file):
    if 'linux' in sys.platform:
        command = f'file -b "{file}"'
        response = subprocess.Popen(command, shell=True, stdin=None, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        lines = response.stdout.readlines()
        data = lines[0].decode('ascii').strip()
        return data
    if 'win' in sys.platform:
        return ''
        # print("implement first")


# set active all drives existing when the app is started
def setActiveDriveDB(mounted_drives):
    if mounted_drives:
        gdb.setDrivesActive(mounted_drives)


def isEmptyFolder(folder):
    dir = os.listdir(folder)
    return len(dir) == 0


def folderCanBeIndexed(folder):
    if 'linux' in sys.platform:
        path = getDevicePathForFolder(folder)
        if path:
            drive_serial = gdb.getDriveByPath(path)
            if drive_serial and serialDriveIsMounted(drive_serial):
                return [True, drive_serial]
        return [False, None]
    if 'win' in sys.platform:
        print("implement first")


def getDevicePathForFolder(folder):  # in linux return /dev/sda
    if 'linux' in sys.platform:
        # sed -e 1d - remove header from response
        command = f'df "{folder}" | sed -e 1d | ' + "awk '{print $1}' | awk -F- '{sub(/[0-9]/," + '""); print}' + "'"
        response = subprocess.Popen(command, shell=True, stdin=None, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # /dev/sda\n
        lines = response.stdout.readlines()
        path = lines[0].decode('ascii').strip()
        return path
    if 'win' in sys.platform:
        print("implement first")


def serialDriveIsMounted(serial):
    return gdb.driveSerialIsMounted(serial)


def mountedDrives():
    if 'linux' in sys.platform:
        disks = []
        drives = subprocess.Popen(f'lsblk -l -o type,serial,path,size,hotplug,model | grep -e disk', shell=True,
                                  stdin=None, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        lines_drives = drives.stdout.readlines()
        if lines_drives:
            for line_drive in lines_drives:
                line_drive = line_drive.decode('ascii').strip()
                x = line_drive.split(' ')
                while "" in x:
                    x.remove("")
                if x[0] == 'disk':
                    disk = {'serial': x[1], 'path': x[2], 'size': sizeToGb(x[3]), 'hotplug': x[4], 'name': x[5]}
                    disks.append(disk)
                else:  # is partition
                    pass
        if disks:
            setActiveDriveDB(disks)
        return disks
        # return this
        # [{'serial': 'S3Z2NB2KA50740N', 'path': '/dev/sda', 'size': 465.8, 'hotplug': '0', 'name': 'Samsung_SSD_860_EVO_500GB'},
        # {'serial': 'Z9AX3YM7', 'path': '/dev/sdc', 'size': 931.5, 'hotplug': '1', 'name': 'ST1000DM010-2EP102'},
        # {'serial': 'WD-WMC4N0404141', 'path': '/dev/sdd', 'size': 2700.0, 'hotplug': '1', 'name': 'WDC_WD30EZRX-00D8PB0'},
        # {'serial': '4990779F50C0', 'path': '/dev/sde', 'size': 931.5, 'hotplug': '1', 'name': 'XPG_EX500'}]


def sizeToGb(size):
    measures = ['M', 'G', 'T']
    new_size = 0
    if size:
        for measure in measures:
            if size.endswith(measure):
                s = size.replace(measure, '')
                if measure == 'M':
                    new_size = float(s.replace(',', '.')) / 1000
                elif measure == 'G':
                    new_size = float(s.replace(',', '.'))
                elif measure == 'T':
                    new_size = float(s.replace(',', '.')) * 1000
                return new_size
    return 0


class SystemClass(QObject):
    def __init__(self):
        super(SystemClass, self).__init__()
        self.mounted_drives = None or mountedDrives()
