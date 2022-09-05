from PyQt5 import QtCore, QtSql, QtGui
from PyQt5.QtCore import Qt, QSortFilterProxyModel
from PyQt5.QtGui import QIcon
from PyQt5.QtSql import QSqlTableModel, QSqlRelation
from PyQt5.QtWidgets import QStyledItemDelegate, QSpinBox, QLineEdit, \
    QDataWidgetMapper, QAbstractItemView

from mymodules import GDBModule as gdb
from mymodules.GlobalFunctions import getIcon, HEADER_SEARCH_RESULTS_TABLE, HEADER_DRIVES_TABLE, HEADER_FOLDERS_TABLE


def sorter(model_obj, table_obj, filter_key, order=Qt.DescendingOrder):
    # add sorting to table
    sortermodel = QSortFilterProxyModel()
    sortermodel.setSourceModel(model_obj)
    sortermodel.setFilterKeyColumn(filter_key)

    # use sorter as model for table
    table_obj.setModel(sortermodel)
    table_obj.setSortingEnabled(True)
    table_obj.sortByColumn(filter_key, order)
    table_obj.setSelectionBehavior(QAbstractItemView.SelectRows)


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
            return getIcon(ex, 32)

    # override method of abstract class
    def rowCount(self, index):
        return len(self.extensions)


class FoldersModel(QtSql.QSqlRelationalTableModel):
    def __init__(self, parent=None):
        super(FoldersModel, self).__init__(parent)
        self.setTable('folders')
        self.setRelation(2, QSqlRelation("drives", "serial", "label"))
        self.setEditStrategy(self.OnRowChange)
        self.setColumnsName()
        self.setSort(self.fieldIndex("id"), Qt.AscendingOrder)
        sorter(self, self.parent(), 1)
        self.parent().setItemDelegate(FoldersItemsDelegate(self))
        self.select()

    def setColumnsName(self):
        for k, v in HEADER_FOLDERS_TABLE.items():
            idx = self.fieldIndex(k)
            self.setHeaderData(idx, Qt.Horizontal, v)

    def nameOfColumn(self, index):
        return [col for idx, col in enumerate(HEADER_FOLDERS_TABLE) if idx == index][0]

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        column_name = self.nameOfColumn(index.column())
        if role == Qt.DisplayRole:
            if column_name == 'status':
                return None

        if role == Qt.DecorationRole:
            if column_name == 'status':
                if QSqlTableModel.data(self, index) == 1:
                    return QIcon(':tick.png')
                else:
                    return QIcon(':exclamation.png')
        return QSqlTableModel.data(self, index, role)

    def selectRowByModelId(self, last_id):
        for i in range(self.rowCount()):
            if last_id == self.record(i).value("id"):
                self.parent().selectRow(i)
                break


class FoldersItemsDelegate(QStyledItemDelegate):
    def __init__(self, parent):
        QStyledItemDelegate.__init__(self, parent)

    def createEditor(self, parent, option, index):
        return None


class SearchResultsTableModel(QtCore.QAbstractTableModel):
    def __init__(self, data, parent):
        super(SearchResultsTableModel, self).__init__(parent)
        self._data = data
        sorter(self, self.parent(), 2)

    def hasMountedDrive(self, index):
        index_column = self.colIndexByName('Drive')
        value = str(self._data.iloc[index.row()][index_column])
        return gdb.isDriveActiveByLabel(value)

    def rowData(self, index):
        row_data = []
        for idx in enumerate(HEADER_SEARCH_RESULTS_TABLE):
            row_data.append(str(self._data.iloc[index.row()][idx[0]]))
        return row_data

    def colIndexByName(self, name):
        return [ix for ix, col in enumerate(HEADER_SEARCH_RESULTS_TABLE) if col == name][0]

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole:
                return str(self._data.iloc[index.row()][index.column()])
            if role == Qt.TextAlignmentRole:
                if index.column() == 2 or index.column() == 3:
                    return Qt.AlignRight

            if role == Qt.ForegroundRole:
                if index.column() == self.colIndexByName('Drive'):
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


class SearchResultsTableItemsDelegate(QStyledItemDelegate):
    def __init__(self, parent):
        QStyledItemDelegate.__init__(self, parent)

    def nameOfColumn(self, index):
        return [col for idx, col in enumerate(HEADER_SEARCH_RESULTS_TABLE) if idx == index][0]

    def createEditor(self, parent, option, index):
        return None


class DrivesTableModel(QtSql.QSqlTableModel):
    def __init__(self):
        super(DrivesTableModel, self).__init__()
        self._data = []
        self.table = 'drives'
        self.setTable(self.table)
        self.setEditStrategy(self.OnRowChange)
        self.setColumnsName()
        self.setSort(self.fieldIndex("size"), Qt.DescendingOrder)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        column_name = nameOfColumn(index.column())

        if role == Qt.DisplayRole:
            if column_name == 'active':
                return None

        if role == Qt.DisplayRole:
            if column_name == 'serial':
                return QSqlTableModel.data(self, index)

        if role == Qt.DecorationRole:
            if column_name == 'active':
                if QSqlTableModel.data(self, index) == 1:
                    return QIcon(':tick.png')
                else:
                    return QIcon(':cross.png')

        if role == Qt.TextAlignmentRole:
            if column_name == 'size':
                return Qt.AlignVCenter + Qt.AlignRight
        # default, no specific condition found
        return QSqlTableModel.data(self, index, role)

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


def nameOfColumn(idx):
    names = HEADER_DRIVES_TABLE.keys()
    for index, name in enumerate(names):
        if index == idx:
            return name


class DrivesItemsDelegate(QStyledItemDelegate):
    def __init__(self, parent):
        QStyledItemDelegate.__init__(self, parent)

    def createEditor(self, parent, option, index):
        disabled = ['serial', 'name', 'active', 'path']
        if nameOfColumn(index.column()) in disabled:
            editor = QLineEdit(parent)
            editor.setDisabled(True)
            return editor
        elif 'label' == nameOfColumn(index.column()):
            editor = QLineEdit(parent)
            editor.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            return editor
        elif 'size' == nameOfColumn(index.column()):
            spinbox = QSpinBox(parent)
            spinbox.setRange(0, 2000000)
            spinbox.setSingleStep(100)
            spinbox.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            return spinbox
        else:
            return None

