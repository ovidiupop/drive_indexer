from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHBoxLayout, QLabel

from mymodules.ComponentsModule import PushButton, TableViewAutoCols
from mymodules.GlobalFunctions import iconForButton, confirmationDialog
from mymodules.ModelsModule import DrivesTableModel, DrivesItemsDelegate, DrivesMapper
from mymodules.SystemModule import System
from mymodules import GDBModule as gdb

COLUMN_SIZE = [0.10, 0.30, 0.20, 0.20, 0.10, 0.10]
COLUMN_SIZE_ID_HIDDEN = [0.10, 0.40, 0.20, 0.20, 0.09, 0.10]


class Drives(QtWidgets.QWidget):

    check_add_button = QtCore.pyqtSignal()

    def __init__(self, parent):
        super(Drives, self).__init__(parent)

        self.partitions_as_list_partition_key = self.partitionsAsListPartitionKey()
        self.partitions_as_list_serial_key = self.partitionsAsListSerialKey()
        self.drive_serial_input = QtWidgets.QLineEdit()
        self.drive_serial_input.setDisabled(True)
        self.drive_name_input = QtWidgets.QLineEdit()
        self.drive_name_input.setDisabled(True)
        self.drive_label_input = QtWidgets.QLineEdit()
        self.drive_size_input = QtWidgets.QDoubleSpinBox()
        self.drive_size_input.setRange(0, 2000000)
        self.drive_size_input.setSingleStep(100)
        self.drive_size_input.setSuffix(' GB')
        self.drive_active_input = QtWidgets.QLineEdit()
        self.drive_active_input.setDisabled(True)
        self.add_drive_button = PushButton('Add')
        self.remove_drive_button = PushButton('Remove')
        self.show_id_drive_button = PushButton('Show ID')
        self.show_id_drive_button.setCheckable(True)
        self.show_id_drive_button.setChecked(False)
        self.drive_form_close = QtWidgets.QPushButton()
        self.drive_form_close.setMaximumWidth(30)
        self.combo_active_drives = QtWidgets.QComboBox()
        self.combo_active_drives.setMaximumWidth(250)

        self.drive_form_close.setIcon(iconForButton('SP_DialogCloseButton'))
        self.add_drive_button.setIcon(iconForButton('SP_DriveHDIcon'))
        self.remove_drive_button.setIcon(iconForButton('SP_TrashIcon'))
        self.show_id_drive_button.setIcon(iconForButton('SP_FileDialogListView'))


    def partitionsAsListSerialKey(self):
        drives = gdb.getAll('drives')
        partitions = {}
        if drives:
            for drive in drives:
                serial = drive['serial']
                dpartitions = drive['partitions'].split(',')
                partitions[serial] = dpartitions
        return partitions

    def partitionsAsListPartitionKey(self):
        drives = gdb.getAll('drives')
        partitions = {}
        if drives:
            for drive in drives:
                serial = drive['serial']
                dpartitions = drive['partitions'].split(',')
                for partition in dpartitions:
                    partitions[partition] = serial
        return partitions


