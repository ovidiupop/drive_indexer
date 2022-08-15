from PyQt5 import QtWidgets, QtCore, QtGui


class TableViewAutoCols(QtWidgets.QTableView):
    """ Override QTableView to override resizeEvent method
    """
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


class PushButton(QtWidgets.QPushButton):
    """
    Push button supporting icon to left/right
    """
    def __init__(self, *args, **kwargs):
        super(PushButton, self).__init__(*args, **kwargs)
        self.styleSheet = "QPushButton { text-align: left; padding: 5}"
        icon = self.icon()
        icon_size = self.iconSize()
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


