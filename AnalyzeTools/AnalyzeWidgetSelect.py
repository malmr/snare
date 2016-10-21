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
import importlib


class AnalyzeWidgetSelect(QWidget):
    """
    AnalyzeWidgetSelect encapsulates the selected Analyze Widget and initialize it dynamically depending on user choice.
    The replot methods handlle the signals for replot/refresh. A method for clearing a layout is also implemented.
    """

    def __init__(self, snare, channel, selNo, type):
        """
        Initialize the widget variables and connect the signals.

        :param snare: Common used variables implenented in MainBackend.
        :type snare: object
        :param channel: unique Channelobject
        :type channel: object
        :param selNo: String of selection label
        :type selNo: str
        :param type: Analyze type (f.e. FFT, Histo. ...)
        :type type: str
        """
        super(AnalyzeWidgetSelect, self).__init__()
        self.currentWidget = None
        self.snare = snare
        self.channel = channel
        self.selNo = selNo
        self.type = type
        self.timeWeight = None
        self.fqWeight = None
        self.widgetInfo = self.snare.analyses.widgetInfo.get(self.type)

        # connect signal: replot with "Data Source"'s analysis button
        self.snare.analyzeBuffer.selectionChanged.connect(self.replotSel)

        # optional parameters
        self.parm1 = None  # f.e. nth Octave
        self.parm2 = None
        self.parm3 = None
        self.initParm()

        self.layout = QVBoxLayout()
        self.setWidget()

    def replotSel(self, channel=None, selNo=None, type='FFT'):
        """
        Replot method triggered by "Editor" Analyze Button.
        Reimport widgetInfo because analyze type could have changed. Also initialize the new widget parameters,
        then refresh.

        :param channel: unique Channelobject
        :type channel: object
        :param selNo: String of selection label
        :type selNo: str
        :param type: Short analyze widget name (f.e. FFT, Hist. ...)
        :type type: str
        """
        if channel is self.channel and selNo == self.selNo:
            # only react to signal for correct channel and selection number
            self.widgetInfo = self.snare.analyses.widgetInfo.get(type)  # change widgetInfo due to type change
            self.initParm()
            print('Replot triggered by "Editor" Analyze Button, type', self.type)
            self.refresh()

    def refreshNav(self, timeWeight=None, fqWeight=None, parm1=None, parm2=None, parm3=None):
        """
        Refresh method triggered from "Analyzer" Navigation Menu.

        :param timeWeight: Time weight slow, fast or impulse
        :type timeWeight: str
        :param fqWeight: Frequency weight A, B, C or Z
        :type fqWeight: str
        :param parm1: optional parameter
        :type parm1: str or int
        :param parm2: optional parameter
        :type parm2: str or int
        :param parm3: optional parameter
        :type parm3: str or int
        """
        self.timeWeight = timeWeight
        self.fqWeight = fqWeight
        self.parm1 = parm1
        self.parm2 = parm2
        self.parm3 = parm3
        print('Refresh triggered by "Analyzer" Navigation', self.type, parm1, parm2, parm3, timeWeight, fqWeight)
        self.refresh()

    def refresh(self):
        """
        General refresh method.
        """
        self.clearLayout(self.layout)
        self.setWidget()

    def setWidget(self):
        filename = self.widgetInfo.get('Filename')
        analyzeClass = self.dynamicClassImport(filename)
        self.currentWidget = analyzeClass(self.snare, self.channel, self.selNo, self.timeWeight, self.fqWeight,
                                          self.parm1, self.parm2, self.parm3)
        self.layout.addWidget(self.currentWidget)
        self.setLayout(self.layout)

        # connect signals
        self.currentWidget.nav.replot.connect(self.refreshNav)
        self.snare.reports.selectAllReports.connect(self.currentWidget.nav.selectReport)
        self.snare.reports.deselectAllReports.connect(self.currentWidget.nav.deselectReport)

    def initParm(self):
        """
        Initialize widget parameter given in Info.txt as constructor variables. If not given initialize with default
        values.
        """
        if 'ParameterFqWeightingInitVal' in self.widgetInfo and not self.fqWeight:
            # if value is set in Info.txt or already initialized
            self.fqWeight = str(self.widgetInfo.get('ParameterFqWeightingInitVal'))
        elif not self.fqWeight:
            # set default init value
            self.fqWeight = 'A'
        if 'ParameterTimeWeightingInitVal' in self.widgetInfo and not self.timeWeight:
            # if value is set in Info.txt or already initialized
            self.timeWeight = str(self.widgetInfo.get('ParameterTimeWeightingInitVal'))
        elif not self.timeWeight:
            # set default init value
            self.timeWeight = 'slow'

        if 'OptParameter1InitVal' in self.widgetInfo and self.parm1 is None or self.parm1 == 'None':
            # parm not already initialized and set in Info.txt
            self.parm1 = self.widgetInfo.get('OptParameter1InitVal')

        if 'OptParameter2InitVal' in self.widgetInfo and self.parm1 is None or self.parm2 == 'None':
            # parm not already initialized and set in Info.txt
            self.parm2 = self.widgetInfo.get('OptParameter2InitVal')

        if 'OptParameter3InitVal' in self.widgetInfo and self.parm1 is None or self.parm3 == 'None':
            # parm not already initialized and set in Info.txt
            self.parm3 = self.widgetInfo.get('OptParameter3InitVal')

    def dynamicClassImport(self, classstr):
        """
        A helper method to import just the needed widget class dynamically depending on current user choice.

        :return: Corresponding class to selected Analyze Widget.
        :rtype: QWidget
        """
        module = importlib.import_module('AnalyzeTools.' + classstr + '.' + classstr)
        return getattr(module, classstr)

    def clearLayout(self, layout):
        """
        Removes all Widgets that are on given layout.

        :param layout: Layout to clear.
        :type layout: QLayout

        """
        while layout.count():
            child = layout.takeAt(0)
            if child.widget() is not None:
                child.widget().deleteLater()
            elif child.layout() is not None:
                self.clearLayout(child.layout())
