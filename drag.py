import sys

from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QListWidget, QAbstractItemView, QMainWindow, QWidget, QVBoxLayout, QListWidgetItem, \
    QApplication


class ThumbListWidget(QListWidget):
    dropped = QtCore.pyqtSignal()
    _drag_info = []

    def __init__(self, type, name, parent=None):
        super(ThumbListWidget, self).__init__(parent)

        self.setObjectName(name)
        self.setIconSize(QtCore.QSize(124, 124))
        self.setDragDropMode(QAbstractItemView.DragDrop)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setAcceptDrops(True)

    def startDrag(self, actions):
        self._drag_info[:] = [str(self.objectName())]
        for item in self.selectedItems():
            self._drag_info.append(self.row(item))
        super(ThumbListWidget, self).startDrag(actions)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            super(ThumbListWidget, self).dragEnterEvent(event)

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.setDropAction(QtCore.Qt.MoveAction)
            event.accept()
        else:
            super(ThumbListWidget, self).dragMoveEvent(event)

    def dropEvent(self, event):
        print('dropEvent', event)
        if event.mimeData().hasUrls():
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()
            links = []
            for url in event.mimeData().urls():
                links.append(str(url.toLocalFile()))
            # self.emit(QtCore.SIGNAL("dropped"), links)
        elif self._drag_info:
            event.setDropAction(QtCore.Qt.MoveAction)
            super(ThumbListWidget, self).dropEvent(event)
            self.emit.dropped(list(self._drag_info))
            # self.emit(QtCore.SIGNAL("dropped"), list(self._drag_info))
        else:
            event.setDropAction(QtCore.Qt.MoveAction)
            super(ThumbListWidget, self).dropEvent(event)


class Dialog_01(QMainWindow):

    def __init__(self):
        super(QMainWindow,self).__init__()
        self.listItems={}

        myQWidget = QWidget()
        myBoxLayout = QVBoxLayout()
        myQWidget.setLayout(myBoxLayout)
        self.setCentralWidget(myQWidget)

        self.listWidgetA = ThumbListWidget(self, 'A')
        for i in range(12):
            QListWidgetItem( 'Item '+str(i), self.listWidgetA )
        myBoxLayout.addWidget(self.listWidgetA)

        self.listWidgetB = ThumbListWidget(self, 'B')
        myBoxLayout.addWidget(self.listWidgetB)

        self.listWidgetA.dropped.connect(self.items_dropped)
        self.listWidgetA.currentItemChanged.connect(self.item_clicked)

        self.listWidgetB.dropped.connect(self.items_dropped)
        self.listWidgetB.currentItemChanged.connect(self.item_clicked)

    def items_dropped(self, arg):
        print('items_dropped', arg)

    def item_clicked(self, arg):
        print(arg)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    dialog_1 = Dialog_01()
    dialog_1.show()
    dialog_1.resize(480,320)
    sys.exit(app.exec())

