from PySide6.QtCore import Qt, QObject, Signal, Slot, QThread, QTimer, QEvent, QByteArray, QBuffer, QIODevice
from PySide6.QtGui import QScreen, QPixmap, QCursor, QResizeEvent, QMouseEvent
from PySide6.QtWidgets import QMainWindow, QApplication, QWidget, QLabel, QStatusBar, QGridLayout
from PySide6.QtMultimedia import QMediaRecorder
import pyautogui

from libs import settings
from libs.logger import logger as lg

class NeedManagement(QThread):
    def __init__(self, settings, id: str):
        super().__init__()
        self.settings = settings
        self.id = id

    def run(self):
        self.shot_timer = QTimer()
        self.shot_timer.timeout.connect(self.shot)
        self.shot_timer.setInterval(1000)
        self.shot_timer.start()

        self.exec()

    screenshotted = Signal(str, QByteArray)
    def shot(self):
        screen = QScreen.grabWindow(QApplication.primaryScreen(), 0)
        pixmap = QPixmap(screen)
        ba = QByteArray()
        buff = QBuffer(ba)
        buff.open(QIODevice.WriteOnly)
        pixmap.save(buff, "PNG")
        self.screenshotted.emit(self.id, ba)

    @Slot(int, int)
    def MoveMouse(self, x, y):
        QCursor.setPos(x, y)

    @Slot(str)
    def setMouseAction(self, action):
        pass
        

class ControlWindow(QMainWindow):
    __max_split_length__ = 120
    splitted_screen = []
    now_resolution = (0, 0)
    def __init__(self, settings):
        super().__init__()
        self.settings = settings

        # Create a central widget and set it to the main window
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Create a status bar and set it to the main window
        self.status_bar = QStatusBar()
        self.status_bar.showMessage("Ready")
        self.setStatusBar(self.status_bar)

        # Create a frame as a screen
        self.combined_screen = QWidget(self.central_widget)
        self.combined_screen.setMouseTracking(True)
        self.combined_screen.mouseMoveEvent = self.screenEvent
        self.combined_screen.setLayout(self.grid_layout)

    mouseMoved = Signal(int, int)
    mouseAction = Signal(QEvent.Type)

    def screenEvent(self, event):
        if event.type() == QEvent.Type.MouseMove:
            self.mouseMoved.emit(event.x(), event.y())
        else:
            self.mouseAction.emit(event.type())
        return True

    @Slot(str, QByteArray)
    def setPixmap(self, idx, pixmap):
        if idx < len(self.splitted_screen):
            self.splitted_screen[idx].setPixmap(pixmap)

    def changeResolution(self, resolution):
        self.now_resolution = resolution
        self.initScreen(resolution[0], resolution[1])
        self.resizeScreen()

    def initScreen(self, rwidth, rheight):
        """
        for every 120*120, create a label in splitted_screen and add it to the grid layout,
        if the length is not enough, still create a label in splitted_screen and add it to the grid layout.
        """
        left_width = rwidth % self.__max_split_length__
        left_height = rheight % self.__max_split_length__
        num_width = rwidth // self.__max_split_length__
        num_height = rheight // self.__max_split_length__

        self.grid_layout = QGridLayout(self.combined_screen)
        self.grid_layout.setSpacing(0)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.splitted_screen.clear()
        for i in range(num_height):
            for j in range(num_width):
                label = QLabel()
                label.setMouseTracking(True)
                self.grid_layout.addWidget(label, i, j)
                self.splitted_screen.append(label)
            self.grid_layout.setRowStretch(i, self.__max_split_length__)
        for j in range(num_width):
            self.grid_layout.setColumnStretch(j, self.__max_split_length__)

        if left_width != 0:
            for i in range(num_height):
                label = QLabel()
                label.setMouseTracking(True)
                self.grid_layout.addWidget(label, i, num_width)
                self.splitted_screen.append(label)
            self.grid_layout.setColumnStretch(num_width, left_width)

        if left_height != 0:
            for j in range(num_width):
                label = QLabel()
                label.setMouseTracking(True)
                self.grid_layout.addWidget(label, num_height, j)
                self.splitted_screen.append(label)
            self.grid_layout.setRowStretch(num_height, left_height)
            
        if left_width != 0 and left_height != 0:
            label = QLabel()
            label.setMouseTracking(True)
            self.grid_layout.addWidget(label, num_height, num_width)
            self.splitted_screen.append(label)

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        self.resizeScreen()

    def resizeScreen(self):
        # resize the screen to the size of the central widget but keep the ratio
        width = self.now_resolution[0]
        height = self.now_resolution[1]
        if width * self.central_widget.height() >= self.central_widget.width() * height:
            self.combined_screen.resize(self.central_widget.width(), self.central_widget.width() / width * height)
        else:
            self.combined_screen.resize(self.central_widget.height() / height * width, self.central_widget.height())
        self.combined_screen.move(self.central_widget.rect().center() - self.combined_screen.rect().center())

class AskManagement(QThread):
    def __init__(self, settings, id: str):
        super().__init__()
        self.settings = settings
        self.id = id

    def run(self):
        self.window = ControlWindow(self.settings)
        self.window.show()
        self.exec()