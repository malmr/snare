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

from PyQt5.QtCore import *


class Calibrations(QObject):

    """
    Analysis in SNARE either use dBFs or the user selects an area in the recording/file that contains a 94dB/1kHz
    calibration tone. That way an analysis can be calibrated.
    """

    calibrationChanged = pyqtSignal(int)

    def __init__(self):
        """
        Only creates a dict for storing calibration factors. A channel object shall be used as key for the dictionary.
        """
        super(Calibrations, self).__init__()
        self.factors = dict()

    def addCalibration(self, channel, factor):
        """
        Adds a calibration to the dictionary.

        :param channel: The channel object the calibration refers to.
        :param factor: The calibration factor.
        """
        try:
            if not factor == self.factors[channel]:
                self.calibrationChanged.emit(channel)
        except KeyError:
            self.calibrationChanged.emit(channel)
        self.factors[channel] = factor

    def getCalibration(self, channel):
        """
        Returns the calibration for the given channel or one if there is no calibration.

        :param channel: The channel object the calibration refers to.
        """
        factor = None
        try:
            factor = self.factors[channel]
        except KeyError:
            factor = 1
        return factor