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

import sys
import os
from PyQt5.Qt import *

from MainUI.StartDialog import StartDialog
from MainUI.MainWindow import MainWindow
from EditorBackend.MainBackend import MainBackend

class Main:

    """
    This is the start point of the SNARE application
    """

    def __init__(self):
        """
        Firstly runs the start routine (StartDialog) and then creates the MainWindow and MainBackend and links the two.
        """

        app = QApplication(sys.argv)

        self.configuration = dict()
        icon = QIcon(self.resource_path("Icon.ico"))
        startDialog = StartDialog(self.configuration, icon)

        # Get information from StartDialog
        self.sampleRate = self.configuration["sampleRate"]
        self.sampleWidth = self.configuration["sampleWidth"]

        # Start MainUI here
        mainWindow = MainWindow()
        mainWindow.setWindowIcon(icon)
        # Initialize backend object here
        mainBackend = MainBackend(self.sampleRate, self.sampleWidth)
        mainWindow.openWave.connect(mainBackend.openWave)
        mainWindow.configRecord.connect(mainBackend.configRecord)
        mainBackend.updateWaveformMessage.connect(mainWindow.updateWaveformMessage)
        mainBackend.updateRecordingStatus.connect(mainWindow.updateRecordingStatus)
        mainBackend.updateAnalysesStatus.connect(mainWindow.updateAnalysesStatus)
        mainBackend.addTrack.connect(mainWindow.addTrack)
        mainBackend.addAnalysis.connect(mainWindow.addAnalysis)
        mainBackend.removeTrack.connect(mainWindow.removeTrack)
        mainBackend.analyses.removeAnalysis.connect(mainWindow.removeAnalysis)

        # Initialize Statusbar - ToDo Can't find better place for initialize
        mainBackend.updateAnalysesStatus.emit(mainBackend.analyses.getStatusBarString())

        # Connect Menubar Signals
        mainWindow.startRecord.connect(mainBackend.startRecord)
        mainWindow.pauseRecord.connect(mainBackend.pauseRecord)
        mainWindow.stopRecord.connect(mainBackend.stopRecord)

        mainWindow.newSelection.connect(mainBackend.newSelection)

        mainWindow.exportReport.connect(mainBackend.exportReport)
        mainWindow.selectAllReports.connect(mainBackend.selectAllReports)
        mainWindow.deselectAllReports.connect(mainBackend.deselectAllReports)

        # Add Wav files that were selected in th startup Dialog
        if self.configuration["allFilesValid"]:
            fileNames = self.configuration["fileNames"]
            for files in fileNames:
                mainBackend.openWave(files)
        else:
            mainWindow.configRecordWindow()

        sys.exit(app.exec_())

    def resource_path(self, relative_path):
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, relative_path)
        return os.path.join(os.path.abspath("."), relative_path)
