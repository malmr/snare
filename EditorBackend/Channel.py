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


class Channel:

    """
    A helper class. instead of working with integer-channel numbers, work with an unique object reference, that might
    as well carry some additional information, like a channel name.
    """

    def __init__(self, type, name):
        """
        Defining all attributes for a channel object to carry.
        """
        self.type = type
        self.name = name
        self.recording = False
        self.length = 0

    def getName(self):
        """
        A getter method.

        :return: The name attribute of this channel.
        """
        return self.name
