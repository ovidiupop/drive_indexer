# this class can be only imported
import mimetypes

from PyQt5 import QtWidgets
from PyQt5.QtCore import QMimeDatabase
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QMessageBox

HEADER_SEARCH_RESULTS_TABLE = ['Directory', 'Filename', 'Size', 'Extension', 'Drive']
HEADER_DRIVES_TABLE = {"serial": "Serial Number", "name": "Drive Name", "label": "Own Label", "size": "Size (GB)", "active": "Active", 'partitions': "Partitions"}


def getIcon(item, size=24):
    mime = mimetypes.types_map
    ext = '.'+item
    if ext in mime.keys():
        name = mime[ext].replace('/', '-')
        icon = QIcon.fromTheme(name)
        return icon.pixmap(size)
    else:
        a = QMimeDatabase().allMimeTypes()
        for mime in a:
            if mime.name() == 'text/' + item or mime.name() == 'application/x-' + item:
                name = mime.name().replace('/', '-')
                icon = QIcon.fromTheme(name)
                return icon.pixmap(size)

def iconForButton(name):
    return QtWidgets.QApplication.style().standardIcon(getattr(QtWidgets.QStyle, name))


def confirmationDialog(title, message):
    msg_box = QtWidgets.QMessageBox()
    msg_box.setIcon(QMessageBox.Warning)
    msg_box.setText(message)
    msg_box.setWindowTitle(title)
    msg_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
    return msg_box.exec() == QMessageBox.Ok


def tabIndexByName(tab_widget, tab_name):
    for index in range(tab_widget.count()):
        if tab_name == tab_widget.tabText(index):
            return index


class Global():
    pass
