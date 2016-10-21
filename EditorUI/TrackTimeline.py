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
from PyQt5.QtGui import *

from EditorUI.TrackAbstract import TrackAbstract

class TrackTimeline(TrackAbstract):

    """
    TrackTimeline adds a equidistant vertical lines to the waveform view and appends time strings to them. This allows
    for an easier navigation through the audio data. It needs to be stacked on top of a TrackView object to have the
    extended interface containing a scene. The drawing process works in a similar way to TrackWaveform and
    TrackTimeline.
    """

    def __init__(self, name, state, selections, analysisTypes, marks, cursorposition, height, width, smptopix, zoom, parent, scene):
        """
        Merely stores initial variables as members and draws a line at the origin.

        :param name: Name assigned to this track
        :param state: Lock-state on creation
        :param selections: Initial list of selection names
        :param analysisTypes: Initial list of analysis types
        :param marks: Initial list of marks on the time axis. Not relevant here.
        :param cursorposition: Initial cursor position. Not relevant here.
        :param height: Dimensions available for the entire track.
        :param width:  Dimensions available for the entire track.
        :param smptopix: Conversion factor, how many samples are displayed as one pixel. (At zoom-factor 1)
        :param zoom: Initial zoom-factor
        :param parent: The object on top of which this object is stacked in the layer structure.
        :param scene: A QGraphicsScene in which to draw the lines and text.
        """
        super(TrackTimeline, self).__init__(name, state, selections, analysisTypes, marks, cursorposition, height, width, smptopix, zoom, parent)

        self.scene = scene
        self.zoom = zoom

        self.lastPos = 0
        self.paintedBlocks = dict()

    def paintBlock(self, block):
        """
        Draws 10 lines per block and then appends a text on the bottom of each line to display the time.

        :param block: Number of block to paint.
        """
        self.paintedBlocks[block] = True

        self.pixmap = QPixmap(self.width, self.height-5)
        self.pixmap.fill(Qt.transparent)
        painter = QPainter(self.pixmap)
        painter.setPen(Qt.lightGray)

        lines = list()
        for n in range(10):
            x = n*(self.width/10)
            lines.append(QLineF(x, 0, x, self.height-15))
            pos = (n+block*10)/self.zoom
            text = self.formatTag(pos)
            painter.drawStaticText(QPointF(x + 2, self.height-20), QStaticText(text))
        painter.drawLines(lines)
        item = self.scene.addPixmap(self.pixmap)
        item.setOffset(block * self.width, 0)

    def formatTag(self, pos):
        """
        Calculates the time for the requested position and formats it according to a set of rules about units and
        rounding.

        :param pos: Position to calculate time at
        :return: a formatted string containing the time e.g. "1:20 + 20ms"
        """
        if self.zoom <= 0.3:
            min = str(int(pos/60))
            sec = str(int(pos%60))
            if int(pos%60) < 10:
                sec = "0" + sec
            text = min + ":" + sec
        else:
            min = str(int(pos/60))
            sec = str(int(pos%60))
            msc = pos - int(pos)
            msc = round(msc, 3)
            msc = int(msc*1000)
            text = min + ":" + sec + "+" + str(msc) + "ms"
        return text


    def slo_update(self, pos):
        """
        The class treats the painting area as divided into blocks. From the given position the next three blocks in each
        direction are calculated. Then if a block has not been already painted, it will be painted. This way only the
        visible portion of the scene has to be painted.

        :param pos: position in pixels around which to paint blocks.
        """
        self.lastPos = pos
        forward = pos + 3 * self.width
        backward = pos - 3 * self.width
        if backward < 0:
            backward = 0
        widthPostScaling = self.width * self.zoom
        forwardBlocks = int(forward//widthPostScaling)+1
        backwardBlocks = int(backward//widthPostScaling)

        for block in range(backwardBlocks, forwardBlocks):
            try:
                self.paintedBlocks[block]
            except KeyError:
                self.paintBlock(block)

    def slo_redraw(self, factor=1):
        """
        A zoom-event will reset the object and trigger a full repaint.

        :param factor: New zoom-factor
        """
        self.zoom = factor
        del self.paintedBlocks
        self.paintedBlocks = dict()
        self.slo_update(self.lastPos)