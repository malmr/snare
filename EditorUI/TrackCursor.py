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

from PyQt5.QtGui import *

from EditorUI.TrackAbstract import TrackAbstract


class TrackCursor(TrackAbstract):

    """
    TrackCursor draws a vertical line on the scene to mark the current position of playback on the timeline. It needs to
    be stacked on top of a TrackView object to have the extended interface containing a scene.
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
        :param scene: A QGraphicsScene in which to draw the cursor/line.
        """
        super(TrackCursor, self).__init__(name, state, selections, analysisTypes, marks, cursorposition, height, width, smptopix, zoom, parent)
        self.smp = 0
        self.scene = scene
        self.factor = zoom
        self.cursor = scene.addLine(0, 0, 0, height, QPen())

    def setCursor(self, smp):
        """
        Public. The only way to set the cursor position is from outside.

        :param smp: Requested cursor position in samples. Automatic conversion from samples to the actual position in pixels on screen
        """
        self.smp = smp
        pos = smp/self.smptopix
        self.cursor.setX(pos*self.factor)

    def slo_redraw(self, factor=1):
        """
        Adjusting the cursor position whenever the zoom-level changes.

        :param factor: The new zoom-factor
        """
        self.factor = factor
        self.cursor = self.scene.addLine(0, 0, 0, self.height, QPen())
        self.setCursor(self.smp)
