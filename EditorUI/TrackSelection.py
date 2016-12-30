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

class TrackSelection(TrackAbstract):

    """
    TrackSelection provides an intuitive way for the user to select areas in the waveform view. The user can simply draw
    by holding the left mouse button a green rectangle, which is added to the selection or by holding the right mouse
    button a red rectangle, which is subtracted from the existing selection area (where there is an intersection)
    The Object needs to be stacked on top of a TrackView object to have the extended interface containing a scene.

    The implementation models the desired behaviour with a state machine. State transitions are triggered by several
    control slots.
    """

    def __init__(self, name, state, selections, analysisTypes, marks, cursorposition, height, width, smptopix, zoom, parent, scene):
        """
        Constructor with usual python-boilerplate, defining paint devices and initialising the state machine to "Idle"

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
        :param scene: A QGraphicsScene in which to draw the selection rectangles.
        """

        super(TrackSelection, self).__init__(name, state, selections, analysisTypes, marks, cursorposition, height, width, smptopix, zoom, parent)

        self.scene = scene
        self.height -= 20 # Offset to not cover time strings

        # Paint Devices
        self.opaqueGreen = QColor(0,255,0,127)
        self.selectBrush = QBrush(self.opaqueGreen)
        self.opaqueRed = QColor(255,0,0,127)
        self.deselectBrush = QBrush(self.opaqueRed)
        self.opaqueBlue = QColor(0,0,255,127)
        self.selectionBrush = QBrush(self.opaqueBlue)

        # List of start/end-points
        # Always scaled with blocksize to waveformWidth
        self.points = dict()
        # List of rectangle-objects/selection-areas
        self.areas = list()

        # This is a state machine, defining inital state
        self.state = "Idle"
        self.selectionStart = None
        self.selectionEnd = None
        self.type = None

    # CONTROL SLOTS

    def slo_startSelection(self, QGraphicsSceneMouseEvent):
        """
        Control Slot. Triggers transition from "Idle" to "Start". Determines the selection type (Add to or subtract from
        selection) by the mouse button pressed and also send the position where the user pressed.

        :param QGraphicsSceneMouseEvent: Qt-type from which to get the pressed mouse button and mouse position on the scene.
        """
        type = None
        button = QGraphicsSceneMouseEvent.button()

        if button == Qt.LeftButton:
            type = "Add"
            x = QGraphicsSceneMouseEvent.buttonDownScenePos(Qt.LeftButton).x()
            if self.state == "Idle":
                self.IdleToStart(x, type)
        elif button == Qt.RightButton:
            type = "Remove"
            x = QGraphicsSceneMouseEvent.buttonDownScenePos(Qt.RightButton).x()
            if self.state == "Idle":
                self.IdleToStart(x, type)

    def slo_endSelection(self, QGraphicsSceneMouseEvent):
        """
        Control Slot. Triggers transition from "Move" to "End" or "Start" to "Idle" if no mouse movement happened since
        the button was pressed.

        :param QGraphicsSceneMouseEvent: Qt-type from which to get the mouse position on the scene.
        """
        x = QGraphicsSceneMouseEvent.scenePos().x()
        if self.state == "Move":
            self.MoveToEnd(x)
        if self.state == "Start":
            self.StartToIdle()

    def slo_moveSelection(self, QGraphicsSceneMouseEvent):
        """
        Control Slot. Trigger transition from "Move" to "Move" or "Start" to "Move".
        This models the dragging of the rectangle size.

        :param QGraphicsSceneMouseEvent:
        """
        x = QGraphicsSceneMouseEvent.scenePos().x()
        if self.state == "Start":
            self.StartToMove(x)
        if self.state == "Move":
            self.MoveToMove(x)

    def slo_enableSelection(self, bool):
        """
        Control Slot. Trigger transition from "Finish" to "Idle" or "Idle" to "Finish". This transition enables the user
        to block the selection from unwanted changes.

        :param bool: Set blocked or not.
        """
        if bool:
            if self.state == "Blocked":
                self.FinishToIdle()
        else:
            if self.state == "Idle":
                self.IdleToFinish()

    # PUBLIC INTERFACE

    def getSelectionPoints(self):
        """
        Getter method.

        :return: A tuple of two elements: start and end points of selection areas and lock-state of the selection
        """
        return [self.points, self.state]

    def slo_setSelection(self, selectionName, analysisType, selection):
        """
        Replace the current selection.

        :param selectionName: Name of the new selection. Not relevant here. See TrackButtons for other end of this command chain
        :param analysisType: Type of analysis of the new selection. Not relevant here.
        :param selection: Start and end points of selection areas of new selection
        """

        self.points = selection
        self.updateSelection()

    def slo_redraw(self, factor):
        """
        Removes all selection rectangels and redraws them after setting the new zoom-level.

        :param factor: The new zoom-level
        """
        self.zoom = factor
        self.areas.clear()
        self.redrawSelection()

    #State transitions

    def IdleToStart(self, x, type):
        """
        State transition. Starts the rectangle by defining the type and start point.

        :param x: Position of start
        :param type: "Add" or "Remove" type of selection rectangle
        """
        self.type = type
        self.selectionStart = x
        self.state = "Start"

    def StartToIdle(self):
        """
        State transition. Returns the machine to "Idle" state when no movement has occurred to draw a rectangle
        """
        self.selectionStart = None
        self.state = "Idle"

    def StartToMove(self, x):
        """
        State transition. After the start point has been set, now after one mouse move event, an provisional end point
        is known, which is enough to draw the rectangle for the first time. The type has been set by a previous
        transition.

        :param x: Position of the provisional end point.
        """
        self.selectionEnd = x

        if self.type == "Remove":
            self.area = self.scene.addRect(self.selectionStart, 0, self.selectionEnd-self.selectionStart, self.height, QPen(), self.deselectBrush)

        if self.type == "Add":
            self.area = self.scene.addRect(self.selectionStart, 0, self.selectionEnd-self.selectionStart, self.height, QPen(), self.selectBrush)

        self.scene.update()
        self.state = "Move"

    def MoveToMove(self, x):
        """
        State transition. Updates the provisional end point of the rectangle for each mouse move event. Also redraws
        the rectangle accordingly.

        :param x: Updated position of the provisional end point.
        """
        self.selectionEnd = x
        self.area.setRect(self.selectionStart, 0, self.selectionEnd - self.selectionStart, self.height)
        self.scene.update()
        self.state = "Move"

    def MoveToEnd(self, x):
        """
        State transition. Triggered by releasing the mouse button. The last provisional end point of the selection
        becomes a definite one. Subsequently the fully defined input rectangle will be processed to intersect with
        the existing selection rectangles and sets the machine to the "End" state.

        :param x: Last position of the end point.
        """
        start = None
        end = None
        # Account for negative values (Selecting from right to left)
        if self.selectionEnd >  self.selectionStart:
            start = self.selectionStart
            end = self.selectionEnd
        else:
            start = self.selectionEnd
            end = self.selectionStart

        self.addSelection(start, end, self.type)

        self.scene.removeItem(self.area)
        self.scene.update()

        self.state = "End"
        self.EndToIdle()

    def EndToIdle(self):
        """
        State transition. Cleaning up variables and returning the machine to the "Idle" state.
        """
        self.selectionStart = None
        self.selectionEnd = None
        self.state = "Idle"

    def IdleToFinish(self):
        """
        State transition. Setting the machine to the blocked state. The selection will be marked as blocked by applying
        a pattern. It will not respond to any mouse input until set back to "Idle"
        """
        self.selectionBrush = QBrush(self.opaqueBlue, Qt.DiagCrossPattern)
        self.updateSelection()
        self.state = "Blocked"

    def FinishToIdle(self):
        """
        State transition. Returning from the "Blocked" state to the "Idle" state. The cross pattern of the selection
        will be removed.
        """
        self.selectionBrush = QBrush(self.opaqueBlue)
        self.updateSelection()
        self.state = "Idle"

    # PRIVATE

    def addSelection(self, start, end, type):
        """
        This processes the rectangle drawn by the user to intersect with the existing selection areas.
        For an explanation on the intersect-algorithm, see the overall documentation of SNARE.

        :param start: Start point of the rectangle, already sorted to be the smaller number.
        :param end: End point of the rectangle, already sorted to be the bigger number
        :param type: "Add" or "Remove" from existing selection areas.
        """
        sampleStart = start*(self.smptopix / self.zoom)
        sampleEnd = end*(self.smptopix / self.zoom)
        sampleBefore = None
        sampleAfter = None

        if not sampleStart == sampleEnd:
            for sample in sorted(self.points):
                if sample < sampleStart:
                    sampleBefore = self.points[sample]
                    if sample == sampleStart:
                        sampleStart += 1
                elif sample >= sampleEnd:
                    sampleAfter = self.points[sample]
                    if sample == sampleEnd:
                        sampleEnd += 1
                    break
                else:
                    del self.points[sample]

            # Condition List
            if type is "Add":
                if sampleBefore is "start":
                    pass
                if sampleBefore is "end" or sampleBefore is None:
                    self.points[sampleStart] = "start"
                if sampleAfter is "start" or sampleAfter is None:
                    self.points[sampleEnd] = "end"
                if sampleAfter is "end":
                    pass
            elif type is "Remove":
                if sampleBefore is "start":
                    self.points[sampleStart] = "end"
                if sampleBefore is "end" or sampleBefore is None:
                    pass
                if sampleAfter is "start" or sampleAfter is None:
                    pass
                if sampleAfter is "end":
                    self.points[sampleEnd] = "start"

            self.updateSelection()

    def updateSelection(self):
        """
        Cleans up all selection areas in the objects list as well as the painted objects on the scene. Subsequently
        triggers a redraw.
        """
        for n in range(len(self.areas)):
            self.scene.removeItem(self.areas[n])
        self.areas.clear()
        self.redrawSelection()

    def redrawSelection(self):
        """
        After the points list has been conditioned by addSelection to be meaningful an alternate series of start and end
        points, the points can be put together to form the selection areas/rectangles.
        """
        rectangleStart = None
        for sample in sorted(self.points):
            if self.points[sample] == "start":
                rectangleStart = sample*(self.zoom / self.smptopix)
            if self.points[sample] == "end":
                rectangleEnd = sample*(self.zoom / self.smptopix)
                rect = self.scene.addRect(rectangleStart,0,rectangleEnd-rectangleStart,self.height,QPen(),self.selectionBrush)
                self.areas.append(rect)

    def clear(self):
        """
        Cleans up all selection areas in the objects list as well as the painted objects on the scene.
        """
        for n in range(len(self.areas)):
            self.scene.removeItem(self.areas[n])
        self.areas.clear()


