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
import matplotlib.pyplot as plt


class PlotExample(Plot):
    """
    Plot class which is a QWidget containing the figure plot.
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
        self.values = calcObj.values    # dB Values
        self.xAxis = calcObj.xAxis      # time Axis
        self.calib = calib

    def getPlot(self):
        """
        Returns the plot obj with plotted matplot canvas (self.canvas).

        :return: plot object
        :rtype: Obj
        """
        plot = plt.plot(self.xAxis, self.values)
        plt.xlabel('Time ($s$)')
        if self.calib is False:
            # dBFS
            plt.ylabel('digital values')
        else:
            # dBSPL
            plt.ylabel('RMS normalized values')
        self.fig.tight_layout()
        return self
