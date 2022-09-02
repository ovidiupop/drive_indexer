from PyQt5 import QtWidgets, QtCore

from mymodules import GDBModule as gdb
from mymodules.GlobalFunctions import setPreferenceById


class Preferences(QtWidgets.QWidget):
    change_settings_tab_position = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(Preferences, self).__init__(parent)
        self.preferences = gdb.getAll('preferences')

        grid_layout = QtWidgets.QGridLayout()
        for i, preference in enumerate(self.preferences):
            if preference['editable']:
                id = preference['id']
                value = preference['value']
                type = preference['type']
                if type == 'bool':
                    input = QtWidgets.QCheckBox()
                    input.setChecked(int(value))
                    x = input
                    sid = id
                    input.stateChanged.connect(lambda checked, input=x, id=sid: self.setNewPreferences(id, input))
                elif type == 'str':
                    input = QtWidgets.QLineEdit()

                grid_layout.addWidget(input, i, 0)
                desc = QtWidgets.QLabel(preference['description'])
                grid_layout.addWidget(desc, i, 1)

        hlay = QtWidgets.QHBoxLayout()
        hlay.addLayout(grid_layout)
        hlay.addStretch()

        vlay = QtWidgets.QVBoxLayout()
        vlay.addLayout(hlay)
        vlay.addStretch()

        self.layout_tab_preferences = QtWidgets.QHBoxLayout()
        self.layout_tab_preferences.addLayout(vlay)

    def setNewPreferences(self, id, checkbox):
        setPreferenceById(id, checkbox)
        name = gdb.getPreferenceNameById(id)
        if name == 'settings_tab_on_top':
            self.change_settings_tab_position.emit()
