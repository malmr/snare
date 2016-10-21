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

from collections import defaultdict

from PyQt5.QtCore import *

import numpy as np

from EditorBackend.Channel import Channel


class AnalyzeBuffer(QObject):

    """
    When the user requests an analysis, all selected areas are composed to one NumPy array and stored here before
    an analysis widget picks it up. Also the calibration is added here.
    """

    selectionChanged = pyqtSignal(Channel, str, str)
    newSelection = pyqtSignal(Channel, str, str)

    def __init__(self, buffer, calibrations):
        """
        Initialise 2D dictionaries to store selections and meta information in. Also link with Buffer as data source
        and the calibration buffer.

        :param buffer: A Buffer object, main data source.
        :param calibrations: The CalibrationBuffer.
        """
        super(AnalyzeBuffer, self).__init__()
        self.buffer = buffer
        self.calibrations = calibrations

        self.selectionExists = defaultdict(lambda: defaultdict(dict))
        self.selectionPoints = defaultdict(lambda: defaultdict(dict))
        self.selectionBuffers = defaultdict(lambda: defaultdict(dict))

    def deleteChannel(self, channel):
        """
        Delete a channel from this buffer. Donne with exceptions, because these data-points only exist if the analysis funnction has been used on this channel

        :param channel: The Channel to delete.
        """
        try:
            del self.selectionPoints[channel]
            del self.selectionExists[channel]
            del self.selectionBuffers[channel]
        except KeyError:
            pass

    def addSelection(self, channel, selNo, points, type):
        """
        Adds a selection to the AnalyzeBuffer.

        :param channel: A Channel object for reference.
        :param selNo: Name of the selection on that channel.
        :param points: List of start and end points, describing the selection areas.
        :param type: Type of analysis, e.g. "FFT"
        """
        self.selectionPoints[channel][selNo] = points
        self.selectionBuffers[channel][selNo] = self.buffer.getSelection(channel, points)
        print("Added a Selection")

        if self.selectionExists[channel][selNo] == True:
            self.selectionChanged.emit(channel, selNo, type)
        else:
            self.newSelection.emit(channel, selNo, type)
            self.selectionExists[channel][selNo] = True

    def getBuffer(self, channel, selNo):
        """
        This is the interface for analysis widgets to access data. Before handover it is converted to a float type to
        avoid precision loss and calibrated.

        :param channel: The requested Channel.
        :param selNo: Name of the selection requested.
        """
        buffer = np.array(self.selectionBuffers[channel][selNo])
        buffer = buffer.astype(np.float64)
        buffer = self.calibrations.getCalibration(channel) * buffer
        return buffer
