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

import struct
import numpy as np


class Unpacker:

    """
    This class simplifies the conversion from the raw bytearray read from the WAVE-file, or received from the recording
    hardware to a NumPy array.
    """

    def __init__(self, blockSize, sampleWidth):
        """
        Initialising and creating format strings.

        :param blockSize: The global block size.
        :param sampleWidth: The global sample width.
        :return:
        """
        self.blockSize = blockSize
        self.sampleWidth = sampleWidth

        self.fmt16 = str(blockSize) + "h"
        self.fmt24 = str(blockSize) + "i"

        self.fmt16_32 = str(blockSize*32) + "h"
        self.fmt24_32 = str(blockSize*32) + "i"

    def unpack(self, data):
        """
        Automatically select the correct unpack method.

        :param data: Raw bytearray input
        :return: Converted numpy array.
        """
        if self.sampleWidth == 2:
            return self.unpack16(data)
        elif self.sampleWidth == 3:
            return self.unpack24(data)

    def unpack16(self, data):
        """
        For 2 Bytes the unpack is simple with the python builtin "struct.unpack"

        :param data: Raw bytearray input
        :return: Converted numpy array.
        """
        return np.array( struct.unpack(self.fmt16, data))

    def unpack24(self, data):
        """
        For 3 Bytes is slighty more complicated. The buultin "struct.unpack" only works on even numbers of bytes,
        therefore the raw bytearray is padded with 1 Byte of zeros before converting it to a numpy array.

        :param data: Raw bytearray input
        :return: Converted numpy array.
        """
        buffer = bytearray(self.blockSize*4)
        buffer[1::4] = data[0::3]
        buffer[2::4] = data[1::3]
        buffer[3::4] = data[2::3]
        return np.array(struct.unpack(self.fmt24, buffer))
