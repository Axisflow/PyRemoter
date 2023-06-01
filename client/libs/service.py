from PySide6 import QtCore
from PySide6.QtNetwork import QHostAddress, QTcpSocket, QUdpSocket
from PySide6.QtCore import QObject, Signal, Slot, QThread, QByteArray, QJsonDocument, QJsonValue, QJsonArray

from . import settings
from .logger import logger as lg

class StatusService(QObject):
    socket = QTcpSocket()
    have_info = Signal(str)
    def __init__(self, settings: settings.Settings):
        super().__init__()
        self.settings = settings
        self.socket.connected.connect(self.onConnected)
        self.socket.disconnected.connect(self.onDisconnected)
        self.socket.errorOccurred.connect(self.onError)
        self.socket.readyRead.connect(self.onReadyRead)

        if self.settings.getAutoLocateServer():
            self.start()

    def terminate(self):
        self.stop()

    def start(self) -> bool:
        if(self.socket.state() == QTcpSocket.SocketState.UnconnectedState):
            addr, port = self.settings.getStatusServer()
            self.have_info.emit("Connecting to " + addr + ":" + str(port))
            self.socket.connectToHost(addr, port)
            return True
        else:
            return False
    
    def stop(self) -> bool:
        if(self.socket.state() == QTcpSocket.SocketState.ConnectedState):
            addr, port = self.settings.getStatusServer()
            self.have_info.emit("Disconnecting from " + addr + ":" + str(port))
            self.socket.disconnectFromHost()
            return True
        else:
            return False
    
    def send(self, json: QJsonDocument) -> bool:
        if(self.socket.state() == QTcpSocket.SocketState.ConnectedState):
            data = json.toJson(QJsonDocument.JsonFormat.Compact)
            length = len(data).to_bytes(4, byteorder="big")
            lg.log("StatusSocket send: " + str(length + data))
            self.socket.write(length + data)
            return True
        else:
            return False
    
    connected = Signal()
    def onConnected(self):
        self.have_info.emit("Connected to " + self.socket.peerAddress().toString() + ":" + str(self.socket.peerPort()))
        self.connected.emit()

    disconnected = Signal()
    def onDisconnected(self):
        self.have_info.emit("Disconnected from " + self.socket.peerAddress().toString() + ":" + str(self.socket.peerPort()))
        self.disconnected.emit()

    error_occurred = Signal(QTcpSocket.SocketError)
    def onError(self, error: QTcpSocket.SocketError):
        lg.log("Error occurred: " + str(error))
        self.error_occurred.emit(error)

    data_received = Signal(QJsonDocument)
    def onReadyRead(self):
        length = int.from_bytes(self.socket.read(4), byteorder="big")
        lg.log(length)
        data = self.socket.read(length)
        lg.log(data)
        self.data_received.emit(QJsonDocument.fromJson(data))

