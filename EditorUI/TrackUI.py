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

from EditorUI.TrackAbstract import TrackAbstract
from EditorUI.TrackButtons import TrackButtons
from EditorUI.TrackView import TrackView

class TrackUI(TrackAbstract):

    """
    The TrackUI forms the bottom layer of one channel strip user interface element. It combines the TrackButtons and
    the waveform viewer (TrackWaveform) to one row with a QHBoxLayout. Apart from its layout functionality it
    relays the interface to its child objects.
    """

    def __init__(self, name, state, selections, analysisTypes, marks, cursorposition, height, width, smptopix, zoom, parent=None):
        """
        The constructor of this class creates the child objects and stores some parameter data as member attributes.

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
        """
        super(TrackUI, self).__init__(name, state, selections, analysisTypes, marks, cursorposition, height, width, smptopix, zoom, parent)

        self.layout = QHBoxLayout()

        self.buttons = TrackButtons(name, state, selections, analysisTypes, marks, cursorposition, height, width, smptopix, zoom, self)
        self.layout.addWidget(self.buttons)

        self.view = TrackView(name, state, selections, analysisTypes, marks, cursorposition, height, width, smptopix, zoom, self)
        self.layout.addWidget(self.view.widget)

        self.lastSelectionName = selections[-1]
        self.lastAnalysisType = analysisTypes[-1]
        self.lastSelection = dict()

        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setAlignment(Qt.AlignLeft)
        self.setLayout(self.layout)
        self.show()

    # Relaying not automated signal lines

    def setView(self, QRectF):
        """
        Relay to TrackView

        :param QRectF: see TrackView
        """
        self.view.setView(QRectF)

    def setCursor(self, smp):
        """
        Relay to TrackView

        :param smp: see TrackView
        """
        self.view.setCursor(smp)

    def enableScrollbar(self, bool):
        """
        Relay to TrackView

        :param bool: see TrackView
        """
        self.view.enableScrollbar(bool)

    def enableDrag(self, bool):
        """
        Relay to TrackView

        :param bool: see TrackView
        """
        self.view.enableDrag(bool)

    def getSelectionPoints(self):
        """
        Relay to TrackView
        """
        return self.view.getSelectionPoints()
