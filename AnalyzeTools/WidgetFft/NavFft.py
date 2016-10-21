from PyQt5.QtWidgets import *
from PyQt5.Qt import *
from PyQt5.QtCore import *
# import NavMenu base class for modification.
from AnalyzeTools.NavMenu import NavMenu


class NavFft(NavMenu):
    """Class for Analyze Widget Navigation. Derivated from "NavMenu" because additional Navigation (nth FFT)
    selection is needed."""
    # Analyze specific signals
    replot = pyqtSignal(str, str, str)

    def __init__(self):
        """
        Initialize variables and then set the layout.
        note:: Setting the layout is the same ending part of every custom Nav*.
        """
        super(NavFft, self).__init__()
        self.nthFftFrame = QVBoxLayout()
        self.nthFftText = QLabel("n-th Octave")
        self.nthFftText.setAlignment(Qt.AlignHCenter)
        self.nthFft = QComboBox()
        self.nthFft.addItems(["1", "3", "6", "12", "24"])
        self.nthFft.currentIndexChanged.connect(self.sendReplot)
        self.nthFftFrame.addWidget(self.nthFftText)
        self.nthFftFrame.addWidget(self.nthFft)

        # general end of AnalyzeWidgetNav*
        self.selectionLayout = QHBoxLayout()
        self.selectionLayout.addLayout(self.fqWeightingFrame)
        self.selectionLayout.addLayout(self.nthFftFrame)

        self.layout.addLayout(self.deleteFrame)
        self.layout.addLayout(self.selectionLayout)
        self.layout.addLayout(self.buttonFrame)
        self.setLayout(self.layout)

    def sendReplot(self):
        """
        Overwrite the Signal emit of NavMenu due to optional parameter.
        """
        timeWeight = str(self.timeWeighting.currentText())
        fqWeight = str(self.fqWeighting.currentText())
        # optional parm
        nthoctave = str(self.nthFft.currentText())

        self.replot.emit(timeWeight, fqWeight, nthoctave)
