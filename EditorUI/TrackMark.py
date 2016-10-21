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

class TrackMark(TrackAbstract):

    """
    TrackMark draws red, dotted, vertical lines on the scene to mark position that the user selected by pressing "M". It
    needs to be stacked on top of a TrackView object to have the extended interface containing a scene.
    The drawing process works in a similar way to TrackWaveform and TrackTimeline. See slo_update.
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
        :param scene: A QGraphicsScene in which to draw the marks.
        """
        super(TrackMark, self).__init__(name, state, selections, analysisTypes, marks, cursorposition, height, width, smptopix, zoom, parent)

        self.scene = scene

        self.lastPos = 0
        self.paintedBlocks = dict()

        self.marks = list()

    def slo_setMark(self, smp):
        """
        Slot to set a mark at the specified position. After storing the position, the pixmap will be renewed.

        :param smp: Position in samples, converted automatically to the actual pixel/on-screen position
        """
        self.marks.append(smp)
        del self.paintedBlocks
        self.paintedBlocks = dict()
        self.slo_update(self.lastPos)

    def paintBlock(self, block):
        """
        Evaluates which marks are inside the requested block and draws them as QLineF on the scene.

        :param block: Number of the block to paint.
        """
        self.paintedBlocks[block] = True

        self.pixmap = QPixmap(self.width, self.height)
        self.pixmap.fill(Qt.transparent)

        painter = QPainter(self.pixmap)

        pen = QPen()
        pen.setDashPattern([2,3])
        pen.setColor(Qt.red)
        pen.setWidth(1.5)

        painter.setPen(pen)

        lines = list()

        for mark in self.marks:
            x = mark / self.smptopix
            x = x * self.zoom

            if block*self.width < x and (block+1)*self.width >= x:
                    xInBlock = x - (block*self.width)
                    line = QLineF(xInBlock, 0, xInBlock, self.height)
                    lines.append(line)

            painter.drawLines(lines)

            item = self.scene.addPixmap(self.pixmap)
            item.setOffset(block * self.width, 0)

    def slo_update(self, pos):
        """
        The class treats the painting area as divided into blocks. From the given position the next three blocks in each
        direction are calculated. Then, if a block has not been already painted, it will be painted. This way only the
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