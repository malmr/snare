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
from EditorBackend.WavFile import WavFile


class StartDialog(QDialog):

    """
    On startup of SNARE, this dialog is presented to the user. There is a choice between opening a WAVE-file (and
    setting sample rate and sample width this way) or manually selecting sample rate and sample width and then
    selecting an input device and channels (via InputSelectorDialog)
    """

    def __init__(self, result, icon):
        """
        Maunally creates the layout, including two dropdown menus and dictionaries associating the entries of the
        dropdown menus.

        :param result: The result of the user input is a dictionary containing entries at "sampleRate", "sampleWidth",
         "allFilesValid" and "fileNames"
        """
        super(StartDialog, self).__init__()

        self.setWindowTitle("SNARE - Configuration")
        self.setWindowIcon(icon)
        self.setAcceptDrops(True)
        self.result = result

        # Rückgabewerte
        self.sampleWidth = None
        self.sampleRate = None
        self.fileNames = None

        self.layout = QVBoxLayout()

        self.topLayout = QHBoxLayout()

        self.rateLabel = QLabel("Samplerate: ")
        self.topLayout.addWidget(self.rateLabel)

        self.rateSelect = QComboBox()
        self.rateSelect.addItem("44.1 kHz")
        self.rateSelect.addItem("48 kHz")
        self.rateSelect.addItem("96 kHz")
        self.topLayout.addWidget(self.rateSelect)

        self.rateDict = dict()
        self.rateDict["44.1 kHz"] = 44100
        self.rateDict["48 kHz"] = 48000
        self.rateDict["96 kHz"] = 96000

        self.widthLabel = QLabel(" and bit depth: ")
        self.topLayout.addWidget(self.widthLabel)

        self.widthSelect = QComboBox()
        self.widthSelect.addItem("16 bit")
        self.widthSelect.addItem("24 bit")
        self.topLayout.addWidget(self.widthSelect)

        self.widthDict = dict()
        self.widthDict["16 bit"] = 2
        self.widthDict["24 bit"] = 3

        self.layout.addItem(self.topLayout)

        self.confirmButton = QPushButton(clicked=self.confirm)
        self.confirmButton.setText("Record...")
        self.layout.addWidget(self.confirmButton)

        self.layout.addSpacing(10)

        self.divider = QFrame()
        self.divider.setFrameShape(QFrame.HLine)
        self.layout.addWidget(self.divider)

        self.layout.addSpacing(10)

        self.openFileButton = QPushButton(clicked=self.openFiles)
        self.openFileButton.setText("Open WAV")
        self.layout.addWidget(self.openFileButton)

        self.setLayout(self.layout)
        self.exec()

    def confirm(self):
        """
        Pressing "Record..." will lead to the InputSelectorDialog and only set sample rate and sample width.
        """
        self.result["sampleRate"] = self.rateDict[self.rateSelect.currentText()]
        self.result["sampleWidth"] = self.widthDict[self.widthSelect.currentText()]
        self.result["allFilesValid"] = False
        self.done(1)

    def openFiles(self, files=False):
        """
        Loop for opening Wav files. Triggered by pressing "Open Wav" or by Drag and Drop in the Window. If no valid
        wave-file has been selected, StartDialog will return to its initial state. First check if method is triggered by
        "Open Files..." button to open file dialog. Then make sure that filename is not empty, which is the case by
        canceling the file dialog.
        """
        if not files:
            files = QFileDialog.getOpenFileNames()

        if files[0]:
            self.result["fileNames"] = []
            for file in files[0]:
                try:
                    print('Opening File:', file)
                    self.openFile(file)
                except:
                    return
            self.result["allFilesValid"] = True
            self.done(1)

    def openFile(self, fileNames=False):
        """
        Opens a Wav File.
        """
        self.result["fileNames"].append(fileNames)

        try:
            wav = WavFile(fileNames, None, None, 1)
            fileInfo = wav.getFileInfo()
            self.result["sampleRate"] = fileInfo["sampleRate"]
            self.result["sampleWidth"] = fileInfo["sampleWidth"]
        except:
            print('Cant read', fileNames)
            self.result["fileNames"] = None
            self.result["allFilesValid"] = False
            raise Exception

    def dragEnterEvent(self, event):
        """
        Overwrites DragEnterEvent for Drag and Drop file support.
        """
        if event.mimeData().hasUrls:
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        """
        Overwrites DragMoveEvent for Drag and Drop file support.
        """
        if event.mimeData().hasUrls:
            event.setDropAction(Qt.CopyAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        """
        Overwrites DropEvent for Drag and Drop file support. Before passing to openFiles, fileNames is casted to the
        needed format.
        """
        if event.mimeData().hasUrls:
            event.setDropAction(Qt.CopyAction)
            event.accept()
            files = []
            for url in event.mimeData().urls():
                files.append(str(url.toLocalFile()))
            files = tuple([files]) + tuple([''])
            self.openFiles(files)
        else:
            event.ignore()
