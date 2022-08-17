from PyQt5 import QtWidgets

from mymodules import GDBModule as gdb
from mymodules.ComponentsModule import PushButton


class Categories(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(Categories, self).__init__(parent)

        self.categories = gdb.getAll('categories')
        categories_selector = CategoriesSelector()
        categories_layout = categories_selector.generateBox()

        self.layout_tab_categories = QtWidgets.QHBoxLayout()
        self.layout_tab_categories.addLayout(categories_layout)


class CategoriesSelector(QtWidgets.QWidget):

    def __init__(self, parent=None, *args, **kwargs):
        super(CategoriesSelector, self).__init__(parent=parent, *args, **kwargs)

        self.column_splitter = 3
        self.categories = gdb.getAll('categories')
        self.check_all_categories = PushButton('Check all')
        self.parent_load_default_categories = PushButton('Reload preferred')

        # Only Search set the parent because it has different behavior than Category
        # On Search selected categories are not saved as preferred, but used only for current search
        self.parent_name = self.parent().metaObject().className() if self.parent() else None

    def generateBox(self):
        columns = []
        # Create categories checkboxes
        for idx, cat in enumerate(self.categories):
            category = cat['category']
            cat_name = QtWidgets.QCheckBox(category, self)
            cat_name.setChecked(cat['selected'])
            x = cat_name
            cat_name.stateChanged.connect(lambda checked, val=x: self.setPreferredCategory(val))
            if idx % self.column_splitter == 0:
                column = QtWidgets.QVBoxLayout()
                columns.append(column)
            # add cat_name to previous column
            column.addWidget(cat_name)

        h_cats = QtWidgets.QHBoxLayout()
        for column in columns:
            column.addStretch()
            h_cats.addLayout(column)

        self.check_all_categories.setCheckable(True)
        self.check_all_categories.setChecked(gdb.allCategoriesAreSelected())
        self.check_all_categories.clicked.connect(lambda: self.checkAllCategories(self.check_all_categories.isChecked()))

        h_buttons = QtWidgets.QHBoxLayout()
        h_buttons.addWidget(self.check_all_categories)
        if self.parent_name:
            h_buttons.addWidget(self.parent_load_default_categories)
            self.parent_load_default_categories.clicked.connect(lambda: self.parent().setPreferredCategoriesOnSearchForm())
        h_buttons.addStretch()

        v_main = QtWidgets.QVBoxLayout()
        v_main.addLayout(h_cats)
        v_main.addLayout(h_buttons)
        v_main.addStretch(0)
        return v_main

    def checkAllCategories(self, is_checked):
        for box in self.sender().parent().findChildren(QtWidgets.QCheckBox):
            # this will trigger change for each button
            box.setChecked(True) if is_checked else box.setChecked(False)

    def setPreferredCategory(self, btn):
        text = btn.text()
        if not self.parent_name:
            # come from settings tab
            if gdb.categorySetSelected(text, btn.isChecked()):
                print("Success")
            else:
                print("Fail")

