from PySide6.QtCore import Qt, QDir, QStandardPaths, QSettings, QJsonDocument, QByteArray, QRandomGenerator
from PySide6.QtGui import QPixmap, QIcon

from .logger import logger as lg

class Settings:
    def __init__(self):
        self.cwd = QDir.currentPath()
        self.settings_path = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppConfigLocation) + "/settings.ini"
        self.load()

    def load(self):
        settings = QSettings(self.settings_path, QSettings.Format.IniFormat)

        settings.beginGroup("General")
        self.auto_locate_server = settings.value("auto_locate_server", True, bool)
        self.auto_login = settings.value("auto_login", True, bool)
        self.friends_data = QJsonDocument.fromJson(settings.value("friends_data", b"{}", QByteArray)).toVariant()
        self.test_json = settings.value("test_json", '{}')
        settings.endGroup()
        settings.beginGroup("Account")
        self.id = settings.value("ID", "")
        self.password = settings.value("password", "")
        settings.endGroup()
        settings.beginGroup("StatusService")
        self.status_service_address = settings.value("address", "axisflow.biz", str)
        self.status_service_port = settings.value("port", 20001, int)
        settings.endGroup()

    def save(self):
        settings = QSettings(self.settings_path, QSettings.Format.IniFormat)
        
        settings.beginGroup("General")
        settings.setValue("auto_locate_server", self.auto_locate_server)
        settings.setValue("auto_login", self.auto_login)
        settings.setValue("friends_data", QJsonDocument.fromVariant(self.friends_data).toJson(QJsonDocument.JsonFormat.Compact))
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
    
    def getConsoleTempDir(self):
        tmp_dir = QDir.tempPath() + "/remoter_"
        
        rd_name = (QRandomGenerator.global_().generate() % 65536).to_bytes(2, "big").hex()
        while QDir(tmp_dir + rd_name).exists():
            rd_name = (QRandomGenerator.global_().generate() % 65536).to_bytes(2, "big").hex()

        QDir.temp().mkdir("remoter_" + rd_name)
        return QDir.tempPath() + "/remoter_" + rd_name
    
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
    
    def existFriend(self, id : str) -> bool:
        return id in self.friends_data

    def setFriendList(self, friends : list[tuple[str, str, str]]):
        self.friends_data.clear()
        for i in friends:
            self.friends_data[i[0]] = {"name": i[1], "password": i[2]}
    
    def getFriendList(self) -> list[tuple[str, str, str]]:
        result = []
        for i in self.friends_data:
            result.append((i, self.friends_data[i]["name"], self.friends_data[i]["password"]))
        return result
    
    def setFriendData(self, id: str, key, value):
        self.friends_data[id][key] = value

    def getFriendData(self, id: str, key):
        return self.friends_data[id][key]
    
    def existFriendData(self, id : str, key) -> bool:
        return key in self.friends_data[id]
    
    def setTestJson(self, json : str):
        self.test_json = json

    def getTestJson(self):
        return self.test_json
