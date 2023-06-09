from PySide6.QtCore import QObject, Signal, Slot, QJsonDocument
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

class StatusProcessor(QObject):
    def __init__(self, settings: settings.Settings):
        super().__init__()
        self.settings = settings
        self.service = service.StatusService(settings)
        self.stream_processor = StreamProcessor(settings)
        self.command_processor = CommandProcessor(settings)
        self.service.data_received.connect(self.Process)
        self.service.connected.connect(self.onConnected)
        self.service.disconnected.connect(self.onDisconnected)
        self.service.have_info.connect(self.onInfo)

        self.ask_id = []
        self.need_id = []
        self.ask_stream_pair = {}
        self.ask_command_pair = {}
        self.need_stream_pair = {}
        self.need_command_pair = {}

    def terminate(self):
        self.stop()

    @Slot(str)
    def terminateAsk(self, id: str):
        if id in self.ask_id:
            self.ask_id.remove(id)
            self.send(QJsonDocument.fromVariant({"status": "AbortAskConn", "to": id}))
            self.RemoveAskPair(id)

    def RemoveAskPair(self, id: str):
        if id in self.ask_id:
            self.ask_id.remove(id)
        if id in self.ask_stream_pair:
            self.stream_processor.RemoveAskPair(id, self.ask_stream_pair[id])
            self.ask_stream_pair.pop(id)
        if id in self.ask_command_pair:
            self.command_processor.RemoveAskPair(id, self.ask_command_pair[id])
            self.ask_command_pair.pop(id)

    @Slot(str)
    def terminateNeed(self, id: str):
        if id in self.need_id:
            self.need_id.remove(id)
            self.send(QJsonDocument.fromVariant({"status": "AbortNeedConn", "to": id}))
            self.RemoveNeedPair(id)

    def RemoveNeedPair(self, id: str):
        if id in self.need_id:
            self.need_id.remove(id)
        if id in self.need_stream_pair:
            self.stream_processor.RemoveNeedPair(id, self.need_stream_pair[id])
            self.need_stream_pair.pop(id)
        if id in self.need_command_pair:
            self.command_processor.RemoveNeedPair(id, self.need_command_pair[id])
            self.need_command_pair.pop(id)


    def send(self, json: QJsonDocument):
        self.service.send(json)

    def start(self):
        self.service.start()

    def stop(self):
        for id in self.ask_id:
            self.terminateAsk(id)
        for id in self.need_id:
            self.terminateNeed(id)
        self.service.stop()

    @Slot(QJsonDocument)
    def Process(self, json: QJsonDocument):
        json_map = json.toVariant()
        status = json_map["status"]
        if status == "GetIDSuccess":
            lg.log("ID: " + json_map["id"])
            lg.log("Password: " + json_map["pwd"])
            self.settings.setID(json_map["id"])
            self.settings.setPassword(json_map["pwd"])
        elif status == "LoginSuccess":
            lg.log("New Password: " + json_map["pwd"])
            self.settings.setPassword(json_map["pwd"])
        elif status == "RegisterSuccess":
            lg.log("Register Success")
        elif status == "AskConnSuccess":
            id = json_map["from"]
            lg.log("{} accepted your connection request".format(id))
            self.ask_id.append(id)
            self.ask_stream_pair[id] = ServerLocation(json_map["UDPip"], json_map["UDPport"])
            self.ask_command_pair[id] = ServerLocation(json_map["TCPip"], json_map["TCPport"])
            management = panel.AskManagement(self.settings, id)
            management.session_closed.connect(self.terminateAsk)
            self.stream_processor.AddAskPair(id, self.ask_stream_pair[id], management)
            self.command_processor.AddAskPair(id, self.ask_command_pair[id], management)
        elif status == "NeedConn":
            id = json_map["from"]
            directly = json_map["directly"]
            self.need_id.append(id)
            self.need_stream_pair[id] = ServerLocation(json_map["UDPip"], json_map["UDPport"])
            self.need_command_pair[id] = ServerLocation(json_map["TCPip"], json_map["TCPport"])
            if directly:
                self.ReturnNeedConnect(True, id)
            else:
                self.need_connect.emit(id)
        elif status == "AbortAskConn":
            id = json_map["from"]
            lg.log("{} aborted your connection".format(id))
            self.RemoveNeedPair(id)
        elif status == "AbortNeedConn":
            id = json_map["from"]
            lg.log("{} aborted your connection".format(id))
            self.RemoveAskPair(id)
        elif status == "LoginFail":
            self.onError(json_map["reason"])
            if json_map["reason"] == "id is not exist":
                self.GetID()
        elif status == "GetIDFail":
            self.onError(json_map["reason"])
            if json_map["reason"] == "mac has one id":
                self.settings.setID(json_map["id"])
                self.settings.setPassword(json_map["pwd"])
                self.Login()
        elif status == "RegisterFail" or status == "AskConnFail":
            self.onError(json_map["reason"])
        else:
            self.onError("Unknown status: " + status)
            
    error_occurred = Signal(str)
    def onError(self, error: str):
        lg.log("Error occur: " + error)
        self.error_occurred.emit(error)

    have_info = Signal(str)
    def onInfo(self, info: str):
        lg.log("Info: " + info)
        self.have_info.emit(info)
    
    connected = Signal()
    def onConnected(self):
        if self.settings.getAutoLogin():
            self.Login()
        self.connected.emit()

    disconnected = Signal()
    def onDisconnected(self):
        self.disconnected.emit()

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
        if accept:
            management = panel.NeedManagement(self.settings, to)
            management.session_closed.connect(self.terminateNeed)
            self.stream_processor.AddNeedPair(to, self.need_stream_pair[to], management)
            self.command_processor.AddNeedPair(to, self.need_command_pair[to], management)
        else:
            json_map["reason"] = reason
            self.need_id.remove(to)
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

