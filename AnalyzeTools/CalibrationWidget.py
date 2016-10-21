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

from PyQt5.QtWidgets import *
from PyQt5.Qt import *
from AnalyzeTools.Calculation import Calculation
import numpy as np

class CalibrationWidget(QWidget):
    """Stores the calibration value of current selection (self.selNo) in SNARE's channel dependent 'calibrations'
    variable."""
    def __init__(self, snare, channel, selNo):
        super().__init__()
        self.channel = channel
        self.selNo = selNo
        self.snare = snare
        self.buffer = None
        self.calibration = None

    def calculate(self):
        self.buffer = np.array(self.snare.analyzeBuffer.selectionBuffers[self.channel][self.selNo])
        self.buffer = self.buffer.astype(np.float64)
        calc = Calculation(self.snare, None, None, None)
        self.calibration = calc.dbSplToPascal(calc.referenceDb) / calc.rms(self.buffer)
        self.snare.calibrations.addCalibration(self.channel, self.calibration)
        return self.calibration
