from PyQt5 import QtWidgets, QtCore

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
    categories_changed = QtCore.pyqtSignal()

    def __init__(self, identifier, save_selection=True, *args, **kwargs):
        super(CategoriesSelector, self).__init__(*args, **kwargs)
        self.identifier = None if not identifier else identifier
        self.categories = gdb.getAll('categories')
        # to identify source of signal; from search will not search new checked/unchecked categories
        self.save_selection = save_selection

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


        last_row = QtWidgets.QHBoxLayout()
        self.check_all_categories = PushButton('Check all')
        self.check_all_categories.setCheckable(True)
        self.check_all_categories.setChecked(gdb.allCategoriesAreSelected())
        self.check_all_categories.clicked.connect(lambda: self.checkAllCategories(self.check_all_categories.isChecked()))
        last_row.addWidget(self.check_all_categories)
        h_cat_box.addLayout(last_row)

        vlast_lay = QtWidgets.QVBoxLayout()
        vlast_lay.addLayout(h_cat_box)
        vlast_lay.addLayout(last_row)
        categories_layout = QtWidgets.QVBoxLayout()
        categories_layout.addLayout(vlast_lay)
        return categories_layout

    def checkAllCategories(self, is_checked):
        for box in self.sender().parent().findChildren(QtWidgets.QCheckBox):
            box.setChecked(True) if is_checked else box.setChecked(False)

    def setPreferredCategory(self, btn):
        text = btn.text()
        if self.save_selection:
            # come from settings tab
            if gdb.categorySetSelected(text, btn.isChecked()):
                print("Success")
                self.categories_changed.emit()
            else:
                print("Fail")

