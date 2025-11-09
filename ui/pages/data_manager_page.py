import sqlite3
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QLineEdit, QMessageBox, QDialog,
    QGridLayout, QDialogButtonBox, QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

DB_PATH = "ui/db/senarath.db"


class VehicleDialog(QDialog):
    def __init__(self, parent=None, edit_data=None):
        super().__init__(parent)
        self.setWindowTitle("Add/Edit Vehicle")
        self.setMinimumWidth(500)
        
        layout = QVBoxLayout()
        form_layout = QGridLayout()
        
        self.company_no_input = QLineEdit()
        self.company_no_input.setPlaceholderText("e.g., CP-001")
        
        self.number_input = QLineEdit()
        self.number_input.setPlaceholderText("e.g., KA-1234")
        
        self.make_input = QLineEdit()
        self.make_input.setPlaceholderText("e.g., Toyota")
        
        self.model_input = QLineEdit()
        self.model_input.setPlaceholderText("e.g., Hilux")
        
        self.type_input = QLineEdit()
        self.type_input.setPlaceholderText("e.g., Double Cab")
        
        form_layout.addWidget(QLabel("Company No:"), 0, 0)
        form_layout.addWidget(self.company_no_input, 0, 1)
        
        form_layout.addWidget(QLabel("Vehicle No:"), 1, 0)
        form_layout.addWidget(self.number_input, 1, 1)
        
        form_layout.addWidget(QLabel("Make:"), 2, 0)
        form_layout.addWidget(self.make_input, 2, 1)
        
        form_layout.addWidget(QLabel("Model:"), 3, 0)
        form_layout.addWidget(self.model_input, 3, 1)
        
        form_layout.addWidget(QLabel("Type:"), 4, 0)
        form_layout.addWidget(self.type_input, 4, 1)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
        
        # If editing, populate fields
        if edit_data:
            self.company_no_input.setText(edit_data.get('company_no', ''))
            self.number_input.setText(edit_data.get('number', ''))
            self.make_input.setText(edit_data.get('make', ''))
            self.model_input.setText(edit_data.get('model', ''))
            self.type_input.setText(edit_data.get('type', ''))
    
    def get_data(self):
        return {
            'company_no': self.company_no_input.text().strip(),
            'number': self.number_input.text().strip(),
            'make': self.make_input.text().strip(),
            'model': self.model_input.text().strip(),
            'type': self.type_input.text().strip()
        }


class DataManagerPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.current_table = "vehicles"
        self.current_edit_id = None

        # === UI Colors (No Blue) ===
        bg_color = "#f5f5f0"
        card_color = "#ffffff"
        accent_color = "#2d7a5f"
        text_color = "#2c2c2c"
        border_color = "#d4d4d4"
        danger_color = "#c84343"
        secondary_color = "#8b6f47"

        self.setStyleSheet(f"""
            QWidget {{
                background-color: {bg_color};
                color: {text_color};
                font-family: 'Segoe UI', Arial;
                font-size: 13px;
            }}
            QLabel#title {{
                font-size: 22px;
                font-weight: bold;
                color: #1a1a1a;
            }}
            QFrame#card {{
                background-color: {card_color};
                border-radius: 10px;
                padding: 20px;
                border: 1px solid {border_color};
            }}
            QPushButton {{
                background-color: {accent_color};
                color: white;
                font-weight: 600;
                padding: 10px 18px;
                border-radius: 7px;
                min-height: 36px;
            }}
            QPushButton:hover {{
                background-color: #246651;
            }}
            QPushButton#tab {{
                background-color: #e8e8e8;
                color: #333;
                padding: 10px 20px;
            }}
            QPushButton#tab:hover {{
                background-color: #d5d5d5;
            }}
            QPushButton#tab_active {{
                background-color: {accent_color};
                color: white;
            }}
            QPushButton#secondary {{
                background-color: {secondary_color};
            }}
            QPushButton#secondary:hover {{
                background-color: #735a38;
            }}
            QPushButton#danger {{
                background-color: {danger_color};
            }}
            QPushButton#danger:hover {{
                background-color: #b03636;
            }}
            QPushButton#ghost {{
                background-color: transparent;
                color: #444;
                border: 1px solid #ccc;
            }}
            QPushButton#ghost:hover {{
                background-color: #f0f0f0;
            }}
            QLineEdit {{
                padding: 8px 12px;
                border-radius: 6px;
                background: #fafafa;
                border: 1px solid {border_color};
                color: {text_color};
                min-height: 32px;
            }}
            QLineEdit:focus {{
                border: 1px solid {accent_color};
                background-color: #ffffff;
            }}
            QTableWidget {{
                background-color: {card_color};
                border: 1px solid {border_color};
                color: {text_color};
                gridline-color: {border_color};
                border-radius: 8px;
            }}
            QHeaderView::section {{
                background-color: {accent_color};
                color: white;
                font-weight: 600;
                padding: 10px;
                border: none;
            }}
            QTableWidget::item {{
                padding: 8px;
            }}
            QTableWidget::item:selected {{
                background-color: #c8e6c9;
                color: #1a1a1a;
            }}
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(30, 25, 30, 25)
        layout.setSpacing(20)

        # Title
        title = QLabel("🔧 Data Manager")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # === Tab Navigation ===
        tab_card = QFrame()
        tab_card.setObjectName("card")
        tab_layout = QHBoxLayout(tab_card)
        
        self.vehicle_btn = QPushButton("🚗 Vehicles")
        self.driver_btn = QPushButton("👤 Drivers")
        self.site_btn = QPushButton("📍 Sites")
        self.section_btn = QPushButton("🏗 Sections")

        self.tab_buttons = [self.vehicle_btn, self.driver_btn, self.site_btn, self.section_btn]
        
        for btn in self.tab_buttons:
            btn.setObjectName("tab")
            btn.setMinimumHeight(45)
            tab_layout.addWidget(btn)
        
        layout.addWidget(tab_card)

        # === Data Card ===
        data_card = QFrame()
        data_card.setObjectName("card")
        data_layout = QVBoxLayout(data_card)
        
        self.table_title = QLabel("Vehicles")
        self.table_title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        self.table_title.setStyleSheet("color: #2d7a5f; padding-bottom: 10px;")
        data_layout.addWidget(self.table_title)
        
        # Table
        self.table = QTableWidget()
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        data_layout.addWidget(self.table)
        
        layout.addWidget(data_card)

        # === Action Buttons ===
        action_card = QFrame()
        action_card.setObjectName("card")
        action_layout = QHBoxLayout(action_card)
        
        # Simple input for drivers, sites, sections
        self.simple_input = QLineEdit()
        self.simple_input.setPlaceholderText("Enter name...")
        self.simple_input.setVisible(False)
        action_layout.addWidget(self.simple_input, 2)
        
        self.add_btn = QPushButton("➕ Add New")
        self.edit_btn = QPushButton("✏ Edit Selected")
        self.edit_btn.setObjectName("secondary")
        self.delete_btn = QPushButton("🗑 Delete Selected")
        self.delete_btn.setObjectName("danger")
        
        action_layout.addWidget(self.add_btn)
        action_layout.addWidget(self.edit_btn)
        action_layout.addWidget(self.delete_btn)
        action_layout.addStretch()
        
        layout.addWidget(action_card)

        # Back button
        back_btn = QPushButton("⬅ Back to Home")
        back_btn.setObjectName("ghost")
        back_btn.clicked.connect(self.go_back)
        layout.addWidget(back_btn)

        self.setLayout(layout)

        # Connect buttons
        self.vehicle_btn.clicked.connect(lambda: self.switch_table("vehicles"))
        self.driver_btn.clicked.connect(lambda: self.switch_table("drivers"))
        self.site_btn.clicked.connect(lambda: self.switch_table("sites"))
        self.section_btn.clicked.connect(lambda: self.switch_table("sections"))
        
        self.add_btn.clicked.connect(self.add_record)
        self.edit_btn.clicked.connect(self.edit_record)
        self.delete_btn.clicked.connect(self.delete_record)

        self.refresh_all()

    def go_back(self):
        self.main_window.go_to_home()

    def switch_table(self, table_name):
        self.current_table = table_name
        self.current_edit_id = None
        
        # Update tab button styles
        for btn in self.tab_buttons:
            btn.setObjectName("tab")
            btn.setStyle(btn.style())  # Force refresh
        
        if table_name == "vehicles":
            self.vehicle_btn.setObjectName("tab_active")
            self.table_title.setText("🚗 Vehicles")
            self.simple_input.setVisible(False)
        elif table_name == "drivers":
            self.driver_btn.setObjectName("tab_active")
            self.table_title.setText("👤 Drivers")
            self.simple_input.setVisible(True)
            self.simple_input.setPlaceholderText("Enter driver name...")
        elif table_name == "sites":
            self.site_btn.setObjectName("tab_active")
            self.table_title.setText("📍 Sites")
            self.simple_input.setVisible(True)
            self.simple_input.setPlaceholderText("Enter site name...")
        elif table_name == "sections":
            self.section_btn.setObjectName("tab_active")
            self.table_title.setText("🏗 Sections")
            self.simple_input.setVisible(True)
            self.simple_input.setPlaceholderText("Enter section name...")
        
        # Force style refresh
        for btn in self.tab_buttons:
            btn.setStyle(btn.style())
        
        self.refresh_all()

    def refresh_all(self):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        if self.current_table == "vehicles":
            c.execute("SELECT id, company_no, number, make, model, type FROM vehicles ORDER BY id DESC")
            data = c.fetchall()
            headers = ["ID", "Company No", "Vehicle No", "Make", "Model", "Type"]
        elif self.current_table == "drivers":
            c.execute("SELECT id, name FROM drivers ORDER BY name")
            data = c.fetchall()
            headers = ["ID", "Name"]
        elif self.current_table == "sites":
            c.execute("SELECT id, name FROM sites ORDER BY name")
            data = c.fetchall()
            headers = ["ID", "Site Name"]
        elif self.current_table == "sections":
            c.execute("SELECT id, name FROM sections ORDER BY name")
            data = c.fetchall()
            headers = ["ID", "Section Name"]
        else:
            data, headers = [], []

        conn.close()

        # Update table
        self.table.clear()
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setColumnHidden(0, True)  # Hide ID column
        self.table.setRowCount(len(data))

        for row_index, row_data in enumerate(data):
            for col_index, col_value in enumerate(row_data):
                item = QTableWidgetItem(str(col_value) if col_value else "")
                item.setFlags(item.flags() ^ Qt.ItemIsEditable)
                self.table.setItem(row_index, col_index, item)

        self.table.resizeColumnsToContents()
        self.simple_input.clear()
        self.current_edit_id = None

    def on_selection_changed(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if selected_rows and self.current_table != "vehicles":
            row = selected_rows[0].row()
            self.current_edit_id = int(self.table.item(row, 0).text())
            name = self.table.item(row, 1).text()
            self.simple_input.setText(name)

    def add_record(self):
        if self.current_table == "vehicles":
            dialog = VehicleDialog(self)
            if dialog.exec():
                data = dialog.get_data()
                if not data['company_no']:
                    QMessageBox.warning(self, "Warning", "Company No is required!")
                    return
                
                conn = sqlite3.connect(DB_PATH)
                c = conn.cursor()
                c.execute("""INSERT INTO vehicles (company_no, number, make, model, type) 
                             VALUES (?, ?, ?, ?, ?)""",
                         (data['company_no'], data['number'], data['make'], data['model'], data['type']))
                conn.commit()
                conn.close()
                
                QMessageBox.information(self, "Success", "Vehicle added successfully!")
                self.refresh_all()
        else:
            text = self.simple_input.text().strip()
            if not text:
                QMessageBox.warning(self, "Warning", "Input field cannot be empty!")
                return

            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()

            if self.current_table == "drivers":
                c.execute("INSERT INTO drivers (name) VALUES (?)", (text,))
            elif self.current_table == "sites":
                c.execute("INSERT INTO sites (name) VALUES (?)", (text,))
            elif self.current_table == "sections":
                c.execute("INSERT INTO sections (name) VALUES (?)", (text,))

            conn.commit()
            conn.close()
            
            QMessageBox.information(self, "Success", "Record added successfully!")
            self.refresh_all()

    def edit_record(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Warning", "Please select a record to edit!")
            return
        
        row = selected_rows[0].row()
        record_id = int(self.table.item(row, 0).text())
        
        if self.current_table == "vehicles":
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("SELECT company_no, number, make, model, type FROM vehicles WHERE id=?", (record_id,))
            vehicle_data = c.fetchone()
            conn.close()
            
            if vehicle_data:
                edit_data = {
                    'company_no': vehicle_data[0],
                    'number': vehicle_data[1],
                    'make': vehicle_data[2],
                    'model': vehicle_data[3],
                    'type': vehicle_data[4]
                }
                
                dialog = VehicleDialog(self, edit_data=edit_data)
                if dialog.exec():
                    data = dialog.get_data()
                    if not data['company_no']:
                        QMessageBox.warning(self, "Warning", "Company No is required!")
                        return
                    
                    conn = sqlite3.connect(DB_PATH)
                    c = conn.cursor()
                    c.execute("""UPDATE vehicles SET company_no=?, number=?, make=?, model=?, type=? 
                                 WHERE id=?""",
                             (data['company_no'], data['number'], data['make'], data['model'], 
                              data['type'], record_id))
                    conn.commit()
                    conn.close()
                    
                    QMessageBox.information(self, "Success", "Vehicle updated successfully!")
                    self.refresh_all()
        else:
            text = self.simple_input.text().strip()
            if not text:
                QMessageBox.warning(self, "Warning", "Input field cannot be empty!")
                return
            
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute(f"UPDATE {self.current_table} SET name=? WHERE id=?", (text, record_id))
            conn.commit()
            conn.close()
            
            QMessageBox.information(self, "Success", "Record updated successfully!")
            self.refresh_all()

    def delete_record(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Warning", "Please select at least one record to delete!")
            return

        confirm = QMessageBox.question(self, "Confirm Delete", 
                                      f"Are you sure you want to delete {len(selected_rows)} record(s)?",
                                      QMessageBox.Yes | QMessageBox.No)
        if confirm != QMessageBox.Yes:
            return

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        for row in selected_rows:
            record_id = int(self.table.item(row.row(), 0).text())
            c.execute(f"DELETE FROM {self.current_table} WHERE id=?", (record_id,))
        
        conn.commit()
        conn.close()
        
        QMessageBox.information(self, "Deleted", "Record(s) deleted successfully!")
        self.refresh_all()