import pandas
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QSortFilterProxyModel, Qt

from mymodules import ComponentsModule, ModelsModule
from mymodules import GDBModule as gdb
from mymodules.CategoriesModule import CategoriesSelector
from mymodules.ComponentsModule import PushButton
from mymodules.GlobalFunctions import iconForButton, HEADER_SEARCH_RESULTS_TABLE
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
        self.export_results_button.clicked.connect(self.exportToCsv)

        self.found_results_table = ComponentsModule.TableViewAutoCols(None)
        self.found_results_table.setColumns([0.40, 0.25, 0.10, 0.10, 0.15])
        self.found_results_table_model = ModelsModule.SearchResultsTableModel(pandas.DataFrame([], columns=HEADER_SEARCH_RESULTS_TABLE))

        # add sorting to table
        sortermodel_results = QSortFilterProxyModel()
        sortermodel_results.setSourceModel(self.found_results_table_model)
        sortermodel_results.setFilterKeyColumn(2)
        # use sorter as model for table
        self.found_results_table.setModel(sortermodel_results)
        self.found_results_table.setSortingEnabled(True)
        self.found_results_table.sortByColumn(2, Qt.AscendingOrder)

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
        self.last_search_configuration = {'term': search_term, 'extensions':extensions}

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



    def exportToCsv(self):

        textData = ''
        selected = self.found_results_table.selectionModel()
        if selected.hasSelection():
            rows = selected.selectedRows()
            columns = selected.selectedColumns()
            model = selected.model()
            for i in range(0, len(rows)):
                for j in range(0, len(columns)):
                    textData += model.data(model.createIndex(i, j))
                    textData += ' '
                textData += "\n"


        print(textData)


        # last_search_configuration = self.last_search_configuration
        # search_term = self.last_search_configuration['term']
        # extensions = self.last_search_configuration['extensions']
        # results = gdb.findFiles(search_term, extensions)
        # x = results
        # header = ",".join(HEADER_SEARCH_RESULTS_TABLE)
        #
        # for row in results:
        #     line = " ".join(row)+"\n"
