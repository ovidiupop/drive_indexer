from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QSortFilterProxyModel, Qt, QModelIndex
from PyQt5.QtWidgets import QFileDialog, QAbstractItemView

from mymodules import GDBModule as gdb
from mymodules.ComponentsModule import PushButton, TableViewAutoCols
from mymodules.GlobalFunctions import iconForButton, confirmationDialog
from mymodules.ModelsModule import FoldersModel
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

        self.folders_indexed_table = TableViewAutoCols(None)
        self.folders_indexed_table_model = FoldersModel(self.folders_indexed_table)
        self.folders_indexed_table.setModel(self.folders_indexed_table_model)
        self.folders_indexed_table.setColumnHidden(self.folders_indexed_table_model.fieldIndex("id"), True)
        self.folders_indexed_table.setColumns([0.1, 0.75, 0.14, 0.10])
        self.folders_indexed_table.setMaximumHeight(200)

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
        folders_column_layout.addWidget(self.folders_indexed_table)
        folders_column_layout.addWidget(self.results_progress_group)
        folders_column_layout.addStretch()

        self.folders_section_layout = QtWidgets.QHBoxLayout()
        self.folders_section_layout.addLayout(buttons_column_layout)
        self.folders_section_layout.addLayout(folders_column_layout)

        self.closeButtonAfterIndex()
        self.fillPreferredFolders()

    def refreshTable(self):
        self.folders_indexed_table.setModel(self.folders_indexed_table_model)
        self.folders_indexed_table_model.select()

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
        self.folders_indexed_table.clearSelection()
        # self.refreshTable()

    # table
    def removeAllFolders(self):
        self.folders_indexed_table.selectAll()
        self.removeFolders()

    # table
    def removeFolders(self):
        indexes = self.folders_indexed_table.selectedIndexes()
        count = len(indexes)
        if count > 0:
            names = [self.folders_indexed_table.model().data(index) for index in indexes if index.column() == 1]
            confirmation_text = f"Next folders will be removed:<br><br>{'<br>'.join(names)}! <br><br>Do you proceed?"
            confirm = confirmationDialog("Do you remove?", confirmation_text)
            if not confirm:
                return
            if gdb.deleteFoldersDB(names):
                self.refreshTable()
                message = f'Removed folder <br><br> {names[0]}' if count == 1 \
                    else f"Removed folders <br><br>{'<br>'.join(names)}"
                QtWidgets.QMessageBox.information(self.parent(), 'Folder removes', message)
            else:
                QtWidgets.QMessageBox.critical(self.parent(), 'Error', "Database wasn't cleaned!")

    def unselectFolderSources(self):
        # TODO Check
        self.folders_indexed_table.clearSelection()

    def selectLastItemFolderSources(self):
        items = self.folders_indexed_table_model.rowCount()
        self.folders_indexed_table.selectRow(int(items) - 1)

    def selectAndAddNewFolder(self):
        self.unselectFolderSources()
        home_path = QtCore.QDir.homePath()
        folder_name = QFileDialog.getExistingDirectory(
            self, directory=home_path, caption="Select a folder")
        if folder_name:
            if gdb.folderExists(folder_name):
                QtWidgets.QMessageBox.warning(self.parent(), 'Folder indexed', 'Folder is already indexed')
            else:
                response = folderCanBeIndexed(folder_name)
                if response[0]:
                    serial = response[1]
                    if self.alreadyIndexed(folder_name, serial):
                        return None
                    if gdb.addFolder(folder_name, serial):
                        self.refreshTable()
                        self.selectLastItemFolderSources()
                        # start indexing of new folder
                        self.folder_added.emit()
                        self.refreshTable()
                else:
                    QtWidgets.QMessageBox.critical(self.parent(),
                                                   'Error!',
                                                   f"Drive for this folder isn't available for index!"
                                                                   f"\nPlease add {response[1]} in Drives section!")

    def alreadyIndexed(self, folder, serial):
        parents_of_drive = gdb.foldersOfDrive(serial)
        if parents_of_drive:
            for parent_folder in parents_of_drive:
                if folder.startswith(parent_folder):
                    QtWidgets.QMessageBox.warning(self.parent(),
                                                  'Exists!',
                                                  f"You already have indexed this folder within "
                                                  f"<b>{parent_folder}</b> folder!<br>Will not be added again!")
                    return True
        return False
