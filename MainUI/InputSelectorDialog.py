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

import pyaudio
import os
import sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.Qt import *


class InputSelectorDialog(QDialog):

    """
    This class creates a dialog window that lets the user select an input audio device and then select which channels
    to record form that device. The result of the selection is saved in self.channels, a list. The last entry of the
    list is the device index while all other entries list the channels to record: e.g. [0,1,2,4] -> record channel 0,
    1 and 2 from device 4.
    """

    def __init__(self, channels):
        """
        A manual layout creation.

        :param channels: Reference to the list that will contain the results when closed.
        """
        super().__init__()

        icon = QIcon(self.resource_path("icon.ico"))
        self.setWindowIcon(icon)

        # Globals
        self.p = pyaudio.PyAudio()

        # Lists
        # Mapping dropdown to device
        self.devices = dict()
        # List of selected channels
        self.channels = channels
        self.dropdown = QComboBox()
        self.dropdown.addItem("Select Device..")
        self.buildDrop()
        self.dropdown.currentIndexChanged.connect(self.buildTree)

        self.tree = QTreeWidget()
        self.buildTree(0)

        # Confirm Button
        self.confirmButton = QPushButton(clicked=self.confirm)
        self.confirmButton.setText("Confirm")

        # All about the looks
        self.setWindowTitle("Select Channels...")
        self.setGeometry(300, 300, 360, 250)
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.addWidget(self.dropdown)
        self.layout.addWidget(self.tree)
        self.layout.addWidget(self.confirmButton)
        self.setLayout(self.layout)
        self.exec()

    def buildDrop(self):
        """
        Retrieves all available audio devices from PyAudio and filters them to only display input devices. All matching
        devices are added to a dropdown menu.
        """
        dropdownIndex = 1
        for device in range(0, self.p.get_device_count()):
            deviceInfo = self.p.get_device_info_by_index(device)
            if deviceInfo['maxInputChannels'] > 0:
                self.dropdown.addItem(deviceInfo['name'])
                self.devices[dropdownIndex] = device
                dropdownIndex += 1


    def buildTree(self, dropdownIndex):
        """
        Creates a list of checkable items after the user selected an input device. Retrieves the number of available
        input channels for the given device from PyAudio.

        :param dropdownIndex: The list self.devices links the dropdown index to the device index
        """
        self.tree.clear()
        self.tree.setColumnCount(2)
        header = self.tree.headerItem()
        header.setText(0, "Select")
        header.setText(1, "Channel")
        self.tree.header().resizeSection(0,75)
        self.tree.header().resizeSection(1,200)

        if dropdownIndex != 0:
            deviceInfo = self.p.get_device_info_by_index(self.devices[dropdownIndex])
            for channel in range(0, deviceInfo['maxInputChannels']):
                parent = QTreeWidgetItem(self.tree)
                parent.setText(1, str(channel))
                parent.setFlags(parent.flags() | Qt.ItemIsUserCheckable)
                parent.setCheckState(0, Qt.Checked)

    def confirm(self):
        """
        When the user has selected device and channel, this method will compose the list and close the dialog.
        """
        if self.dropdown.currentIndex() != 0:
            iterator = QTreeWidgetItemIterator(self.tree, QTreeWidgetItemIterator.Checked)
            while iterator.value():
                item = iterator.value()
                self.channels.append(int(item.text(1)))
                iterator += 1
            # The last element is the channel
            self.channels.append(self.devices[self.dropdown.currentIndex()])
        self.done(1)

    def resource_path(self, relative_path):
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, relative_path)
        return os.path.join(os.path.abspath("."), relative_path)