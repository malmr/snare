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
from PyQt5 import Qt
import math
import time


class WavFile(QThread):
    """
    This class reads standard RIFF-WAVE-files and BWF-WAVE-files. Once successfully opened, raw audio data can be
    accessed in blocked segments by providing the channel number and a sample to start from. 16bit and 24bit files
    are supported as well as audio-files with an arbitrary number of channels.

    :Example:

    file = 'test.wav'
    sampleRate = 44100
    sampleWidth = 2
    blockSize = 441000 # 10 seconds per block

    wav = WavFile(file, sampleRate, sampleWidth, blockSize)

    startSample = 30 * sampleRate # read 10 seconds starting from 0:30
    leftChannel = 0

    rawData = wav.getBlock(startSample, leftChannel)
    
    #rawData could now be fed to e.g. a pyaudio callback
    """

    def __init__(self, fileName, sampleRate, sampleWidth, blockSize):
        """
        :param fileName: Full path to file (or only name if in same directory)
        :param sampleRate: in Hz. It will be checked if sampleRate matches the sample rate of the file.
                            If not, an exception will be raised. Checking will be ignored if type is None.
        :param sampleWidth: in Bytes!: 16bit -> sampleWidth = 2. It will be checked if sampleWidth matches the sample
                            width of the file. If not, an exception will be raised. Checking will be ignored if type is
                            None.
        :param blockSize: number of samples to return per getBlock() request.
        :return: WavFile-object containing an opened QDataStream of the file at fileName
        """
        super(WavFile, self).__init__()

        self.mutex = QMutex()

        self.fileName = fileName
        self.sampleRate = sampleRate
        self.sampleWidth = sampleWidth
        self.blockSize = blockSize

        # This header length applies to a standard RIFF-Wave
        # other formats extend the header length
        self.headerLength = 44 # Applies to standard RIFF

        self.file = QFile(self.fileName)

        try:
            self.file.open(Qt.QIODevice.ReadOnly)
        except:
            raise("Can't open WAVE-File " + self.fileName)

        self.stream = QDataStream(self.file)

        # RIFF
        self.RIFF = None
        self.SIZE = None
        self.WAVE = None

        # FMT
        self.FMT = None
        self.FMT_LENGTH = None
        self.FORMAT_TAG = None
        self.CHANNELS = None
        self.SAMPLE_RATE = None
        self.BYTES_SECOND = None
        self.BLOCK_ALIGN = None
        self.BITS_SAMPLE = None

        self.channels = None
        self.sampleRateFromFile = None
        self.frameLength = None
        self.sampleWidthFromFile = None

        # DATA
        self.DATA = None
        self.LENGTH = None

        self.length = None
        self.__readHeader__()

        if self.sampleRate is None:
            self.sampleRate = self.sampleRateFromFile
        if self.sampleWidth is None:
            self.sampleWidth = self.sampleWidthFromFile

        if not (self.sampleRate == self.sampleRateFromFile and self.sampleWidth == self.sampleWidthFromFile \
                and self.__valid__()):
            self.printHeader()
            raise BaseException("WAVE-File not valid: " + str(self.fileName))

    def printHeader(self):
        """
        Prints entire RIFF-Header section to shell.
        """
        self.__printRIFF__()
        self.__printFMT__()
        self.__printDATA__()

    def blockCount(self):
        """
        Gets the length of the audio stream in blocks. Full length of audiostream would be blockCount()*blockSize

        :return: Length of audiostream in blocks, always rounded up.
        """
        return int(math.ceil(self.length / (self.sampleWidth * self.channels * self.blockSize)))

    def channelCount(self):
        """
        Gets the number of channels present in the WAVE-file

        :return: number of channels
        """
        return self.channels

    def getFileInfo(self):
        """
        To access basic file-information. At the moment only sampleRate and sampleWidth

        :return: Dictionary containing file information. Keys: 'sampleRate', 'sampleWidth'.
        """
        fileInfo = dict()
        fileInfo["sampleRate"] = self.sampleRate
        fileInfo["sampleWidth"] = self.sampleWidth
        return fileInfo
        #return self.sampleRate, self.sampleWidth

    def getBlock(self, start, channel):
        """
        Read block wise raw data from wav-file. Meaning that this method will always return a full block, if necessary
        a zero-padded block or even an entirely empty block.

        :param start: number of sample to start reading from. E.g. start = 88200 will read form 0:02s onwards.
        :param channel: 0 -> Left Channel, 1 -> Rigth Channel, n -> further channels
        :return: Returns raw unformatted audio data as bytearray. This means that e.g. in an 24bit-file three consecutive bytearray elements form one sample.
        """
        pos = self.headerLength + (start * self.channels * self.sampleWidth)

        # Pad bytes for uneven lenghts
        if self.length % 2 != 0:
            pos -= 1

        fileLength = self.length + self.headerLength
        self.file.seek(pos)
        # Block fully in file
        if (pos + self.blockSize*self.sampleWidth*self.channels) <= fileLength:
            ret = self.__readSamples__(self.blockSize, channel)
            return ret
        # Block partially contained
        else:
            containedpart = fileLength - pos
            remainingpart = self.blockSize*self.sampleWidth*self.channels - containedpart

            containedpart = int(containedpart / (self.channels*self.sampleWidth))
            remainingpart = int(remainingpart / (self.channels*self.sampleWidth))

            # Block not contained at all
            if containedpart <= 0:
                return bytearray(self.blockSize*self.sampleWidth)
            temp = self.__readSamples__(containedpart, channel)
            ret = temp.__add__(b"".__add__(bytearray((remainingpart+1)*self.sampleWidth)))
            return ret

    def __readSamples__(self, blockSize, channel=0):
        """
        This private method reads the actual bytes from the file and solves the channel interweaving.

        :param blockSize: Number of samples to read, can vary from the global blocksize to account for the end of file
        :param channel: The channel from which to read, other channels are skipped.
        :return:
        """
        if channel >= self.channels:
            raise BaseException("No such Channel")

        try:
            #b = b"".__add__(self.stream.readRawData(blockSize*self.sampleWidth*self.channels))
            b = self.stream.readRawData(blockSize*self.sampleWidth*self.channels)
            c = bytearray(len(b)//self.channels)

            c[0::self.sampleWidth] = b[channel*self.sampleWidth::self.channels*self.sampleWidth]
            c[1::self.sampleWidth] = b[channel*self.sampleWidth+1::self.channels*self.sampleWidth]
            if self.sampleWidth == 3:
                c[2::self.sampleWidth] = b[channel*self.sampleWidth+2::self.channels*self.sampleWidth]

        except MemoryError:
            raise MemoryError

        return c

    def __printRIFF__(self):
        """
        Prints RIFF part of header.
        """
        print("RIFF: " + str(self.RIFF))
        print("SIZE: " + str(int.from_bytes(self.SIZE, byteorder="little")))
        print("WAVE: " + str(self.WAVE))

    def __printFMT__(self):
        """
        Prints FMT part of header.
        """
        print("FMT: " + str(self.FMT))
        print("FMT_LENGTH: " + str(int.from_bytes(self.FMT_LENGTH, byteorder="little")))
        print("FORMAT_TAG: " + str(int.from_bytes(self.FORMAT_TAG, byteorder="little")))
        print("CHANNELS: " + str(int.from_bytes(self.CHANNELS, byteorder="little")))
        print("SAMPLE_RATE: " + str(int.from_bytes(self.SAMPLE_RATE, byteorder="little")))
        print("BYTES_SECOND: " + str(int.from_bytes(self.BYTES_SECOND, byteorder="little")))
        print("BLOCK_ALIGN: " + str(int.from_bytes(self.BLOCK_ALIGN, byteorder="little")))
        print("BITS_SAMPLE: " + str(int.from_bytes(self.BITS_SAMPLE, byteorder="little")))

    def __printDATA__(self):
        """
        Prints header part of DATA header.
        """
        print("DATA: " + str(self.DATA))
        print("LENGTH: " + str(int.from_bytes(self.LENGTH, byteorder="little")))

    def __readHeader__(self):
        """
        Reads the entire header section.
        """
        self.__readRIFF__()
        self.__readFMT__()
        self.__readDATA__()

    def __readRIFF__(self):
        """
        Reads the RIFF part of header. For a valid WAVE-file the size of this portion is always 12 Bytes.
        """
        self.RIFF = self.stream.readRawData(4)
        self.SIZE = self.stream.readRawData(4)
        self.WAVE = self.stream.readRawData(4)

    def __readFMT__(self):
        """
        Reads the FMT part of header. For a valid WAVE-file the size of this portion is always 24 Bytes
        :return:
        """
        self.FMT = self.stream.readRawData(4)
        self.FMT_LENGTH = self.stream.readRawData(4)
        self.FORMAT_TAG = self.stream.readRawData(2)
        self.CHANNELS = self.stream.readRawData(2)
        self.channels = int.from_bytes(self.CHANNELS, byteorder="little")
        self.SAMPLE_RATE = self.stream.readRawData(4)
        self.sampleRateFromFile = int.from_bytes(self.SAMPLE_RATE, byteorder="little")
        self.BYTES_SECOND = self.stream.readRawData(4)
        self.BLOCK_ALIGN = self.stream.readRawData(2)
        self.frameLength = int.from_bytes(self.BLOCK_ALIGN, byteorder="little")
        self.BITS_SAMPLE = self.stream.readRawData(2)
        self.sampleWidthFromFile = int(int.from_bytes(self.BITS_SAMPLE, byteorder="little")/8)

    def __readDATA__(self):
        """
        Reads the header part of the DATA section. The length can vary if Broadcast Wave extensions are present. BWF
        header sections (bext, junk) are skipped.
        """
        self.DATA = self.stream.readRawData(4)
        self.LENGTH = self.stream.readRawData(4)
        self.length = int.from_bytes(self.LENGTH, byteorder="little")

        # Skip metadata-chunks of Broadcast Wave Format
        if self.DATA == b'bext' or self.DATA == b'junk':
            self.headerLength =+ self.length
            self.stream.readRawData(self.length)
            self.__readDATA__()

    def __del__(self):
        """
        Close QDataStream.
        """
        self.file.close()

    def __valid__(self):
        """
        Compare file-header to standard.

        :return: True if all header signatures of a correct RIFF/BWF-WAVE-file were found
        """
        if self.RIFF == b"RIFF" and self.WAVE == b"WAVE":
            if self.DATA == b"data":
                if self.FORMAT_TAG == 0x1.to_bytes(2, byteorder="little"):
                    return 1
        return 0

    def run(self):
        pass
        #while True:
        #    print("Wav Thread alive!")
        #    time.sleep(1)