import sqlite3
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QLineEdit, QMessageBox, QDialog,
    QGridLayout, QDialogButtonBox, QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from ui.theme import ColorPalette, Typography, Spacing, Styles, create_page_header

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
            QLabel {{
                background-color: transparent;
            }}
            QLabel#title {{
                font-size: 26px;
                font-weight: 700;
                color: #1a1a1a;
            }}
            QLabel#section_title {{
                font-size: 14px;
                font-weight: 600;
                color: #555;
            }}
            QFrame#card {{
                background-color: {card_color};
                border-radius: 8px;
                padding: 16px;
                border: none;
            }}
            QPushButton {{
                background-color: {accent_color};
                color: white;
                font-weight: 700;
                padding: 10px 18px;
                border-radius: 6px;
                min-height: 36px;
                font-size: 13px;
                border: none;
            }}
            QPushButton:hover {{
                background-color: #246651;
            }}
            QPushButton:pressed {{
                background-color: #1f5443;
            }}
            QPushButton#tab {{
                background-color: #f0f0f0;
                color: #666;
                padding: 11px 18px;
                font-weight: 600;
                min-height: 38px;
                font-size: 13px;
                border-radius: 6px;
            }}
            QPushButton#tab:hover {{
                background-color: #e5e5e5;
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
                color: #333;
                border: 1px solid #ccc;
                font-weight: 600;
                font-size: 13px;
                text-transform: none;
                letter-spacing: 0px;
            }}
            QPushButton#ghost:hover {{
                background-color: #f5f5f5;
                border-color: #999;
            }}
            QLineEdit {{
                padding: 9px 12px;
                border-radius: 6px;
                background: #fafafa;
                border: 1px solid {border_color};
                color: {text_color};
                min-height: 34px;
                font-size: 13px;
                font-weight: 500;
            }}
            QLineEdit:focus {{
                border: 2px solid {accent_color};
                background-color: #ffffff;
            }}
            QTableWidget {{
                background-color: {card_color};
                border: 1px solid {border_color};
                color: {text_color};
                gridline-color: #f0f0f0;
                border-radius: 6px;
                font-size: 13px;
            }}
            QHeaderView::section {{
                background-color: {accent_color};
                color: white;
                font-weight: 700;
                padding: 10px 8px;
                border: none;
                font-size: 12px;
                text-transform: uppercase;
                letter-spacing: 0.3px;
            }}
            QTableWidget::item {{
                padding: 10px 8px;
                border: none;
                color: {text_color};
            }}
            QTableWidget::item:selected {{
                background-color: #e8f4f0;
                color: {text_color};
            }}
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(30, 24, 30, 24)
        layout.setSpacing(16)

        # === Header with Title and Back Button ===
        header_layout, title_label, back_btn = create_page_header("🔧 Data Manager")
        back_btn.clicked.connect(self.go_back)
        layout.addLayout(header_layout)

        # === Tab Navigation ===
        tab_layout = QHBoxLayout()
        tab_layout.setSpacing(10)
        
        self.vehicle_btn = QPushButton("🚗 Vehicles")
        self.driver_btn = QPushButton("👤 Drivers")
        self.site_btn = QPushButton("📍 Sites")
        self.section_btn = QPushButton("🏗 Sections")

        self.tab_buttons = [self.vehicle_btn, self.driver_btn, self.site_btn, self.section_btn]
        
        for btn in self.tab_buttons:
            btn.setObjectName("tab")
            btn.setFixedHeight(38)
            btn.setMinimumWidth(120)
            tab_layout.addWidget(btn)
        
        tab_layout.addStretch()
        layout.addLayout(tab_layout)

        # === Data Table Card ===
        data_card = QFrame()
        data_card.setObjectName("card")
        data_layout = QVBoxLayout(data_card)
        data_layout.setContentsMargins(0, 0, 0, 0)
        data_layout.setSpacing(0)
        
        # Table
        self.table = QTableWidget()
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setAlternatingRowColors(False)
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        data_layout.addWidget(self.table)
        
        layout.addWidget(data_card, 1)

        # === Action Buttons ===
        action_layout = QHBoxLayout()
        action_layout.setSpacing(10)
        
        # Simple input for drivers, sites, sections
        self.simple_input = QLineEdit()
        self.simple_input.setPlaceholderText("Enter name...")
        self.simple_input.setVisible(False)
        self.simple_input.setMaximumWidth(250)
        action_layout.addWidget(self.simple_input)
        
        self.add_btn = QPushButton("➕ Add New")
        self.add_btn.setFixedHeight(36)
        self.add_btn.setMinimumWidth(110)
        
        self.edit_btn = QPushButton("✏ Edit")
        self.edit_btn.setObjectName("secondary")
        self.edit_btn.setFixedHeight(36)
        self.edit_btn.setMinimumWidth(90)
        
        self.delete_btn = QPushButton("🗑 Delete")
        self.delete_btn.setObjectName("danger")
        self.delete_btn.setFixedHeight(36)
        self.delete_btn.setMinimumWidth(90)
        
        action_layout.addWidget(self.add_btn)
        action_layout.addWidget(self.edit_btn)
        action_layout.addWidget(self.delete_btn)
        action_layout.addStretch()
        
        layout.addLayout(action_layout)

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
            self.simple_input.setVisible(False)
        elif table_name == "drivers":
            self.driver_btn.setObjectName("tab_active")
            self.simple_input.setVisible(True)
            self.simple_input.setPlaceholderText("Enter driver name...")
        elif table_name == "sites":
            self.site_btn.setObjectName("tab_active")
            self.simple_input.setVisible(True)
            self.simple_input.setPlaceholderText("Enter site name...")
        elif table_name == "sections":
            self.section_btn.setObjectName("tab_active")
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