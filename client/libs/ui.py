from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtNetwork import QTcpSocket

from libs import service, settings, logger
lg = logger.logger()

class Scene_About(QtWidgets.QWidget):
    def __init__(self, settings, parent = None):
        super().__init__(parent)
        self.settings = settings

class Scene_Settings(QtWidgets.QWidget):
    def __init__(self, settings, parent = None):
        super().__init__(parent)
        self.settings = settings

class Scene_LocateServer(QtWidgets.QWidget):
    def __init__(self, settings, parent = None):
        super().__init__(parent)
        self.setMaximumWidth(400)
        self.settings = settings

        # Create a layout for the central widget
        layout = QtWidgets.QVBoxLayout()
        layout.setAlignment(QtCore.Qt.AlignCenter)
        self.setLayout(layout)

        # Create a label to hold the image
        label = QtWidgets.QLabel()
        label.setText("Please enter the branch server address and port\r\n(leave empty for default value)")
        label.setAlignment(QtCore.Qt.AlignCenter)
        label.setWordWrap(True)
        layout.addWidget(label)

        middle_layout = QtWidgets.QHBoxLayout()
        layout.addLayout(middle_layout)

        # Create a line edit to enter the server address
        self.server_address = QtWidgets.QLineEdit()
        self.server_address.setPlaceholderText("Server address")
        self.server_address.setText(self.settings.status_service_address)
        self.server_address.setAlignment(QtCore.Qt.AlignCenter)
        middle_layout.addWidget(self.server_address, 5)

        self.server_port = QtWidgets.QSpinBox()
        self.server_port.setRange(0, 65535)
        self.server_port.setValue(self.settings.status_service_port)
        self.server_port.setAlignment(QtCore.Qt.AlignCenter)
        middle_layout.addWidget(self.server_port, 1)

        # Create a button to connect to the server
        self.confirm_button = QtWidgets.QPushButton("Confirm")
        #confirm_button.clicked.connect(self.confirm)
        layout.addWidget(self.confirm_button)

class Scene_Home(QtWidgets.QWidget):
    """
        Create a label to hold the image and a label to hold the welcome message.
    """
    def __init__(self, settings, parent = None):
        super().__init__(parent)

        # Create a layout for the central widget
        layout = QtWidgets.QVBoxLayout()
        layout.setAlignment(QtCore.Qt.AlignCenter)
        layout.setSpacing(20)
        self.setLayout(layout)

        # Create a label to hold the image
        label = QtWidgets.QLabel()
        label.setText("Welcome to Remoter!")
        label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(label)

        # Create a label to hold the welcome message
        label = QtWidgets.QLabel()
        label.setText("Remoter is a remote control application that can control the computer remotely.")
        label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(label)

        # Create a label to show logo
        logo = QtWidgets.QLabel()
        logo.setPixmap(settings.getLogo(200))
        logo.setAlignment(QtCore.Qt.AlignCenter)
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
                       ["Settings", Scene_Settings(self.settings), self.to_settings], 
                       ["About", Scene_About(self.settings), self.to_about],
                       ["Test", Scene_Test(self.settings), self.to_test]]
        for i in range(len(self.scenes)):
            self.scenes[i][1].hide()
            self.scenes[i].append(QtWidgets.QPushButton(self.scenes[i][0]))
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

    def to_settings(self):
        self.change_scene(2)

    def to_about(self):
        self.change_scene(3)

    def to_test(self):
        self.change_scene(4)

class Entry(QtWidgets.QMainWindow):
    status_bar_resetter = QtCore.QTimer()
    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        self.status_service = service.StatusService(settings)
        self.design(settings)
        self.build()

        QtCore.QTimer.singleShot(2500, self.show)

    def design(self, settings):
        self.setWindowTitle("Remoter")
        self.resize(800, 600)
        self.setWindowIcon(settings.getLogoIcon())

        # Create a widget to hold the layout
        self.scene = Scene(settings)
        self.setCentralWidget(self.scene)

        # Create a label to hold the status
        self.status_bar = QtWidgets.QStatusBar()
        self.status_bar.showMessage("Ready")
        self.setStatusBar(self.status_bar)

    def build(self):
        self.scene.scenes[1][1].confirm_button.clicked.connect(self.ConnectStatus)
        self.scene.scenes[4][1].send_button.clicked.connect(self.sendTest)
        self.status_service.error_occurred.connect(self.showError)
        self.status_bar_resetter.timeout.connect(self.clearError)

    def ConnectStatus(self):
        self.settings.setStatusServer(self.scene.scenes[1][1].server_address.text(), self.scene.scenes[1][1].server_port.value())
        self.status_service.start()

    def showError(self, error):
        self.status_bar.showMessage(str(error))
        self.status_bar_resetter.start(2000)

    def clearError(self):
        self.status_bar.showMessage("Ready")

    def sendTest(self):
        self.settings.setTestJson(self.scene.scenes[4][1].line_edit.text())
        json = QtCore.QJsonDocument.fromJson(self.scene.scenes[4][1].line_edit.text().encode())
        self.status_service.send(json)
        self.status_bar.showMessage("Send: " + self.scene.scenes[4][1].line_edit.text())
        self.status_bar_resetter.start(10000)
