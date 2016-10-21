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

from AnalyzeTools.PlotBar import PlotBar


class PlotHistogram(PlotBar):
    """
    QWidget class which contains the Histogram figure plot.

    General acessable variables (from calculation instance):
    self.values         --  calculation result
    self.xAxis          --  calculated x Axis
    """
    def __init__(self, xAxis, bars, calib, xLabelCalibrated, xLabelUncalibrated,  yLabel, probSum, resolution):
        """
        Initialize the parameters.

        :param calcObj: Adress of calculation object.
        :type calcObj: object
        :param calib: Is None if calibration is unset or the calibration value.
        :type calib: int
        """
        self.xLimMin = min(xAxis)
        self.xLimMax = max(xAxis)
        super().__init__(xAxis, bars, calib, xLabelCalibrated, xLabelUncalibrated, yLabel,
                         xLim=[self.xLimMin, self.xLimMax], barWidth=0.15)
        self.bars = bars
        self.probSum = probSum
        self.xAxis = xAxis

    def getPlot(self):
        """
        Returns the plot obj with plotted matplot canvas (self.canvas).

        :return: plot object
        :rtype: Obj
        """
        super().getPlot()
        self.axSum = self.ax.twinx()  # right ax
        self.axSum.plot(self.xAxis, self.probSum, 'r--', linewidth=2)
        self.axSum.set_ylabel('Cumulative Sum (%)', color='r')
        for label in self.axSum.yaxis.get_ticklabels():
            # label is a Text instance
            label.set_color('red')
        self.axSum.set_xlim(self.xLimMin, self.xLimMax + 0.5)
        self.ax.set_zorder(0.2)                 # increase z-order for bar plot, that pick_event is working!
        self.ax.patch.set_visible(False)        # hide the white 'canvas' from barplot
        self.axSum.patch.set_visible(True)      # enable canvas in the back

        self.fig.tight_layout()
        return self
