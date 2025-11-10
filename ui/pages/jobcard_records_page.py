import sqlite3
import json
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QTableWidget, QTableWidgetItem, QMessageBox, QComboBox,
    QDateEdit, QCheckBox, QFrame, QDialog, QTextEdit, QGridLayout,
    QDialogButtonBox, QScrollArea, QSpinBox, QDoubleSpinBox, QTabWidget
)
from PySide6.QtCore import Qt, QDate, QTimer
from PySide6.QtGui import QFont, QColor
from ui.theme import ColorPalette, Typography, Spacing, Styles, create_page_header

DB_PATH = "ui/db/senarath.db"


class LabourWorksDialog(QDialog):
    """Display labour works with detailed breakdown"""
    def __init__(self, labour_works_json, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Labour Works Details")
        self.setMinimumSize(900, 600)
        
        self.labour_works_data = []
        try:
            self.labour_works_data = json.loads(labour_works_json) if labour_works_json else []
        except:
            self.labour_works_data = []
        
        self.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
            }
            QLabel {
                color: #2c2c2c;
                font-weight: 600;
                font-size: 13px;
            }
            QTableWidget {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                gridline-color: #e0e0e0;
            }
            QHeaderView::section {
                background-color: #2d7a5f;
                color: white;
                padding: 10px;
                border: none;
                font-weight: 700;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("👷 Labour Works Summary")
        title.setFont(QFont("Segoe UI", 15, QFont.Bold))
        title.setStyleSheet("color: #2d7a5f; padding-bottom: 10px;")
        layout.addWidget(title)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["#", "Description", "Hours", "Labour Assigned", "Cost"])
        layout.addWidget(self.table)
        
        # Summary
        summary_layout = QHBoxLayout()
        summary_layout.addStretch()
        
        self.total_hours_label = QLabel("Total Hours: 0.00")
        self.total_hours_label.setStyleSheet("font-size: 13px; padding: 8px 15px; background-color: #f0f0f0; border-radius: 5px;")
        summary_layout.addWidget(self.total_hours_label)
        
        self.total_labour_cost_label = QLabel("Total Labour Cost: Rs. 0.00")
        self.total_labour_cost_label.setStyleSheet("font-size: 13px; font-weight: 700; padding: 8px 15px; background-color: #e8f4f0; border-radius: 5px; color: #2d7a5f;")
        summary_layout.addWidget(self.total_labour_cost_label)
        
        layout.addLayout(summary_layout)
        
        # Close button
        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        button_box.accepted.connect(self.accept)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
        self.refresh_table()
    
    def refresh_table(self):
        self.table.setRowCount(len(self.labour_works_data))
        total_hours = 0.0
        total_cost = 0.0
        
        for row_idx, work in enumerate(self.labour_works_data):
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(row_idx + 1)))
            self.table.setItem(row_idx, 1, QTableWidgetItem(work.get('description', '')))
            self.table.setItem(row_idx, 2, QTableWidgetItem(str(work.get('hours', '0'))))
            
            # Parse labour list
            labour_list = []
            try:
                labour_json = work.get('labour_list', '[]')
                labour_items = json.loads(labour_json) if isinstance(labour_json, str) else labour_json
                labour_list = [item['name'] for item in labour_items]
            except:
                pass
            
            self.table.setItem(row_idx, 3, QTableWidgetItem(', '.join(labour_list)))
            self.table.setItem(row_idx, 4, QTableWidgetItem(f"Rs. {work.get('work_cost', '0')}"))
            
            try:
                total_hours += float(work.get('hours', 0))
                total_cost += float(work.get('work_cost', 0))
            except ValueError:
                pass
        
        self.total_hours_label.setText(f"Total Hours: {total_hours:.2f}")
        self.total_labour_cost_label.setText(f"Total Labour Cost: Rs. {total_cost:,.2f}")


