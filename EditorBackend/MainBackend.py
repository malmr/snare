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

import os
import pyaudio
from PyQt5.Qt import *

from EditorBackend.Calibrations import Calibrations
from EditorBackend.Buffer import Buffer
from EditorUI.TrackManager import TrackManager
from EditorUI.TrackAbstract import TrackAbstract
from EditorBackend.WaveformBuffer import WaveformBuffer
from EditorBackend.Audioplayer import Audioplayer
from EditorBackend.Recorder import Recorder
from EditorBackend.AnalyzeBuffer import AnalyzeBuffer
from AnalyzeTools.AnalyzeManager import AnalyzeManager
from AnalyzeTools.AnalyzeWidget import AnalyzeWidget
from AnalyzeTools.AnalyzeWidgetSelect import AnalyzeWidgetSelect
from AnalyzeTools.CalibrationWidget import CalibrationWidget
from Reports.ReportManager import ReportManager

from EditorUI.TrackUI import TrackUI


class MainBackend(QObject):

    """
    The main backend presents the collection of backend-objects, e.g. the main audio-data buffer, the recorder,
    audioplayer, the waveformbuffer et al. Those objects communicate with each other through the MainBackend.
    """

    updateWaveformMessage = pyqtSignal(int)
    updateRecordingStatus = pyqtSignal(str)
    updateAnalysesStatus = pyqtSignal(str)
    addTrack = pyqtSignal(TrackAbstract)
    addAnalysis = pyqtSignal(AnalyzeWidget)
    removeTrack = pyqtSignal(TrackUI)

    def __init__(self, sampleRate, sampleWidth):
        """
        Creates the backend objects in a specific order and makes signal/slot connections where necessary. For a
        complete overview of the object interaction see the overall documentation of SNARE.

        :param sampleRate: The sample rate to be set once on startup.
        :param sampleWidth: The sample width to be set once on startup.
        """
        super(MainBackend, self).__init__()

        self.sampleRate = sampleRate
        self.sampleWidth = sampleWidth

        self.blockSize = self.sampleRate*10
        self.waveformHeight = 100
        # Construct Backend
        self.channels = list()

        self.buffer = Buffer(self.sampleRate, self.sampleWidth, self.blockSize)

        self.calibrations = Calibrations()
        self.analyzeBuffer = AnalyzeBuffer(self.buffer, self.calibrations, self.sampleRate)
        self.analyzeBuffer.newSelection.connect(self.newAnalysis)
        self.analyzeBuffer.selectionChanged.connect(self.updateAnalysis)

        self.waveformBuffer = WaveformBuffer(self.buffer, self.sampleWidth, self.blockSize, self.waveformHeight)
        self.waveformBuffer.updateWaveformMessage.connect(self.updateWaveformMessage)

        self.audioplayer = Audioplayer(self.buffer, self.sampleRate, self.sampleWidth, self.blockSize)

        self.recorder = Recorder(self.buffer, self.sampleRate, self.sampleWidth, self.blockSize)
        self.recorder.updateRecording.connect(self.updateRecordingStatus)

        self.analyzeWidgetDirs = None

        # To change between dynamic and static import:
        # (un-)comment this block and the block in AnalyzeManager.
        #
        # <-- dynamic import
        # self.analyzeWidgetDirs = next(os.walk(os.getcwd()+'/AnalyzeTools'))[1]
        # self.analyzeWidgetDirs = list(filter(lambda x: x.startswith('Widget'), self.analyzeWidgetDirs))
        # self.analyzeWidgetDirs = ['AnalyzeTools/' + s for s in self.analyzeWidgetDirs]
        # dynamic import -->

        self.analyses = AnalyzeManager(self, self.analyzeWidgetDirs)

        self.reports = ReportManager(self)

        self.tracks = TrackManager(self.analyses, self.blockSize)

        self.tracks.addTrack.connect(self.addTrack)
        self.waveformBuffer.returnWaveform.connect(self.tracks.slo_addWaveform)
        self.tracks.getWaveform.connect(self.waveformBuffer.getWaveform)
        self.tracks.deleteChannel.connect(self.deleteChannel)

        self.tracks.setPlayerPosition.connect(self.audioplayer.setPos)
        self.tracks.playerPlay.connect(self.audioplayer.play)
        self.tracks.playerPause.connect(self.audioplayer.pause)
        self.audioplayer.sendPos.connect(self.tracks.updateSmp)
        self.recorder.sendRecPos.connect(self.tracks.updateFromRecorder)

        self.tracks.addSelection.connect(self.analyzeBuffer.addSelection)

    def exportReport(self):
        """
        Relay to ReportManager.
        """
        self.reports.createReport()

    def selectAllReports(self):
        """
        Relay to ReportManager.
        """
        self.reports.selectAll()

    def deselectAllReports(self):
        """
        Relay to ReportManager
        """
        self.reports.deselectAll()

    def newAnalysis(self, channel, selNo, type='FFT'):
        """
        Adds a new analysis or calibration.

        :param channel: Channel object the analysis refers to.
        :param selNo: Name of the selection.
        :param type: Analysis type of the selection.
        """
        print('Analyze Channel unknown', 'SelNo', selNo, 'Analyzetype', type)
        if selNo == "Calib.":
            self.addCalibration(channel, selNo)
        else:
            analysis = AnalyzeWidgetSelect(self, channel, selNo, type)
            self.addAnalysis.emit(analysis)
            self.analyses.addWidget(analysis, channel, selNo)  # add to Analyses Mapping

    def addCalibration(self, channel, selNo):
        """
        Adds (or updates) a calibration for

        :param channel: Channel object the analysis refers to.
        :param selNo: Name of the selection, that contains the calibration selection.
        """
        self.cali = CalibrationWidget(self, channel, selNo).calculate()
        print('Calibrationfactor: ', self.cali)

    def updateAnalysis(self, channel, selNo, type):
        """
        Updates an existing analysis.

        :param channel: Channel object the analysis refers to.
        :param selNo: Name of the selection.
        :param type: Analysis type of the selection.
        """
        print("Updating")
        if selNo == "Calib.":
            self.addCalibration(channel, selNo)

    # Provide full interface to TrackManager and MainWindow
    def newSelection(self):
        """
        Adds a new selection on the TrackManager.
        """
        self.tracks.newSelection()

    def openWave(self, fileName):
        """
        After the user selected a valid WAVE-file in the file dialog. Adds a track for every channel of the WAVE-file.
        :param fileName: Full path to file.
        """
        newChannels = self.buffer.loadWave(fileName)
        self.channels.append(newChannels)

        for channel in newChannels:
            self.waveformBuffer.addChannel(channel)
            self.tracks.addChannel(channel)

    def startRecord(self):
        """
        Notifies all relevant objects about starting a recortding.
        """
        self.tracks.setRecording(True)
        self.recorder.record()

    def pauseRecord(self):
        """
        Notifies all relevant objects about pausing the recording.
        """
        self.recorder.pause()

    def stopRecord(self):
        """
        Notifies all relevant objects about closing the recording.
        """
        self.tracks.setRecording(False)
        self.buffer.closeRecording()
        self.recorder.stop()

    def configRecord(self, device, channels):
        """
        After InputSelectorDialog configured a recording. When configured it will add channel objects and tracks
        accordingly.

        :param device: Audio device to record from.
        :param channels: Channels to record from that device.
        """
        self.recorder.open(device)

        p = pyaudio.PyAudio()
        name = p.get_device_info_by_index(device)['name']

        recordingChannels = self.buffer.addRecording(channels, name)

        for channel in recordingChannels:
            self.waveformBuffer.addChannel(recordingChannels[channel])
            self.tracks.addChannel(recordingChannels[channel])

    def deleteChannel(self, channel, track):
        """
        Delete a channel. Since the signal comes from TrackManager, the UI part of the channel has already been deleted.

        :param channel: Delete data associated with this channel objects.
        :param track: Track QWidget to delete from MainWindow.
        :type track: EditorUI.TrackUI
        """
        self.waveformBuffer.deleteChannel(channel)
        self.buffer.deleteChannel(channel)
        self.removeTrack.emit(track)

    def exportReport(self):
        self.reports.createReport()

    def selectAllReports(self):
        self.reports.selectAll()

    def deselectAllReports(self):
        self.reports.deselectAll()