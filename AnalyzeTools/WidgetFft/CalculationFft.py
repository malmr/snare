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

# ToDo: Toniproject Windowing FFT


class CalculationFft(Calculation):
    """
    FFT Calculation Class including the methods for the FFT signal processing.

    variables
    self.values:    Buffer values.
    self.xAxis:     To write the xAxis values into.

    Additional variables
    self.nthOctave  int: 1, 3, 6, 12, 24
    self.xAxisComplete
    """

    def __init__(self, snare, buffer, calib, nthOctave, timeWeight, fqWeight):
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

        # additional instance variables
        self.nthOctave = nthOctave
        self.xAxisComplete = None

        # frequency-weighting
        self.values = self.fqWeighting(self.values, self.fqWeight)

        self.calculate()

    def calculate(self):
        """
        Calculates the single sided FFT.
        A fftSize of 2^18 is choosen which offers a resolution of 32 values in the lowest frequency bin. When
        calculating the dB values of the energetic values the return is either dBFS or dBSPL depending on calibration.
        Stores the result in self.values, self.xAxis and self.xAxisComplete.
        """
        fftSize = 262144

        [bandNo, bandFinal, everyNth] = self.fftBandNo()
        [fNominalAxis, fNominalAxisReduced] = self.__nominalValues__.nominalFrequencies(self.nthOctave, bandNo, everyNth)

        y = np.abs(self.fft(self.values, fftSize)) / fftSize
        y = 2 * y[0:fftSize // 2]   # take absolute values, cut them to fftsize/2, multiply by 2 (single sided FFT)
        p = y ** 2                  # power of spectrum
        faxisexact = np.linspace(0, self.snare.sampleRate / 2, fftSize / 2)
        pBars = self.calcBars(p, bandNo, bandFinal, faxisexact, self.nthOctave)

        # convert to dB values.
        # Beware that either dBFS or dbSPL values are returned.
        pDb = self.db(pBars)

        # result
        self.values = pDb
        self.xAxis = fNominalAxisReduced
        self.xAxisComplete = fNominalAxis

    def centerFqExact(self, bandNo, nthOctave):
        """
        Returns the exact center frequency of given band no and N.

        :param bandNo: Band number of needed center frequency.
        :type bandNo: int
        :param nthOctave: N FFT octave
        :type nthOctave: int
        :return: exact center frequency in Hz
        :rtype: float
        """
        if nthOctave % 2:
            #uneven
            return 10 ** (3 / 10 * bandNo / 24 + 3)
        else:
            return 10 ** (3 / 10 * 2 * bandNo / (2 * 24) + 3)

    def edgeFqExact(self, centerFq, nthOctave):
        """
        Returns the exact edge frequencies for a given center frequency and N.

        :param centerFq: center frequency
        :type centerFq: float
        :param nthOctave: N FFT octave
        :type nthOctave: int
        :return: exact side frequencies in Hz
        :rtype: tuple
        """
        lowerfq = centerFq / 2 ** (1 / (2 * nthOctave))
        upperfq = centerFq * 2 ** (1 / (2 * nthOctave))
        return (lowerfq, upperfq)

    def calcBars(self, a, bandNo, bandFinal, FqAxisExact, nthOctave):
        """
        Calculates the FFT bars.

        note:: Exception for the upper frequency in full octave calculation is realized, which allowes to attain a
        value above Fs/2. Otherwise the highest bar in full ocatve would be 16kHz instead of 20kHz because of a few
        percentage of missing values.

        :param a: values
        :type a: array
        :param bandNo: start noninal band number
        :type bandNo: int
        :param bandFinal: final nominal band number
        :type bandFinal: int
        :param FqAxisExact: exact frequency axis which correpsonds to param a (in contrast to the rounded nominal axis)
        :type FqAxisExact: array
        :param nthOctave: N FFT octave
        :type nthOctave: int
        :return: Array with calculated bars
        :rtype: array
        """
        yBars = np.array([])
        for bandNo in range(bandNo, bandFinal + 1)[0::24 // nthOctave]:
            centerFqExact = self.centerFqExact(bandNo, nthOctave)

            # calculate exact edge frequencies
            [lowerEdgeExact, upperEdgeExact] = self.edgeFqExact(centerFqExact, nthOctave)
            lowerIdx = self.indexOfNearestVal(FqAxisExact, lowerEdgeExact)
            if (bandNo == 96) & (nthOctave == 1):
                # exception: upperFq of full octave is allowed to get above fs/2
                upperIdx = int(len(FqAxisExact)) - 1
            else:
                upperIdx = self.indexOfNearestVal(FqAxisExact, upperEdgeExact)
            yBars = np.append(yBars, np.sum(a[lowerIdx:upperIdx]))

            # analyse:
            # band no: 24 band normed to 1kHz
            # print('band: %7d \t\tL: %7.2f U: %7.2f calced' % (bandNo, lowerEdgeExact, upperEdgeExact))
            # print('center: %7.2f \tL: %7.2f U: %7.2f picked' % (centerFqExact, FqAxisExact[lowerIdx],
            #                                                        FqAxisExact[upperIdx]))
            #
            # print('fq bins:', upperIdx - lowerIdx)
            # print('value: %7.2f\n' % np.mean(a[lowerIdx:upperIdx]))

            bandNo += 1
        return yBars

    def fftBandNo(self):
        """
        Returns the correct nominal start and end band no as well as well as the stepsize corresponding to the current
        Nth Octave.
        
        :return: Nominal start and finish band and stepsize
        :rtype: tuple
        """
        if self.nthOctave == 1:
            [bandNo, bandFinal] = -120, 96  # 31.5Hz, 16 kHz (bandNo 96, upper Fq actually > fs/2)
            everyNth = 1  # step-size for ticks in plot
        elif self.nthOctave == 3:
            [bandNo, bandFinal] = -128, 96  # 25Hz, 16kHz
            everyNth = 1
        elif self.nthOctave == 6:
            [bandNo, bandFinal] = -136, 104  # 20Hz, 20kHz
            everyNth = 2
        elif self.nthOctave == 12:
            [bandNo, bandFinal] = -160, 104  # 10Hz, 20kHz
            everyNth = 4
        elif self.nthOctave == 24:
            [bandNo, bandFinal] = -160, 104  # 10Hz, 20kHz
            everyNth = 8
        else:
            raise BaseException(self.nthOctave + ' is not a supported Octave fragmentation.')
        return bandNo, bandFinal, everyNth

    # def getFftLin(self):
    #     """ Get the fft with linear interpolation (point averaging).
    #         It can plot the full spectrum (no optional parameter) or just the singlesided spectrum."""
    #
    #     fftsize = len(self.values)  # calcable value
    #     a = np.abs(self.fft(self.values, fftsize)) / fftsize
    #     a = 2 * a[0:fftsize // 2]
    #     p = a ** 2  # power of spectrum
    #     self.values = self.db(p, rms=False)
    #     self.xAxis = self.snare.sampleRate * np.linspace(0, fftsize / 2, fftsize / 2) / fftsize
