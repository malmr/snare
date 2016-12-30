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

import pandas as pd
import numpy as np


class NominalData:
    """
    Pool for common nominal data.
    Handles the read from NominalData CSV file in which the FFT band indices, corresponding nominal frequencies and
    time weighting coefficients for the difference equation are stored. All nominal data are adopted after standard
    IEC 61672:1 2013: A standard for sound level meters.
    """
    def __init__(self, csvFile):
        """
        Initialize parameters.
        :param csvFile: absolute path to csv file.
        """
        self.csvFile = csvFile
        print(csvFile)

    def weighting(self, weight):
        if weight == 'A':
            b = 'Ba'
            a = 'Aa'
        elif weight == 'B':
            b = 'Bb'
            a = 'Ab'
        elif weight == 'C':
            b = 'Bc'
            a = 'Ac'
        else:
            raise BaseException('Unknown weighting value.')
        return np.array(self.__readWeighting__()[b])[:10], np.array(self.__readWeighting__()[a])[:10]

    def nominalFrequencies(self, nthOctave, bandNo, onlyNth=1):
        """
        Returns the nominal frequencies.
        Parameter nthOctave specifies for witch nth Octave the nominal frequencies are needed.

        :param nthOctave: Nth Octave
        :type nthOctave: int
        :param bandNo: Band indices
        :type bandNo: int
        :param onlyNth: defines if every nominal frequency or just every nth frequency is returned
        :type onlyNth: int
        :return: nominal frequencies
        :rtype: array
        """
        if nthOctave == 1:
            selector = 24
            idx = 160 + bandNo      # 31.5Hz -maxBandNo + (-startBandNo)
        elif nthOctave == 3:
            selector = 8
            idx = 160 + bandNo      # 25Hz
        elif nthOctave == 6:
            selector = 4
            idx = 160 + bandNo      # 20Hz
        elif nthOctave == 12:
            selector = 2
            idx = 0                 # 10Hz
        elif nthOctave == 24:
            selector = 1
            idx = 0                 # 10Hz
        axis = np.array(self.__readWeighting__()['nominal'])[idx::selector]
        axisShort = axis
        if onlyNth != 1:
            # select only every nth nominalfq
            nominal = ["" for x in range(len(axisShort))]
            nominal[::onlyNth] = axisShort[::onlyNth]
            axisShort = np.asarray(nominal)
            return axis, axisShort
        else:
            return axis, axis

    def __readWeighting__(self):
        """Returns DataFrame with nominal frequencies, band No,
        A, B, C, Z weighted discrete coefficients out of a CSV file.
        Usage:  np.array(weightingData[ColName])
                weightingData['C']"""
        return pd.DataFrame(pd.read_csv(self.csvFile, sep=';', index_col=0))