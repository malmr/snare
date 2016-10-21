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
from PyQt5.QtGui import *

from EditorUI.TrackAbstract import TrackAbstract

class TrackButtons(TrackAbstract):

    """
    Each Track is accompanied by a selection of buttons on the left side. They are implemented in this class.
    All signals are automatically relayed to the managing backend class by the principle described in TrackAbstract.
    To function properly the files "EditorUI/Lock.png", "Marker.png" and "EditorUI/Unlock.png" need to be available.

    """

    def __init__(self, name, state, selections, analysisTypes, marks, cursorposition, height, width, smptopix, zoom, parent=None):
        """
        The constructor of this class mainly creates the buttons and their layout by code, no .ui files are used. All
        elements are grouped to QHBoxLayouts or QGridLayouts and then stacked in one overall QFormLayout.

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
        super(TrackButtons, self).__init__(name, state, selections, analysisTypes, marks, cursorposition, height, width, smptopix, zoom, parent)

        self.state = state

        self.setMaximumWidth(220)
        self.setMinimumWidth(220)

        self.setMaximumHeight(175)
        self.setMinimumHeight(175)

        self.layout = QFormLayout()

        # Header
        self.header = QHBoxLayout()

        self.nameLabel = QLabel(name)
        self.nameLabel.setToolTip('Filename and current channel:\n' + self.nameLabel.text())

        self.header.addWidget(self.nameLabel)

        # First Row
        self.firstRow = QHBoxLayout()

        self.deleteButton = QToolButton(clicked=self.sig_delete)
        self.deleteButton.setIcon(self.style().standardIcon(QStyle.SP_TitleBarCloseButton))
        self.deleteButton.setToolTip('Delete channel')

        self.lockButton = QToolButton(clicked=self.lock)
        self.lockButton.setIcon(QIcon("EditorUI/Unlock.png"))
        self.lockButton.setToolTip('Lock/Unlock selection')
        self.lockState = "Unlocked"

        self.firstRow.addWidget(self.deleteButton)
        self.firstRow.addWidget(self.lockButton)

        # Second Row
        self.secondRow = QHBoxLayout()

        self.selectSelection = QComboBox()
        for item in selections:
            self.selectSelection.addItem(item)
        self.selectSelection.activated.connect(self.selectionChange)
        self.selectSelection.setCurrentIndex(self.selectSelection.count()-1)
        self.selectSelection.setToolTip('Choose selection or calibration')

        self.typeSelection = QComboBox()
        for item in analysisTypes:
            self.typeSelection.addItem(item)
        self.typeSelection.activated.connect(self.selectionChange)
        self.typeSelection.setToolTip('Choose analyse type')

        self.secondRow.addWidget(self.selectSelection)
        self.secondRow.addWidget(self.typeSelection)

        # Third Row
        self.thirdRow = QHBoxLayout()

        self.analButton = QPushButton(clicked=self.sig_analyze)
        self.analButton.setText("Analyze")
        self.analButton.setToolTip('Start analyse')

        self.thirdRow.addWidget(self.analButton)

        # Fourth Row
        self.fourthRow = QGridLayout()

        self.zoomPlusButton = QPushButton(clicked=self.sig_zoomIn)
        self.zoomPlusButton.setText("+")
        self.zoomPlusButton.setToolTip('Zoom in')
        self.zoomLabel = QLabel(str('{0:.2f}'.format(self.zoom)))
        self.zoomLabel.setMinimumWidth(30)
        self.zoomLabel.setAlignment(Qt.AlignCenter)
        self.zoomMinusButton = QPushButton(clicked=self.sig_zoomOut)
        self.zoomMinusButton.setText("-")
        self.zoomMinusButton.setToolTip('Zoom out')

        self.playButton = QPushButton(clicked=self.sig_playpause)
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.playButton.setToolTip("Play/Pause audio channel")
        self.skipForwardButton = QPushButton(clicked=self.sig_skipForward)
        self.skipForwardButton.setIcon(self.style().standardIcon(QStyle.SP_MediaSkipForward))
        self.skipForwardButton.setToolTip('Jump to next marker')
        self.skipBackwardButton = QPushButton(clicked=self.sig_skipBackward)
        self.skipBackwardButton.setIcon(self.style().standardIcon(QStyle.SP_MediaSkipBackward))
        self.skipBackwardButton.setToolTip('Jump to last marker')
        self.markerButton = QPushButton(clicked=self.sig_requestMark)
        self.markerButton.setIcon(QIcon("EditorUI/Marker.png"))
        self.markerButton.setStyleSheet("QToolButton {border-style: outset; border-width: 0px;}");
        self.markerButton.setToolTip('Set marker at current position')
        self.skipBackwardButton.setFixedSize(24,24)
        self.skipForwardButton.setFixedSize(24,24)
        self.playButton.setFixedSize(24,24)
        self.markerButton.setFixedSize(24,24)
        self.zoomMinusButton.setFixedSize(24,24)
        self.zoomPlusButton.setFixedSize(24,24)

        self.fourthRow.addWidget(self.zoomMinusButton, 0, 0)
        self.fourthRow.addWidget(self.zoomLabel, 0, 1)
        self.fourthRow.addWidget(self.zoomPlusButton, 0, 2)
        self.fourthRow.addWidget(self.playButton, 0, 3)
        self.fourthRow.addWidget(self.skipBackwardButton, 0, 4)
        self.fourthRow.addWidget(self.markerButton, 0, 5)
        self.fourthRow.addWidget(self.skipForwardButton, 0, 6)

        # Finish Layout
        self.layout.addRow(self.firstRow)
        self.layout.addRow(self.header)
        self.layout.addRow(self.secondRow)
        self.layout.addRow(self.thirdRow)
        self.layout.addRow(self.fourthRow)
        self.setLayout(self.layout)
        self.show()

    def slo_redraw(self, factor):
        """
        Set the zoom level label.
        :param factor: New zoom factor.
        """
        val = round(1/factor, 4)
        self.zoomLabel.setText(str('{0:.2f}'.format(val)))

    def slo_setPlaying(self, bool):
        """
        Sets the "play"-buttons icon to represent the playback state of this channel.
        :param bool: True if playback is on. (Display "pause"-icon)
        """
        if bool:
            self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
        else:
            self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))

    def selectionChange(self):
        """
        An in between slot triggered by changing one of the dropdown-menus, gathers relevant information before
        triggering the sig_selectionChange that is connected to the command chain.
        """
        selection = self.selectSelection.currentText()
        analysisType = self.typeSelection.currentText()
        self.sig_selectionChange.emit(selection, analysisType)

    def lock(self):
        """
        A toggle switch for the lock symbol
        """
        if self.lockState == "Locked":
            self.lockButton.setIcon(QIcon("EditorUI/Unlock.png"))
            self.lockButton.update()
            self.lockState = "Unlocked"
            self.sig_editSelection.emit()
        elif self.lockState == "Unlocked":
            self.lockButton.setIcon(QIcon("EditorUI/Lock.png"))
            self.lockButton.update()
            self.lockState = "Locked"
            self.sig_finishSelection.emit()

    # --- Public ---
    def slo_setSelection(self, selectionName, analysisType, selection, state):
        """
        If the selection has been changed by the user at one track or by the program, the new state is synchronised over
        all tracks. This means the name of the selection, the analysis type, selection points and selection state are
        sent to each track. In TrackButtons the dropdown menus have to be changed accordingly. (The other endpoint of
        this command chain can be found at TrackSelection.) There is one special case: selectionName "Calib." is reserved
        for the Calibration selection and causes the analysis type dropdown menu to grey out.

        :param selectionName: Name of the selection to switch to. In case it doesn't exist, a new selection is added.
        :param analysisType: Name of the type of analysis associated with the current selection.
        :param selection: Start and end-samples of the actual selection. Not needed here, see TrackSelection.
        :param state: Lock state of the current selection
        """
        if self.selectSelection.findText(selectionName) == -1:
            self.selectSelection.addItem(selectionName)

        self.selectSelection.setCurrentText(selectionName)
        self.typeSelection.setCurrentText(analysisType)

        if selectionName == "Calib.":
            self.analButton.setText("Calibrate")
            self.typeSelection.setDisabled(True)
        else:
            self.analButton.setText("Analyze")
            self.typeSelection.setDisabled(False)

        if state == "Blocked":
            self.lockState = "Unlocked"
        else:
            self.lockState = "Locked"
        self.lock()
