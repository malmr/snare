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

from collections import defaultdict
from PyQt5.Qt import *

from EditorBackend.Waveform import Waveform
from EditorBackend.WaveformThread import WaveformThread


class WaveformBufferChannel(QObject):

    """
    This is added as a layer between WaveformBuffer and the rendering threads. It makes it easier to add and delete
    channels, also multiple threads can work on the rendering.
    """

    returnWaveform = pyqtSignal(Waveform)
    updateWaveformMessage = pyqtSignal(int, int)

    def __init__(self, buffer, sampleWidth, blockSize, waveformHeight, channel, mutex, thread):
        """
        New: Manages the waveforms for one channel and feed waveform-requests, if necessary to the thread. Initialise
        two-dimensional dictionaries to store the waveforms in.

        :param buffer: Reference to the Buffer for receiving sample data
        :param sampleWidth: The global sample width
        :param blockSize: The global block size
        :param waveformHeight: Height of a waveform pixmap
        :param channel: The channel object that is linked with this WaveformBufferChannel
        """
        super(WaveformBufferChannel, self).__init__()

        self.buffer = buffer
        self.sampleWidth = sampleWidth
        self.blockSize = blockSize
        self.waveformHeight = waveformHeight
        self.channel = channel

        # List for easier checking if waveform exists
        self.waveformList = list()
        self.waveformObjectList = list()
        # 2D-Dictionary to store waveforms [block number]x[width]
        self.waveforms = defaultdict(lambda: defaultdict(dict))
        self.isRendered = defaultdict(lambda: defaultdict(dict))

        # outsource rendering to thread to keep UI responsive
        self.waveformThread = thread
        #self.waveformThread = WaveformThread(self.sampleWidth, self.blockSize, mutex)

        #self.waveformThread.start()
    def getWaveform(self, startBlock, dataBlocks, numberOfPixmaps):
        """
        Either check by the provided parameters if the waveform already exists or create an unrendered pixmap with
        the given parameters and data from the buffer.

        :param blockNumber: Block number to have a pixmap of
        :param width: Width of the requested pixmap equalling the zoom-level
        """
        empty = False
        if [startBlock, dataBlocks, numberOfPixmaps] in self.waveformList:
            if self.isRendered[startBlock][dataBlocks][numberOfPixmaps]:
                # Has already been calculated, immediately return
                waveform = self.waveforms[startBlock][dataBlocks][numberOfPixmaps]
                self.returnWaveform.emit(waveform)

            else:
                # Already in queue
                pass
        else:
            # Needs to be calculated on thread

            dataSrc = list()
            for blockNo in range(startBlock, startBlock+dataBlocks):
                block = self.buffer.getBlock(self.channel, blockNo)
                dataSrc.append(block)
                if block.isEmpty():
                    empty = True
            if not (self.channel.recording and empty):
                waveform = Waveform(self.channel, startBlock, dataBlocks, numberOfPixmaps, dataSrc)
                self.waveformList.append([startBlock, dataBlocks, numberOfPixmaps])
                self.waveformObjectList.append(waveform)
                self.isRendered[startBlock][dataBlocks][numberOfPixmaps] = False
                self.waveformThread.add(waveform)

    def addWaveform(self, waveform):
        """
        Return path for rendered pixmaps from the thread. Write into the dictionaries to avoid double renderings.
        Then free the AudioBlock to save memory.

        :param waveform: A rendered pixmap object.
        """
        if not waveform.memoryError:
            self.isRendered[waveform.startBlock][waveform.dataBlocks][waveform.numberOfPixmaps] = True
            self.waveforms[waveform.startBlock][waveform.dataBlocks][waveform.numberOfPixmaps] = waveform
            self.returnWaveform.emit(waveform)