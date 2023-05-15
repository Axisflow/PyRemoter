from PySide6.QtCore import QObject, Signal, Slot, QByteArray, QJsonDocument, QJsonValue, QJsonArray
from PySide6.QtNetwork import QNetworkInterface

from libs import logger
lg = logger.logger()

class StatusProcessor(QObject):
    def __init__(self, settings, service):
        self.settings = settings
        self.service = service
        self.service.data_received.connect(self.Process)
        self.service.connected.connect(self.onConnected)

    @Slot(QJsonDocument)
    def Process(self, json: QJsonDocument):
        json_map = json.toVariant()
        status = json_map["status"]
        if status == "GetIDSuccess":
            self.settings.setID(json_map["id"])
            self.settings.setPassword(json_map["pwd"])
            lg.log("ID: " + json_map["id"])
            lg.log("Password: " + json_map["pwd"])
        elif status == "LoginSuccess":
            self.settings.setPassword(json_map["pwd"])
            lg.log("New Password: " + json_map["pwd"])
        elif status == "GetIDFailed" or status == "LoginFailed":
            self.onError(json_map["reason"])
            
    error_occurred = Signal(str)
    def onError(self, error: str):
        lg.log(error)
        self.error_occurred.emit(error)

    def onConnected(self):
        if self.settings.getAutoLogin():
            self.Login()

    def GetID(self):
        json_map = {"status": "GetID", "mac": self.GetMacAddress()}
        self.service.send(QJsonDocument.fromVariant(json_map))

    def Login(self):
        if self.settings.getID() == "":
            self.GetID()
        else:
            json_map = {"status": "Login", "id": self.settings.getID(), "pwd": self.settings.getPassword()}
            self.service.send(QJsonDocument.fromVariant(json_map))

    def Register(self, id: str, pwd: str, permeanent: bool):
        json_map = {"status": "Register", "id": id, "pwd": pwd, "permanent": permeanent}
        self.service.send(QJsonDocument.fromVariant(json_map))

    @classmethod
    def GetMacAddress(cls):
        interface = QNetworkInterface.allInterfaces()
        for i in interface:
            if i.flags() & QNetworkInterface.IsUp:
                if i.flags() & QNetworkInterface.IsRunning:
                    if not i.flags() & QNetworkInterface.IsLoopBack:
                        if i.hardwareAddress() != "":
                            lg.log(i.hardwareAddress())
                            return i.hardwareAddress()