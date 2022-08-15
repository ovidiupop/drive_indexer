import sys

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, QMessageBox

from mymodules import GDBModule as gdb, TabsModule


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


class IndexerWindow(QMainWindow):
    def __init__(self, parent=None):
        super(IndexerWindow, self).__init__(parent)
        gdb.GDatabase()

        # remaining code
        self.statusbar = self.statusBar()
        self.tabs = TabsModule.TabsView(self).tabs_main
        self.setCentralWidget(self.tabs)
        self.init_UI()

    def setStatusBar(self, text):
        self.statusbar.showMessage(text)

    def init_UI(self):
        self.resize(1000, 800)
        self.setWindowTitle("File Indexer")

        # MENU
        file_menu = self.menuBar()
        file_menu = file_menu.addMenu('File')
        open_action = file_menu.addAction('Open')
        save_action = file_menu.addAction('Save')
        file_menu.addSeparator()
        quit_action = file_menu.addAction('Quit', self.close)

        settings_menu  = self.menuBar()
        settings_menu = settings_menu .addMenu('Settings')
        settings_extensions_action = settings_menu.addAction('Extensions')
        settings_folders_action = settings_menu.addAction('Folders')
        settings_drives_action = settings_menu.addAction('Drives')

        # Status Bar
        # self.statusbar = self.statusBar()

        #
        # self.print_number = None

        # End main UI code
        self.show()


def set_print_number(self, number):
    print(number)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    mw = IndexerWindow()
    sys.exit(app.exec())
