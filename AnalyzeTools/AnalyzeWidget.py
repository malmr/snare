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
from PyQt5.QtCore import *


class AnalyzeWidget(QWidget):
    """
    AnalyzeWidget is the base class for every Analyze Widget.
    It contains the figurePlot, navigation menu and the labels. The whole layout is set in self.layout. The figurePlot
    is stored in self.figurePlot, the navigation in self.nav and the labels in self.titleLabel as well as
    self.infoLabel."""

    report = pyqtSignal(bool, object, str)

    def __init__(self, snare, channel, selNo, timeWeight, fqWeight):
        """
        Initialize the variables, frequency-weight the values and start the calculation method.

        :param snare: Common used variables implenented in MainBackend.
        :type snare: object
        :param channel: Channel Object
        :type channel: object
        :param selNo: String of selection label
        :type selNo: str
        :param timeWeight: Time weight slow, fast or impulse
        :type timeWeight: str
        :param fqWeight: Frequency weight A, B, C or Z
        :type fqWeight: str
         """
        super(AnalyzeWidget, self).__init__()
        # initial values general
        self.timeWeight = timeWeight
        self.fqWeight = fqWeight
        self.snare = snare
        self.channel = channel
        self.selNo = selNo
        self.calc = None
        self.titleLabel = None
        self.infoLabel = None
        self.calib = self.snare.calibrations.factors.get(self.channel, False)
        self.layout = QVBoxLayout()

        # set initial vals
        self.nav.timeWeighting.setCurrentText(self.timeWeight)
        self.nav.fqWeighting.setCurrentText(self.fqWeight)

        # labeling
        self.spacing = '<span>' + 5 * "&nbsp;" + '</span>'
        if self.calib:
            self.calibInfo = "Cal factor (94dB): " + str(
                round((2 ** (8 * self.snare.sampleWidth) * self.calib), 5))
        else:
            self.calibInfo = "Calibrated: <span style='color:#B84E48'>No</span>"

        # calculate and plot
        self.calculate()
        self.plot()
        self.setupLayout(self.layout)

        # connect signals
        self.nav.pan.connect(self.pan)
        self.nav.zoom.connect(self.zoom)
        self.nav.reset.connect(self.reset)
        self.nav.reportState.connect(self.sendReportState)
        self.nav.delete.connect(self.delete)

        # zoom with scrollwheel (when ctrl is pressed)
        self.plot.fig.canvas.mpl_connect('scroll_event', self.zoomPlot)

    # function calls for signals
    def pan(self):
        """
        Trigger the pan signal for the figure toolbar.
        """
        self.plot.toolbar.pan()

    def zoom(self):
        """
        Trigger the zoom signal for the figure toolbar.
        """
        self.plot.toolbar.zoom()

    def reset(self):
        """
        Trigger the reset signal for the figure toolbar.
        """
        self.plot.toolbar.home()

    def zoomPlot(self, event):
        """
        Zoom in and out by ctrl + scroll wheel.
        :param event: Mouse event
        :type event: matplotlib.backend_bases.MouseEvent
        """
        modifiers = QApplication.keyboardModifiers()
        if modifiers == Qt.ControlModifier:
            # get the current x and y limits

            zoomScale = 1.2

            if event.button == 'up':
                # deal with zoom in
                scale_factor = 1 / zoomScale
            elif event.button == 'down':
                # deal with zoom out
                scale_factor = zoomScale
            else:
                # deal with something that should never happen
                scale_factor = 1
                print(event.button)

            xdata = event.xdata
            ydata = event.ydata

            if xdata and ydata:
                cur_xlim = self.plot.ax.get_xlim()
                cur_ylim = self.plot.ax.get_ylim()

                x_left = xdata - cur_xlim[0]
                x_right = cur_xlim[1] - xdata
                y_top = ydata - cur_ylim[0]
                y_bottom = cur_ylim[1] - ydata

                self.plot.ax.set_xlim([xdata - x_left * scale_factor,
                                             xdata + x_right * scale_factor])
                self.plot.ax.set_ylim([ydata - y_top * scale_factor,
                                             ydata + y_bottom * scale_factor])

                self.plot.ax.figure.canvas.draw()  # force re-draw

    def delete(self):
        """
        Trigger the delete widget signal.
        """
        self.snare.analyses.deleteWidget(self.channel, self.selNo)

    def sendReportState(self, state):
        """
        Forward report information to ReportManager; with togglestate and channel/selNo as parameters.
        :param state: Togglestate of "Report" checkbox.
        :type state: bool
        """
        self.snare.reports.state(state, self.channel, self.selNo)

    def setupLayout(self, layout):
        """
        Set up the default layout of a AnalyzeWidget.
        :param layout: transmit the layout
        :type layout: layout
        """
        layout.addWidget(self.titleLabel)
        layout.addWidget(self.nav)
        layout.addWidget(self.plot.canvas)
        layout.addWidget(self.infoLabel)
        self.setLayout(layout)
