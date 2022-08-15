import sys
from PyQt5 import QtWidgets, QtSql
from PyQt5.QtCore import qDebug

from mymodules import HumanReadableSize
from mymodules.HumanReadableSize import HumanBytes

DATABASE_NAME = 'indexer.db'

def connection(name):
    driver = 'QSQLITE'
    database = DATABASE_NAME
    db = QtSql.QSqlDatabase.addDatabase(driver, name)
    db.setDatabaseName(database)
    return db


def printQueryErr(query, method_name=''):
    db_err = "Database Error: %s" % query.lastError().databaseText()
    errors = [db_err, query.lastError().text(), query.lastQuery(), query.executedQuery(), method_name]
    print(", ".join(errors))


def allExtensions():
    extensions = []
    query = QtSql.QSqlQuery()
    if query.exec("SELECT extension FROM extensions ORDER BY id"):
        while query.next():
            extensions.append(query.value('extension'))
    return extensions


def preselectedExtensions():
    query = QtSql.QSqlQuery()
    selected = []
    if query.exec("SELECT extension FROM extensions where selected=1 ORDER BY id"):
        while query.next():
            selected.append(query.value('extension'))
    return selected


def allFolders(hide_inactive=True):
    folders = []
    query = QtSql.QSqlQuery()
    if hide_inactive:
        command = "SELECT fo.path FROM folders fo " \
                  "left join drives d on d.serial=fo.drive_id " \
                  "where d.active=1"
    else:
        command = "SELECT path FROM folders"
    if query.exec(command):
        while query.next():
            folders.append(query.value('path'))
    return folders


def folderExists(folder):
    query = QtSql.QSqlQuery()
    query.prepare("SELECT path FROM folders where path=:path limit 1")
    query.bindValue(':path', folder)
    return query.exec() and query.first()


def addFolder(folder, serial):
    query = QtSql.QSqlQuery()
    query.prepare(""" INSERT INTO folders (path, drive_id) VALUES (?,?) """)
    query.addBindValue(folder)
    query.addBindValue(serial)
    return query.exec()


def deleteFoldersDB(paths):
    query = QtSql.QSqlQuery()
    for path in paths:
        folder_id = folderId(path)
        query.prepare("""Delete from folders where path=:path""")
        query.bindValue(':path', path)
        if query.exec():
            deleteFilesDB(folder_id)
        else:
            printQueryErr(query, 'cleanFolders')
            return False
    return True


def deleteFilesDB(folder_id):
    query = QtSql.QSqlQuery()
    query.prepare("""Delete from files where folder_id=:folder_id""")
    query.bindValue(':folder_id', folder_id)
    if query.exec():
        return True
    else:
        printQueryErr(query, 'clearFiles')


def folderId(path):
    query = QtSql.QSqlQuery()
    query.prepare("select id from folders where path=:path")
    query.bindValue(':path', path)
    if query.exec():
        while query.next():
            folder_id = query.value(0)
            return folder_id
    else:
        printQueryErr(query, 'folderId')


def extensionsToInt(extensions_list_string):
    query = QtSql.QSqlQuery()
    placeholder = ','.join("?" * len(extensions_list_string))
    query.prepare('SELECT id FROM extensions WHERE extension IN (%s)' % placeholder)
    for binder in extensions_list_string:
        query.addBindValue(str(binder))
    if query.exec():
        ext = []
        while query.next():
            ext.append(query.value(0))
        return ext
    else:
        printQueryErr(query, 'extensionsToInt')
        qDebug(query.lastQuery())


