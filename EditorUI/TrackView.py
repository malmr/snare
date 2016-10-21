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
from PyQt5.QtCore import *

from EditorUI.TrackAbstract import TrackAbstract
from EditorUI.TrackTimeline import TrackTimeline
from EditorUI.TrackCursor import TrackCursor
from EditorUI.TrackSelection import TrackSelection
from EditorUI.TrackMark import TrackMark
from EditorUI.TrackWaveform import TrackWaveform


class TrackViewWidget(QGraphicsView):

    """
    TrackViewWidget is a helper class. A QGraphicsView object is necessary to display a QGraphicsScene. Ideally one
    could describe a class that inherits from TrackAbstract to keep the automated signal lines and from
    QGraphicsView to have the display functionality, but the Qt framework does not support multiple inheritance.
    Therefore TrackViewWidget inherits from QGraphicsView and the missing functionality is added manually.
    """

    def __init__(self, scene, root):
        """
        Link the view to the scene and remember the root.

        :param scene: The scene to be displayed by the view widget
        :param root: the parent object in the layer model
        """
        super(TrackViewWidget, self).__init__(scene)
        self.root = root

    def keyPressEvent(self, QKeyEvent):
        """
        Override method to grab and relay QKeyEvent to parent object.

        :param QKeyEvent: KeyEvent to relay :
        """
        self.root.slo_keyEnter(QKeyEvent)

    def keyReleaseEvent(self, QKeyEvent):
        """
        Override method to grab and relay QKeyEvent to parent object.

        :param QKeyEvent: KeyEvent to relay :
        """
        self.root.slo_keyRelease(QKeyEvent)


class TrackScene(QGraphicsScene):

    """
    TrackScene is a helper class. A QGraphicsScene object is necessary to give classes like TrackWaveform something to
    paint on. Ideally one could describe a class that inherits from TrackAbstract to keep the automated signal lines and
    from QGraphicsScene to have the paint functionality, but the Qt framework does not support multiple inheritance.
    Therefore TrackScene inherits from QGraphicsScene and the missing functionality is added manually.
    """

    def __init__(self, root):
        """
        Remember the parent object.

        :param root: Reference to the parent object
        """
        super(TrackScene, self).__init__()
        self.root = root

    def mousePressEvent(self, QGraphicsSceneMouseEvent):
        """
        Override method to grab and relay QGraphicsSceneMouseEvent to parent object.

        :param QGraphicsSceneMouseEvent: MouseEvent to relay
        """
        self.root.slo_mousePress(QGraphicsSceneMouseEvent)

    def mouseReleaseEvent(self, QGraphicsSceneMouseEvent):
        """
        Override method to grab and relay QGraphicsSceneMouseEvent to parent object.

        :param QGraphicsSceneMouseEvent: MouseEvent to relay
        """
        self.root.slo_mouseRelease(QGraphicsSceneMouseEvent)

    def mouseMoveEvent(self, QGraphicsSceneMouseEvent):
        """
        Override method to grab and relay QGraphicsSceneMouseEvent to parent object.

        :param QGraphicsSceneMouseEvent: MouseEvent to relay
        """
        self.root.slo_mouseMove(QGraphicsSceneMouseEvent)

    def mouseDoubleClickEvent(self, QGraphicsSceneMouseEvent):
        """
        Override method to grab and relay QGraphicsSceneMouseEvent to parent object.

        :param QGraphicsSceneMouseEvent: MouseEvent to relay
        """
        self.root.slo_mouseDoubleClick(QGraphicsSceneMouseEvent)


