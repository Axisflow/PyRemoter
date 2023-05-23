from PySide6 import QtCore
from PySide6.QtNetwork import QHostAddress, QTcpSocket, QUdpSocket
from PySide6.QtCore import QObject, Signal, Slot, QThread, QByteArray, QJsonDocument, QJsonValue, QJsonArray

from . import settings
from .logger import logger as lg

"""
Create a abstract class for the services.
"""
class StatusService(QObject):
    socket = QTcpSocket()
    have_info = Signal(str)
    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        self.socket.connected.connect(self.onConnected)
        self.socket.disconnected.connect(self.onDisconnected)
        self.socket.errorOccurred.connect(self.onError)
        self.socket.readyRead.connect(self.onReadyRead)

        if self.settings.getAutoLocateServer():
            self.start()

    def start(self) -> bool:
        if(self.socket.state() == QTcpSocket.SocketState.UnconnectedState):
            self.have_info.emit("Connecting to " + self.settings.status_service_address + ":" + str(self.settings.status_service_port))
            self.socket.connectToHost(self.settings.status_service_address, self.settings.status_service_port)
            return True
        else:
            return False
    
    def stop(self) -> bool:
        if(self.socket.state() == QTcpSocket.SocketState.ConnectedState):
            self.have_info.emit("Disconnecting from " + self.settings.status_service_address + ":" + str(self.settings.status_service_port))
            self.socket.disconnectFromHost()
            return True
        else:
            return False
    
    def send(self, json: QJsonDocument) -> bool:
        if(self.socket.state() == QTcpSocket.SocketState.ConnectedState):
            data = json.toJson(QJsonDocument.JsonFormat.Compact)
            length = len(data).to_bytes(4, byteorder="big")
            self.socket.write(length + data)
            lg.log(length + data)
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
        if self.socket.bytesAvailable() > 0:
            data = self.socket.readAll().data()
            self.data_received.emit(QJsonDocument.fromJson(data))
            lg.log(data)

class StreamServiceStruct(QObject):
    def __init__(self):
        self.signals = StreamServiceSignals()
        self.service = StreamService()

        self.signals.send.connect(self.service.send)

class StreamServiceSignals(QObject):
    send = Signal(list)

class StreamService(QThread):
    socket = QUdpSocket()
    def run(self):
        self.exec()

    @Slot(str, int)
    def ConnectHost(self, address: str, port: int):
        self.socket.connectToHost(address, port)

    @Slot(list)
    def send(self, array: list) -> bool:
        if(self.socket.state() == QUdpSocket.SocketState.ConnectedState):
            # add a ';' to the end of every element in the array and join them together
            # convert the string to bytes and pad it to 65500 bytes
            data = ";".join([str(i) for i in array]).encode("utf-8").ljust(65500, b'\x00')
            self.socket.write(data)
            lg.log(data)
            return True
        
        return False
    
    @Slot(str, QByteArray)
    def sendScreenShot(self, id: str, data: QByteArray) -> bool:
        pass

class CommandServicePairSignals(QObject):
    rece_need_update = Signal(str, str)
    rece_mouse_point = Signal(int, int)

    send_part_screen = Signal(str, str, int, int, QByteArray)
    send_mouse_point = Signal(int, int)

class CommandService(QThread):
    socket = QTcpSocket()
    connect_host = Signal(str, int)
    add_ask_pair = Signal(str)
    def run(self):
        self.socket.readyRead.connect(self.onReadyRead)
        self.data_received.connect(self.Process)
        self.ask_signals_pair = {}
        self.need_signals_pair = {}

        self.connect_host.connect(self.service.ConnectHost)
        self.add_ask_pair.connect(self.service.AddAskPair)

        self.exec()

    @Slot(str, int)
    def ConnectHost(self, address: str, port: int):
        self.socket.connectToHost(address, port)

    def send(self, json: QJsonDocument) -> bool:
        if(self.socket.state() == QTcpSocket.SocketState.ConnectedState):
            data = json.toJson(QJsonDocument.JsonFormat.Compact)
            length = len(data).to_bytes(4, byteorder="big")
            self.socket.write(length + data)
            lg.log(length + data)
            return True
        else:
            return False
        
    data_received = Signal(QJsonDocument)
    def onReadyRead(self):
        if self.socket.bytesAvailable() > 0:
            data = self.socket.readAll().data()
            self.data_received.emit(QJsonDocument.fromJson(data))
            lg.log(data)

    def Process(self, json: QJsonDocument):
        json_map = json.toVariant()
        _type = json_map["type"]
        if _type == "NeedUpdate":
            self.need_signals_pair[json_map["from"]].rece_need_update.emit(json_map["key"], json_map["value"])
        if _type == "MousePoint":
            self.need_signals_pair[json_map["id"]].rece_mouse_point.emit(json_map["mx"], json_map["my"])
        elif _type == "MouseEvent":
            pass

    ask_signals_prepared = Signal(str, CommandServicePairSignals)
    def AddAskPair(self, id: str):
        self.ask_signals_pair[id] = CommandServicePairSignals()
        self.ask_signals_prepared.emit(id, self.ask_signals_pair[id])
        
    need_signals_prepared = Signal(str, CommandServicePairSignals)
    def AddNeedPair(self, id: str):
        self.need_signals_pair[id] = CommandServicePairSignals()
        self.need_signals_prepared.emit(id, self.need_signals_pair[id])