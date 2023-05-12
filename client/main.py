import sys
import __main__
from PySide6 import QtWidgets, QtCore

from libs import splash, ui, settings, logger

if __name__ == "__main__":
    lg = logger.logger()
    lg.enable()
    lg.log("Starting Remoter...")
    lg.separator()

    app = QtWidgets.QApplication([])
    app.setStyle("Fusion")
    dir = QtCore.QFileInfo(__main__.__file__).absoluteDir().absolutePath()
    lg.log("Current Working Directory: " + dir)

    settings = settings.Settings()
    settings.setCWD(dir)

    sp = splash.Splash(settings)
    sp.show()
    remoter = ui.Entry(settings)
    status = app.exec()

    lg.breakline()
    lg.log("Exiting...")
    sys.exit(status)