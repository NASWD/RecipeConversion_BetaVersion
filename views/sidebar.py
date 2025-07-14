from PyQt5.QtWidgets import QWidget,QVBoxLayout,QPushButton,QLabel
from PyQt5.QtGui import QIcon,QPixmap
from PyQt5.QtCore import QSize,Qt


class Sidebar(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedWidth(160)
        self.setStyleSheet("background-color: #1e1e1e; border-right: 1px solid #333;")
        layout=QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)
        self.setLayout(layout)

        self.home_btn=QPushButton("  Home")
        self.home_btn.setIcon(QIcon("views/icons/home.svg"))
        self.home_btn.setIconSize(QSize(20,20))
        self.home_btn.setObjectName("sidebarBtn")

        self.wafer_btn=QPushButton("  Wafer Map")
        self.wafer_btn.setIcon(QIcon("views/icons/wafer.svg"))
        self.wafer_btn.setIconSize(QSize(20,20))
        self.wafer_btn.setObjectName("sidebarBtn")

        layout.addWidget(self.home_btn)
        layout.addWidget(self.wafer_btn)
