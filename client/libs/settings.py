from PySide6 import QtCore, QtGui

class Settings:
    def __init__(self):
        self.cwd = QtCore.QDir.currentPath()

    def setCWD(self, dir : str): # CWD = Current Working Directory
        self.cwd = dir

    def getCWD(self):
        return self.cwd
    
    def getLogo(self, size : int) -> QtGui.QPixmap:
        return QtGui.QPixmap(self.cwd + "/images/remoter.png").scaled(size, size, QtCore.Qt.AspectRatioMode.KeepAspectRatioByExpanding)
        