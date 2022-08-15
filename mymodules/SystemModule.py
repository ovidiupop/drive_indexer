import os
import pwd
import subprocess

from PyQt5 import QtWidgets
from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QInputDialog

from mymodules import GDBModule as gdb


# set active all drives existing when the app is started
def setActiveDriveDB(mounted_drives):
    gdb.setDrivesActive(mounted_drives)


def folderCanBeIndexed(folder):
    response = subprocess.Popen(f'df {folder}', shell=True, stdin=None,
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
    dpartitions = {}
    partitions = subprocess.Popen(f'lsblk -l -o type,path,mountpoint | grep -e part', shell=True, stdin=None,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    lines_partitions = partitions.stdout.readlines()
    if lines_partitions:
        for line_partition in lines_partitions:
            line_partition = line_partition.decode('ascii').strip()
            parts = line_partition.split(' ')
            while "" in parts:
                parts.remove("")
            parent = parts[1].rstrip('0123456789').strip()
            if len(parts) > 2:
                mount_point = parts[2]
                if parent in dpartitions:
                    dpartitions[parent].append(mount_point)
                else:
                    dpartitions[parent] = [mount_point]

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
                disk = {'serial': x[1], 'path': x[2], 'size': sizeToGb(x[3]), 'hotplug': x[4], 'name': x[5], 'vendor': x[6], 'partitions': ','.join(dpartitions[x[2]])}
                disks.append(disk)
            else:  # is partition
                pass
    setActiveDriveDB(disks)
    return disks
    # return this
    # [{'serial': 'S3Z2NB2KA50740N', 'path': '/dev/sda', 'size': 465.8, 'hotplug': '0', 'name': 'Samsung_SSD_860_EVO_500GB', 'vendor': 'ATA', 'partitions': '/boot/efi,/,/home,/home/matricks/aacustom'},
    # {'serial': 'Z9AX3YM7', 'path': '/dev/sdc', 'size': 931.5, 'hotplug': '1', 'name': 'ST1000DM010-2EP102', 'vendor': 'ST1000DM', 'partitions': '/home/matricks/aacustom/myoneterra'},
    # {'serial': 'WD-WMC4N0404141', 'path': '/dev/sdd', 'size': 2700.0, 'hotplug': '1', 'name': 'WDC_WD30EZRX-00D8PB0', 'vendor': 'WDC', 'partitions': '/home/matricks/aacustom/mybook'},
    # {'serial': '4990779F50C0', 'path': '/dev/sde', 'size': 931.5, 'hotplug': '1', 'name': 'XPG_EX500', 'vendor': 'ADATA', 'partitions': '/home/matricks/aacustom/myseriale'}]


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


def getActiveUser():
    return pwd.getpwuid(os.getuid())[0]



def mountedDrivesOld():
    disks = []
    s = subprocess.Popen(f'lsblk --nodeps -o type,name,serial,size,model', shell=True, stdin=None,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    lines = s.stdout.readlines()
    if lines:
        for line in lines:
            line = line.decode('ascii').strip()
            x = line.split(' ')
            while "" in x:
                x.remove("")
            if x[0] == 'disk':
                disk = {'mounted': x[1], 'name': x[4], 'serial': x[2], 'size': sizeToGb(x[3])}
                disks.append(disk)
    setActiveDriveDB(disks)
    return disks

class System(QObject):
    def __init__(self):
        super(System, self).__init__()
        self.normal_user = None
        getActiveUser()
        self.mounted_drives = None or mountedDrives()

    # unused (root)
    def backToNormalUser(self):
        cmd = f'su - {self.normal_user}'
        os.system(cmd)

    # unused (root)
    def connectAsRoot(self):
        # *nix system
        if os.name == 'posix' and not os.getuid() == 0:
            # save actual user
            self.normal_user = getActiveUser()
            print('not logged as root')
            passwd, ok = QInputDialog.getText(None, 'Root Password', 'Please enter root password:',
                                              QtWidgets.QLineEdit.Password)
            if ok:
                answer = os.system("echo '" + passwd + "' |sudo -S echo 'checking passwd'  ")
                while answer != 0:
                    passwd, ok = QInputDialog.getText(None, 'Root Password', 'Wrong Password!\nTry again!',
                                                      QtWidgets.QLineEdit.Password)
                    if ok:
                        answer = os.system("echo '" + passwd + "' |sudo -S echo 'checking passwd'  ")
                    else:
                        ok = False
                        break
                if ok:
                    print('You are root now!')
                    return True
            print("Loging as root failed!")
            return False
        else:
            print("Not unix or already logged")
            return True