def findFiles(search_term, extensions):
    if not search_term:
        return
    extensions_list_ids = extensionsToInt(extensions) or []
    placeholder = ','.join("?" * len(extensions_list_ids))
    query = QtSql.QSqlQuery()
    if len(extensions_list_ids) > 0:
        query.prepare("select f.dir, f.filename, f.size, e.extension, d.label "
                      "from files f "
                      "left join extensions e on e.id=f.extension_id "
                      "left join folders fo on fo.id=f.folder_id "
                      "left join drives d on d.serial=fo.drive_id "
                      "where f.extension_id in (%s) and (f.dir like ? or f.filename like ?)" % placeholder)
        for binder in extensions_list_ids:
            query.addBindValue(binder)
    else:
        query.prepare("select f.dir, f.filename, f.size, e.extension, fo.label "
                      "from files f "
                      "left join folders fo on fo.id=f.folder_id "
                      "left join drives d on d.serial=fo.drive_id "
                      "left join extensions e on e.id=f.extension_id "
                      "where (f.dir like ? or f.filename like ?)")
    query.addBindValue("%" + search_term + "%")
    query.addBindValue("%" + search_term + "%")

    if query.exec():
        results = []
        while query.next():
            item = [
                query.value('dir'),
                query.value('filename'),
                HumanBytes.format(query.value('size'), True),
                query.value('extension'),
                query.value('label')
            ]
            results.append(item)
        return results


def allDrives():
    drives = []
    query = QtSql.QSqlQuery()
    if query.exec("SELECT serial, name, label, size, active, partitions FROM drives"):
        while query.next():
            drive = {
                'serial': query.value('serial'),
                'name': query.value('name'),
                'label': query.value('label'),
                'active': query.value('active'),
                'size': query.value('size'),
                'partitions': query.value('partitions'),
            }
            drives.append(drive)
    return drives


def setDrivesActive(drives):
    if not drives:
        return
    query = QtSql.QSqlQuery()
    query.prepare("UPDATE drives SET active=0, path='unmounted'")
    if query.exec():
        for drive in drives:
            query.prepare('UPDATE drives SET active=1, path=:path WHERE serial=:serial')
            query.bindValue(':path', drive['path'])
            query.bindValue(':serial', drive['serial'])
            query.exec()


def dummyDataResult():
    term = 'index'
    query = QtSql.QSqlQuery()
    query.prepare("select dir, filename, size, extension_id, folder_id from files "
                  "where filename like '%index%'")
    if query.exec():
        results = []
        while query.next():
            item = [
                query.value('dir'),
                query.value('filename'),
                query.value('size'),
                query.value('extension_id'),
                query.value('folder_id')
            ]
            results.append(item)
        return results


def extensionExists(extension):
    query = QtSql.QSqlQuery()
    query.prepare("SELECT extension FROM extensions WHERE extension=:extension")
    query.bindValue(":extension", str(extension))
    return query.exec() and query.first()


def addNewExtension(extension):
    if not extension or extensionExists(extension):
        return
    query = QtSql.QSqlQuery()
    query.prepare(""" INSERT INTO extensions (extension) VALUES (?)""")
    query.addBindValue(extension)
    return query.exec()


def setPreferredExtensions(extensions):
    if not extensions:
        return
    query = QtSql.QSqlQuery()
    query.prepare("UPDATE extensions SET selected=0 WHERE 1")
    if query.exec():
        placeholder = ','.join("?" * len(extensions))
        query.prepare('UPDATE extensions SET selected=1 WHERE extension IN (%s)' % placeholder)
        for binder in extensions:
            query.addBindValue(str(binder))
        return query.exec()


def removeExtensions(extensions):
    query = QtSql.QSqlQuery()
    exts_id = extensionsToInt(extensions)
    # clear indexed files with extension
    placeholder = ','.join("?" * len(exts_id))
    query.prepare('DELETE FROM files WHERE extension_id IN (%s)' % placeholder)
    for binder in exts_id:
        query.addBindValue(str(binder))
    if query.exec():
        # delete extension itself
        query.prepare('DELETE FROM extensions WHERE id IN (%s)' % placeholder)
        for binder in exts_id:
            query.addBindValue(str(binder))
        return query.exec()
    return False


def getDriveByPath(path):
    query = QtSql.QSqlQuery()
    query.prepare("SELECT serial FROM drives WHERE path=:path and active=1")
    query.bindValue(":path", str(path))
    if query.exec():
        while query.first():
            return query.value('serial')


def driveSerialExists(serial):
    query = QtSql.QSqlQuery()
    query.prepare("SELECT * FROM drives WHERE serial=:serial")
    query.bindValue(":serial", str(serial))
    return query.exec() and query.first()


