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

from AnalyzeTools.Plot import Plot
from AnalyzeTools.PlotBar import PlotBarToolTip
import matplotlib.pyplot as plt
import numpy as np

class PlotFft(Plot):
    """
    QWidget class which contains the FFT figure plot.

    General acessable variables (from calculation instance):
    self.values         --  calculation result
    self.xAxis          --  calculated x Axis

    Additional variables:
    self.nthOctave      --  3, 6, 12, 24th Octave
    self.xAxisComplete  --  complete frequency axis with all nominal values. Depending on nth Octave the right values are picked.
    """
    def __init__(self, calcObj, calib):
        """
        Initialize the parameters.

        :param calcObj: Adress of calculation object.
        :type calcObj: object
        :param calib: Is None if calibration is unset or the calibration value.
        :type calib: int
        """
        super().__init__()

        # route instance variables from calculation
        self.values = calcObj.values
        self.xAxis = calcObj.xAxis
        self.xAxisComplete = calcObj.xAxisComplete
        self.nthOctave = calcObj.nthOctave
        self.calib = calib

    def getPlot(self):
        """
        Returns the plot obj with plotted matplot canvas (self.canvas).

        :return: plot object
        :rtype: Obj
        """
        barCnt = len(self.values)
        barWidth = 0.828 + 0.15/21 * self.nthOctave
        plotAxis = np.linspace(0, barCnt, barCnt)
        barPlot = plt.bar(plotAxis, self.values, width=barWidth, picker=0)
        xTicksPos = [0.5 * patch.get_width() + patch.get_xy()[0] for patch in barPlot]
        plt.xticks(xTicksPos, self.xAxis, ha='center')
        plt.tick_params(length=0)
        plt.xlabel('Frequency ($Hz$)')
        if self.calib is False:
            # dBFS
            plt.ylabel('$dB FS$')
            plt.ylim(top=0)

        else:
            # dBSPL
            plt.ylabel('$L_p$ ($dB SPL$)')
            plt.ylim(bottom=0)
        plt.xlim(-3 * self.nthOctave/24, barCnt + 1 + 3 * self.nthOctave/24)

        tooltip = PlotBarToolTip(self.values, plotAxis, ax=self.ax, calib=self.calib,
                                 xDataComplete=self.xAxisComplete, xTol=barWidth)

        self.fig.canvas.mpl_connect('button_press_event', tooltip)
        self.fig.canvas.mpl_connect('pick_event', tooltip.changeColor)

        self.fig.tight_layout()
        return self

    # def getfftplotlin(self):
    #     plt.plot(self.xAxis, self.values)
    #     plt.xlabel('Frequency ($f$)')
    #     plt.ylabel('Amplitude ($dB$)')
    #     self.ax.set_xscale('log')
    #     plt.fill_between(self.xAxis, self.values, min(self.values), interpolate=True, color='blue')
    #     return self
