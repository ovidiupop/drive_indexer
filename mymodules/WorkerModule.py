import os
from PyQt5 import QtCore, QtSql
from mymodules import GDBModule


def percentage(part, whole):
    """calculate percents of progress """
    result = 100 * float(part) / float(whole)
    return int(result)


def countTotalFiles(roots):
    """ count the files in directories roots is array of folders
    """
    count = 0
    for root in roots:
        for root_dir, cur_dir, files in os.walk(root, topdown=True):
            count += len(files)
    return count


class Indexer(QtCore.QObject):
    """ Indexer class
    The worker responsible with indexing of files to database
    """
    match_found = QtCore.pyqtSignal()
    directory_changed = QtCore.pyqtSignal(str)
    finished = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.con = GDBModule.connection('indexer_connection')
        self.con.open()
        self.extensions = self.getExtensionsList()
        self.folders_to_index = []
        self.found_files = 0
        self.total_files = 0
        self.checked_files = 0
        self.percentage = 0
        self.folder_id = 0
        self.remove_indexed = True

    def getExtensionsList(self):
        extensions = {}
        all_extensions = GDBModule.getAll('extensions')
        for ext in all_extensions:
            extensions[ext['id']] = ext['extension']
        return extensions

    def setExtensions(self, extensions):
        self.extensions = extensions

    # use the @QtCore.pyqtSlot() decorator to
    # make the worker's methods into true Qt slots
    @QtCore.pyqtSlot()
    def doIndex(self):
        self.total_files = countTotalFiles(self.folders_to_index)
        for folder in self.folders_to_index:
            self.folder_id = self.folderId(folder)
            if self.remove_indexed:
                self.removeFilesBeforeReindex(self.folder_id)
            self._index(folder)
        # finish the thread
        self.con.close()
        self.finished.emit()

    def removeFilesBeforeReindex(self, folder_id):
        """ before reindex a folder, remove old indexed files from that folder
        to prevent duplication
        """
        query = QtSql.QSqlQuery(self.con)
        query.prepare("""Delete from files where folder_id=:folder_id""")
        query.bindValue(':folder_id', folder_id)
        if not query.exec():
            GDBModule.printQueryErr(query, 'removeFilesBeforeReindex')

    def _index(self, path):
        """recursive method for indexing files"""
        self.directory_changed.emit(path)
        # switch to new directory (root or recursive)
        directory = QtCore.QDir(path)
        directory.setFilter(directory.filter() | QtCore.QDir.NoDotAndDotDot | QtCore.QDir.NoSymLinks)
        for entry in directory.entryInfoList():
            if entry.isFile():
                self.checked_files += 1
                self.percentage = percentage(self.checked_files, self.total_files)

            # check if we have matched extension (zip / tar.gz) or there is no any extension to match
            file_ext = entry.suffix()
            file_ext_complete = entry.completeSuffix()
            if file_ext in self.extensions or file_ext_complete in self.extensions.values() or self.extensions == {}:
                extension_id = 0
                if file_ext:
                    extension_id = self.extensionId(file_ext)
                elif entry.completeSuffix():
                    extension_id = self.extensionId(file_ext_complete)
                item = {'dir': path, 'filename': entry.fileName(), 'size': entry.size(),
                        'extension_id': extension_id, 'folder_id': self.folder_id}
                self.match_found.emit()

                # insert file in database
                self.addFile(item)
            if entry.isDir():
                self._index(entry.filePath())

    def extensionId(self, extension):
        for key, value in self.extensions.items():
            if extension == value:
                return key

        # """Get extension's id inside of worker"""
        # query = QtSql.QSqlQuery(self.con)
        # query.prepare(""" SELECT id FROM extensions WHERE extension=:extension """)
        # query.bindValue(':extension', extension)
        # if query.exec():
        #     query.next()
        #     return query.value(0)
        # else:
        #     GDBModule.printQueryErr(query, 'extensionId')

    def addFile(self, file):
        """Used by indexer thread with own connection
        to add new-found file to database"""
        query = QtSql.QSqlQuery(self.con)
        query.prepare(
            "INSERT INTO files (%s) VALUES (%s)" % (','.join(file.keys()), ','.join("?" * len(file.values()))))
        for binder in file.values():
            query.addBindValue(binder)
        if query.exec():
            return True
        else:
            GDBModule.printQueryErr(query, 'addFile')

    def folderId(self, path):
        """Get folder id inside of worker"""
        query = QtSql.QSqlQuery(self.con)
        query.prepare("SELECT id FROM folders WHERE path=:path")
        query.bindValue(':path', str(path))
        if query.exec():
            while query.first():
                return query.value(0)
