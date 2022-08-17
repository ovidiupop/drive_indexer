from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QFileDialog

from mymodules import GDBModule as gdb
from mymodules.ComponentsModule import PushButton
from mymodules.GlobalFunctions import iconForButton
from mymodules.SystemModule import folderCanBeIndexed


class Folders(QtWidgets.QWidget):
    folder_added = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(Folders, self).__init__(parent)
        self.hide_unmounted_drives = True
        self.folder_add_button = PushButton('Add')
        self.folder_remove_all_button = PushButton('Remove All')
        self.folder_remove_selected_button = PushButton('Remove')
        self.folder_reindex_button = PushButton('Re/Index')

        self.close_indexed_results_button = PushButton()
        self.close_indexed_results_button.hide()
        self.indexing_progress_bar = QtWidgets.QProgressBar()
        self.indexing_progress_bar.hide()
        self.report_indexed_path_label = QtWidgets.QLabel('')
        self.total_folders_indexed_label = QtWidgets.QLabel('')

        self.folders_indexed = QtWidgets.QListWidget()
        self.folders_indexed.setMaximumHeight(200)

        self.results_progress_group = QtWidgets.QGroupBox('Results')
        self.results_progress_group.hide()

        self.folder_reindex_button.setIcon(iconForButton('SP_BrowserReload'))
        self.folder_remove_all_button.setIcon(iconForButton('SP_DialogDiscardButton'))
        self.folder_add_button.setIcon(iconForButton('SP_DialogOpenButton'))
        self.folder_remove_selected_button.setIcon(iconForButton('SP_DialogResetButton'))

        self.close_indexed_results_button.setIcon(iconForButton('SP_DialogCloseButton'))
        self.folder_add_button.clicked.connect(self.selectAndAddNewFolder)
        self.folder_remove_all_button.clicked.connect(self.removeAllFolders)
        self.folder_remove_selected_button.clicked.connect(self.removeFolders)
        self.close_indexed_results_button.clicked.connect(self.hideResults)

        buttons_column_layout = QtWidgets.QVBoxLayout()
        buttons_column_layout.insertSpacing(10, 20)
        buttons_column_layout.addWidget(self.folder_add_button)
        buttons_column_layout.addWidget(self.folder_remove_selected_button)
        buttons_column_layout.addWidget(self.folder_remove_all_button)
        buttons_column_layout.addWidget(self.folder_reindex_button)
        buttons_column_layout.addStretch()
        # folders and progress of indexing
        folders_column_layout = QtWidgets.QVBoxLayout()
        folders_column_layout.addWidget(self.folders_indexed)
        folders_column_layout.addWidget(self.results_progress_group)
        folders_column_layout.addStretch()

        self.folders_section_layout = QtWidgets.QHBoxLayout()
        self.folders_section_layout.addLayout(buttons_column_layout)
        self.folders_section_layout.addLayout(folders_column_layout)

        self.closeButtonAfterIndex()
        self.fillPreferredFolders()

    def closeButtonAfterIndex(self):
        # close button for indexing report box
        close_results_layout = QtWidgets.QHBoxLayout()
        close_results_layout.addWidget(self.close_indexed_results_button)
        close_results_layout.setAlignment(QtCore.Qt.AlignRight)
        results_layout = QtWidgets.QVBoxLayout()
        results_layout.addLayout(close_results_layout)
        results_layout.addWidget(self.report_indexed_path_label)
        results_layout.addWidget(self.total_folders_indexed_label)
        self.results_progress_group.setLayout(results_layout)

    def hideResults(self):
        self.results_progress_group.hide()

    def fillPreferredFolders(self):
        self.folders_indexed.setSelectionMode(QtWidgets.QListWidget.ExtendedSelection)
        self.folders_indexed.addItems(gdb.allFolders())

    def removeAllFolders(self):
        self.folders_indexed.selectAll()
        self.removeFolders()

    def removeFolders(self):
        items = self.folders_indexed.selectedIndexes()
        count = len(items)
        if count > 0:
            names = [name.data() for name in items]
            confirmation_text = f"Next folders will be removed:<br><br>{'<br>'.join(names)}! <br><br>Do you proceed?"
            confirm = confirmationDialog("Do you remove?", confirmation_text)
            if not confirm:
                return
            if gdb.deleteFoldersDB(names):
                for _item in items:
                    self.folders_indexed.takeItem(self.folders_indexed.currentRow())
                message = f'Removed folder <br><br> {names[0]}' if count == 1 \
                    else f"Removed folders <br><br>{'<br>'.join(names)}"

                QtWidgets.QMessageBox.information(self, 'Folder removes', message)
            else:
                QtWidgets.QMessageBox.critical(self, 'Error', "Database wasn't cleaned!")

    def unselectFolderSources(self):
        self.folders_indexed.clearSelection()

    def selectLastItemFolderSources(self):
        items = self.folders_indexed.count()
        self.folders_indexed.setCurrentRow(int(items) - 1)

    def selectAndAddNewFolder(self):
        self.unselectFolderSources()
        home_path = QtCore.QDir.homePath()
        folder_name = QFileDialog.getExistingDirectory(
            self, directory=home_path, caption="Select a folder")
        if folder_name:
            if gdb.folderExists(folder_name):
                QtWidgets.QMessageBox.critical(self, 'Folder indexed', 'Folder is already indexed')
            else:
                response = folderCanBeIndexed(folder_name)
                if response[0]:
                    serial = response[1]
                    if gdb.addFolder(folder_name, serial):
                        self.folders_indexed.addItem(folder_name)
                        # select last inserted row
                        self.selectLastItemFolderSources()
                        # start indexing of new folder
                        self.folder_added.emit()
                else:
                    QtWidgets.QMessageBox.critical(self, 'Error!', f"Drive for this folder isn't available for index!"
                                                                   f"\nPlease add {response[1]} in Drives section!")
