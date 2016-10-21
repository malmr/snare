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
import datetime
import os
from Reports.ReportObject import ReportObject


class ReportHtml(ReportObject):
    """
    The PDF report object handles the generation of the analyses images,
    """
    def __init__(self, snare, fileName, imgDir):
        """
        Initialize the variables and inherit the QWidget base class.
        :param snare: Common used variables implenented in MainBackend.
        :type snare: object
        :param fileName: The user input filename
        :type fileName: str
        :param imgDir: The image dir (not temporary for HTML export)
        :type imgDir: str
        """
        super(ReportHtml, self).__init__(snare, fileName, imgDir)
        self.appendHeader()

    def appendAnalyze(self, widget, channel, sel, imgDir):
        # modify appendAnalyze method to create a new pdf page every 3rd widget per channel:
        self.appendTitle(channel)
        super().appendAnalyze(widget, channel, sel, imgDir, width=1000)

    def exportHtml(self):
        text_file = open(self.fileName, "w")
        for page in self.pages:
            text_file.write(page)
        text_file.close()