class StreamService(QObject):
    class Thread(QThread):
        def run(self):
            self.exec()

    class AskPairSignals(QObject):
        rece_screen = Signal(QByteArray)

    class NeedPairSignals(QObject):
        send = Signal(list)
        send_screen = Signal(str, QByteArray)

    connect_host = Signal(str, int)
    add_ask_pair = Signal(str)
    add_need_pair = Signal(str)
    def __init__(self, settings: settings.Settings):
        super().__init__()
        self.settings = settings

        self.self_thread = StreamService.Thread()
        self.moveToThread(self.self_thread)
        self.self_thread.start()

        self.socket = QTcpSocket()
        self.socket.moveToThread(self.self_thread)
        self.socket.connected.connect(self.onConnected)
        self.socket.disconnected.connect(self.onDisconnected)
        self.socket.errorOccurred.connect(self.onError)
        self.socket.readyRead.connect(self.onReadyRead)
        self.data_received.connect(self.Process)

        self.ask_signals_pair = {}
        self.need_signals_pair = {}

        self.connect_host.connect(self.ConnectHost)
        self.add_ask_pair.connect(self.AddAskPair)
        self.add_need_pair.connect(self.AddNeedPair)

    @Slot(str, int)
    def ConnectHost(self, address: str, port: int):
        lg.log("Connecting to " + address + ":" + str(port))
        self.socket.connectToHost(address, port)
    
    connected = Signal()
    def onConnected(self):
        self.send([self.settings.getID(), "Login", self.settings.getPassword()]) # 00000000;Login
        self.connected.emit()

    disconnected = Signal()
    def onDisconnected(self):
        self.disconnected.emit()

    error_occurred = Signal(QTcpSocket.SocketError)
    def onError(self, error: QTcpSocket.SocketError):
        lg.log("Error occurred: " + str(error))
        self.error_occurred.emit(error)

    @Slot(list)
    def send(self, array: list) -> bool:
        if(self.socket.state() == QTcpSocket.SocketState.ConnectedState):
            # add a ';' to the end of every element in the array and join them together
            # convert the string to bytes and pad it to 65500 bytes
            data = b";".join([StreamService.bytize(i) for i in array])
            length = len(data).to_bytes(4, byteorder="big")
            lg.log("StreamSocket is sending data! {}...".format(length + data[:75]))
            self.socket.write(length + data)
            return True
        
        return False
    
    data_received = Signal(QByteArray)
    unfinished_length = None
    unfinished_data = QByteArray()
    unfinish = False
    def onReadyRead(self):
        if self.socket.bytesAvailable() > 0:
            if self.unfinish == False:
                self.unfinished_length = int.from_bytes(self.socket.read(4), byteorder="big")
                lg.log("StreamSocket Length: " + str(self.unfinished_length))
                self.unfinished_data = QByteArray()
                
            data = self.socket.read(self.unfinished_length)
            self.unfinished_data += data
            lg.log("Data real length: " + str(len(data)))
            self.unfinished_length -= len(data)

            if self.unfinished_length == 0:
                lg.log("StreamSocket received data! {}...".format(self.unfinished_data[:75]))
                self.data_received.emit(self.unfinished_data)
                self.unfinish = False
            else:
                self.unfinish = True
                

    @Slot(QByteArray)
    def Process(self, data: QByteArray):
        data = data.data()
        _len = len(data)
        sep = ord(b';')

    # try:
        id = ""
        i = 0
        while data[i] != sep and i < _len:
            id += chr(data[i])
            i += 1
        i += 1
        lg.log("ID(From): " + id)

        _type = ""
        while data[i] != sep and i < _len:
            _type += chr(data[i])
            i += 1
        i += 1
        lg.log("Type: " + _type)

        if _type == "screen":
            pixmap = data[i:]
            self.ask_signals_pair[id].rece_screen.emit(pixmap)
    # except Exception as e:
    #     lg.log(e)

    ask_signals_prepared = Signal(str, AskPairSignals)
    def AddAskPair(self, id: str):
        self.ask_signals_pair[id] = StreamService.AskPairSignals()
        self.ask_signals_prepared.emit(id, self.ask_signals_pair[id])
        
    need_signals_prepared = Signal(str, NeedPairSignals)
    def AddNeedPair(self, id: str):
        self.need_signals_pair[id] = StreamService.NeedPairSignals()
        self.need_signals_pair[id].send_screen.connect(self.sendScreenShot)
        self.need_signals_prepared.emit(id, self.need_signals_pair[id])

    @Slot(str, QByteArray)
    def sendScreenShot(self, id: str, pixmap: QByteArray):
        self.send([id, "screen", pixmap])

    @staticmethod
    def bytize(obj):
        if isinstance(obj, bytes):
            return obj
        elif isinstance(obj, QByteArray):
            return obj
        else:
            return str(obj).encode("utf-8")

