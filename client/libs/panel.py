from PySide6.QtCore import Qt, QObject, Signal, Slot, QThread, QTimer, QEvent, QByteArray, QBuffer, QIODevice, QProcess, QSize, QRandomGenerator
from PySide6.QtGui import QScreen, QPixmap, QResizeEvent, QDesktopServices, QCloseEvent, QImage, QEnterEvent
from PySide6.QtWidgets import QMainWindow, QApplication, QWidget, QLabel, QStatusBar, QTextBrowser, QLineEdit, QVBoxLayout, QHBoxLayout
from PySide6.QtMultimedia import QMediaRecorder
import enum
import pyautogui
import locale

from . import settings
from .logger import logger as lg


class FeatureType(enum.IntEnum):
    Null = 0
    Screen = 1
    Console = 2
    Keyboard = 3
    Mouse = 4
    Speaker = 5
    Camera = 6
    Microphone = 7
    Clipboard = 8
    File = 9
    Chat = 10

class FeatureButton(QLabel):
    enabled = Signal(FeatureType)
    disabled = Signal(FeatureType)
    def __init__(self, settings: settings.Settings, feature: FeatureType, parent: QWidget):
        super().__init__(parent)
        self.settings = settings
        self.feature = feature
        self.setText(self.feature.name)
        self.setFixedSize(self.settings.getFeatureButtonSize())
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setPixmap(self.settings.getFeatureImage(self.feature.name))
        self.state = False

    def releaseMouse(self) -> None:
        self.UserChangeState()
        return super().releaseMouse()

    def UserChangeState(self):
        self.state = not self.state
        if self.state:
            self.enabled.emit(self.feature)
        else:
            self.disabled.emit(self.feature)

    def Enable(self):
        self.state = True

    def Disable(self):
        self.state = False

class SessionController(QMainWindow):
    enabled = Signal(FeatureType)
    disabled = Signal(FeatureType)
    def __init__(self, settings: settings.Settings, id: str):
        super().__init__()
        self.settings = settings
        self.id = id
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, False)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        """
        Create a vertical layout that will contain (a horizontal layout with close label,
        expand label and a horizontal layout with feature buttons) and an ID label.
        """
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setLayout(self.main_layout)

        self.top_layout = QHBoxLayout()
        self.top_layout.setContentsMargins(0, 0, 0, 0)
        self.top_layout.setSpacing(0)
        self.top_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addLayout(self.top_layout)

        self.close_label = QLabel()
        self.close_label.setFixedSize(self.settings.getFeatureButtonSize())
        self.close_label.setPixmap(self.settings.getFeatureImage("Close"))
        self.close_label.setScaledContents(True)
        self.close_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.close_label.mousePressEvent = self.close
        self.top_layout.addWidget(self.close_label)

        self.expand_label = QLabel()
        self.expand_label.setFixedSize(self.settings.getFeatureButtonSize())
        self.expand_label.setPixmap(self.settings.getFeatureImage("Expand"))
        self.expand_label.setScaledContents(True)
        self.expand_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.expand_label.enterEvent = self.Expend
        self.expand_label.leaveEvent = self.Unexpend
        self.top_layout.addWidget(self.expand_label)

        self.features_widget = QWidget()
        self.top_layout.addWidget(self.features_widget)

        self.feature_layout = QHBoxLayout()
        self.feature_layout.setContentsMargins(0, 0, 0, 0)
        self.feature_layout.setSpacing(0)
        self.feature_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.features_widget.setLayout(self.feature_layout)

        self.feature_buttons = {}
        for feature in FeatureType:
            if feature != FeatureType.Null:
                feature_button = FeatureButton(self.settings, feature, self.features_widget)
                feature_button.enabled.connect(self.enabled)
                feature_button.disabled.connect(self.disabled)
                self.feature_layout.addWidget(feature_button)
                self.feature_buttons[feature.name] = feature_button

        self.id_label = QLabel()
        self.id_label.setText(self.id)
        self.id_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.id_label)

        self.move(QRandomGenerator.global_().bounded(self.width(), QApplication.primaryScreen().size().width() - 2 * self.width()), self.id_label.height() - self.height())

    def enterEvent(self, event: QEnterEvent) -> None:
        self.move(self.x(), 0)
        return super().enterEvent(event)
    
    def leaveEvent(self, event: QEnterEvent) -> None:
        self.move(self.x(), self.id_label.height() - self.height())
        return super().leaveEvent(event)
    
    session_closed = Signal(str) # id
    def closeEvent(self, event: QCloseEvent) -> None:
        self.session_closed.emit(self.id)
        return super().closeEvent(event)

    def Expend(self, event):
        self.setFixedSize(self.settings.getFeatureButtonSize() * (len(self.feature_buttons) + 2))
        self.expand_label.setPixmap(self.settings.getFeatureImage("Unexpand"))

    def Unexpend(self, event):
        self.setFixedSize(self.settings.getFeatureButtonSize())
        self.expand_label.setPixmap(self.settings.getFeatureImage("Expand"))

    @Slot(FeatureType)
    def UserEnable(self, feature: FeatureType):
        self.enabled.emit(feature)

    @Slot(FeatureType)
    def UserDisable(self, feature: FeatureType):
        self.disabled.emit(feature)

    @Slot(FeatureType, bool)
    def setClickable(self, feature: FeatureType, clickable: bool):
        self.feature_buttons[feature.name].setEnable(clickable)

    @Slot(FeatureType)
    def Enable(self, feature: FeatureType):
        self.feature_buttons[feature.name].Enable()

    @Slot(FeatureType)
    def Disable(self, feature: FeatureType):
        self.feature_buttons[feature.name].Disable()

