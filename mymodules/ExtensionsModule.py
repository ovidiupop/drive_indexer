from PyQt5 import QtWidgets, QtCore


from gallery import iconForButton
from mymodules import GDBModule as gdb
from mymodules.ComponentsModule import PushButton


class Extensions(QtWidgets.QWidget):
    extension_added = QtCore.pyqtSignal()
    reindex_for_new_extension = QtCore.pyqtSignal()

    preselect_favorite_extensions = QtCore.pyqtSignal()

    update_view_extensions = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(Extensions, self).__init__(parent)

        # temporary set True after adding a new extension
        # to set indexer prevent to remove already indexed folders
        # and index only files for new extension
        self.added_new_extension = False
        self.last_added_extension = None

        self.add_extension_input = QtWidgets.QLineEdit()
        self.add_extension_input.setPlaceholderText('Insert new extension')
        self.settings_extensions_list = QtWidgets.QListView()
        self.add_extension_button = PushButton('Add')
        self.set_preferred_extension_button = PushButton('Preferred')
        self.remove_extension_button = PushButton('Remove')

        self.add_extension_button.setIcon(iconForButton('SP_FileDialogNewFolder'))
        self.set_preferred_extension_button.setIcon(iconForButton('SP_FileDialogDetailedView'))
        self.remove_extension_button.setIcon(iconForButton('SP_DialogDiscardButton'))

        self.add_extension_input.returnPressed.connect(lambda: self.addNewExtension())
        self.add_extension_button.clicked.connect(lambda: self.addNewExtension())
        self.set_preferred_extension_button.clicked.connect(lambda: self.setPreferredExtension())
        self.remove_extension_button.clicked.connect(lambda: self.removeExtension())

        # self.preselect_favorite_extensions.emit()

        # """settings extension section"""
        layout_tab_extensions_buttons = QtWidgets.QVBoxLayout()
        layout_tab_extensions_buttons.addWidget(self.set_preferred_extension_button)
        layout_tab_extensions_buttons.addWidget(self.remove_extension_button)
        layout_tab_extensions_buttons.addWidget(self.add_extension_button)
        layout_tab_extensions_buttons.addStretch()

        layout_tab_extensions_list = QtWidgets.QVBoxLayout()
        layout_tab_extensions_list.addWidget(self.settings_extensions_list)
        layout_tab_extensions_list.addWidget(self.add_extension_input)
        self.layout_tab_extensions = QtWidgets.QHBoxLayout()
        self.layout_tab_extensions.addLayout(layout_tab_extensions_buttons)
        self.layout_tab_extensions.addLayout(layout_tab_extensions_list)


    def setPreferredExtension(self):
        selected_ex = self.settings_extensions_list.selectedIndexes()
        extensions = []
        if len(selected_ex):
            extensions = []
            for extension in selected_ex:
                extensions.append(extension.data())
        if extensions:
            if gdb.setPreferredExtensions(extensions):
                self.preselect_favorite_extensions.emit()
                QtWidgets.QMessageBox.information(None, 'Preferred set', 'Preferred extensions set!')

    @QtCore.pyqtSlot()
    def addNewExtension(self):
        new_extension = self.add_extension_input.text()
        if not new_extension:
            QtWidgets.QMessageBox.information(None, 'No Extension', 'Please insert the name of new extension!')
            return
        if gdb.extensionExists(new_extension):
            QtWidgets.QMessageBox.information(None, 'Extension exists', 'The extension already exists!')
            return
        if gdb.addNewExtension(new_extension):
            self.last_added_extension = new_extension
            self.update_view_extensions.emit()
            self.reindex_for_new_extension.emit()
        else:
            QtWidgets.QMessageBox.critical(None, 'Not added', 'The extension has not been added!')

    def removeExtension(self):
        selected_ex = self.settings_extensions_list.selectedIndexes()
        extensions = []
        if len(selected_ex):
            extensions = []
            for extension in selected_ex:
                extensions.append(extension.data())
        if extensions:
            if gdb.removeExtensions(extensions):
                self.update_view_extensions.emit()

