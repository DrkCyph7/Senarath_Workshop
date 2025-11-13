import sqlite3
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QLineEdit, QMessageBox, QDialog,
    QGridLayout, QDialogButtonBox, QFrame, QComboBox, QSpinBox, QDoubleSpinBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from ui.theme import ColorPalette, Typography, Spacing, Styles, create_page_header

GRADES = ["Grade1", "Grade2", "Grade3", "Grade4", "Helper"]

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


class LabourDialog(QDialog):
    def __init__(self, parent=None, edit_data=None, sites=None):
        super().__init__(parent)
        self.setWindowTitle("Add/Edit Labour")
        self.setMinimumWidth(500)
        
        layout = QVBoxLayout()
        form_layout = QGridLayout()
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g., Ravi Kumar")
        
        self.site_input = QComboBox()
        if sites:
            self.site_input.addItems(sites)
        
        self.grade_input = QComboBox()
        self.grade_input.addItems(GRADES)
        
        form_layout.addWidget(QLabel("Name:"), 0, 0)
        form_layout.addWidget(self.name_input, 0, 1)
        
        form_layout.addWidget(QLabel("Site:"), 1, 0)
        form_layout.addWidget(self.site_input, 1, 1)
        
        form_layout.addWidget(QLabel("Grade:"), 2, 0)
        form_layout.addWidget(self.grade_input, 2, 1)
        
        layout.addLayout(form_layout)
        
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
        
        if edit_data:
            self.name_input.setText(edit_data.get('name', ''))
            idx = self.site_input.findText(edit_data.get('site', ''))
            if idx >= 0:
                self.site_input.setCurrentIndex(idx)
            idx = self.grade_input.findText(edit_data.get('grade', ''))
            if idx >= 0:
                self.grade_input.setCurrentIndex(idx)
    
    def get_data(self):
        return {
            'name': self.name_input.text().strip(),
            'site': self.site_input.currentText(),
            'grade': self.grade_input.currentText()
        }


class LabourRateDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Manage Labour Rates")
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        
        layout = QVBoxLayout()
        
        title = QLabel("Labour Grade Hourly Rates")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        layout.addWidget(title)
        
        form_layout = QGridLayout()
        self.rate_inputs = {}
        
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        for idx, grade in enumerate(GRADES):
            c.execute("SELECT cost_per_hour FROM labour_rates WHERE grade=?", (grade,))
            result = c.fetchone()
            rate = result[0] if result else 0.0
            
            label = QLabel(grade + ":")
            spin = QDoubleSpinBox()
            spin.setMinimum(0)
            spin.setMaximum(9999.99)
            spin.setValue(rate)
            spin.setSingleStep(10.0)
            spin.setDecimals(2)
            spin.setSuffix(" Rs/hr")
            
            self.rate_inputs[grade] = spin
            form_layout.addWidget(label, idx, 0)
            form_layout.addWidget(spin, idx, 1)
        
        conn.close()
        
        layout.addLayout(form_layout)
        layout.addStretch()
        
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
    
    def get_rates(self):
        return {grade: spin.value() for grade, spin in self.rate_inputs.items()}


class DriverDialog(QDialog):
    def __init__(self, parent=None, edit_data=None, sites=None):
        super().__init__(parent)
        self.setWindowTitle("Add/Edit Driver")
        self.setMinimumWidth(600)

        layout = QVBoxLayout()
        form = QGridLayout()

        self.first_name = QLineEdit()
        self.first_name.setPlaceholderText("First name")
        self.middle_name = QLineEdit()
        self.middle_name.setPlaceholderText("Middle name (optional)")
        self.last_name = QLineEdit()
        self.last_name.setPlaceholderText("Last name")

        self.nic_input = QLineEdit()
        self.nic_input.setPlaceholderText("NIC Number")

        self.license_input = QLineEdit()
        self.license_input.setPlaceholderText("Driving license number")

        self.address_input = QLineEdit()
        self.address_input.setPlaceholderText("Address")

        self.contact_input = QLineEdit()
        self.contact_input.setPlaceholderText("Contact number")

        self.site_input = QComboBox()
        if sites:
            self.site_input.addItems(sites)

        form.addWidget(QLabel("First Name:"), 0, 0)
        form.addWidget(self.first_name, 0, 1)
        form.addWidget(QLabel("Middle Name:"), 0, 2)
        form.addWidget(self.middle_name, 0, 3)

        form.addWidget(QLabel("Last Name:"), 1, 0)
        form.addWidget(self.last_name, 1, 1)
        form.addWidget(QLabel("NIC No:"), 1, 2)
        form.addWidget(self.nic_input, 1, 3)

        form.addWidget(QLabel("Driving License:"), 2, 0)
        form.addWidget(self.license_input, 2, 1)
        form.addWidget(QLabel("Contact:"), 2, 2)
        form.addWidget(self.contact_input, 2, 3)

        form.addWidget(QLabel("Address:"), 3, 0)
        form.addWidget(self.address_input, 3, 1, 1, 3)

        form.addWidget(QLabel("Site:"), 4, 0)
        form.addWidget(self.site_input, 4, 1)

        layout.addLayout(form)

        btn_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)

        self.setLayout(layout)

        if edit_data:
            # populate if editing
            self.first_name.setText(edit_data.get('first_name', ''))
            self.middle_name.setText(edit_data.get('middle_name', ''))
            self.last_name.setText(edit_data.get('last_name', ''))
            self.nic_input.setText(edit_data.get('nic', ''))
            self.license_input.setText(edit_data.get('license_no', ''))
            self.address_input.setText(edit_data.get('address', ''))
            self.contact_input.setText(edit_data.get('contact', ''))
            idx = self.site_input.findText(edit_data.get('site', ''))
            if idx >= 0:
                self.site_input.setCurrentIndex(idx)

    def get_data(self):
        return {
            'first_name': self.first_name.text().strip(),
            'middle_name': self.middle_name.text().strip(),
            'last_name': self.last_name.text().strip(),
            'nic': self.nic_input.text().strip(),
            'license_no': self.license_input.text().strip(),
            'address': self.address_input.text().strip(),
            'contact': self.contact_input.text().strip(),
            'site': self.site_input.currentText()
        }


