# this class can be only imported
import os
import shutil
import subprocess
import sys
from contextlib import redirect_stdout

from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import QMimeDatabase, QDir, QStandardPaths
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMessageBox, QTabWidget, QFileDialog, QApplication, QMainWindow

from mymodules import GDBModule as gdb

APP_NAME = 'Indexer'
DATABASE_NAME = 'indexer.sqlite'
DATABASE_DRIVER = 'QSQLITE'

CSV_COLUMN_SEPARATOR = ','
CSV_LINE_SEPARATOR = '\n'

CODECS = ['ascii', 'big5', 'big5hkscs', 'cp037', 'cp273', 'cp424', 'cp437',
          'cp500', 'cp720', 'cp737', 'cp775', 'cp850', 'cp852', 'cp855', 'cp856', 'cp857',
          'cp858', 'cp860', 'cp861', 'cp862', 'cp863', 'cp864', 'cp865', 'cp866', 'cp869',
          'cp874', 'cp875', 'cp932', 'cp949', 'cp950', 'cp1006', 'cp1026', 'cp1125',
          'cp1140', 'cp1250', 'cp1251', 'cp1252', 'cp1253', 'cp1254', 'cp1255', 'cp1256',
          'cp1257', 'cp1258', 'euc_jp', 'euc_jis_2004', 'euc_jisx0213', 'euc_kr',
          'gb2312', 'gbk', 'gb18030', 'hz', 'iso2022_jp', 'iso2022_jp_1', 'iso2022_jp_2',
          'iso2022_jp_2004', 'iso2022_jp_3', 'iso2022_jp_ext', 'iso2022_kr', 'latin_1',
          'iso8859_2', 'iso8859_3', 'iso8859_4', 'iso8859_5', 'iso8859_6', 'iso8859_7',
          'iso8859_8', 'iso8859_9', 'iso8859_10', 'iso8859_11', 'iso8859_13',
          'iso8859_14', 'iso8859_15', 'iso8859_16', 'johab', 'koi8_r', 'koi8_t', 'koi8_u',
          'kz1048', 'mac_cyrillic', 'mac_greek', 'mac_iceland', 'mac_latin2', 'mac_roman',
          'mac_turkish', 'ptcp154', 'shift_jis', 'shift_jis_2004', 'shift_jisx0213',
          'utf_32', 'utf_32_be', 'utf_32_le', 'utf_16', 'utf_16_be', 'utf_16_le', 'utf_7',
          'utf_8', 'utf_8_sig']

REQUIRED_TABLES = {'drives', 'folders', 'extensions', 'files', 'categories', 'preferences'}
CATEGORIES = {'Audio': ':music.png', 'Compressed': ':compress.png',
              'Disc and media': ':cd.png', 'Data and database': ':database.png',
              'E-mail': ':email.png', 'Executable': ':lightning.png',
              'Font': ':font.png', 'Image': ':image.png',
              'Internet': ':www_page.png', 'Presentation': ':chart_pie.png',
              'Programming': ':page_white_code.png', 'Spreadsheet': ':table_multiple.png',
              'System': ':application_osx_terminal.png', 'Video': ':television.png',
              'Word': ':page_white_word.png'}

HEADER_SEARCH_RESULTS_TABLE = ['Directory', 'Filename', 'Size', 'Extension', 'Drive']
HEADER_DRIVES_TABLE = {"serial": "Serial Number", "name": "Drive Name", "label": "Own Label", "size": "Size (GB)",
                       "active": "Active"}

