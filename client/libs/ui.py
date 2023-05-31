from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtNetwork import QAbstractSocket
from PySide6.QtCore import Signal, Slot
from PySide6.QtGui import QCloseEvent

from . import service, settings, processor
from .logger import logger as lg

class Scene_About(QtWidgets.QWidget):
    def __init__(self, settings, parent = None):
        super().__init__(parent)
        self.settings = settings

class Scene_Settings(QtWidgets.QWidget):
    def __init__(self, settings, parent = None):
        super().__init__(parent)
        self.settings = settings

class Scene_Control(QtWidgets.QWidget):
    """
    The Left Layout: A panel contains friend list and a horizontal layout for the buttons.
    The Right Layout: A Vertical layout contains two vertical layout that one contains two line edits for showing id and password,
    the other contains a line edit for inputting the id of friends and a button for connecting to the friend.
    """
    id_list = list()
    password_list = list()
    def __init__(self, settings, parent = None):
        super().__init__(parent)
        self.settings = settings
        self.msg_addfriend = MsgBox_AddFriend()
        self.msg_addfriend.hide()
        self.msg_addfriend.AddFriend.connect(self.add_friend)

        # Create a layout for the central widget
        layout = QtWidgets.QHBoxLayout()
        layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.setLayout(layout)

        # Create a layout for the left panel
        friend_panel = QtWidgets.QVBoxLayout()
        friend_panel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addLayout(friend_panel, 1)

        # Create a list for the friends
        self.friend_list = QtWidgets.QListWidget()
        self.friend_list.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)
        self.friend_list.itemSelectionChanged.connect(self.onSelectionChanged)
        self.load_friend_settings()
        friend_panel.addWidget(self.friend_list, 1)

        # Create a horizontal layout for the buttons
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        friend_panel.addLayout(button_layout)

        # Create a button for adding friends
        add_friend_button = QtWidgets.QPushButton("Add")
        add_friend_button.setMaximumWidth(50)
        add_friend_button.clicked.connect(self.msg_addfriend.show)
        button_layout.addWidget(add_friend_button)

        # Create a button for removing friends
        remove_friend_button = QtWidgets.QPushButton("Remove")
        remove_friend_button.setMaximumWidth(50)
        remove_friend_button.clicked.connect(self.remove_friend)
        button_layout.addWidget(remove_friend_button)

        # Create a button for connecting to friends
        self.connect_friends_button = QtWidgets.QPushButton("Connect")
        self.connect_friends_button.setMaximumWidth(50)
        button_layout.addWidget(self.connect_friends_button)

        # Create a layout for the right panel
        right_layout = QtWidgets.QVBoxLayout()
        right_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addLayout(right_layout, 2)

        # Create a vertical layout for the id and password
        id_password_layout = QtWidgets.QVBoxLayout()
        id_password_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        right_layout.addLayout(id_password_layout, 2)

        # Create a line edit to show the id
        self.id = QtWidgets.QLineEdit()
        self.id.setReadOnly(True)
        self.id.setMaximumWidth(150)
        self.id.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.id.setText("-")
        id_password_layout.addWidget(self.id)

        # Create a line edit to show the password
        self.password = QtWidgets.QLineEdit()
        self.password.setReadOnly(True)
        self.password.setMaximumWidth(150)
        self.password.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.id.setText("-")
        id_password_layout.addWidget(self.password)

        # Create a vertical layout for the id input and connect button
        id_connect_layout = QtWidgets.QVBoxLayout()
        id_connect_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        right_layout.addLayout(id_connect_layout, 3)

        # Create a line edit to input the id of friends
        self.friend_id = QtWidgets.QLineEdit()
        self.friend_id.setPlaceholderText("Friend ID")
        self.friend_id.setMaximumWidth(150)
        self.friend_id.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        id_connect_layout.addWidget(self.friend_id)

        # Create a button to connect to the friend
        self.connect_button = QtWidgets.QPushButton("Connect")
        self.connect_button.setMaximumWidth(100)
        #connect_button.clicked.connect(self.connect)
        id_connect_layout.addWidget(self.connect_button)

    def add_friend(self, name, id, pwd):
        item = QtWidgets.QListWidgetItem()
        item.setText(name)
        item.setToolTip("ID: " + id + "\r\nPassword: " + pwd)
        data = {"id": id, "pwd": pwd}
        item.setData(QtCore.Qt.ItemDataRole.UserRole, data)
        self.friend_list.addItem(item)
        self.update_friend_settings()

    def remove_friend(self):
        items = self.friend_list.selectedItems()
        for item in items:
            self.friend_list.takeItem(self.friend_list.row(item))
            del item
        self.update_friend_settings()

    def onSelectionChanged(self):
        items = self.friend_list.selectedItems()
        self.id_list.clear()
        self.password_list.clear()
        for item in items:
            data = item.data(QtCore.Qt.ItemDataRole.UserRole)
            self.id_list.append(data["id"])
            self.password_list.append(data["pwd"])

    def load_friend_settings(self):
        friends = self.settings.getFriendList()
        for friend in friends:
            item = QtWidgets.QListWidgetItem()
            item.setText(friend[1])
            item.setToolTip("ID: " + friend[0] + "\r\nPassword: " + friend[2])
            data = {"id": friend[0], "pwd": friend[2]}
            item.setData(QtCore.Qt.ItemDataRole.UserRole, data)
            self.friend_list.addItem(item)

    def update_friend_settings(self):
        friends = list()
        for i in range(self.friend_list.count()):
            item = self.friend_list.item(i)
            data = item.data(QtCore.Qt.ItemDataRole.UserRole)
            friends.append((data["id"], item.text(), data["pwd"]))

        self.settings.setFriendList(friends)

