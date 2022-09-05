from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QFileDialog, QListView, QAbstractItemView, QTreeView


class TableViewAutoCols(QtWidgets.QTableView):
    """ Override QTableView to override resizeEvent method
    """

    delete_key_pressed = QtCore.pyqtSignal()

    def __init__(self, model, parent=None):
        super(TableViewAutoCols, self).__init__(parent)
        self.columns = []

        rowHeight = self.fontMetrics().height()
        self.verticalHeader().setDefaultSectionSize(rowHeight)
        self.setModel(model)

    def setColumns(self, columns):
        self.columns = columns

    def resizeEvent(self, event):
        width = event.size().width()
        for index, size in enumerate(self.columns):
            self.setColumnWidth(index, width * size)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Delete:
            self.delete_key_pressed.emit()
        else:
            super().keyPressEvent(event)


class PushButton(QtWidgets.QPushButton):
    """
    Push button supporting icon to left/right
    """
    def __init__(self, *args, **kwargs):
        super(PushButton, self).__init__(*args, **kwargs)
        self.styleSheet = "QPushButton { text-align: left; padding: 5}"
        # icon = self.icon()
        # icon_size = self.iconSize()
        # remove icon
        self.setStyleSheet(self.styleSheet)

    def setTextCenter(self):
        self.setStyleSheet("QPushButton {text-align: center; padding: 5}")

    def setMyIcon(self, icon, icon_size=QtCore.QSize(16, 16), position=QtCore.Qt.AlignLeft):
        self.icon = icon
        self.icon_size = icon_size
        icon_alignment = QtCore.Qt.AlignLeft
        if position == 'right':
            icon_alignment = QtCore.Qt.AlignRight
        self.setIcon(QtGui.QIcon())
        label_icon = QtWidgets.QLabel()
        label_icon.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        label_icon.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)
        lay = QtWidgets.QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(label_icon, alignment=icon_alignment)
        label_icon.setPixmap(self.icon.pixmap(icon_size))


class ListWidget(QtWidgets.QListWidget):
    delete_key_pressed = QtCore.pyqtSignal()

    def __init__(self,  parent=None):
        super(ListWidget, self).__init__(parent)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Delete:
            self.delete_key_pressed.emit()
        else:
            super().keyPressEvent(event)


class ListView(QtWidgets.QListView):

    delete_key_pressed = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(ListView, self).__init__(parent)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Delete:
            self.delete_key_pressed.emit()
        else:
            super().keyPressEvent(event)


class getExistingDirectories(QFileDialog):
    def __init__(self, *args, **kwargs):
        super(getExistingDirectories, self).__init__(*args, **kwargs)
        self.setOption(self.DontUseNativeDialog, True)
        self.setFileMode(self.Directory)
        self.setOption(self.ShowDirsOnly, True)
        self.findChildren(QListView)[0].setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.findChildren(QTreeView)[0].setSelectionMode(QAbstractItemView.ExtendedSelection)
