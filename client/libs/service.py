from PySide6 import QtCore
from PySide6.QtNetwork import QHostAddress, QTcpSocket, QUdpSocket
from PySide6.QtCore import QObject, Signal, QJsonDocument, QJsonValue, QJsonArray

from libs import settings, logger
lg = logger.logger()

"""
Create a abstract class for the services.
"""
class StatusService(QObject):
    socket = QTcpSocket()
    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        self.socket.connected.connect(self.onConnected)
        self.socket.disconnected.connect(self.onDisconnected)
        self.socket.errorOccurred.connect(self.onError)
        self.socket.readyRead.connect(self.onReadyRead)

    def start(self) -> bool:
        if(self.socket.state() == QTcpSocket.SocketState.UnconnectedState):
            self.socket.connectToHost(QHostAddress(self.settings.status_service_address), self.settings.status_service_port)
            lg.log("Connecting to " + self.settings.status_service_address + ":" + str(self.settings.status_service_port))
            return True
    
        return False
    
    connected = Signal()
    def onConnected(self):
        self.connected.emit()

    disconnected = Signal()
    def onDisconnected(self):
        self.disconnected.emit()

    error_occurred = Signal(QTcpSocket.SocketError)
    def onError(self, error: QTcpSocket.SocketError):
        self.error_occurred.emit(error)

    
    def onReadyRead(self):
        if self.socket.bytesAvailable() > 0:
            data = self.socket.readAll().data().decode("utf-8")
            lg.log(data.data().decode("utf-8"))


class StreamService:
    pass

class CommandService:
    pass