#
#
#
#
#
# Need
#
#
#
#
#
class NeedManagement(QObject):
    class Thread(QThread):
        def run(self):
            self.exec()

    inform = None # Signal(str, str, str) # id, key, value
    session_closed = Signal(str) # id
    def __init__(self, settings: settings.Settings, id: str):
        super().__init__()
        self.settings = settings
        self.id = id

        self.self_thread = NeedManagement.Thread(self)
        self.moveToThread(self.self_thread)
        self.self_thread.start()

        self.session_controller = SessionController(self.settings, self.id)
        self.session_controller.session_closed.connect(self.session_closed)
        self.session_controller.enabled.connect(self.EnableFeature)
        self.session_controller.disabled.connect(self.DisableFeature)
        self.__session_enable_feature.connect(self.session_controller.Enable)
        self.__session_disable_feature.connect(self.session_controller.Disable)
        self.__session_clickable_feature.connect(self.session_controller.setClickable)
        self.session_controller.show()

        self.initialize_features()

    __session_enable_feature = Signal(FeatureType)
    __session_disable_feature = Signal(FeatureType)
    __session_clickable_feature = Signal(FeatureType, bool)
    def initialize_features(self):
        self.screen_process = ScreenProcess(self.settings)
        self.screen_process.moveToThread(self.self_thread)
        self.screen_process.screenshotted.connect(self.processScreenShot)

        self.console_process = ConsoleProcess(self.settings)
        self.console_process.moveToThread(self.self_thread)
        self.console_process.console_output.connect(self.processConsoleOutput)

        if self.settings.existFriendData(self.id, "need_features_state"):
            self.features_state = self.settings.getFriendData(self.id, "need_features_state")
        else:
            self.features_state = {}
            for feature in FeatureType:
                self.features_state[feature.name] = False
            self.settings.setFriendData(self.id, "need_features_state", self.features_state)

        for i in FeatureType:
            if i.name not in self.features_state:
                self.features_state[i.name] = False

            if self.features_state[i.name]:
                self.__session_enable_feature.emit(i)
                self.EnableFeature(i)
            else:
                self.__session_disable_feature.emit(i)
                self.DisableFeature(i)
    
    def terminate(self):
        self.session_controller.close()
        self.screen_process.terminate()
        self.console_process.terminate()
        self.settings.setFriendData(self.id, "need_features_state", self.features_state)
        self.self_thread.quit()
        self.self_thread.wait()

    def EnableFeature(self, feature: FeatureType):
        self.features_state[feature.name] = True
        if feature == FeatureType.Screen:
            self.screen_process.enable()
        elif feature == FeatureType.Keyboard:
            pass
        elif feature == FeatureType.Mouse:
            pass
        elif feature == FeatureType.Console:
            self.console_process.enable()
        else:
            lg.log("Unknown Feature: " + feature.name)
        self.inform.emit(self.id, "EnableFeature", feature.name)

    def DisableFeature(self, feature: FeatureType):
        self.features_state[feature.name] = False
        if feature == FeatureType.Screen:
            self.screen_process.disable()
        elif feature == FeatureType.Keyboard:
            pass
        elif feature == FeatureType.Mouse:
            pass
        elif feature == FeatureType.Console:
            self.console_process.disable()
        else:
            lg.log("Unknown Feature: " + feature.name)
        self.inform.emit(self.id, "DisableFeature", feature.name)

    @Slot(str, str)
    def NeedUpdate(self, key: str, value: str):
        if key == "ConsoleInput":
            self.console_process.WriteConsole(value)
        elif key == "EnableFeature":
            self.EnableFeature(FeatureType[value])
        elif key == "DisableFeature":
            self.DisableFeature(FeatureType[value])
        else:
            lg.log("Unknown Key: " + key)

    send_screen = None # Signal(str, QByteArray) # id, pixmap
    def processScreenShot(self, pixmap: QPixmap):
        if self.send_screen != None:
            self.send_screen.emit(self.id, self.toByteArray(pixmap))

    @Slot(QByteArray)
    def processConsoleOutput(self, data: QByteArray):
        if self.inform != None:
            self.inform.emit(self.id, "ConsoleOutput", data.data().decode("utf-8", "ignore"))

    @Slot(dict)
    def ProcessScreenEvent(self, event: dict):
        if event["event"] == "mouse_move":
            if self.features_state[FeatureType.Mouse.name]:
                pyautogui.moveTo(event["x"], event["y"])
        elif event["event"] == "mouse_press":
            if self.features_state[FeatureType.Mouse.name]:
                pyautogui.mouseDown(button=event["button"])
        elif event["event"] == "mouse_release":
            if self.features_state[FeatureType.Mouse.name]:
                pyautogui.mouseUp(button=event["button"])
        elif event["event"] == "mouse_double_click":
            if self.features_state[FeatureType.Mouse.name]:
                pyautogui.doubleClick(button=event["button"])
        elif event["event"] == "mouse_wheel":
            if self.features_state[FeatureType.Mouse.name]:
                if(event["x"] > 0):
                    pyautogui.hscroll(1)
                elif(event["x"] < 0):
                    pyautogui.hscroll(-1)
                if(event["y"] > 0):
                    pyautogui.vscroll(1)
                elif(event["y"] < 0):
                    pyautogui.vscroll(-1)
        elif event["event"] == "key_press":
            if self.features_state[FeatureType.Keyboard.name]:
                pyautogui.keyDown(event["key"])
        elif event["event"] == "key_release":
            if self.features_state[FeatureType.Keyboard.name]:
                pyautogui.keyUp(event["key"])

    @staticmethod
    def toByteArray(pixmap: QPixmap):
        _bytes = QByteArray()
        _buffer = QBuffer(_bytes)
        _buffer.open(QIODevice.OpenModeFlag.WriteOnly)
        pixmap.save(_buffer, "WebP")
        _buffer.close()
        return _bytes

