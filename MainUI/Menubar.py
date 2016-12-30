# This file is part of SNARE.
# Copyright (C) 2016  Philipp Merz and Malte Merdes
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from PyQt5.Qt import *


class Menubar(QMenuBar):

    """
    This class creates the menubar displayed on top of SNARE's main window.
    """

    openWave = pyqtSignal()
    startRecord = pyqtSignal()
    pauseRecord = pyqtSignal()
    stopRecord = pyqtSignal()
    configRecord = pyqtSignal()
    selectAllReports = pyqtSignal()
    deselectAllReports = pyqtSignal()
    exportReport = pyqtSignal()
    newSelection = pyqtSignal()
    changeViewTab = pyqtSignal()
    changeViewNested = pyqtSignal()
    aboutDialog = pyqtSignal()
    helpDialog = pyqtSignal()


    def __init__(self):
        """
        Creates a number of menu items sorted in submenus. See the Qt documentation on QMenuBar for further reference.
        All events triggered here are relayed to the main window.
        """
        super(Menubar, self).__init__()

        self.actionFileOpen = QAction(self.tr(u"Open WAV..."), self)
        self.actionFileOpen.triggered.connect(self.openWave)
        self.actionFileOpen.setShortcut(self.tr("Ctrl+O"))

        self.actionRecordingInput = QAction(self.tr(u"Select Input..."), self)
        self.actionRecordingInput.triggered.connect(self.configRecord)
        self.actionRecordingInput.setShortcut(self.tr("Ctrl+I"))
        self.actionRecordingStart = QAction(self.tr(u"Record"), self)
        self.actionRecordingStart.triggered.connect(self.startRecord)
        self.actionRecordingStart.setShortcut(self.tr("Ctrl+R"))
        self.actionRecordingPause = QAction(self.tr(u"Pause"), self)
        self.actionRecordingPause.triggered.connect(self.pauseRecord)
        self.actionRecordingPause.setShortcut(self.tr("Ctrl+P"))
        self.actionRecordingStop = QAction(self.tr(u"Stop"), self)
        self.actionRecordingStop.triggered.connect(self.stopRecord)
        self.actionRecordingStop.setShortcut(self.tr("Ctrl+S"))

        self.actionEditorNewSelection = QAction(self.tr(u"Add new Selection"), self)
        self.actionEditorNewSelection.triggered.connect(self.newSelection)

        self.actionReportSelectAll = QAction(self.tr(u"Select all"), self)
        self.actionReportSelectAll.triggered.connect(self.selectAllReports)
        self.actionReportSelectAll.setShortcut(self.tr("Ctrl+A"))
        self.actionReportDeselectAll = QAction(self.tr(u"Deselect all"), self)
        self.actionReportDeselectAll.triggered.connect(self.deselectAllReports)
        self.actionReportExport = QAction(self.tr(u"Export..."), self)
        self.actionReportExport.setShortcut(self.tr("Ctrl+E"))
        self.actionReportExport.triggered.connect(self.exportReport)

        self.actionViewsTab = QAction(self.tr(u"Tab View"), self)
        self.actionViewsTab.setShortcut(self.tr("Ctrl+T"))
        self.actionViewsTab.triggered.connect(self.changeViewTab)
        self.actionViewsNested = QAction(self.tr(u"Nested View"), self)
        self.actionViewsNested.setShortcut(self.tr("Ctrl+N"))
        self.actionViewsNested.triggered.connect(self.changeViewNested)

        self.actionDocumentation = QAction(self.tr(u"QuickGuide and documentation"),self)
        self.actionDocumentation.setShortcut(self.tr("Ctrl+H"))
        self.actionDocumentation.triggered.connect(self.helpDialog)

        self.actionAbout = QAction(self.tr(u"About..."), self)
        self.actionAbout.triggered.connect(self.aboutDialog)


        menuFile = self.addMenu(self.tr("&File"))
        menuFile.addAction(self.actionFileOpen)

        menuRecording = self.addMenu(self.tr("&Recording"))
        menuRecording.addAction(self.actionRecordingInput)
        menuRecording.addSeparator()
        menuRecording.addAction(self.actionRecordingStart)
        menuRecording.addAction(self.actionRecordingPause)
        menuRecording.addAction(self.actionRecordingStop)

        menuEditor = self.addMenu(self.tr("&Editor"))
        menuEditor.addAction(self.actionEditorNewSelection)

        menuReport = self.addMenu(self.tr("&Report"))
        menuReport.addAction(self.actionReportSelectAll)
        menuReport.addAction(self.actionReportDeselectAll)
        menuReport.addSeparator()
        menuReport.addAction(self.actionReportExport)

        menuViews = self.addMenu(self.tr("&Views"))
        menuViews.addAction(self.actionViewsTab)
        menuViews.addAction(self.actionViewsNested)

        menuHelp = self.addMenu(self.tr("&Help"))
        menuHelp.addAction(self.actionAbout)
        menuHelp.addAction(self.actionDocumentation)
        menuHelp.addSeparator()
