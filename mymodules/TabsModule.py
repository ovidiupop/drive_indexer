import sys

from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtCore import QThreadPool
from PyQt5.QtWidgets import QTabWidget

from mymodules import GDBModule as gdb
from mymodules.CategoriesModule import Categories
from mymodules.DevicesMonitorModule import Monitoring, DeviceJobRunner, Devices
from mymodules.DrivesModule import DrivesView
from mymodules.ExtensionsModule import Extensions
from mymodules.FoldersModule import Folders
from mymodules.GlobalFunctions import setStatusBarMW
from mymodules.IndexerModule import JobRunner
from mymodules.PreferencesModule import Preferences
from mymodules.SearchModule import Search
from mymodules.SystemModule import folderCanBeIndexed, isEmptyFolder


class TabsWidget(QtWidgets.QWidget):
    reindex_folder = QtCore.pyqtSignal(object)
    kill_device_monitor_runner = QtCore.pyqtSignal()

    def __init__(self, parent):
        super(TabsWidget, self).__init__(parent)
        self.indexer_thread = None
        self.indexer = None
        self.monitoring = None

        # importing Categories Module
        self.categories = Categories()
        # importing Drives Module
        self.drives = DrivesView()
        # import Search Module
        self.search = Search(self)
        # import Extensions Module
        self.extensions = Extensions()
        # import Folders Module
        self.folders = Folders()
        # import Preferences Module
        self.preferences = Preferences()
        self.setDefaultActions()

        self.tab_search_group = QtWidgets.QGroupBox()
        self.tab_settings_group = QtWidgets.QGroupBox()

        self.tabs_main = QTabWidget()
        self.tabs_main.addTab(self.tab_search_group, QtGui.QIcon(':magnifier.png'), 'Search')
        self.tabs_main.addTab(self.tab_settings_group, QtGui.QIcon(':setting_tools.png'), 'Settings')
        self.tabs_main.setMovable(True)

        self.tab_categories_group = QtWidgets.QGroupBox('Preferred categories for search')
        self.tab_folders_group = QtWidgets.QGroupBox('Folders')
        self.tab_extensions_group = QtWidgets.QGroupBox('Extensions')
        self.tab_drives_group = QtWidgets.QGroupBox('Drives')
        self.tab_preferences_group = QtWidgets.QGroupBox('Preferences')

        # tabs inside Settings tab
        self.tabs_settings = QTabWidget()
        self.tabs_settings.setTabPosition(QTabWidget.West)
        self.tabs_settings.setTabShape(QTabWidget.Rounded)
        self.tabs_settings.setMovable(True)

        self.tabs_settings.addTab(self.tab_folders_group, QtGui.QIcon(':folder.png'), 'Folders')
        self.tabs_settings.addTab(self.tab_drives_group, QtGui.QIcon(':drive.png'), 'Drives')
        self.tabs_settings.addTab(self.tab_categories_group, QtGui.QIcon(':accordion.png'), 'Categories')
        self.tabs_settings.addTab(self.tab_extensions_group, QtGui.QIcon(':file_extension_exe.png'), 'Extensions')
        self.tabs_settings.addTab(self.tab_preferences_group, QtGui.QIcon(':preferences.png'), 'Preferences')

        layout_tab_categories = self.categories.layout_tab_categories
        self.tab_categories_group.setLayout(layout_tab_categories)
        self.tab_categories_group.setMaximumHeight(200)

        layout_tab_drives = self.drives.layout_tab_drives
        self.tab_drives_group.setLayout(layout_tab_drives)

        # final layout for search tab
        layout_tab_search = self.search.search_tab_layout
        self.tab_search_group.setLayout(layout_tab_search)

        layout_tab_extensions = self.extensions.layout_tab_extensions
        self.tab_extensions_group.setLayout(layout_tab_extensions)

        preferences_section_layout = self.preferences.layout_tab_preferences
        self.tab_preferences_group.setLayout(preferences_section_layout)

        folders_section_layout = self.folders.folders_section_layout
        self.tab_folders_group.setLayout(folders_section_layout)

        settings_tab_layout = QtWidgets.QVBoxLayout()
        settings_tab_layout.addWidget(self.tabs_settings)
        self.tab_settings_group.setLayout(settings_tab_layout)

        self.setProgressBarToStatusBar()
        self.startThreadMonitoringDevices()
        self.parent().kill_device_monitor_runner.connect(lambda: self.killDeviceMonitorRunner())

    def killDeviceMonitorRunner(self):
        self.kill_device_monitor_runner.emit()

    def setDefaultActions(self):
        self.folders.folder_reindex_button.clicked.connect(self.startThreadIndexer)
        # signals actions
        self.folders.folder_added.connect(self.startThreadIndexer)
        self.extensions.extension_added.connect(self.startThreadIndexer)
        self.extensions.reindex_for_new_extension.connect(self.reindexForNewExtension)

    @QtCore.pyqtSlot()
    def onFinished(self):
        """ End of thread """
        # re-enable buttons
        self.setStatusButtons(True)
        self.folders.folder_stop_index_button.hide()
        self.setStatusBar(f'Indexed {self.runner.found_files} files')
        self.folders.indexing_progress_bar.setValue(100)
        self.toggleProgressVisibility(False)
        # show close button
        self.folders.close_indexed_results_button.show()
        if self.extensions.last_added_extension:
            self.extensions.last_added_extension = None

    def setStatusBar(self, text):
        self.parent().setStatusBar(text)

    def setProgressBarToStatusBar(self):
        self.parent().statusBar().addPermanentWidget(self.folders.indexing_progress_bar)

    # enable/disable buttons while indexing
    # TODO: queue for thread
    def setStatusButtons(self, status):
        inputs = [self.folders.folder_add_button,
                  self.folders.folder_remove_selected_button,
                  self.folders.folder_remove_all_button,
                  self.folders.folder_reindex_button,
                  self.extensions.add_extension_button,
                  self.extensions.remove_extension_button,
                  self.extensions.add_extension_input
                  ]
        for my_input in inputs:
            my_input.setEnabled(status)

    @QtCore.pyqtSlot()
    def reindexForNewExtension(self):
        self.folders.unselectFolderSources()
        self.extensions.extension_added.emit()

    # here we create the thread
    # after create the long time method
    def startThreadIndexer(self):
        if setStatusBarMW('Please wait while drive is initialized...'):
            self.folders.results_progress_group.show()
            self.folders.close_indexed_results_button.hide()
            self.setStatusButtons(False)
            self.folders.folder_stop_index_button.show()
            self.threadpool = QThreadPool()
            self.runner = JobRunner()
            # if indexing for new extension
            # preserve already indexed files
            if self.extensions.last_added_extension:
                self.runner.remove_indexed = False
                extension = self.extensions.last_added_extension
                ext_id = gdb.extensionId(extension)
                self.runner.setExtensions({ext_id: extension})
            self.setIndexableFolders()
            self.runner.found_files = 0
            self.runner.signals.finished.connect(self.onFinished)
            self.runner.signals.status_folder_changed.connect(self.folders.refreshTable)
            self.runner.signals.directory_changed.connect(self.onDirectoryChanged)
            self.runner.signals.match_found.connect(self.onMatchFound)
            self.threadpool.start(self.runner)
            self.folders.stop_indexer.connect(self.runner.kill)

    def setIndexableFolders(self):
        indexes = self.folders.folders_indexed_table.selectedIndexes()
        if indexes:
            folders = [self.folders.folders_indexed_table.model().data(index) for index in indexes if
                       index.column() == 1]
        else:
            folders = gdb.allFolders()
        non_indexable = []
        indexable_folders = []
        for folder in folders:
            can = folderCanBeIndexed(folder)
            is_indexable = can[0]
            is_not_empty = not isEmptyFolder(folder)
            if is_indexable and is_not_empty:
                if not isEmptyFolder(folder):
                    indexable_folders.append(folder)
            else:
                non_indexable.append(folder)
        self.runner.folders_to_index = indexable_folders
        if len(non_indexable):
            non = "<br>".join(non_indexable)
            QtWidgets.QMessageBox.critical(self,
                                           'Error!',
                                           f"Next folders are empty! Probably the source drive is not active!<br>"
                                           f"<br>{non}"
                                           f"<br><br>Please check!")

    @QtCore.pyqtSlot()
    def onMatchFound(self):
        self.runner.found_files += 1
        self.folders.total_folders_indexed_label.setText(f'Found: {self.runner.found_files} files')
        self.folders.indexing_progress_bar.setValue(self.runner.percentage)

    @QtCore.pyqtSlot(str)
    def onDirectoryChanged(self, path):
        """ New folder is indexing and its path is displayed"""
        self.folders.report_indexed_path_label.setText(f'Indexing: {path}')
        self.toggleProgressVisibility(True)
        self.setStatusBar(f'Indexing: {path}')

    def toggleProgressVisibility(self, visible):
        if visible:
            self.folders.indexing_progress_bar.setValue(0)
            self.folders.indexing_progress_bar.show()
        else:
            self.folders.indexing_progress_bar.hide()

    def startThreadMonitoringDevices(self):
        self.monitoring = Monitoring(self)
        self.monitoring.configuration_changed.connect(lambda: self.deviceListChanged())

    @QtCore.pyqtSlot()
    def deviceListChanged(self):
        self.drives.comboActiveDrives()
        self.drives.drives_table.setModel(self.drives.drives_table_model)
        self.drives.drives_table_model.select()
        self.folders.fillPreferredFolders()



