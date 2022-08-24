from PyQt5 import QtCore, QtSql, QtGui
from PyQt5.QtCore import Qt, QSortFilterProxyModel
from PyQt5.QtWidgets import QStyledItemDelegate, QSpinBox, QItemDelegate, QLineEdit, \
    QDataWidgetMapper

from mymodules.GlobalFunctions import getIcon, HEADER_SEARCH_RESULTS_TABLE, HEADER_DRIVES_TABLE
from mymodules import GDBModule as gdb


class ExtensionsModel(QtCore.QAbstractListModel):
    def __init__(self, extensions):
        super().__init__()
        self.extensions = extensions

    # override method of abstract class
    def data(self, index, role):
        ex = self.extensions[index.row()]
        if role == Qt.DisplayRole:
            return ex
        elif role == Qt.DecorationRole:
            return getIcon(ex)

    # override method of abstract class
    def rowCount(self, index):
        return len(self.extensions)


class DrivesTableModel(QtSql.QSqlTableModel):
    def __init__(self):
        super(DrivesTableModel, self).__init__()
        self._data = []
        self.table = 'drives'
        self.setTable(self.table)
        self.setEditStrategy(self.OnRowChange)
        self.setColumnsName()
        self.setSort(self.fieldIndex("size"), Qt.DescendingOrder)

    def setColumnsName(self):
        for k, v in HEADER_DRIVES_TABLE.items():
            idx = self.fieldIndex(k)
            self.setHeaderData(idx, Qt.Horizontal, v)

    def setTableSorter(self, column_index, table):
        sort_filter = QSortFilterProxyModel()
        sort_filter.setSourceModel(self)
        sort_filter.setFilterKeyColumn(column_index)
        table.setModel(sort_filter)
        table.setSortingEnabled(True)
        table.sortByColumn(column_index, Qt.DescendingOrder)


class SearchResultsTableModel(QtCore.QAbstractTableModel):
    def __init__(self, data):
        super(SearchResultsTableModel, self).__init__()
        self._data = data

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole:
                return str(self._data.iloc[index.row()][index.column()])
            if role == Qt.TextAlignmentRole:
                if index.column() == 2 or index.column() == 3:
                    return Qt.AlignRight
            if role == Qt.ForegroundRole:
                if index.column() == 4:
                    value = str(self._data.iloc[index.row()][index.column()])
                    is_active = gdb.isDriveActiveByLabel(value)
                    if not is_active:
                        return QtGui.QColor('red')
        return None

    def rowCount(self, parent=None):
        return len(self._data.values)

    def columnCount(self, parent=None):
        return self._data.columns.size

    def headerData(self, section, orientation, role):
        # section is the index of the column/row.
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return HEADER_SEARCH_RESULTS_TABLE[section]
            if orientation == Qt.Vertical:
                return section + 1  # row numbers start from 1
        return None

    def flags(self, index):
        flags = super(self.__class__, self).flags(index)
        flags |= Qt.ItemIsEditable
        flags |= Qt.ItemIsSelectable
        flags |= Qt.ItemIsEnabled
        flags |= Qt.ItemIsDragEnabled
        flags |= Qt.ItemIsDropEnabled
        return flags

    def sort(self, column, order):
        """Sort table by given column number."""
        try:
            self.layoutAboutToBeChanged.emit()
            self._data = self._data.sort_values(self._data.columns[column], ascending=not order)
            self.layoutChanged.emit()
        except Exception as e:
            print(e)


class SortFilterProxyModel(QSortFilterProxyModel):
    def __init__(self, *args, **kwargs):
        QSortFilterProxyModel.__init__(self, *args, **kwargs)
        self.filters = {}

    def setFilterByColumn(self, regex, column):
        self.filters[column] = regex
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row, source_parent):
        for key, regex in self.filters.items():
            ix = self.sourceModel().index(source_row, key, source_parent)
            if ix.isValid():
                text = self.sourceModel().data(ix).toString()
                if not text.contains(regex):
                    return False
        return True


class DrivesMapper(QDataWidgetMapper):
    def __init__(self, parent):
        super().__init__(parent)
        model = parent.drives_table_model
        self.setModel(model)
        self.addMapping(parent.drive_serial_input, model.fieldIndex('serial'))
        self.addMapping(parent.drive_name_input, model.fieldIndex('name'))
        self.addMapping(parent.drive_label_input, model.fieldIndex('label'))
        self.addMapping(parent.drive_size_input, model.fieldIndex('size'))
        self.addMapping(parent.drive_active_input, model.fieldIndex('active'))


class DrivesItemsDelegate(QStyledItemDelegate):
    def __init__(self, parent):
        QStyledItemDelegate.__init__(self, parent)

    def nameOfColumn(self, idx):
        names = HEADER_DRIVES_TABLE.keys()
        for index, name in enumerate(names):
            if index == idx:
                return name

    def createEditor(self, parent, option, index):
        disabled = ['serial', 'name', 'active']
        if self.nameOfColumn(index.column()) in disabled:
            editor = QLineEdit(parent)
            editor.setDisabled(True)
            return editor
        elif 'label' == self.nameOfColumn(index.column()):
            editor = QLineEdit(parent)
            editor.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            return editor
        elif 'size' == self.nameOfColumn(index.column()):
            spinbox = QSpinBox(parent)
            spinbox.setRange(0, 2000000)
            spinbox.setSingleStep(100)
            spinbox.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            return spinbox
        else:
            return QItemDelegate.createEditor(self, parent, option, index)

# KEEP THIS FOR EXAMPLE
        # elif index.column() == OWNER:
        #     combobox = QComboBox(parent)
        #     combobox.addItems(sorted(index.model().owners))
        #     combobox.setEditable(True)
        #     return combobox
        #     elif index.column() == COUNTRY:
        #     combobox = QComboBox(parent)
        #     combobox.addItems(sorted(index.model().countries))
        #     combobox.setEditable(True)
        #     return combobox
        # elif index.column() == NAME:
        #     editor = QLineEdit(parent)
        #     self.connect(editor, SIGNAL("returnPressed()"),
        #                  self.commitAndCloseEditor)
        #     return editor
        #     elif index.column() == DESCRIPTION:
        #     editor = richtextlineedit.RichTextLineEdit(parent)
        #     self.connect(editor, SIGNAL("returnPressed()"),
        #                  self.commitAndCloseEditor)
        #     return editor
        # else:
        #     return QItemDelegate.createEditor(self, parent, option, index)
