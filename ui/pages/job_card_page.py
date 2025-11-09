import sqlite3
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QGridLayout, QLabel, QLineEdit, QTextEdit, QPushButton,
    QDateEdit, QComboBox, QFrame, QScrollArea, QHBoxLayout, QMessageBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QDialog, QDialogButtonBox
)
from PySide6.QtCore import QDate, Qt
from PySide6.QtGui import QFont
from ui.theme import ColorPalette, Typography, Spacing, Styles, create_page_header

DB_PATH = "ui/db/senarath.db"


class SparePartDialog(QDialog):
    def __init__(self, parent=None, edit_data=None):
        super().__init__(parent)
        self.setWindowTitle("Add/Edit Spare Part")
        self.setMinimumWidth(480)
        
        # Modern dialog styling using theme
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {ColorPalette.CARD_BG};
            }}
            QLabel {{
                color: {ColorPalette.TEXT_PRIMARY};
                font-weight: {Typography.WEIGHT_SEMIBOLD};
                font-size: {Typography.SIZE_SMALL}px;
                background: transparent;
            }}
            QLineEdit, QTextEdit {{
                background-color: #fafafa;
                border: 1px solid {ColorPalette.BORDER_LIGHT};
                border-radius: {Spacing.BORDER_RADIUS_SMALL}px;
                padding: {Spacing.PADDING_SMALL}px {Spacing.PADDING_MEDIUM}px;
                font-size: {Typography.SIZE_SMALL}px;
            }}
            QLineEdit:focus, QTextEdit:focus {{
                border: 2px solid {ColorPalette.ACCENT_PRIMARY};
                background-color: #ffffff;
            }}
            QTextEdit {{
                min-height: 80px;
            }}
            QDialogButtonBox QPushButton {{
                background-color: {ColorPalette.ACCENT_PRIMARY};
                color: white;
                border: none;
                border-radius: {Spacing.BORDER_RADIUS_MEDIUM}px;
                padding: {Spacing.PADDING_SMALL}px 18px;
                font-weight: {Typography.WEIGHT_SEMIBOLD};
                min-width: 75px;
            }}
            QDialogButtonBox QPushButton:hover {{
                opacity: 0.9;
            }}
            QDialogButtonBox QPushButton[text="Cancel"] {{
                background-color: #e8e8e8;
                color: #333;
            }}
            QDialogButtonBox QPushButton[text="Cancel"]:hover {{
                background-color: #d5d5d5;
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(Spacing.MARGIN_LARGE)
        layout.setContentsMargins(Spacing.PADDING_XL, Spacing.PADDING_XL, Spacing.PADDING_XL, Spacing.PADDING_XL)
        
        # Title
        title = QLabel("🔧 Spare Part Details")
        title.setFont(QFont("Segoe UI", 15, QFont.Bold))
        title.setStyleSheet("color: #1a1a1a; padding-bottom: 6px;")
        layout.addWidget(title)
        
        form_layout = QGridLayout()
        form_layout.setSpacing(10)
        form_layout.setVerticalSpacing(14)
        
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("e.g., Oil Filter - Mann W610/3")
        
        self.ref_no_input = QLineEdit()
        self.ref_no_input.setPlaceholderText("e.g., INV-2024-001")
        
        self.quantity_input = QLineEdit()
        self.quantity_input.setPlaceholderText("e.g., 2")
        self.quantity_input.textChanged.connect(self.calculate_total)
        
        self.unit_input = QLineEdit()
        self.unit_input.setPlaceholderText("e.g., pcs, liters, kg")
        
        self.unit_price_input = QLineEdit()
        self.unit_price_input.setPlaceholderText("e.g., 1500.00")
        self.unit_price_input.textChanged.connect(self.calculate_total)
        
        self.total_input = QLineEdit()
        self.total_input.setReadOnly(True)
        self.total_input.setPlaceholderText("Auto-calculated")
        
        form_layout.addWidget(QLabel("Description:"), 0, 0)
        form_layout.addWidget(self.description_input, 0, 1)
        
        form_layout.addWidget(QLabel("Reference No:"), 1, 0)
        form_layout.addWidget(self.ref_no_input, 1, 1)
        
        form_layout.addWidget(QLabel("Quantity:"), 2, 0)
        form_layout.addWidget(self.quantity_input, 2, 1)
        
        form_layout.addWidget(QLabel("Unit:"), 3, 0)
        form_layout.addWidget(self.unit_input, 3, 1)
        
        form_layout.addWidget(QLabel("Unit Price:"), 4, 0)
        form_layout.addWidget(self.unit_price_input, 4, 1)
        
        form_layout.addWidget(QLabel("Total:"), 5, 0)
        form_layout.addWidget(self.total_input, 5, 1)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
        
        # If editing, populate fields
        if edit_data:
            self.description_input.setPlainText(edit_data.get('description', ''))
            self.ref_no_input.setText(edit_data.get('ref_no', ''))
            self.quantity_input.setText(edit_data.get('quantity', ''))
            self.unit_input.setText(edit_data.get('unit', ''))
            self.unit_price_input.setText(edit_data.get('unit_price', ''))
            self.total_input.setText(edit_data.get('total', ''))
    
    def calculate_total(self):
        try:
            quantity = float(self.quantity_input.text() or 0)
            unit_price = float(self.unit_price_input.text() or 0)
            total = quantity * unit_price
            self.total_input.setText(f"{total:.2f}")
        except ValueError:
            self.total_input.setText("0.00")
    
    def get_data(self):
        return {
            'description': self.description_input.toPlainText().strip(),
            'ref_no': self.ref_no_input.text().strip(),
            'quantity': self.quantity_input.text().strip(),
            'unit': self.unit_input.text().strip(),
            'unit_price': self.unit_price_input.text().strip(),
            'total': self.total_input.text().strip()
        }


class JobCardPage(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.conn = sqlite3.connect(DB_PATH)
        self.spare_parts_data = []

        # === Professional UI Colors ===
        bg_color = "#f5f5f5"
        card_color = "#ffffff"
        accent_color = "#2d7a5f"
        text_color = "#2c2c2c"
        border_color = "#e0e0e0"
        secondary_color = "#8b6f47"
        input_bg = "#fafafa"
        input_focus_bg = "#ffffff"

        self.setStyleSheet(f"""
            QWidget {{
                background-color: {bg_color};
                color: {text_color};
                font-family: "Segoe UI", -apple-system, system-ui;
                font-size: 13px;
            }}
            QLabel {{
                background: transparent;
            }}
            QLabel#page_title {{
                font-weight: 700;
                color: #1a1a1a;
                font-size: 24px;
                background: transparent;
            }}
            QLabel#section_title {{
                font-weight: 700;
                color: {accent_color};
                font-size: 14px;
                padding: 0px 0px 12px 0px;
                background: transparent;
            }}
            QLabel#field_label {{
                font-weight: 500;
                color: #666666;
                font-size: 11px;
                background: transparent;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            QLabel#total_label {{
                font-weight: 700;
                color: #1a1a1a;
                font-size: 14px;
                background: transparent;
            }}
            QFrame#card {{
                background-color: {card_color};
                border-radius: 8px;
                padding: 18px;
                border: none;
            }}
            QLineEdit, QDateEdit, QComboBox {{
                background-color: {input_bg};
                border: 1px solid {border_color};
                border-radius: 6px;
                padding: 8px 11px;
                min-height: 32px;
                font-size: 12px;
            }}
            QLineEdit:focus, QComboBox:focus, QDateEdit:focus {{
                border: 2px solid {accent_color};
                background-color: {input_focus_bg};
                outline: none;
            }}
            QLineEdit:read-only {{
                background-color: #f8f8f8;
                color: #666666;
                font-weight: 500;
                border: 1px solid #efefef;
            }}
            QTextEdit {{
                background-color: {input_bg};
                border: 1px solid {border_color};
                border-radius: 6px;
                padding: 10px;
                min-height: 80px;
                font-size: 12px;
            }}
            QTextEdit:focus {{
                border: 2px solid {accent_color};
                background-color: {input_focus_bg};
            }}
            QComboBox::drop-down {{
                border: none;
                padding-right: 6px;
                width: 20px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid #999;
                margin-right: 4px;
            }}
            QPushButton {{
                border: none;
                border-radius: 6px;
                font-weight: 600;
                font-size: 12px;
                text-transform: uppercase;
                letter-spacing: 0.3px;
            }}
            QPushButton#primary {{
                background-color: {accent_color};
                color: white;
                padding: 11px 22px;
            }}
            QPushButton#primary:hover {{
                background-color: #246651;
            }}
            QPushButton#primary:pressed {{
                background-color: #1f5443;
            }}
            QPushButton#secondary {{
                background-color: {secondary_color};
                color: white;
                padding: 9px 16px;
            }}
            QPushButton#secondary:hover {{
                background-color: #735a38;
            }}
            QPushButton#muted {{
                background-color: #e8e8e8;
                color: #333;
                padding: 9px 16px;
            }}
            QPushButton#muted:hover {{
                background-color: #d5d5d5;
            }}
            QPushButton#danger {{
                background-color: #c84343;
                color: white;
                padding: 9px 16px;
            }}
            QPushButton#danger:hover {{
                background-color: #b03636;
            }}
            QPushButton#ghost {{
                background-color: transparent;
                color: #666;
                border: 1px solid #d0d0d0;
                padding: 9px 18px;
                text-transform: none;
                letter-spacing: 0px;
            }}
            QPushButton#ghost:hover {{
                background-color: #fafafa;
                border-color: #bbb;
            }}
            QTableWidget {{
                background-color: {card_color};
                border: 1px solid {border_color};
                border-radius: 6px;
                gridline-color: #f0f0f0;
                font-size: 12px;
            }}
            QTableWidget::item {{
                padding: 8px;
                background: transparent;
                border: none;
            }}
            QTableWidget::item:selected {{
                background-color: #e8f4f0;
                color: #1a1a1a;
            }}
            QHeaderView::section {{
                background-color: {accent_color};
                color: white;
                padding: 10px 8px;
                border: none;
                font-weight: 700;
                font-size: 11px;
                text-transform: uppercase;
                letter-spacing: 0.3px;
            }}
            QScrollBar:vertical {{
                background: #f5f5f5;
                width: 8px;
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical {{
                background: #bfbfbf;
                border-radius: 4px;
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: #9f9f9f;
            }}
        """)

        # === Scroll container ===
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        container = QWidget()
        root_layout = QVBoxLayout(container)
        root_layout.setContentsMargins(35, 28, 35, 28)
        root_layout.setSpacing(20)

        # === Page Title with Back Button ===
        header_layout, title_label, back_btn_top = create_page_header("📝 Job Card Entry")
        back_btn_top.clicked.connect(lambda: self.parent.go_to_home() if self.parent else None)
        root_layout.addLayout(header_layout)

        # === Basic Information Card ===
        basic_card = QFrame()
        basic_card.setObjectName("card")
        basic_layout = QVBoxLayout(basic_card)
        basic_layout.setSpacing(14)
        
        basic_title = QLabel("📋 Basic Information")
        basic_title.setObjectName("section_title")
        basic_layout.addWidget(basic_title)
        
        grid = QGridLayout()
        grid.setHorizontalSpacing(14)
        grid.setVerticalSpacing(14)
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(3, 1)

        # === Create labels with consistent styling ===
        def create_label(text):
            lbl = QLabel(text)
            lbl.setObjectName("field_label")
            return lbl

        # === Inputs ===
        self.job_no_input = QLineEdit()
        self.job_no_input.setText(self.generate_job_number())
        self.job_no_input.setPlaceholderText("Auto-generated or enter custom job number")

        self.driver_input = QComboBox()
        self.company_no_input = QComboBox()
        self.company_no_input.currentTextChanged.connect(self.auto_fill_from_company)

        self.site_input = QComboBox()
        self.vehicle_input = QComboBox()
        self.vehicle_input.currentTextChanged.connect(self.auto_fill_from_vehicle)

        self.section_input = QComboBox()
        
        self.make_input = QLineEdit()
        self.make_input.setReadOnly(True)
        self.make_input.setPlaceholderText("Auto-filled")

        self.hr_km_input = QLineEdit()
        self.hr_km_input.setPlaceholderText("e.g. 12450 km")

        self.model_input = QLineEdit()
        self.model_input.setReadOnly(True)
        self.model_input.setPlaceholderText("Auto-filled")

        self.date_input = QDateEdit(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        self.date_input.setDisplayFormat("yyyy-MM-dd")
        self.date_input.dateChanged.connect(self.on_date_changed)  # Update job no when date changes

        self.type_input = QLineEdit()
        self.type_input.setReadOnly(True)
        self.type_input.setPlaceholderText("Auto-filled")

        self.end_date_input = QDateEdit(QDate.currentDate())
        self.end_date_input.setCalendarPopup(True)
        self.end_date_input.setDisplayFormat("yyyy-MM-dd")

        # === Grid layout - Optimized Order ===
        grid.addWidget(create_label("Job No"), 0, 0)
        grid.addWidget(self.job_no_input, 0, 1)
        grid.addWidget(create_label("Driver Name"), 0, 2)
        grid.addWidget(self.driver_input, 0, 3)

        grid.addWidget(create_label("Company No"), 1, 0)
        grid.addWidget(self.company_no_input, 1, 1)
        grid.addWidget(create_label("Site"), 1, 2)
        grid.addWidget(self.site_input, 1, 3)

        grid.addWidget(create_label("Vehicle No"), 2, 0)
        grid.addWidget(self.vehicle_input, 2, 1)
        grid.addWidget(create_label("Section"), 2, 2)
        grid.addWidget(self.section_input, 2, 3)

        grid.addWidget(create_label("Make"), 3, 0)
        grid.addWidget(self.make_input, 3, 1)
        grid.addWidget(create_label("Hr/Km Reading"), 3, 2)
        grid.addWidget(self.hr_km_input, 3, 3)

        grid.addWidget(create_label("Model"), 4, 0)
        grid.addWidget(self.model_input, 4, 1)
        grid.addWidget(create_label("Start Date"), 4, 2)
        grid.addWidget(self.date_input, 4, 3)

        grid.addWidget(create_label("Type"), 5, 0)
        grid.addWidget(self.type_input, 5, 1)
        grid.addWidget(create_label("End Date"), 5, 2)
        grid.addWidget(self.end_date_input, 5, 3)

        basic_layout.addLayout(grid)
        root_layout.addWidget(basic_card)

        # === Job Description Card ===
        desc_card = QFrame()
        desc_card.setObjectName("card")
        desc_layout = QVBoxLayout(desc_card)
        desc_layout.setSpacing(12)
        
        desc_title = QLabel("📝 Job Description")
        desc_title.setObjectName("section_title")
        desc_layout.addWidget(desc_title)
        
        self.desc_input = QTextEdit()
        self.desc_input.setPlaceholderText("Describe the work performed, issues found, repairs made, maintenance activities, etc...")
        desc_layout.addWidget(self.desc_input)
        
        root_layout.addWidget(desc_card)

        # === Spare Parts Card ===
        spare_card = QFrame()
        spare_card.setObjectName("card")
        spare_layout = QVBoxLayout(spare_card)
        spare_layout.setSpacing(12)
        
        spare_header = QHBoxLayout()
        spare_header.setSpacing(10)
        spare_title = QLabel("🔧 Spare Parts & Materials")
        spare_title.setObjectName("section_title")
        spare_header.addWidget(spare_title)
        spare_header.addStretch()
        
        add_part_btn = QPushButton("+ Add Part")
        add_part_btn.setObjectName("secondary")
        add_part_btn.setFixedHeight(32)
        add_part_btn.setMaximumWidth(120)
        add_part_btn.setCursor(Qt.PointingHandCursor)
        add_part_btn.clicked.connect(self.add_spare_part)
        spare_header.addWidget(add_part_btn)
        
        spare_layout.addLayout(spare_header)
        
        # Spare parts table
        self.spare_table = QTableWidget()
        self.spare_table.setColumnCount(6)
        self.spare_table.setHorizontalHeaderLabels(["#", "Description", "Ref No", "Quantity", "Unit", "Total"])
        self.spare_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.spare_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.spare_table.setMinimumHeight(180)
        self.spare_table.setMaximumHeight(260)
        self.spare_table.setSelectionBehavior(QTableWidget.SelectRows)
        spare_layout.addWidget(self.spare_table)
        
        # Grand Total
        total_layout = QHBoxLayout()
        total_layout.addStretch()
        self.grand_total_label = QLabel("Grand Total: Rs. 0.00")
        self.grand_total_label.setObjectName("total_label")
        self.grand_total_label.setStyleSheet("font-size: 13px; padding: 8px 12px; background-color: #e8f4f0; border-radius: 6px;")
        total_layout.addWidget(self.grand_total_label)
        spare_layout.addLayout(total_layout)
        
        # Spare parts action buttons
        spare_btn_layout = QHBoxLayout()
        spare_btn_layout.setSpacing(8)
        
        edit_part_btn = QPushButton("✏️ Edit")
        edit_part_btn.setObjectName("muted")
        edit_part_btn.setFixedHeight(32)
        edit_part_btn.setMaximumWidth(100)
        edit_part_btn.setCursor(Qt.PointingHandCursor)
        edit_part_btn.clicked.connect(self.edit_spare_part)
        
        delete_part_btn = QPushButton("🗑️ Delete")
        delete_part_btn.setObjectName("danger")
        delete_part_btn.setFixedHeight(32)
        delete_part_btn.setMaximumWidth(100)
        delete_part_btn.setCursor(Qt.PointingHandCursor)
        delete_part_btn.clicked.connect(self.delete_spare_part)
        
        spare_btn_layout.addWidget(edit_part_btn)
        spare_btn_layout.addWidget(delete_part_btn)
        spare_btn_layout.addStretch()
        spare_layout.addLayout(spare_btn_layout)
        
        root_layout.addWidget(spare_card)

        # === Action Buttons ===
        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)
        
        save_btn = QPushButton("💾 Save Job Card")
        save_btn.setObjectName("primary")
        save_btn.setFixedHeight(38)
        save_btn.setMinimumWidth(180)
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.clicked.connect(self.save_job_card)

        clear_btn = QPushButton("🧹 Clear All")
        clear_btn.setObjectName("muted")
        clear_btn.setFixedHeight(38)
        clear_btn.setMinimumWidth(120)
        clear_btn.setCursor(Qt.PointingHandCursor)
        clear_btn.clicked.connect(self.clear_all_fields)

        btn_row.addWidget(save_btn)
        btn_row.addWidget(clear_btn)
        btn_row.addStretch()

        root_layout.addLayout(btn_row)
        root_layout.addStretch()
        
        scroll.setWidget(container)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(scroll)
        self.setLayout(layout)

        # === Load initial data ===
        self.refresh_dropdowns()

    def refresh_dropdowns(self):
        # Refresh job number in real-time
        self.job_no_input.setText(self.generate_job_number())
        
        cur = self.conn.cursor()

        # Vehicles
        cur.execute("SELECT company_no, number, make, model, type FROM vehicles")
        vehicles = cur.fetchall()
        self.company_no_input.clear()
        self.vehicle_input.clear()
        company_nos = set()
        vehicle_nos = set()
        
        for v in vehicles:
            company_no, number, *_ = v
            if company_no and company_no not in company_nos:
                self.company_no_input.addItem(company_no)
                company_nos.add(company_no)
            if number and number != "-" and number not in vehicle_nos:
                self.vehicle_input.addItem(number)
                vehicle_nos.add(number)

        # Drivers
        cur.execute("SELECT name FROM drivers")
        self.driver_input.clear()
        [self.driver_input.addItem(d[0]) for d in cur.fetchall()]

        # Sites
        cur.execute("SELECT name FROM sites")
        self.site_input.clear()
        [self.site_input.addItem(s[0]) for s in cur.fetchall()]

        # Sections
        cur.execute("SELECT name FROM sections")
        self.section_input.clear()
        [self.section_input.addItem(s[0]) for s in cur.fetchall()]

    def auto_fill_from_company(self, company_no):
        if not company_no:
            self.vehicle_input.clear()
            self.make_input.clear()
            self.model_input.clear()
            self.type_input.clear()
            return
        
        cur = self.conn.cursor()
        cur.execute("SELECT number, make, model, type FROM vehicles WHERE company_no=?", (company_no,))
        vehicles = cur.fetchall()
        
        self.vehicle_input.blockSignals(True)
        self.vehicle_input.clear()
        
        if vehicles:
            for vehicle in vehicles:
                if vehicle[0] and vehicle[0] != "-":
                    self.vehicle_input.addItem(vehicle[0])
            
            first_vehicle = vehicles[0]
            self.vehicle_input.setCurrentIndex(0)
            self.make_input.setText(first_vehicle[1] or "")
            self.model_input.setText(first_vehicle[2] or "")
            self.type_input.setText(first_vehicle[3] or "")
        else:
            self.make_input.clear()
            self.model_input.clear()
            self.type_input.clear()
        
        self.vehicle_input.blockSignals(False)

    def auto_fill_from_vehicle(self, number):
        if not number:
            return
        cur = self.conn.cursor()
        cur.execute("SELECT make, model, type FROM vehicles WHERE number=?", (number,))
        row = cur.fetchone()
        if row:
            self.make_input.setText(row[0] or "")
            self.model_input.setText(row[1] or "")
            self.type_input.setText(row[2] or "")

    def on_date_changed(self):
        """Update job number when start date changes"""
        self.job_no_input.setText(self.generate_job_number())

    def generate_job_number(self):
        cur = self.conn.cursor()
        # Use start date if available, otherwise use current date
        if hasattr(self, 'date_input'):
            start_date = self.date_input.date()
        else:
            start_date = QDate.currentDate()
        
        yy = start_date.toString("yy")
        mm = start_date.toString("MM")
        
        # Find the maximum job number for the selected month/year
        cur.execute("SELECT job_no FROM job_cards WHERE job_no LIKE ? ORDER BY job_no DESC LIMIT 1", 
                   (f"SEN/DO/{yy}{mm}%",))
        last_job = cur.fetchone()

        if last_job:
            try:
                next_num = int(last_job[0][-3:]) + 1
            except (ValueError, IndexError):
                next_num = 1
        else:
            next_num = 1

        return f"SEN/DO/{yy}{mm}{next_num:03d}"

    def add_spare_part(self):
        dialog = SparePartDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            if data['description']:
                self.spare_parts_data.append(data)
                self.refresh_spare_table()

    def edit_spare_part(self):
        current_row = self.spare_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "No Selection", "Please select a spare part to edit.")
            return
        
        current_data = self.spare_parts_data[current_row]
        dialog = SparePartDialog(self, edit_data=current_data)
        if dialog.exec():
            data = dialog.get_data()
            if data['description']:
                self.spare_parts_data[current_row] = data
                self.refresh_spare_table()

    def delete_spare_part(self):
        current_row = self.spare_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "No Selection", "Please select a spare part to delete.")
            return
        
        confirm = QMessageBox.question(self, "Confirm Delete", 
                                      "Are you sure you want to delete this spare part?",
                                      QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            del self.spare_parts_data[current_row]
            self.refresh_spare_table()

    def refresh_spare_table(self):
        self.spare_table.setRowCount(len(self.spare_parts_data))
        self.spare_table.setColumnCount(6)
        self.spare_table.setHorizontalHeaderLabels(["#", "Description", "Ref No", "Quantity", "Unit", "Total"])
        
        grand_total = 0.0
        
        for row_idx, part in enumerate(self.spare_parts_data):
            self.spare_table.setItem(row_idx, 0, QTableWidgetItem(str(row_idx + 1)))
            self.spare_table.setItem(row_idx, 1, QTableWidgetItem(part.get('description', '')))
            self.spare_table.setItem(row_idx, 2, QTableWidgetItem(part.get('ref_no', '')))
            self.spare_table.setItem(row_idx, 3, QTableWidgetItem(part.get('quantity', '')))
            self.spare_table.setItem(row_idx, 4, QTableWidgetItem(part.get('unit', '')))
            self.spare_table.setItem(row_idx, 5, QTableWidgetItem(part.get('total', '')))
            
            try:
                total = float(part.get('total', 0))
                grand_total += total
            except ValueError:
                pass
        
        self.grand_total_label.setText(f"Grand Total: Rs. {grand_total:,.2f}")

    def clear_all_fields(self):
        # Only ask for confirmation when Clear button is clicked
        reply = QMessageBox.question(
            self,
            "Clear All Fields",
            "Are you sure you want to clear all fields?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self._perform_clear()

    def _perform_clear(self):
        """Internal method to clear fields without confirmation"""
        self.job_no_input.setText(self.generate_job_number())
        for combo in [self.company_no_input, self.vehicle_input, self.driver_input, self.site_input, self.section_input]:
            combo.setCurrentIndex(-1)
        for line in [self.make_input, self.model_input, self.type_input, self.hr_km_input]:
            line.clear()
        self.date_input.setDate(QDate.currentDate())
        self.end_date_input.setDate(QDate.currentDate())
        self.desc_input.clear()
        self.spare_parts_data = []
        self.refresh_spare_table()

    def save_job_card(self):
        job_no = self.job_no_input.text().strip()
        company_no = self.company_no_input.currentText().strip()

        if not company_no:
            QMessageBox.warning(self, "Missing Field", "Please select a Company No.")
            return

        # Check if job_no already exists
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(*) FROM job_cards WHERE job_no = ?", (job_no,))
        if cur.fetchone()[0] > 0:
            QMessageBox.warning(self, "Duplicate Entry", f"Job card {job_no} already exists!")
            return

        import json
        spare_parts_json = json.dumps(self.spare_parts_data)

        try:
            cur.execute("""
                INSERT INTO job_cards (
                    job_no, company_no, vehicle_no, driver, make, model, type,
                    site, section, hr_km, start_date, end_date, description, spare_parts
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                job_no,
                company_no,
                self.vehicle_input.currentText().strip() or "-",
                self.driver_input.currentText().strip(),
                self.make_input.text(),
                self.model_input.text(),
                self.type_input.text(),
                self.site_input.currentText(),
                self.section_input.currentText(),
                self.hr_km_input.text(),
                self.date_input.date().toString("yyyy-MM-dd"),
                self.end_date_input.date().toString("yyyy-MM-dd"),
                self.desc_input.toPlainText(),
                spare_parts_json
            ))
            self.conn.commit()

            QMessageBox.information(self, "Success ✅", f"Job card {job_no} has been saved successfully!")
            
            # Automatically clear all fields after successful save
            self._perform_clear()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save job card: {str(e)}")