class SparePartEditDialog(QDialog):
    def __init__(self, spare_parts_json, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Spare Parts")
        self.setMinimumSize(800, 500)
        
        self.spare_parts_data = []
        try:
            self.spare_parts_data = json.loads(spare_parts_json) if spare_parts_json else []
        except:
            self.spare_parts_data = []
        
        self.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
            }
            QLabel {
                color: #2c2c2c;
                font-weight: 600;
                font-size: 13px;
            }
            QTableWidget {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                gridline-color: #e0e0e0;
            }
            QHeaderView::section {
                background-color: #2d7a5f;
                color: white;
                padding: 10px;
                border: none;
                font-weight: 700;
            }
            QPushButton {
                background-color: #2d7a5f;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 9px 18px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #246651;
            }
            QPushButton#secondary {
                background-color: #8b6f47;
            }
            QPushButton#secondary:hover {
                background-color: #735a38;
            }
            QPushButton#danger {
                background-color: #c84343;
            }
            QPushButton#danger:hover {
                background-color: #b03636;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("🔧 Spare Parts & Materials Used")
        title.setFont(QFont("Segoe UI", 15, QFont.Bold))
        title.setStyleSheet("color: #2d7a5f; padding-bottom: 10px;")
        layout.addWidget(title)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["#", "Description", "Ref No", "Quantity", "Unit", "Unit Price", "Total"])
        layout.addWidget(self.table)
        
        # Grand Total
        total_layout = QHBoxLayout()
        total_layout.addStretch()
        self.grand_total_label = QLabel("Grand Total: Rs. 0.00")
        self.grand_total_label.setStyleSheet("font-size: 16px; font-weight: 700; padding: 10px; background-color: #e8f4f0; border-radius: 5px;")
        total_layout.addWidget(self.grand_total_label)
        layout.addLayout(total_layout)
        
        # Buttons
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("+ Add Part")
        add_btn.clicked.connect(self.add_part)
        edit_btn = QPushButton("✏️ Edit Selected")
        edit_btn.setObjectName("secondary")
        edit_btn.clicked.connect(self.edit_part)
        delete_btn = QPushButton("🗑️ Delete Selected")
        delete_btn.setObjectName("danger")
        delete_btn.clicked.connect(self.delete_part)
        
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(edit_btn)
        btn_layout.addWidget(delete_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        # Dialog buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
        self.refresh_table()
    
    def refresh_table(self):
        self.table.setRowCount(len(self.spare_parts_data))
        grand_total = 0.0
        
        for row_idx, part in enumerate(self.spare_parts_data):
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(row_idx + 1)))
            self.table.setItem(row_idx, 1, QTableWidgetItem(part.get('description', '')))
            self.table.setItem(row_idx, 2, QTableWidgetItem(part.get('ref_no', '')))
            self.table.setItem(row_idx, 3, QTableWidgetItem(part.get('quantity', '')))
            self.table.setItem(row_idx, 4, QTableWidgetItem(part.get('unit', '')))
            self.table.setItem(row_idx, 5, QTableWidgetItem(part.get('unit_price', '')))
            self.table.setItem(row_idx, 6, QTableWidgetItem(part.get('total', '')))
            
            try:
                total = float(part.get('total', 0))
                grand_total += total
            except ValueError:
                pass
        
        self.grand_total_label.setText(f"Grand Total: Rs. {grand_total:,.2f}")
    
    def add_part(self):
        from ui.pages.job_card_page import SparePartDialog
        dialog = SparePartDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            if data['description']:
                self.spare_parts_data.append(data)
                self.refresh_table()
    
    def edit_part(self):
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "No Selection", "Please select a spare part to edit.")
            return
        
        from ui.pages.job_card_page import SparePartDialog
        current_data = self.spare_parts_data[current_row]
        dialog = SparePartDialog(self, edit_data=current_data)
        if dialog.exec():
            data = dialog.get_data()
            if data['description']:
                self.spare_parts_data[current_row] = data
                self.refresh_table()
    
    def delete_part(self):
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "No Selection", "Please select a spare part to delete.")
            return
        
        confirm = QMessageBox.question(self, "Confirm Delete", 
                                      "Are you sure you want to delete this spare part?",
                                      QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            del self.spare_parts_data[current_row]
            self.refresh_table()
    
    def get_data(self):
        return json.dumps(self.spare_parts_data)


class JobCardEditDialog(QDialog):
    def __init__(self, job_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Edit Job Card - {job_data.get('job_no', 'N/A')}")
        self.setMinimumSize(800, 700)
        self.job_id = job_data.get('id')
        
        # Load dropdown data
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        # Get all vehicles
        c.execute("SELECT company_no, number, make, model, type FROM vehicles")
        self.vehicles = c.fetchall()
        
        # Get drivers
        c.execute("SELECT name FROM drivers")
        self.drivers = [row[0] for row in c.fetchall()]
        
        # Get sites
        c.execute("SELECT name FROM sites")
        self.sites = [row[0] for row in c.fetchall()]
        
        # Get sections
        c.execute("SELECT name FROM sections")
        self.sections = [row[0] for row in c.fetchall()]
        
        conn.close()
        
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
            }
            QLabel {
                color: #2c2c2c;
                font-weight: 600;
                font-size: 13px;
            }
            QLineEdit, QComboBox, QDateEdit, QTextEdit {
                background-color: #fafafa;
                border: 1px solid #e0e0e0;
                border-radius: 5px;
                padding: 8px 10px;
                font-size: 13px;
            }
            QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QTextEdit:focus {
                border: 2px solid #2d7a5f;
                background-color: #ffffff;
            }
            QPushButton {
                background-color: #2d7a5f;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 9px 18px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #246651;
            }
            QPushButton#secondary {
                background-color: #8b6f47;
            }
            QPushButton#secondary:hover {
                background-color: #735a38;
            }
        """)
        
        # Main layout with scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel(f"✏️ Edit Job Card: {job_data.get('job_no', 'N/A')}")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setStyleSheet("color: #2d7a5f; padding: 10px;")
        layout.addWidget(title)
        
        # Form grid
        grid = QGridLayout()
        grid.setHorizontalSpacing(15)
        grid.setVerticalSpacing(12)
        
        # Job No (read-only)
        self.job_no_input = QLineEdit(job_data.get('job_no', ''))
        self.job_no_input.setReadOnly(True)
        self.job_no_input.setStyleSheet("background-color: #f0f0f0; font-weight: 600;")
        
        # Driver
        self.driver_input = QComboBox()
        self.driver_input.setEditable(True)
        self.driver_input.addItems(self.drivers)
        self.driver_input.setCurrentText(job_data.get('driver', ''))
        
        # Company No
        self.company_no_input = QComboBox()
        self.company_no_input.setEditable(True)
        company_nos = list(set([v[0] for v in self.vehicles if v[0]]))
        self.company_no_input.addItems(company_nos)
        self.company_no_input.setCurrentText(job_data.get('company_no', ''))
        self.company_no_input.currentTextChanged.connect(self.auto_fill_from_company)
        
        # Site
        self.site_input = QComboBox()
        self.site_input.addItems(self.sites)
        self.site_input.setCurrentText(job_data.get('site', ''))
        
        # Vehicle No
        self.vehicle_input = QComboBox()
        self.vehicle_input.setEditable(True)
        vehicle_nos = list(set([v[1] for v in self.vehicles if v[1] and v[1] != '-']))
        self.vehicle_input.addItems(vehicle_nos)
        self.vehicle_input.setCurrentText(job_data.get('vehicle_no', ''))
        self.vehicle_input.currentTextChanged.connect(self.auto_fill_from_vehicle)
        
        # Section
        self.section_input = QComboBox()
        self.section_input.addItems(self.sections)
        self.section_input.setCurrentText(job_data.get('section', ''))
        
        # Make, Model, Type
        self.make_input = QLineEdit(job_data.get('make', ''))
        self.make_input.setReadOnly(True)
        self.model_input = QLineEdit(job_data.get('model', ''))
        self.model_input.setReadOnly(True)
        self.type_input = QLineEdit(job_data.get('type', ''))
        self.type_input.setReadOnly(True)
        
        # Hr/Km
        self.hr_km_input = QLineEdit(job_data.get('hr_km', ''))
        
        # Dates
        self.start_date_input = QDateEdit()
        self.start_date_input.setCalendarPopup(True)
        self.start_date_input.setDisplayFormat("yyyy-MM-dd")
        start_date_str = job_data.get('start_date', '')
        if start_date_str:
            self.start_date_input.setDate(QDate.fromString(start_date_str, "yyyy-MM-dd"))
        
        self.end_date_input = QDateEdit()
        self.end_date_input.setCalendarPopup(True)
        self.end_date_input.setDisplayFormat("yyyy-MM-dd")
        end_date_str = job_data.get('end_date', '')
        if end_date_str:
            self.end_date_input.setDate(QDate.fromString(end_date_str, "yyyy-MM-dd"))
        
        # Add to grid - New Order
        row = 0
        grid.addWidget(QLabel("Job No:"), row, 0)
        grid.addWidget(self.job_no_input, row, 1)
        grid.addWidget(QLabel("Driver Name:"), row, 2)
        grid.addWidget(self.driver_input, row, 3)
        
        row += 1
        grid.addWidget(QLabel("Company No:"), row, 0)
        grid.addWidget(self.company_no_input, row, 1)
        grid.addWidget(QLabel("Site:"), row, 2)
        grid.addWidget(self.site_input, row, 3)
        
        row += 1
        grid.addWidget(QLabel("Vehicle No:"), row, 0)
        grid.addWidget(self.vehicle_input, row, 1)
        grid.addWidget(QLabel("Section:"), row, 2)
        grid.addWidget(self.section_input, row, 3)
        
        row += 1
        grid.addWidget(QLabel("Make:"), row, 0)
        grid.addWidget(self.make_input, row, 1)
        grid.addWidget(QLabel("Hr/Km Reading:"), row, 2)
        grid.addWidget(self.hr_km_input, row, 3)
        
        row += 1
        grid.addWidget(QLabel("Model:"), row, 0)
        grid.addWidget(self.model_input, row, 1)
        grid.addWidget(QLabel("Start Date:"), row, 2)
        grid.addWidget(self.start_date_input, row, 3)
        
        row += 1
        grid.addWidget(QLabel("Type:"), row, 0)
        grid.addWidget(self.type_input, row, 1)
        grid.addWidget(QLabel("End Date:"), row, 2)
        grid.addWidget(self.end_date_input, row, 3)
        
        layout.addLayout(grid)
        
        # Description
        desc_label = QLabel("📝 Job Description:")
        desc_label.setStyleSheet("color: #2d7a5f; font-size: 14px; padding-top: 10px;")
        layout.addWidget(desc_label)
        self.description_input = QTextEdit()
        self.description_input.setPlainText(job_data.get('description', ''))
        self.description_input.setMaximumHeight(120)
        layout.addWidget(self.description_input)
        
        # Spare parts button
        spare_btn_layout = QHBoxLayout()
        self.spare_parts_data = job_data.get('spare_parts', '[]')
        edit_spare_btn = QPushButton("🔧 Edit Spare Parts")
        edit_spare_btn.setObjectName("secondary")
        edit_spare_btn.clicked.connect(self.edit_spare_parts)
        spare_btn_layout.addWidget(edit_spare_btn)
        spare_btn_layout.addStretch()
        layout.addLayout(spare_btn_layout)
        
        scroll.setWidget(container)
        
        # Main dialog layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(scroll)
        
        # Dialog buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.save_changes)
        button_box.rejected.connect(self.reject)
        main_layout.addWidget(button_box)
        
        self.setLayout(main_layout)
    
    def auto_fill_from_company(self, company_no):
        if not company_no:
            self.vehicle_input.clear()
            self.make_input.clear()
            self.model_input.clear()
            self.type_input.clear()
            return
        
        # Filter vehicles for this company
        company_vehicles = [v for v in self.vehicles if v[0] == company_no]
        
        # Update vehicle dropdown
        self.vehicle_input.blockSignals(True)
        self.vehicle_input.clear()
        
        if company_vehicles:
            for vehicle in company_vehicles:
                if vehicle[1] and vehicle[1] != '-':
                    self.vehicle_input.addItem(vehicle[1])
            
            # Auto-fill with first vehicle
            first_vehicle = company_vehicles[0]
            self.vehicle_input.setCurrentIndex(0)
            self.make_input.setText(first_vehicle[2] or '')
            self.model_input.setText(first_vehicle[3] or '')
            self.type_input.setText(first_vehicle[4] or '')
        else:
            self.make_input.clear()
            self.model_input.clear()
            self.type_input.clear()
        
        self.vehicle_input.blockSignals(False)
    
    def auto_fill_from_vehicle(self, number):
        if not number:
            return
        for v in self.vehicles:
            if v[1] == number:
                self.make_input.setText(v[2] or '')
                self.model_input.setText(v[3] or '')
                self.type_input.setText(v[4] or '')
                break
    
    def edit_spare_parts(self):
        dialog = SparePartEditDialog(self.spare_parts_data, self)
        if dialog.exec():
            self.spare_parts_data = dialog.get_data()
    
    def save_changes(self):
        if not self.company_no_input.currentText().strip():
            QMessageBox.warning(self, "Missing Field", "Company No is required.")
            return
        
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            
            c.execute("""
                UPDATE job_cards SET
                    company_no=?, vehicle_no=?, driver=?, make=?, model=?, type=?,
                    site=?, section=?, hr_km=?, start_date=?, end_date=?,
                    description=?, spare_parts=?
                WHERE id=?
            """, (
                self.company_no_input.currentText().strip(),
                self.vehicle_input.currentText().strip(),
                self.driver_input.currentText().strip(),
                self.make_input.text().strip(),
                self.model_input.text().strip(),
                self.type_input.text().strip(),
                self.site_input.currentText(),
                self.section_input.currentText(),
                self.hr_km_input.text().strip(),
                self.start_date_input.date().toString("yyyy-MM-dd"),
                self.end_date_input.date().toString("yyyy-MM-dd"),
                self.description_input.toPlainText(),
                self.spare_parts_data,
                self.job_id
            ))
            
            conn.commit()
            conn.close()
            
            QMessageBox.information(self, "Success ✅", "Job card updated successfully!")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update job card:\n{str(e)}")


class JobCardDetailDialog(QDialog):
    def __init__(self, job_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Job Card Details - {job_data.get('job_no', 'N/A')}")
        self.setMinimumSize(1000, 800)
        
        self.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
            }
            QTextEdit {
                background-color: #fafafa;
                border: 1px solid #e0e0e0;
                border-radius: 5px;
                padding: 15px;
            }
            QPushButton {
                background-color: #2d7a5f;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: 600;
                min-height: 36px;
            }
            QPushButton:hover {
                background-color: #246651;
            }
            QPushButton#secondary {
                background-color: #8b6f47;
            }
            QPushButton#secondary:hover {
                background-color: #735a38;
            }
            QTabWidget::pane {
                border: 1px solid #e0e0e0;
            }
            QTabBar::tab {
                background-color: #f5f5f5;
                border: 1px solid #e0e0e0;
                padding: 8px 15px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #2d7a5f;
                color: white;
                border: 1px solid #2d7a5f;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)
        
        # Header with Job No and Dates
        header_layout = QHBoxLayout()
        title = QLabel(f"📋 Job Card: {job_data.get('job_no', 'N/A')}")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setStyleSheet("color: #2d7a5f;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        date_info = QLabel(f"📅 {job_data.get('start_date', 'N/A')} → {job_data.get('end_date', 'N/A')}")
        date_info.setFont(QFont("Segoe UI", 11))
        date_info.setStyleSheet("color: #666; padding: 8px 15px; background-color: #f5f5f5; border-radius: 5px;")
        header_layout.addWidget(date_info)
        layout.addLayout(header_layout)
        
        # Main Info Grid
        info_layout = QGridLayout()
        info_layout.setSpacing(15)
        
        info_cards = [
            ("Driver", job_data.get('driver', 'N/A'), "👤"),
            ("Company No", job_data.get('company_no', 'N/A'), "🏢"),
            ("Vehicle No", job_data.get('vehicle_no', 'N/A'), "🚗"),
            ("Make/Model", f"{job_data.get('make', 'N/A')} / {job_data.get('model', 'N/A')}", "⚙️"),
            ("Site", job_data.get('site', 'N/A'), "📍"),
            ("Section", job_data.get('section', 'N/A'), "📋"),
        ]
        
        for idx, (label, value, icon) in enumerate(info_cards):
            card = QFrame()
            card.setStyleSheet("background-color: #f9f9f9; border-radius: 6px; border: 1px solid #e0e0e0; padding: 12px;")
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(10, 8, 10, 8)
            card_layout.setSpacing(4)
            
            label_widget = QLabel(f"{icon} {label}")
            label_widget.setFont(QFont("Segoe UI", 11, QFont.Bold))
            label_widget.setStyleSheet("color: #2d7a5f;")
            value_widget = QLabel(value)
            value_widget.setFont(QFont("Segoe UI", 12, QFont.Bold))
            value_widget.setStyleSheet("color: #1a1a1a;")
            
            card_layout.addWidget(label_widget)
            card_layout.addWidget(value_widget)
            
            info_layout.addWidget(card, idx // 3, idx % 3)
        
        layout.addLayout(info_layout)
        
        # Tab widget for detailed info
        tabs = QTabWidget()
        
        # ==== TAB 1: Job Description ====
        desc_tab = QWidget()
        desc_layout = QVBoxLayout(desc_tab)
        desc_label = QLabel("📝 Job Description:")
        desc_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        desc_label.setStyleSheet("color: #2d7a5f;")
        desc_layout.addWidget(desc_label)
        desc_text = QTextEdit()
        desc_text.setPlainText(job_data.get('description', 'No description provided.'))
        desc_text.setReadOnly(True)
        desc_text.setMinimumHeight(120)
        desc_layout.addWidget(desc_text)
        tabs.addTab(desc_tab, "📝 Description")
        
        # ==== TAB 2: Spare Parts ====
        spare_tab = QWidget()
        spare_layout = QVBoxLayout(spare_tab)
        spare_label = QLabel("🔧 Spare Parts & Materials:")
        spare_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        spare_label.setStyleSheet("color: #2d7a5f;")
        spare_layout.addWidget(spare_label)
        
        spare_parts = job_data.get('spare_parts', '[]')
        try:
            parts = json.loads(spare_parts) if spare_parts else []
            if parts:
                spare_text = "<table border='1' cellpadding='10' style='border-collapse: collapse; width: 100%; margin-top: 10px; background-color: #ffffff;'>"
                spare_text += "<tr style='background-color: #2d7a5f; color: white; font-weight: 700;'>"
                spare_text += "<th style='text-align: center; width: 40px;'>#</th>"
                spare_text += "<th style='text-align: left;'>Description</th>"
                spare_text += "<th style='text-align: center; width: 80px;'>Qty</th>"
                spare_text += "<th style='text-align: center; width: 60px;'>Unit</th>"
                spare_text += "<th style='text-align: right; width: 100px;'>Unit Price</th>"
                spare_text += "<th style='text-align: right; width: 100px;'>Total</th>"
                spare_text += "</tr>"
                
                grand_total = 0.0
                for idx, part in enumerate(parts, 1):
                    total_val = part.get('total', '0')
                    try:
                        grand_total += float(total_val)
                    except:
                        pass
                    
                    bg_color = "#f9f9f9" if idx % 2 == 0 else "#ffffff"
                    spare_text += f"<tr style='background-color: {bg_color};'>"
                    spare_text += f"<td style='text-align: center; font-weight: 600;'>{idx}</td>"
                    spare_text += f"<td>{part.get('description', '')}</td>"
                    spare_text += f"<td style='text-align: center;'>{part.get('quantity', '')}</td>"
                    spare_text += f"<td style='text-align: center;'>{part.get('unit', '')}</td>"
                    spare_text += f"<td style='text-align: right;'>Rs. {float(part.get('unit_price', 0)):,.2f}</td>"
                    spare_text += f"<td style='text-align: right; font-weight: 600;'>Rs. {float(total_val):,.2f}</td>"
                    spare_text += "</tr>"
                
                spare_text += f"<tr style='background-color: #e8f4f0; font-weight: 700;'>"
                spare_text += f"<td colspan='5' style='text-align: right; padding: 12px;'>Spare Parts Total:</td>"
                spare_text += f"<td style='text-align: right; color: #2d7a5f; font-size: 14px;'>Rs. {grand_total:,.2f}</td>"
                spare_text += "</tr>"
                spare_text += "</table>"
                
                spare_display = QTextEdit()
                spare_display.setHtml(spare_text)
                spare_display.setReadOnly(True)
                spare_layout.addWidget(spare_display)
            else:
                no_parts = QLabel("No spare parts recorded for this job card.")
                no_parts.setStyleSheet("color: #666; font-style: italic; padding: 20px;")
                spare_layout.addWidget(no_parts)
        except:
            error_label = QLabel("Error loading spare parts data.")
            error_label.setStyleSheet("color: #c84343;")
            spare_layout.addWidget(error_label)
        
        tabs.addTab(spare_tab, "🔧 Spare Parts")
        
        # ==== TAB 3: Labour Works ====
        labour_tab = QWidget()
        labour_layout = QVBoxLayout(labour_tab)
        labour_label = QLabel("👷 Labour Works:")
        labour_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        labour_label.setStyleSheet("color: #2d7a5f;")
        labour_layout.addWidget(labour_label)
        
        labour_works = job_data.get('labour_works', '[]')
        try:
            works = json.loads(labour_works) if labour_works else []
            if works:
                labour_text = "<table border='1' cellpadding='10' style='border-collapse: collapse; width: 100%; margin-top: 10px; background-color: #ffffff;'>"
                labour_text += "<tr style='background-color: #2d7a5f; color: white; font-weight: 700;'>"
                labour_text += "<th style='text-align: center; width: 40px;'>#</th>"
                labour_text += "<th style='text-align: left;'>Work Description</th>"
                labour_text += "<th style='text-align: center; width: 80px;'>Hours</th>"
                labour_text += "<th style='text-align: left;'>Labour Assigned</th>"
                labour_text += "<th style='text-align: right; width: 120px;'>Cost</th>"
                labour_text += "</tr>"
                
                total_hours = 0.0
                total_labour_cost = 0.0
                for idx, work in enumerate(works, 1):
                    labour_list = []
                    try:
                        labour_json = work.get('labour_list', '[]')
                        labour_items = json.loads(labour_json) if isinstance(labour_json, str) else labour_json
                        for item in labour_items:
                            labour_list.append(f"{item.get('name', '')} ({item.get('grade', '')})")
                    except:
                        pass
                    
                    hours = float(work.get('hours', 0))
                    cost = float(work.get('work_cost', 0))
                    total_hours += hours
                    total_labour_cost += cost
                    
                    bg_color = "#f9f9f9" if idx % 2 == 0 else "#ffffff"
                    labour_text += f"<tr style='background-color: {bg_color};'>"
                    labour_text += f"<td style='text-align: center; font-weight: 600;'>{idx}</td>"
                    labour_text += f"<td>{work.get('description', '')}</td>"
                    labour_text += f"<td style='text-align: center;'>{hours:.2f}</td>"
                    labour_text += f"<td>{', '.join(labour_list)}</td>"
                    labour_text += f"<td style='text-align: right; font-weight: 600;'>Rs. {cost:,.2f}</td>"
                    labour_text += "</tr>"
                
                labour_text += f"<tr style='background-color: #e8f4f0; font-weight: 700;'>"
                labour_text += f"<td colspan='2' style='text-align: right; padding: 12px;'>Total Hours: {total_hours:.2f}</td>"
                labour_text += f"<td colspan='2' style='text-align: right; padding: 12px;'>Labour Cost Total:</td>"
                labour_text += f"<td style='text-align: right; color: #2d7a5f; font-size: 14px;'>Rs. {total_labour_cost:,.2f}</td>"
                labour_text += "</tr>"
                labour_text += "</table>"
                
                labour_display = QTextEdit()
                labour_display.setHtml(labour_text)
                labour_display.setReadOnly(True)
                labour_layout.addWidget(labour_display)
            else:
                no_labour = QLabel("No labour works recorded for this job card.")
                no_labour.setStyleSheet("color: #666; font-style: italic; padding: 20px;")
                labour_layout.addWidget(no_labour)
        except:
            error_label = QLabel("Error loading labour works data.")
            error_label.setStyleSheet("color: #c84343;")
            labour_layout.addWidget(error_label)
        
        tabs.addTab(labour_tab, "👷 Labour Works")
        
        layout.addWidget(tabs)
        
        # ==== COST SUMMARY ====
        summary_frame = QFrame()
        summary_frame.setStyleSheet("background-color: #e8f4f0; border-radius: 8px; border: 2px solid #2d7a5f; padding: 15px;")
        summary_layout = QHBoxLayout(summary_frame)
        summary_layout.setContentsMargins(20, 15, 20, 15)
        
        # Spare parts total
        spare_total = 0.0
        try:
            parts = json.loads(spare_parts) if spare_parts else []
            for part in parts:
                spare_total += float(part.get('total', 0))
        except:
            pass
        
        # Labour total
        labour_total = 0.0
        try:
            works = json.loads(labour_works) if labour_works else []
            for work in works:
                labour_total += float(work.get('work_cost', 0))
        except:
            pass
        
        grand_total = spare_total + labour_total
        
        spare_label = QLabel(f"Spare Parts: Rs. {spare_total:,.2f}")
        spare_label.setFont(QFont("Segoe UI", 12))
        spare_label.setStyleSheet("color: #2d7a5f; font-weight: 600;")
        
        labour_label = QLabel(f"Labour Cost: Rs. {labour_total:,.2f}")
        labour_label.setFont(QFont("Segoe UI", 12))
        labour_label.setStyleSheet("color: #2d7a5f; font-weight: 600;")
        
        grand_label = QLabel(f"GRAND TOTAL: Rs. {grand_total:,.2f}")
        grand_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        grand_label.setStyleSheet("color: #2d7a5f;")
        
        summary_layout.addWidget(spare_label)
        summary_layout.addSpacing(30)
        summary_layout.addWidget(labour_label)
        summary_layout.addStretch()
        summary_layout.addWidget(grand_label)
        
        layout.addWidget(summary_frame)
        
        # Close button
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        close_btn = QPushButton("✓ Close")
        close_btn.setFixedWidth(120)
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)


class JobCardRecordsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent

        # === UI Colors ===
        bg_color = "#f5f5f5"
        card_color = "#ffffff"
        accent_color = "#2d7a5f"
        text_color = "#2c2c2c"
        border_color = "#e0e0e0"
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
            QLabel#section_label {{
                font-weight: 500;
                color: #666;
                font-size: 12px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            QFrame#filter_card {{
                background-color: {card_color};
                border-radius: 6px;
                padding: 6px;
                border: 1px solid {border_color};
            }}
            QLineEdit, QComboBox, QDateEdit {{
                background-color: #fafafa;
                border: 1px solid {border_color};
                color: {text_color};
                padding: 6px 8px;
                border-radius: 4px;
                min-height: 30px;
                font-size: 12px;
            }}
            QLineEdit:focus, QComboBox:focus, QDateEdit:focus {{
                border: 2px solid {accent_color};
                background-color: #ffffff;
                outline: none;
            }}
            QPushButton {{
                background-color: {accent_color};
                border-radius: 4px;
                padding: 8px 12px;
                color: white;
                font-weight: 600;
                min-height: 30px;
                border: none;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: #246651;
            }}
            QPushButton:pressed {{
                background-color: #1f5443;
            }}
            QPushButton#secondary {{
                background-color: {secondary_color};
            }}
            QPushButton#secondary:hover {{
                background-color: #735a38;
            }}
            QPushButton#secondary:pressed {{
                background-color: #654b31;
            }}
            QPushButton#danger {{
                background-color: {danger_color};
            }}
            QPushButton#danger:hover {{
                background-color: #b03636;
            }}
            QPushButton#danger:pressed {{
                background-color: #992e2e;
            }}
            QPushButton#nav {{
                background-color: {secondary_color};
                padding: 8px 12px;
                min-height: 30px;
                font-size: 12px;
            }}
            QPushButton#nav:hover {{
                background-color: #735a38;
            }}
            QTableWidget {{
                background-color: {card_color};
                border: 1px solid {border_color};
                color: {text_color};
                gridline-color: #f0f0f0;
                border-radius: 6px;
                font-size: 13px;
            }}
            QTableWidget::item {{
                padding: 10px 8px;
                border: none;
                color: {text_color};
            }}
            QTableWidget::item:selected {{
                background-color: #e8f4f0;
                color: {text_color};
                font-weight: 500;
            }}
            QHeaderView::section {{
                background-color: {accent_color};
                color: white;
                padding: 10px 8px;
                border: none;
                font-weight: 700;
                font-size: 12px;
                text-transform: uppercase;
                letter-spacing: 0.3px;
                font-weight: 700;
                font-size: 12px;
            }}
            QTableWidget::item {{
                padding: 8px;
            }}
            QTableWidget::item:selected {{
                background-color: #c8e6c9;
                color: #1a1a1a;
            }}
            QCheckBox {{
                color: {text_color};
                spacing: 8px;
            }}
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(16, 12, 16, 16)
        layout.setSpacing(8)
        
        # === Header: Title and Back Button ===
        header_layout, title_label, back_btn_top = create_page_header("📋 Job Card Records")
        back_btn_top.clicked.connect(self.go_back)
        layout.addLayout(header_layout)



        # === Compact Filter Card ===
        filter_card = QFrame()
        filter_card.setObjectName("filter_card")
        filter_layout = QVBoxLayout(filter_card)
        filter_layout.setContentsMargins(8, 8, 8, 8)
        filter_layout.setSpacing(6)
        
        # Row 1: Search + Site + Section
        filter_row1 = QHBoxLayout()
        filter_row1.setSpacing(6)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search...")
        self.search_input.setMaximumHeight(32)
        filter_row1.addWidget(self.search_input, 2)
        
        self.site_filter = QComboBox()
        self.site_filter.addItem("All Sites")
        self.site_filter.setMaximumHeight(32)
        self.site_filter.setMaximumWidth(140)
        filter_row1.addWidget(self.site_filter)
        
        self.section_filter = QComboBox()
        self.section_filter.addItem("All Sections")
        self.section_filter.setMaximumHeight(32)
        self.section_filter.setMaximumWidth(140)
        filter_row1.addWidget(self.section_filter)
        
        filter_layout.addLayout(filter_row1)
        
        # Row 2: Date + Cost Range
        filter_row2 = QHBoxLayout()
        filter_row2.setSpacing(6)
        
        self.date_filter_type = QComboBox()
        self.date_filter_type.addItems(["All Dates", "Date Range", "This Month", "Last Month", "Last 3 Mo", "Last 6 Mo", "This Year"])
        self.date_filter_type.setMaximumHeight(32)
        self.date_filter_type.setMaximumWidth(130)
        self.date_filter_type.currentTextChanged.connect(self.on_date_filter_changed)
        filter_row2.addWidget(self.date_filter_type)
        
        self.start_date = QDateEdit(QDate.currentDate().addDays(-30))
        self.start_date.setCalendarPopup(True)
        self.start_date.setDisplayFormat("yyyy-MM-dd")
        self.start_date.setVisible(False)
        self.start_date.setMaximumHeight(32)
        self.start_date.setMaximumWidth(110)
        filter_row2.addWidget(self.start_date)
        
        self.end_date = QDateEdit(QDate.currentDate())
        self.end_date.setCalendarPopup(True)
        self.end_date.setDisplayFormat("yyyy-MM-dd")
        self.end_date.setVisible(False)
        self.end_date.setMaximumHeight(32)
        self.end_date.setMaximumWidth(110)
        filter_row2.addWidget(self.end_date)
        
        # Cost Range
        cost_label = QLabel("Cost:")
        cost_label.setMaximumWidth(40)
        filter_row2.addWidget(cost_label)
        
        self.min_cost = QDoubleSpinBox()
        self.min_cost.setPrefix("Rs. ")
        self.min_cost.setMinimum(0)
        self.min_cost.setMaximum(9999999)
        self.min_cost.setValue(0)
        self.min_cost.setMaximumHeight(32)
        self.min_cost.setMaximumWidth(100)
        filter_row2.addWidget(self.min_cost)
        
        self.max_cost = QDoubleSpinBox()
        self.max_cost.setPrefix("Rs. ")
        self.max_cost.setMinimum(0)
        self.max_cost.setMaximum(9999999)
        self.max_cost.setValue(9999999)
        self.max_cost.setMaximumHeight(32)
        self.max_cost.setMaximumWidth(100)
        filter_row2.addWidget(self.max_cost)
        
        filter_row2.addStretch()
        
        filter_layout.addLayout(filter_row2)
        
        # Row 3: Action buttons (Compact)
        filter_row3 = QHBoxLayout()
        filter_row3.setSpacing(3)
        
        btn_apply = QPushButton("Apply")
        btn_apply.setMaximumHeight(28)
        btn_apply.setMaximumWidth(70)
        btn_apply.clicked.connect(self.apply_filters)
        filter_row3.addWidget(btn_apply)
        
        btn_clear = QPushButton("Clear")
        btn_clear.setObjectName("secondary")
        btn_clear.setMaximumHeight(28)
        btn_clear.setMaximumWidth(60)
        btn_clear.clicked.connect(self.clear_filters)
        filter_row3.addWidget(btn_clear)
        
        btn_export = QPushButton("Export")
        btn_export.setObjectName("secondary")
        btn_export.setMaximumHeight(28)
        btn_export.setMaximumWidth(70)
        btn_export.clicked.connect(self.export_data)
        filter_row3.addWidget(btn_export)
        
        filter_row3.addStretch()
        
        filter_layout.addLayout(filter_row3)
        layout.addWidget(filter_card)

        # === Navigation & Action Buttons (Compact) ===
        action_bar = QHBoxLayout()
        action_bar.setSpacing(3)
        action_bar.setContentsMargins(0, 0, 0, 0)
        
        # Navigation buttons
        btn_new_job = QPushButton("New Job")
        btn_new_job.setObjectName("nav")
        btn_new_job.setMaximumHeight(28)
        btn_new_job.setMaximumWidth(90)
        btn_new_job.setCursor(Qt.PointingHandCursor)
        btn_new_job.clicked.connect(self.go_to_job_card)
        
        btn_data_manager = QPushButton("Manager")
        btn_data_manager.setObjectName("nav")
        btn_data_manager.setMaximumHeight(28)
        btn_data_manager.setMaximumWidth(80)
        btn_data_manager.setCursor(Qt.PointingHandCursor)
        btn_data_manager.clicked.connect(self.go_to_data_manager)
        
        action_bar.addWidget(btn_new_job)
        action_bar.addWidget(btn_data_manager)
        action_bar.addSpacing(8)
        
        # Record actions
        btn_view = QPushButton("View")
        btn_view.setMaximumHeight(28)
        btn_view.setMaximumWidth(60)
        btn_view.setCursor(Qt.PointingHandCursor)
        btn_view.clicked.connect(self.view_details)
        
        btn_edit = QPushButton("Edit")
        btn_edit.setObjectName("secondary")
        btn_edit.setMaximumHeight(28)
        btn_edit.setMaximumWidth(60)
        btn_edit.setCursor(Qt.PointingHandCursor)
        btn_edit.clicked.connect(self.edit_record)
        
        btn_delete = QPushButton("Delete")
        btn_delete.setObjectName("danger")
        btn_delete.setMaximumHeight(28)
        btn_delete.setMaximumWidth(70)
        btn_delete.setCursor(Qt.PointingHandCursor)
        btn_delete.clicked.connect(self.delete_selected)
        
        btn_refresh = QPushButton("Refresh")
        btn_refresh.setMaximumHeight(28)
        btn_refresh.setMaximumWidth(75)
        btn_refresh.setCursor(Qt.PointingHandCursor)
        btn_refresh.clicked.connect(self.load_records)

        action_bar.addWidget(btn_view)
        action_bar.addWidget(btn_edit)
        action_bar.addWidget(btn_delete)
        action_bar.addWidget(btn_refresh)
        action_bar.addStretch()
        
        layout.addLayout(action_bar)

        # === Table ===
        self.table = QTableWidget()
        self.table.setColumnCount(11)
        self.table.setHorizontalHeaderLabels([
            "ID", "Job No", "Company No", "Vehicle No", "Driver",
            "Make", "Model", "Type", "Site", "Section", "Start Date"
        ])
        self.table.setColumnHidden(0, True)
        self.table.setSortingEnabled(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.doubleClicked.connect(self.view_details)
        layout.addWidget(self.table, 1)  # Give table maximum space

        self.setLayout(layout)
        self.load_filter_options()
        self.load_records()

    def on_date_filter_changed(self, filter_type):
        """Show/hide date inputs based on filter type"""
        if "Date Range" in filter_type:
            self.start_date.setVisible(True)
            self.end_date.setVisible(True)
        else:
            self.start_date.setVisible(False)
            self.end_date.setVisible(False)

    def load_filter_options(self):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        # Load sites
        c.execute("SELECT DISTINCT name FROM sites ORDER BY name")
        for row in c.fetchall():
            self.site_filter.addItem(row[0])
        
        # Load sections
        c.execute("SELECT DISTINCT name FROM sections ORDER BY name")
        for row in c.fetchall():
            self.section_filter.addItem(row[0])
        
        conn.close()

    def load_records(self):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("""SELECT id, job_no, company_no, vehicle_no, driver, make, model, type, site, section, start_date,
                     spare_parts, labour_works
                     FROM job_cards ORDER BY id DESC""")
        rows = c.fetchall()
        conn.close()
        
        # Extract table data (first 11 columns)
        table_rows = [row[:11] for row in rows]
        self.populate_table(table_rows)

    def apply_filters(self):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        query = """SELECT id, job_no, company_no, vehicle_no, driver, make, model, type, site, section, start_date,
                   spare_parts, labour_works
                   FROM job_cards WHERE 1=1"""
        params = []
        
        # Search keyword
        keyword = self.search_input.text().strip()
        if keyword:
            query += " AND (job_no LIKE ? OR company_no LIKE ? OR vehicle_no LIKE ? OR driver LIKE ?)"
            params.extend([f"%{keyword}%"] * 4)
        
        # Site filter
        site_filter = self.site_filter.currentText()
        if not site_filter.startswith("📍"):
            site_filter = site_filter.replace("📍 ", "")
        if site_filter != "All Sites":
            query += " AND site = ?"
            params.append(site_filter)
        
        # Section filter
        section_filter = self.section_filter.currentText()
        if not section_filter.startswith("📋"):
            section_filter = section_filter.replace("📋 ", "")
        if section_filter != "All Sections":
            query += " AND section = ?"
            params.append(section_filter)
        
        # Date filter
        filter_type = self.date_filter_type.currentText()
        filter_type = filter_type.replace("📅 ", "")  # Remove emoji
        current_date = QDate.currentDate()
        
        if "Date Range" in filter_type:
            query += " AND start_date BETWEEN ? AND ?"
            params.append(self.start_date.date().toString("yyyy-MM-dd"))
            params.append(self.end_date.date().toString("yyyy-MM-dd"))
        elif "This Month" in filter_type:
            first_day = QDate(current_date.year(), current_date.month(), 1)
            query += " AND start_date BETWEEN ? AND ?"
            params.append(first_day.toString("yyyy-MM-dd"))
            params.append(current_date.toString("yyyy-MM-dd"))
        elif "Last Month" in filter_type:
            last_month = current_date.addMonths(-1)
            first_day = QDate(last_month.year(), last_month.month(), 1)
            last_day = QDate(last_month.year(), last_month.month(), last_month.daysInMonth())
            query += " AND start_date BETWEEN ? AND ?"
            params.append(first_day.toString("yyyy-MM-dd"))
            params.append(last_day.toString("yyyy-MM-dd"))
        elif "Last 3 Months" in filter_type:
            three_months_ago = current_date.addMonths(-3)
            query += " AND start_date BETWEEN ? AND ?"
            params.append(three_months_ago.toString("yyyy-MM-dd"))
            params.append(current_date.toString("yyyy-MM-dd"))
        elif "Last 6 Months" in filter_type:
            six_months_ago = current_date.addMonths(-6)
            query += " AND start_date BETWEEN ? AND ?"
            params.append(six_months_ago.toString("yyyy-MM-dd"))
            params.append(current_date.toString("yyyy-MM-dd"))
        elif "This Year" in filter_type:
            first_day = QDate(current_date.year(), 1, 1)
            query += " AND start_date BETWEEN ? AND ?"
            params.append(first_day.toString("yyyy-MM-dd"))
            params.append(current_date.toString("yyyy-MM-dd"))
        
        query += " ORDER BY id DESC"
        
        c.execute(query, params)
        all_rows = c.fetchall()
        conn.close()
        
        # Filter by cost range
        min_cost = self.min_cost.value()
        max_cost = self.max_cost.value()
        
        filtered_rows = []
        for row in all_rows:
            total_cost = 0.0
            try:
                spare_parts = json.loads(row[11]) if row[11] else []
                for part in spare_parts:
                    total_cost += float(part.get('total', 0))
            except:
                pass
            try:
                labour_works = json.loads(row[12]) if row[12] else []
                for work in labour_works:
                    total_cost += float(work.get('work_cost', 0))
            except:
                pass
            
            if min_cost <= total_cost <= max_cost:
                filtered_rows.append(row[:11])
        
        self.populate_table(filtered_rows)

    def clear_filters(self):
        self.search_input.clear()
        self.site_filter.setCurrentIndex(0)
        self.section_filter.setCurrentIndex(0)
        self.date_filter_type.setCurrentIndex(0)
        self.start_date.setDate(QDate.currentDate().addDays(-30))
        self.end_date.setDate(QDate.currentDate())
        self.min_cost.setValue(0)
        self.max_cost.setValue(9999999)
        self.load_records()
    
    def export_data(self):
        """Export filtered data to CSV"""
        try:
            csv_content = "Job No,Company No,Vehicle No,Driver,Make,Model,Type,Site,Section,Start Date,Spare Parts Cost,Labour Cost,Grand Total\n"
            
            for row in range(self.table.rowCount()):
                job_no = self.table.item(row, 1).text()
                company_no = self.table.item(row, 2).text()
                vehicle_no = self.table.item(row, 3).text()
                driver = self.table.item(row, 4).text()
                make = self.table.item(row, 5).text()
                model = self.table.item(row, 6).text()
                type_val = self.table.item(row, 7).text()
                site = self.table.item(row, 8).text()
                section = self.table.item(row, 9).text()
                start_date = self.table.item(row, 10).text()
                
                # Get costs from database
                record_id = int(self.table.item(row, 0).text())
                conn = sqlite3.connect(DB_PATH)
                c = conn.cursor()
                c.execute("SELECT spare_parts, labour_works FROM job_cards WHERE id=?", (record_id,))
                data = c.fetchone()
                conn.close()
                
                spare_cost = 0.0
                labour_cost = 0.0
                
                try:
                    spare_parts = json.loads(data[0]) if data[0] else []
                    for part in spare_parts:
                        spare_cost += float(part.get('total', 0))
                except:
                    pass
                
                try:
                    labour_works = json.loads(data[1]) if data[1] else []
                    for work in labour_works:
                        labour_cost += float(work.get('work_cost', 0))
                except:
                    pass
                
                grand_total = spare_cost + labour_cost
                
                csv_content += f'"{job_no}","{company_no}","{vehicle_no}","{driver}","{make}","{model}","{type_val}","{site}","{section}","{start_date}",{spare_cost:.2f},{labour_cost:.2f},{grand_total:.2f}\n'
            
            # Save to file
            from datetime import datetime
            filename = f"job_cards_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            filepath = f"/Users/darkcyph7/Documents/GitHub/Senarath_Workshop/{filename}"
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(csv_content)
            
            QMessageBox.information(self, "Export Successful ✅", f"Data exported to:\n{filename}")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export data:\n{str(e)}")

    def populate_table(self, rows):
        self.table.setRowCount(len(rows))
        for row_idx, row_data in enumerate(rows):
            for col_idx, col_data in enumerate(row_data):
                item = QTableWidgetItem(str(col_data) if col_data else "")
                item.setFlags(item.flags() ^ Qt.ItemIsEditable)
                self.table.setItem(row_idx, col_idx, item)
        
        self.table.resizeColumnsToContents()

    def view_details(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select a record to view.")
            return
        
        record_id = int(self.table.item(selected_rows[0].row(), 0).text())
        
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("""SELECT job_no, company_no, vehicle_no, driver, make, model, type, 
                     site, section, hr_km, start_date, end_date, description, spare_parts, labour_works
                     FROM job_cards WHERE id=?""", (record_id,))
        row = c.fetchone()
        conn.close()
        
        if row:
            job_data = {
                'job_no': row[0], 'company_no': row[1], 'vehicle_no': row[2],
                'driver': row[3], 'make': row[4], 'model': row[5], 'type': row[6],
                'site': row[7], 'section': row[8], 'hr_km': row[9],
                'start_date': row[10], 'end_date': row[11], 'description': row[12],
                'spare_parts': row[13], 'labour_works': row[14]
            }
            dialog = JobCardDetailDialog(job_data, self)
            dialog.exec()

    def edit_record(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select a record to edit.")
            return
        
        record_id = int(self.table.item(selected_rows[0].row(), 0).text())
        
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("""SELECT id, job_no, company_no, vehicle_no, driver, make, model, type, 
                     site, section, hr_km, start_date, end_date, description, spare_parts
                     FROM job_cards WHERE id=?""", (record_id,))
        row = c.fetchone()
        conn.close()
        
        if row:
            job_data = {
                'id': row[0], 'job_no': row[1], 'company_no': row[2], 'vehicle_no': row[3],
                'driver': row[4], 'make': row[5], 'model': row[6], 'type': row[7],
                'site': row[8], 'section': row[9], 'hr_km': row[10],
                'start_date': row[11], 'end_date': row[12], 'description': row[13],
                'spare_parts': row[14]
            }
            dialog = JobCardEditDialog(job_data, self)
            if dialog.exec():
                # Refresh the table after successful edit
                self.load_records()

    def delete_selected(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select at least one record to delete.")
            return

        confirm = QMessageBox.question(self, "Confirm Delete", 
                                      f"Are you sure you want to delete {len(selected_rows)} job card(s)?",
                                      QMessageBox.Yes | QMessageBox.No)
        if confirm != QMessageBox.Yes:
            return

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        for row in selected_rows:
            record_id = int(self.table.item(row.row(), 0).text())
            c.execute("DELETE FROM job_cards WHERE id=?", (record_id,))
        
        conn.commit()
        conn.close()

        QMessageBox.information(self, "Deleted ✅", "Selected job cards deleted successfully.")
        self.load_records()

    def go_back(self):
        if self.parent:
            self.parent.go_to_home()
    
    def go_to_job_card(self):
        """Navigate to Job Card Entry page"""
        if self.parent:
            self.parent.go_to_jobcard()
    
    def go_to_data_manager(self):
        """Navigate to Data Manager page"""
        if self.parent:
            self.parent.go_to_data_manager()