default_extensions = [['aif', 1, 0], ['cda', 1, 0], ['mid', 1, 0], ['midi', 1, 0], ['mp3', 1, 1],
                      ['mpa', 1, 0], ['ogg', 1, 1], ['wav', 1, 0], ['wma', 1, 0], ['wpl', 1, 0],
                      ['7z', 2, 0], ['arj', 2, 0], ['deb', 2, 0], ['pkg', 2, 0], ['rar', 2, 1],
                      ['rpm', 2, 0], ['tar.gz', 2, 0], ['z', 2, 0], ['zip', 2, 1], ['dmg', 3, 0],
                      ['iso', 3, 0], ['toast', 3, 0], ['vcd', 3, 0], ['csv', 4, 1], ['dat', 4, 0],
                      ['db', 4, 1], ['dbf', 4, 0], ['log', 4, 0], ['mdb', 4, 0], ['sav', 4, 0],
                      ['sql', 4, 1], ['tar', 4, 0], ['xml', 4, 1], ['email', 5, 0], ['eml', 5, 0],
                      ['emlx', 5, 0], ['msg', 5, 0], ['oft', 5, 0], ['ost', 5, 0], ['pst', 5, 0],
                      ['vcf', 5, 0], ['apk', 6, 0], ['bat', 6, 0], ['bin', 6, 0], ['cgi', 6, 0],
                      ['com', 6, 0], ['exe', 6, 1], ['gadget', 6, 0], ['jar', 6, 0], ['msi', 6, 1],
                      ['wsf', 6, 0], ['fnt', 7, 0], ['fon', 7, 0], ['otf', 7, 1], ['ttf', 7, 1],
                      ['ai', 8, 1], ['bmp', 8, 0], ['gif', 8, 0], ['ico', 8, 0], ['jpeg', 8, 1],
                      ['jpg', 8, 1], ['png', 8, 1], ['ps', 8, 0], ['psd', 8, 0], ['svg', 8, 0],
                      ['tif', 8, 0], ['tiff', 8, 0], ['asp', 9, 1], ['aspx', 9, 1], ['cer', 9, 0],
                      ['cfm', 9, 0], ['css', 9, 1], ['htm', 9, 0], ['html', 9, 1], ['js', 9, 1],
                      ['jsp', 9, 0], ['part', 9, 0], ['rss', 9, 0], ['xhtml', 9, 0], ['key', 10, 0],
                      ['odp', 10, 0], ['pps', 10, 0], ['ppt', 10, 1], ['pptx', 10, 1], ['c', 11, 0],
                      ['pl', 11, 0], ['class', 11, 0], ['cpp', 11, 0], ['cs', 11, 0], ['h', 11, 1],
                      ['java', 11, 1], ['php', 11, 1], ['py', 11, 1], ['sh', 11, 1], ['swift', 11, 0],
                      ['vb', 11, 0], ['json', 11, 0], ['ods', 12, 1], ['xls', 12, 1], ['xlsm', 12, 1],
                      ['xlsx', 12, 1], ['bak', 13, 0], ['cab', 13, 0], ['cfg', 13, 0], ['cpl', 13, 0],
                      ['cur', 13, 0], ['dll', 13, 0], ['dmp', 13, 0], ['drv', 13, 0], ['icns', 13, 0],
                      ['ini', 13, 0], ['lnk', 13, 0], ['sys', 13, 0], ['tmp', 13, 0], ['3g2', 14, 0],
                      ['3gp', 14, 0], ['avi', 14, 1], ['flv', 14, 0], ['h264', 14, 0], ['m4v', 14, 1],
                      ['mkv', 14, 1], ['mov', 14, 0], ['mp4', 14, 1], ['mpg', 14, 1], ['mpeg', 14, 1],
                      ['rm', 14, 0], ['swf', 14, 0], ['vob', 14, 0], ['wmv', 14, 1], ['srt', 14, 1],
                      ['sub', 14, 1], ['doc', 15, 1], ['docx', 15, 1], ['odt', 15, 1], ['pdf', 15, 1],
                      ['rtf', 15, 0], ['tex', 15, 0], ['txt', 15, 0], ['wpd', 15, 0]]

PREFERENCES = [
    ['header_to_csv', 'Add header to exported csv', '0', '0', 'bool', '1'],
    ['file_dialog_modal', 'File Information is modal', '1', '1', 'bool', '1'],
    ['window_size', 'Dimension for window when start (width, height)', '1000, 800', '1000, 800', 'str', '0'],
    ['settings_tabs_order', 'Preferred order for settings tabs', '0, 1, 2, 3, 4', '0, 1, 2, 3, 4', 'str', '0'],
]


def findMainWindow():
    # Global function to find the (open) QMainWindow in application
    app = QApplication.instance()
    for widget in app.topLevelWidgets():
        if isinstance(widget, QMainWindow):
            return widget
    return None


def getMimeTypeForExtension(extension_name: str) -> str:
    """
    :param extension_name:
    :return:
    """
    mt = QMimeDatabase()
    z = mt.mimeTypeForFile(f'*.{extension_name}')
    return z.iconName()


