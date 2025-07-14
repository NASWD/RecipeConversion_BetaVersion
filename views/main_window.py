from PyQt5.QtWidgets import QMainWindow,QWidget,QHBoxLayout,QStackedWidget
from .sidebar import Sidebar
from views.home_tab import HomeTab
from views.wafer_map_tab import WaferMapTab


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Recipe Converter")
        self.setGeometry(100,100,1200,680)
        self.setStyleSheet(open("views/dark_theme.qss").read())

        central_widget=QWidget()
        layout=QHBoxLayout()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.stack=QStackedWidget()
        self.home_tab=HomeTab()
        self.wafer_tab=WaferMapTab()
        self.stack.addWidget(self.home_tab)
        self.stack.addWidget(self.wafer_tab)

        self.sidebar=Sidebar()
        self.sidebar.home_btn.clicked.connect(lambda:self.stack.setCurrentIndex(0))
        self.sidebar.wafer_btn.clicked.connect(lambda:self.stack.setCurrentIndex(1))

        layout.addWidget(self.sidebar)
        layout.addWidget(self.stack)
