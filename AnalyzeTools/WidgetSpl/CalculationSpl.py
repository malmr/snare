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


class CalculationSpl(Calculation):
    """
    CalculationSpl includes the methods for the dBFS/dBSPL level signal processing calculation.
    """

    def __init__(self, snare, buffer, calib, timeWeight, fqWeight):
        """
        Initialize the variables, frequency-weight the values and start the calculation method.

        :param snare: Common used variables implenented in MainBackend.
        :type snare: object
        :param buffer: buffer array
        :type buffer: list
        :param calib: Is None if calibration is unset or the calibration value.
        :type calib: int
        :param timeWeight: Time weight slow, fast or impulse
        :type timeWeight: str
        :param fqWeight: Frequency weight A, B, C or Z
        :type fqWeight: str
         """
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
        Depending on calibration either in dBFS Peakvalues or in dbSPL values.
        seealso::For further information on the calibration implementation have a look at AnalyzeBuffer,
        'calib' is only used to choose the right dBFS/dBSPL Scale.

        Stores the result in self.values and self.xAxis.
        """
        sampleLen = len(self.values)
        self.values **= 2  # square pressure (positive values)
        # time-weighting
        self.values = self.timeWeighting(self.values, self.timeWeight)

        # result
        self.values = self.db(self.values, rms=False)   # convert to dB values
        print(self.snare.sampleRate)
        self.xAxis = np.linspace(0, self.values.size / self.snare.sampleRate, self.values.size)
