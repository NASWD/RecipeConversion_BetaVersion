from PyQt5.QtCore import QTimer,Qt
from PyQt5.QtWidgets import QWidget,QLabel
from PyQt5.QtCore import QTimer


class Toast(QWidget):
    def __init__(self,message,parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint|Qt.WindowStaysOnTopHint)

        self.setStyleSheet("""
            QWidget {
                background-color: #333;
                color: white;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 12px;
            }
        """)
        label=QLabel(message,self)
        label.setAlignment(Qt.AlignCenter)
        self.resize(label.sizeHint().width()+32,label.sizeHint().height()+16)

    def show_(self,x,y):
        self.move(x-self.width()-16,y-self.height()-16)
        self.show()
        QTimer.singleShot(2500,self.close)