class ConsoleProcess(QObject):
    def __init__(self, settings: settings.Settings):
        super().__init__()
        self.settings = settings

        self.process = QProcess(self)
        self.process.setProgram(self.settings.getDefaultTerminal())
        self.process.setWorkingDirectory(self.settings.getConsoleTempDir())
        self.process.readyReadStandardOutput.connect(self.onProcessReadyReadStdout)
        self.process.readyReadStandardError.connect(self.onProcessReadyReadStderr)
        self.process.finished.connect(self.restartProcess)

    def terminate(self):
        self.process.terminate()
        self.process.waitForFinished()

    def enable(self):
        self.process.start()

    def disable(self):
        self.process.terminate()

    console_output = Signal(QByteArray)
    @Slot()
    def onProcessReadyReadStdout(self):
        self.console_output.emit(self.process.readAllStandardOutput().data().decode(locale.getpreferredencoding()).encode("utf-8"))

    @Slot()
    def onProcessReadyReadStderr(self):
        self.console_output.emit(self.process.readAllStandardError().data().decode(locale.getpreferredencoding()).encode("utf-8"))

    @Slot(int, QProcess.ExitStatus)
    def restartProcess(self, state: int, status: QProcess.ExitStatus):
        self.console_output.emit("[Process] {} with state code {}\r\n[Process] Restarting...\r\n\r\n".format("Exited" if status == QProcess.ExitStatus.NormalExit else "Crashed", state).encode("utf-8"))
        self.process.start()

    def WriteConsole(self, data: str):
        self.process.write(data.encode("utf-8"))

