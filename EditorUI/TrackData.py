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

class TrackData():

    """
    All data collected trough the Track User Interface will be stored here. This allows for easier communication with
    other backend objects. The TrackManager stores all invisible data in here (e.g. selections that are currently not
    active) and loads it back from here when needed (e.g. going back to a previously edited selection)
    Since everything relevant to the state of one track is concentrated in this class, it'll make it easier to implement
    a save/load feature in future releases.

    The full set of data for one track includes:
        - last cursor position
        - all selections, with start/end points, name, analysis type and lock state
        - all marks on the timeline
        - reference to the backend-channel it is connected to
        - reference to the user interface element
    """

    def __init__(self, selectionNames, analysisTypes, channel, track):
        """
        The constructor contains the usual python-boilerplate to store parameters and sets up a data structure for
        storing selections (with name, type and points)

        :param selectionNames: Initial list of selection names. Data structure is created for each.
        :param analysisTypes: Initial list of all analysis types available. Only first one is used for setting a
        default.
        :param channel: The channel object to associate the track with.
        :param track: A reference to the corresponding user interface object.
        """

        self.channel = channel
        self.track = track
        self.analysisTypes = analysisTypes
        self.smp = 0
        self.selections = dict()
        self.playbackState = False
        for selectionName in selectionNames:
            selection = dict()
            selection["points"] = dict()
            selection["analysisType"] = analysisTypes[0]
            selection["state"] = "Idle"
            self.selections[selectionName] = selection

        self.currentSelectionName = selectionNames[-1]

        self.marks = list()

    def isPlaying(self):
        """
        Inform caller of this channel's playback state.

        :return: Bool, True if channel is on playback.
        """
        return self.playbackState

    def setPlaying(self, bool):
        """
        Remember if this channel is on playback.

        :param bool: True if playback is on
        """
        self.playbackState = bool

    def addSelection(self, selectionName):
        """
        Prepares the data structure for an additional selection.

        :param selectionName: Name of the selection. Must be unique.
        """
        selection = dict()
        selection["points"] = dict()
        selection["analysisType"] = self.analysisTypes[0]
        selection["state"] = "Idle"
        self.selections[selectionName] = selection

    def getCurrentSelection(self):
        """
        Interface for the TrackManager to load back a selection.

        :return: a tuple of four elements containing the name, points, lock-state and the analysis type of the selection
        """
        points = self.selections[self.currentSelectionName]["points"]
        state = self.selections[self.currentSelectionName]["state"]
        analysisType = self.selections[self.currentSelectionName]["analysisType"]
        return [self.currentSelectionName, points, state, analysisType]

    def updateCurrentSelection(self, points, state=None, analysisType=None):
        """
        Stores adjustments made to the current selection. E.g. when the analysis type has been changed or the selection
        area (in start/end-points)

        :param points: Updated list of start and end samples of the selection areas
        :param state: Updated lock-state
        :param analysisType: Updated analysis type
        """
        self.selections[self.currentSelectionName]["points"] = points
        if state is not None:
            self.selections[self.currentSelectionName]["state"] = state
        if analysisType is not None:
            self.selections[self.currentSelectionName]["analysisType"] = analysisType

    def setCurrentSelection(self, selectionName):
        """
        Simple setter method.

        :param selectionName: Name of the selection to switch to. Must exist, otherwise untreated KeyError exceptions
          occur.
        """
        self.currentSelectionName = selectionName

    def getLastPos(self):
        """
        Simple getter method.

        :return: The last stored cursor position in samples.
        """
        return self.smp

    def setLastPos(self, smp):
        """
        Simple setter method.

        :param smp: Update the last cursor position to this in samples.
        """
        self.smp = smp

    def setMark(self, smp):
        """
        Adds a mark to the list. Deleting of marks not yet available.

        :param smp: Position of the mark in samples
        """
        self.marks.append(smp)

    def getNextMark(self, smp):
        """
        Allow jumping forward from one position to the nearest mark.

        :param smp: position in samples from which to look for the next mark
        :return: sample position of the nearest mark in forward direction.
        """
        for mark in sorted(self.marks):
            if mark > smp:
                return mark
        return smp

    def getPreviousMark(self, smp):
        """
        Allow jumping backward from one position to the nearest mark.

        :param smp: position in samples from which to look for the next mark
        :return: sample position of the nearest mark in backward direction.
        """
        for mark in sorted(self.marks, reverse=True):
            if mark < smp:
                return mark
        return smp