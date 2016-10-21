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
from scipy import fftpack, signal
from AnalyzeTools.NominalData import NominalData
from PyQt5.QtCore import QThread


class Calculation(QThread):
    """
    Pool for common calculation methods which is inherited for every calculation class of a analyze widget.
    The class contain all necessary nominal data adopted from IEC 61672:1 2013 Standard. More precisely this involves band
    indices, nominal frequencies and weighting values. Frequency weighting is preformed in time domain with an
    implementation of the difference equation in direct form II with the correct coefficients. ::seealso fqWeighting
    Time weighting is done by integrate the sound pressure using exponential integration. This is realized by applying
    a low-pass filter with one real pole at :math:'-1/\\tau'.
    """
    def __init__(self, snare, calib, timeWeight, fqWeight):
        # data from IEC 61672:1 2013 Norm. Band Indizes, Normfrequenzen und Gewichtung:
        self.__nominalValues__ = NominalData()
        self.snare = snare
        self.timeWeight = timeWeight
        self.fqWeight = fqWeight
        self.calib = calib
        self.p0 = 20 * 10**(-6)
        self.referenceDb = 94

    def db(self, a, rms=False):
        """
        Returns dB sound pressure level or dB fullscale peakvalues depending if a calibration is set.
        warning:: Values in array 'a' need to be energetic values (pressure squared).

        :param a: Input values
        :type a: array
        :param rms: Optional to handle root mean square
        :type rms: bool
        :return: dBSPL or dBFS values
        :rtype: array
        """
        if rms is True:
            a /= 2  # RMS value (Effektivwert), divided by sqrt(2)^2 because of power spectrum

        if self.calib is False:
            # dBFS
            print('no calibration - take dBFS')
            p_db = self.___dbFsSquare___(a)
        else:
            # dBSPL
            print('calibration')
            p_db = self.___dbSplSquare___(a)
        return p_db

    def rms(self, a):
        """
        Returns the root mean square of all the elements of a.

        :param a: Input array
        :type a: array
        :return: RMS of a
        :rtype: array
        """
        return np.sqrt(np.mean(np.absolute(a) ** 2))

    def dbSplToPascal(self, db):
        """
        Converts dBSPL to Pascal.
        :param db: Array with dB values
        :return: array
        """
        return self.p0 * 10**(db/20)

    def fft(self, a, fftSize=10000):
        """
        Calculates the fast fourier transform of the input array.

        :param a: Input array
        :type a: array
        :param fftSize: FFT Size; optional parameter
        :return: FFT values
        :rtype: array
        """
        return fftpack.fft(a, fftSize)

    def fqWeighting(self, values, fqWeight):
        """
        Apply A, B, C or Z frequency-weighting.
        First the needed nominal weighting coefficients a and b are imported. The filtering is implementated in lfilter
        with Direct Form II using standard difference equation.

        :param values: Input values
        :type values: array
        :param fqWeight: Frequency-weight A, B, C or Z
        :type fqWeight: str
        :return: Frequency-weighted values
        :rtype: array
        """
        if fqWeight == 'Z':
            return values
        [b, a] = self.__nominalValues__.weighting(fqWeight)
        return signal.lfilter(b, a, values)

    def timeWeighting(self, values, timeWeight):
        """Apply slow, fast or impulse time-weighting.
         Time weighting is done by integrate the sound pressure using exponential integration.

        :param values: Input values
        :type values: array
        :param timeWeight: Time-weight slow, fast or impulse
        :type timeWeight: str
        :return: Time-weighted values
        :rtype: array
        """
        if timeWeight == 'slow':
            integrationTime = 1.000
        elif timeWeight == 'fast':
            integrationTime = 0.125
        elif timeWeight == 'impulse':
            integrationTime = 0.035
        else:
            raise BaseException(type, 'is an unknown time weighting type!')

        values = self.___integrateSpl___(values, integrationTime)
        values *= 1 / integrationTime
        return values

    def indexOfNearestVal(self, a, value):
        """
        Returns the index of an array which is nearest to the given value.
        Finds an index of nearest value in sorted array compared to given value. Its fast for large arrays.
        warning:: array needs to be sorted!
        :param a: Input values
        :type a: array
        :param value: Nearest value
         :type value: int
        :return: Index of nearest value
        :rtype: int
        """
        idx = np.searchsorted(a, value, side="left")
        idx -= np.abs(value - a[idx - 1]) < np.abs(value - a[idx])
        return idx

    def ___dbSplSquare___(self, a):
        """
        Private class used by db method to convert to dB sound pressure level with already squared values.

        :param a: Energetic quantity (squared amplitudes)
        :type a: array
        :returns: array in Decibel SPL
        :rtype: array
        """
        # set zero values to almost 0 (log(0) raises error)
        zeroIndices = np.asarray(a) == 0
        a[zeroIndices] = 10**(-12)

        db_spl = 10.0 * np.log10(a/(self.p0**2))
        # cut values lower 0, occours during frequency weighting:
        lowIndices = np.asarray(db_spl) < 0
        db_spl[lowIndices] = 0
        return db_spl

    def ___dbFsSquare___(self, a):
        """
        Private class used by db method to convert to dB fullscale with already squared values.

        :param a: Energetic quantity (squared amplitudes)
        :type a: array
        :return: array in Decibel FS
        :rtype: array
        """
        return 10.0 * np.log10(8.0 * a / ((2 ** (self.snare.sampleWidth * 8.0)) ** 2))

    def ___integrateSpl___(self, y, integrationTime):
        """
        Private class used by fqWeighting to Integrate the sound pressure squared using exponential integration.
        Time weighting is applied by applying a low-pass filter with one real pole at :math:'-1/\\tau'.
    
        :param a: Energetic quantity (squared amplitudes)
        :type a: array
        :param integrationTime: Integration time
        :type integrationTime: int
        :returns: Time weighted sound pressure
        """
        b, a = signal.bilinear(1, [1, 1 / integrationTime], fs=self.snare.sampleRate)
        return signal.lfilter(b, a, y)