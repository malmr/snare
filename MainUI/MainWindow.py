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

from MainUI.Menubar import Menubar
from MainUI.Statusbar import Statusbar

from MainUI.SubWindow import SubWindowDock
from MainUI.InputSelectorDialog import InputSelectorDialog


class MainWindow(QMainWindow):

    """
    The MainWindow class combines the menubar and statusbar with the analysis and editor dockwidget to create the main
    window of the SNARE application. The analysis and editor widgets communicate mostly directly with the backend, for
    all other user interface elements, this class provides the interface to the backend. E.g. all input on the menubar
    and all output on the statusbar.
    """

    # Signals from menubar
    newSelection = pyqtSignal()
    openWave = pyqtSignal(str)
    startRecord = pyqtSignal()
    pauseRecord = pyqtSignal()
    stopRecord = pyqtSignal()
    configRecord = pyqtSignal(int, list)
    exportReport = pyqtSignal()
    selectAllReports = pyqtSignal()
    deselectAllReports = pyqtSignal()
    changeViewTab = pyqtSignal()
    changeViewNested = pyqtSignal()

    def __init__(self):

        """
        Manually creates the four UI-Elements and relays the signals coming from the menubar.
        """
        super(MainWindow, self).__init__()

        self.menubar = Menubar()
        self.menubar.newSelection.connect(self.newSelection)
        self.menubar.openWave.connect(self.__openWave__)
        self.menubar.configRecord.connect(self.configRecordWindow)
        self.menubar.startRecord.connect(self.startRecord)
        self.menubar.pauseRecord.connect(self.pauseRecord)
        self.menubar.stopRecord.connect(self.stopRecord)
        self.menubar.newSelection.connect(self.newSelection)
        self.menubar.exportReport.connect(self.exportReport)
        self.menubar.selectAllReports.connect(self.selectAllReports)
        self.menubar.deselectAllReports.connect(self.deselectAllReports)
        self.menubar.changeViewTab.connect(self.changeViewTab)
        self.menubar.changeViewTab.connect(self.tabView)
        self.menubar.changeViewNested.connect(self.changeViewTab)
        self.menubar.changeViewNested.connect(self.nestedView)

        self.statusbar = Statusbar()

        self.setMenuBar(self.menubar)
        self.setStatusBar(self.statusbar)

        self.editorWindowDock = SubWindowDock("Editor")
        self.addDockWidget(Qt.LeftDockWidgetArea, self.editorWindowDock)

        self.analyzeWindowDock = SubWindowDock("Analyzer")
        self.addDockWidget(Qt.LeftDockWidgetArea, self.analyzeWindowDock)

        self.setWindowTitle("SNARE - Sound Noise Analyser, Recorder and Editor")
        self.setGeometry(80, 80, 1400, 800)
        self.setAcceptDrops(True)
        self.show()

    def configRecordWindow(self):
        """
        Opens a dialog (InputSelectorDialog) for selecting an input device and channel. The results of the selection
        are then transmitted to the backend.
        """
        channellist = list()
        ex = InputSelectorDialog(channellist)
        if len(channellist) > 1:
            # Format: Last element is device-ID, indices before are selected channels
            deviceNumber = channellist[-1]
            deviceChannels = channellist[:-1]
            self.configRecord.emit(deviceNumber, deviceChannels)

    def __openWave__(self, files=False):
        """
        Opens a standard Qt file dialog for selecting an input files in case of menubar or uses the optional parameter
        files in case of Drag and Drop. The filenames are then transmitted to the backend in a loop.
        """
        if not files:
           files = QFileDialog.getOpenFileNames()
        if files[0]:
            for file in files[0]:
                self.openWave.emit(file)

    # Slots for adding and removing sub-widgets
    def addTrack(self, track):
        """
        Interface relay to add Track elements to the editor area.

        :param track: The TrackUI object to add.
        """
        self.editorWindowDock.addWidget(track)

    def removeTrack(self, track):
        """
        Interface relay to remove a Track element from the editor area.

        :param track: Reference to the TrackUI object to remove.
        """
        self.editorWindowDock.removeWidget(track)

    def addAnalysis(self, analysis):
        """
        Interface relay to add an analysis widget to the analysis area.

        :param analysis: The AnalysisWidget to add.
        """
        self.analyzeWindowDock.addWidget(analysis)

    def removeAnalysis(self, analysis):
        """
        Interface relay to remove an analysis widget from the analysis area.

        :param analysis: Reference to the AnalysisWidget to remove.
        """
        self.analyzeWindowDock.removeWidget(analysis)

    # Slots for statusbar
    def updateRecordingStatus(self, text):
        """
        Relay message to the status bar.

        :param text: String containing a recording status message.
        """
        self.statusbar.updateRecordingStatus(text)

    def updateWaveformMessage(self, quelength):
        """
        Relay message to the status bar.

        :param quelength: Integer containing the current workload of the render threads.
        """
        self.statusbar.updateWaveformMessage(quelength)

    def updateAnalysesStatus(self, text):
        """
        Relay message to the status bar.

        :param text: Integer containing the number of currently loaded widgets.
        """
        self.statusbar.updateAnalysesStatus(text)

    # Slots for views
    def tabView(self):
        """
        Slot to switch the main window view to a tabbed style.
        """
        self.tabifyDockWidget(self.editorWindowDock, self.analyzeWindowDock)
        self.editorWindowDock.raise_()
        self.editorWindowDock.activateWindow()

    def nestedView(self):
        """
        Slot to switch the main window view to a nested style. (Windows side by side)
        """
        self.addDockWidget(Qt.LeftDockWidgetArea, self.editorWindowDock)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.analyzeWindowDock)

    # Drag and Drop support
    def dragEnterEvent(self, event):
        """
        Overwrites DragEnterEvent for Drag and Drop file support.
        """
        if event.mimeData().hasUrls:
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        """
        Overwrites DragMoveEvent for Drag and Drop file support.
        """
        if event.mimeData().hasUrls:
            event.setDropAction(Qt.CopyAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        """
        Overwrites DropEvent for Drag and Drop file support. Before passing to __openWave__, fileNames is casted to the
        needed format.
        """
        if event.mimeData().hasUrls:
            event.setDropAction(Qt.CopyAction)
            event.accept()
            files = []
            for url in event.mimeData().urls():
                files.append(str(url.toLocalFile()))
            files = tuple([files]) + tuple([''])
            self.__openWave__(files)
        else:
            event.ignore()
