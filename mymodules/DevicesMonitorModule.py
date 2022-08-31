from PyQt5 import QtCore
import pyudev


class Devices(QtCore.QObject):
    """
    Monitoring devices status for adding/removing from device
    and add/remove available folders for indexing/reindexing
    """
    configuration_changed = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        context = pyudev.Context()
        # Monitor devices
        monitor = pyudev.Monitor.from_netlink(context)
        monitor.filter_by('block', device_type='disk')
        observer = pyudev.MonitorObserver(monitor, self.handleEvent)
        observer.start()
        # this will have to run continuously so will not stop
        # observer.stop()

    def handleEvent(self, _action, _device):
        self.configuration_changed.emit()
