import sys
import os
import platform
import subprocess

if sys.platform == 'win32':
    import win32api
    import wmi

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
        from pathlib import Path
        root = Path(folder).anchor

        parts = folder.split(':')
        letter = root.strip('\\')

        serial = get_serial_number_of_physical_disk(drive_letter=letter)
        serial_is_mounted = gdb.driveSerialIsMounted(serial)
        if serial:
            if serial_is_mounted:
                return [True, serial]
        return [False, None]


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


def mountedDrivesWindows():
    # dl = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    # drives = ['%s:' % d for d in dl if os.path.exists('%s:' % d)]
    # #drives = ['C:', 'D:', 'F:']
    #
    # serials = {}
    # for letter in drives:
    #     disk_serial = get_serial_number_of_physical_disk(drive_letter=letter)
    #     serials[disk_serial] = letter

    disks = []
    drives = subprocess.Popen(f'wmic diskdrive get model,interfaceType,serialNumber,size,name', shell=True, stdin=None,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    lines_drives = drives.stdout.readlines()
    lines_drives.pop(0)
    count = len(lines_drives)
    lines_drives.pop(count - 1)

    if lines_drives:
        for line_drive in lines_drives:
            x = line_drive.decode('ascii').strip()
            data = x.split(' ')
            data.pop(0)
            data = [item for item in data if item]
            length = len(data)

            # this order is mandatory
            size = data.pop(len(data) - 1)
            serial = data.pop(len(data) - 1)
            path = data.pop(len(data) - 1)
            name = '_'.join(data)

            # if serial in serials:
            #     path = serials[serial]
            disk = {'serial': serial, 'path': path, 'size': sizeToGb(size), 'name': name}
            disks.append(disk)

        if disks:
            setActiveDriveDB(disks)
        return disks


def get_serial_number_of_physical_disk(drive_letter='C:'):
    # c = wmi.WMI()
    # logical_disk = c.Win32_LogicalDisk(Caption=drive_letter)[0]
    # partition = logical_disk.associators()[1]
    # physical_disc = partition.associators()[0]
    # return physical_disc.SerialNumber

    c = wmi.WMI()
    for physical_disk in c.Win32_DiskDrive():
        for partition in physical_disk.associators("Win32_DiskDriveToDiskPartition"):
            for logical_disk in partition.associators("Win32_LogicalDiskToPartition"):
                if logical_disk.Caption == drive_letter:
                    return physical_disk.SerialNumber


# df /home/matricks/aacustom/Muzica/ => /dev/sda4      316212352 204173148  95906752  69% /home/matricks/aacustom
# inxi -Dxx
# lsblk -l -o type,fstype,kname,size,hotplug,serial,path,mountpoint,vendor,model | grep -e disk -e part
def mountedDrivesLinux():
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
    if 'win' in sys.platform:
        pass


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


def systemType():
    return platform.system()


class SystemClass(QObject):
    def __init__(self):
        super(SystemClass, self).__init__()
        self.system_type = None or systemType()
        self.normal_user = None
        self.mounted_drives = None or self.checkMountedDrives()

    def checkMountedDrives(self):
        if self.system_type == 'Linux':
            return mountedDrivesLinux()
        if self.system_type == 'Windows':
            return mountedDrivesWindows()
