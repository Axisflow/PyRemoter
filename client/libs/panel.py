from PySide6.QtCore import Qt, QObject, Signal, Slot, QThread, QTimer, QEvent, QByteArray, QBuffer, QIODevice, QProcess, QSize
from PySide6.QtGui import QScreen, QPixmap, QResizeEvent, QDesktopServices
from PySide6.QtWidgets import QMainWindow, QApplication, QWidget, QLabel, QStatusBar, QTextBrowser, QLineEdit, QVBoxLayout
from PySide6.QtMultimedia import QMediaRecorder
import pyautogui
import locale

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
    def ButtonConvert(button: Qt.MouseButton) -> str:
        return NameConverter.__mouse_map__[button]

class ControlBackground(QObject):
    def __init__(self, settings: settings.Settings):
        super().__init__()
        self.settings = settings

        self.shot_timer = QTimer(self)
        self.shot_timer.timeout.connect(self.shot)
        self.shot_timer.setInterval(1000)
        self.shot_timer.start()

        self.console = QProcess(self)
        self.console.setProgram(self.settings.getDefaultTerminal())
        self.console.setWorkingDirectory(self.settings.getConsoleTempDir())
        self.console.readyReadStandardOutput.connect(self.onConsoleReadyReadStdout)
        self.console.readyReadStandardError.connect(self.onConsoleReadyReadStderr)
        self.console.finished.connect(self.restartConsole)
        self.console.start()

    screenshotted = Signal(QPixmap)
    def shot(self):
        screen = QScreen.grabWindow(QApplication.primaryScreen(), 0)
        pixmap = QPixmap(screen)
        self.screenshotted.emit(pixmap)

    console_output = Signal(QByteArray)
    @Slot()
    def onConsoleReadyReadStdout(self):
        self.console_output.emit(self.console.readAllStandardOutput().data().decode(locale.getpreferredencoding()).encode("utf-8"))

    @Slot()
    def onConsoleReadyReadStderr(self):
        self.console_output.emit(self.console.readAllStandardError().data().decode(locale.getpreferredencoding()).encode("utf-8"))

    @Slot(int, QProcess.ExitStatus)
    def restartConsole(self, state: int, status: QProcess.ExitStatus):
        self.console_output.emit("[Console] {} with state code {}\r\n[Console] Restarting...\r\n\r\n".format("Exited" if status == QProcess.ExitStatus.NormalExit else "Crashed", state).encode("utf-8"))
        self.console.start()

    def WriteConsole(self, data: str):
        self.console.write(data.encode("utf-8"))

class NeedManagement(QObject):
    class Thread(QThread):
        def run(self):
            self.exec()

    inform = None # Signal(str, str, str) # id, key, value
    def __init__(self, settings: settings.Settings, id: str):
        super().__init__()
        self.settings = settings
        self.id = id

        self.self_thread = NeedManagement.Thread(self)
        self.moveToThread(self.self_thread)
        self.self_thread.start()

        self.background = ControlBackground(self.settings)
        self.background.moveToThread(self.self_thread)
        self.background.screenshotted.connect(self.processScreenShot)
        self.background.console_output.connect(self.processConsoleOutput)

    send_screen = None # Signal(str, QByteArray) # id, pixmap
    def processScreenShot(self, pixmap: QPixmap):
        if self.send_screen != None:
            self.send_screen.emit(self.id, self.toByteArray(pixmap))
        

    @Slot(QByteArray)
    def processConsoleOutput(self, data: QByteArray):
        if self.inform != None:
            self.inform.emit(self.id, "ConsoleOutput", data.data().decode("utf-8", "ignore"))

    @Slot(str, str)
    def NeedUpdate(self, key: str, value: str):
        if key == "ConsoleInput":
            self.background.WriteConsole(value)
        else:
            lg.log("Unknown Key: " + key)

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

    @staticmethod
    def toByteArray(pixmap: QPixmap):
        _bytes = QByteArray()
        _buffer = QBuffer(_bytes)
        _buffer.open(QIODevice.OpenModeFlag.WriteOnly)
        pixmap.save(_buffer, "JPG")
        return _bytes

