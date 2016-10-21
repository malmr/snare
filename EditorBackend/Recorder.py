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
from PyQt5.QtCore import *


class Recorder(QObject):

    """
    This class provides an interface to a non-blocking pyaudio recording stream. The interleaved channels of the raw
    input stream are separated, collected to form blocks of a certain size and the resulting bytearray is sent to a
    buffer object. The status of the object is communicated through a signal and displayed at the status bar.
    """

    updateRecording = pyqtSignal(str)
    sendRecPos = pyqtSignal(int)

    def __init__(self, buffer, sampleRate, sampleWidth, blockSize):
        """
        The constructor only reserves memory.

        :param buffer: Reference to a buffer object to send raw sample data to.
        :param sampleRate: Global sample rate to use device with.
        :param sampleWidth: Global sample width to use device with.
        :param blockSize: Global block size defining intervals to call the buffer
        :return:
        """

        super(Recorder, self).__init__()

        self.buffer = buffer
        self.sampleRate = sampleRate
        self.sampleWidth = sampleWidth
        self.blockSize = blockSize

        self.chunkSize = 8192
        self.tempBuffer = bytearray()

        self.p = None
        self.device = None
        self.deviceMaxChannels = None
        self.stream = None
        self.frameSize = None

        self.running = False
        self.ready = False

        self.length = 0

    def isRunning(self):
        """
        Is there a recording ongoing?

        :return: True if recording is ongoing.
        """
        return self.running

    def isReady(self):
        """
        Is the Recorder object ready for a recording (device set)?

        :return: True if Recorder is ready to record.
        """
        return self.ready

    def open(self, deviceIndex):
        """
        Open the given device for recording. Then set the object to be ready for recording.

        :param deviceIndex: PyAudio device index.
        """
        # Open Device
        self.tempBuffer.clear()
        self.length = 0
        self.p = pyaudio.PyAudio()
        self.device = deviceIndex
        self.deviceMaxChannels = self.p.get_device_info_by_index(deviceIndex)['maxInputChannels']
        self.stream = self.p.open(rate=self.sampleRate,
                                  channels=self.deviceMaxChannels,
                                  format=self.p.get_format_from_width(self.sampleWidth),
                                  input=True,
                                  input_device_index=self.device,
                                  frames_per_buffer=self.chunkSize,
                                  stream_callback=self.callback)
        self.stream.stop_stream()
        self.frameSize = self.deviceMaxChannels*self.sampleWidth
        self.ready = True
        self.updateRecording.emit("Ready for Recording")

    def record(self):
        """
        Starts the recording and updates the status.
        """
        if self.ready:
            self.stream.start_stream()
            self.running = True
            self.updateRecording.emit("Recording...")
        else:
            self.updateRecording.emit("Select Input first!")

    def pause(self):
        """
        Pauses the recording and updates the status. Remaining data in the temporary buffer will not be sent to the
        buffer, but also will not be lost.
        """
        self.stream.stop_stream()
        self.running = False
        self.updateRecording.emit("Recording pause.")

    def stop(self):
        """
        Stops the recording: The last remaining contents of the temporary buffer a zero padded to match the blocksize
        and sent to the buffer. Then the object is set back to the ready for recording state.
        """
        self.running = False
        self.ready = False
        self.stream.close()
        samplesInBuffer = int(len(self.tempBuffer)/self.frameSize)
        remaining = self.blockSize - samplesInBuffer
        self.tempBuffer += bytearray(remaining*self.frameSize)
        self.sendToBuffer(self.tempBuffer)
        self.updateRecording.emit("Recording stopped.")

    def callback(self, in_data, frame_count, time_info, status):
        """
        A PyAudio method called every time a chunckSize amount of samples have been recorded. The new samples are added
        to the temporary buffer until a blockSize is reached. At this point the new block is sent to the buffer and the
        temporary buffer is reset.

        :param in_data: see PyAudio Reference.
        :param frame_count: see PyAudio Reference.
        :param time_info: see PyAudio Reference.
        :param status: see PyAudio Reference.
        :return: see PyAudio Reference.
        """
        self.length += self.chunkSize
        self.updateRecording.emit("Recorded " + str(int(self.length/self.sampleRate)) + "s")
        self.tempBuffer += in_data
        samplesInBuffer = int(len(self.tempBuffer)/self.frameSize)
        if samplesInBuffer >= self.blockSize:
            self.sendToBuffer(self.tempBuffer[0:self.frameSize*self.blockSize])
            self.tempBuffer = self.tempBuffer[self.frameSize*self.blockSize:len(self.tempBuffer)]
        self.sendRecPos.emit(self.length)
        return None, pyaudio.paContinue

    def sendToBuffer(self, data):
        """
        Before sending the unformatted bytearray to the buffer it is filtered for the channels. Wanted channels are
        separated, according to the same principle to solve the WAVE-file channel interweaving. Unwanted channels are
        ignored.

        :param data: Channel interweaved raw bytearray
        """
        for deviceChannel in range(self.deviceMaxChannels):
            c = bytearray(self.blockSize*self.sampleWidth)
            c[0::self.sampleWidth] = data[deviceChannel*self.sampleWidth::self.deviceMaxChannels*self.sampleWidth]
            c[1::self.sampleWidth] = data[deviceChannel*self.sampleWidth+1::self.deviceMaxChannels*self.sampleWidth]
            if self.sampleWidth == 3:
                c[2::self.sampleWidth] = data[deviceChannel*self.sampleWidth+2::self.deviceMaxChannels*self.sampleWidth]
            self.buffer.appendData(c, deviceChannel, self.length)




