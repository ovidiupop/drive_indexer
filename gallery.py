import sys

from PyQt5.QtGui import QIcon

import resources

from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QMainWindow, QAction, QMenu

from mymodules import GDBModule as gdb, TabsModule


class IndexerWindow(QMainWindow):
    def __init__(self, parent=None):
        super(IndexerWindow, self).__init__(parent)
        gdb.GDatabase()

        self._createActions()
        self._createMenuBar()
        self._createStatusBar()
        self._createTabs()

        self.init_UI()

    def _createTabs(self):
        # remaining code
        tabs_view = TabsModule.TabsView(self)
        self.tabs = tabs_view.tabs_main

    def _createStatusBar(self):
        self.statusbar = self.statusBar()

    def _createActions(self):
        # # Creating action using the first constructor
        self.export_all_action = QAction("Export &All Results", self)
        self.export_selected_action = QAction("Export &Selected Results", self)
        self.exit_action = QAction("&Exit", self)

        self.settings_drives = QAction("&Drives", self)
        self.settings_categories = QAction("&Categories", self)
        self.settings_folders = QAction("&Folders", self)
        self.settings_extensions = QAction("&Extensions", self)

        self.help_content_action = QAction("&Help Content", self)
        self.about_action = QAction("&About", self)

    def _createMenuBar(self):
        # MENU
        menuBar = self.menuBar()

        helpMenu = menuBar.addMenu(QIcon(":help-content.svg"), "&Help")

        # Using a QMenu object
        fileMenu = QMenu("&File", self)
        menuBar.addMenu(fileMenu)
        # Using a title
        editMenu = menuBar.addMenu("&Edit")
        # Using an icon and a title



        # file_menu = self.menuBar()
        # file_menu = file_menu.addMenu("&File")
        # file_menu.addAction(self.export_all_action)
        # file_menu.addAction(self.export_selected_action)
        # file_menu.addSeparator()
        # file_menu.addAction(self.exit_action)
        #
        # settings_menu = self.menuBar()
        # settings_menu = settings_menu.addMenu("&Settings")
        # settings_menu.addAction(self.settings_drives)
        # settings_menu.addAction(self.settings_categories)
        # settings_menu.addAction(self.settings_folders)
        # settings_menu.addAction(self.settings_extensions)
        #
        # help_menu = self.menuBar()
        # help_menu = help_menu.addMenu('&Help')
        # help_menu.addAction(self.about_action)
        # help_menu.addAction(self.help_content_action)

    def setStatusBar(self, text):
        self.statusbar.showMessage(text)

    def init_UI(self):
        self.setCentralWidget(self.tabs)
        self.resize(1000, 800)
        self.setWindowTitle("File Indexer")

        # # MENU
        # file_menu = self.menuBar()
        # file_menu = file_menu.addMenu('&File')
        #
        # open_action = file_menu.addAction('&Open')
        # save_action = file_menu.addAction('&Save')
        # file_menu.addSeparator()
        # quit_action = file_menu.addAction('&Quit', self.close)
        #
        # settings_menu = self.menuBar()
        # settings_menu = settings_menu .addMenu('Settings')
        # settings_extensions_action = settings_menu.addAction('Extensions')
        # settings_folders_action = settings_menu.addAction('Folders')
        # settings_drives_action = settings_menu.addAction('Drives')
        #
        # help_menu = self.menuBar()
        # help_menu = help_menu .addMenu('Help')
        # about_action = help_menu.addAction('About')

        # End main UI code
        self.show()


def set_print_number(self, number):
    print(number)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    mw = IndexerWindow()
    sys.exit(app.exec())
