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
from EditorBackend.WavFile import WavFile
import numpy as np
from EditorBackend.WavFileWrite import WavFileWrite
import time
from EditorBackend.Channel import Channel
from EditorBackend.Unpacker import Unpacker

from PyQt5.QtCore import *


class AudioBlock:

    """
    The Buffer's audio data storage is organised in AudioBlocks. An AudioBlock does not necessarily contain sample data.
    If there is no sample data stored in the Audioblock, the AudioBlock knows how and where to get it from (has a
    reference to the WavFile-object). Sample data should only be accessed through the getData interface. That way, if
    no sample data is present, the AudioBlock will load it by itself. There is also an interface for releasing memory.
    """
    def __init__(self, source, start, channel=0):
        """
        Defines the initial state of the AudioBlock.

        :param source: Source for sample data with the interface source.getBlock, usually WavFile
        :param start: Start sample in the line of blocks
        :param channel: A Channel object to identify the block.
        """
        self.inMemory = False
        self.array = bytearray()
        self.source = source
        self.start = start
        self.empty = False
        self.channel = channel

        self.averages = list()
        self.maximums = list()

    def readdata(self):
        """
        Reads data from the source and writes it to memory.
        """
        b = self.source.getBlock(self.start, self.channel)
        self.array.extend(b)
        self.inMemory = True

    def setdata(self, data):
        """
        Manually write data to the AudioBlock, without a source. (Used for Recording)

        :param data: A raw bytearray
        """
        self.array = data
        self.inMemory = True

    def free(self):
        """
        Delete the data to free memory.
        """
        if self.source is not None:
            self.inMemory = False
            self.array.clear()

    def isEmpty(self):
        """
        Is it an EmptyBlock?

        :return: True if it is an EmptyBlock.
        """
        return self.empty

    def getData(self):
        """
        Interface to retrieve raw sample data.

        :return: A raw bytearray
        """
        if self.inMemory is False:
            self.readdata()
        return self.array


class EmpytBlock(AudioBlock):
    """
    Empty blocks are used when somehow data is requested form an area where the file already ends.
    """

    def __init__(self, source, start, channel= 0, arraySize=None):
        """
        Defines the initial state of the EmptyBlock

        :param source: Source for sample data with the interface source.getBlock, usually WavFile
        :param start: Start sample in the line of blocks
        :param channel: A Channel object to identify the block.
        """
        self.inMemory = True
        self.empty = True
        self.array = bytearray(arraySize)

    def free(self):
        """
        This is overwritten because deleting nothing would not make much sense.
        """
        pass


