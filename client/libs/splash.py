from PySide6 import QtCore, QtWidgets, QtGui

from . import settings

class Splash(QtWidgets.QLabel):
    def __init__(self, settings):
        super().__init__()
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.setText("Logo")
        self.setWindowTitle("Loading...")
        self.setPixmap(settings.getLogo(256))
        self.resize(self.pixmap().size())
        
        # move the splash screen to the center of the screen
        self.move(self.screen().geometry().center() - self.frameGeometry().center())

        # set the splash screen to be transparent
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        # set timer to close the splash screen after 2.5 seconds
        QtCore.QTimer.singleShot(4000, self.close)
