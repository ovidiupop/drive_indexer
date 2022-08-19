from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtGui import QIcon

from mymodules import GDBModule as gdb
from mymodules.ComponentsModule import PushButton
from mymodules.GlobalFunctions import iconForButton, categoriesCombo, confirmationDialog
from mymodules.ModelsModule import ExtensionsModel


class Extensions(QtWidgets.QWidget):
    extension_added = QtCore.pyqtSignal()
    reindex_for_new_extension = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(Extensions, self).__init__(parent)

        # temporary set True after adding a new extension
        # to set indexer prevent to remove already indexed folders
        # and index only files for new extension
        self.added_new_extension = False
        self.last_added_extension = None

        self.add_extension_input = QtWidgets.QLineEdit()
        self.add_extension_input.setMaximumWidth(300)
        self.add_extension_input.setPlaceholderText('Insert new extension in selected category')
        self.settings_extensions_list = QtWidgets.QListView()
        self.settings_extensions_list.setMaximumSize(300, 200)
        self.add_extension_button = PushButton('Add')
        # self.set_preferred_extension_button = PushButton('Preferred')
        self.remove_extension_button = PushButton('Remove')

        self.add_extension_button.setIcon(iconForButton('SP_FileDialogNewFolder'))
        # self.set_preferred_extension_button.setIcon(iconForButton('SP_FileDialogDetailedView'))
        self.remove_extension_button.setIcon(iconForButton('SP_DialogDiscardButton'))

        self.categories_combo = categoriesCombo()

        icon = QIcon('logo.png')
        self.categories_combo.setItemIcon(0, icon)

        self.add_extension_input.returnPressed.connect(lambda: self.addNewExtension())
        self.add_extension_button.clicked.connect(lambda: self.addNewExtension())
        # self.set_preferred_extension_button.clicked.connect(lambda: self.setPreferredExtension())
        self.remove_extension_button.clicked.connect(lambda: self.removeExtension())
        self.categories_combo.currentIndexChanged.connect(self.loadExtensionsForCategory)

        # """settings extension section"""
        layout_tab_extensions_buttons = QtWidgets.QVBoxLayout()
        layout_tab_extensions_buttons.addWidget(self.categories_combo)
        layout_tab_extensions_buttons.addSpacing(20)
        layout_tab_extensions_buttons.addWidget(self.remove_extension_button)
        layout_tab_extensions_buttons.addWidget(self.add_extension_input)
        layout_tab_extensions_buttons.addWidget(self.add_extension_button)
        layout_tab_extensions_buttons.addSpacing(20)
        # layout_tab_extensions_buttons.addWidget(self.set_preferred_extension_button)
        layout_tab_extensions_buttons.addStretch()

        layout_tab_extensions_list = QtWidgets.QVBoxLayout()
        layout_tab_extensions_list.addWidget(self.settings_extensions_list)
        layout_tab_extensions_list.addStretch()
        self.layout_tab_extensions = QtWidgets.QHBoxLayout()
        self.layout_tab_extensions.addLayout(layout_tab_extensions_buttons)
        self.layout_tab_extensions.addLayout(layout_tab_extensions_list)
        self.layout_tab_extensions.addStretch()

    @QtCore.pyqtSlot(int)
    def loadExtensionsForCategory(self, category_id):
        if category_id:
            extensions = gdb.getExtensionsForCategoryId(category_id)
            self.settings_extensions_list.setModel(ExtensionsModel(extensions))
            self.settings_extensions_list.setSelectionMode(QtWidgets.QListView.ExtendedSelection)

    @QtCore.pyqtSlot()
    def addNewExtension(self):
        new_extension = self.add_extension_input.text()
        category_text = self.categories_combo.currentText()
        category_id = gdb.categoryIdByText(category_text)
        if not new_extension:
            QtWidgets.QMessageBox.information(None, 'No Extension', 'Please insert the name of new extension!')
            return
        if gdb.extensionExists(new_extension):
            QtWidgets.QMessageBox.information(None, 'Extension exists', 'The extension already exists!')
            return
        if gdb.addNewExtension(new_extension, category_id):
            self.last_added_extension = new_extension
            self.reindex_for_new_extension.emit()
            self.add_extension_input.setText('')
            self.loadExtensionsForCategory(category_id)

        else:
            QtWidgets.QMessageBox.critical(None, 'Not added', 'The extension has not been added!')

    def removeExtension(self):
        selected_ex = self.settings_extensions_list.selectedIndexes()
        confirmation_text = "'If you remove selected extensions, all indexed files belonging to them, will be also removed!<br><br>Do you proceed?"
        confirm = confirmationDialog("Do you remove?", confirmation_text)
        if not confirm:
            return
        extensions = []
        if len(selected_ex):
            extensions = []
            for extension in selected_ex:
                extensions.append(extension.data())
        if extensions:
            category_text = self.categories_combo.currentText()
            category_id = gdb.categoryIdByText(category_text)
            gdb.removeExtensions(extensions)
            self.loadExtensionsForCategory(category_id)

    def visibleButtons(self):
        index = self.categories_combo.currentIndex()
        if index > 0:
