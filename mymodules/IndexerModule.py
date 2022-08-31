import os

from PyQt5 import QtCore, QtSql
from PyQt5.QtCore import QObject, pyqtSignal, QRunnable, pyqtSlot

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


class WorkerKilledException(Exception):
    pass


# we need this WorkerSignals, because QRunnable hasn't signals
# WorkerSignals is derived from Object and have signals
class WorkerSignals(QObject):
    progress = pyqtSignal(int)
    match_found = QtCore.pyqtSignal()
    directory_changed = QtCore.pyqtSignal(str)
    finished = QtCore.pyqtSignal()
    status_folder_changed = QtCore.pyqtSignal()


class JobRunner(QRunnable):
    signals = WorkerSignals()

    def __init__(self):
        super().__init__()
        self.is_killed = False

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

    @pyqtSlot()
    def run(self):
        try:
            self.total_files = countTotalFiles(self.folders_to_index)
            for folder in self.folders_to_index:
                self.folder_id = self.folderId(folder)
                if self.remove_indexed:
                    self.removeFilesBeforeReindex(self.folder_id)
                self.setStatusFolder(folder, 0)
                self.signals.status_folder_changed.emit()
                self._index(folder)
                self.setStatusFolder(folder, 1)
                self.signals.status_folder_changed.emit()
            self.finishThread()
        except WorkerKilledException:
            pass

    def _index(self, path):
        if self.is_killed:
            self.finishThread()
            raise WorkerKilledException

        """recursive method for indexing files"""
        # switch to new directory (root or recursive)
        directory = QtCore.QDir(path)
        directory.setFilter(directory.filter() | QtCore.QDir.NoDotAndDotDot | QtCore.QDir.NoSymLinks)
        self.signals.directory_changed.emit(path)
        for entry in directory.entryInfoList():
            if entry.isDir():
                if self.folderExists(entry.filePath()):
                    continue
                self._index(entry.filePath())

            if entry.isFile():
                self.checked_files += 1
                self.percentage = percentage(self.checked_files, self.total_files)

            # check if we have matched extension (zip / tar.gz) or there is no any extension to match
            file_ext = entry.suffix() or entry.completeSuffix()
            if file_ext in self.extensions.values() or self.extensions == {}:
                # no extensions selected and file hasn't extension
                extension_id = 0
                if file_ext:
                    extension_id = self.extensionId(file_ext)
                item = {'dir': path, 'filename': entry.fileName(), 'size': entry.size(),
                        'extension_id': extension_id, 'folder_id': self.folder_id}
                self.signals.match_found.emit()

                # insert file in database
                self.addFile(item)

    def finishThread(self):
        self.con.close()
        self.signals.finished.emit()

    def kill(self):
        self.is_killed = True

    def getExtensionsList(self):
        extensions = {}
        all_extensions = GDBModule.getAll('extensions')
        for ext in all_extensions:
            extensions[ext['id']] = ext['extension']
        return extensions

    def setExtensions(self, extensions):
        self.extensions = extensions

    def setStatusFolder(self, path, status):
        query = QtSql.QSqlQuery(self.con)
        query.prepare("UPDATE folders SET status=:status WHERE path=:path")
        query.bindValue(':path', path)
        query.bindValue(':status', int(status))
        if query.exec():
            query.clear()
        return True

    def removeFilesBeforeReindex(self, folder_id):
        """ before reindex a folder, remove old indexed files from that folder
        to prevent duplication
        """
        query = QtSql.QSqlQuery(self.con)
        query.prepare("""Delete from files where folder_id=:folder_id""")
        query.bindValue(':folder_id', folder_id)
        if not query.exec():
            GDBModule.printQueryErr(query, 'removeFilesBeforeReindex')

    def extensionId(self, extension):
        for key, value in self.extensions.items():
            if extension == value:
                return key

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

    def folderExists(self, folder: str) -> bool:
        """
        :param folder:
        :return:
        check if a folder exists
        """
        query = QtSql.QSqlQuery(self.con)
        query.prepare("SELECT path FROM folders where path=:path limit 1")
        query.bindValue(':path', folder)
        ret = query.exec() and query.first()
        query.clear()
        return ret