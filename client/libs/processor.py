from PySide6.QtCore import QObject, Signal, Slot, QByteArray, QJsonDocument, QJsonValue, QJsonArray
from PySide6.QtNetwork import QNetworkInterface

from libs import settings, service
from libs.logger import logger as lg

class StatusProcessor(QObject):
    def __init__(self, settings, service):
        super().__init__()
        self.settings = settings
        self.service = service
        self.service.data_received.connect(self.Process)
        self.service.connected.connect(self.onConnected)
        self.service.have_info.connect(self.onInfo)

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
        elif status == "RegisterSuccess":
            lg.log("Register Success")
        elif status == "AskConnSuccess":
            id = json_map["from"]
            lg.log("{} accepted your connection request".format(id))
        elif status == "NeedConn":
            id = json_map["from"]
            directly = json_map["directly"]
            if directly:
                self.ReturnNeedConnect(True, id)
            else:
                self.need_connect.emit(id)
        elif status == "GetIDFail" or status == "LoginFail" or status == "RegisterFail" or status == "AskConnFail":
            self.onError(json_map["reason"])
        else:
            self.onError("Unknown status: " + status)
            
    error_occurred = Signal(str)
    def onError(self, error: str):
        lg.log(error)
        self.error_occurred.emit(error)

    have_info = Signal(str)
    def onInfo(self, info: str):
        lg.log(info)
        self.have_info.emit(info)
    
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
            json_map = {"status": "Login", "mac": self.GetMacAddress(), "id": self.settings.getID(), "pwd": self.settings.getPassword()}
            self.service.send(QJsonDocument.fromVariant(json_map))

    def Register(self, id: str, pwd: str, permeanent: bool):
        json_map = {"status": "Register", "mac": self.GetMacAddress(), "id": id, "pwd": pwd, "permanent": permeanent}
        self.service.send(QJsonDocument.fromVariant(json_map))

    def AskConnect(self, id: list, pwd: list):
        json_map = {"status": "AskConn", "to": id, "pwd": pwd}
        self.service.send(QJsonDocument.fromVariant(json_map))

    need_connect = Signal(str)
    def ReturnNeedConnect(self, accept: bool, to: str, reason = ""):
        json_map = {"status": "NeedConn" + "Accept" if accept else "Refuse", "to": to}
        if not accept:
            json_map["reason"] = reason
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