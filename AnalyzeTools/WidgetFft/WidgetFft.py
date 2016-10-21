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

from PyQt5.QtWidgets import *
from PyQt5.Qt import *
from AnalyzeTools.AnalyzeWidget import AnalyzeWidget

# adjust these imports
from AnalyzeTools.WidgetFft.CalculationFft import CalculationFft
from AnalyzeTools.WidgetFft.PlotFft import PlotFft
from AnalyzeTools.WidgetFft.NavFft import NavFft


class WidgetFft(AnalyzeWidget):
    """
    Fast Fourier Transform Analyze Widget.

    Plots the one sided nth Octave FFT with N = 1, 3, 6, 12, 24. The values are frequency- and time-weighted depending
    on the user selection. According to whether calibration is set, the values are either in dB fullscale peakvalues or
    in dB soundpressure level values.
    seealso::For further information on the calculation implementation have a look at CalculationFft.

    note::At initialisation the calculation and plotFigure methods are executed automatically.

    note:: The essential parts which will be automatically set to the widget (by base class):
    self.titleLabel -- widget title
    self.nav        -- navigation menu (dropdown selections, zoom, pan etc)
    self.figurePlot -- actual matplot figure
    self.infoLabel  -- additonal widget information
    """

    def __init__(self, snare, channel, selNo, timeWeight, fqWeight, parm1, parm2, parm3):
        """
        Initialize the parameters and submit them to the constructor of the AnalyzeWidget base class.
        :param snare: Common used variables implenented in MainBackend.
        :type snare: object
        :param channel: Channelobject
        :type channel: object
        :param selNo: String of selection label
        :type selNo: str
        :param timeWeight: Time weight slow, fast or impulse
        :type timeWeight: str
        :param fqWeight: Frequency weight A, B, C or Z
        :type fqWeight: str
        :param parm1: optional widget parameter (for widget NavMenu)
        :param parm2: optional widget parameter (for widget NavMenu)
        :param parm3: optional widget parameter (for widget NavMenu)
        """

        # initial values
        self.nthOctave = int(parm1)
        self.nav = NavFft()
        self.nav.nthFft.setCurrentText(str(self.nthOctave))

        self.buffer = snare.analyzeBuffer.getBuffer(channel, selNo)
        super().__init__(snare, channel, selNo, timeWeight, fqWeight)

    def calculate(self):
        """
        Initialize the calculation object and execute it.
        """
        self.calc = CalculationFft(self.snare, self.buffer, self.calib, self.nthOctave, self.timeWeight, self.fqWeight)
        return self.calc.fft

    def plot(self):
        """
        Initialize the plot object, store the matplot figure and fill out the labels.
         """
        # store & plotting
        self.plot = PlotFft(self.calc, self.calib).getPlot()

        # labeling
        self.titleLabel = QLabel(self.channel.getName() + ' ' + self.selNo + ': ' + self.fqWeight + ' Weighted ' + str(
            self.nthOctave) + "th Octave Band Analysis")
        self.titleLabel.setAlignment(Qt.AlignCenter)
        self.infoLabel = QLabel(self.calibInfo)