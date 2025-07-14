from cmath import sqrt

from PyQt5.QtWidgets import (
    QWidget,QVBoxLayout,QHBoxLayout,QLabel,
    QLineEdit,QPushButton,QFileDialog,QFrame,
    QGraphicsView,QGraphicsScene,QGraphicsEllipseItem,QGraphicsRectItem,QGraphicsTextItem
)
from PyQt5.QtGui import QBrush,QColor,QPainter,QFont,QPen
from PyQt5.QtCore import Qt

from wafermap_data import _wafer_map_payload


class WaferMapTab(QWidget):
    def __init__(self):
        super().__init__()

        self.diameter_input=QLineEdit()
        self.grid_x_input=QLineEdit()
        self.grid_y_input=QLineEdit()

        self.upload_btn=QPushButton("Upload Wafer Map (.txt)")
        self.upload_btn.clicked.connect(self.upload_wafer_map)

        self.draw_btn=QPushButton("Draw Wafer")
        self.draw_btn.clicked.connect(self.update_canvas)

        self.scene=QGraphicsScene()
        self.canvas=QGraphicsView(self.scene)
        self.canvas.setRenderHint(QPainter.Antialiasing,True)
        self.canvas.setMinimumHeight(400)

        # UI layout
        form_layout=QHBoxLayout()
        form_layout.addWidget(QLabel("Wafer Diameter (mm)"))
        form_layout.addWidget(self.diameter_input)
        form_layout.addWidget(QLabel("Grid X Size (mm)"))
        form_layout.addWidget(self.grid_x_input)
        form_layout.addWidget(QLabel("Grid Y Size (mm)"))
        form_layout.addWidget(self.grid_y_input)

        button_layout=QHBoxLayout()
        button_layout.addWidget(self.upload_btn)
        button_layout.addWidget(self.draw_btn)

        card=QFrame()
        card.setObjectName("card")
        card_layout=QVBoxLayout(card)
        title=QLabel("Wafer Map Generator")
        title.setObjectName("pageTitle")

        card_layout.addWidget(title)
        card_layout.addLayout(form_layout)
        card_layout.addLayout(button_layout)
        card_layout.addWidget(self.canvas)

        layout=QVBoxLayout()
        layout.addWidget(card)
        self.setLayout(layout)

    def upload_wafer_map(self):
        filepath,_=QFileDialog.getOpenFileName(self,"Select Wafer Map File","","Text Files (*.txt)")
        if filepath:
            _wafer_map_payload["path"]=filepath

    def update_canvas(self):
        self.scene.clear()
        try:
            gx=float(self.grid_x_input.text())  # e.g. 10
            gy=float(self.grid_y_input.text())  # e.g. 10
            diameter=float(self.diameter_input.text())  # e.g. 150

            cols=int(diameter // gx)
            rows=int(diameter // gy)

            # Load wafer map data
            map_path=_wafer_map_payload.get("path","")
            if not map_path:
                raise ValueError("No wafer map file uploaded.")

            with open(map_path,"r") as f:
                content=f.read()

            # Parse enabled dies
            enabled_dies=set()
            entries=content.strip().split(";")

            offset_row=rows // 2
            offset_col=cols // 2
            for entry in entries:
                if entry:
                    parts=entry.split(",")
                    if len(parts)==4:

                        row=int(parts[1])+offset_row
                        col=int(parts[2])+offset_col
                        enabled_dies.add((col,row))

            # Grid origin
            origin_x =- (cols * gx) / 2
            origin_y =- (rows * gy) / 2

            font=QFont("Sans Serif",4)

            for i in range(cols):
                for j in range(rows):
                    x=(i-cols // 2) * gx
                    y=-(j-rows // 2) * gy  # or just remove - if flipped

                    if (i,j) in enabled_dies:
                        color=QColor("#00cc88")
                    else:
                        color=QColor("#cccccc")

                    die=QGraphicsRectItem(x,y,gx-0.5,gy-0.5)
                    die.setBrush(QBrush(color))
                    die.setPen(QPen(Qt.NoPen))
                    self.scene.addItem(die)

                    if (i,j) in enabled_dies:
                        label=QGraphicsTextItem(f"{i},{j}")
                        label.setFont(font)
                        label.setDefaultTextColor(Qt.black)
                        label.setPos(x+2,y+2)
                        self.scene.addItem(label)

            self.canvas.fitInView(self.scene.itemsBoundingRect(),Qt.KeepAspectRatio)

        except Exception as e:
            self.scene.clear()
            error=QGraphicsTextItem(f"❌ Error: {str(e)}")
            error.setDefaultTextColor(Qt.red)
            error.setFont(QFont("Sans Serif",10))
            self.scene.addItem(error)