import sys
import __main__
from PySide6 import QtWidgets, QtCore
from PySide6.QtCore import QCoreApplication, QFileInfo
from PySide6.QtWidgets import QApplication

from .libs import splash, ui, settings, logger, processor

if __name__ == "__main__":
    QCoreApplication.setApplicationName("PyRemoter")
    QCoreApplication.setApplicationVersion("0.1.0")
    QCoreApplication.setOrganizationName("Axisflow")
    QCoreApplication.setOrganizationDomain("axisflow.biz")
    QApplication.setStyle("Fusion")

    lg = logger.logger()
    lg.enable()
    lg.log("Starting Remoter...")
    lg.separator()

    app = QApplication(sys.argv)
    dir = QFileInfo(__main__.__file__).absoluteDir().absolutePath()
    settings = settings.Settings()
    settings.setCWD(dir)

    sp = splash.Splash(settings)
    sp.show()
    remoter = ui.Entry(settings)
    status = app.exec()

    lg.breakline()
    lg.log("Exiting...")
    sys.exit(status)