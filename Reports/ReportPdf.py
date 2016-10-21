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
from PyQt5.Qt import *
from PyQt5.QtGui import *
from PyQt5.QtPrintSupport import *
from PyQt5.QtCore import *
from Reports.ReportObject import ReportObject


class ReportPdf(ReportObject):
    """
    The PDF report object handles the generation of the analyses images and the PDF painting.
    """
    def __init__(self, snare, fileName, imgDir):
        """
        Initialize the variables and inherit the QWidget base class.
        :param snare: Common used variables implenented in MainBackend.
        :type snare: object
        :param fileName: The user input filename
        :type fileName: str
        :param imgDir: The image dir (temporary for PDF export)
        :type imgDir: str
        """
        self.printer = None
        self.painter = None
        self.doc = QTextDocument()
        super(ReportPdf, self).__init__(snare, fileName, imgDir)

    def startPaint(self):
        """
        Set the QPrinter device and starts the painting of the PDF file.
        """
        self.printer = QPrinter(QPrinter.HighResolution)
        self.printer.setOutputFileName(self.fileName)
        self.printer.setPageSize(QPrinter.A4)
        self.printer.setColorMode(QPrinter.Color)
        self.printer.setOutputFormat(QPrinter.PdfFormat)

        # Create a QPainter to draw widgets
        self.painter = QPainter()
        self.painter.begin(self.printer)
        self.doc.documentLayout().setPaintDevice(self.printer)
        self.doc.setPageSize(QSizeF(self.printer.pageRect().size()))
        self.doc.setDefaultStyleSheet(
            '''
            body {color: black;}
            .plot{background-color:grey;
            position:absolute;margin-top:0px;}
            ''')

    def finishPaint(self):
        """
        Stop the QPrinter painting.
        """
        if self.painter:
            self.painter.end()

    def appendAnalyze(self, widget, channel, sel):
        """
        Modify appendAnalyze method from baseclass to create new pdf pages every 3rd widget per channel.
        :param widget: AnalyzeWidget object
        :type widget: QWidget
        :param channel: channel object
        :type channel: Obj
        :param sel: Sel No
        :type sel: str
        """
        if (not self.widgetsOnPage % 3) and self.widgetsOnPage != 0:
            # create a new page every 3rd widget per channel
            self.appendFooter()
            self.PaintPage(self.pageCnt)
            self.newPage()
            self.appendHeader()
            self.appendTitle(channel)
        else:
            # create the header
            self.appendHeader()
            self.appendTitle(channel)
        super().appendAnalyze(widget, channel, sel)

    def newPage(self):
        """
        Print new page.
        """
        self.printer.newPage()
    
    def PaintPage(self, page):
        """
        Paint given page to PDF print device.
        """
        self.doc.setHtml(self.pages[page])
        self.doc.drawContents(self.painter)
        self.pageCnt += 1
        self.widgetsOnPage = 0
