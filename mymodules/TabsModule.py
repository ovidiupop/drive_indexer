from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import QTabWidget

from gallery import tabIndexByName
from mymodules import GDBModule as gdb, WorkerModule as wk
from mymodules.CategoriesModule import Categories
from mymodules.DrivesModule import DrivesView
from mymodules.ExtensionsModule import Extensions
from mymodules.FoldersModule import Folders
from mymodules.ModelsModule import ExtensionsModel
from mymodules.SearchModule import Search


class TabsWidget(QtWidgets.QWidget):

    reindex_folder = QtCore.pyqtSignal(object)

    def __init__(self, parent):
        super(TabsWidget, self).__init__(parent)
        self.indexer_thread = None
        self.indexer = None

        # importing Categories Module
        self.categories = Categories()
        # importing Drives Module
        self.drives = DrivesView()
        # import Search Module
        self.search = Search()
        # import Extensions Module
        self.extensions = Extensions()
        # import Folders Module
        self.folders = Folders()

        self.setDefaultActions()

        self.tab_search_group = QtWidgets.QGroupBox()
        self.tab_settings_group = QtWidgets.QGroupBox()

        self.tabs_main = QTabWidget()
        self.tabs_main.addTab(self.tab_search_group, 'Search')
        self.tabs_main.addTab(self.tab_settings_group, 'Settings')
        self.tabs_main.setMovable(True)

        self.tab_categories_group = QtWidgets.QGroupBox('Preferred categories for search')
        self.tab_folders_group = QtWidgets.QGroupBox('Folders')
        self.tab_extensions_group = QtWidgets.QGroupBox('Extensions')
        self.tab_drives_group = QtWidgets.QGroupBox('Drives')

        # tabs inside Settings tab
        self.tabs_settings = QTabWidget()
        self.tabs_settings.setTabPosition(QTabWidget.West)
        self.tabs_settings.setTabShape(QTabWidget.Rounded)
        self.tabs_settings.setMovable(True)
        self.tabs_settings.addTab(self.tab_categories_group, 'Categories')
        self.tabs_settings.addTab(self.tab_folders_group, 'Folders')
        self.tabs_settings.addTab(self.tab_extensions_group, 'Extensions')
        self.tabs_settings.addTab(self.tab_drives_group, 'Drives')

        self.setProgressBarToStatusBar()
        self.fillExtensions()
        self.preselectFavoriteExtensions()

    def setDefaultActions(self):
        self.folders.folder_reindex_button.clicked.connect(self.startThreadIndexer)
        # signals actions
        self.folders.folder_added.connect(self.startThreadIndexer)
        self.extensions.extension_added.connect(self.startThreadIndexer)
        self.extensions.reindex_for_new_extension.connect(self.reindexForNewExtension)
        self.extensions.preselect_favorite_extensions.connect(lambda: self.preselectFavoriteExtensions())
        self.extensions.update_view_extensions.connect(self.updateViewExtensions)

    @QtCore.pyqtSlot()
    def fillExtensions(self):
        extensions_list = [self.extensions.settings_extensions_list]
        extensions_db = gdb.getAll('extensions')
        for ext_list in extensions_list:
            ext_list.setSelectionMode(QtWidgets.QListView.ExtendedSelection)
            ext_list.setModel(ExtensionsModel(extensions_db))

    def updateViewExtensions(self):
        all_extensions = gdb.getAll('extensions')
        extensions_model = ExtensionsModel(all_extensions)
        self.search.extensions_list_search.setModel(extensions_model)
        self.extensions.settings_extensions_list.setModel(extensions_model)
        self.preselectFavoriteExtensions()

    @QtCore.pyqtSlot()
    def onFinished(self):
        """ End of thread """
        # re-enable buttons
        self.setStatusButtons(True)
        self.setStatusBar(f'Indexed {self.indexer.found_files} files')
        # sometimes the percent is not 100 at the end
        # set manually to fill the bar
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
                  self.extensions.set_preferred_extension_button,
                  self.extensions.add_extension_input
                  ]
        for my_input in inputs:
            my_input.setEnabled(status)

    @QtCore.pyqtSlot()
    def reindexForNewExtension(self):
        self.folders.unselectFolderSources()
        tab_folder_index = tabIndexByName(self.tabs_settings, 'Folders')
        self.tabs_settings.setCurrentIndex(tab_folder_index)
        self.extensions.extension_added.emit()

    # here we create the thread
    # after create the long time method
    def startThreadIndexer(self):
        self.folders.results_progress_group.show()
        self.folders.close_indexed_results_button.hide()
        self.setStatusButtons(False)
        self.indexer = wk.Indexer()
        # indexing for new extension
        if self.extensions.last_added_extension:
            self.indexer.remove_indexed = False
            self.indexer.setExtensions([self.extensions.last_added_extension])

        selected = self.folders.folders_indexed.selectedIndexes()
        if selected:
            folders = []
            for folder in selected:
                folders.append(folder.data())
            self.indexer.folders_to_index = folders
        else:
            self.indexer.folders_to_index = gdb.allFolders()
        self.indexer.found_files = 0
        self.indexer_thread = QtCore.QThread()
        self.indexer.moveToThread(self.indexer_thread)
        self.indexer.finished.connect(self.onFinished)
        self.indexer.finished.connect(self.indexer_thread.quit)
        self.indexer_thread.start()
        self.indexer.directory_changed.connect(self.onDirectoryChanged)
        self.indexer.match_found.connect(self.onMatchFound)
        self.reindex_folder.connect(self.indexer.doIndex)
        self.reindex_folder.connect(self.indexer_thread.start)
        self.reindex_folder.emit(self.indexer)

    @QtCore.pyqtSlot()
    def onMatchFound(self):
        self.indexer.found_files += 1
        self.folders.total_folders_indexed_label.setText(f'Found: {self.indexer.found_files} files')
        self.folders.indexing_progress_bar.setValue(self.indexer.percentage)

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

    def preselectFavoriteExtensions(self):
        ext_lists = [self.extensions.settings_extensions_list]
        extensions_db = gdb.getAll('extensions')
        selected_extensions = gdb.preselectedExtensions()
        self.entry = QtGui.QStandardItemModel()
        for alist in ext_lists:
            for idx, ex in enumerate(extensions_db):
                extension = ex['extension']
                ext = QtGui.QStandardItem(extension)
                self.entry.appendRow(ext)
                # select preselected items
                if extension in selected_extensions:
                    ix = self.entry.index(idx, 0)
                    sm = alist.selectionModel()
                    sm.select(ix, QtCore.QItemSelectionModel.Select)


class TabsView(TabsWidget):
    def __init__(self, parent):
        super(TabsView, self).__init__(parent)

        layout_tab_categories = self.categories.layout_tab_categories
        self.tab_categories_group.setLayout(layout_tab_categories)

        layout_tab_drives = self.drives.layout_tab_drives
        self.tab_drives_group.setLayout(layout_tab_drives)

        # final layout for search tab
        layout_tab_search = self.search.search_tab_layout
        self.tab_search_group.setLayout(layout_tab_search)

        layout_tab_extensions = self.extensions.layout_tab_extensions
        self.tab_extensions_group.setLayout(layout_tab_extensions)

        folders_section_layout = self.folders.folders_section_layout
        self.tab_folders_group.setLayout(folders_section_layout)

        settings_tab_layout = QtWidgets.QVBoxLayout()
        settings_tab_layout.addWidget(self.tabs_settings)
        settings_tab_layout.addStretch()
        self.tab_settings_group.setLayout(settings_tab_layout)


