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
# this file contains the NavMenu base class and the NavMenuStandard Class, which is a Widgetused in the most of the cases.


class NavMenu(QWidget):

    """
    Nav Menu is the base class for the navigation and can be modified if not the standard
    navigation "NavMenuStandard" with delete, timeweighting, frequency weighting, and plot
    functions (pan, zoom, reset) isn't enoguh. This is E.g. the case for the FFT widget, 
    which includes the nth octave dropdown.
    """
    # general Nav signals
    # use this base class to modify your own navigation bar, that differs from the Basic Layout (WidgetNavFixed)
    pan = pyqtSignal()
    reset = pyqtSignal()
    zoom = pyqtSignal()
    reset = pyqtSignal()
    delete = pyqtSignal()
    reportState = pyqtSignal(bool)
    replot = pyqtSignal(str, str)

    def __init__(self):
        super(NavMenu, self).__init__()
        self.layout = QHBoxLayout()
        self.spacerwidget = QWidget()

        # Delete Frame
        self.deleteButton = QToolButton(clicked=self.delete)
        self.deleteButton.setToolTip('Delete analyse widget')
        self.deleteFrame = self.getFrame(self.deleteButton)
        self.deleteButton.setIcon(self.style().standardIcon(QStyle.SP_TitleBarCloseButton))

        # timeWeighting Frame
        self.timeWeightingFrame = QVBoxLayout()
        self.timeWeightingText = QLabel("Time Weighting")
        self.timeWeightingText.setAlignment(Qt.AlignHCenter)
        self.timeWeighting = QComboBox()
        self.timeWeighting.addItems(["slow", "fast", "impulse"])
        self.timeWeightingFrame.addWidget(self.timeWeightingText)
        self.timeWeightingFrame.addWidget(self.timeWeighting)

        # Frequencyweighting Frame
        self.fqWeightingFrame = QVBoxLayout()
        self.fqWeightingText = QLabel("Frequency Weighting")
        self.fqWeightingText.setAlignment(Qt.AlignHCenter)
        self.fqWeighting = QComboBox()
        self.fqWeighting.addItems(["A", "B", "C", "Z"])
        self.fqWeightingFrame.addWidget(self.fqWeightingText)
        self.fqWeightingFrame.addWidget(self.fqWeighting)

        # Buttons Frame
        self.buttonFrame = QHBoxLayout()
        self.buttonPan = QPushButton(clicked=self.pan)
        self.buttonPan.setCheckable(True)
        self.buttonPan.setText('Pan')
        self.buttonPan.setToolTip('Activate/Deactivate navigation for analyse plot')
        self.buttonZoom = QPushButton(clicked=self.zoom)
        self.buttonZoom.setCheckable(True)
        self.buttonZoom.setText('Zoom')
        self.buttonZoom.setToolTip('Activate/Deactivate zoom for analyse plot')
        self.buttonReset = QPushButton(clicked=self.reset)
        self.buttonReset.setText('Reset')
        self.buttonReset.setToolTip('Restore default zoom and pan settings')

        self.reportCheckbox = QCheckBox(toggled=self.sendReportState)
        self.reportCheckbox.setMaximumWidth(62)
        self.reportCheckbox.setText("Report")
        self.reportCheckbox.setToolTip('Activate for Report')

        self.buttonPanFrame = self.getFrame(self.buttonPan)
        self.buttonResetFrame = self.getFrame(self.buttonReset)
        self.buttonZoomFrame = self.getFrame(self.buttonZoom)

        self.buttonFrame.addLayout(self.buttonPanFrame)
        self.buttonFrame.addLayout(self.buttonZoomFrame)
        self.buttonFrame.addLayout(self.buttonResetFrame)
        self.buttonFrame.addWidget(self.reportCheckbox)

        # Signal connects
        self.fqWeighting.currentIndexChanged.connect(self.sendReplot)
        self.timeWeighting.currentIndexChanged.connect(self.sendReplot)

    def getFrame(self, bottomwidget, topwidget=None):
        layout = QVBoxLayout()
        if topwidget is None:
            topwidget = self.spacerwidget
        layout.addWidget(topwidget)
        layout.addWidget(bottomwidget)
        return layout

    def sendReplot(self):
        """
        Emit replot signal.
        """
        timeWeight = str(self.timeWeighting.currentText())
        fqWeight = str(self.fqWeighting.currentText())
        self.replot.emit(timeWeight, fqWeight)

    def sendReportState(self, status):
        """
        Emit report signal.
        
        :param status: bool state if report is activated
        :type status: bool
        """
        self.reportState.emit(status)

    def selectReport(self):
        """
    	Activate widget report checkbox.
    	"""
        self.reportCheckbox.setCheckState(3)

    def deselectReport(self):
        """
    	Deactivate widget report checkbox.
    	"""
        self.reportCheckbox.setChecked(False)


class NavMenuStandard(NavMenu):
    """Use this standard navigation class to provide your Analyse Widget with a regular, fixed Navigation bar:
    Frequency Weighting (Dropdown), Time Weighting (Dropdown), Reset, Zoom, Pan, Report (Checkbox) and Delete.
    Optional parameters 'timeWeighting' and 'fqWeighting' offers the possibility to hide the selection.

    For extendend more buttons, create your Widget own Nav* Script and inherit from WidgetNav Base Class."""
    replot = pyqtSignal(str, str)

    def __init__(self, timeWeighting=True, fqWeighting=True):
        super(NavMenuStandard, self).__init__()
        self.selectionLayout = QHBoxLayout()
        if timeWeighting:
            self.selectionLayout.addLayout(self.timeWeightingFrame)
        if fqWeighting:
            self.selectionLayout.addLayout(self.fqWeightingFrame)

        self.layout.addLayout(self.deleteFrame)
        self.layout.addLayout(self.selectionLayout)
        self.layout.addLayout(self.buttonFrame)

        self.setLayout(self.layout)
