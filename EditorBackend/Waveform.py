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

class Waveform:
    """
    Merely a data structure to simplify the handling of waveforms. This class contains space for sample data,
    which might be rendered by the WaveformThread to a cooridnate-list, which then can be sent to a TrackWaveform object
    to be painted and display to the user. It also contains information about the channel it belongs to and its position
    and size on the timeline.
    """

    def __init__(self, channel, startBlock, dataBlocks, numberOfPixmaps, dataSrc):

        self.channel = channel
        self.startBlock = startBlock
        self.dataBlocks = dataBlocks
        self.numberOfPixmaps = numberOfPixmaps

        self.dataSrc = dataSrc
        self.memoryError = False
        self.height = 100

        self.pointsMax = None
        self.pointsRMS = None