class ControlWindow(QMainWindow):
    now_resolution = QSize(0, 0)
    def __init__(self, settings: settings.Settings):
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
        self.control_screen = QLabel(self.central_widget)
        self.control_screen.setFocusPolicy(Qt.FocusPolicy.WheelFocus)
        self.control_screen.setMouseTracking(True)
        self.control_screen.mouseMoveEvent = self.ScreenEvent
        self.control_screen.mousePressEvent = self.ScreenEvent
        self.control_screen.mouseReleaseEvent = self.ScreenEvent
        self.control_screen.mouseDoubleClickEvent = self.ScreenEvent
        self.control_screen.wheelEvent = self.ScreenEvent
        self.control_screen.keyPressEvent = self.ScreenEvent
        self.control_screen.keyReleaseEvent = self.ScreenEvent

        self.setFocusProxy(self.control_screen)
        self.central_widget.setFocusProxy(self.control_screen)
        lg.log("ControlWindow initialized")

    screen_event = Signal(dict)
    def ScreenEvent(self, event):
        if event.type() == QEvent.Type.MouseMove:
            self.screen_event.emit({"event": "mouse_move", "x": self.now_resolution.width() / self.control_screen.width() * event.position().x(), "y": self.now_resolution.height() / self.control_screen.height() * event.position().y()})
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

    original_screen = None # QPixmap
    @Slot(int, QByteArray)
    def setScreenData(self, pixmap):
        _p = ControlWindow.fromByteArray(pixmap)
        if(self.now_resolution != _p.size()):
            self.now_resolution = _p.size()
            self.resizeScreen()
        
        self.original_screen = _p
        self.resizeScreen()

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        self.resizeControlScreen()

    def resizeControlScreen(self):
        # resize the screen to the size of the central widget but keep the ratio
        width = self.now_resolution.width() if self.now_resolution.width() != 0 else 1
        height = self.now_resolution.height() if self.now_resolution.height() != 0 else 1
        if width * self.central_widget.height() >= self.central_widget.width() * height:
            self.control_screen.resize(self.central_widget.width(), self.central_widget.width() / width * height)
        else:
            self.control_screen.resize(self.central_widget.height() / height * width, self.central_widget.height())

        self.resizeScreen()
        self.control_screen.move(self.central_widget.rect().center() - self.control_screen.rect().center())

    def resizeScreen(self):
        if self.original_screen != None:
            self.control_screen.setPixmap(self.original_screen.scaled(self.control_screen.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

    @staticmethod
    def fromByteArray(data: QByteArray) -> QPixmap:
        p = QPixmap()
        p.loadFromData(data, "JPG")
        return p

class ControlConsole(QMainWindow):
    append_output = Signal(str)
    def __init__(self, settings: settings.Settings):
        super().__init__()
        self.settings = settings

        self.setWindowTitle("Console")

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        
        """
        Create a vertical layout and add a text browser and a line edit to it.
        """
        self.console_layout = QVBoxLayout(self.central_widget)
        self.console_layout.setSpacing(0)
        self.console_layout.setContentsMargins(0, 0, 0, 0)

        self.output = QTextBrowser()
        self.output.setReadOnly(True)
        self.output.setOpenExternalLinks(True)
        self.output.setOpenLinks(True)
        self.output.anchorClicked.connect(self.openLink)
        self.console_layout.addWidget(self.output, 1)

        self.input = QLineEdit()
        self.input.returnPressed.connect(self.sendCommand)
        self.console_layout.addWidget(self.input)

        self.append_output.connect(self.AppendOutput)

    def openLink(self, url):
        QDesktopServices.openUrl(url)

    command_sent = Signal(str)
    def sendCommand(self):
        command = self.input.text()
        self.input.clear()
        self.command_sent.emit(command + "\r\n")

    @Slot(str)
    def AppendOutput(self, text):
        self.output.insertPlainText(text)

class AskManagement(QObject):
    class Thread(QThread):
        def run(self):
            self.exec()

    update = None # Signal(str, str)
    def __init__(self, settings: settings.Settings, id: str):
        super().__init__()
        self.settings = settings
        self.id = id
        
        self.self_thread = AskManagement.Thread(self)
        self.moveToThread(self.self_thread)
        self.self_thread.start()

        self.start.connect(self.__start__)

        self.window = ControlWindow(self.settings)
        self.window.screen_event.connect(self.sendScreenEvent)
        self.window.show()

        self.console = ControlConsole(self.settings)
        self.console.command_sent.connect(self.sendCommand)
        self.console.show()
        lg.log("AskManagement started")

    start = Signal()
    @Slot()
    def __start__(self):
        pass

    @Slot(QByteArray)
    def setScreenPixmap(self, pixmap):
        self.window.setScreenData(pixmap)

    send_screen_event = None # Signal(str, dict)
    def sendScreenEvent(self, data: dict):
        if self.send_screen_event != None:
            self.send_screen_event.emit(self.id, data)

    @Slot(str)
    def sendCommand(self, command: str):
        if self.update != None:
            self.update.emit(self.id, "ConsoleInput", command)

    @Slot(str, str)
    def NeedInform(self, key: str, value: str):
        if key == "ConsoleOutput":
            self.console.append_output.emit(value)
