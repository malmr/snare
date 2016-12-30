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

from PyQt5.Qt import *
from collections import defaultdict
import pandas as pd


class AnalyzeManager(QObject):

    """
    AnalyzeManager handles the main analyze methods like adding and deleting a widget. It contains the active widgets
    in an 2D dictionary depending on the channel. As well as a channel depending boolean dictionary with the activated
    reports. All widget information which is dynamically imported at startup ("Info.txt") is also stored in this class.
    """

    removeAnalysis = pyqtSignal(QWidget)

    def __init__(self, snare, analysesFullPaths):
        """
        Initialize the 2D dictionaries and full paths list.

        :param snare: Common used variables implenented in MainBackend.
        :type snare: object
        :param analysesFullPaths: List of paths to all widgets.
        :type analysesFullPaths: list
        """
        super(AnalyzeManager, self).__init__()
        self.snare = snare
        self.widgetPaths = analysesFullPaths                        # Full Path to Widgets
        self.widgetInfo = dict()                                    # 2D dict contains Info.txt dict for every Widget
        self.analysesDict = defaultdict(lambda: defaultdict(dict))  # contains active Analyses [channelInstance][selNo]
        self.activatedReports = defaultdict(lambda: defaultdict(dict))
        self.widgetsactive = 0

        # To change between dynamic and static import:
        #(un-)comment this block and the block in MainBackend.
        #
        # <-- dynamic import
        # reading Info.txt of every AnalyzeWidgets
        # for i in range(len(self.widgetPaths)):
        #     pdframe = self.readWidgetInfo(self.widgetPaths[i])
        #     widgetname = pdframe['values'].get('ShortName')
        #     widgetdict = {widgetname:pdframe['values'].to_dict()}
        #     self.widgetInfo.update(widgetdict)
        #     print('Imported ' + self.widgetInfo.get(widgetname).get('ShortName') + ' Widget.')
        #
        # Example usage: print(self.widgetInfo.get('FFT').get('ShortName'))
        # dynamic import -->

        #
        # <-- static import
        staticDic = {'ShortName': 'Example',
                     'Filename': 'WidgetExample',
                     'OptParameter1': 'None',
                     'OptParameter1InitVal': 'None',
                     'OptParameter2': 'None',
                     'OptParameter2InitVal': 'None',
                     'OptParameter3': 'None',
                     'OptParameter3InitVal': 'None',
                     'ParameterFqWeightingInitVal': 'Z',
                     'ParameterTimeWeightingInitVal': 'impulse'}
        widgetname = 'Example'
        widgetdict = {widgetname: staticDic}
        self.widgetInfo.update(widgetdict)
        print('Imported ' + self.widgetInfo.get(widgetname).get('ShortName') + ' Widget.')

        staticDic = {'ShortName': 'FFT',
                     'Filename': 'WidgetFft',
                     'OptParameter1': 'nthfft',
                     'OptParameter1InitVal': '3',
                     'OptParameter2': 'None',
                     'OptParameter2InitVal': 'None',
                     'OptParameter3': 'None',
                     'OptParameter3InitVal': 'None'}
        widgetname = 'FFT'
        widgetdict = {widgetname: staticDic}
        self.widgetInfo.update(widgetdict)
        print('Imported ' + self.widgetInfo.get(widgetname).get('ShortName') + ' Widget.')

        staticDic = {'ShortName': 'Hist.',
                     'Filename': 'WidgetHistogram',
                     'OptParameter1': 'None',
                     'OptParameter1InitVal': 'None',
                     'OptParameter2': 'None',
                     'OptParameter2InitVal': 'None',
                     'OptParameter3': 'None',
                     'OptParameter3InitVal': 'None',
                     'ParameterFqWeightingInitVal': 'Z',
                     'ParameterTimeWeightingInitVal': 'impulse'}
        widgetname = 'Hist.'
        widgetdict = {widgetname: staticDic}
        self.widgetInfo.update(widgetdict)
        print('Imported ' + self.widgetInfo.get(widgetname).get('ShortName') + ' Widget.')

        staticDic = {'ShortName': 'SPL',
                     'Filename': 'WidgetSpl',
                     'OptParameter1': 'None',
                     'OptParameter1InitVal': 'None',
                     'OptParameter2': 'None',
                     'OptParameter2InitVal': 'None',
                     'OptParameter3': 'None',
                     'OptParameter3InitVal': 'None'}
        widgetname = 'SPL'
        widgetdict = {widgetname: staticDic}
        self.widgetInfo.update(widgetdict)
        print('Imported ' + self.widgetInfo.get(widgetname).get('ShortName') + ' Widget.')
    # static import -->


    def addWidget(self, analysis, channel, selNo):
        """
        Adds Analyze to Analyze mapping.

        :param analysis: Analyze
        :type analysis: QWidget
        :param channel: unique Channelobject
        :type channel: Object
        :param selNo: String of selection label
        :type selNo: str
        """
        self.widgetsactive += 1
        self.analysesDict[channel][selNo] = analysis
        self.snare.updateAnalysesStatus.emit(self.getStatusBarString())

    def deleteWidget(self, channel, selNo):
        """
        Delete Analyze from Analyze mapping.

        :param channel: unique Channelobject
        :type channel: object
        :param selNo: String of selection label
        :type selNo: str
        """
        self.widgetsactive -= 1
        widget = self.snare.analyses.analysesDict[channel][selNo]
        # disconnect signals
        self.snare.analyzeBuffer.selectionChanged.disconnect(widget.replotSel)
        self.snare.analyzeBuffer.selectionExists[channel][selNo] = False  # for correct SelChanged / NewSel signal
        self.snare.reports.state(False, channel, selNo)  # delete
        self.snare.updateAnalysesStatus.emit(self.getStatusBarString())
        widget.setParent(None)
        self.removeAnalysis.emit(widget)

    def readWidgetInfo(self, path):
        """
        Read the Widget information and parameters from Info.txt.

        :param path: path to Widget Info.txt
        :type path: str
        :return: DataFrame with the imported Widget information
        :rtype: panda DataFrame
        """
        return pd.DataFrame(pd.read_csv(path + '/Info.txt', sep=': ', index_col=0, header=2, engine='python'))

    def listAnalyzeTypes(self):
        """
        List all imported Analyses as a list.

        :return: List of all AnalyzeWidgets
        :rtype: list
        """
        # <-- static import
        # analyzeList = ['Example', 'FFT', 'Histogram', 'Spl']
        # -->
        analyzeList = list(self.widgetInfo.keys())
        analyzeList.sort()
        return analyzeList

    def getStatusBarString(self):
        """
        Returns a string for the Status Bar with analyse depending information.
        :return: string with AnalyzeWidget information
        :rtype: str
        """
        return str(len(self.widgetInfo)) + ' Widgets imported.  ' + str(self.widgetsactive) + ' Analyses active.'