class Scene_LocateServer(QtWidgets.QWidget):
    def __init__(self, settings, parent = None):
        super().__init__(parent)
        self.setMaximumWidth(400)
        self.settings = settings

        # Create a layout for the central widget
        layout = QtWidgets.QVBoxLayout()
        layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.setLayout(layout)

        # Create a label to hold the image
        label = QtWidgets.QLabel()
        label.setText("Please enter the branch server address and port\r\n(leave empty for default value)")
        label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        label.setWordWrap(True)
        layout.addWidget(label)

        middle_layout = QtWidgets.QHBoxLayout()
        layout.addLayout(middle_layout)

        # Create a line edit to enter the server address
        self.server_address = QtWidgets.QLineEdit()
        self.server_address.setPlaceholderText("Server address")
        self.server_address.setText(self.settings.status_service_address)
        self.server_address.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        middle_layout.addWidget(self.server_address, 5)

        self.server_port = QtWidgets.QSpinBox()
        self.server_port.setRange(0, 65535)
        self.server_port.setValue(self.settings.status_service_port)
        self.server_port.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        middle_layout.addWidget(self.server_port, 1)

        # Create a button to connect to the server
        self.confirm_button = QtWidgets.QPushButton("Confirm")
        layout.addWidget(self.confirm_button)

        self.disconnect_button = QtWidgets.QPushButton("Disconnect")
        self.disconnect_button.setDisabled(True)
        layout.addWidget(self.disconnect_button)

class Scene_Home(QtWidgets.QWidget):
    """
        Create a label to hold the image and a label to hold the welcome message.
    """
    def __init__(self, settings, parent = None):
        super().__init__(parent)

        # Create a layout for the central widget
        layout = QtWidgets.QVBoxLayout()
        layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(20)
        self.setLayout(layout)

        # Create a label to hold the image
        label = QtWidgets.QLabel()
        label.setText("Welcome to Remoter!")
        label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        # Create a label to hold the welcome message
        label = QtWidgets.QLabel()
        label.setText("Remoter is a remote control application that can control the computer remotely.")
        label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        # Create a label to show logo
        logo = QtWidgets.QLabel()
        logo.setPixmap(settings.getLogo(200))
        logo.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo)

class Scene_Test(QtWidgets.QWidget):
    """
    Create a line editor to enter string and a button to send it to the server.
    """
    def __init__(self, settings, parent = None):
        super().__init__(parent)
        self.settings = settings

        # Create a layout for the central widget
        layout = QtWidgets.QVBoxLayout()
        layout.setAlignment(QtCore.Qt.AlignCenter)
        self.setLayout(layout)

        # Create a line edit to enter the string
        self.line_edit = QtWidgets.QLineEdit()
        self.line_edit.setPlaceholderText("Enter string")
        self.line_edit.setText(self.settings.getTestJson())
        self.line_edit.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.line_edit)

        # Create a button to send the string to the server
        self.send_button = QtWidgets.QPushButton("Send")
        layout.addWidget(self.send_button)

