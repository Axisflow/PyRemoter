from PySide6 import QtCore
from PySide6.QtNetwork import QHostAddress, QTcpSocket, QUdpSocket
from PySide6.QtCore import QObject, Signal, Slot, QThread, QByteArray, QJsonDocument, QJsonValue, QJsonArray

from . import settings
from .logger import logger as lg

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

class StreamService(QThread):
    class AskPairSignals(QObject):
        rece_part_screen = Signal(str, int, int, QByteArray)

    class NeedPairSignals(QObject):
        send = Signal(list)
        send_part_screen = Signal(str, str, int, int, QByteArray)

    socket = QUdpSocket()
    connect_host = Signal(str, int)
    add_ask_pair = Signal(str)
    add_need_pair = Signal(str)
    def run(self):
        self.socket.readyRead.connect(self.onReadyRead)
        self.data_received.connect(self.Process)
        self.ask_signals_pair = {}
        self.need_signals_pair = {}

        self.connect_host.connect(self.ConnectHost)
        self.add_ask_pair.connect(self.AddAskPair)
        self.add_need_pair.connect(self.AddNeedPair)

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
    
    data_received = Signal(QByteArray)
    def onReadyRead(self):
        if self.socket.bytesAvailable() > 0:
            data = self.socket.readAll().data()
            self.data_received.emit(data)
            lg.log(data)

    @Slot(QByteArray)
    def Process(self, data: QByteArray):
        _len = len(data)

        try:
            id = ""
            i = 0
            while data[i] != b';' and i < _len:
                id += chr(data[i])
                i += 1
            i += 1

            _type = ""
            while data[i] != b';' and i < _len:
                _type += chr(data[i])
                i += 1
            i += 1

            if _type == "screen":
                seq_id = ""
                while data[i] != b';' and i < _len:
                    seq_id += chr(data[i])
                    i += 1
                i += 1

                time_stamp = ""
                while data[i] != b';' and i < _len:
                    time_stamp += chr(data[i])
                    i += 1
                time_stamp = int(time_stamp)
                i += 1

                part_num = ""
                while data[i] != b';' and i < _len:
                    part_num += chr(data[i])
                    i += 1
                part_num = int(part_num)
                i += 1

                pixmap_size = int.from_bytes(data[i:i+2], 'big')
                i += 2

                pixmap = data[i:i+pixmap_size]
                self.ask_signals_pair[id].rece_part_screen.emit(seq_id, time_stamp, part_num, pixmap)
        except Exception as e:
            lg.log(e)

    ask_signals_prepared = Signal(str, AskPairSignals)
    def AddAskPair(self, id: str):
        self.ask_signals_pair[id] = StreamService.AskPairSignals()
        self.ask_signals_prepared.emit(id, self.ask_signals_pair[id])
        
    need_signals_prepared = Signal(str, NeedPairSignals)
    def AddNeedPair(self, id: str):
        self.need_signals_pair[id] = StreamService.NeedPairSignals()
        self.need_signals_pair[id].send_part_screen.connect(self.sendScreenShot)
        self.need_signals_prepared.emit(id, self.need_signals_pair[id])

    @Slot(str, QByteArray)
    def sendScreenShot(self, id: str, seq_id: str, time_stamp: int, part_num: int, pixmap: QByteArray):
        self.send([id, "screen", seq_id, time_stamp, part_num, len(pixmap).to_bytes(2, 'big') + pixmap])


class CommandService(QThread):
    class AskPairSignals(QObject):
        send_ask_update = Signal(str, str, str)
        send_screen_event = Signal(str, dict)

    class NeedPairSignals(QObject):
        rece_need_update = Signal(str, str)
        rece_screen_event = Signal(dict)

    socket = QTcpSocket()
    connect_host = Signal(str, int)
    add_ask_pair = Signal(str)
    add_need_pair = Signal(str)
    def run(self):
        self.socket.readyRead.connect(self.onReadyRead)
        self.data_received.connect(self.Process)
        self.ask_signals_pair = {}
        self.need_signals_pair = {}

        self.connect_host.connect(self.ConnectHost)
        self.add_ask_pair.connect(self.AddAskPair)
        self.add_need_pair.connect(self.AddNeedPair)

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
        if _type == "ScreenEvent":
            self.need_signals_pair[json_map["id"]].rece_screen_event.emit(json_map)

    @Slot(str, dict)
    def sendScreenEvent(self, id: str, data: dict):
        data["id"] = id
        data["type"] = "ScreenEvent"
        self.send(QJsonDocument(data))

    @Slot(str, str, str)
    def sendAskUpdate(self, id: str, key: str, value: str):
        self.send(QJsonDocument({"type": "AskUpdate", "id": id, "key": key, "value": value}))

    ask_signals_prepared = Signal(str, AskPairSignals)
    def AddAskPair(self, id: str):
        self.ask_signals_pair[id] = CommandService.AskPairSignals()
        self.ask_signals_pair[id].send_ask_update.connect(self.sendAskUpdate)
        self.ask_signals_pair[id].send_screen_event.connect(self.sendScreenEvent)
        self.ask_signals_prepared.emit(id, self.ask_signals_pair[id])
        
    need_signals_prepared = Signal(str, NeedPairSignals)
    def AddNeedPair(self, id: str):
        self.need_signals_pair[id] = CommandService.NeedPairSignals()
        self.need_signals_prepared.emit(id, self.need_signals_pair[id])