class DrivesView(Drives):
    def __init__(self, parent=None):
        super(DrivesView, self).__init__(parent)

        """settings drives section
        """
        self.comboActiveDrives()

        self.drives_table_model = DrivesTableModel()
        # self.drives_table_model.dataChanged.connect(self.validateData)
        self.drives_table_model.select()
        self.drives_table = TableViewAutoCols(None)
        self.drives_table.setColumns(COLUMN_SIZE)
        self.drives_table_model = DrivesTableModel()

        self.drives_table_model.dataChanged.connect(self.validateData)
        self.drives_table_model.select()
        self.drives_table.setModel(self.drives_table_model)
        self.drives_table.setColumnHidden(self.drives_table_model.fieldIndex("serial"), True)
        self.drives_table_model.setTableSorter(self.drives_table_model.fieldIndex('size'), self.drives_table)
        self.drives_table.setItemDelegate(DrivesItemsDelegate(self))

        form_drives = QtWidgets.QFormLayout()
        close_layout = QtWidgets.QHBoxLayout()
        close_layout.addWidget(self.drive_form_close)
        self.drive_form_close.clicked.connect(self.close_drives_form)
        close_layout.setAlignment(Qt.AlignRight | Qt.AlignTop)

        controls = QHBoxLayout()
        prev_rec = PushButton('Previous')
        prev_rec.setMyIcon(iconForButton('SP_MediaSeekBackward'))
        prev_rec.setTextCenter()
        prev_rec.clicked.connect(lambda: self.drive_mapper.toPrevious())

        next_rec = PushButton("Next")
        next_rec.setMyIcon(iconForButton('SP_MediaSeekForward'), position='right')
        next_rec.setTextCenter()
        next_rec.clicked.connect(lambda: self.drive_mapper.toNext())
        save_rec = PushButton("Save Changes")
        save_rec.setIcon(iconForButton('SP_DialogSaveButton'))
        save_rec.clicked.connect(lambda: self.drive_mapper.submit())

        controls.addWidget(prev_rec)
        controls.addWidget(next_rec)

        self.drives_table.doubleClicked.connect(self.show_drive_form)
        self.drives_table.clicked.connect(self.show_drive_form)
        form_drives.addRow(close_layout)
        form_drives.addRow('Navigate', controls)
        form_drives.addRow(QLabel('Serial'), self.drive_serial_input)
        form_drives.addRow(QLabel('Name'), self.drive_name_input)
        form_drives.addRow(QLabel('Own Label'), self.drive_label_input)
        form_drives.addRow(QLabel('Size (GB)'), self.drive_size_input)
        form_drives.addRow(QLabel('Active'), self.drive_active_input)
        form_drives.addRow('', save_rec)

        self.drive_mapper = DrivesMapper(self)
        self.drive_mapper.model().select()
        self.drive_mapper.toLast()

        self.group_form = QtWidgets.QGroupBox()
        self.group_form.setMaximumWidth(330)
        self.group_form.setLayout(form_drives)
        self.group_form.hide()

        layout_tab_drives_buttons = QtWidgets.QVBoxLayout()
        layout_tab_drives_buttons.addWidget(self.combo_active_drives)
        layout_tab_drives_buttons.addSpacing(20)
        layout_tab_drives_buttons.addWidget(self.add_drive_button)
        layout_tab_drives_buttons.addWidget(self.remove_drive_button)
        layout_tab_drives_buttons.addWidget(self.show_id_drive_button)

        layout_tab_drives_buttons.addWidget(self.group_form)
        layout_tab_drives_buttons.addStretch()

        layout_tab_drives_table = QtWidgets.QHBoxLayout()
        layout_tab_drives_table.addWidget(self.drives_table)

        # for connection with app
        self.layout_tab_drives = QtWidgets.QHBoxLayout()
        self.layout_tab_drives.addLayout(layout_tab_drives_buttons)
        self.layout_tab_drives.addLayout(layout_tab_drives_table)

        self.my_actions()
        self.check_add_button.emit()

    def my_actions(self):
        self.add_drive_button.clicked.connect(self.addRowDrive)
        self.remove_drive_button.clicked.connect(self.deleteRowDrive)
        self.show_id_drive_button.clicked.connect(self.toggleIdDrive)
        self.combo_active_drives.currentIndexChanged.connect(self.check_add_button)
        self.check_add_button.connect(self.disableAddButtonForExisting)

    def validateData(self):
        pass

    def toggleIdDrive(self):
        self.drives_table.setColumnHidden(self.drives_table_model.fieldIndex("serial"),
                                          not self.show_id_drive_button.isChecked())
        if self.show_id_drive_button.isChecked():
            self.drives_table.setColumns(COLUMN_SIZE)
        else:
            self.drives_table.setColumns(COLUMN_SIZE_ID_HIDDEN)

    def deleteRowDrive(self):
        confirmation_text = f"You will remove the drive/s! <br><br>Do you proceed?"
        confirm = confirmationDialog("Do you remove?", confirmation_text)
        if not confirm:
            return
        selected = self.drives_table.selectedIndexes()
        for index in selected or []:
            self.drives_table_model.removeRow(index.row())
        self.drives_table_model.select()
        self.check_add_button.emit()

    def getSelectedDriveComboData(self):
        mounted_drives = System().mounted_drives
        c = self.combo_active_drives.currentText()
        parts = c.split(' ')
        serial = parts[-1]
        for drive in mounted_drives:
            if drive['serial'] == serial:
                return {
                    'serial': str(drive['serial']),
                    'name': drive['name'],
                    'label': drive['name'],
                    'size': float(drive['size']),
                    'active': int(1),
                    'partitions': drive['partitions'],
                    'path': drive['path']
                }

    def addRowDrive(self):
        drive_model = self.drives_table_model
        new_row = drive_model.record()
        defaults = self.getSelectedDriveComboData()
        for field, value in defaults.items():
            index = drive_model.fieldIndex(field)
            new_row.setValue(index, value)

        inserted = drive_model.insertRecord(-1, new_row)
        if not inserted:
            error = drive_model.lastError().text()
            print(f"Insert Failed: {error}")
        # Select the new row is editable
        drive_model.select()
        self.drive_mapper.toLast()
        self.add_drive_button.setDisabled(True)

    def close_drives_form(self):
        self.group_form.hide()

    def show_drive_form(self, drives_table_index):
        self.group_form.show()
        self.drive_mapper.setCurrentIndex(drives_table_index.row())

    def comboActiveDrives(self):
        active_drives = System().mounted_drives
        items = []
        if active_drives:
            for drive in active_drives:
                item = drive['name']
                item += ' (' + drive['path'] + ') ' + drive['serial']
                items.append(item)
        self.combo_active_drives.addItems(items)

    def disableAddButtonForExisting(self):
        combo_text = self.combo_active_drives.currentText()
        parts = combo_text.split(' ')
        serial = parts[-1]
        self.add_drive_button.setDisabled(gdb.driveSerialExists(serial))
