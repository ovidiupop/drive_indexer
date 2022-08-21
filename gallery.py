import sys

from PyQt5.QtCore import QSize
from PyQt5.QtGui import QIcon

import resources

from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QMainWindow, QAction, QMenu, QLabel, QCheckBox, QToolBar, QWidget

from mymodules import GDBModule as gdb, TabsModule
from mymodules.GlobalFunctions import tabIndexByName


class IndexerWindow(QMainWindow):
    def __init__(self, parent=None):
        super(IndexerWindow, self).__init__(parent)
        gdb.GDatabase()

        self.init_UI()

    def _createActions(self):
        # # Creating action using the first constructor
        self.export_all_action = QAction("&All Results", self)
        self.export_selected_action = QAction("&Selected Results", self)
        self.exit_action = QAction("&Exit", self)

        self.settings_drives_action = QAction("&Drives", self)
        self.settings_categories_action = QAction("&Categories", self)
        self.settings_folders_action = QAction("&Folders", self)
        self.settings_extensions_actions = QAction("&Extensions", self)

        self.help_content_action = QAction("&Help Content", self)
        self.about_action = QAction("&About", self)

    def exportAllResults(self):
        print('exportAllResults')

    def exportSelectedResults(self):
        print('exportSelectedResults')

    def switchTab(self, tab):
       tabs = self.tabs.findChildren(QtWidgets.QTabWidget)

       tab_folder_index = tabIndexByName(tabs, tab)
       tabs.setCurrentIndex(tab_folder_index)
       print(tab)

    def helpContent(self):
        pass

    def about(self):
        pass

    def _connectActions(self):
        # Connect File actions
        self.export_all_action.triggered.connect(self.exportAllResults)
        self.export_selected_action.triggered.connect(self.exportSelectedResults)
        self.exit_action.triggered.connect(self.close)

        # Connect Settings actions
        self.settings_drives_action.triggered.connect(lambda: self.switchTab('Drives'))
        self.settings_categories_action.triggered.connect(lambda: self.switchTab('Categories'))
        self.settings_folders_action.triggered.connect(lambda: self.switchTab('Folders'))
        self.settings_extensions_actions.triggered.connect(lambda: self.switchTab('Extensions'))

        # Connect Help actions
        self.help_content_action.triggered.connect(self.helpContent)
        self.about_action.triggered.connect(self.about)

    def _createMenuBar(self):

        self.menu_bar = self.menuBar()

        self.file_menu = self.menu_bar.addMenu("&File")
        self.export_menu = self.file_menu.addMenu("&Export")
        self.export_menu.addAction(self.export_all_action)
        self.export_menu.addAction(self.export_selected_action)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.exit_action)

        self.settings_menu = self.menu_bar.addMenu("&Settings")
        self.settings_menu.addAction(self.settings_drives_action)
        self.settings_menu.addAction(self.settings_categories_action)
        self.settings_menu.addAction(self.settings_folders_action)
        self.settings_menu.addAction(self.settings_extensions_actions)

        self.help_menu = self.menu_bar.addMenu('&Help')
        self.help_menu.addAction(self.help_content_action)
        self.help_menu.addAction(self.about_action)

    def setStatusBar(self, text):
        self.statusbar.showMessage(text)

    def _createTabs(self):
        # remaining code
        tabs_view = TabsModule.TabsView(self)
        self.tabs = tabs_view.tabs_main

    def init_UI(self):
        self._createTabs()
        self.setCentralWidget(self.tabs)
        self.resize(1000, 800)
        self.setWindowTitle("File Indexer")
        self._createActions()
        self._createMenuBar()
        self._connectActions()
        self._createStatusBar()
        # End main UI code
        self.show()

    def _createStatusBar(self):
        self.statusbar = self.statusBar()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    mw = IndexerWindow()
    sys.exit(app.exec())