class ScreenProcess(QObject):
    def __init__(self, settings: settings.Settings):
        super().__init__()
        self.settings = settings

        self.shot_timer = QTimer(self)
        self.shot_timer.timeout.connect(self.shot)
        self.shot_timer.setInterval(47)
        self.shot_timer.start()

    def terminate(self):
        self.shot_timer.stop()

    def enable(self):
        self.shot_timer.start()

    def disable(self):
        self.shot_timer.stop()

    screenshotted = Signal(QPixmap)
    def shot(self):
        self.screenshotted.emit(QApplication.primaryScreen().grabWindow(0))





















































































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
        self.screen_data_setter.connect(self.setScreenData)

        self.can_move_mouse = True
        self.mouse_move_timer = QTimer(self)
        self.mouse_move_timer.setSingleShot(True)
        self.mouse_move_timer.setInterval(100)
        self.mouse_move_timer.timeout.connect(self.enableMouseMove)

        self.setFocusProxy(self.control_screen)
        self.central_widget.setFocusProxy(self.control_screen)
        lg.log("ControlWindow initialized")

    feature_state = {FeatureType.Screen: False, FeatureType.Keyboard: False, FeatureType.Mouse: False}
    def enable(self, feature: FeatureType):
        if feature == FeatureType.Screen:
            self.control_screen.setVisible(True)
            self.feature_state[feature] = True
        elif feature == FeatureType.Keyboard:
            self.feature_state[feature] = True
        elif feature == FeatureType.Mouse:
            self.feature_state[feature] = True

        self.show()

    def disable(self, feature: FeatureType):
        if feature == FeatureType.Screen:
            self.control_screen.setVisible(False)
            self.feature_state[feature] = False
        elif feature == FeatureType.Keyboard:
            self.feature_state[feature] = False
        elif feature == FeatureType.Mouse:
            self.feature_state[feature] = False

        if self.feature_state[FeatureType.Keyboard] == False and self.feature_state[FeatureType.Mouse] == False and self.feature_state[FeatureType.Screen] == False:
            self.hide()

    screen_event = Signal(dict)
    def ScreenEvent(self, event):
        if event.type() == QEvent.Type.MouseMove:
            if self.can_move_mouse and self.feature_state[FeatureType.Mouse]:
                self.screen_event.emit({"event": "mouse_move", "x": self.now_resolution.width() / self.control_screen.width() * event.position().x(), "y": self.now_resolution.height() / self.control_screen.height() * event.position().y()})
                self.can_move_mouse = False
                self.mouse_move_timer.start()
        elif event.type() == QEvent.Type.MouseButtonPress:
            if self.feature_state[FeatureType.Mouse]:
                self.screen_event.emit({"event": "mouse_press", "button": NameConverter.ButtonConvert(event.button())})
        elif event.type() == QEvent.Type.MouseButtonRelease:
            if self.feature_state[FeatureType.Mouse]:
                self.screen_event.emit({"event": "mouse_release", "button": NameConverter.ButtonConvert(event.button())})
        elif event.type() == QEvent.Type.MouseButtonDblClick:
            if self.feature_state[FeatureType.Mouse]:
                self.screen_event.emit({"event": "mouse_double_click", "button": NameConverter.ButtonConvert(event.button())})
        elif event.type() == QEvent.Type.Wheel:
            if self.can_move_mouse and self.feature_state[FeatureType.Mouse]:
                self.screen_event.emit({"event": "mouse_wheel", "x": event.angleDelta().x(), "y": event.angleDelta().y()})
                self.can_move_mouse = False
                self.mouse_move_timer.start()
        elif event.type() == QEvent.Type.KeyPress:
            if self.feature_state[FeatureType.Keyboard]:
                self.screen_event.emit({"event": "key_press", "key": NameConverter.KeyConvert(event.key())})
        elif event.type() == QEvent.Type.KeyRelease:
            if self.feature_state[FeatureType.Keyboard]:
                self.screen_event.emit({"event": "key_release", "key": NameConverter.KeyConvert(event.key())})

    def enableMouseMove(self):
        self.can_move_mouse = True

    original_screen = None # QPixmap
    screen_data_setter = Signal(QByteArray)
    @Slot(QByteArray)
    def setScreenData(self, pixmap):
        if self.feature_state[FeatureType.Screen]:
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

    closing_window_data_return = Signal(str, dict) # window type, data
    def closeEvent(self, event: QCloseEvent) -> None:
        self.closing_window_data_return.emit("control_window", {"w": self.width(), "h": self.height()})
        return super().closeEvent(event)

    @staticmethod
    def fromByteArray(data: QByteArray) -> QPixmap:
        return QPixmap.fromImage(QImage.fromData(data, "WebP"))

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

    def enable(self):
        self.show()

    def disable(self):
        self.hide()

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
        
    closing_window_data_return = Signal(str, dict) # window type, data
    def closeEvent(self, event: QCloseEvent) -> None:
        self.closing_window_data_return.emit("control_console", {"w": self.width(), "h": self.height()})
        return super().closeEvent(event)

