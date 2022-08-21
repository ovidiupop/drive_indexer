import os

import pandas
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QSortFilterProxyModel, Qt
from PyQt5.QtWidgets import QTableView, QAbstractItemView, QFileDialog

from mymodules import ComponentsModule, ModelsModule
from mymodules import GDBModule as gdb
from mymodules.CategoriesModule import CategoriesSelector
from mymodules.ComponentsModule import PushButton
from mymodules.GlobalFunctions import iconForButton, HEADER_SEARCH_RESULTS_TABLE, CSV_COLUMN_SEPARATOR, \
    CSV_LINE_SEPARATOR, DEFAULT_DIR
from mymodules.ModelsModule import SearchResultsTableModel


class Search(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super(Search, self).__init__(parent)

        self.last_search_configuration = {}

        self.search_input_label = QtWidgets.QLabel('Search for:')
        self.search_term_input = QtWidgets.QLineEdit()
        self.search_term_input.setPlaceholderText('Insert term to search')
        self.search_button = PushButton('Search')
        self.search_button.setMinimumWidth(200)
        self.search_button.setIcon(iconForButton('SP_FileDialogContentsView'))

        self.search_term_input.returnPressed.connect(self.onSubmitted)
        self.search_button.clicked.connect(self.onSubmitted)

        self.found_search_label = QtWidgets.QLabel('Found')
        self.found_search_label.hide()
        self.export_results_button = PushButton('Export to CSV')
        self.export_results_button.clicked.connect(
            lambda: self.prepareSelectedAsCSV(
                checked=False, column_separator=CSV_COLUMN_SEPARATOR, line_separator=CSV_LINE_SEPARATOR))

        self.found_results_table = ComponentsModule.TableViewAutoCols(None)
        self.found_results_table.setColumns([0.40, 0.25, 0.10, 0.10, 0.15])
        self.found_results_table_model = ModelsModule.SearchResultsTableModel(
            pandas.DataFrame([], columns=HEADER_SEARCH_RESULTS_TABLE))

        # add sorting to table
        sortermodel_results = QSortFilterProxyModel()
        sortermodel_results.setSourceModel(self.found_results_table_model)
        sortermodel_results.setFilterKeyColumn(2)
        # use sorter as model for table
        self.found_results_table.setModel(sortermodel_results)
        self.found_results_table.setSortingEnabled(True)
        self.found_results_table.sortByColumn(2, Qt.AscendingOrder)
        self.found_results_table.setSelectionBehavior(QAbstractItemView.SelectRows)

        # categories box
        self.categories_selector_search = CategoriesSelector(parent=self)
        self.categories_layout = self.categories_selector_search.generateBox()

        h_label = QtWidgets.QHBoxLayout()
        h_label.addWidget(self.search_input_label)

        h_search_row = QtWidgets.QHBoxLayout()
        h_search_row.addWidget(self.search_term_input)
        h_search_row.addWidget(self.search_button)

        h_categories_row = QtWidgets.QHBoxLayout()
        self.checkboxes_group = QtWidgets.QGroupBox()
        self.checkboxes_group.setMaximumHeight(140)
        self.checkboxes_group.setLayout(self.categories_layout)
        h_categories_row.addWidget(self.checkboxes_group)

        v_col_general = QtWidgets.QVBoxLayout()
        v_col_general.addLayout(h_label)
        v_col_general.addLayout(h_search_row)
        v_col_general.addLayout(h_categories_row)

        # search results section
        search_results_layout = QtWidgets.QVBoxLayout()
        row_over_table = QtWidgets.QHBoxLayout()
        row_over_table.addWidget(self.found_search_label, 0, Qt.AlignLeft)
        row_over_table.addStretch()
        row_over_table.addWidget(self.export_results_button, 0, Qt.AlignLeft)

        search_results_layout.addLayout(row_over_table)
        search_results_layout.addWidget(self.found_results_table)

        v_col_general.addLayout(search_results_layout)

        h_main = QtWidgets.QHBoxLayout()
        h_main.addLayout(v_col_general)

        self.search_tab_layout = QtWidgets.QVBoxLayout()
        self.search_tab_layout.addLayout(h_main)

        # prepare extensions for search
        self.extensions_for_search = []
        self.getExtensionsForSearch()

    @QtCore.pyqtSlot()
    def onSubmitted(self):
        search_term = self.search_term_input.text()
        if not search_term:
            QtWidgets.QMessageBox.information(None, 'No term to search', 'Please write a term for search')
            return

        self.getExtensionsForSearch()
        extensions = self.extensions_for_search
        if not len(extensions):
            QtWidgets.QMessageBox.information(None, 'No one category', 'Please check at least a category!')
            return

        self.last_search_configuration = {'term': search_term, 'extensions': extensions}
        results = gdb.findFiles(search_term, extensions)
        count_results = len(results)
        self.found_search_label.show()
        self.found_search_label.setText(f'Found: {count_results} results')
        self.updateResults(results)

    def updateResults(self, results):
        data = pandas.DataFrame(results, columns=ModelsModule.HEADER_SEARCH_RESULTS_TABLE)
        self.found_results_table.setModel(SearchResultsTableModel(data))
        self.update()

    # load extensions when the search is started
    # based on checked categories from search form
    def getExtensionsForSearch(self):
        selected_categories = []
        checkboxes = self.checkboxes_group.findChildren(QtWidgets.QCheckBox)
        for checkbox in checkboxes:
            if checkbox.isChecked():
                selected_categories.append(checkbox.text())
        # with selected categories from search form
        # take the list of extensions for selected categories
        # and set them for searching
        self.extensions_for_search = gdb.getExtensionsForCategories(selected_categories)

    # synchronize search form categories with defaults
    @QtCore.pyqtSlot()
    def setPreferredCategoriesOnSearchForm(self):
        categories = gdb.getAll('categories')
        if categories:
            selected = []
            for category in categories:
                if category['selected'] == 1:
                    selected.append(category['category'])
                checkboxes = self.checkboxes_group.findChildren(QtWidgets.QCheckBox)
                for ckb in checkboxes:
                    text = ckb.text()
                    ckb.setChecked(True) if text in selected else ckb.setChecked(False)

    def prepareSelectedAsCSV(self, column_separator, line_separator, checked=False):
        model = self.found_results_table.model()
        columns = model.columnCount()
        indexes = self.found_results_table.selectionModel().selectedRows()
        if not len(indexes):
            display = self.tableToCSV(checked, column_separator, line_separator)
            return self.putInFile(display, line_separator)

        results = []
        for index in indexes:
            one_line = []
            for col in range(0, columns):
                val = model.data(model.index(index.row(), col), Qt.DisplayRole)
                # we have to convert values to string if we wish to concatenate them
                if not isinstance(val, str):
                    val = '%s' % val
                one_line.append(val)
            line = column_separator.join(one_line)
            results.append(line)
        return self.putInFile(results)

    def tableToCSV(self, checked=False, column_separator=" ", line_separator="\n"):
        model = self.found_results_table.model()
        columns = model.columnCount()
        rows = model.rowCount()

        results = []
        for row in range(0, rows):
            one_line = []
            for col in range(0, columns):
                val = model.data(model.index(row, col), Qt.DisplayRole)
                # we have to convert values to string if we wish to concatenate them
                if not isinstance(val, str):
                    val = '%s' % val
                one_line.append(val)
            line = column_separator.join(one_line)
            results.append(line)
        return results

    # we have to pass data as list
    def putInFile(self, data, line_separator):
        default_dir = DEFAULT_DIR
        default_filename = os.path.join(default_dir, "")
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save CSV", default_filename, "CSV Files (*.csv)"
        )
        if filename:
            file = open(filename, 'w')
            text = line_separator.join(data)
            file.write(text)
            file.close()
            QtWidgets.QMessageBox.information(None, 'Export CSV', 'Exported successfully!')
            return
