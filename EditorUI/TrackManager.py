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

from EditorUI.TrackAbstract import TrackAbstract
from EditorUI.TrackUI import TrackUI
from EditorUI.TrackData import TrackData
from EditorBackend.Channel import Channel

from EditorUI.TrackOverview import TrackOverview


class TrackManager(TrackAbstract):

    """
    The TrackManager provides the connection between the editor area of SNARE and the MainBackend. Also it defines the
    behaviour of the entire editor area. An editor element (TrackUI) does not contain any logic, it merely sends all
    input from the user to the TrackManager and receives its commands from the TrackManager. Therefore a TrackUI object
    without the TrackManager does not respond to any input. This way user input, processing and display are separated
    and the definition the editor area's behaviour is concentrated in this class. For a more detailed explanation on
    the underlying design principle, see the overall documentation of SNARE.
    """

    setPlayerPosition = pyqtSignal(int, Channel)
    playerPlay = pyqtSignal()
    playerPause = pyqtSignal()
    addSelection = pyqtSignal(Channel, str, dict, str)

    addTrack = pyqtSignal(TrackAbstract)
    getWaveform = pyqtSignal(Channel, int, int, int)
    deleteChannel = pyqtSignal(Channel, TrackUI)

    def __init__(self, analyses, blockSize):
        """
        Defines the initial state of the editor area and reserves memory for all Track elements that will follow.

        :param analyses: The list of available analysis types that have been loaded from file.
        :return:
        """
        self.name = "Hanns"
        self.state = "Idle"
        self.selectionNames = ["Calib.", "Sel 1", "Sel 2"]
        self.selectionCount = 3
        self.analysisTypes = analyses.listAnalyzeTypes()
        self.marks = list()
        self.cursorposition = 0
        self.height = 150
        self.width = 1000
        self.blockSize = blockSize
        self.smptopix = self.blockSize // self.width #441

        self.factor = 1

        super(TrackManager, self).__init__(self.name, self.state, self.selectionNames, self.analysisTypes, self.marks,
                                           self.cursorposition, self.height, self.width, self.smptopix, self.factor)
        # A place to store all track-Objects
        self.tracks = list()
        self.trackData = dict()

        self.playing = False
        self.recording = False

        self.overviewLoaded = False

        self.overview = None

    def slo_playpause(self):
        """
        Behaviour when pressing the "play/pause" button. (Or triggering the same event possibly with a key)
        """
        trackData = self.trackData[self.sender()]

        if trackData.isPlaying():
            self.playing = False
            trackData.setPlaying(False)
            self.playerPause.emit()
        else:
            for track in self.tracks:
                self.trackData[track].setPlaying(False)

            self.playing = True
            trackData.setPlaying(True)

            channel = trackData.channel
            smp = trackData.getLastPos()
            self.setPlayerPosition.emit(smp, channel)
            self.playerPlay.emit()

        for track in self.tracks:
            track.slo_setPlaying(self.trackData[track].isPlaying())

    def updateSmp(self, smp, channel):
        """
        A slot to be called from the backend. When the Audioplayer is running it regularly send an update containing
        which sample on which channel was played. The last position is saved in the corresponding TrackData object ans
        the cursor is moved accordingly.

        :param smp: Playback position in samples on update time.
        :param channel: A channel-object referring to the channel currently on playback.
        """
        for track in self.tracks:
            trackData = self.trackData[track]
            if trackData.channel is channel:
                trackData.setLastPos(smp)
                track.setCursor(smp)

    def slo_analyze(self):
        """
        Triggered when the "analyze"-button was pressed. The method gathers the selection points/area (in samples)
        and the relevant channel-reference and passes the information to the backend via the "addSelection" signal.
        """
        trackData = self.trackData[self.sender()]
        [points, state] = self.sender().getSelectionPoints()
        trackData.updateCurrentSelection(points)

        [selectionName, points, state, analysisType] = trackData.getCurrentSelection()
        channel = trackData.channel

        if points:
            self.addSelection.emit(channel, selectionName, points, analysisType)

    def slo_addWaveform(self, waveform):
        """
        This is the place where rendered waveforms from the backend are processed. They are filtered according to the
        channel they belong to and passed on to the corresponding Track.

        :param waveform: A waveform object containing a pixmap.
        """
        for track in self.tracks:
            if self.trackData[track].channel is waveform.channel:
                track.slo_addWaveform(waveform)

    def slo_finishSelection(self):
        """
        This loops back the signal to block a selection. Could be changed e.g. to block all Selections with one event.
        """
        self.sender().slo_enableSelection(False)

    def slo_editSelection(self):
        """
        This loops back the signal to unblock a selection. Could be changed e.g. to block all Selections with one event.
        """
        self.sender().slo_enableSelection(True)

    def slo_mouseDoubleClick(self, QGraphicsSceneMouseEvent):
        """
        Triggered by a double click on TrackView. Places the TrackCursor on the requested position. The received
        position is translated to the position on the scene and then to samples. The value is stored in the TrackData
        object and the signal to set the cursor is emitted.

        :param QGraphicsSceneMouseEvent: Qt mouse event type containing the position on the scene where the click event
         was triggered
        """
        pos = QGraphicsSceneMouseEvent.scenePos().x()
        pos /= self.factor
        smp = int(pos * self.smptopix)
        self.trackData[self.sender()].setLastPos(smp)
        self.sender().setCursor(smp)

    def slo_mousePress(self, QGraphicsSceneMouseEvent):
        """
        Triggered by a mouse press on TrackView. The signal is multiplied to all tracks and used to control the
        selection rectangles. It would also be possible to loop back the signal to only one track instead of having
        synchronised selections on all tracks.

        :param QGraphicsSceneMouseEvent: Qt mouse event type containing the position on the scene, where the event was
         triggered.
        """
        self.sender().slo_startSelection(QGraphicsSceneMouseEvent)

    def slo_mouseRelease(self, QGraphicsSceneMouseEvent):
        """
        Triggered by a mouse release on TrackView. The signal is multiplied to all tracks and used to control the
        selection rectangles. It would also be possible to loop back the signal to only one track instead of having
        synchronised selections on all tracks.

        :param QGraphicsSceneMouseEvent: Qt mouse event type containing the position on the scene, where the event was
         triggered.
        """
        self.sender().slo_endSelection(QGraphicsSceneMouseEvent)

    def slo_mouseMove(self, QGraphicsSceneMouseEvent):
        """
        Triggered by a mouse movement on TrackView. The signal is multiplied to all tracks and used to control the
        selection rectangles. It would also be possible to loop back the signal to only one track instead of having
        synchronised selections on all tracks.

        :param QGraphicsSceneMouseEvent: Qt mouse event type containing the position on the scene, where the event was
         triggered.
        """
        self.sender().slo_moveSelection(QGraphicsSceneMouseEvent)

    def slo_delete(self):
        """
        Triggered by pressing the "X"-button. Deletion is only possible when there is no backend processing active
        (playback or recording) to reduce complexity. The user interface elements are removed and the remaining objects
        are deleted. Then a signal is emitted to also remove this channel from the backend.
        """
        if not self.playing and not self.recording:
            trackData = self.trackData[self.sender()]
            track = self.sender()
            channel = trackData.channel

            self.tracks.remove(track)
            del self.trackData[track]
            track.setVisible(False)
            track.destroy()
            track.sig_requestWaveform.disconnect()
            track.sig_viewChanged.disconnect()
            self.deleteChannel.emit(channel, track)

    def slo_zoomIn(self):
        """
        Triggered by pressing the "+"-button. The zoom range is limited and the steps are selected in a way that they
        are equal in both directions: (1.25)^-1 = 0.8 and one can always return to exactly one step no rounding errors.
        """
        if self.factor < 22:
            self.factor *= 1.25
            self.sig_redraw.emit(self.factor)

    def slo_zoomOut(self):
        """
        Triggered by pressing the "-"-button. The zoom range is limited and the steps are selected in a way that they
        are equal in both directions: (1.25)^-1 = 0.8 and one can always return to exactly one step no rounding errors.
        """
        if self.factor > 0.007 or True:
            self.factor *= 0.8
            self.sig_redraw.emit(self.factor)

    def slo_selectionChange(self, selectionName, analysisType):
        """
        Triggered when the user has made a change to one of the dropdown menus on TrackButtons. The selection areas of
        each track are stored in TrackData, the new selection areas are loaded and the state of the dropdown-menus is
        synchronized.

        :param selectionName: Name of the selection to switch to.
        :param analysisType: Name of the analysis type to switch to.
        """
        for track in self.tracks:
            # Store current data
            [points, state] = track.getSelectionPoints()
            self.trackData[track].updateCurrentSelection(points, state, analysisType)

            # Switch selection
            self.trackData[track].setCurrentSelection(selectionName)

            # Replace with stored data
            [selectionName, points, state, analysisType] = self.trackData[track].getCurrentSelection()
            track.slo_setSelection(selectionName, analysisType, points, state)

    def slo_viewChanged(self, QRectF):
        """
        Triggered by any change on TrackView, e.g. by dragging or scrolling in the view widget. The changes are simply
        synchronised. The signal is not sent back to the sender object to avoid an infinite loop.

        :param QRectF: Portion of the scene to display.
        """
        for track in self.tracks:
            if track is not self.sender():
                track.slo_setView(QRectF)
            self.overview.slo_setView(QRectF)
        self.slo_update(0.0)

    def slo_keyEnter(self, QKeyEvent):
        """
        Receives any keyboard press event from any area of the track. There are two inputs filtered at the moment:
        "M" to set a mark and "Shift" to enter drag mode.

        :param QKeyEvent: Qt type containing the key pressed.
        """
        if QKeyEvent.key() == Qt.Key_Shift:
            for track in self.tracks:
                track.enableDrag(True)
        if QKeyEvent.key() == Qt.Key_M:
            self.slo_requestMark()

    def slo_requestMark(self):
        """
        Triggered by pressing "M" or the marker button on TrackButtons. The last position/sample (the cursor position)
        is retrieved from TrackData for the active channel and a mark is then set on this position for  all channels.
        """
        smp = self.trackData[self.sender()].getLastPos()
        for track in self.tracks:
                self.trackData[track].setMark(smp)
                self.slo_setMark(smp)
                self.slo_redraw(self.factor)

    def slo_skipForward(self):
        """
        Request from a TrackUI object to move the cursor the next mark in forward direction. Positions are all read from
        the corresponding TrackData object.
        """
        self.slo_playpause()
        trackData = self.trackData[self.sender()]
        smp = trackData.getLastPos()
        mark = trackData.getNextMark(smp)
        trackData.setLastPos(mark)
        self.sender().setCursor(mark)
        self.slo_playpause()

    def slo_skipBackward(self):
        """
        Request from a TrackUI object to move the cursor the next mark in backward direction. Positions are all read
        from the corresponding TrackData object.
        """
        self.slo_playpause()
        trackData = self.trackData[self.sender()]
        smp = trackData.getLastPos()
        mark = trackData.getPreviousMark(smp)
        trackData.setLastPos(mark)
        self.sender().setCursor(mark)
        self.slo_playpause()

    def slo_keyRelease(self, QKeyEvent):
        """
        Receives any keyboard release event from any area of the track. There is only one input filtered at the moment:
        "Shift" to leave drag mode.

        :param QKeyEvent: Qt type containing the key released.
        """
        if QKeyEvent.key() == Qt.Key_Shift:
            for track in self.tracks:
                track.enableDrag(False)

    # Required interface to work with legacy
    def updateRecording(self, int):
        """
        Legayc interface. Required. Not used anymore.

        :param int: not elefant
        """
        pass

    def addChannel(self, channel):
        """
        Called from backend. Creates a new TrackUI and TrackData for the given channel. Everything will be linked
        automatically.

        :param channel: A channel object referring to the channel to be displayed
        """
        if not self.overviewLoaded:
            self.overviewLoaded = True
            self.overview = TrackOverview("overview", None, self.selectionNames, self.analysisTypes, self.marks, 0, self.height, self.width, self.smptopix, self.factor, self)
            self.addTrack.emit(self.overview)

        state = None
        if channel.recording:
            state = "Recording"
        else:
            state = "Playback"
            self.overview.updateMaxLength(channel.length)
            self.overview.updateRectangle()


        newTrack = TrackUI(channel.getName(), state, self.selectionNames, self.analysisTypes, None, 0, self.height,
                           self.width, self.smptopix, self.factor, self)

        trackData = TrackData(self.selectionNames, self.analysisTypes, channel, newTrack)

        self.tracks.append(newTrack)
        self.trackData[newTrack] = trackData

        for track in self.tracks:
            track.enableScrollbar(False)
        newTrack.enableScrollbar(False)

        self.slo_update(0.0)
        self.addTrack.emit(newTrack)

    def slo_requestWaveform(self, startBlock, dataBlocks, numberOfPixmaps):
        """
        This is the slot used by TrackWaveform to request all needed waveforms for the current position and zoom level.
        Since a Track element does not know its channel, this information is added here, before the signal gets relayed
        to the backend.

        :param block: The requested block.
        :param widthPreScaling: The width of the requested pixmap, equalling the zoom level.
        :param height: Height of the pixmap
        """
        channel = self.trackData[self.sender()].channel
        self.getWaveform.emit(channel, startBlock, dataBlocks, numberOfPixmaps)

    def updateFromRecorder(self, smp):
        """
        When recording, the backend will update the TrackManager on the currently recorded position. E.g. to keep
        scrolling with the recording progress.

        :param smp: Last recorded sample/position
        """
        pos = smp / self.smptopix
        self.slo_update(pos)


    def newSelection(self):
        """
        A slot called from the backend to add a selection. It will appear on the TrackButtons' dropdown menu and have
        the last added analysis widget as default selected.
        """
        selectionName = "Sel " + str(self.selectionCount)
        self.selectionCount += 1

        for track in self.tracks:
            trackData = self.trackData[track]
            trackData.addSelection(selectionName)

        self.slo_selectionChange(selectionName, self.analysisTypes[-1])

    def closeRecordings(self):
        """
        A slot called from the backend to notify that the recording has been finished. The track will then display the
        file where the recording has been store instead of the source audio device. (To be implemented)
        """
        self.recording = False

    def setRecording(self, bool):
        """
        A slot called from the backend to notify of a changed recording status.

        :param bool: True if there is a recording ongoing.
        """
        self.recording = bool