def ensure_driver_columns(conn):
    """Ensure drivers table has necessary columns; add them if missing."""
    c = conn.cursor()
    c.execute("PRAGMA table_info(drivers)")
    existing = [row[1] for row in c.fetchall()]
    to_add = []
    cols = {
        'first_name': 'TEXT', 'middle_name': 'TEXT', 'last_name': 'TEXT',
        'nic': 'TEXT', 'license_no': 'TEXT', 'address': 'TEXT', 'contact': 'TEXT',
        'site': 'TEXT', 'driver_uid': 'TEXT'
    }
    for col, typ in cols.items():
        if col not in existing:
            to_add.append((col, typ))
    for col, typ in to_add:
        try:
            c.execute(f"ALTER TABLE drivers ADD COLUMN {col} {typ}")
        except Exception:
            pass
    conn.commit()


def generate_driver_uid(conn, first_name, site):
    """Generate an 8-char unique driver uid: 2 chars from firstname + 2 from site + 4 digit sequence."""
    prefix = (first_name[:2] if first_name else 'XX').upper()
    site_part = (site[:2] if site else 'XX').upper()
    prefix = (prefix + site_part)[:4]
    c = conn.cursor()
    try:
        c.execute("SELECT driver_uid FROM drivers WHERE driver_uid LIKE ?", (prefix + '%',))
        rows = [r[0] for r in c.fetchall() if r[0]]
    except Exception:
        rows = []
    max_seq = 0
    for r in rows:
        suf = ''.join([ch for ch in r if ch.isdigit()])
        if len(suf) >= 1:
            try:
                val = int(suf)
                if val > max_seq:
                    max_seq = val
            except Exception:
                pass
    next_seq = max_seq + 1
    seq_str = str(next_seq).zfill(4)
    return f"{prefix}{seq_str}"


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
        self.labour_btn = QPushButton("👷 Labour")
        self.outsource_btn = QPushButton("🔨 Outsource Types")

        self.tab_buttons = [self.vehicle_btn, self.driver_btn, self.site_btn, self.section_btn, self.labour_btn, self.outsource_btn]
        
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
        
        self.labour_rates_btn = QPushButton("💰 Labour Rates")
        self.labour_rates_btn.setObjectName("secondary")
        self.labour_rates_btn.setFixedHeight(36)
        self.labour_rates_btn.setMinimumWidth(140)
        self.labour_rates_btn.setVisible(False)
        
        action_layout.addWidget(self.add_btn)
        action_layout.addWidget(self.edit_btn)
        action_layout.addWidget(self.delete_btn)
        action_layout.addWidget(self.labour_rates_btn)
        action_layout.addStretch()
        
        layout.addLayout(action_layout)

        self.setLayout(layout)

        # Connect buttons
        self.vehicle_btn.clicked.connect(lambda: self.switch_table("vehicles"))
        self.driver_btn.clicked.connect(lambda: self.switch_table("drivers"))
        self.site_btn.clicked.connect(lambda: self.switch_table("sites"))
        self.section_btn.clicked.connect(lambda: self.switch_table("sections"))
        self.labour_btn.clicked.connect(lambda: self.switch_table("labour"))
        self.outsource_btn.clicked.connect(lambda: self.switch_table("outsource"))
        
        self.add_btn.clicked.connect(self.add_record)
        self.edit_btn.clicked.connect(self.edit_record)
        self.delete_btn.clicked.connect(self.delete_record)
        self.labour_rates_btn.clicked.connect(self.show_labour_rates_dialog)

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
            self.labour_rates_btn.setVisible(False)
        elif table_name == "drivers":
            self.driver_btn.setObjectName("tab_active")
            self.simple_input.setVisible(True)
            self.simple_input.setPlaceholderText("Enter driver name...")
            self.labour_rates_btn.setVisible(False)
        elif table_name == "sites":
            self.site_btn.setObjectName("tab_active")
            self.simple_input.setVisible(True)
            self.simple_input.setPlaceholderText("Enter site name...")
            self.labour_rates_btn.setVisible(False)
        elif table_name == "sections":
            self.section_btn.setObjectName("tab_active")
            self.simple_input.setVisible(True)
            self.simple_input.setPlaceholderText("Enter section name...")
            self.labour_rates_btn.setVisible(False)
        elif table_name == "labour":
            self.labour_btn.setObjectName("tab_active")
            self.simple_input.setVisible(False)
            self.labour_rates_btn.setVisible(True)
        elif table_name == "outsource":
            self.outsource_btn.setObjectName("tab_active")
            self.simple_input.setVisible(True)
            self.simple_input.setPlaceholderText("Enter outsource work type...")
            self.labour_rates_btn.setVisible(False)
        
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
            ensure_driver_columns(conn)
            c.execute(
                """
                SELECT id, name, driver_uid, first_name, middle_name, last_name,
                       nic, license_no, contact, site, address
                FROM drivers
                ORDER BY name
                """
            )
            data = c.fetchall()
            headers = [
                "ID", "Name", "Driver ID", "First Name", "Middle Name", "Last Name",
                "NIC", "License", "Contact", "Site", "Address"
            ]
        elif self.current_table == "sites":
            c.execute("SELECT id, name FROM sites ORDER BY name")
            data = c.fetchall()
            headers = ["ID", "Site Name"]
        elif self.current_table == "sections":
            c.execute("SELECT id, name FROM sections ORDER BY name")
            data = c.fetchall()
            headers = ["ID", "Section Name"]
        elif self.current_table == "labour":
            c.execute("SELECT id, name, site, grade FROM labour ORDER BY name")
            data = c.fetchall()
            headers = ["ID", "Name", "Site", "Grade"]
        elif self.current_table == "outsource":
            c.execute("SELECT id, name FROM outsource_types ORDER BY name")
            data = c.fetchall()
            headers = ["ID", "Work Type"]
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
        elif self.current_table == "labour":
            # Get sites for dropdown
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("SELECT name FROM sites ORDER BY name")
            sites = [row[0] for row in c.fetchall()]
            conn.close()
            
            dialog = LabourDialog(self, sites=sites)
            if dialog.exec():
                data = dialog.get_data()
                if not data['name']:
                    QMessageBox.warning(self, "Warning", "Labour name is required!")
                    return
                
                conn = sqlite3.connect(DB_PATH)
                c = conn.cursor()
                c.execute("INSERT INTO labour (name, site, grade) VALUES (?, ?, ?)",
                         (data['name'], data['site'], data['grade']))
                conn.commit()
                conn.close()
                
                QMessageBox.information(self, "Success", "Labour added successfully!")
                self.refresh_all()
        else:
            text = self.simple_input.text().strip()
            if not text and self.current_table not in ("drivers",):
                QMessageBox.warning(self, "Warning", "Input field cannot be empty!")
                return

            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()

            if self.current_table == "drivers":
                # Open full driver dialog to collect structured info
                c.execute("SELECT name FROM sites ORDER BY name")
                sites = [r[0] for r in c.fetchall()]
                # Ensure driver table has expected columns
                ensure_driver_columns(conn)
                dialog = DriverDialog(self, sites=sites)
                if dialog.exec():
                    data = dialog.get_data()
                    # Validate required fields
                    if not data['first_name'] or not data['last_name']:
                        QMessageBox.warning(self, "Warning", "First and Last name are required!")
                        conn.close()
                        return
                    if not data['nic'] or not data['license_no']:
                        QMessageBox.warning(self, "Warning", "NIC and Driving License are required!")
                        conn.close()
                        return
                    if not data['contact']:
                        QMessageBox.warning(self, "Warning", "Contact number is required!")
                        conn.close()
                        return

                    # Generate unique 8-char driver id
                    driver_uid = generate_driver_uid(conn, data['first_name'], data['site'])
                    display_name = f"{data['first_name']} {data['last_name']}"
                    c.execute(
                        "INSERT INTO drivers (name, first_name, middle_name, last_name, nic, license_no, address, contact, site, driver_uid) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        (display_name, data['first_name'], data['middle_name'], data['last_name'], data['nic'], data['license_no'], data['address'], data['contact'], data['site'], driver_uid)
                    )
                    conn.commit()
                    conn.close()
                    QMessageBox.information(self, "Success", f"Driver added successfully! ID: {driver_uid}")
                    self.refresh_all()
                    return
                else:
                    conn.close()
                    return
            elif self.current_table == "sites":
                c.execute("INSERT INTO sites (name) VALUES (?)", (text,))
            elif self.current_table == "sections":
                c.execute("INSERT INTO sections (name) VALUES (?)", (text,))
            elif self.current_table == "outsource":
                c.execute("INSERT INTO outsource_types (name) VALUES (?)", (text,))

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
        elif self.current_table == "labour":
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("SELECT name, site, grade FROM labour WHERE id=?", (record_id,))
            labour_data = c.fetchone()
            c.execute("SELECT name FROM sites ORDER BY name")
            sites = [row[0] for row in c.fetchall()]
            conn.close()
            
            if labour_data:
                edit_data = {
                    'name': labour_data[0],
                    'site': labour_data[1],
                    'grade': labour_data[2]
                }
                
                dialog = LabourDialog(self, edit_data=edit_data, sites=sites)
                if dialog.exec():
                    data = dialog.get_data()
                    if not data['name']:
                        QMessageBox.warning(self, "Warning", "Labour name is required!")
                        return
                    
                    conn = sqlite3.connect(DB_PATH)
                    c = conn.cursor()
                    c.execute("UPDATE labour SET name=?, site=?, grade=? WHERE id=?",
                             (data['name'], data['site'], data['grade'], record_id))
                    conn.commit()
                    conn.close()
                    
                    QMessageBox.information(self, "Success", "Labour updated successfully!")
                    self.refresh_all()
        else:
            # If editing drivers, open the full driver dialog to edit structured fields
            if self.current_table == "drivers":
                conn = sqlite3.connect(DB_PATH)
                c = conn.cursor()
                ensure_driver_columns(conn)
                c.execute("SELECT name, first_name, middle_name, last_name, nic, license_no, address, contact, site, driver_uid FROM drivers WHERE id=?", (record_id,))
                drv = c.fetchone()
                conn.close()
                if drv:
                    edit_data = {
                        'name': drv[0], 'first_name': drv[1] or '', 'middle_name': drv[2] or '',
                        'last_name': drv[3] or '', 'nic': drv[4] or '', 'license_no': drv[5] or '',
                        'address': drv[6] or '', 'contact': drv[7] or '', 'site': drv[8] or '', 'driver_uid': drv[9] or ''
                    }
                    # get sites for dropdown
                    conn = sqlite3.connect(DB_PATH)
                    c = conn.cursor()
                    c.execute("SELECT name FROM sites ORDER BY name")
                    sites = [r[0] for r in c.fetchall()]
                    conn.close()
                    dialog = DriverDialog(self, edit_data=edit_data, sites=sites)
                    if dialog.exec():
                        data = dialog.get_data()
                        if not data['first_name'] or not data['last_name']:
                            QMessageBox.warning(self, "Warning", "First and Last name are required!")
                            return
                        conn = sqlite3.connect(DB_PATH)
                        c = conn.cursor()
                        c.execute("UPDATE drivers SET first_name=?, middle_name=?, last_name=?, nic=?, license_no=?, address=?, contact=?, site=? WHERE id=?",
                                  (data['first_name'], data['middle_name'], data['last_name'], data['nic'], data['license_no'], data['address'], data['contact'], data['site'], record_id))
                        conn.commit()
                        conn.close()
                        QMessageBox.information(self, "Success", "Driver updated successfully!")
                        self.refresh_all()
                        return

            text = self.simple_input.text().strip()
            if not text:
                QMessageBox.warning(self, "Warning", "Input field cannot be empty!")
                return

            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            table_name = "outsource_types" if self.current_table == "outsource" else self.current_table
            c.execute(f"UPDATE {table_name} SET name=? WHERE id=?", (text, record_id))
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
            table_name = "outsource_types" if self.current_table == "outsource" else self.current_table
            c.execute(f"DELETE FROM {table_name} WHERE id=?", (record_id,))
        
        conn.commit()
        conn.close()
        
        QMessageBox.information(self, "Deleted", "Record(s) deleted successfully!")
        self.refresh_all()

    def show_labour_rates_dialog(self):
        dialog = LabourRateDialog(self)
        if dialog.exec():
            rates = dialog.get_rates()
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            for grade, rate in rates.items():
                c.execute("UPDATE labour_rates SET cost_per_hour=? WHERE grade=?", (rate, grade))
            conn.commit()
            conn.close()
            QMessageBox.information(self, "Success", "Labour rates updated successfully!")