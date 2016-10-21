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

from PyQt5.QtCore import *
from PyQt5.Qt import *
from AnalyzeTools.Plot import Plot
import matplotlib.pyplot as plt
import math
import numpy as np


class PlotBar(Plot):
    """Common used plot class for bar plots."""
    def __init__(self, xAxis, bars, calib, xLabelCalibrated, xLabelUncalibrated, yLabel, xLim, barWidth=0.1):
        super().__init__()
        self.bars = bars
        self.xAxis = xAxis
        self.xLabelCalibrated = xLabelCalibrated
        self.xLabelUncalibrated = xLabelUncalibrated
        self.yLabel = yLabel
        self.xLim = xLim
        self.barWidth = barWidth
        self.calib = calib

    def getPlot(self):
        self.ax.bar(self.xAxis, self.bars, width=self.barWidth, picker=0, linewidth=0, color='k')
        if self.calib is False:
            # dBFS
            plt.ylabel(self.yLabel)
            plt.ylim(bottom=0)
            plt.xlabel(self.xLabelUncalibrated)
        else:
            # dBSPL
            plt.ylabel(self.yLabel)
            plt.ylim(bottom=0)
            plt.xlabel(self.xLabelCalibrated)
        plt.xlim(self.xLim)

        tooltip = PlotBarToolTip(self.bars, self.xAxis, ax=self.ax, calib=True, xTol=self.barWidth, xUnit='dB', yUnit='%')
        self.fig.canvas.mpl_connect('button_press_event', tooltip)
        self.fig.canvas.mpl_connect('pick_event', tooltip.changeColor)
        return self


class PlotBarToolTip(QThread):
    """callback for matplotlib to display a tooltip when frequencybars are
    clicked.
    parm: calib  boolean if plot is calibration dependent (dbFS and dBSPL on y axis)
    xDataComplete is used for FFT Plots, where more FQ Bars exist as the axis got for discrete values.
    """

    def __init__(self, values, xAxis, ax, calib=True, xDataComplete=None, xTol=None, xUnit='Hz', yUnit='dB'):
        """
        Initialize the variables. Round dB values for showing. Set offset if calibration is set. Start method for
        drawing anotations.

        :param values: Y axis values
        :type values: array
        :param xAxis: x Axis values
        :type xAxis: array
        :param ax: X Axis object from the original plot to adjust the plot (f.e. change color on pick)
        :type ax: ndarray
        :param calib: calibration factor, False if empty
        :type calib: int
        :param xDataComplete: Complete xAxis (only for FFT needed), stores the original values in contrast to nominal
        xAxis.
        :type xDataComplete: array
        :param xTol: Area in pixel in which a click is tolerated around the bars.
        :type xTol: int (px)
        :param xUnit: x axis unit for tooltip
        :type xUnit: str
        :param yUnit: y axis unit for tooltip
        :type yUnit: str
        """
        super().__init__()
        self.calib = calib
        self.xAxis = xAxis
        self.xUnit = xUnit
        self.yUnit = yUnit
        self.values = values

        roundedDb = np.around(values, decimals=2)

        if self.calib is False:
            self.calibOffset = 6
        else:
            self.calibOffset = 0

        # additional x vectors for FFT
        self.xDataComplete = xDataComplete
        if xDataComplete is None:
            #not FFT
            self.xDataComplete = np.around(self.xAxis, decimals=2)

        if xTol is None:
            xTol = ((max(xAxis) - min(xAxis))/float(len(xAxis)))/2
        self.xTol = xTol
        self.ax = ax
        self.drawnAnnotations = {}
        self.data = list(zip(xAxis, values, roundedDb))

    def distance(self, x1, x2, y1, y2):
        """
        return the distance between two points.
        """
        return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)

    def __call__(self, event):
        """
        Overwrites click event to get coordinates and clicked bar.
        """
        if event.inaxes:
            clickX = event.xdata
            clickY = event.ydata
            if (self.ax is None) or (self.ax is event.inaxes):
                roundedDb = []
                # print(event.xdata, event.ydata)
                idx = 0
                for x, y, a in self.data:
                    #print(idx, x, y, a)
                    if x <= clickX <= x + self.xTol and (bool(self.calib) == bool((clickY <= y))):
                        roundedDb.append((self.distance(x, clickX, y, clickY), x, y, a, idx))
                    idx += 1

                if roundedDb:
                    roundedDb.sort()
                    distance, x, y, dbval, idx = roundedDb[0]
                    self.drawTooltip(event.inaxes, x-0.5, y-self.calibOffset, dbval, idx)

    def drawTooltip(self, ax, x, y, dbval, idx):
        """
        Draw the bar text on the plot.
        """
        if (x, y) in self.drawnAnnotations:
            markers = self.drawnAnnotations[(x, y)]
            for m in markers:
                m.set_visible(not m.get_visible())
            self.ax.figure.canvas.draw_idle()
        else:
            t = ax.text(x, y, "{:}{:}\n{:^10}".format(dbval, self.yUnit,
                                                      str(self.xDataComplete[idx]) + str(self.xUnit)), alpha=0.8)
            t.set_bbox(dict(color='white', alpha=0.7))
            m = ax.scatter([x], [y], marker=None)
            self.drawnAnnotations[(x, y)] = (t, m)
            self.ax.figure.canvas.draw_idle()

    def changeColor(self, event):
        """
        Deal with pick events and changes the color..
        """
        if event.mouseevent.button == 1:  # --> Left-click only
            selectedColor = (0.25, 1.0, 0.25, 1.0)
            if event.artist.get_facecolor() == selectedColor:
                event.artist.set_facecolor(self.normalColor)
            else:
                self.normalColor = event.artist.get_facecolor()
                event.artist.set_facecolor(selectedColor)

            self.ax.figure.canvas.draw_idle()