class StreamProcessor(QObject):
    def __init__(self, settings: settings.Settings):
        self.settings = settings
        
        self.ask_stream_service = {}
        self.ask_stream_management = {}
        self.need_stream_service = {}
        self.need_stream_management = {}

    def RemoveAskPair(self, id: str, sl: ServerLocation):
        lg.log("Remove ask pair: " + id + " " + sl.addr + " " + str(sl.port))
        if(sl in self.ask_stream_service):
            self.ask_stream_management[id].terminate()
            self.ask_stream_management.pop(id)
            self.ask_stream_service[sl].remove_ask_pair.emit(id)

    def RemoveNeedPair(self, id: str, sl: ServerLocation):
        lg.log("Remove need pair: " + id + " " + sl.addr + " " + str(sl.port))
        if(sl in self.need_stream_service):
            self.need_stream_management[id].terminate()
            self.need_stream_management.pop(id)
            self.need_stream_service[sl].remove_need_pair.emit(id)

    @Slot(str, int)
    def DeleteService(self, addr: str, port: int):
        sl = ServerLocation(addr, port)
        if sl in self.ask_stream_service:
            self.ask_stream_service[sl].terminate()
            self.ask_stream_service.pop(sl)
        if sl in self.need_stream_service:
            self.need_stream_service[sl].terminate()
            self.need_stream_service.pop(sl)
    
    def AddAskPair(self, id: str, sl: ServerLocation, management: panel.AskManagement):
        lg.log("Add ask pair: " + id + " " + sl.addr + " " + str(sl.port))
        if(sl not in self.ask_stream_service):
            self.ask_stream_service[sl] = service.StreamService(self.settings)
            self.ask_stream_service[sl].ask_signals_prepared.connect(self.ConnectAsk)
            self.ask_stream_service[sl].disconnected.connect(self.DeleteService)
            self.ask_stream_service[sl].connect_host.emit(sl.addr, sl.port)

        self.ask_stream_management[id] = management
        self.ask_stream_service[sl].add_ask_pair.emit(id)

    def AddNeedPair(self, id: str, sl: ServerLocation, management: panel.NeedManagement):
        lg.log("Add need pair: " + id + " " + sl.addr + " " + str(sl.port))
        if(sl not in self.need_stream_service):
            self.need_stream_service[sl] = service.StreamService(self.settings)
            self.need_stream_service[sl].need_signals_prepared.connect(self.ConnectNeed)
            self.need_stream_service[sl].disconnected.connect(self.DeleteService)
            self.need_stream_service[sl].connect_host.emit(sl.addr, sl.port)

        self.need_stream_management[id] = management
        self.need_stream_service[sl].add_need_pair.emit(id)

    def ConnectAsk(self, id: str, signals: service.StreamService.AskPairSignals):
        lg.log("Connect ask: " + id)
        signals.rece_screen.connect(self.ask_stream_management[id].setScreenPixmap)
        self.ask_stream_management[id].start()

    def ConnectNeed(self, id: str, signals: service.StreamService.NeedPairSignals):
        lg.log("Connect need: " + id)
        self.need_stream_management[id].send_screen = signals.send_screen
        self.need_stream_management[id].start()

