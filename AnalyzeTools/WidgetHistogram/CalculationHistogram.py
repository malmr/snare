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
import sys
from AnalyzeTools.Calculation import Calculation

class CalculationHistogram(Calculation):
    """
    CalculationHistogram includes the methods for the Histogram signal processing calculation.
    """

    def __init__(self, snare, buffer, calib, timeWeight, fqWeight, resolution):
        """
        Initialize the variables, frequency-weight the values and start the calculation method.

        :param snare: Common used variables implenented in MainBackend.
        :type snare: object
        :param buffer: Buffer array
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
        self.probDb = list()
        self.probSum = list()
        self.values = buffer
        self.xAxis = None
        self.resolution = resolution

        # frequency-weighting
        self.values = self.fqWeighting(self.values, self.fqWeight)

        self.calculate()

    def calculate(self):
        """
        Calculates the Histogram.
        The Histogram shows the probability of occurance for every 0.1 dB sound pressure level step. Beside the
        propability bar plot a rising cumultative sum is overlayed.

        Stores the result in self.probSum, self.probDb and self.xAxis.
        """

        # get dB values
        self.values **= 2  # square pressure (because energetic quantity needed)
        # time-weighting
        self.values = self.timeWeighting(self.values, self.timeWeight)
        # convert to dB values
        self.values = self.db(self.values, rms=False)

        self.values = np.array(self.values)

        # set values -inf to very low number 0, occours during frequency weighting:
        low_indices = np.isinf(self.values)
        self.values[low_indices] = sys.float_info.min

        self.values.sort()
        smpLen = len(self.values)

        # calculate range
        dbMin = self.values.min()
        dbMax = self.values.max()
        totalBars = int(np.ceil(np.abs(dbMax - dbMin) * self.resolution) + 1)   # rounded up

        # padding sorted array (because db range 'totalBars' is rounded up (max. variance of 1 dB = 10 smps))
        self.values = list(self.values)
        self.values.extend([1])

        smp = 0
        for bar in range(totalBars):
            # bar sum loop
            bar_smps = 0
            while (self.values[smp] < (dbMin + (bar + 1) / self.resolution)) and (smp < smpLen):
                # sample sum loop
                bar_smps += 1
                smp += 1
            self.probDb.append(bar_smps)

        self.probDb = np.array(self.probDb)
        self.probDb = self.probDb / smpLen * 100

        # calculate probability curve
        self.probSum.append(0)
        for idx in range((self.probDb.size) - 1):
            self.probSum.append(self.probDb[idx + 1] + self.probSum[idx])

        if self.calib:
            self.xAxis = np.linspace(dbMin, dbMax + 1 / self.resolution, totalBars)  # padding dBmax due padding above
        else:
            # dBFS
            self.xAxis = np.linspace(dbMin, 1 / self.resolution, totalBars)  # padding dBmax due padding above

        print('Prob sum', sum(self.probDb))
