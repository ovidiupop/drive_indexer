import subprocess

from PyQt5.QtCore import QObject

from mymodules import GDBModule as gdb


# set active all drives existing when the app is started
def setActiveDriveDB(mounted_drives):
    if mounted_drives:
        gdb.setDrivesActive(mounted_drives)


def folderCanBeIndexed(folder):
    command = f'df "{folder}"'
    response = subprocess.Popen(command, shell=True, stdin=None,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # /dev/sda4      316212352 204173148  95906752  69% /home/matricks/aacustom
    lines = response.stdout.readlines()
    if lines:
        lines.pop(0)
        for line in lines:
            line = line.decode('ascii').strip()
            parts = line.split(' ')
            while "" in parts:
                parts.remove("")
            path = parts[0].rstrip('0123456789').strip()
            if path:
                drive = gdb.getDriveByPath(path)
                if drive:
                    return [True, drive]
            return [False, path]
    return [False, None]


# df /home/matricks/aacustom/Muzica/ => /dev/sda4      316212352 204173148  95906752  69% /home/matricks/aacustom
# inxi -Dxx
# lsblk -l -o type,fstype,kname,size,hotplug,serial,path,mountpoint,vendor,model | grep -e disk -e part
def mountedDrives():
    disks = []
    dpart = {}
    disk_parts = subprocess.Popen(f'lsblk -l -o type,path,mountpoint | grep -e part', shell=True, stdin=None,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    lines_disk_parts = disk_parts.stdout.readlines()
    if lines_disk_parts:
        for line_partition in lines_disk_parts:
            line_partition = line_partition.decode('ascii').strip()
            parts = line_partition.split(' ')
            while "" in parts:
                parts.remove("")
            parent = parts[1].rstrip('0123456789').strip()
            if len(parts) > 2:
                mount_point = parts[2]
                if parent in dpart:
                    dpart[parent].append(mount_point)
                else:
                    dpart[parent] = [mount_point]

    drives = subprocess.Popen(f'lsblk -l -o type,serial,path,size,hotplug,model,vendor | grep -e disk', shell=True, stdin=None,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    lines_drives = drives.stdout.readlines()
    if lines_drives:
        for line_drive in lines_drives:
            line_drive = line_drive.decode('ascii').strip()
            x = line_drive.split(' ')
            while "" in x:
                x.remove("")
            if x[0] == 'disk':
                disk = {'serial': x[1], 'path': x[2], 'size': sizeToGb(x[3]), 'hotplug': x[4], 'name': x[5], 'vendor': x[6]}
                disks.append(disk)
            else:  # is partition
                pass
    if disks:
        setActiveDriveDB(disks)
    return disks
    # return this
    # [{'serial': 'S3Z2NB2KA50740N', 'path': '/dev/sda', 'size': 465.8, 'hotplug': '0', 'name': 'Samsung_SSD_860_EVO_500GB', 'vendor': 'ATA'},
    # {'serial': 'Z9AX3YM7', 'path': '/dev/sdc', 'size': 931.5, 'hotplug': '1', 'name': 'ST1000DM010-2EP102', 'vendor': 'ST1000DM'},
    # {'serial': 'WD-WMC4N0404141', 'path': '/dev/sdd', 'size': 2700.0, 'hotplug': '1', 'name': 'WDC_WD30EZRX-00D8PB0', 'vendor': 'WDC'},
    # {'serial': '4990779F50C0', 'path': '/dev/sde', 'size': 931.5, 'hotplug': '1', 'name': 'XPG_EX500', 'vendor': 'ADATA'}]


def sizeToGb(size):
    measures = ['M', 'G', 'T']
    new_size = 0
    if size:
        for measure in measures:
            if size.endswith(measure):
                s = size.replace(measure, '')
                if measure == 'M':
                    new_size = float(s.replace(',', '.'))/1000
                elif measure == 'G':
                    new_size = float(s.replace(',', '.'))
                elif measure == 'T':
                    new_size = float(s.replace(',', '.')) * 1000
                return new_size
    return 0

class System(QObject):
    def __init__(self):
        super(System, self).__init__()
        self.normal_user = None
        self.mounted_drives = None or mountedDrives()
