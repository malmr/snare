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

import queue
import time
import sys
import struct
import traceback
import gc
import time
import numpy as np
from operator import itemgetter

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.Qt import (Qt, QPolygon)

from EditorBackend.Waveform import Waveform
from EditorBackend.Unpacker import Unpacker

class WaveformThread(QThread):

    """
    This class runs the computationally intensive rendering of sample data to waveform points list. It runs in its own
    thread. (It is not a real thread due to python's GIL, but it still allows the User-Interface to be more responsive
    by switching between "threads".)
    The samples to be rendered into waveforms are contained in the waveform object. The thread will get
    unrendered waveform objects loaded onto a queue and emit rendered waveforms through a signal. There is also a signal
    for communicating the current workload. Apart from that, there is no communication with the main thread.
    """

    finishedWaveform = pyqtSignal(Waveform)
    updateMsg = pyqtSignal(int)

    def __init__(self, sampleWidth, blockSize, mutex):
        """
        Initialise the queue, reserve memory and define maximum values.

        :param sampleWidth: The sample width in Bytes (24bit -> 3 Bytes)
        :param blockSize: The expected block size to render onto
        """
        QThread.__init__(self)
        self.mutex = mutex
        self.sampleWidth = sampleWidth
        self.blockSize = blockSize
        self.unpacker = Unpacker(self.blockSize, self.sampleWidth)

        self.waveforms = queue.LifoQueue()
        #self.waveforms = queue.Queue()

        if not (self.sampleWidth == 2 or self.sampleWidth == 3):
            raise BaseException("Unsupported Samplewidth")

        self.maximum = 2**(8*self.sampleWidth)-1
        if self.sampleWidth == 3:
            self.maximum *= 256

        self.polygonLinear = QPolygon()
        self.polygonQuadratic = QPolygon()
        self.queueLength = 0

    def __del__(self):
        """
        Procedure to close thread.
        """
        self.wait()

    def add(self, waveform):
        """
        Slot for backend to add waveform objects to queue.

        :param waveform: A waveform object.
        """
        self.waveforms.put(waveform)
        self.queueLength += 1

    def run(self):
        """
        This method starts the thread. When started the thread will work on its queue and if empty check every second
        for new jobs.
        """
        while True:
            while not self.waveforms.empty():
                self.draw()
            time.sleep(1)

    def points(self, width, height, blocks):
        """
        This method creates two lists containing coordinates for Drawing the waveform. The x-coordinates range
        from 0 to width-1. Y-coordinates represent the maximum or an average of the sample area. All coordinates are
        mirrored to create the usual symmetrical waveform shape. The algorithm was optimised for low memory usage.
        Even though the algorithm would be faster when operating on larger chunks of samples, python does not allow
        control over mallocs. A previous version of this algorithm had the problem that python would request new memory
        faster then it would free unused memory, (Although this algorithm would only need a static amount of memory)
        eventually reaching the memory limit for a 32bit-python. Especially with the version of this algorithm using
        numpy: Numpy cannot alter arrays in place, every operation on an array creates a copy, demanding new memory in
        big blocks.

        :param width: Range of x-coordinates
        :param height: Maximum for y-coordinates.
        :param blocks: List of AudioBlocks to be used as data source
        :return: Tuple of two lists, containing coordinates for the maximums-plot and the averages-plot
        """

        # How many samples make one pixel
        windowsize = int(len(blocks)*self.blockSize / width)

        # How many windows per block
        windowsPerBlock = int(self.blockSize / windowsize)

        #Scaling
        heightOffset = height / 2
        y_scaling = height / self.maximum

        # unpack format
        fmt = None
        if self.sampleWidth == 2:
            fmt = str(windowsize) + "h"
        elif self.sampleWidth == 3:
            fmt = str(windowsize) + "i"

        pointsMax = list()
        pointsMin = list()
        cnt = 0

        # Padding
        pad = windowsize - (self.blockSize % windowsize)
        # Space for remain
        data = bytearray()
        for block in blocks:
            if self.sampleWidth == 2:
                data += block.getData()
                data += bytearray((windowsize*self.sampleWidth) - len(data) % (windowsize*self.sampleWidth))
            elif self.sampleWidth == 3:
                hans = block.getData()
                peter = bytearray(self.blockSize*4)
                peter[1::4] = hans[0::3]
                peter[2::4] = hans[1::3]
                peter[3::4] = hans[2::3]
                peter += bytearray((windowsize*4) - (len(peter)+len(data)) % (windowsize*4))
                data += peter

            it = struct.iter_unpack(fmt, data)

            # Calculate each window in a block
            if self.sampleWidth == 2:
                windowsPerBlock = int( (len(data)/2) / windowsize)
            elif self.sampleWidth == 3:
                windowsPerBlock = int( (len(data)/4) / windowsize)

            for window in range(0, windowsPerBlock):
                chunk = next(it)
                maximum = max(chunk)

                # ToDo Compare these two options
                #average = sum(abs(i) for i in chunk)
                average = np.sum(np.abs(chunk))

                average /= windowsize

                # X
                pointsMax.append(cnt)
                # Y (Max top)
                pointsMax.append(maximum*y_scaling + heightOffset)
                # X
                pointsMax.append(cnt)
                # Y (Max bottom)
                pointsMax.append(-maximum*y_scaling + heightOffset)
                # X
                pointsMin.append(cnt)
                # Y (Min top)
                pointsMin.append(average*y_scaling + heightOffset)
                # X
                pointsMin.append(cnt)
                # Y (Min bottom)
                pointsMin.append(-average*y_scaling + heightOffset)

                cnt += 1
                if cnt > 999:
                    cnt = 0
            # Carry remaining piece to next block
            if self.sampleWidth == 2:
                data = data[windowsPerBlock*windowsize*self.sampleWidth:self.blockSize*self.sampleWidth]
            elif self.sampleWidth == 3:
                data = data[windowsPerBlock*windowsize*4:self.blockSize*4]
        for block in blocks:
            block.free()

        return [pointsMax, pointsMin]

    def draw(self):
        """
        Computes the list of points to a pixmap drawing. In this setup will create a layering of Peak and RMS display.
        For close zoom levels it switches to the linear display and also uses spreads out the entire waveform-drawing
        over several pixmaps (subblocks) to account for a limited maximum size of QPixmaps. Finished pixmaps are sent
        to the backend through a signal. New: pixmap rendering has been moved to TrackWaveform.
        """

        self.mutex.lock()
        waveform = self.waveforms.get()

        try:
            [waveform.pointsMax, waveform.pointsRMS] = self.points(1000*waveform.numberOfPixmaps, waveform.height, waveform.dataSrc)

        except:
            print(traceback.format_exc())
            waveform.memoryError = True
        else:
            waveform.rendered = True
            waveform.memoryError = False
        self.finishedWaveform.emit(waveform)
        self.queueLength -= 1
        self.updateMsg.emit(self.queueLength)

        self.mutex.unlock()

