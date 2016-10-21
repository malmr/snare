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

from EditorBackend.Waveform import Waveform
from EditorBackend.WaveformBufferChannel import WaveformBufferChannel
from EditorBackend.WaveformThread import WaveformThread


class WaveformBuffer(QObject):

    """
    At TrackWaveform only waveforms are stored that are currently displayed. To avoid the computationally intense
    rendering of new waveforms, every waveform that has been rendered will be stored in an object of this class.
    E.g. if a waveform was rendered and then the user changed the zoom-level, so that the TrackWaveform dropped all
    waveform objects, and then the user likes to return to the previous zoom-level, all waveforms are still available
    from the WaveformBuffer without the need to render again.
    WaveformBuffer takes a waveform request, looks up if it has been rendered already and either immediately returns
    the rendered waveform or creates an unrendered waveform to put on the stack of a render WaveformThread.
    """

    returnWaveform = pyqtSignal(Waveform)
    updateWaveformMessage = pyqtSignal(int)

    def __init__(self, buffer, sampleWidth, blockSize, waveformHeight):
        """
        Initialising and reservong memory for WaveformBufferChannels.

        :param buffer: Reference to the buffer to receive sample data from.
        :param sampleWidth: The sample width in bytes
        :param blockSize: The global block size
        :param waveformHeight: The height of one waveform
        """
        super(WaveformBuffer, self).__init__()

        self.mutex = QMutex()

        self.buffer = buffer
        self.sampleWidth = sampleWidth
        self.blockSize = blockSize
        self.waveformHeight = waveformHeight

        self.channelLoad = dict()
        self.waveformBufferChannels = dict()

        self.waveformThread = WaveformThread(self.sampleWidth, self.blockSize, self.mutex)
        self.waveformThread.finishedWaveform.connect(self.addWaveform)
        self.waveformThread.updateMsg.connect(self.formatWaveformMessage)
        self.waveformThread.start()

    def addChannel(self, channel):
        """
        Adding a channel in the backend will add a WaveformBufferChannel in this object.

        :param channel: Reference to a channel object to associate with the right sample data when accessing the buffer.
        """
        waveformBufferChannel = WaveformBufferChannel(self.buffer, self.sampleWidth,
            self.blockSize, self.waveformHeight, channel, self.mutex, self.waveformThread)

        waveformBufferChannel.returnWaveform.connect(self.returnWaveform)

        self.waveformBufferChannels[channel] = waveformBufferChannel


    def deleteChannel(self, channel):
        """
        Simply remove the WaveformBufferChannel that is associated with thc given Channel object.

        :param channel: s.a.
        """
        del self.waveformBufferChannels[channel]

    def formatWaveformMessage(self, load):
        """
        Slot called from a WaveformBufferChannel's render thread. Collects the current queue size from all threads
        (inside of WaveformBufferChannels), adds them up and sends a  message, which will be used to update the status
        bar.

        :param channel: Channel from which the update was sent.
        :param load: Current workload of that channel.
        """
        self.updateWaveformMessage.emit(load)

    def getWaveform(self, channel, startBlock, dataBlocks, numberOfPixmaps):
        """
        Request to return a rendered waveform. Simply relayed to the responsible WaveformbufferChannel.

        :param channel: Channel object linking to the responsible WaveformBufferChannel.
        :param blockNumber: The block to be rendered.
        :param width: Width of the waveform pixmap, equals zoom-level.
        """
        self.waveformBufferChannels[channel].getWaveform(startBlock, dataBlocks, numberOfPixmaps)

    def addWaveform(self, waveform):
        """
        Return path for rendered waveforms. Will be transmitted through the MainBackend to the TrackManager.

        :param waveform: A rendered waveform-object.
        """
        self.waveformBufferChannels[waveform.channel].addWaveform(waveform)