class CommandProcessor(QObject):
    def __init__(self, settings: settings.Settings):
        self.settings = settings

        self.ask_command_service = {}
        self.ask_command_management = {}
        self.need_command_service = {}
        self.need_command_management = {}

    def RemoveAskPair(self, id: str, sl: ServerLocation):
        lg.log("Remove ask pair: " + id + " " + sl.addr + " " + str(sl.port))
        if(sl in self.ask_command_service):
            self.ask_command_management[id].terminate()
            self.ask_command_management.pop(id)
            self.ask_command_service[sl].remove_ask_pair.emit(id)

    def RemoveNeedPair(self, id: str, sl: ServerLocation):
        lg.log("Remove need pair: " + id + " " + sl.addr + " " + str(sl.port))
        if(sl in self.need_command_service):
            self.need_command_management[id].terminate()
            self.need_command_management.pop(id)
            self.need_command_service[sl].remove_need_pair.emit(id)

    @Slot(str, int)
    def DeleteService(self, addr: str, port: int):
        sl = ServerLocation(addr, port)
        if sl in self.ask_command_service:
            self.ask_command_service[sl].terminate()
            self.ask_command_service.pop(sl)
        if sl in self.need_command_service:
            self.need_command_service[sl].terminate()
            self.need_command_service.pop(sl)

    def AddAskPair(self, id: str, sl: ServerLocation, management: panel.AskManagement):
        lg.log("Add ask pair: " + id + " " + sl.addr + " " + str(sl.port))
        if(sl not in self.ask_command_service):
            self.ask_command_service[sl] = service.CommandService(self.settings)
            self.ask_command_service[sl].ask_signals_prepared.connect(self.ConnectAsk)
            self.ask_command_service[sl].disconnected.connect(self.DeleteService)
            self.ask_command_service[sl].connect_host.emit(sl.addr, sl.port)

        self.ask_command_management[id] = management
        self.ask_command_service[sl].add_ask_pair.emit(id)

    def AddNeedPair(self, id: str, sl: ServerLocation, management: panel.NeedManagement):
        lg.log("Add need pair: " + id + " " + sl.addr + " " + str(sl.port))
        if(sl not in self.need_command_service):
            self.need_command_service[sl] = service.CommandService(self.settings)
            self.need_command_service[sl].need_signals_prepared.connect(self.ConnectNeed)
            self.need_command_service[sl].disconnected.connect(self.DeleteService)
            self.need_command_service[sl].connect_host.emit(sl.addr, sl.port)

        self.need_command_management[id] = management
        self.need_command_service[sl].add_need_pair.emit(id)

    def ConnectAsk(self, id: str, signals: service.CommandService.AskPairSignals):
        lg.log("Connect ask: " + id)
        signals.rece_need_inform.connect(self.ask_command_management[id].NeedInform)
        self.ask_command_management[id].update = signals.send_ask_update
        self.ask_command_management[id].send_screen_event = signals.send_screen_event
        self.ask_command_management[id].start()

    def ConnectNeed(self, id: str, signals: service.CommandService.NeedPairSignals):
        lg.log("Connect need: " + id)
        self.need_command_management[id].inform = signals.send_ask_inform
        signals.rece_need_update.connect(self.need_command_management[id].NeedUpdate)
        signals.rece_screen_event.connect(self.need_command_management[id].ProcessScreenEvent)
        self.need_command_management[id].start()
