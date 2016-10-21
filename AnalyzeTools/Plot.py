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
import matplotlib
matplotlib.use('qt5agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from PyQt5.QtCore import QThread

class Plot(QThread):
    """
    Base class for every plot class.
    """
    def __init__(self):
        """
        Set up common used variables for plotting the matplotlib figure.
        :return:
        :rtype:
        """
        super(Plot, self).__init__()
        plt.close('all')
        plotWidth = 15
        plotHeight = 5
        self.fig, self.ax = plt.subplots(figsize=(plotWidth, plotHeight), facecolor="#EDEDED")
        self.canvas = self.ax.figure.canvas

        self.toolbar = NavigationToolbar(self.canvas, None)
        self.toolbar.hide()  # initialize toolbar to later acess their methods
        self.canvas.setMinimumHeight(350)
        self.canvas.setMinimumWidth(1200)
