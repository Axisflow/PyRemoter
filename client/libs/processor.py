from PySide6.QtCore import QObject

from libs import logger
lg = logger.logger()

class StatusProcessor(QObject):
    def __init__(self, settings, service):
        self.settings = settings
        self.service = service