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


class Statusbar(QStatusBar):

    """
    A status bar displayed at the bottom of SNARE's main window.
    """

    def __init__(self):
        """
        Creating spaces for all status messages.
        """
        super(Statusbar, self).__init__()

        self.defaultMsg = QLabel("Status:")
        self.insertPermanentWidget(0, self.defaultMsg)

        self.waveformMsg = QLabel("Rendering 0 Waveforms.")
        self.insertPermanentWidget(1, self.waveformMsg)

        self.recordingMsg = QLabel("Recording not configured.")
        self.insertPermanentWidget(2, self.recordingMsg)

        self.widgetsMsg = QLabel("0 Widgets imported. 0 Analyses active.")
        self.insertPermanentWidget(3, self.widgetsMsg)

    def updateWaveformMessage(self, quelength):
        """
        Interface for the render thread workload message.

        :param quelength: Current workload measured in pixmaps to render
        """
        self.waveformMsg.setText("Rendering " + str(quelength) + " Waveforms.")
        self.waveformMsg.update()

    def updateRecordingStatus(self, str):
        """
        Interface for the recording status message.

        :param str: E.g. "Ready for Recording"
        """
        self.recordingMsg.setText(str)
        self.recordingMsg.update()

    def updateAnalysesStatus(self, cntwidgets):
        """
        Inteface for the analysis status message.

        :param cntwidgets: Takes a fully formatted message.
        """
        self.widgetsMsg.setText(str(cntwidgets))
        self.widgetsMsg.update()
