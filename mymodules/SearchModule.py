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

    categories_changed = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(Search, self).__init__(parent)

        self.search_input_label = QtWidgets.QLabel('Search for:')
        self.search_term_input = QtWidgets.QLineEdit()
        self.search_term_input.setPlaceholderText('Insert term to search')
        self.search_button = PushButton('Search')
        self.search_button.setIcon(iconForButton('SP_FileDialogContentsView'))

        self.search_term_input.returnPressed.connect(self.onSubmitted)
        self.search_button.clicked.connect(self.onSubmitted)

        self.found_search_label = QtWidgets.QLabel('Found')
        self.found_search_label.hide()
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
        # input search layout
        search_row_layout = QtWidgets.QHBoxLayout()
        search_row_layout.addWidget(self.search_term_input)
        search_row_layout.addWidget(self.search_button)
        search_input_section_layout = QtWidgets.QVBoxLayout()
        search_input_section_layout.addWidget(self.search_input_label)
        search_input_section_layout.addLayout(search_row_layout)
        search_input_section_layout.addStretch()

        self.categories_selector = CategoriesSelector('search_categories_', save_selection=False)
        # categories box
        self.categories_layout = self.categories_selector.generateBox()
        self.categories_layout.addStrut(100)

        self.load_default_categories = PushButton('Load preferred')
        self.load_default_categories.clicked.connect(self.setPreferredCategoriesOnSearchForm)
        buttons_layout = QtWidgets.QHBoxLayout()
        buttons_layout.addWidget(self.load_default_categories)

        # self.categories_layout.addLayout(buttons_layout)
        self.checkboxes_group = QtWidgets.QGroupBox()
        self.checkboxes_group.setLayout(self.categories_layout)

        hlay = QtWidgets.QHBoxLayout()
        hlay.addWidget(self.checkboxes_group)
        hlay.addLayout(buttons_layout)

        # upper area layout
        top_layout = QtWidgets.QHBoxLayout()
        top_layout.addLayout(search_input_section_layout, 85)
        top_layout.addLayout(hlay, 85)

        # container to maintain fixed height of top area
        container_search_top = QtWidgets.QWidget(self)
        container_search_top.setMaximumHeight(160)
        container_search_top.setLayout(top_layout)

        # search results section
        search_results_layout = QtWidgets.QVBoxLayout()
        search_results_layout.addWidget(self.found_search_label)
        search_results_layout.addWidget(self.found_results_table)

        self.search_tab_layout = QtWidgets.QVBoxLayout()
        self.search_tab_layout.addWidget(container_search_top)
        self.search_tab_layout.addLayout(search_results_layout)

        # prepare extensions for search
        self.extensions_for_search = []
        self.getExtensionsForSearch()

        self.categories_selector.check_all_categories.clicked.connect(lambda :self.preferredCategoriesChanged())


    @QtCore.pyqtSlot()
    def preferredCategoriesChanged(self):
        print("I know")

    @QtCore.pyqtSlot()
    def onSubmitted(self):
        search_term = self.search_term_input.text()
        if not search_term:
            QtWidgets.QMessageBox.information(None, 'No term to search', 'Please write a term for search')
            return

        self.getExtensionsForSearch()
        extensions = self.extensions_for_search
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
    def setPreferredCategoriesOnSearchForm(self):
        print('load defaulta')
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