class TrackView(TrackAbstract):

    """
    TrackView provides the user interface elements necessary to display the waveform, allow the user to make selections,
    place a cursor etc.
    """

    def __init__(self, name, state, selections, analysisTypes, marks, cursorposition, height, width, smptopix, zoom, parent=None):
        """
        The constructor of this class creates a QGraphicsScene, links it with a QGraphicsView and creates all objects
        that paint on the scene

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
        super(TrackView, self).__init__(name, state, selections, analysisTypes, marks, cursorposition, height, width, smptopix, zoom, parent)

        self.scene = TrackScene(self)

        self.waveform = TrackWaveform(name, state, selections, analysisTypes, marks, cursorposition, height, width, smptopix, zoom, self, self.scene)

        self.timeline = TrackTimeline(name, state, selections, analysisTypes, marks, cursorposition, height, width, smptopix, zoom, self, self.scene)

        self.cursor = TrackCursor(name, state, selections, analysisTypes, marks, cursorposition, height, width, smptopix, zoom, self, self.scene)

        self.selection = TrackSelection(name, state, selections, analysisTypes, marks, cursorposition, height, width, smptopix, zoom, self, self.scene)

        self.mark = TrackMark(name, state, selections, analysisTypes, marks, cursorposition, height, width, smptopix, zoom, self, self.scene)

        self.widget = TrackViewWidget(self.scene, self)
        self.widget.setFixedSize(width, height+10)
        self.widget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.widget.horizontalScrollBar().sliderMoved.connect(self.viewChanged)
        self.widget.horizontalScrollBar().valueChanged.connect(self.viewChanged)
        self.widget.horizontalScrollBar().actionTriggered.connect(self.viewChangedByScrollbar)
        self.widget.setDragMode(QGraphicsView().ScrollHandDrag)
        self.widget.setDragMode(QGraphicsView().NoDrag)

        self.factor = 1

    def slo_redraw(self, factor):
        """
        Slightly extends the base class' slo_redraw. Child classes will draw their content scaled when the slo_redraw
         has been triggered, but before thar happens, the scene has to be emptied.

        :param factor: New zoom-level
        """
        adjustFactor = factor / self.factor
        self.factor = factor
        rect = self.widget.mapToScene(self.widget.viewport().geometry()).boundingRect()
        sceneLeftCorner = rect.x()
        rect = QRectF(sceneLeftCorner*adjustFactor,0,1000,100)
        self.widget.ensureVisible(rect, 0, 0)

        self.scene.clear()

        super(TrackView, self).slo_redraw(factor)

    def viewChanged(self):
        """
        Slot for signal triggered by the view widget. The signal should only be relayed to the parent if this is the
        active track. The dimensions of the currently by the view widget displayed portion of the scene is extracted
        and sent with the signal.
        """
        if self.widget.hasFocus():
            rect = self.widget.mapToScene(self.widget.viewport().geometry()).boundingRect()
            self.sig_viewChanged.emit(rect)

    def viewChangedByScrollbar(self, int):
        """
        Slot for signal triggered by the view widget. The dimensions of the currently by the view widget displayed
        portion of the scene is extracted and sent with the signal.

        :param int: Not elefant.
        """
        rect = self.widget.mapToScene(self.widget.viewport().geometry()).boundingRect()
        self.sig_viewChanged.emit(rect)

    def slo_setView(self, QRectF):
        """
        Display the specified portion of the scene in the view widget. Then let the base class handle further treatment
        of the signal (avoid breaking the chain of command)

        :param QRectF: Position/rectangle to display
        """
        sceneRightCorner = self.widget.sceneRect().right()
        requestedRightCorner = QRectF.x()

        if sceneRightCorner < requestedRightCorner:
            sceneRect = self.widget.sceneRect()
            sceneRect.setRight(requestedRightCorner)
            self.widget.setSceneRect(sceneRect)

        self.widget.ensureVisible(QRectF, 0, 0)
        super(TrackView, self).slo_setView(QRectF)

    def slo_update(self, pos):
        """
        TrackManager triggers slo_update without a meaningful position. This method extracts a meaningful posiiton from
        the currently displayed portion of the scene and leaves it to the base class to relay the signal to all child
        classes

        :param pos: Not relevant here.
        """
        pos = self.widget.mapFromScene(0, 0).x() * (-1)
        super(TrackView, self).slo_update(pos)

    def setCursor(self, smp):
        """
        Relay to TrackCursor

        :param smp: see TrackCursor
        """
        self.cursor.setCursor(smp)

    def enableScrollbar(self, bool):
        """
        The scrollbar of the view widget can be turned on or off. It is only necessary to display the scrollbar of the
        bottom view widget if all tracks are synchronized.

        :param bool: True means the scrollbar is visible
        """
        if bool:
            self.widget.setFixedSize(self.width, self.height+25)
            self.widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        else:
            self.widget.setFixedSize(self.width, self.height+5)
            self.widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def enableDrag(self, bool):
        """
        Turning on and off the manual dragging mode of the view widget, which is one way to navigate.

        :param bool: True means manual dragging is enabled
        """
        if bool:
            self.widget.setDragMode(QGraphicsView().ScrollHandDrag)
        else:
            self.widget.setDragMode(QGraphicsView().NoDrag)

    def getSelectionPoints(self):
        """
        Relay to TrackSelection

        :return: see TrackSelection
        """
        return self.selection.getSelectionPoints()
