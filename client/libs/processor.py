from PySide6.QtCore import QObject, Signal, QByteArray, QJsonDocument, QJsonValue, QJsonArray
from PySide6.QtNetwork import QNetworkInterface

from libs import logger
lg = logger.logger()

class StatusProcessor(QObject):
    def __init__(self, settings, service):
        self.settings = settings
        self.service = service

    def GetID(self):
        json = QJsonDocument()
        json["status"] = "GetID"
        """
        set value as mac id
        """
        json["mac"] = self.GetMacAddress()
        self.service.send(json)

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