class Buffer(QObject):

    """
    The Buffer class provides SNARE's storage for audio data. Data can be accessed in a block-wise manner or via a list
    of selection points from TrackSelection. Data can be added by specifying a source WAVE-file or from the Recorder.
    """
    updateFromRecorder = pyqtSignal(int)

    def __init__(self, sampleRate, sampleWidth, blockSize):
        """
        Creates the dictionaries for the actual data storage and an unpack-object to convert from raw bytearray to a
        numpy array.

        :param sampleRate: The global sample rate.
        :param sampleWidth: The global sample width.
        :param blockSize: The global blocksize.
        """
        super(Buffer, self).__init__()

        self.sampleRate = sampleRate
        self.sampleWidth = sampleWidth
        self.blockSize = blockSize

        self.unpacker = Unpacker(self.blockSize, self.sampleWidth)

        self.recordingChannels = dict()
        # Write one wav-File for each recording channel
        self.wavWriters = dict()

        self.data = dict()

        # Empty Block for out of Range access
        self.emptyBlock = EmpytBlock(None, None, None, self.blockSize*self.sampleWidth)

        # Required Interface#

    def loadWave(self, filename):
        """
        This is the procedure to add a WAVE-file to the buffer. No data from the file is read. Only the right amount
        of empty Audioblocks is prepared. Data is only read from disk when needed.

        :param filename: Full path to file to be loaded.
        :return: List of newly created Channel objects.
        """
        newchannels = list()
        try:
            wav = WavFile(filename, self.sampleRate, self.sampleWidth, self.blockSize)
        except:
            print("Load Wave failed: " + filename)
        else:
            blocks = wav.blockCount()
            channelCount = wav.channelCount()
            channels = list()

            for fileChannel in range(channelCount):
                shortname = filename.split("/")[-1] + "[" + str(fileChannel) + "]"
                channel = Channel("File", shortname)
                audioblocks = list()
                for block in range(blocks):
                    audioblock = AudioBlock(wav, block * self.blockSize, fileChannel)
                    audioblocks.append(audioblock)
                self.data[channel] = audioblocks
                channel.length = blocks*self.blockSize
                newchannels.append(channel)
            wav.start()
        return newchannels

    def getBlock(self, channel, block):
        audioblock = None
        try:
            audioblock = self.data[channel][block]
        except:
            audioblock = self.emptyBlock
        return audioblock

    def addRecording(self, deviceChannels, deviceName):
        """
        Prepares the buffer for receiving recording data.

        :param deviceChannels: List of channels to record.
        :param deviceName: Name of the device to record from.
        :return: Dictionary linking the numerical device channels with Channel objects.
        """
        # Which hardware channel maps to which buffer channel
        self.recordingChannels = dict()

        for deviceChannel in deviceChannels:
            fileName = time.strftime(deviceName + "_[" + str(deviceChannel))
            channel = Channel("Recording", fileName)
            channel.recording = True
            fileName = time.strftime("%d.%m.%Y-%H.%M.%S__" + fileName + "].wav")
            self.recordingChannels[deviceChannel] = channel

            audioblocks = list()
            self.data[channel] = audioblocks
            self.wavWriters[deviceChannel] = WavFileWrite(fileName, self.sampleRate,
                                                          self.sampleWidth, 1, self.blockSize)
        return self.recordingChannels

    def closeRecording(self):
        """
        Closes the recording, which means that the corresponding WAVE-file will be completed. Then the buffer reopens
        the WAVE-file in read-mode. Therefore the type of channel is changed.
        """
        for deviceChannel in self.wavWriters:
            # Close as recording Chanel
            self.wavWriters[deviceChannel].close()
            fileName = self.wavWriters[deviceChannel].fileName
            self.wavWriters[deviceChannel].__del__()

            # Reopen as file-channel
            print("opening:", fileName)
            wav = WavFile(fileName, self.sampleRate, self.sampleWidth, self.blockSize)
            bufferChannel = self.recordingChannels[deviceChannel]
            for block in self.data[bufferChannel]:
                block.source = wav

    def appendData(self, data, deviceChannel, length):
        """
        Slot for the recorder to add recorded data. Input data will be stored in the buffer and also written to disk
        with WavFileWrite.

        :param data: The input array, a raw bytearray.
        :param deviceChannel: The device channel it is from.
        :param length: and the length of data.
        """
        try:
            channel = self.recordingChannels[deviceChannel]
            block = AudioBlock(None, self.blockSize*length, channel)
            block.setdata(data)
            self.data[channel].append(block)
            self.wavWriters[deviceChannel].appendBlock(data)
            smp = len(self.data[channel])*self.blockSize
            self.updateFromRecorder.emit(smp)
        except KeyError:
            print("Channel not listed")

    def deleteChannel(self, channel):
        """
        Removes the specified channel from the buffer.

        :param channel: The channel to remove.
        """
        del self.data[channel]

    def getSelection(self, channel, points):
        """
        When the user has selected the areas on the data that he wants to analyze, it would not make sense to transmit
        blocks. Instead the selected areas are extracted from their respective blocks and joined together to one numpy
        array.

        :param channel: The channel on which the selection was made.
        :param points: The list of start and end samples marking the selected areas.
        :return: A numpy array of unpacked sample data.
        """
        selection = None

        start = None
        end = None

        for smp in sorted(points):
            if points[smp] == "start":
                start = smp
            elif points[smp] == "end":
                end = smp

                # Get this buffer portion
                block = self.getArray(channel, start, end)
                if selection is None:
                    selection = np.array(block)
                else:
                    selection = np.append(selection, block)
        return selection

    def getArray(self, channel, start, end):
        """
        Since a user analysis selection might consist of several marked areas, this method helps by returning an array
        from the blocked-buffer starting at "start" to "end"

        :param channel: The channel on which the selection was made.
        :param start: The sample on which this portion of the selection starts.
        :param end: The sample on which this portion of the selection ends.
        :return: A numpy array of unpacked sample data.
        """
        array = None
        # Avoid floats when indexing
        start = int(start)
        if start < 0:
            start = 0
        end = int(end)
        # Determine from which blocks to read data
        startblock = int(start/self.blockSize)
        endblock = int(end/self.blockSize)+1

        # Read data and convert into numpyarray
        for blockNumber in range(startblock, endblock):
            data = self.getBlock(channel, blockNumber).getData()
            block = self.unpacker.unpack(data)

            if array is None:
                array = np.array(block)
            else:
                array = np.append(array, block)

        # Cut off overlap
        # Selection starts at this smp in the first block
        startSmp = start-(startblock*self.blockSize)
        array = np.array(array[startSmp::])

        # Reduce to correct length
        endSmp = end - start
        array = np.array(array[:endSmp:])

        return array
