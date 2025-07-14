from PyQt5.QtWidgets import (
    QWidget,QVBoxLayout,QHBoxLayout,QLabel,QLineEdit,QPushButton,
    QCheckBox,QFrame,QTableWidget,QTableWidgetItem,QFileDialog,
    QToolButton,QSizePolicy,QHeaderView,QMessageBox
)
from PyQt5.QtCore import Qt
import pandas as pd
import os
from .toast_widget import Toast
from .generate_fmw import build_clean_fmw
from wafermap_data import _wafer_map_payload
from excel_dual_parser import parse_dual_excel


class HomeTab(QWidget):
    def __init__(self):
        super().__init__()
        self.file_paths=[]
        self.last_dir=os.getcwd()

        self.table=QTableWidget()
        self.table.setEditTriggers(QTableWidget.DoubleClicked)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(False)
        self.table.setFixedHeight(220)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setHighlightSections(False)
        self.table.setShowGrid(True)
        header=self.table.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(QHeaderView.Fixed)
        header.setDefaultSectionSize(130)

        # 🌑 Apply custom dark stylesheet for pixel-perfect look
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #1e1e1e;
                color: #f0f0f0;
                gridline-color: #2c2c2c;
                font-size: 11px;
                selection-background-color: #4f90ff;
                selection-color: #000000;
                border: none;
            }
            QHeaderView::section {
                background-color: #2c2c2c;
                color: #f0f0f0;
                padding: 4px;
                font-weight: bold;
                border: 1px solid #3a3a3a;
            }
            QScrollBar:vertical {
                background: #1e1e1e;
                width: 12px;
                margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:vertical {
                background: #4f90ff;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                background: none;
                height: 0px;
            }
            QTableWidget::item:hover {
                background-color: #2a2a2a;
            }
        """)

        self.load_button=QPushButton("Load Files")
        self.export_button=QPushButton("Export")
        self.save_button=QPushButton("Save")
        self.load_button.clicked.connect(self.open_file_dialog)
        self.export_button.clicked.connect(self.export_fmw)
        self.save_button.clicked.connect(self.save_excel)
        self.export_button.setEnabled(False)
        self.save_button.setEnabled(False)

        self.ref_x_input=QLineEdit("0")
        self.ref_y_input=QLineEdit("0")
        self.theta_input=QLineEdit("0")
        self.include_height_sense=QCheckBox("Include Height Sense Location")

        # UI Layout (modern)
        main_layout=QVBoxLayout()
        card=QFrame()
        card.setObjectName("card")
        card_layout=QVBoxLayout()
        card.setLayout(card_layout)

        title=QLabel("Recipe Converter")
        title.setObjectName("pageTitle")
        card_layout.addWidget(title)

        self.file_list_layout=QVBoxLayout()
        card_layout.addLayout(self.file_list_layout)

        card_layout.addWidget(self.table)

        form_layout=QHBoxLayout()
        form_layout.addWidget(QLabel("Ref X:"))
        form_layout.addWidget(self.ref_x_input)
        form_layout.addWidget(QLabel("Ref Y:"))
        form_layout.addWidget(self.ref_y_input)
        form_layout.addWidget(QLabel("Theta:"))
        form_layout.addWidget(self.theta_input)
        form_layout.addStretch()
        form_layout.addWidget(self.include_height_sense)
        card_layout.addLayout(form_layout)

        button_layout=QHBoxLayout()
        button_layout.addWidget(self.save_button)
        button_layout.addStretch()
        button_layout.addWidget(self.load_button)
        button_layout.addWidget(self.export_button)
        button_layout.addStretch()
        card_layout.addLayout(button_layout)

        main_layout.addWidget(card)
        self.setLayout(main_layout)

    def open_file_dialog(self):
        files,_=QFileDialog.getOpenFileNames(
            self,"Select Recipe Input Files",self.last_dir,
            "All Files ();;Excel (.xlsx);;Text (.txt);;Config (.ini)"
        )
        if files:
            self.last_dir=os.path.dirname(files[0])
            self.file_paths=list(set(self.file_paths+files))
            self.export_button.setEnabled(True)
            self.save_button.setEnabled(True)
            self.refresh_file_list()
            excel_file=next((f for f in self.file_paths if f.endswith(".xlsx")),None)
            if excel_file:
                self.display_excel(excel_file)

    def refresh_file_list(self):
        while self.file_list_layout.count():
            child=self.file_list_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        for fpath in self.file_paths:
            fname=os.path.basename(fpath)
            file_row=QFrame()
            file_row.setStyleSheet("background-color: #2c2c2c; border-radius: 6px;")
            file_row.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Fixed)
            row_layout=QHBoxLayout(file_row)
            row_layout.setContentsMargins(8,4,8,4)
            icon=QLabel("📄")
            icon.setStyleSheet("font-size: 12px; color: #aaa;")
            label=QLabel(fname)
            label.setFixedWidth(220)
            label.setToolTip(fpath)
            label.setTextInteractionFlags(Qt.TextSelectableByMouse)
            label.setStyleSheet("color: white; font-size: 11px;")
            remove_btn=QToolButton()
            remove_btn.setText("❌")
            remove_btn.setStyleSheet("font-size: 10px; color: red; padding: 0 6px;")
            remove_btn.clicked.connect(lambda _,path=fpath:self.remove_file(path))
            row_layout.addWidget(icon)
            row_layout.addWidget(label)
            row_layout.addStretch()
            row_layout.addWidget(remove_btn)
            self.file_list_layout.addWidget(file_row)

    def remove_file(self,path):
        self.file_paths.remove(path)
        self.refresh_file_list()
        self.export_button.setEnabled(bool(self.file_paths))
        self.save_button.setEnabled(bool(self.file_paths))
        if path.endswith(".xlsx"):
            self.table.clearContents()
            self.table.setRowCount(0)

    def display_excel(self,file_path):
        try:
            df=pd.read_excel(file_path)
            self.table.setRowCount(len(df))
            self.table.setColumnCount(len(df.columns))
            self.table.setHorizontalHeaderLabels(df.columns)
            for i in range(len(df)):
                for j in range(len(df.columns)):
                    val=str(df.iloc[i,j])
                    item=QTableWidgetItem(val)
                    item.setFlags(item.flags()|Qt.ItemIsEditable)
                    self.table.setItem(i,j,item)
        except Exception as e:
            print(f"Error loading Excel: {e}")

    def save_excel(self):
        excel_path=next((f for f in self.file_paths if f.endswith(".xlsx")),None)
        if not excel_path:
            print("❌ No Excel file to save.")
            return
        row_count=self.table.rowCount()
        col_count=self.table.columnCount()
        headers=[self.table.horizontalHeaderItem(i).text() for i in range(col_count)]
        data=[]
        for row in range(row_count):
            row_data=[]
            for col in range(col_count):
                item=self.table.item(row,col)
                row_data.append(item.text() if item else "")
            data.append(row_data)
        df=pd.DataFrame(data,columns=headers)
        df.to_excel(excel_path,index=False)
        print(f"✅ Saved to {excel_path}")

    def export_fmw(self):
        try:
            if not _wafer_map_payload:
                reply=QMessageBox.question(
                    self,
                    "Wafer Map Not Found",
                    "No wafer map has been submitted from the Wafer Map tab. Do you want to continue without it?",
                    QMessageBox.Yes|QMessageBox.No
                )
                if reply==QMessageBox.No:
                    return
                wafer_map_path=None
            else:
                wafer_map_path=_wafer_map_payload.get("path")
            coord_file=next((f for f in self.file_paths if "coord" in os.path.basename(f).lower()),None)
            meta_file=next((f for f in self.file_paths if "meta" in os.path.basename(f).lower()),None)
            if not coord_file or not meta_file:
                print("❌ Coordinate and Metadata Excel files not found.")
                return
            parsed=parse_dual_excel(coord_file,meta_file)
            filenames={"fluid1":"","fluid2":"","heater1":"","heater2":"","heater3":"","heater4":""}
            fluid_count=0
            heater_count=0
            for path in self.file_paths:
                fname=os.path.basename(path)
                if fname.lower().endswith(".flu"):
                    if fluid_count==0:
                        filenames["fluid1"]=fname
                        fluid_count+=1
                    elif fluid_count==1:
                        filenames["fluid2"]=fname
                        fluid_count+=1
                elif fname.lower().endswith(".htc"):
                    if heater_count==0:
                        filenames["heater1"]=fname
                        heater_count+=1
                    elif heater_count==1:
                        filenames["heater2"]=fname
                        heater_count+=1
                    elif heater_count==2:
                        filenames["heater3"]=fname
                        heater_count+=1
                    elif heater_count==3:
                        filenames["heater4"]=fname
                        heater_count+=1
            output_path,total_lines=build_clean_fmw(
                self.file_paths,
                parsed["excel_data"],
                origin=parsed["origin"],
                fiducials=parsed["fiducials"],
                scale=parsed["scale"],
                substrate_height=parsed["substrate_height"],
                filenames=filenames,
                user_step_repeat=parsed.get("step_params"),
                wafer_map_path=wafer_map_path
            )
            import shutil
            uploaded_avw_path=next(
                (f for f in self.file_paths if f.lower().endswith(".avw")),
                None
            )
            if uploaded_avw_path:
                avw_output_path=os.path.splitext(output_path)[0]+".avw"
                shutil.copyfile(uploaded_avw_path,avw_output_path)
                print(f"✅ .avw copied to: {avw_output_path}")
            else:
                print("⚠ No .avw file was uploaded.")
            print(f"✅ .fmw generated at: {output_path} ({total_lines} lines)")
            toast=Toast("✅ .fmw program exported successfully!",self)
            toast.show_(self.mapToGlobal(self.rect().bottomRight()).x(),
                        self.mapToGlobal(self.rect().bottomRight()).y())
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"❌ Export failed: {e}")