class AskManagement(QObject):
    class Thread(QThread):
        def run(self):
            self.exec()

    update = None # Signal(str, str)
    session_closed = Signal(str)
    def __init__(self, settings: settings.Settings, id: str):
        super().__init__()
        self.settings = settings
        self.id = id
        
        self.self_thread = AskManagement.Thread(self)
        self.moveToThread(self.self_thread)
        self.self_thread.start()

        self.start.connect(self.__start__)

        self.session_controller = SessionController(self.settings, self.id)
        self.session_controller.session_closed.connect(self.session_closed)
        self.session_controller.enabled.connect(self.EnableFeature)
        self.session_controller.disabled.connect(self.DisableFeature)
        self.__session_enable_feature.connect(self.session_controller.Enable)
        self.__session_disable_feature.connect(self.session_controller.Disable)
        self.__session_clickable_feature.connect(self.session_controller.setClickable)
        self.session_controller.show()

        self.initialize_features()
        lg.log("AskManagement started")

    start = Signal()
    @Slot()
    def __start__(self):
        pass

    __session_enable_feature = Signal(FeatureType)
    __session_disable_feature = Signal(FeatureType)
    __session_clickable_feature = Signal(FeatureType, bool)
    def initialize_features(self):
        self.window = ControlWindow(self.settings)
        control_window_size = self.settings.getFriendData(id, "control_window_size") if self.settings.existFriendData(id, "control_window_size") else {"w": 1280, "h": 720}
        self.window.resize(control_window_size["w"], control_window_size["h"])
        self.window.closing_window_data_return.connect(self.saveWindowData)
        self.window.screen_event.connect(self.sendScreenEvent)
        self.window.show()

        self.console = ControlConsole(self.settings)
        control_console_size = self.settings.getFriendData(id, "control_console_size") if self.settings.existFriendData(id, "control_console_size") else {"w": 640, "h": 480}
        self.console.resize(control_console_size["w"], control_console_size["h"])
        self.console.closing_window_data_return.connect(self.saveWindowData)
        self.console.command_sent.connect(self.sendCommand)
        self.console.show()

        if self.settings.existFriendData(self.id, "ask_features_state"):
            self.features_state = self.settings.getFriendData(self.id, "ask_features_state")
        else:
            self.features_state = {}
            for feature in FeatureType:
                self.features_state[feature.name] = False
            self.settings.setFriendData(self.id, "ask_features_state", self.features_state)

        for i in FeatureType:
            if i.name not in self.features_state:
                self.features_state[i.name] = False

            if self.features_state[i.name]:
                self.__session_enable_feature.emit(i)
                self.EnableFeature(i)
            else:
                self.__session_disable_feature.emit(i)
                self.DisableFeature(i)
    
    def terminate(self):
        self.session_controller.close()
        self.window.close()
        self.console.close()
        self.settings.setFriendData(self.id, "ask_features_state", self.features_state)
        self.self_thread.quit()
        self.self_thread.wait()

    def EnableFeature(self, feature: FeatureType):
        self.features_state[feature.name] = True
        if feature == FeatureType.Screen:
            self.window.enable()
        elif feature == FeatureType.Keyboard:
            self.window.enable()
        elif feature == FeatureType.Mouse:
            self.window.enable()
        elif feature == FeatureType.Console:
            self.console.enable()
        else:
            lg.log("Unknown Feature: " + feature.name)

    def DisableFeature(self, feature: FeatureType):
        self.features_state[feature.name] = False
        if feature == FeatureType.Screen:
            self.window.disable()
        elif feature == FeatureType.Keyboard:
            self.window.disable()
        elif feature == FeatureType.Mouse:
            self.window.disable()
        elif feature == FeatureType.Console:
            self.console.disable()
        else:
            lg.log("Unknown Feature: " + feature.name)

    @Slot(QByteArray)
    def setScreenPixmap(self, pixmap):
        self.window.screen_data_setter.emit(pixmap)

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

    def saveWindowData(self, window_type: str, data: dict):
        if window_type == "control_window":
            self.settings.setFriendData(self.id, "control_window_size", {"w": data["w"], "h": data["h"]})
        elif window_type == "control_console":
            self.settings.setFriendData(self.id, "control_console_size", {"w": data["w"], "h": data["h"]})

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
