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
from Reports.ReportPdf import ReportPdf
from Reports.ReportHtml import ReportHtml
import os


class ReportManager(QWidget):

    selectAllReports = pyqtSignal()
    deselectAllReports = pyqtSignal()

    def __init__(self, snare):
        """
        Initialize the variables and inherit the QWidget base class.
        :param snare: Common used variables implenented in MainBackend.
        :type snare: object
        """
        super(ReportManager, self).__init__()
        self.snare = snare
        self.activatedReports = defaultdict(lambda: defaultdict(dict))
        self.dirtmp = 'tmp/'
        self.allReportsActivated = False
        self.filename = None

    def state(self, state, channel, selNo):
        """
        Toogle the state of the activated analyse widgets in a 2D list.
        :param state: Bool wheather report is activated or deactivated for widget.
        :type state: bool
        :param channel: channel object
        :type channel: Obj
        :param selNo: Sel No
        :type selNo: str
        """
        if state is True:
            self.activatedReports[channel][selNo] = state
        elif state is False:
            try:
                del self.activatedReports[channel][selNo]
            except:
                pass

    def numOfReports(self):
        """
        Returns the amoungh of activated reports.
        :return: Len of activated reports.
        :rtype: int
        """
        return sum((len(v) for v in self.activatedReports.values()))

    def selectAll(self):
        """
        Emits signal triggered by pressing in report menu 'Select all'.
        """
        self.selectAllReports.emit()

    def deselectAll(self):
        """
        Emits signal triggered by pressing in report menu 'Deselect all'.
        """
        self.deselectAllReports.emit()

    def createReport(self):
        """
        Open a filedialog to select the output file and start the generation.
        """
        if self.numOfReports():
            selFilter = "PDF (*.pdf); html (.html); png (.png)"
            self.filename = QFileDialog.getSaveFileName(self, 'Export Report...', 'Reports/Export.pdf',
                                                        "PDF (*.pdf);;HTML (*.html);;PNG (*.png)", selFilter)
            if self.filename:
                # generate tmp dir
                if not os.path.exists(self.dirtmp):
                    os.makedirs(self.dirtmp)
                if self.filename[0].endswith('.pdf'):
                    print('Generating PDF...')
                    self.generatePdf()
                elif self.filename[0].endswith('.html'):
                    print('Generating HTML...')
                    self.generateHtml()
                elif self.filename[0].endswith('.png'):
                    print('Generating PNG...')
                    self.generatePng()
            print('Export finished.')
        else:
            print("Activate a report first!")
        
    def generatePdf(self):
        """
        Handles the generation and export of the selected analyses to PDF.
        Iterate trough all selected analyses (in first layer through all channels and second layer through all activated
        selections = analyses) and generate the image in a predefined tmp dir (self.dirtmp).
        After generateImage an html string is appended to a page depending list.
        After completly exported the PDF, the tmp dir is cleared.
        """
        report = ReportPdf(self.snare, self.filename[0], self.dirtmp)
        report.startPaint()
        for (channel, channelDict) in self.activatedReports.items():
            # Channel iteration
            for (sel, selDict) in self.activatedReports[channel].items():
                # Analyse widget iteration
                analyze = self.snare.analyses.analysesDict[channel][sel]
                report.generateImage(analyze, channel, sel)
                report.appendAnalyze(analyze, channel, sel)
            # finish and paint channel page
            report.appendFooter()
            report.PaintPage(report.pageCnt)
            if report.pageCnt < len(self.activatedReports):
                report.newPage()  # create new page but not on last iteration
            report.widgetsOnPage = 0  # reset widgetOnPage counter

        report.finishPaint()
        report.deleteImages()

    def generateHtml(self):
        """
        Handles the generation and export of the selected analyses to HTML.
        Iterate trough all selected analyses (in first layer through all channels and second layer through all activated
        selections = analyses) and generate the image in a subfolder defined with 'imgDirRel'. After each generation
        an analyse html block is generated and appended to an page string.
        In exportHtml the html blocks are summed up and exported in one .html file.
        """
        filename = self.filename[0]
        imgDirRel = 'analyses/'
        imgDir = os.path.dirname(filename) + '/' + imgDirRel
        if not os.path.exists(imgDir):
            os.makedirs(imgDir)
        report = ReportHtml(self.snare, filename, imgDir)
        for (channel, channelDict) in self.activatedReports.items():
            for (sel, selDict) in self.activatedReports[channel].items():
                analyze = self.snare.analyses.analysesDict[channel][sel]
                report.generateImage(analyze, channel, sel)
                report.appendAnalyze(analyze, channel, sel, imgDirRel)
        report.appendFooter()
        report.exportHtml()

    def generatePng(self):
        """
        Handles the generation and export of the selected analyses to PNG.Depending if one analyse is selected or
        several, it exports the file either to the user input filename or to dynamically generated filenames.
        Iterating trough all selected analyses (in first layer through all channels and second layer through all
        activated selections = analyses) and generate the image in a subfolder defined with 'imgDirRel'. After each
        generation an analyse html block is generated and appended to an page string.
        In exportHtml the html blocks are summed up and exported in one .html file.
        """
        filename = self.filename[0]
        imgDir = os.path.dirname(filename) + '/'
        if not os.path.exists(imgDir):
            os.makedirs(imgDir)
        report = ReportHtml(self.snare, filename, imgDir)

        for (channel, channelDict) in self.activatedReports.items():
            for (sel, selDict) in self.activatedReports[channel].items():
                analyze = self.snare.analyses.analysesDict[channel][sel]
                if self.numOfReports() == 1:
                    analyze.currentWidget.plot.fig.savefig(filename)  # safe one file with user dialog input
                else:
                    report.imgDir = imgDir + os.path.basename(filename) + '_'
                    report.generateImage(analyze, channel, sel)  # save several files with dynamic filenames