class CommandService(QObject):
    class Thread(QThread):
        def run(self):
            self.exec()

    class AskPairSignals(QObject):
        rece_need_inform = Signal(str, str)
        send_ask_update = Signal(str, str, str)
        send_screen_event = Signal(str, dict)

    class NeedPairSignals(QObject):
        send_ask_inform = Signal(str, str, str)
        rece_need_update = Signal(str, str)
        rece_screen_event = Signal(dict)

    connect_host = Signal(str, int)
    add_ask_pair = Signal(str)
    add_need_pair = Signal(str)
    def __init__(self, settings: settings.Settings):
        super().__init__()
        self.settings = settings

        self.self_thread = CommandService.Thread()
        self.moveToThread(self.self_thread)
        self.self_thread.start()

        self.socket = QTcpSocket()
        self.socket.moveToThread(self.self_thread)
        self.socket.connected.connect(self.onConnected)
        self.socket.disconnected.connect(self.onDisconnected)
        self.socket.errorOccurred.connect(self.onError)
        self.socket.readyRead.connect(self.onReadyRead)
        self.data_received.connect(self.Process)

        self.ask_signals_pair = {}
        self.need_signals_pair = {}

        self.connect_host.connect(self.ConnectHost)
        self.add_ask_pair.connect(self.AddAskPair)
        self.add_need_pair.connect(self.AddNeedPair)

    @Slot(str, int)
    def ConnectHost(self, address: str, port: int):
        lg.log("Connecting to " + address + ":" + str(port))
        self.socket.connectToHost(address, port)
    
    connected = Signal()
    def onConnected(self):
        self.send(QJsonDocument({"type": "Login", "from": self.settings.getID(), "pwd": self.settings.getPassword()}))
        self.connected.emit()

    disconnected = Signal()
    def onDisconnected(self):
        self.disconnected.emit()

    error_occurred = Signal(QTcpSocket.SocketError)
    def onError(self, error: QTcpSocket.SocketError):
        lg.log("Error occurred: " + str(error))
        self.error_occurred.emit(error)

    def send(self, json: QJsonDocument) -> bool:
        if(self.socket.state() == QTcpSocket.SocketState.ConnectedState):
            data = json.toJson(QJsonDocument.JsonFormat.Compact)
            length = len(data).to_bytes(4, byteorder="big")
            lg.log("CommandSocket send:" + str(length + data))
            self.socket.write(length + data)
            return True
        else:
            return False
        
    data_received = Signal(QJsonDocument)
    def onReadyRead(self):
        if self.socket.bytesAvailable() > 0:
            length = int.from_bytes(self.socket.read(4), byteorder="big")
            lg.log(length)
            data = self.socket.read(length)
            lg.log(data)
            self.data_received.emit(QJsonDocument.fromJson(data))

    def Process(self, json: QJsonDocument):
        json_map = json.toVariant()
        _type = json_map["type"]
        if _type == "NeedInform":
            self.ask_signals_pair[json_map["from"]].rece_need_inform.emit(json_map["key"], json_map["value"])
        elif _type == "NeedUpdate":
            self.need_signals_pair[json_map["from"]].rece_need_update.emit(json_map["key"], json_map["value"])
        elif _type == "ScreenEvent":
            self.need_signals_pair[json_map["from"]].rece_screen_event.emit(json_map)

    @Slot(str, dict)
    def sendScreenEvent(self, id: str, data: dict):
        data["to"] = id
        data["type"] = "ScreenEvent"
        self.send(QJsonDocument(data))

    @Slot(str, str, str)
    def sendAskUpdate(self, id: str, key: str, value: str):
        self.send(QJsonDocument({"type": "AskUpdate", "to": id, "key": key, "value": value}))

    @Slot(str, str, str)
    def sendAskInform(self, id: str, key: str, value: str):
        self.send(QJsonDocument({"type": "AskInform", "to": id, "key": key, "value": value}))

    ask_signals_prepared = Signal(str, AskPairSignals)
    def AddAskPair(self, id: str):
        self.ask_signals_pair[id] = CommandService.AskPairSignals()
        self.ask_signals_pair[id].send_ask_update.connect(self.sendAskUpdate)
        self.ask_signals_pair[id].send_screen_event.connect(self.sendScreenEvent)
        self.ask_signals_prepared.emit(id, self.ask_signals_pair[id])
        
    need_signals_prepared = Signal(str, NeedPairSignals)
    def AddNeedPair(self, id: str):
        self.need_signals_pair[id] = CommandService.NeedPairSignals()
        self.need_signals_pair[id].send_ask_inform.connect(self.sendAskInform)
        self.need_signals_prepared.emit(id, self.need_signals_pair[id])