from PyQt5.Qt import *
from PyQt5.QtGui import *

from EditorUI.TrackAbstract import TrackAbstract
from EditorUI.TrackView import TrackScene

class TrackOverview(TrackAbstract):

    def __init__(self, name, state, selections, analysisTypes, marks, cursorposition, height, width, smptopix, zoom, parent):
        super(TrackOverview, self).__init__(name, state, selections, analysisTypes, marks, cursorposition, height, width, smptopix, zoom, parent)

        self.layout = QHBoxLayout()

        self.setMaximumWidth(1225)
        self.setMinimumWidth(1225)
        self.setMaximumHeight(25)
        self.setMinimumHeight(25)

        self.spacer = QSpacerItem(225, 20)

        self.scene = TrackScene(self)

        self.view = QGraphicsView(self.scene)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.ensureVisible(0, 0, self.width, 25, 0, 0)

        self.layout.addItem(self.spacer)
        self.layout.addWidget(self.view)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.blackPen = QPen(QColor(Qt.black))
        self.blackBrush = QBrush(QColor(Qt.black))
        self.polygon1 = QPolygonF([QPoint(0, 0), QPoint(10, 10), QPoint(0, 20)])
        self.polygon2 = QPolygonF([QPoint(996, 0), QPoint(986, 10), QPoint(996, 20)])

        self.mark1 = self.scene.addPolygon(self.polygon1, self.blackPen, self.blackBrush)
        self.mark2 = self.scene.addPolygon(self.polygon2, self.blackPen, self.blackBrush)

        self.opaqueGreen = QColor(0, 255, 0, 127)
        self.selectBrush = QBrush(self.opaqueGreen)
        self.area = self.scene.addRect(0, 0, 100, 15, QPen(), self.selectBrush)

        self.displayedArea = 441000 # samples
        self.maxLength = 441000
        self.startPos = 0

        self.factor = 1

        self.setLayout(self.layout)
        self.show()

    def slo_mousePress(self, QGraphicsSceneMouseEvent):
        self.mouseEvent(QGraphicsSceneMouseEvent)

    def slo_mouseMove(self, QGraphicsSceneMouseEvent):
        self.mouseEvent(QGraphicsSceneMouseEvent)

    def slo_mouseDoubleClick(self, QGraphicsSceneMouseEvent):
        pass

    def slo_mouseRelease(self, QGraphicsSceneMouseEvent):
        pass

    def mouseEvent(self, QGraphicsSceneMouseEvent):
        x = QGraphicsSceneMouseEvent.scenePos().x()
        x = x * (self.maxLength / self.width)
        if x < 0:
            x = 0
        if x > self.maxLength:
            x = self.maxLength

        rect = QRectF((x*self.factor)/441, 0, 1000, 10)
        self.sig_viewChanged.emit(rect)


    def slo_setView(self, QRectF):
        x = QRectF.x() * 441
        x = x / self.factor
        self.startPos = x
        self.updateRectangle()

    def updateRectangle(self):
        percentage = self.displayedArea/self.maxLength
        areaWidth = (percentage * self.width) / self.factor
        start = (self.startPos * self.width) / self.maxLength
        self.setArea(start, areaWidth)

    def setArea(self, start, width):
        if start < 0:
            start = 0
        if (start+width) > 999:
            start = 999-width
        self.area.setRect(start, 0, width, 20)

    def updateMaxLength(self, smp):
        self.maxLength = smp

    def slo_redraw(self, factor):
        self.factor = factor
        self.updateRectangle()