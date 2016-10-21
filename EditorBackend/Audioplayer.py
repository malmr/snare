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
import pyaudio

from EditorBackend.Channel import Channel


class Audioplayer(QObject):

    """
    This class takes care of audio playback via PyAudio. It also works in the block-wise manner like Buffer.
    It can switch between channels, but only one channel can be played at a time.
    """

    sendPos = pyqtSignal(int, Channel)

    def __init__(self, buffer, sampleRate, sampleWidth, blockSize):
        QObject.__init__(self)

        # A carefully selected chunkSize, compromise between no lagging and responsiveness
        self.chunkSize = 8192       # Chunksize is requested for PyAudio Stream

        self.buffer = buffer
        self.channel = None
        self.sampleRate = sampleRate
        self.sampleWidth = sampleWidth
        self.blockSize = blockSize

        # Initialize to Position 0 at Channel 0
        self.smp = 0 # Current position ON SAMPLE
        self.oldBlockNo = -1
        self.currentBlock = -1
        self.data = None
        self.channelChangeFlag = False

        self.playing = False

        self.p = pyaudio.PyAudio()

        self.stream = self.p.open(format=self.p.get_format_from_width(self.sampleWidth), channels=1,
                                  rate=self.sampleRate, output=True, stream_callback=self.callback,
                                  frames_per_buffer=self.chunkSize)

        self.stream.stop_stream()

    def __getChunk__(self):
        """
        Cuts a self.chunkSize big portion out of a sample block from the buffer and writes it to self.chunk, where it
        will be picked up by the callback.
        """
        blockNo = self.smp // self.blockSize
        self.blockPos = self.smp % self.blockSize
        self.__getBlock__(blockNo)
        # Check if requested Chucksize is still in the Block
        if (self.blockPos + self.chunkSize) <= self.blockSize:
            self.chunk = self.currentBlock[self.blockPos * self.sampleWidth:(self.blockPos + self.chunkSize) * self.sampleWidth]
        else:
            first = self.blockSize - self.blockPos      # Take so many samples from first block
            second = self.chunkSize - first             # Take so many samples from second block
            self.__getBlock__(blockNo)
            self.chunk = self.currentBlock[self.blockPos * self.sampleWidth:(self.blockPos + first) * self.sampleWidth]
            self.__getBlock__(blockNo + 1)
            self.chunk += self.currentBlock[0:second * self.sampleWidth]

    def __getBlock__(self, blockno):
        """
        Retreives a block from the buffer, but first evaluates if the block has not already been loaded.

        :param blockno: Requested block.
        """
        if self.oldBlockNo == blockno and self.channelChangeFlag == False:
            return self.currentBlock
        else:
            self.currentBlock = self.buffer.getBlock(self.channel, blockno).getData()
            self.oldBlockNo = blockno
            self.channelChangeFlag = False
            return self.currentBlock

    def setPos(self, smp, channel):
        """
        Sets the playback on the specified position and channel.

        :param smp: An integer representing the sample from which to start playing.
        :param channel: A Channel object referring to the channel to play.
        """
        if self.channel != channel:
            self.channelChangeFlag = True
        self.channel = channel
        self.smp = smp

    def __del__(self):
        """
        Closes streams and callbacks before destroying the object.
        """
        self.stream.close()
        self.p.terminate()

    def callback(self, in_data, frame_count, time_info, status):
        """
        PyAudio callback, used to feed new samples for playback.

        :param in_data: See PyAudio documentation.
        :param frame_count: See PyAudio documentation.
        :param time_info: See PyAudio documentation.
        :param status: See PyAudio documentation.
        :return: See PyAudio documentation.
        """
        self.__getChunk__()
        self.sendPos.emit(self.smp, self.channel)
        self.smp += self.chunkSize
        self.data = b"".__add__(self.chunk)
        return self.data, pyaudio.paContinue

    def play(self):
        """
        Start playback from the last known position.
        """
        self.playing = True
        self.stream.start_stream()

    def pause(self):
        """
        Pause the current playback.
        """
        self.playing = False
        self.stream.stop_stream()

    def isPlaying(self):
        """
        Is it playing?

        :return: True if playback ongoing.
        """
        return self.playing
