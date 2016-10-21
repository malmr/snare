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

import numpy as np
from AnalyzeTools.Calculation import Calculation


class CalculationExample(Calculation):

    """
    CalculationExample contains an example on how to use the AnalyzeWidgets for signal processing.
    It just plots the current selection with the correct axis.

    variables
    self.values:    To store the yAxis values.
    self.xAxis:     To store the xAxis values.
    """

    def __init__(self, snare, buffer, calib, timeWeight, fqWeight):
        super().__init__(snare, calib, timeWeight, fqWeight)
        # instance variables
        self.values = buffer
        self.xAxis = None

        # frequency-weighting
        self.values = self.fqWeighting(self.values, self.fqWeight)

        self.calculate()

    def calculate(self):
        """
        Calculates the Sound Pressure Level.
        Depending on calibration either in dBFS Peakvalue or in dbSPL values. For further information on the
        calibration implementation have a look at AnalyzeBuffer, 'calib' is only used to choose the right
        dBFS/dBSPL Scale.
        """
        sampleLen = len(self.values)

        # result
        self.values = self.values   # do nothing
        self.xAxis = np.linspace(0, sampleLen / self.snare.sampleRate, self.values.size)
