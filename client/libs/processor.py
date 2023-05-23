from PySide6.QtCore import QObject, Signal, Slot, QByteArray, QJsonDocument, QThread
from PySide6.QtNetwork import QNetworkInterface

from . import settings, service, panel
from .logger import logger as lg

class ServerLocation:
    def __init__(self, addr: str, port: int):
        self.addr = addr
        self.port = port
    def __eq__(self, other):
        return self.addr == other.addr and self.port == other.port
    def __hash__(self):
        return hash((self.addr, self.port))

class StreamProcessor(QObject):
    def __init__(self, settings):
        self.settings = settings
        
        self.ask_stream_service = {}
        self.ask_stream_management = {}
        self.need_stream_service = {}
        self.need_stream_management = {}

    
    def AddAskPair(self, id: str, addr: str, port: int, management: panel.AskManagement):
        sl = ServerLocation(addr, port)
        if(sl not in self.ask_stream_service):
            self.ask_stream_service[sl] = service.StreamServiceStruct()
            self.ask_stream_service[sl].service.start()

        self.ask_stream_management[id] = management
        self.AskConnect(self.ask_stream_service[sl].service, management)

    def AddNeedPair(self, id: str, addr: str, port: int, management: panel.NeedManagement):
        sl = ServerLocation(addr, port)
        if(sl not in self.need_stream_service):
            self.need_stream_service[sl] = service.StreamServiceStruct()
            self.need_stream_service[sl].service.start()

        self.need_stream_management[id] = management
        self.NeedConnect(self.need_stream_service[sl].service, management)

    def AskConnect(self, id: str, signals: service.CommandServicePairSignals):
        pass

    def NeedConnect(self, id: str, signals: service.CommandServicePairSignals):
        self.need_stream_management[id].send_part_screen = signals.send_part_screen
        pass

class CommandProcessor(QObject):
    def __init__(self, settings):
        self.settings = settings

        self.ask_command_service = {}
        self.ask_command_management = {}
        self.need_command_service = {}
        self.need_command_management = {}

    def AddAskPair(self, id: str, addr: str, port: int, management: panel.AskManagement):
        sl = ServerLocation(addr, port)
        if(sl not in self.ask_command_service):
            self.ask_command_service[sl] = service.CommandServiceStruct()
            self.ask_command_service[sl].service.start()
            self.ask_command_service[sl].connect_host.emit(sl.addr, sl.port)

        self.ask_command_management[id] = management
        self.ask_command_service[sl].signals.add_ask_pair.emit(id)

    def AddNeedPair(self, id: str, addr: str, port: int, management: panel.NeedManagement):
        sl = ServerLocation(addr, port)
        if(sl not in self.need_command_service):
            self.need_command_service[sl] = service.CommandServiceStruct()
            self.need_command_service[sl].service.start()

        self.need_command_management[id] = management

    def AskConnect(self, id: str, signals: service.CommandServicePairSignals):
        pass

    def NeedConnect(self, id: str, signals: service.CommandServicePairSignals):
        signals.rece_mouse_point.connect(self.need_command_management[id].MoveMouse)
        pass

class StatusProcessor(QObject):
    def __init__(self, settings, service):
        super().__init__()
        self.settings = settings
        self.service = service
        self.stream_processor = StreamProcessor(settings)
        self.command_processor = CommandProcessor(settings)
        self.service.data_received.connect(self.Process)
        self.service.connected.connect(self.onConnected)
        self.service.have_info.connect(self.onInfo)
        self.ask_stream_pair = {}
        self.ask_command_pair = {}
        self.need_stream_pair = {}
        self.need_command_pair = {}

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
            self.ask_stream_pair[id] = {"ip": json_map["UDPip"], "port": json_map["UDPport"]}
            self.ask_command_pair[id] = {"ip": json_map["TCPip"], "port": json_map["TCPport"]}
            lg.log("{} accepted your connection request".format(id))
        elif status == "NeedConn":
            id = json_map["from"]
            directly = json_map["directly"]
            self.need_stream_pair[id] = {"ip": json_map["UDPip"], "port": json_map["UDPport"]}
            self.need_command_pair[id] = {"ip": json_map["TCPip"], "port": json_map["TCPport"]}
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
            self.need_stream_pair.pop(to)
            self.need_command_pair.pop(to)
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
