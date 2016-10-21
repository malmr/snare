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

import numpy as np
import sys
from EditorUI.TrackAbstract import TrackAbstract


from PyQt5.QtGui import *
from PyQt5.Qt import *

class TrackWaveform(TrackAbstract):

    """
    TrackWaveform takes the currently displayed position of the scene and the zoom-level and requests the corresponding
    waveforms for the area surrounding this position. The creation of the waveform-points list is handled in the backend
    (see WaveformBuffer and WaveformThread) and the results are sent to TrackWaveform through a slot. Requesting and
    receiving waveform-points list is therefore independent or asynchronous. There are several zoom levels for which new
    waveforms will be requested. In between these zoom levels the pixmaps will be stretched to fit instead of a new
    render. Only the currently displayer pixmaps are stored in this object, but all rendered points lists are stored in the
    backend (WaveformBuffer).
    For a detailed overview of the waveform rendering and display, see the overall documentation of SNARE.
    """

    def __init__(self, name, state, selections, analysisTypes, marks, cursorposition, height, width, smptopix, zoom, parent, scene):
        """
        Merely stores initial variables as members and reserves memory for storing pixmaps.

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
        :param scene: A QGraphicsScene in which to place the waveform-pixmaps
        """

        super(TrackWaveform, self).__init__(name, state, selections, analysisTypes, marks, cursorposition, height, width, smptopix, zoom, parent)

        self.scene = scene
        self.height = height-25

        self.lastPos = 0
        self.loadedBlocks = list()

        self.widthPreScaling = width
        self.widthPostScaling = width

        self.counter = 0

    def slo_addWaveform(self, waveform):
        """
        Requested waveforms return after rendering in the backend by means of this slot. The points list itself and all
        information needed to place the pixmap on the right spot with the right size is part of the Waveform-object.
        E.g. if a waveform took too long to render (because the user has already set a new zoom level again) it will
        simply be filtered here and not used.
        The pixmap is either rendered for exactly the requested zoom level or it will be stretched to some extent.

        :param waveform: A Waveform-object containing a pixmap to place on the scene.
        """
        if self.getClosestWaveformZoomLevel() == waveform.dataBlocks or self.getClosestWaveformZoomLevel() == 1/waveform.numberOfPixmaps:
            if self.state == "Recording":
                self.loadedBlocks.append([waveform.startBlock, self.getClosestWaveformZoomLevel()])

            for pixmapNo in range(0, waveform.numberOfPixmaps):
                pixmap = QPixmap(1000, waveform.height)
                pixmap.fill(Qt.transparent)

                painter = QPainter()
                painter.begin(pixmap)
                polygon = QPolygon()
                painter.setPen(Qt.darkBlue)
                polygon.setPoints(waveform.pointsMax[4000*pixmapNo:4000*(pixmapNo+1)])
                painter.drawPolyline(polygon)
                painter.setPen(Qt.blue)
                polygon.setPoints(waveform.pointsRMS[4000*pixmapNo:4000*(pixmapNo+1)])
                painter.drawPolyline(polygon)
                painter.end()

                correctionFactor = self.zoom*self.getClosestWaveformZoomLevel()
                image = pixmap.scaled(1001*correctionFactor, self.height-10, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
                item = self.scene.addPixmap(image)

                scaledSize = 1000*correctionFactor
                offset = scaledSize*((pixmapNo+(waveform.startBlock*waveform.numberOfPixmaps))/waveform.dataBlocks)
                item.setOffset(offset, 0)

    def getClosestWaveformZoomLevel(self):
        """
        Defines the available zoom-levels for pixmaps and returns the one closest to the current actual zoom level.

        :return: closest available zoom level
        """
        waveformZoomLevels = [1/64, 1/8, 1, 4, 16, 32]
        currentZoomLevel = 1/self.zoom

        dist = 1024
        closest = None

        for zoomLevel in waveformZoomLevels:
            if (zoomLevel - currentZoomLevel) <= 0:
                if abs(zoomLevel - currentZoomLevel) < dist:
                    dist = abs(zoomLevel - currentZoomLevel)
                    closest = zoomLevel
        return closest

    def slo_update(self, pos):
        """
        Creates the requests for waveforms to the backend.

        :param pos: Position around which to render
        """
        self.lastPos = pos

        # Imagine the painting area as split into 1000pix wide blocks
        # Now calculate on which block the left corner of the view is currently
        # From there go three blocks in each direction to get the blocks that need to be loaded
        factor = self.width*self.zoom

        startAt = int((pos-(3*self.width))/factor)
        if startAt <= 0:
            startAt = 0
        stopAt = int((pos+3*self.width)/factor)

        # Waveforms are only available in 5 zoom-levels. Find the closest to the current zoom level.
        closestZoomLevel = self.getClosestWaveformZoomLevel()

        blocks = None
        if closestZoomLevel >= 1:
            # e.g. only every 4th block
            blocks = np.arange(startAt, stopAt+1)[0::closestZoomLevel]
        else:
            blocks = np.arange(startAt, stopAt+1)

        if closestZoomLevel >= 1:
            for waveformRequest in blocks:
                startBlock = waveformRequest
                zoomLevel = closestZoomLevel
                if [startBlock, zoomLevel] not in self.loadedBlocks:
                    if not (startBlock % zoomLevel) and startBlock < 120:
                        self.sig_requestWaveform.emit(startBlock, zoomLevel, 1)
                        if self.state == "Playback":
                            self.loadedBlocks.append([startBlock, zoomLevel])
        else:
            for waveformRequest in blocks:
                startBlock = waveformRequest
                zoomLevel = closestZoomLevel
                if [startBlock, zoomLevel] not in self.loadedBlocks:
                    self.sig_requestWaveform.emit(startBlock, 1, 1/zoomLevel)
                    if self.state == "Playback":
                        self.loadedBlocks.append([startBlock, zoomLevel])


    def slo_redraw(self, factor=1):
        """
        A zoom-event will reset the object and trigger a full repaint.
        There is a distinction between the width of a pixmap before scaling, which represents the zoom-levels for which
        a new pixmap will be rendered and the width of a pixmap after scaling, which, if it differs from the width
        before scaling, accounts for a stretching of the pixmap.
        The zoom levels for which new pixmaps will be rendered are defined in this method.

        :param factor: New zoom-factor
        """
        del self.loadedBlocks
        self.loadedBlocks = list()
        self.counter = 0

        self.zoom = factor

        if self.zoom > 0.0025 and self.zoom <= 0.005:
            self.widthPreScaling = self.width * 0.005

        if self.zoom > 0.005 and self.zoom <= 0.01:
            self.widthPreScaling = self.width * 0.01

        elif self.zoom > 0.01 and self.zoom <= 0.02:
            self.widthPreScaling = self.width * 0.02

        elif self.zoom > 0.02 and self.zoom <= 0.05:
            self.widthPreScaling = self.width * 0.05

        elif self.zoom > 0.05 and self.zoom <= 0.1:
            self.widthPreScaling = self.width * 0.1

        elif self.zoom > 0.1 and self.zoom <= 1:
            self.widthPreScaling = self.width * 1

        elif self.zoom > 1 and self.zoom <= 10:
            self.widthPreScaling = self.width * 10

        elif self.zoom > 10:
            self.widthPreScaling = self.width * 100

        self.widthPostScaling = self.width * self.zoom

        self.slo_update(self.lastPos)