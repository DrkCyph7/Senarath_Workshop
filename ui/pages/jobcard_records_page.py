import sqlite3
import json
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QTableWidget, QTableWidgetItem, QMessageBox, QComboBox,
    QDateEdit, QCheckBox, QFrame, QDialog, QTextEdit, QGridLayout,
    QDialogButtonBox, QScrollArea
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont

DB_PATH = "ui/db/senarath.db"


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
        self.setMinimumSize(800, 650)
        
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
            }
            QPushButton:hover {
                background-color: #246651;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)
        
        # Job info
        info_text = f"""
<h2 style="color: #2d7a5f; border-bottom: 2px solid #2d7a5f; padding-bottom: 8px;">📋 Job Card: {job_data.get('job_no', 'N/A')}</h2>

<table style="width: 100%; margin-top: 15px;" cellpadding="8">
<tr>
    <td style="width: 50%; background-color: #f5f5f5; padding: 10px; border-radius: 5px;">
        <p style="margin: 5px 0;"><b>Job No:</b> {job_data.get('job_no', 'N/A')}</p>
        <p style="margin: 5px 0;"><b>Driver:</b> {job_data.get('driver', 'N/A')}</p>
        <p style="margin: 5px 0;"><b>Company No:</b> {job_data.get('company_no', 'N/A')}</p>
        <p style="margin: 5px 0;"><b>Site:</b> {job_data.get('site', 'N/A')}</p>
        <p style="margin: 5px 0;"><b>Vehicle No:</b> {job_data.get('vehicle_no', 'N/A')}</p>
        <p style="margin: 5px 0;"><b>Section:</b> {job_data.get('section', 'N/A')}</p>
    </td>
    <td style="width: 50%; background-color: #f5f5f5; padding: 10px; border-radius: 5px;">
        <p style="margin: 5px 0;"><b>Make:</b> {job_data.get('make', 'N/A')}</p>
        <p style="margin: 5px 0;"><b>Hr/Km Reading:</b> {job_data.get('hr_km', 'N/A')}</p>
        <p style="margin: 5px 0;"><b>Model:</b> {job_data.get('model', 'N/A')}</p>
        <p style="margin: 5px 0;"><b>Start Date:</b> {job_data.get('start_date', 'N/A')}</p>
        <p style="margin: 5px 0;"><b>Type:</b> {job_data.get('type', 'N/A')}</p>
        <p style="margin: 5px 0;"><b>End Date:</b> {job_data.get('end_date', 'N/A')}</p>
    </td>
</tr>
</table>

<h3 style="color: #2d7a5f; margin-top: 20px; border-bottom: 2px solid #e0e0e0; padding-bottom: 5px;">📝 Job Description:</h3>
<p style="background-color: #f9f9f9; padding: 12px; border-radius: 5px; line-height: 1.6;">{job_data.get('description', 'No description provided.')}</p>

<h3 style="color: #2d7a5f; margin-top: 20px; border-bottom: 2px solid #e0e0e0; padding-bottom: 5px;">🔧 Spare Parts & Materials Used:</h3>
        """
        
        # Parse spare parts
        spare_parts = job_data.get('spare_parts', '[]')
        try:
            parts = json.loads(spare_parts) if spare_parts else []
            if parts:
                grand_total = 0.0
                info_text += "<table border='1' cellpadding='8' style='border-collapse: collapse; width: 100%; margin-top: 10px;'>"
                info_text += "<tr style='background-color: #2d7a5f; color: white;'><th>#</th><th>Description</th><th>Ref No</th><th>Qty</th><th>Unit</th><th>Unit Price</th><th>Total</th></tr>"
                for idx, part in enumerate(parts, 1):
                    total_val = part.get('total', '0')
                    try:
                        grand_total += float(total_val)
                    except:
                        pass
                    info_text += f"<tr style='background-color: {"#f9f9f9" if idx % 2 == 0 else "#ffffff"};'>"
                    info_text += f"<td style='text-align: center;'>{idx}</td>"
                    info_text += f"<td>{part.get('description', '')}</td>"
                    info_text += f"<td>{part.get('ref_no', '')}</td>"
                    info_text += f"<td style='text-align: center;'>{part.get('quantity', '')}</td>"
                    info_text += f"<td>{part.get('unit', '')}</td>"
                    info_text += f"<td style='text-align: right;'>Rs. {part.get('unit_price', '')}</td>"
                    info_text += f"<td style='text-align: right; font-weight: 600;'>Rs. {total_val}</td></tr>"
                info_text += f"<tr style='background-color: #e8f4f0; font-weight: 700;'><td colspan='6' style='text-align: right; padding: 10px;'>Grand Total:</td><td style='text-align: right; color: #2d7a5f; font-size: 15px;'>Rs. {grand_total:,.2f}</td></tr>"
                info_text += "</table>"
            else:
                info_text += "<p style='font-style: italic; color: #666; padding: 10px;'>No spare parts recorded.</p>"
        except:
            info_text += "<p style='color: #c84343;'><i>Error loading spare parts data.</i></p>"
        
        text_display = QTextEdit()
        text_display.setHtml(info_text)
        text_display.setReadOnly(True)
        layout.addWidget(text_display)
        
        # Close button
        close_btn = QPushButton("✓ Close")
        close_btn.setFixedHeight(42)
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
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
            QLabel#title {{
                font-size: 26px;
                font-weight: 700;
                color: #1a1a1a;
            }}
            QFrame#filter_card {{
                background-color: {card_color};
                border-radius: 8px;
                padding: 16px;
                border: 1px solid {border_color};
            }}
            QLineEdit, QComboBox, QDateEdit {{
                background-color: #fafafa;
                border: 1px solid {border_color};
                color: {text_color};
                padding: 7px 10px;
                border-radius: 5px;
                min-height: 30px;
            }}
            QLineEdit:focus, QComboBox:focus, QDateEdit:focus {{
                border: 2px solid {accent_color};
                background-color: #ffffff;
            }}
            QPushButton {{
                background-color: {accent_color};
                border-radius: 6px;
                padding: 9px 16px;
                color: white;
                font-weight: 600;
                min-height: 36px;
            }}
            QPushButton:hover {{
                background-color: #246651;
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
                color: #555;
                border: 1px solid #d0d0d0;
            }}
            QPushButton#ghost:hover {{
                background-color: #f5f5f5;
                border-color: #bbb;
            }}
            QPushButton#nav {{
                background-color: #8b6f47;
                padding: 8px 14px;
                min-height: 32px;
            }}
            QPushButton#nav:hover {{
                background-color: #735a38;
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
                padding: 10px;
                border: none;
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
        layout.setContentsMargins(35, 28, 35, 28)
        layout.setSpacing(18)
        
        # === Header: Title and Back Button ===
        header_layout = QHBoxLayout()
        title = QLabel("📋 Job Card Records")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignLeft)
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        back_btn_top = QPushButton("⬅ Back to Home")
        back_btn_top.setObjectName("ghost")
        back_btn_top.setFixedHeight(38)
        back_btn_top.setCursor(Qt.PointingHandCursor)
        back_btn_top.clicked.connect(self.go_back)
        header_layout.addWidget(back_btn_top)
        
        layout.addLayout(header_layout)

        # === Compact Filter Card ===
        filter_card = QFrame()
        filter_card.setObjectName("filter_card")
        filter_layout = QVBoxLayout(filter_card)
        filter_layout.setSpacing(12)
        
        # Single row with all filters
        filter_row = QHBoxLayout()
        
        # Search
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search job no, company, vehicle, driver...")
        self.search_input.setMinimumWidth(280)
        filter_row.addWidget(self.search_input, 2)
        
        # Site filter
        self.site_filter = QComboBox()
        self.site_filter.addItem("All Sites")
        self.site_filter.setMinimumWidth(120)
        filter_row.addWidget(self.site_filter, 1)
        
        # Section filter
        self.section_filter = QComboBox()
        self.section_filter.addItem("All Sections")
        self.section_filter.setMinimumWidth(120)
        filter_row.addWidget(self.section_filter, 1)
        
        # Date filter type
        self.date_filter_type = QComboBox()
        self.date_filter_type.addItems(["No Date Filter", "Date Range", "This Month", "Last Month", "Last 3 Months", "Last 6 Months", "This Year"])
        self.date_filter_type.setMinimumWidth(140)
        self.date_filter_type.currentTextChanged.connect(self.on_date_filter_changed)
        filter_row.addWidget(self.date_filter_type, 1)
        
        # Date inputs (hidden by default)
        self.start_date = QDateEdit(QDate.currentDate().addDays(-30))
        self.start_date.setCalendarPopup(True)
        self.start_date.setDisplayFormat("yyyy-MM-dd")
        self.start_date.setVisible(False)
        self.start_date.setMinimumWidth(130)
        filter_row.addWidget(self.start_date)
        
        self.end_date = QDateEdit(QDate.currentDate())
        self.end_date.setCalendarPopup(True)
        self.end_date.setDisplayFormat("yyyy-MM-dd")
        self.end_date.setVisible(False)
        self.end_date.setMinimumWidth(130)
        filter_row.addWidget(self.end_date)
        
        # Filter buttons
        btn_apply = QPushButton("Apply")
        btn_apply.setFixedWidth(90)
        btn_apply.clicked.connect(self.apply_filters)
        filter_row.addWidget(btn_apply)
        
        btn_clear = QPushButton("Clear")
        btn_clear.setObjectName("secondary")
        btn_clear.setFixedWidth(80)
        btn_clear.clicked.connect(self.clear_filters)
        filter_row.addWidget(btn_clear)
        
        filter_layout.addLayout(filter_row)
        layout.addWidget(filter_card)

        # === Navigation & Action Buttons ===
        action_bar = QHBoxLayout()
        
        # Navigation buttons
        btn_new_job = QPushButton("➕ New Job Card")
        btn_new_job.setObjectName("nav")
        btn_new_job.setCursor(Qt.PointingHandCursor)
        btn_new_job.clicked.connect(self.go_to_job_card)
        
        btn_data_manager = QPushButton("📊 Data Manager")
        btn_data_manager.setObjectName("nav")
        btn_data_manager.setCursor(Qt.PointingHandCursor)
        btn_data_manager.clicked.connect(self.go_to_data_manager)
        
        action_bar.addWidget(btn_new_job)
        action_bar.addWidget(btn_data_manager)
        action_bar.addSpacing(20)
        
        # Record actions
        btn_view = QPushButton("👁 View")
        btn_view.setCursor(Qt.PointingHandCursor)
        btn_view.clicked.connect(self.view_details)
        
        btn_edit = QPushButton("✏ Edit")
        btn_edit.setObjectName("secondary")
        btn_edit.setCursor(Qt.PointingHandCursor)
        btn_edit.clicked.connect(self.edit_record)
        
        btn_delete = QPushButton("🗑 Delete")
        btn_delete.setObjectName("danger")
        btn_delete.setCursor(Qt.PointingHandCursor)
        btn_delete.clicked.connect(self.delete_selected)
        
        btn_refresh = QPushButton("🔄 Refresh")
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
        if filter_type == "Date Range":
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
        c.execute("""SELECT id, job_no, company_no, vehicle_no, driver, make, model, type, site, section, start_date
                     FROM job_cards ORDER BY id DESC""")
        rows = c.fetchall()
        conn.close()

        self.populate_table(rows)

    def apply_filters(self):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        query = """SELECT id, job_no, company_no, vehicle_no, driver, make, model, type, site, section, start_date
                   FROM job_cards WHERE 1=1"""
        params = []
        
        # Search keyword
        keyword = self.search_input.text().strip()
        if keyword:
            query += " AND (job_no LIKE ? OR company_no LIKE ? OR vehicle_no LIKE ? OR driver LIKE ?)"
            params.extend([f"%{keyword}%"] * 4)
        
        # Site filter
        if self.site_filter.currentText() != "All Sites":
            query += " AND site = ?"
            params.append(self.site_filter.currentText())
        
        # Section filter
        if self.section_filter.currentText() != "All Sections":
            query += " AND section = ?"
            params.append(self.section_filter.currentText())
        
        # Date filter
        filter_type = self.date_filter_type.currentText()
        current_date = QDate.currentDate()
        
        if filter_type == "Date Range":
            query += " AND start_date BETWEEN ? AND ?"
            params.append(self.start_date.date().toString("yyyy-MM-dd"))
            params.append(self.end_date.date().toString("yyyy-MM-dd"))
        elif filter_type == "This Month":
            first_day = QDate(current_date.year(), current_date.month(), 1)
            query += " AND start_date BETWEEN ? AND ?"
            params.append(first_day.toString("yyyy-MM-dd"))
            params.append(current_date.toString("yyyy-MM-dd"))
        elif filter_type == "Last Month":
            last_month = current_date.addMonths(-1)
            first_day = QDate(last_month.year(), last_month.month(), 1)
            last_day = QDate(last_month.year(), last_month.month(), last_month.daysInMonth())
            query += " AND start_date BETWEEN ? AND ?"
            params.append(first_day.toString("yyyy-MM-dd"))
            params.append(last_day.toString("yyyy-MM-dd"))
        elif filter_type == "Last 3 Months":
            three_months_ago = current_date.addMonths(-3)
            query += " AND start_date BETWEEN ? AND ?"
            params.append(three_months_ago.toString("yyyy-MM-dd"))
            params.append(current_date.toString("yyyy-MM-dd"))
        elif filter_type == "Last 6 Months":
            six_months_ago = current_date.addMonths(-6)
            query += " AND start_date BETWEEN ? AND ?"
            params.append(six_months_ago.toString("yyyy-MM-dd"))
            params.append(current_date.toString("yyyy-MM-dd"))
        elif filter_type == "This Year":
            first_day = QDate(current_date.year(), 1, 1)
            query += " AND start_date BETWEEN ? AND ?"
            params.append(first_day.toString("yyyy-MM-dd"))
            params.append(current_date.toString("yyyy-MM-dd"))
        
        query += " ORDER BY id DESC"
        
        c.execute(query, params)
        rows = c.fetchall()
        conn.close()
        
        self.populate_table(rows)

    def clear_filters(self):
        self.search_input.clear()
        self.site_filter.setCurrentIndex(0)
        self.section_filter.setCurrentIndex(0)
        self.date_filter_type.setCurrentIndex(0)
        self.start_date.setDate(QDate.currentDate().addDays(-30))
        self.end_date.setDate(QDate.currentDate())
        self.load_records()

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
                     site, section, hr_km, start_date, end_date, description, spare_parts
                     FROM job_cards WHERE id=?""", (record_id,))
        row = c.fetchone()
        conn.close()
        
        if row:
            job_data = {
                'job_no': row[0], 'company_no': row[1], 'vehicle_no': row[2],
                'driver': row[3], 'make': row[4], 'model': row[5], 'type': row[6],
                'site': row[7], 'section': row[8], 'hr_km': row[9],
                'start_date': row[10], 'end_date': row[11], 'description': row[12],
                'spare_parts': row[13]
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