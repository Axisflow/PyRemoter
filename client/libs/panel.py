from PySide6.QtCore import Qt, QObject, Signal, Slot, QThread, QTimer, QEvent, QByteArray, QBuffer, QIODevice, QRandomGenerator
from PySide6.QtGui import QScreen, QPixmap, QCursor, QResizeEvent, QMouseEvent
from PySide6.QtWidgets import QMainWindow, QApplication, QWidget, QLabel, QStatusBar, QGridLayout
from PySide6.QtMultimedia import QMediaRecorder
import pyautogui

from . import settings
from .logger import logger as lg

class ControlBackground(QObject):
    def __init__(self, settings):
        self.shot_timer = QTimer(self)
        self.shot_timer.timeout.connect(self.shot)
        self.shot_timer.setInterval(1000)
        self.shot_timer.start()

    screenshotted = Signal(QByteArray)
    def shot(self):
        screen = QScreen.grabWindow(QApplication.primaryScreen(), 0)
        pixmap = QPixmap(screen)
        ba = QByteArray()
        buff = QBuffer(ba)
        buff.open(QIODevice.OpenModeFlag.WriteOnly)
        pixmap.save(buff, "PNG")
        self.screenshotted.emit(ba)


class NeedManagement(QThread):
    __max_split_length__ = 120
    seq_id = ""
    time_stamp = 0
    def __init__(self, settings, id: str):
        super().__init__()
        self.settings = settings
        self.id = id

    def run(self):
        self.background = ControlBackground(self.settings)
        self.background.screenshotted.connect(self.processScreenShot)
        self.exec()

    send_part_screen = None # Signal(str, str, int, int, QByteArray) # id, seq_id, time_stamp, part_num, pixmap
    def processScreenShot(self, pixmap: QByteArray):
        if self.send_part_screen is None:
            return
        """
        for every 120*120px, send a part of screen
        if the screen is not a multiple of 120, send the rest of screen
        """
        pixmap = QPixmap(pixmap)
        left_width = pixmap.width() % self.__max_split_length__
        left_height = pixmap.height() % self.__max_split_length__
        num_width = pixmap.width() // self.__max_split_length__
        num_height = pixmap.height() // self.__max_split_length__
        part_num = 0
        for i in range(num_width):
            for j in range(num_height):
                self.send_part_screen.emit(self.id, self.seq_id, self.time_stamp, part_num, pixmap.copy(i * self.__max_split_length__, j * self.__max_split_length__, self.__max_split_length__, self.__max_split_length__).toImage().saveToData("PNG"))
                part_num += 1
        if left_width != 0:
            for i in range(num_height):
                self.send_part_screen.emit(self.id, self.seq_id, self.time_stamp, part_num, pixmap.copy(num_width * self.__max_split_length__, i * self.__max_split_length__, left_width, self.__max_split_length__).toImage().saveToData("PNG"))
                part_num += 1
        if left_height != 0:
            for i in range(num_width):
                self.send_part_screen.emit(self.id, self.seq_id, self.time_stamp, part_num, pixmap.copy(i * self.__max_split_length__, num_height * self.__max_split_length__, self.__max_split_length__, left_height).toImage().saveToData("PNG"))
                part_num += 1
        if left_width != 0 and left_height != 0:
            self.send_part_screen.emit(self.id, self.seq_id, self.time_stamp, part_num, pixmap.copy(num_width * self.__max_split_length__, num_height * self.__max_split_length__, left_width, left_height).toImage().saveToData("PNG"))
            part_num += 1

        self.time_stamp += 1

    @Slot(str, str)
    def NeedUpdate(self, key: str, value: str):
        if key == "SeqId":
            self.seq_id = value
            self.time_stamp = 0

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
            self.mouseMoved.emit(event.position().x(), event.position().y())
        else:
            self.mouseAction.emit(event.type())
        return True

    @Slot(int, QByteArray)
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
    update = None # Signal(str, str)
    def __init__(self, settings, id: str):
        super().__init__()
        self.settings = settings
        self.id = id

    def run(self):
        self.window = ControlWindow(self.settings)
        self.window.mouseMoved.connect(self.sendMousePoint)
        self.window.show()

        self.seq_id_now = None
        self.seq_id_deprecating = None
        self.screen_now_time_stamp = -1
        self.screen_now_part_num = -1
        self.seq_id_timer = QTimer(self)
        self.seq_id_timer.timeout.connect(self.changeSeqId)
        self.seq_id_timer.setSingleShot(True)
        self.changeSeqId()
        self.deprecate_seq_id_timer = QTimer(self)
        self.deprecate_seq_id_timer.timeout.connect(self.deprecateSeqId)
        self.deprecate_seq_id_timer.setSingleShot(True)
        self.deprecateSeqId()

        self.exec()

    @Slot()
    def changeSeqId(self):
        if self.update is None:
            return
        
        self.seq_id_deprecating = self.seq_id_now
        char_set = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        while True:
            self.seq_id_now = ""
            for i in range(10):
                self.seq_id_now += char_set[QRandomGenerator().bounded(len(char_set))]
            if self.seq_id_now != self.seq_id_deprecating:
                break

        self.update.emit("SeqId", self.seq_id_now)
        self.seq_id_timer.start(QRandomGenerator().bounded(15000, 25000))
        self.deprecate_seq_id_timer.start(QRandomGenerator().bounded(5000, 7500))

    @Slot()
    def deprecateSeqId(self):
        self.deprecate_seq_id_timer.stop()
        self.screen_now_time_stamp = -1
        self.screen_now_part_num = -1
        self.seq_id_deprecating = None

    @Slot(str, int, int, QByteArray)
    def setScreenPixmap(self, seq_id, time_stamp, part_num, pixmap): #seq_id, time_stamp, part_num, pixmap
        if self.seq_id_deprecating == None:
            if time_stamp > self.screen_now_time_stamp:
                self.screen_now_time_stamp = time_stamp
                self.screen_now_part_num = part_num
                self.window.setPixmap(part_num, pixmap)
            elif time_stamp == self.screen_now_time_stamp:
                if part_num > self.screen_now_part_num:
                    self.window.setPixmap(part_num, pixmap)
        else:
            if seq_id == self.seq_id_deprecating:
                if time_stamp > self.screen_now_time_stamp:
                    self.screen_now_time_stamp = time_stamp
                    self.screen_now_part_num = part_num
                    self.window.setPixmap(part_num, pixmap)
                elif time_stamp == self.screen_now_time_stamp:
                    if part_num > self.screen_now_part_num:
                        self.window.setPixmap(part_num, pixmap)
            elif seq_id == self.seq_id_now:
                self.deprecateSeqId()
                self.screen_now_time_stamp = time_stamp
                self.screen_now_part_num = part_num
                self.window.setPixmap(part_num, pixmap)

    send_mouse_point = None # Signal(str, int, int)
    def sendMousePoint(self, x, y):
        if self.send_mouse_point is not None:
            self.send_mouse_point.emit(self.id, x, y)
