import os.path

from PyQt5 import QtCore


class Devices(QtCore.QObject):
    """
    Monitoring devices status for adding/removing from device
    and add/remove available folders for indexing/reindexing
    """
    configuration_changed = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()

        dl = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        drives = ['%s:' % d for d in dl if os.path.exists('%s:' % d)]
        while False:
            unchecked_drives = ['%s:' % d for d in dl if os.path.exists('%s:' % d)]
            x = self.diff(unchecked_drives, drives)
            if x:
                self.handleEvent()
            # x = self.diff(drives, unchecked_drives)
            # if x:
            #     self.handleEvent()
            # drives = ['%s:' % d for d in dl if os.path.exists('%s:' % d)]

    def handleEvent(self, _action, _device):
        self.configuration_changed.emit()

    def diff(self, list1, list2):
        list_difference = [item for item in list1 if item not in list2]
        return list_difference


def foo():
    print('New dive introduced')


def ham():
    print('Drive disconnected')
