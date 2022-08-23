import sys
import resources



from PyQt5 import QtWidgets
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QAction

from mymodules import GDBModule as gdb, TabsModule
from mymodules.GlobalFunctions import tabIndexByName


class IndexerWindow(QMainWindow):
    def __init__(self, parent=None):
        super(IndexerWindow, self).__init__(parent)
        gdb.GDatabase()
        res = resources
        self.init_UI()

    def _createActions(self):
        # # Creating action using the first constructor
        self.export_all_action = QAction(QIcon(":all-results.svg"), "&All Search Results", self)
        self.export_selected_action = QAction(QIcon(":selected-results.svg"), "&Selected Search Results", self)
        self.exit_action = QAction(QIcon(":application-exit.svg"), "E&xit", self)

        self.settings_drives_action = QAction(QIcon(":drives.svg"), "&Drives", self)
        self.settings_categories_action = QAction(QIcon(":categories.svg"), "&Categories", self)
        self.settings_folders_action = QAction(QIcon(":folders.svg"), "&Folders", self)
        self.settings_extensions_actions = QAction(QIcon(":extensions.svg"), "&Extensions", self)

        self.help_content_action = QAction(QIcon(":help-contents.svg"), "&Help Content", self)
        self.about_action = QAction(QIcon(":help-about.svg"), "&About", self)

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
        self.export_menu = self.file_menu.addMenu(QIcon(":export.svg"), "CSV &Export")
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
        self.tabs_view = TabsModule.TabsView(self)
        self.tabs = self.tabs_view.tabs_main

    def init_UI(self):
        self._createTabs()
        self.setCentralWidget(self.tabs)
        self.resize(1000, 800)
        self.setWindowTitle("File Indexer")
        self.setWindowIcon(QIcon(":app_logo_32.png"))
        self._createActions()
        self._createMenuBar()
        self._connectActions()
        self._createStatusBar()
        self.show()

    def _createStatusBar(self):
        self.statusbar = self.statusBar()

    def exportAllResults(self):
        self.tabs_view.search.export_all_results_signal.emit()

    def exportSelectedResults(self):
        self.tabs_view.search.export_selected_results_signal.emit()

    def switchTab(self, tab):
        tabs_main_index = tabIndexByName(self.tabs_view.tabs_main, "Settings")
        self.tabs_view.tabs_main.setCurrentIndex(tabs_main_index)
        tab_settings_index = tabIndexByName(self.tabs_view.tabs_settings, tab)
        self.tabs_view.tabs_settings.setCurrentIndex(tab_settings_index)

    def helpContent(self):
        pass

    def about(self):
        QtWidgets.QMessageBox.about(self, 'About Indexer',
            "<h4>Find all your files in a single place</h4><br>"
            "Index your entire drive collection in one place and find anything in a second!<br><br>"
            "This app was developed as a study project when I started learning Python and Qt,"
            "so its code can be improved and also new features can be added!<br><br>"
            "Any suggestions and criticisms are welcome!<br><br>"
            "© 2022 Ovidiu Pop"
                                    )


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    mw = IndexerWindow()
    sys.exit(app.exec())
