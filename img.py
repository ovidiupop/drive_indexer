import sys

from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QMainWindow, QGridLayout


class Image(QtWidgets.QWidget):
    def __init__(self, file, parent=None):
        super(Image, self).__init__(parent)
        self.file = file
        self.resize(800, 600)
        pixmap = QPixmap(file)

        self.image_width = pixmap.width()
        self.image_height = pixmap.height()

        if self.image_height > self.width() or self.image_height > self.height():
            image = pixmap.scaled(self.width(), self.height(), Qt.KeepAspectRatio)
        else:
            image = pixmap.scaled(self.image_width, self.image_height, Qt.KeepAspectRatio)

        self.label = QtWidgets.QLabel()
        self.label.setPixmap(image)

        l_h = QtWidgets.QHBoxLayout()
        l_h.setAlignment(Qt.AlignCenter)
        l_h.addWidget(self.label)
        self.parent().layout.addLayout(l_h)

    def resizeEvent(self, event):
        if self.image_height < self.parent().width() or self.image_height < self.parent().height():
            return
        pixmap1 = QPixmap(self.file)
        pixmap = pixmap1.scaled(self.parent().width(), self.parent().height(), Qt.KeepAspectRatio)
        self.label.setPixmap(pixmap)
        self.label.resize(self.parent().width(), self.parent().height())


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        # self.file = 'imagine.jpg'
        self.file = 'accordion.png'

        self.layout = QtWidgets.QHBoxLayout()
        Image(self.file, self)

        gr = QtWidgets.QGroupBox()
        gr.setLayout(self.layout)
        self.setCentralWidget(gr)
        self.show()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    mw = MainWindow()
    sys.exit(app.exec())