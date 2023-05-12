from PySide6 import QtCore, QtWidgets, QtGui

from libs import logger
lg = logger.logger()

class Welcome(QtWidgets.QWidget):
    def __init__(self, cwd, parent = None):
        lg.log("Welcome.__init__")
        super().__init__(parent)

        self.scenes = []

        # Create a widget to hold the layout
        welcome = Welcome(cwd)
        self.scenes.append(welcome)
        self.setCentralWidget(welcome)

    def change_scene(self, scene : QtWidgets.QWidget):
        self.scenes.append(self.centralWidget())
        self.scenes[-1].hide()
        self.setCentralWidget(scene)
        scene.show()

    def back(self):
        self.centralWidget().hide()
        self.setCentralWidget(self.scenes[-1])
        self.centralWidget().show()
        self.scenes.pop()

class Scene_About(QtWidgets.QWidget):
    pass

class Scene_Settings(QtWidgets.QWidget):
    pass

class Scene_LocateServer(QtWidgets.QWidget):
    def __init__(self, settings):
        super().__init__()
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
        self.server_address.setAlignment(QtCore.Qt.AlignCenter)
        #self.server_address.setText(self.settings["server_address"])
        middle_layout.addWidget(self.server_address, 5)

        self.server_port = QtWidgets.QLineEdit()
        self.server_port.setPlaceholderText("Server port")
        self.server_port.setAlignment(QtCore.Qt.AlignCenter)
        #self.server_port.setText(self.settings["server_port"])
        middle_layout.addWidget(self.server_port, 1)

        # Create a button to connect to the server
        confirm_button = QtWidgets.QPushButton("Confirm")
        #confirm_button.clicked.connect(self.confirm)
        layout.addWidget(confirm_button)

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
                       ["Settings", Scene_Settings(), self.to_settings], 
                       ["About", Scene_About(), self.to_about]]
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

class Entry(QtWidgets.QMainWindow):
    def __init__(self, settings):
        super().__init__()
        self.setWindowTitle("Remoter")
        self.resize(800, 600)
        self.setWindowIcon(QtGui.QIcon(settings.getCWD() + "/images/remoter.png"))

        # Create a widget to hold the layout
        scene = Scene(settings)
        self.setCentralWidget(scene)

        # Create a label to hold the status
        status_bar = QtWidgets.QStatusBar()
        status_bar.showMessage("Ready")
        self.setStatusBar(status_bar)

        QtCore.QTimer.singleShot(2500, self.show)