class GDatabase:
    def __init__(self):
        super().__init__()
        driver = 'QSQLITE'
        database = DATABASE_NAME
        self.con = QtSql.QSqlDatabase.addDatabase(driver)
        self.con.setDatabaseName(database)
        # self.default_drive = {'name': 'tecra', 'size': 500}  # size in gigabytes
        self.required_tables = {'drives', 'folders', 'extensions', 'files', 'categories'}
        self.categories = ['Audio', 'Compressed', 'Disc and media', 'Data and database', 'E-mail', 'Executable',
                           'Font', 'Image', 'Internet', 'Presentation', 'Programming', 'Spreadsheet', 'System',
                           'Video', 'Word']
        self.default_extensions = [['aif', 1, 0], ['cda', 1, 0], ['mid', 1, 0], ['midi', 1, 0], ['mp3', 1, 1], ['mpa', 1, 0], ['ogg', 1, 1], ['wav', 1, 0], ['wma', 1, 0], ['wpl', 1, 0], ['7z', 2, 0], ['arj', 2, 0], ['deb', 2, 0], ['pkg', 2, 0], ['rar', 2, 1], ['rpm', 2, 0], ['tar.gz', 2, 0], ['z', 2, 0], ['zip', 2, 1], ['dmg', 3, 0], ['iso', 3, 0], ['toast', 3, 0], ['vcd', 3, 0], ['csv', 4, 1], ['dat', 4, 0], ['db', 4, 1], ['dbf', 4, 0], ['log', 4, 0], ['mdb', 4, 0], ['sav', 4, 0], ['sql', 4, 1], ['tar', 4, 0], ['xml', 4, 1], ['email', 5, 0], ['eml', 5, 0], ['emlx', 5, 0], ['msg', 5, 0], ['oft', 5, 0], ['ost', 5, 0], ['pst', 5, 0], ['vcf', 5, 0], ['apk', 6, 0], ['bat', 6, 0], ['bin', 6, 0], ['cgi', 6, 0], ['com', 6, 0], ['exe', 6, 1], ['gadget', 6, 0], ['jar', 6, 0], ['msi', 6, 1], ['wsf', 6, 0], ['fnt', 7, 0], ['fon', 7, 0], ['otf', 7, 1], ['ttf', 7, 1], ['ai', 8, 1], ['bmp', 8, 0], ['gif', 8, 0], ['ico', 8, 0], ['jpeg', 8, 1], ['jpg', 8, 1], ['png', 8, 1], ['ps', 8, 0], ['psd', 8, 0], ['svg', 8, 0], ['tif', 8, 0], ['tiff', 8, 0], ['asp', 9, 1], ['aspx', 9, 1], ['cer', 9, 0], ['cfm', 9, 0], ['css', 9, 1], ['htm', 9, 0], ['html', 9, 1], ['js', 9, 1], ['jsp', 9, 0], ['part', 9, 0], ['rss', 9, 0], ['xhtml', 9, 0], ['key', 10, 0], ['odp', 10, 0], ['pps', 10, 0], ['ppt', 10, 1], ['pptx', 10, 1], ['c', 11, 0], ['pl', 11, 0], ['class', 11, 0], ['cpp', 11, 0], ['cs', 11, 0], ['h', 11, 1], ['java', 11, 1], ['php', 11, 1], ['py', 11, 1], ['sh', 11, 1], ['swift', 11, 0], ['vb', 11, 0], ['json', 11, 0], ['ods', 12, 1], ['xls', 12, 1], ['xlsm', 12, 1], ['xlsx', 12, 1], ['bak', 13, 0], ['cab', 13, 0], ['cfg', 13, 0], ['cpl', 13, 0], ['cur', 13, 0], ['dll', 13, 0], ['dmp', 13, 0], ['drv', 13, 0], ['icns', 13, 0], ['ini', 13, 0], ['lnk', 13, 0], ['sys', 13, 0], ['tmp', 13, 0], ['3g2', 14, 0], ['3gp', 14, 0], ['avi', 14, 1], ['flv', 14, 0], ['h264', 14, 0], ['m4v', 14, 1], ['mkv', 14, 1], ['mov', 14, 0], ['mp4', 14, 1], ['mpg', 14, 1], ['mpeg', 14, 1], ['rm', 14, 0], ['swf', 14, 0], ['vob', 14, 0], ['wmv', 14, 1], ['srt', 14, 1], ['sub', 14, 1], ['doc', 15, 1], ['docx', 15, 1], ['odt', 15, 1], ['pdf', 15, 1], ['rtf', 15, 0], ['tex', 15, 0], ['txt', 15, 0], ['wpd', 15, 0]]
        self.checkDatabaseConnection()
        self.ensureData()

    def checkDatabaseConnection(self):
        if not self.con.open():
            QtWidgets.QMessageBox.critical(
                None, 'DB Connection Error',
                'Could not open database: '
                f'{self.con.lastError().databaseText()}')
            sys.exit(1)

    def ensureData(self):
        self.tablesExists()
        return True

    def tablesExists(self):
        required_tables = self.required_tables
        missing_tables = required_tables - set(self.con.tables())
        if missing_tables:
            self.addTablesDatabase()

    def addTablesDatabase(self):
        query = QtSql.QSqlQuery()
        commands = [
            'DROP TABLE IF EXISTS categories',
            'DROP TABLE IF EXISTS drives',
            'DROP TABLE IF EXISTS folders',
            'DROP TABLE IF EXISTS extensions',
            'DROP TABLE IF EXISTS files',
            'CREATE TABLE categories (id INTEGER PRIMARY KEY, category TEXT NOT NULL)',
            'CREATE TABLE drives ( serial TEXT PRIMARY KEY, name TEXT NOT NULL, label TEXT NOT NULL, size FLOAT NOT NULL, active INTEGER DEFAULT 0, partitions TEXT NOT NULL, path TEXT NOT NULL)',
            'CREATE TABLE folders ( id INTEGER PRIMARY KEY, path TEXT NOT NULL, drive_id TEXT, FOREIGN KEY(drive_id) REFERENCES drives(serial))',
            'CREATE TABLE extensions ( id INTEGER PRIMARY KEY, extension TEXT NOT NULL, category_id INTEGER NOT NULL, selected INTEGER DEFAULT 0, FOREIGN KEY(category_id) REFERENCES categories(id))',
            'CREATE TABLE files ( id INTEGER PRIMARY KEY, dir TEXT NOT NULL, filename TEXT NOT NULL, size INTEGER, '
            'extension_id INTEGER NOT NULL, folder_id INTEGER NOT NULL, FOREIGN KEY(extension_id) REFERENCES extensions(id), FOREIGN KEY(folder_id) REFERENCES folders(id))',
        ]

        # each query must be prepared before execution
        for command in commands:
            query = QtSql.QSqlQuery()
            query.prepare(f"""{command};""")
            if not query.exec():
                print(f"""Error running {command} command""")

        # check if we have all tables created
        required_tables = self.required_tables
        missing_tables = required_tables - set(self.con.tables())
        if missing_tables:
            QtWidgets.QMessageBox.critical(
                None, 'DB Integrity Error',
                'Missing tables, please repair DB: '
                f'{missing_tables}')
            sys.exit(1)

        # populate categories
        for category in self.categories:
            query.prepare("""INSERT INTO categories (category) VALUES (?)""")
            query.addBindValue(category)
            query.exec()

        # populate tables with default values
        # populate extensions
        for extension in self.default_extensions:
            query.prepare("""INSERT INTO extensions (extension, category_id, selected) VALUES (?, ?, ?)""")
            query.addBindValue(extension[0])
            query.addBindValue(extension[1])
            query.addBindValue(extension[2])
            query.exec()

        # check if extension has been populated
        if query.exec("SELECT extension FROM extensions"):
            query.first()
            extension = query.value('extension')
            if not extension:
                QtWidgets.QMessageBox.critical(
                    None, 'DB Integrity Error',
                    'Missing data from extensions')
                sys.exit(1)

