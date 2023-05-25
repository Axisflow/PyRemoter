from PySide6.QtCore import QEvent, Qt, Signal
from PySide6.QtGui import QResizeEvent
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QGridLayout, QWidget, QStatusBar, QSizePolicy

class TestScreen(QMainWindow):
    __max_split_length__ = 120
    splitted_screen = []
    now_resolution = (0, 0)
    def __init__(self):
        super().__init__()
        self.resize(800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.status_bar = QStatusBar()
        self.status_bar.showMessage("Ready")
        self.setStatusBar(self.status_bar)

        # Create a frame as a screen
        self.combined_screen = QWidget(self.central_widget)
        self.combined_screen.setMouseTracking(True)
        self.combined_screen.mouseMoveEvent = self.mouseMoveTest
        # self.combined_screen.eventFilter = self.screenEventFilter
        self.combined_screen.setStyleSheet("background-color: black;")

        self.changeResolution((1900, 1000))

    mouseMoved = Signal(int, int)
    mouseAction = Signal(QEvent.Type)

    def mouseMoveTest(self, event):
        self.status_bar.showMessage(f"Mouse Moved: {event.position().x()}, {event.position().y()}")

    def screenEventFilter(self, obj, event) -> bool:
        if event.type() == QEvent.Type.MouseMove:
            self.mouseMoved.emit(event.x(), event.y())
            self.status_bar.showMessage(f"Mouse Moved: {event.x()}, {event.y()}")
        else:
            self.mouseAction.emit(event.type())
        return True

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
                label.setStyleSheet("border: 1px solid white;")
                label.setMouseTracking(True)
                self.grid_layout.addWidget(label, i, j)
                self.splitted_screen.append(label)
            self.grid_layout.setRowStretch(i, self.__max_split_length__)
        for j in range(num_width):
            self.grid_layout.setColumnStretch(j, self.__max_split_length__)

        if left_width != 0:
            for i in range(num_height):
                label = QLabel()
                label.setStyleSheet("border: 1px solid white;")
                label.setMouseTracking(True)
                self.grid_layout.addWidget(label, i, num_width)
                self.splitted_screen.append(label)
            self.grid_layout.setColumnStretch(num_width, left_width)

        if left_height != 0:
            for j in range(num_width):
                label = QLabel()
                label.setStyleSheet("border: 1px solid white;")
                label.setMouseTracking(True)
                self.grid_layout.addWidget(label, num_height, j)
                self.splitted_screen.append(label)
            self.grid_layout.setRowStretch(num_height, left_height)

        if left_width != 0 and left_height != 0:
            label = QLabel()
            label.setStyleSheet("border: 1px solid white;")
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


if __name__ == "__main__":
    app = QApplication([])
    widget = TestScreen()
    widget.show()
    app.exec()