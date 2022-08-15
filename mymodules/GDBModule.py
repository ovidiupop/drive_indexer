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
        self.required_tables = {'drives', 'folders', 'extensions', 'files'}
        self.preselected_extensions = ['py', 'csv', 'php']
        # self.default_extensions = ['mkv', 'mov', 'mp4', 'avi', 'srt', 'sub']
        self.default_extensions = ['csv', 'txt', 'xml', 'js', 'php', 'py', 'mkv', 'mov', 'mp4', 'avi', 'srt', 'sub']

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
            'DROP TABLE IF EXISTS drives',
            'DROP TABLE IF EXISTS folders',
            'DROP TABLE IF EXISTS extensions',
            'DROP TABLE IF EXISTS files',
            'CREATE TABLE drives ( serial TEXT PRIMARY KEY, name TEXT NOT NULL, label TEXT NOT NULL, size FLOAT NOT NULL, active INTEGER DEFAULT 0, partitions TEXT NOT NULL, path TEXT NOT NULL)',
            'CREATE TABLE folders ( id INTEGER PRIMARY KEY, path TEXT NOT NULL, drive_id TEXT)',
            'CREATE TABLE extensions ( id INTEGER PRIMARY KEY, extension TEXT NOT NULL, selected INTEGER DEFAULT 0)',
            'CREATE TABLE files ( id INTEGER PRIMARY KEY, dir TEXT NOT NULL, filename TEXT NOT NULL, size INTEGER, '
            'extension_id INTEGER NOT NULL, folder_id INTEGER NOT NULL)',
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

        # populate tables with default values
        # populate extensions
        for extension in self.default_extensions:
            selected = 0
            if extension in self.preselected_extensions:
                selected = 1
            query.prepare("""INSERT INTO extensions (extension, selected) VALUES (?, ?)""")
            query.addBindValue(extension)
            query.addBindValue(selected)
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

        # self.populateDrives(query)

    def populateDrives(self, query):
        # populate tables with default values
        # populate drives
        name = self.default_drive['name']
        size = self.default_drive['size']
        query.prepare("""INSERT INTO drives (name, size) VALUES (?, ?)""")
        query.addBindValue(name)
        query.addBindValue(size)
        query.exec()

        # check if drives has been populated
        if query.exec("SELECT name FROM drives"):
            query.first()
            name = query.value('name')
            if not name:
                QtWidgets.QMessageBox.critical(
                    None, 'DB Integrity Error',
                    'Missing data from drives')
                sys.exit(1)
