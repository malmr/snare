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
from AnalyzeTools.WidgetSpl.CalculationSpl import CalculationSpl
from AnalyzeTools.WidgetSpl.PlotSpl import PlotSpl
from AnalyzeTools.NavMenu import NavMenuStandard


class WidgetSpl(AnalyzeWidget):
    """
    Sound Pressure Level Analyze Widget.

    Plots the dB values against time axis. According to whether calibration is set, the values are either in dB
    fullscale peakvalues or in dB soundpressure level values. The values are frequency- and time-weighted.
    seealso::For further information on the calibration implementation have a look at AnalyzeBuffer.

    note::At initialisation the calculation and plot methods are executed automatically.
    The QWidget stored in self.plot will be integrated in the Analyze Frame.
    """

    def __init__(self, snare, channel, selNo, timeWeight, fqWeight, parm1=None, parm2=None, parm3=None):
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
        self.nav = NavMenuStandard()
        self.buffer = snare.analyzeBuffer.getBuffer(channel, selNo)

        super().__init__(snare, channel, selNo, timeWeight, fqWeight)

    def calculate(self):
        """
        Initialize the calculation object and execute it.
        """
        self.calc = CalculationSpl(self.snare, self.buffer, self.calib, self.timeWeight, self.fqWeight)

    def plot(self):
        """
        Initialize the plot object, store the matplot figure and fill out the labels.
        """
        # store & plotting
        self.plot = PlotSpl(self.calc, self.calib).getPlot()

        # labeling
        self.titleLabel = QLabel(self.channel.getName() + ' ' + self.selNo + ' ' + ": Sound Pressure Level")
        self.titleLabel.setAlignment(Qt.AlignCenter)
        self.infoLabel = QLabel(self.calibInfo + self.spacing + 'Weighting: ' + self.fqWeight + self.spacing +
                                'Meter Speed: ' + self.timeWeight)