class Scene(QtWidgets.QWidget):
    """
        Create a VBox layout that the top widget is a label for the title, 
        the middle widget is a HBox layout that the left widget contains buttons that can change the scenes (home, locate_server, settings, about) and
        the right widget contains the scene widget, the bottom widget is a label for the status.

        Default scene is home.
    """
    def __init__(self, settings, parent = None):
        super().__init__(parent)
        self.settings = settings

        # Create a layout for the central widget
        layout = QtWidgets.QVBoxLayout()
        layout.setAlignment(QtCore.Qt.AlignCenter)
        self.setLayout(layout)

        # Create a label to hold the title
        title = QtWidgets.QLabel()
        title.setText("Remoter")
        title.setAlignment(QtCore.Qt.AlignCenter)
        # Set the font size to 20 and make it bold
        font = QtGui.QFont()
        font.setPointSize(20)
        font.setBold(True)
        title.setFont(font)
        layout.addWidget(title, 0)

        # Create a layout for the buttons
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.setAlignment(QtCore.Qt.AlignCenter)
        layout.addLayout(button_layout, 0)

        self.scenes = [["Home", Scene_Home(self.settings), self.to_home], 
                       ["Locate Server", Scene_LocateServer(self.settings), self.to_locate_server],
                       ["Control", Scene_Control(self.settings), self.to_control],
                       ["Settings", Scene_Settings(self.settings), self.to_settings], 
                       ["About", Scene_About(self.settings), self.to_about],
                       ["Test", Scene_Test(self.settings), self.to_test]]
        for i in range(len(self.scenes)):
            self.scenes[i][1].hide()
            self.scenes[i].append(QtWidgets.QPushButton(self.scenes[i][0]))
            self.scenes[i][-1].num = i
            self.scenes[i][-1].clicked.connect(self.scenes[i][2])
            button_layout.addWidget(self.scenes[i][-1])

        # Create a layout to hold the scene
        self.scene = QtWidgets.QHBoxLayout()
        self.scene.setAlignment(QtCore.Qt.AlignCenter)
        self.scene.addWidget(self.scenes[0][1])
        self.scenes[0][1].show()
        layout.addLayout(self.scene, 1)

    def change_scene(self, num):
        lg.log(num)
        self.scene.itemAt(0).widget().hide()
        self.scene.removeItem(self.scene.itemAt(0))
        self.scene.addWidget(self.scenes[num][1])
        self.scenes[num][1].show()

    def to_home(self):
        self.change_scene(0)

    def to_locate_server(self):
        self.change_scene(1)

    def to_control(self):
        self.change_scene(2)

    def to_settings(self):
        self.change_scene(3)

    def to_about(self):
        self.change_scene(4)

    def to_test(self):
        self.change_scene(5)

