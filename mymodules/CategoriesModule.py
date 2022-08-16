from PyQt5 import QtWidgets, QtCore

from gallery import iconForButton
from mymodules import GDBModule as gdb
from mymodules.ComponentsModule import PushButton

class Categories(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(Categories, self).__init__(parent)

        self.categories = gdb.getAll('categories')
        categories_selector = CategoriesSelector('tab_categories_', save_selection=True)
        categories_layout = categories_selector.generateBox()

        self.layout_tab_categories = QtWidgets.QHBoxLayout()
        self.layout_tab_categories.addLayout(categories_layout)


class CategoriesSelector(QtWidgets.QWidget):
    def __init__(self, identifier, save_selection=True, *args, **kwargs):
        super(CategoriesSelector, self).__init__(*args, **kwargs)
        self.identifier = None if not identifier else identifier
        self.categories = gdb.getAll('categories')
        self.save_selection = save_selection
        self.extensions_for_search = []

    def generateBox(self):
        # Set the vertical Qt Layout
        h_cat_box = QtWidgets.QHBoxLayout()
        columns = []
        # Create categories checkboxes
        for idx, cat in enumerate(self.categories):
            category = cat['category']
            cat_name = self.identifier + category.lower() + str(idx)
            cat_name = QtWidgets.QCheckBox(category, self)
            cat_name.setChecked(cat['selected'])
            x = cat_name
            cat_name.stateChanged.connect(lambda checked, val=x: self.setPreferredCategory(val))
            if idx % 5 == 0:
                column = QtWidgets.QVBoxLayout()
                columns.append(column)
            # add cat_name to previous column
            column.addWidget(cat_name)

        for column in columns:
            column.addStretch()
            h_cat_box.addLayout(column)

        last_column = QtWidgets.QVBoxLayout()
        check_all_categories = PushButton('Check all')
        check_all_categories.setCheckable(True)
        check_all_categories.setChecked(gdb.allCategoriesAreSelected())
        check_all_categories.clicked.connect(lambda: self.checkAllCategories(check_all_categories.isChecked()))
        last_column.addWidget(check_all_categories)
        h_cat_box.addLayout(last_column)

        categories_layout = QtWidgets.QVBoxLayout()
        categories_layout.addLayout(h_cat_box)
        return categories_layout

    def checkAllCategories(self, is_checked):
        for box in self.sender().parent().findChildren(QtWidgets.QCheckBox):
            box.setChecked(True) if is_checked else box.setChecked(False)

    def getExtensionsForSearch(self):
        # come from search tab
        selected_categories = []
        checkboxes = self.sender().parent().findChildren(QtWidgets.QCheckBox)
        for checkbox in checkboxes:
            if checkbox.isChecked():
                print(checkbox.text())
                selected_categories.append(checkbox.text())
        print("NO SAVE! CREATE LIST")
        print(selected_categories)
        # Get list of extensions for selected categories
        # and set them for searching
        selected_extensions = gdb.getExtensionsForCategories(selected_categories)
        self.extensions_for_search = selected_extensions

    def setPreferredCategory(self, btn):
        text = btn.text()
        if self.save_selection:
            # come from settings tab
            if gdb.categorySetSelected(text, btn.isChecked()):
                print("Success")
                # check also in search tab
            else:
                print("Fail")
        else:
            self.getExtensionsForSearch()

