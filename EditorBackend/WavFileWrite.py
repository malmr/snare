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


class WavFileWrite:

    """
    This class is used to write RIFF-WAVE-files when recording with SNARE. It supports 16bit or 24bit but only one
    channel. It opens (and if necessary overwrites) a wav file, writes a header (initially with a filesize of zero)
    and then is ready to receive blockwise updates of recorded samples to append to the file. On closing the file, the
    header will be updated to contain the right data block length.
    """

    def __init__(self, fileName, sampleRate, sampleWidth, channels, blocksize):
        """
        Initially opens the file and prepares the header.

        :param fileName: File to open or create.
        :param sampleRate: Samplerate to write in header
        :param sampleWidth: Samplewidth to write to header
        :param channels: Number of channels (use one, otherwise not tested)
        :param blocksize: Size of block to receive per update call.
        """
        self.fileName = fileName
        self.sampleRate = sampleRate
        self.sampleWidth = sampleWidth
        self.channels = channels
        self.blocksize = blocksize

        # Open File
        self.file = QFile(fileName)
        self.file.open(QIODevice.WriteOnly)
        self.stream = QDataStream(self.file)
        self.blockcount = 0

        # Header, standard length of 44 bytes
        self.RIFF = b"RIFF"
        self.SIZE = 0x0.to_bytes(4, byteorder="little") # Update when closing
        self.WAVE = b"WAVE"

        self.FMT = b"fmt "
        self.FMT_LENGTH = int(16).to_bytes(4, byteorder="little")

        self.FORMAT_TAG = 0x1.to_bytes(2, byteorder="little")
        self.CHANNELS = self.channels.to_bytes(2, byteorder="little")

        self.SAMPLE_RATE = self.sampleRate.to_bytes(4, byteorder="little")
        a = self.channels * int(((self.sampleWidth*8 + 7)/8))
        self.BLOCK_ALIGN = a.to_bytes(2, byteorder="little")

        self.BYTES_SECOND = int(a*self.sampleRate).to_bytes(4, byteorder="little")
        b = int(self.sampleWidth*8)
        self.BITS_SAMPLE = b.to_bytes(2, byteorder="little")
        self.DATA = b"data"
        self.LENGTH = 0x0.to_bytes(4, byteorder="little") # Update when closing

        self.writeHeader()

    def writeHeader(self):
        """
        Writes the header with member attributes that already have the right byteformat.
        """
        self.file.seek(0)
        self.stream.writeRawData(self.RIFF)
        self.stream.writeRawData(self.SIZE)
        self.stream.writeRawData(self.WAVE)
        self.stream.writeRawData(self.FMT)
        self.stream.writeRawData(self.FMT_LENGTH)
        self.stream.writeRawData(self.FORMAT_TAG)
        self.stream.writeRawData(self.CHANNELS)
        self.stream.writeRawData(self.SAMPLE_RATE)
        self.stream.writeRawData(self.BYTES_SECOND)
        self.stream.writeRawData(self.BLOCK_ALIGN)
        self.stream.writeRawData(self.BITS_SAMPLE)
        self.stream.writeRawData(self.DATA)
        self.stream.writeRawData(self.LENGTH)

    def __del__(self):
        """
        Destructor call -> self.close()
        """
        self.close()

    def close(self):
        """
        Finish the writing process by updating the header to contain correct size information. Then close Qt stream.
        """
        datalength = self.blockcount * self.blocksize * self.channels * self.sampleWidth
        self.LENGTH = datalength.to_bytes(4, byteorder="little")
        self.SIZE = int(datalength+36).to_bytes(4, byteorder="little")
        # Update header
        self.writeHeader()
        self.file.close()

    def appendBlock(self, block):
        """
        Appends a block of raw sample data to the file. Note that the header will not be updated until the file is
        closed. In case of a crash, all sample data is saved, but the file will look empty to most programs.

        :param block: A bytearray already in a format of interleaved raw integer samples
        """
        # Check size of block
        if len(block) == self.blocksize*self.channels*self.sampleWidth:
            self.stream.writeRawData(block)
            self.blockcount += 1
        else:
            print("Incorrect Block Format, can't write!")