def getIcon(item: str, size: int = 24) -> object:
    """
    :param item:
    :param size:
    :return:
    get icon for mimes
    if it is missing from theme, will load from resources
    """
    mime_for_extension = getMimeTypeForExtension(item)
    icon = QtGui.QIcon.fromTheme(mime_for_extension)
    if icon.isNull():
        icon = QtGui.QIcon(f':' + mime_for_extension + '.png')
    return icon.pixmap(size)


def formatDictToHuman(d: dict) -> str:
    """
    :param d:
    :return:
    return a string as list from a dict
    """
    lista = []
    for k, v in d.items():
        item = k + ' : ' + v
        lista.append(item)
    human_list = "\n".join(lista)
    return human_list


def putInFile(data: str, filename: str = 'out.txt') -> None:
    """
    :param data:
    :param filename:
    """
    with open(filename, 'w') as f:
        with redirect_stdout(f):
            print(data)


def iconForButton(name: str) -> QIcon:
    """
    :param name:
    :return:
    """
    return QtWidgets.QApplication.style().standardIcon(getattr(QtWidgets.QStyle, name))


def confirmationDialog(title: str, message: str) -> object:
    """
    :param title:
    :param message:
    :return:
    """
    msg_box = QtWidgets.QMessageBox()
    msg_box.setIcon(QMessageBox.Warning)
    msg_box.setText(message)
    msg_box.setWindowTitle(title)
    msg_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
    return msg_box.exec() == QMessageBox.Ok


def tabIndexByName(tab_widget: QTabWidget, tab_name: str) -> int:
    """
    :param tab_widget:
    :param tab_name:
    :return:
    """
    for index in range(tab_widget.count()):
        if tab_name == tab_widget.tabText(index):
            return index


def categoriesCombo():
    categories = gdb.getAll('categories')
    combo = QtWidgets.QComboBox()
    combo.addItem('Categories')
    for item in categories:
        combo.addItem(QIcon(item['icon']), item['category'])
    return combo


def getDatabaseLocation():
    return QDir(getAppLocation()).filePath(DATABASE_NAME)


def getAppLocation():
    return QStandardPaths.writableLocation(QStandardPaths.AppDataLocation)


def getDefaultDir():
    return QStandardPaths.writableLocation(QStandardPaths.HomeLocation)


def exportDataBase():
    sqlite_file = getDatabaseLocation()
    filename_save = getDefaultDir() + os.sep + DATABASE_NAME
    filename, _ = QFileDialog.getSaveFileName(
        None,
        "EXPORT DATABASE",
        filename_save,
        "SQLITE Files (*.sqlite)"
    )
    if filename:
        shutil.copyfile(sqlite_file, filename)
        QtWidgets.QMessageBox.information(None, 'Database Export', 'Exported successfully!')
        return
    pass


def importDataBase():
    confirmation_text = f"Your database will be replaced and all indexed files will be lost!<br><br>Do you proceed?"
    confirm = confirmationDialog("Do you import database?", confirmation_text)
    if not confirm:
        return
    filename = QFileDialog.getOpenFileName(None, "Select database", getDefaultDir(),
                                           filter="SQLITE Files (*.sqlite)")

    if filename[0] and filename[1]:
        if isValidSQLiteDatabase(filename[0]):
            shutil.copyfile(filename[0], getDatabaseLocation())
            QtWidgets.QMessageBox.information(None, 'Database imported',
                                              "Database has been imported!<br><br>Please restart application!")


# https://www.sqlite.org/fileformat2.html#the_database_header
# check if header is correct
def isValidSQLiteDatabase(database_file_path):
    f = open(database_file_path, "rb")
    while b := f.read(15):
        if b.decode('ascii') == 'SQLite format 3':
            return True


def goToFileBrowser(path):
    if sys.platform == 'win32':
        subprocess.Popen(['start', path], shell=True)

    elif sys.platform == 'darwin':
        subprocess.Popen(['open', path])

    else:
        try:
            # xdg-open *should* be supported by recent Gnome, KDE, Xfce
            subprocess.Popen(['xdg-open', path])
        except OSError:
            pass
        # er, think of something else to try


def setPreferenceById(pid, checkbox):
    value = checkbox.isChecked()
    gdb.setPreferenceById(pid, int(value))

def setPreferenceByName(name, value):
    gdb.setPreferenceByName(name, value)

def getPreference(name):
    return gdb.getPreferenceByName(name)