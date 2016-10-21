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


class SubWindow(QWidget):

    """
    Both the analysis window and the editor window are objects of this class. It contains a layout and an interface to
    add and remove widgets to/from the layout.
    """

    def __init__(self):
        """
        Setting up the layout.
        """
        super(SubWindow, self).__init__()

        self.layout = QFormLayout()
        self.layout.setContentsMargins(0, 20, 0, 0)

        self.setLayout(self.layout)

    def addWidget(self, widget):
        """
        Adds a widget to the layout.

        :param widget: A QWidget to add.
        """
        #print("Adding: ", widget)
        self.layout.addWidget(widget)

    def removeWidget(self, widget):
        """
        Removes a widget from the layout.

        :param widget: A QWidget to remove.
        """
        print('called')
        self.layout.removeWidget(widget)


class SubWindowDock(QDockWidget):

    """
    This class turns the SubWindow into a dock widget, that can be dragged, minimised and detached from the main window,
    allowing the user to set up the user interface in an individual way.
    """

    def __init__(self, title):
        """
        Sets up the SubWindow, the title and some Qt properties.

        :param title: Name of this subwindow.
        """
        super(SubWindowDock, self).__init__()

        self.subWindow = SubWindow()

        self.setWindowTitle(title)

        self.scroller = QScrollArea()
        self.scroller.setWidgetResizable(True)
        self.scroller.setWidget(self.subWindow)

        self.setWidget(self.scroller)
        self.setFeatures(QDockWidget.DockWidgetFloatable |
                 QDockWidget.DockWidgetMovable)

    def addWidget(self, widget):
        """
        Interface for adding a widget, relayed to SubWindow.

        :param widget: A QWidget to add.
        """
        self.subWindow.addWidget(widget)

    def removeWidget(self, widget):
        """
        Interface for removing a widget, relayed to SubWindow.

        :param widget: A QWidget to remove.
        """
        self.subWindow.removeWidget(widget)
