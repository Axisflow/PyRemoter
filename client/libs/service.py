from PySide6 import QtCore
from PySide6.QtNetwork import QHostAddress, QTcpSocket, QUdpSocket
from PySide6.QtCore import QObject, Signal, QByteArray, QJsonDocument, QJsonValue, QJsonArray

from libs import settings
from libs.logger import logger as lg

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
            self.socket.connectToHost(QHostAddress(self.settings.status_service_address), self.settings.status_service_port)
            return True
    
        return False
    
    def stop(self) -> bool:
        if(self.socket.state() == QTcpSocket.SocketState.ConnectedState):
            self.have_info.emit("Disconnecting from " + self.settings.status_service_address + ":" + str(self.settings.status_service_port))
            self.socket.disconnectFromHost()
            return True
        
        return False
    
    def send(self, json: QJsonDocument) -> bool:
        if(self.socket.state() == QTcpSocket.SocketState.ConnectedState):
            data = json.toJson(QJsonDocument.JsonFormat.Compact)
            length = len(data).to_bytes(4, byteorder="big")
            self.socket.write(length + data)
            lg.log(length + data)
            return True
        
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


class StreamService:
    pass

class CommandService:
    pass