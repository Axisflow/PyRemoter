from PySide6.QtCore import Qt, QObject, Signal, Slot, QThread, QTimer, QEvent, QByteArray, QBuffer, QIODevice, QRandomGenerator
from PySide6.QtGui import QScreen, QPixmap, QCursor, QResizeEvent
from PySide6.QtWidgets import QMainWindow, QApplication, QWidget, QLabel, QStatusBar, QGridLayout
from PySide6.QtMultimedia import QMediaRecorder
import pyautogui

from . import settings
from .logger import logger as lg

class NameConverter:
    __key_map__ = { # Just create pairs of Qt.Key and key name that pyautogui KEY_NAMES has
        Qt.Key.Key_Escape: "escape",
        Qt.Key.Key_Tab: "tab",
        Qt.Key.Key_Backspace: "backspace",
        Qt.Key.Key_Return: "return",
        Qt.Key.Key_Enter: "enter",
        Qt.Key.Key_Insert: "insert",
        Qt.Key.Key_Delete: "delete",
        Qt.Key.Key_Pause: "pause",
        Qt.Key.Key_Print: "print",
        Qt.Key.Key_Clear: "clear",
        Qt.Key.Key_Home: "home",
        Qt.Key.Key_End: "end",
        Qt.Key.Key_Left: "left",
        Qt.Key.Key_Up: "up",
        Qt.Key.Key_Right: "right",
        Qt.Key.Key_Down: "down",
        Qt.Key.Key_PageUp: "pageup",
        Qt.Key.Key_PageDown: "pagedown",
        Qt.Key.Key_Shift: "shift",
        Qt.Key.Key_Control: "ctrl",
        Qt.Key.Key_Meta: "command",
        Qt.Key.Key_Alt: "alt",
        Qt.Key.Key_CapsLock: "capslock",
        Qt.Key.Key_NumLock: "numlock",
        Qt.Key.Key_ScrollLock: "scrolllock",
        Qt.Key.Key_F1: "f1",
        Qt.Key.Key_F2: "f2",
        Qt.Key.Key_F3: "f3",
        Qt.Key.Key_F4: "f4",
        Qt.Key.Key_F5: "f5",
        Qt.Key.Key_F6: "f6",
        Qt.Key.Key_F7: "f7",
        Qt.Key.Key_F8: "f8",
        Qt.Key.Key_F9: "f9",
        Qt.Key.Key_F10: "f10",
        Qt.Key.Key_F11: "f11",
        Qt.Key.Key_F12: "f12",
        Qt.Key.Key_F13: "f13",
        Qt.Key.Key_F14: "f14",
        Qt.Key.Key_F15: "f15",
        Qt.Key.Key_F16: "f16",
        Qt.Key.Key_F17: "f17",
        Qt.Key.Key_F18: "f18",
        Qt.Key.Key_F19: "f19",
        Qt.Key.Key_F20: "f20",
        Qt.Key.Key_F21: "f21",
        Qt.Key.Key_F22: "f22",
        Qt.Key.Key_F23: "f23",
        Qt.Key.Key_F24: "f24",
        Qt.Key.Key_Space: "space",
        Qt.Key.Key_Exclam: "!",
        Qt.Key.Key_QuoteDbl: '"',
        Qt.Key.Key_NumberSign: "#",
        Qt.Key.Key_Dollar: "$",
        Qt.Key.Key_Percent: "%",
        Qt.Key.Key_Ampersand: "&",
        Qt.Key.Key_Apostrophe: "'",
        Qt.Key.Key_ParenLeft: "(",
        Qt.Key.Key_ParenRight: ")",
        Qt.Key.Key_Asterisk: "*",
        Qt.Key.Key_Plus: "+",
        Qt.Key.Key_Comma: ",",
        Qt.Key.Key_Minus: "-",
        Qt.Key.Key_Period: ".",
        Qt.Key.Key_Slash: "/",
        Qt.Key.Key_0: "0",
        Qt.Key.Key_1: "1",
        Qt.Key.Key_2: "2",
        Qt.Key.Key_3: "3",
        Qt.Key.Key_4: "4",
        Qt.Key.Key_5: "5",
        Qt.Key.Key_6: "6",
        Qt.Key.Key_7: "7",
        Qt.Key.Key_8: "8",
        Qt.Key.Key_9: "9",
        Qt.Key.Key_Colon: ":",
        Qt.Key.Key_Semicolon: ";",
        Qt.Key.Key_Less: "<",
        Qt.Key.Key_Equal: "=",
        Qt.Key.Key_Greater: ">",
        Qt.Key.Key_Question: "?",
        Qt.Key.Key_At: "@",
        Qt.Key.Key_A: "a",
        Qt.Key.Key_B: "b",
        Qt.Key.Key_C: "c",
        Qt.Key.Key_D: "d",
        Qt.Key.Key_E: "e",
        Qt.Key.Key_F: "f",
        Qt.Key.Key_G: "g",
        Qt.Key.Key_H: "h",
        Qt.Key.Key_I: "i",
        Qt.Key.Key_J: "j",
        Qt.Key.Key_K: "k",
        Qt.Key.Key_L: "l",
        Qt.Key.Key_M: "m",
        Qt.Key.Key_N: "n",
        Qt.Key.Key_O: "o",
        Qt.Key.Key_P: "p",
        Qt.Key.Key_Q: "q",
        Qt.Key.Key_R: "r",
        Qt.Key.Key_S: "s",
        Qt.Key.Key_T: "t",
        Qt.Key.Key_U: "u",
        Qt.Key.Key_V: "v",
        Qt.Key.Key_W: "w",
        Qt.Key.Key_X: "x",
        Qt.Key.Key_Y: "y",
        Qt.Key.Key_Z: "z",
        Qt.Key.Key_BracketLeft: "[",
        Qt.Key.Key_Backslash: "\\",
        Qt.Key.Key_BracketRight: "]",
        Qt.Key.Key_AsciiCircum: "^",
        Qt.Key.Key_Underscore: "_",
        Qt.Key.Key_QuoteLeft: "`",
        Qt.Key.Key_BraceLeft: "{",
        Qt.Key.Key_Bar: "|",
        Qt.Key.Key_BraceRight: "}",
        Qt.Key.Key_AsciiTilde: "~",
    }

    @staticmethod
    def KeyConvert(key: Qt.Key) -> str:
        return NameConverter.__key_map__[key]
    
    __mouse_map__ = {
        Qt.MouseButton.LeftButton: "left",
        Qt.MouseButton.RightButton: "right",
        Qt.MouseButton.MiddleButton: "middle",
    }
    
    @staticmethod
    def MouseConvert(button: Qt.MouseButton) -> str:
        return NameConverter.__mouse_map__[button]

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

    @Slot(dict)
    def ProcessScreenEvent(self, event: dict):
        if event["event"] == "mouse_move":
            pyautogui.moveTo(event["x"], event["y"])
        elif event["event"] == "mouse_press":
            pyautogui.mouseDown(button=event["button"])
        elif event["event"] == "mouse_release":
            pyautogui.mouseUp(button=event["button"])
        elif event["event"] == "mouse_double_click":
            pyautogui.doubleClick(button=event["button"])
        elif event["event"] == "mouse_wheel":
            if(event["x"] > 0):
                pyautogui.hscroll(1)
            elif(event["x"] < 0):
                pyautogui.hscroll(-1)
            if(event["y"] > 0):
                pyautogui.vscroll(1)
            elif(event["y"] < 0):
                pyautogui.vscroll(-1)
        elif event["event"] == "key_press":
            pyautogui.keyDown(event["key"])
        elif event["event"] == "key_release":
            pyautogui.keyUp(event["key"])
        

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
        self.combined_screen.mouseMoveEvent = self.ScreenEvent
        self.combined_screen.mousePressEvent = self.ScreenEvent
        self.combined_screen.mouseReleaseEvent = self.ScreenEvent
        self.combined_screen.mouseDoubleClickEvent = self.ScreenEvent
        self.combined_screen.wheelEvent = self.ScreenEvent
        self.combined_screen.keyPressEvent = self.ScreenEvent
        self.combined_screen.keyReleaseEvent = self.ScreenEvent
        self.combined_screen.setLayout(self.grid_layout)

    screen_event = Signal(dict)
    def ScreenEvent(self, event):
        if event.type() == QEvent.Type.MouseMove:
            self.screen_event.emit({"event": "mouse_move", "x": self.now_resolution[0] / self.combined_screen.width() * event.position().x(), "y": self.now_resolution[1] / self.combined_screen.height() * event.position().y()})
        elif event.type() == QEvent.Type.MouseButtonPress:
            self.screen_event.emit({"event": "mouse_press", "button": NameConverter.ButtonConvert(event.button())})
        elif event.type() == QEvent.Type.MouseButtonRelease:
            self.screen_event.emit({"event": "mouse_release", "button": NameConverter.ButtonConvert(event.button())})
        elif event.type() == QEvent.Type.MouseButtonDblClick:
            self.screen_event.emit({"event": "mouse_double_click", "button": NameConverter.ButtonConvert(event.button())})
        elif event.type() == QEvent.Type.Wheel:
            self.screen_event.emit({"event": "mouse_wheel", "x": event.angleDelta().x(), "y": event.angleDelta().y()})
        elif event.type() == QEvent.Type.KeyPress:
            self.screen_event.emit({"event": "key_press", "key": NameConverter.KeyConvert(event.key())})
        elif event.type() == QEvent.Type.KeyRelease:
            self.screen_event.emit({"event": "key_release", "key": NameConverter.KeyConvert(event.key())})

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
        self.window.screen_event.connect(self.sendScreenEvent)
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

    send_screen_event = None # Signal(str, dict)
    def sendScreenEvent(self, data: dict):
        if self.send_screen_event is not None:
            self.send_screen_event.emit(self.id, data)
