from PySide6.QtCore import Qt, QDir, QStandardPaths, QSettings
from PySide6.QtGui import QPixmap, QIcon

from libs import logger
lg = logger.logger()

class Settings:
    def __init__(self):
        self.cwd = QDir.currentPath()
        self.load()

    def load(self):
        setting_path = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppConfigLocation) + "/settings.ini"
        settings = QSettings(setting_path, QSettings.Format.IniFormat)

        settings.beginGroup("General")
        self.test_json = settings.value("test_json", '{}')
        settings.endGroup()
        settings.beginGroup("StatusService")
        self.status_service_address = settings.value("address", "axisflow.biz")
        self.status_service_port = settings.value("port", 5000, int)
        settings.endGroup()

    def save(self):
        setting_path = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppConfigLocation) + "/settings.ini"
        settings = QSettings(setting_path, QSettings.Format.IniFormat)
        
        settings.beginGroup("General")
        settings.setValue("test_json", self.test_json)
        settings.endGroup()
        settings.beginGroup("StatusService")
        settings.setValue("address", self.status_service_address)
        settings.setValue("port", self.status_service_port)
        settings.endGroup()

    def setCWD(self, dir : str): # CWD = Current Working Directory
        self.cwd = dir

    def getCWD(self):
        return self.cwd
    
    def getLogo(self, size : int) -> QPixmap:
        return QPixmap(self.cwd + "/images/remoter.png").scaled(size, size, Qt.AspectRatioMode.KeepAspectRatioByExpanding)
    
    def getLogoIcon(self) -> QIcon:
        return QIcon(self.cwd + "/images/remoter.png")
    
    def setStatusServer(self, address : str, port : int):
        self.status_service_address = address
        self.status_service_port = port

    def getStatusServer(self):
        return self.status_service_address, self.status_service_port
    
    def setTestJson(self, json : str):
        self.test_json = json

    def getTestJson(self):
        return self.test_json

    def __del__(self):
        self.save()
        