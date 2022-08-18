import sys

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow

from mymodules import GDBModule as gdb, TabsModule
from mymodules.CategoriesModule import CategoriesSelector
from mymodules.SearchModule import Search


class IndexerWindow(QMainWindow):
    def __init__(self, parent=None):
        super(IndexerWindow, self).__init__(parent)
        gdb.GDatabase()

        # search = Search()
        # categories_selector = CategoriesSelector(None)
        # categories_selector.set_categories_on_search.connect(self.bla)

        # drives = gdb.getAll('extensions', ['extension'])
        # print(drives, len(drives))

        # remaining code
        self.statusbar = self.statusBar()
        tabs_view = TabsModule.TabsView(self)
        self.tabs = tabs_view.tabs_main

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

        settings_menu = self.menuBar()
        settings_menu = settings_menu .addMenu('Settings')
        settings_extensions_action = settings_menu.addAction('Extensions')
        settings_folders_action = settings_menu.addAction('Folders')
        settings_drives_action = settings_menu.addAction('Drives')

        help_menu = self.menuBar()
        help_menu = help_menu .addMenu('Help')
        about_action = help_menu.addAction('About')

        # End main UI code
        self.show()


def set_print_number(self, number):
    print(number)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    mw = IndexerWindow()
    sys.exit(app.exec())
