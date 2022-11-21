import filecmp
import hashlib
import os
from collections import defaultdict

import pandas as pd
from PyQt5 import QtWidgets, QtCore, QtTest
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAbstractItemView, QFileDialog, QLabel

from mymodules import ComponentsModule, ModelsModule
from mymodules import GDBModule as gdb
from mymodules.ComponentsModule import PushButton
from mymodules.GlobalFunctions import HEADER_DUPLICATES_TABLE, spinner, CSV_COLUMN_SEPARATOR, getPreference, \
    getDefaultDir, CSV_LINE_SEPARATOR, HEADER_DUPLICATES_STRICT_TABLE, confirmationDialog


class DuplicateFinder(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super(DuplicateFinder, self).__init__(parent)

        self.find_duplicate_label = QLabel('Find duplicates by name and size')
        self.find_duplicate_button = PushButton('Find')
        self.find_duplicate_button.setMinimumWidth(200)
        self.find_duplicate_button.setIcon(QIcon(':magnifier.png'))
        self.find_duplicate_button.setStyleSheet("""QPushButton { text-align: center; }""")
        self.find_duplicate_button.setFixedSize(180, 40)
        self.find_duplicate_button.clicked.connect(self.findDuplicates)

        # self.find_strict_duplicate_label = QLabel('Find duplicates on mounted drives')
        # self.find_strict_duplicate_button = PushButton('Find')
        # self.find_strict_duplicate_button.setMinimumWidth(200)
        # self.find_strict_duplicate_button.setIcon(QIcon(':magnifier.png'))
        # self.find_strict_duplicate_button.setStyleSheet("""QPushButton { text-align: center; }""")
        # self.find_strict_duplicate_button.setFixedSize(180, 40)
        # self.find_strict_duplicate_button.clicked.connect(self.findStrictDuplicates)

        self.export_duplicate_label = QLabel('Export duplicates to CSV')
        self.export_duplicate_button = PushButton('Export')
        self.export_duplicate_button.setMinimumWidth(200)
        self.export_duplicate_button.setIcon(QIcon(':table_export.png'))
        self.export_duplicate_button.setStyleSheet("""QPushButton { text-align: center; }""")
        self.export_duplicate_button.setFixedSize(180, 40)
        self.export_duplicate_button.clicked.connect(self.exportAllResultsToCSV)

        # self.remove_checked_label = QLabel('Remove checked')
        # self.remove_checked_button = PushButton('Remove checked')
        # self.remove_checked_button.setMinimumWidth(200)
        # self.remove_checked_button.setIcon(QIcon(':cross.png'))
        # self.remove_checked_button.setStyleSheet("""QPushButton { text-align: center; }""")
        # self.remove_checked_button.setFixedSize(180, 40)
        # self.remove_checked_button.clicked.connect(self.removeChecked)

        self.spinner = spinner(parent)
        self.spinner.hide()
        self.searching_label = QtWidgets.QLabel('Found')
        self.searching_label.hide()
        # self.toggleRemoveSelected(False)

        # set table for results
        self.duplicate_results_table = ComponentsModule.TableViewAutoCols(None)
        self.duplicate_results_table.setColumns([0.35, 0.25, 0.10, 0.10, 0.15, 0.05])
        self.duplicate_results_table_model = ModelsModule.DuplicateResultsTableModel(
            pd.DataFrame([], columns=HEADER_DUPLICATES_TABLE), self.duplicate_results_table)

        # self.duplicate_strict_results_table = ComponentsModule.TableViewAutoCols(None, selection='Multiple')
        # self.duplicate_strict_results_table.setColumns([0.35, 0.05, 0.05, 0.40, 0.10, 0.05])
        # self.duplicate_strict_results_table.hide()
        # self.duplicate_strict_results_table_model = ModelsModule.DuplicateResultsTableModel(
        #     pd.DataFrame([], columns=HEADER_DUPLICATES_STRICT_TABLE), self.duplicate_strict_results_table)

        v_lay_find_duplicates = QtWidgets.QVBoxLayout()
        v_lay_find_duplicates.addWidget(self.find_duplicate_label)
        v_lay_find_duplicates.addWidget(self.find_duplicate_button)

        # v_lay_find_strict_duplicates = QtWidgets.QVBoxLayout()
        # v_lay_find_strict_duplicates.addWidget(self.find_strict_duplicate_label)
        # v_lay_find_strict_duplicates.addWidget(self.find_strict_duplicate_button)

        v_lay_export_duplicates = QtWidgets.QVBoxLayout()
        v_lay_export_duplicates.addWidget(self.export_duplicate_label)
        v_lay_export_duplicates.addWidget(self.export_duplicate_button)

        # v_lay_remove_checked = QtWidgets.QVBoxLayout()
        # v_lay_remove_checked.addWidget(self.remove_checked_label)
        # v_lay_remove_checked.addWidget(self.remove_checked_button)

        h_row = QtWidgets.QHBoxLayout()
        h_row.addLayout(v_lay_find_duplicates)
        # h_row.addLayout(v_lay_find_strict_duplicates)
        h_row.addLayout(v_lay_export_duplicates)
        # h_row.addLayout(v_lay_remove_checked)
        h_row.addStretch()

        # search results section
        duplicate_results_layout = QtWidgets.QVBoxLayout()
        row_over_table = QtWidgets.QHBoxLayout()
        row_over_table.addWidget(self.spinner, 0, Qt.AlignLeft)
        row_over_table.addWidget(self.searching_label, 0, Qt.AlignLeft)
        row_over_table.addStretch()

        duplicate_results_layout.addLayout(row_over_table)
        duplicate_results_layout.addWidget(self.duplicate_results_table)
        # duplicate_results_layout.addWidget(self.duplicate_strict_results_table)

        v_lay = QtWidgets.QVBoxLayout()
        v_lay.addLayout(h_row)
        v_lay.addLayout(duplicate_results_layout)

        self.find_duplicate_tab_layout = QtWidgets.QVBoxLayout()
        self.find_duplicate_tab_layout.addLayout(v_lay)

    # def toggleRemoveSelected(self, show):
    #     self.remove_checked_label.setVisible(show)
    #     self.remove_checked_button.setVisible(show)

    @QtCore.pyqtSlot()
    def findDuplicates(self):
        self.searching_label.show()
        self.spinner.show()
        self.searching_label.setText(f'Please wait! Searching for duplicates...')
        self.searching_label.show()
        QtTest.QTest.qWait(1000)
        results = gdb.findDuplicates()
        if results:
            self.updateResults(results)

    @QtCore.pyqtSlot()
    def findStrictDuplicates(self):
        self.spinner.show()
        self.searching_label.setText(f'Please wait! Searching for strict duplicates...')
        self.searching_label.show()
        QtTest.QTest.qWait(1000)
        results = gdb.findDuplicatesBySize()
        if results:
            # strict = self.findStrict(results)
            strict = self.checkForDuplicates(results)
            strict = self.formatResultsForTable(strict)

            self.updateStrictResults(strict)
            self.toggleRemoveSelected(True)
        else:
            self.searching_label.setText(f'There are not any duplicates!')
            self.spinner.hide()
            self.toggleRemoveSelected(False)

    def sortResultsBySize(self, results):
        paths = defaultdict(list)
        for result in results:
            size = result[2]
            full_path = os.path.join(result[0], result[1])
            path = {'full_path': full_path, 'filename': result[1], 'size': size, 'drive': result[4]}
            old_path = paths[size]
            old_path.append(path)
            paths[size] = old_path

        return paths

    def checkForDuplicates(self, results):

        hashes_by_size = defaultdict(list)  # dict of size_in_bytes: [full_path_to_file1, full_path_to_file2, ]
        hashes_on_1k = defaultdict(list)  # dict of (hash1k, size_in_bytes): [full_path_to_file1, full_path_to_file2, ]
        hashes_full = {}  # dict of full_file_hash: full_path_to_file_string
        duplicates = defaultdict(list)

        paths = self.sortResultsBySize(results)
        if len(paths) < 1:
            return []

        for path, item in paths.items():
            for data in item:
                # get all files that have the same size - they are the collision candidates
                # full_path = os.path.join(dirpath, filename)
                full_path = data['full_path']

                try:
                    # if the target is a symlink (soft one), this will
                    # dereference it - change the value to the actual target file
                    full_path = os.path.realpath(full_path)
                    file_size = os.path.getsize(full_path)
                    hashes_by_size[file_size].append(full_path)
                except (OSError,):
                    # not accessible (permissions, etc) - pass on
                    continue

        # For all files with the same file size, get their hash on the 1st 1024 bytes only
        for size_in_bytes, files in hashes_by_size.items():
            if len(files) < 2:
                continue  # this file size is unique, no need to spend CPU cycles on it

            for filename in files:
                try:
                    small_hash = self.getHash(filename, first_chunk_only=True)
                    # the key is the hash on the first 1024 bytes plus the size - to
                    # avoid collisions on equal hashes in the first part of the file
                    # credits to @Futal for the optimization
                    hashes_on_1k[(small_hash, size_in_bytes)].append(filename)
                except (OSError,):
                    # the file access might've changed till the exec point got here
                    continue

        # For all files with the hash on the 1st 1024 bytes,
        # get their hash on the full file - collisions will be duplicates
        for __, files_list in hashes_on_1k.items():
            if len(files_list) < 2:
                continue  # this hash of fist 1k file bytes is unique, no need to spend cpy cycles on it

            for filename in files_list:
                try:
                    full_hash = self.getHash(filename, first_chunk_only=False)
                    duplicate = hashes_full.get(full_hash)

                    if duplicate:
                        duplicate_data = self.dataForPath(paths, duplicate)
                        filename_data = self.dataForPath(paths, filename)

                        duplicate_drive = duplicate_data[0]
                        duplicate_size = duplicate_data[1]
                        filename_drive = filename_data[0]
                        filename_size = filename_data[1]

                        # data.append([reference, is_reference, size, path, drive, 1])
                        # filename_drive = self.driveForPath(paths, filename)
                        # duplicates[duplicate].append([filename, filename_drive, duplicate, duplicate_drive])

                        # data.append([reference, is_reference, size, path, drive, 1])
                        duplicates[duplicate_size].append([duplicate, 1, duplicate_size, duplicate, duplicate_drive, 1])
                        duplicates[duplicate_size].append([duplicate, 0, filename_size, filename, filename_drive, 0])

                        # duplicates[duplicate_size].append([duplicate_size, duplicate, duplicate_drive])
                        # duplicates[duplicate_size].append([filename_size, filename, filename_drive])

                        # print("Duplicate found: {} from {} AND {} from {}".format(duplicate, duplicate_drive, filename,
                        #                                                           filename_drive))

                    else:
                        hashes_full[full_hash] = filename
                except (OSError,):
                    # the file access might've changed till the exec point got here
                    continue

        return duplicates

    def dataForPath(self, paths, active_full_path):
        for size, items in paths.items():
            for item in items:
                if item['full_path'] == active_full_path:
                    return [item['drive'], item['size']]
        return None

    def driveForPath(self, paths, active_full_path):
        for size, items in paths.items():
            for item in items:
                if item['full_path'] == active_full_path:
                    return item['drive']
        return None

    def chunkReader(self, fobj, chunk_size=1024):
        """Generator that reads a file in chunks of bytes"""
        while True:
            chunk = fobj.read(chunk_size)
            if not chunk:
                return
            yield chunk

    def getHash(self, filename, first_chunk_only=False, hash=hashlib.sha1):
        hashobj = hash()
        file_object = open(filename, 'rb')

        if first_chunk_only:
            hashobj.update(file_object.read(1024))
        else:
            for chunk in self.chunkReader(file_object):
                hashobj.update(chunk)
        hashed = hashobj.digest()

        file_object.close()
        return hashed

    def updateResults(self, results):
        self.duplicate_results_table.show()
        # self.duplicate_strict_results_table.hide()

        self.duplicate_results_table_model = ModelsModule.DuplicateResultsTableModel(
            pd.DataFrame(results, columns=HEADER_DUPLICATES_TABLE), self.duplicate_results_table)

        self.duplicate_results_table.setModel(self.duplicate_results_table_model)
        self.duplicate_results_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.spinner.hide()
        count_results = len(results) if results else 0
        self.searching_label.setText(f'Found: {count_results} results')
        self.duplicate_results_table.setSortingEnabled(True)
        self.duplicate_results_table_model.sort(2, Qt.DescendingOrder)

    @QtCore.pyqtSlot()
    def exportAllResultsToCSV(self):
        # if self.duplicate_results_table.isVisible():
        model = self.duplicate_results_table.model()
        # else:
        #     model = self.duplicate_strict_results_table.model()

        columns = model.columnCount()
        rows = model.rowCount()
        results = []
        for row in range(0, rows):
            one_line = []
            for col in range(0, columns):
                if col != 5:
                    val = model.data(model.index(row, col), Qt.DisplayRole)
                else:
                    val = model.data(model.index(row, col), Qt.CheckStateRole)
                    val = "Remove" if val else ""

                val = val.replace(CSV_COLUMN_SEPARATOR, '_')
                # we have to convert values to string if we wish to concatenate them
                if not isinstance(val, str):
                    val = '%s' % val
                one_line.append(val)
            line = CSV_COLUMN_SEPARATOR.join(one_line)
            results.append(line)
        return self.putInFile(results)

    # we have to pass data as list
    def putInFile(self, data):
        if not data:
            QtWidgets.QMessageBox.information(self, 'Nothing to export', "There is nothing to export<br>")
            return False

        if int(getPreference('header_to_csv')):
            if self.duplicate_results_table.isVisible():
                header = CSV_COLUMN_SEPARATOR.join(HEADER_DUPLICATES_TABLE)
            else:
                header = CSV_COLUMN_SEPARATOR.join(HEADER_DUPLICATES_STRICT_TABLE)
            data.insert(0, header)

        default_dir = getDefaultDir()
        default_filename = os.path.join(default_dir, "")
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save CSV", default_filename, "CSV Files (*.csv)"
        )
        if filename:
            file = open(filename, 'w')
            text = CSV_LINE_SEPARATOR.join(data)
            file.write(text)
            file.close()
            QtWidgets.QMessageBox.information(None, 'Export CSV', 'Exported successfully!')
            return

    @QtCore.pyqtSlot()
    def removeChecked(self):
        # we will remove files only if are strict because
        # there are mounted the drives that we checked
        if self.duplicate_results_table.isVisible():
            return False

        indexes = self.duplicate_strict_results_table.selectedIndexes()
        count = len(indexes)
        if count < 1:
            message = f'You have to select some rows to remove the checked files!'
            QtWidgets.QMessageBox.information(self.parent(), 'Select some rows', message)
            return

        confirmation_text = f"Are you sure you wish to remove the checked files from selected rows?" \
                            f"<br>The files will be physical removed from drive(s)." \
                            f"<br>Do you proceed?"

        confirm = confirmationDialog("Remove files?", confirmation_text)
        if not confirm:
            return
        self.spinner.show()
        files = self.prepareFilesForRemove(indexes)

        if len(files) > 0:
            for path in files:
                full_path = os.path.realpath(path)
                # if os.path.exists(full_path):
                try:
                    os.remove(path)
                    removed_path = [os.path.dirname(full_path), os.path.basename(full_path)]
                    gdb.cleanRemovedDuplicates(removed_path[0], removed_path[1])
                    print("% s removed successfully" % path)
                except OSError as error:
                    print(error)
                    print("File path can not be removed")
        self.spinner.hide()

    def prepareFilesForRemove(self, indexes):
        files = []
        model = self.duplicate_strict_results_table.model()
        for index in indexes:
            val = model.data(model.index(index.row(), 5), Qt.CheckStateRole)
            if val == 2:  # Remove
                path = model.data(model.index(index.row(), 3), Qt.DisplayRole)
                if path not in files:
                    files.append(path)
        return files

        # model = self.duplicate_strict_results_table.model()
        # if model:
        #     self.spinner.show()
        #     QtTest.QTest.qWait(1000)
        #     columns = model.columnCount()
        #     rows = model.rowCount()
        #     results = []
        #
        #     for row in range(0, rows):
        #         for col in range(0, columns):
        #             if col == 5:
        #                 val = model.data(model.index(row, col), Qt.CheckStateRole)
        #                 if val == 2:  # Remove
        #                     path = model.data(model.index(row, 3), Qt.DisplayRole)
        #                     full_path = os.path.realpath(path)
        #                     if os.path.exists(full_path):
        #                         if os.remove(full_path):
        #                             print(full_path)
        #                             results.append(full_path)
        #                         else:
        #                             print(f'Not removed {full_path}')
        #     print(results)


    def formatResultsForTable(self, results):

        data = []
        # for size, lists in results.items():
        #     for reference, duplicates in lists.items():
        #         for path, is_reference, drive in duplicates:
        #             data.append([reference, is_reference, size, path, drive, 1])
        # return data

        exists = []
        for size, lists in results.items():
            for alist in lists:
                if alist[1] == 1:
                    if alist[0] not in exists:
                        exists.append(alist[0])
                        data.append(alist)
                else:
                    data.append(alist)
        return data

    def updateStrictResults(self, results):
        self.duplicate_results_table.hide()
        self.duplicate_strict_results_table.show()
        self.spinner.hide()
        self.searching_label.hide()

        self.duplicate_strict_results_table_model = ModelsModule.DuplicateStrictResultsTableModel(
            pd.DataFrame(results, columns=HEADER_DUPLICATES_STRICT_TABLE), self.duplicate_strict_results_table)

        self.duplicate_strict_results_table.setModel(self.duplicate_strict_results_table_model)
        self.duplicate_strict_results_table.setSelectionBehavior(QAbstractItemView.SelectRows)

    # def findStrict(self, results):
    #     found = {}
    #     last_size = None
    #     to_check = []
    #
    #     for item in results:
    #         if item[2] != last_size:
    #             if to_check:
    #                 checked = self.compareFiles(to_check)
    #                 if checked:
    #                     found[last_size] = checked
    #             last_size = item[2]
    #             to_check = [item]
    #         else:
    #             to_check.append(item)
    #     return self.formatResultsForTable(found)

    # def compareFiles(self, to_check):
    #     paths = []
    #     fields = ['dirpath', 'filename', 'size', 'extension', 'drive']
    #     for item in to_check:
    #         path = dict(zip(fields, item))
    #         path['full_path'] = os.path.join(item[0], item[1])
    #         paths.append(path)
    #     duplicates = self.checkIfDuplicate(paths)
    #     return duplicates

    # def checkIfDuplicate(self, paths):
    #     identical = {}
    #     for i in range(len(paths)):
    #         try:
    #             fpi = paths[i]['full_path']
    #             di = paths[i]['drive']
    #             identical[fpi] = []
    #             for j in range(i + 1, len(paths)):
    #                 fpj = paths[j]['full_path']
    #                 dj = paths[j]['drive']
    #
    #                 if self.alreadyFound(identical, fpj):
    #                     continue
    #
    #                 if filecmp.cmp(fpi, fpj, shallow=False):
    #                     if len(identical[fpi]) == 0:
    #                         identical[fpi].append([fpi, 1, di])
    #                     identical[fpi].append([fpj, 0, dj])
    #         except (OSError,):
    #             # the file access might've changed till the exec point got here
    #             continue
    #
    #     # clean duplicate entries
    #     no_add = []
    #     if identical:
    #         for k, v in identical.items():
    #             if len(v) == 0:
    #                 no_add.append(k)
    #     if no_add:
    #         for i in no_add:
    #             del identical[i]
    #     return identical

    # def alreadyFound(self, identical, new):
    #     for k, v in identical.items():
    #         for full_path, reference, drive in v:
    #             if new == full_path:
    #                 return True
    #     return False
