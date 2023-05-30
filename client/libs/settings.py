from PySide6.QtCore import Qt, QDir, QStandardPaths, QSettings
from PySide6.QtGui import QPixmap, QIcon

from .logger import logger as lg

class Settings:
    def __init__(self):
        self.cwd = QDir.currentPath()
        self.load()

    def load(self):
        setting_path = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppConfigLocation) + "/settings.ini"
        settings = QSettings(setting_path, QSettings.Format.IniFormat)

        settings.beginGroup("General")
        self.auto_locate_server = settings.value("auto_locate_server", True, bool)
        self.auto_login = settings.value("auto_login", True, bool)
        self.friends_id = settings.value("friends_id", [], list)
        self.test_json = settings.value("test_json", '{}')
        settings.endGroup()
        settings.beginGroup("Account")
        self.id = settings.value("ID", "")
        self.password = settings.value("password", "")
        settings.endGroup()
        settings.beginGroup("StatusService")
        self.status_service_address = settings.value("address", "axisflow.biz")
        self.status_service_port = settings.value("port", 5000, int)
        settings.endGroup()

    def save(self):
        setting_path = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppConfigLocation) + "/settings.ini"
        settings = QSettings(setting_path, QSettings.Format.IniFormat)
        
        settings.beginGroup("General")
        settings.setValue("auto_locate_server", self.auto_locate_server)
        settings.setValue("auto_login", self.auto_login)
        settings.setValue("friends_id", self.friends_id)
        settings.setValue("test_json", self.test_json)
        settings.endGroup()
        settings.beginGroup("Account")
        settings.setValue("ID", self.id)
        settings.setValue("password", self.password)
        settings.endGroup()
        settings.beginGroup("StatusService")
        settings.setValue("address", self.status_service_address)
        settings.setValue("port", self.status_service_port)
        settings.endGroup()

    def setCWD(self, dir : str): # CWD = Current Working Directory
        self.cwd = dir

    def getCWD(self):
        return self.cwd
    
    def getDefaultTerminal(self):
        return "cmd.exe"
    
    def getLogo(self, size : int) -> QPixmap:
        return QPixmap(self.cwd + "/images/remoter.png").scaled(size, size, Qt.AspectRatioMode.KeepAspectRatioByExpanding)
    
    def getLogoIcon(self) -> QIcon:
        return QIcon(self.cwd + "/images/remoter.png")
    
    def setStatusServer(self, address : str, port : int):
        self.status_service_address = address
        self.status_service_port = port

    def getStatusServer(self):
        return self.status_service_address, self.status_service_port
    
    def setAutoLocateServer(self, auto : bool):
        self.auto_locate_server = auto

    def getAutoLocateServer(self):
        return self.auto_locate_server
    
    def setAutoLogin(self, auto : bool):
        self.auto_login = auto

    def getAutoLogin(self):
        return self.auto_login
    
    def setID(self, id : str):
        self.id = id

    def getID(self):
        return self.id
    
    def setPassword(self, password : str):
        self.password = password

    def getPassword(self):
        return self.password
    
    def setTestJson(self, json : str):
        self.test_json = json

    def getTestJson(self):
        return self.test_json

    def __del__(self):
        self.save()
        