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


class ReportObject:
    """
    ReportObject is the base class for the PDF and HTML export objects.
    It handles the generation of the analyses images and the html code assembling (like header, footer, analyse
    widget block).
    """
    def __init__(self, snare, fileName, imgDir):
        """
        Initialize the variables.
        :param snare: Common used variables implenented in MainBackend.
        :type snare: object
        :param fileName: The user input filename
        :type fileName: str
        :param imgDir: The image dir (temporary for PDF export)
        :type imgDir: str
        """
        self.snare = snare
        self.fileName = fileName
        self.now = datetime.datetime.now()
        self.imgDir = imgDir
        self.pages = list()         # List for page HTML strings
        self.imgAbsPaths = list()   # List of absolute paths for all generated images

        self.pageCnt = 0
        self.widgetsOnPage = 0

    def generateImage(self, widget, channelObj, selNo):
        """
        Generate an png file from AnalyseWidget.
        Image path is composed of self.imgDir and an id string.
        :param widget: AnalyzeWidget object
        :type widget: QWidget
        :param channelObj: channel object
        :type channelObj: Obj
        :param sel: Sel No
        :type sel: str
        """
        imgPath = self.imgDir + str(channelObj.getName()) + '_' + selNo + ".png"
        widget.currentWidget.plot.fig.savefig(imgPath)
        self.imgAbsPaths.append(imgPath)

    def deleteImages(self):
        """
        Delete all generated images.
        """
        for img in self.imgAbsPaths:
            os.remove(img)

    def appendAnalyze(self, widget, channel, sel, imgDir=False, width=550):
        """
        Appending the analyse to a html page string.
        self.pages stores the html page strings.

        :param widget: AnalyzeWidget object
        :type widget: QWidget
        :param channel: channel object
        :type channel: Obj
        :param sel: Sel No
        :type sel: str
        :param imgDir: Optional parameter to set the image path to a non absolute path (in case of HTML export)
        :type imgDir: str
        :param width: Optional parameter to set the analyse image width in the html code.
        :type width: int
        """

        if imgDir is False:
            # take absolute path for PDF export
            imgDir = self.imgDir
        imgPath = imgDir + str(channel.getName()) + '_' + sel + ".png"

        self.pages[self.pageCnt] += '<div class ="plot" id="plot-' + str(self.widgetsOnPage) + '">' +\
        widget.currentWidget.titleLabel.text().split('] ')[1] + '''
        </div>
        <p>''' + widget.currentWidget.infoLabel.text() + '''</p>
        <p><img width =\"''' + str(width) + '\" src=\"' + str(imgPath) + '\" ></p>'
        self.widgetsOnPage += 1

    def appendHeader(self):
        """
        Create the page header in a new html page string.
        """
        self.pages.append('''
        <html>
        <body>
        <vertical-align="bottom"><div align="right">p.
        ''' + str(len(self.pages) + 1) + ', ' + self.now.strftime("%Y-%m-%d %H:%M:%S") + '''
        </font></div>
        ''')

    def appendTitle(self, channel):
        """
        Append the widget title to the html page.
        :param channel: channel object
        :type channel: Obj
        """
        self.pages[len(self.pages) - 1] += '''

        <font align="center"><h3>''' + channel.getName() + '''</h3></font>
        '''

    def appendFooter(self):
        """
        Append the widget header to the current html page.
        """
        self.pages[len(self.pages) - 1] += '''
        </body>
        </html>
        '''