class Entry(QtWidgets.QMainWindow):
    status_bar_resetter = QtCore.QTimer()
    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        self.status_service = service.StatusService(settings)
        self.status_processer = processor.StatusProcessor(settings, self.status_service)
        self.design(settings)
        self.build()

        QtCore.QTimer.singleShot(2500, self.show)

    def closeEvent(self, event: QCloseEvent) -> None:
        if self.status_service.socket.state() != QAbstractSocket.SocketState.UnconnectedState:
            self.status_service.socket.disconnectFromHost()

    def design(self, settings):
        self.setWindowTitle("Remoter")
        self.resize(800, 600)
        self.setWindowIcon(settings.getLogoIcon())

        # Create a widget to hold the layout
        self.scene = Scene(settings)
        self.setCentralWidget(self.scene)

        # Create a label to hold the status
        self.status_bar = QtWidgets.QStatusBar()
        self.status_bar.setStyleSheet("background-color: green;")
        self.status_bar.showMessage("Ready")
        self.setStatusBar(self.status_bar)

    def build(self):
        self.scene.scenes[1][1].confirm_button.clicked.connect(self.ConnectStatus)
        self.scene.scenes[1][1].disconnect_button.clicked.connect(self.DisconnectStatus)
        self.scene.scenes[2][1].connect_friends_button.clicked.connect(self.ConnectFriends)
        self.scene.scenes[5][1].send_button.clicked.connect(self.sendTest)
        self.status_service.connected.connect(self.onConnected)
        self.status_service.disconnected.connect(self.onDisconnected)
        self.status_service.error_occurred.connect(self.showError)
        self.status_processer.have_info.connect(self.showInfo)
        self.status_processer.error_occurred.connect(self.showError)
        self.status_processer.need_connect.connect(self.ConnectComfirm)
        self.status_bar_resetter.timeout.connect(self.clearStatusBar)

    def ConnectStatus(self):
        self.settings.setStatusServer(self.scene.scenes[1][1].server_address.text(), self.scene.scenes[1][1].server_port.value())
        self.status_service.start()

    def DisconnectStatus(self):
        self.status_service.stop()

    def ConnectFriends(self):
        self.status_processer.AskConnect(self.scene.scenes[2][1].id_list, self.scene.scenes[2][1].password_list)

    def ConnectComfirm(self, id: str):
        msgBox = QtWidgets.QMessageBox()
        msgBox.setWindowTitle("A Friend Want to Connect You!")
        msgBox.setText("ID \"{}\" Connection Need".format(id))
        msgBox.setInformativeText("Do you want to accept?")
        msgBox.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No)
        msgBox.setDefaultButton(QtWidgets.QMessageBox.StandardButton.Yes)
        ret = msgBox.exec()
        if ret == QtWidgets.QMessageBox.StandardButton.Yes:
            self.status_processer.ReturnNeedConnect(True, id)
        else:
            self.status_processer.ReturnNeedConnect(False, id, "Refused by user")

    def onConnected(self):
        self.scene.scenes[1][1].confirm_button.setDisabled(True)
        self.scene.scenes[1][1].disconnect_button.setDisabled(False)

    def onDisconnected(self):
        self.scene.scenes[1][1].confirm_button.setDisabled(False)
        self.scene.scenes[1][1].disconnect_button.setDisabled(True)

    def showError(self, error):
        self.status_bar.showMessage(str(error))
        # Set the background color to red
        self.status_bar.setStyleSheet("background-color: red")
        self.status_bar_resetter.start(2000)

    def showInfo(self, info):
        self.status_bar.showMessage(str(info))
        # Set the background color to blue
        self.status_bar.setStyleSheet("background-color: blue")
        self.status_bar_resetter.start(2000)

    def clearStatusBar(self):
        # Set the background color to green
        self.status_bar.setStyleSheet("background-color: green")
        self.status_bar.showMessage("Ready")

    def sendTest(self):
        self.settings.setTestJson(self.scene.scenes[5][1].line_edit.text())
        json = QtCore.QJsonDocument.fromJson(self.scene.scenes[5][1].line_edit.text().encode())
        self.status_service.send(json)
        self.status_bar.showMessage("Send: " + self.scene.scenes[5][1].line_edit.text())
        self.status_bar_resetter.start(10000)


class MsgBox_AddFriend(QtWidgets.QMainWindow):
    """
    Create a line edit to enter the friend's name, a line edit to enter the friend's ID,
    a password edit to enter the friend's password, a button to confirm, a button to cancel.
    They are all in a vertical layout.
    """
    def __init__(self, parent = None):
        super().__init__(parent)
        self.setWindowTitle("Add Friend")

        # Create a widget to hold the layout
        self.widget = QtWidgets.QWidget()
        self.setCentralWidget(self.widget)

        # Create a layout to hold the widgets
        self.layout = QtWidgets.QVBoxLayout()
        self.widget.setLayout(self.layout)

        # Create a label to hold the title
        title = QtWidgets.QLabel("Add Friend")
        title.setAlignment(QtCore.Qt.AlignCenter)
        self.layout.addWidget(title)

        # Create a line edit to enter the friend's name
        self.name = QtWidgets.QLineEdit()
        self.name.setPlaceholderText("Name")
        self.layout.addWidget(self.name)

        # Create a line edit to enter the friend's ID
        self.id = QtWidgets.QLineEdit()
        self.id.setPlaceholderText("ID")
        self.layout.addWidget(self.id)

        # Create a password edit to enter the friend's password
        self.password = QtWidgets.QLineEdit()
        self.password.setPlaceholderText("Password")
        self.password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.layout.addWidget(self.password)

        # Create a button to confirm
        self.confirm_button = QtWidgets.QPushButton("Confirm")
        self.confirm_button.clicked.connect(self.confirm)
        self.layout.addWidget(self.confirm_button)

        # Create a button to cancel
        self.cancel_button = QtWidgets.QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.hide)
        self.layout.addWidget(self.cancel_button)

    AddFriend = Signal(str, str, str)
    def confirm(self):
        if self.name.text() == "":
            self.name.setFocus()
        elif self.id.text() == "":
            self.id.setFocus()
        else:
            self.AddFriend.emit(self.name.text(), self.id.text(), self.password.text())
            self.hide()
            self.name.clear()
            self.id.clear()
            self.password.clear()