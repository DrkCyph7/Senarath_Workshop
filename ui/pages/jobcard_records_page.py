import sqlite3
import json
import os
import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QTableWidget, QTableWidgetItem, QMessageBox, QComboBox,
    QDateEdit, QCheckBox, QFrame, QDialog, QTextEdit, QGridLayout,
    QDialogButtonBox, QScrollArea, QSpinBox, QDoubleSpinBox, QTabWidget,
    QHeaderView, QFileDialog, QInputDialog, QLineEdit
)
from PySide6.QtCore import Qt, QDate, QTimer
from PySide6.QtGui import QFont, QColor, QPixmap
from ui.theme import ColorPalette, Typography, Spacing, Styles, create_page_header

DB_PATH = "ui/db/senarath.db"

# Try to import reportlab for PDF export
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    from reportlab.pdfgen import canvas
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False


class LabourWorksDialog(QDialog):
    """Display labour works with detailed breakdown"""
    def __init__(self, labour_works_json, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Labour Works Details")
        self.setMinimumSize(900, 600)

        # parse incoming data
        self.labour_works_data = []
        try:
            self.labour_works_data = json.loads(labour_works_json) if labour_works_json else []
        except Exception:
            self.labour_works_data = []

        # Styling
        self.setStyleSheet("""
            QDialog { background-color: #ffffff; }
            QLabel { color: #2c2c2c; font-weight: 600; font-size: 13px; }
            QTableWidget { background-color: #ffffff; border: 1px solid #e0e0e0; border-radius: 6px; gridline-color: #e0e0e0; }
            QHeaderView::section { background-color: #2d7a5f; color: white; padding: 10px; border: none; font-weight: 700; }
        """)

        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)

        # Title
        title = QLabel("👷 Labour Works Summary")
        title.setFont(QFont("Segoe UI", 15, QFont.Bold))
        title.setStyleSheet("color: #2d7a5f; padding-bottom: 8px;")
        layout.addWidget(title)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["#", "Description", "Hours", "Labour Assigned", "Cost"])
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)

        # Summary labels
        summary_layout = QHBoxLayout()
        summary_layout.addStretch()
        self.total_hours_label = QLabel("Total Hours: 0.00")
        self.total_hours_label.setStyleSheet("font-size: 13px; padding: 6px 10px; background-color: #f0f0f0; border-radius: 4px;")
        summary_layout.addWidget(self.total_hours_label)
        self.total_labour_cost_label = QLabel("Total Labour Cost: Rs. 0.00")
        self.total_labour_cost_label.setStyleSheet("font-size: 13px; font-weight: 700; padding: 6px 10px; background-color: #e8f4f0; border-radius: 4px; color: #2d7a5f;")
        summary_layout.addWidget(self.total_labour_cost_label)
        layout.addLayout(summary_layout)

        # Close button
        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        button_box.setFixedHeight(36)
        for b in button_box.buttons():
            try:
                b.setFixedHeight(32)
                b.setStyleSheet("padding:6px 12px; font-size:12px;")
            except Exception:
                pass
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
        
        # Footer: actions + dialog buttons on same row (single-line footer)
        footer = QHBoxLayout()
        footer.setSpacing(8)

        add_btn = QPushButton("+ Add Part")
        add_btn.setFixedHeight(32)
        add_btn.setFixedWidth(140)
        add_btn.setStyleSheet("font-size: 11px; padding: 4px 8px;")
        add_btn.clicked.connect(self.add_part)

        edit_btn = QPushButton("Edit")
        edit_btn.setObjectName("secondary")
        edit_btn.setFixedHeight(32)
        edit_btn.setFixedWidth(140)
        edit_btn.setStyleSheet("font-size: 11px; padding: 4px 8px;")
        edit_btn.clicked.connect(self.edit_part)

        delete_btn = QPushButton("Delete")
        delete_btn.setObjectName("danger")
        delete_btn.setFixedHeight(32)
        delete_btn.setFixedWidth(140)
        delete_btn.setStyleSheet("font-size: 12px; padding: 6px 10px;")
        delete_btn.clicked.connect(self.delete_part)

        footer.addWidget(add_btn)
        footer.addWidget(edit_btn)
        footer.addWidget(delete_btn)
        footer.addStretch()

        # Dialog buttons (Cancel / OK) aligned to right - use explicit buttons for consistent sizing
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("secondary")
        cancel_btn.setFixedHeight(32)
        cancel_btn.setFixedWidth(90)
        cancel_btn.clicked.connect(self.reject)
        footer.addWidget(cancel_btn)

        ok_btn = QPushButton("OK")
        ok_btn.setFixedHeight(32)
        ok_btn.setFixedWidth(90)
        ok_btn.clicked.connect(self.accept)
        footer.addWidget(ok_btn)

        layout.addLayout(footer)
        
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


class LabourWorkEditDialog(QDialog):
    """Dialog for editing labour works"""
    def __init__(self, labour_works_json, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Labour Works")
        self.setMinimumSize(1000, 600)
        
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
        title = QLabel("👷 Labour Works")
        title.setFont(QFont("Segoe UI", 15, QFont.Bold))
        title.setStyleSheet("color: #2d7a5f; padding-bottom: 10px;")
        layout.addWidget(title)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["#", "Date", "Description", "Hours", "Labour", "Cost"])
        layout.addWidget(self.table)
        
        # Total
        total_layout = QHBoxLayout()
        total_layout.addStretch()
        self.total_cost_label = QLabel("Total Labour Cost: Rs. 0.00")
        self.total_cost_label.setStyleSheet("font-size: 14px; font-weight: 700; padding: 8px 15px; background-color: #e8f4f0; border-radius: 5px; color: #2d7a5f;")
        total_layout.addWidget(self.total_cost_label)
        layout.addLayout(total_layout)
        
        # Footer: actions + dialog buttons on same row
        footer = QHBoxLayout()
        footer.setSpacing(8)

        add_btn = QPushButton("+ Add Work")
        add_btn.setFixedHeight(32)
        add_btn.setFixedWidth(140)
        add_btn.setStyleSheet("font-size: 11px; padding: 4px 8px;")
        add_btn.clicked.connect(self.add_work)

        edit_btn = QPushButton("Edit")
        edit_btn.setObjectName("secondary")
        edit_btn.setFixedHeight(32)
        edit_btn.setFixedWidth(140)
        edit_btn.setStyleSheet("font-size: 11px; padding: 4px 8px;")
        edit_btn.clicked.connect(self.edit_work)

        delete_btn = QPushButton("Delete")
        delete_btn.setObjectName("danger")
        delete_btn.setFixedHeight(32)
        delete_btn.setFixedWidth(140)
        delete_btn.setStyleSheet("font-size: 12px; padding: 6px 10px;")
        delete_btn.clicked.connect(self.delete_work)

        footer.addWidget(add_btn)
        footer.addWidget(edit_btn)
        footer.addWidget(delete_btn)
        footer.addStretch()

        # Dialog buttons (Ok / Cancel) - explicit buttons for uniform sizing
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("secondary")
        cancel_btn.setFixedHeight(32)
        cancel_btn.setFixedWidth(90)
        cancel_btn.clicked.connect(self.reject)
        footer.addWidget(cancel_btn)

        ok_btn = QPushButton("OK")
        ok_btn.setFixedHeight(32)
        ok_btn.setFixedWidth(90)
        ok_btn.clicked.connect(self.accept)
        footer.addWidget(ok_btn)

        layout.addLayout(footer)
        
        self.setLayout(layout)
        self.refresh_table()
    
    def refresh_table(self):
        self.table.setRowCount(len(self.labour_works_data))
        total_cost = 0.0
        
        for row_idx, work in enumerate(self.labour_works_data):
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(row_idx + 1)))
            self.table.setItem(row_idx, 1, QTableWidgetItem(work.get('work_date', '')))
            self.table.setItem(row_idx, 2, QTableWidgetItem(work.get('description', '')))
            self.table.setItem(row_idx, 3, QTableWidgetItem(str(work.get('hours', '0'))))
            
            labour_list = []
            try:
                labour_items = json.loads(work.get('labour_list', '[]'))
                labour_list = [item['name'] for item in labour_items]
            except:
                pass
            
            self.table.setItem(row_idx, 4, QTableWidgetItem(', '.join(labour_list)))
            self.table.setItem(row_idx, 5, QTableWidgetItem(f"Rs. {work.get('work_cost', '0')}"))
            
            try:
                total_cost += float(work.get('work_cost', 0))
            except ValueError:
                pass
        
        self.total_cost_label.setText(f"Total Labour Cost: Rs. {total_cost:,.2f}")
    
    def add_work(self):
        from ui.pages.job_card_page import LabourWorkDialog
        # Get labour names from database for the dialog
        labour_names = []
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("SELECT name FROM labour ORDER BY name")
            labour_names = [row[0] for row in c.fetchall()]
            conn.close()
        except:
            pass
        
        dialog = LabourWorkDialog(parent=self, labour_list=labour_names)
        if dialog.exec():
            data = dialog.get_data()
            if data.get('description', '').strip():
                self.labour_works_data.append(data)
                self.refresh_table()
            else:
                QMessageBox.warning(self, "Error", "Please fill in all required fields")
    
    def edit_work(self):
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "No Selection", "Please select a labour work to edit.")
            return
        
        # Get labour names from database for the dialog
        labour_names = []
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("SELECT name FROM labour ORDER BY name")
            labour_names = [row[0] for row in c.fetchall()]
            conn.close()
        except:
            pass
        
        from ui.pages.job_card_page import LabourWorkDialog
        current_data = self.labour_works_data[current_row]
        dialog = LabourWorkDialog(parent=self, edit_data=current_data, labour_list=labour_names)
        if dialog.exec():
            data = dialog.get_data()
            if data.get('description', '').strip():
                self.labour_works_data[current_row] = data
                self.refresh_table()
            else:
                QMessageBox.warning(self, "Error", "Please fill in all required fields")
    
    def delete_work(self):
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "No Selection", "Please select a labour work to delete.")
            return
        
        confirm = QMessageBox.question(self, "Confirm Delete", 
                                      "Are you sure you want to delete this labour work?",
                                      QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            del self.labour_works_data[current_row]
            self.refresh_table()
    
    def get_data(self):
        return json.dumps(self.labour_works_data)


class OutsourceWorkEditDialog(QDialog):
    """Dialog for editing outsource works"""
    def __init__(self, outsource_works_json, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Outsource Works")
        self.setMinimumSize(900, 520)

        # load data
        self.outsource_works_data = []
        try:
            self.outsource_works_data = json.loads(outsource_works_json) if outsource_works_json else []
        except Exception:
            self.outsource_works_data = []

        # styling
        self.setStyleSheet("""
            QDialog { background-color: #ffffff; }
            QLabel { color: #2c2c2c; font-weight: 600; font-size: 13px; }
            QTableWidget { background-color: #ffffff; border: 1px solid #e0e0e0; border-radius: 6px; gridline-color: #e0e0e0; }
            QHeaderView::section { background-color: #2d7a5f; color: white; padding: 10px; border: none; font-weight: 700; }
            QPushButton { background-color: #2d7a5f; color: white; border: none; border-radius: 6px; padding: 8px 14px; font-weight: 600; }
            QPushButton#secondary { background-color: #8b6f47; }
            QPushButton#danger { background-color: #c84343; }
        """)

        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(12, 12, 12, 12)

        # Title
        title = QLabel("🔨 Outsource Works")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title.setStyleSheet("color: #2d7a5f; padding-bottom: 6px;")
        layout.addWidget(title)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["#", "Date", "Work Type", "Description", "Cost", "Remark"])
        layout.addWidget(self.table)

        # Total
        total_layout = QHBoxLayout()
        total_layout.addStretch()
        self.total_cost_label = QLabel("Total Outsource Cost: Rs. 0.00")
        self.total_cost_label.setStyleSheet("font-size: 13px; font-weight: 700; padding: 6px 10px; background-color: #e8f4f0; border-radius: 4px; color: #2d7a5f;")
        total_layout.addWidget(self.total_cost_label)
        layout.addLayout(total_layout)

        # Footer: actions + dialog buttons on same row
        footer = QHBoxLayout()
        footer.setSpacing(8)

        add_btn = QPushButton("+ Add Work")
        add_btn.setFixedHeight(32)
        add_btn.setFixedWidth(140)
        add_btn.clicked.connect(self.add_work)
        footer.addWidget(add_btn)

        edit_btn = QPushButton("Edit")
        edit_btn.setObjectName("secondary")
        edit_btn.setFixedHeight(32)
        edit_btn.setFixedWidth(140)
        edit_btn.clicked.connect(self.edit_work)
        footer.addWidget(edit_btn)

        delete_btn = QPushButton("Delete")
        delete_btn.setObjectName("danger")
        delete_btn.setFixedHeight(32)
        delete_btn.setFixedWidth(140)
        delete_btn.clicked.connect(self.delete_work)
        footer.addWidget(delete_btn)

        footer.addStretch()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("secondary")
        cancel_btn.setFixedHeight(32)
        cancel_btn.setFixedWidth(90)
        cancel_btn.clicked.connect(self.reject)
        footer.addWidget(cancel_btn)

        ok_btn = QPushButton("OK")
        ok_btn.setFixedHeight(32)
        ok_btn.setFixedWidth(90)
        ok_btn.clicked.connect(self.accept)
        footer.addWidget(ok_btn)

        layout.addLayout(footer)

        self.setLayout(layout)
        self.refresh_table()

    def refresh_table(self):
        self.table.setRowCount(len(self.outsource_works_data))
        total_cost = 0.0
        for row_idx, work in enumerate(self.outsource_works_data):
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(row_idx + 1)))
            self.table.setItem(row_idx, 1, QTableWidgetItem(work.get('work_date', '')))
            self.table.setItem(row_idx, 2, QTableWidgetItem(work.get('work_type', '')))
            self.table.setItem(row_idx, 3, QTableWidgetItem(work.get('description', '')))
            self.table.setItem(row_idx, 4, QTableWidgetItem(f"Rs. {work.get('cost', '0')}"))
            self.table.setItem(row_idx, 5, QTableWidgetItem(work.get('remark', '')))
            try:
                total_cost += float(work.get('cost', 0))
            except ValueError:
                pass
        self.total_cost_label.setText(f"Total Outsource Cost: Rs. {total_cost:,.2f}")

    def add_work(self):
        from ui.pages.job_card_page import OutsourceWorkDialog
        dialog = OutsourceWorkDialog(parent=self)
        if dialog.exec():
            data = dialog.get_data()
            self.outsource_works_data.append(data)
            self.refresh_table()

    def edit_work(self):
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "No Selection", "Please select an outsource work to edit.")
            return
        from ui.pages.job_card_page import OutsourceWorkDialog
        current_data = self.outsource_works_data[current_row]
        dialog = OutsourceWorkDialog(parent=self, edit_data=current_data)
        if dialog.exec():
            data = dialog.get_data()
            self.outsource_works_data[current_row] = data
            self.refresh_table()

    def delete_work(self):
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "No Selection", "Please select an outsource work to delete.")
            return
        confirm = QMessageBox.question(self, "Confirm Delete", "Are you sure you want to delete this outsource work?", QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            del self.outsource_works_data[current_row]
            self.refresh_table()

    def get_data(self):
        return json.dumps(self.outsource_works_data)


class JobCardEditDialog(QDialog):
    def __init__(self, job_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Edit Job Card - {job_data.get('job_no', 'N/A')}")
        # Use a more compact dialog size (smaller, cleaner layout)
        self.setMinimumSize(920, 640)
        self.resize(960, 680)
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
        
        # Compact styling: smaller paddings, slightly smaller fonts and controls
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
            }
            QLabel {
                color: #2c2c2c;
                font-weight: 600;
                font-size: 12px;
            }
            QLineEdit, QComboBox, QDateEdit, QTextEdit {
                background-color: #fafafa;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                padding: 4px 6px;
                font-size: 12px;
                min-height: 24px;
            }
            QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QTextEdit:focus {
                border: 2px solid #2d7a5f;
                background-color: #ffffff;
            }
            QPushButton {
                background-color: #2d7a5f;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: 600;
                font-size: 12px;
                min-height: 28px;
            }
            QPushButton:hover {
                background-color: #246651;
            }
            QPushButton#secondary {
                background-color: #8b6f47;
                padding: 5px 10px;
                min-height: 26px;
                font-size: 11px;
            }
            QPushButton#secondary:hover {
                background-color: #735a38;
            }
        """)
        # Main container (no scroll) — layout compressed for a clean professional look
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(6)
        layout.setContentsMargins(6, 6, 6, 6)

        # Title
        title = QLabel(f"✏️ Edit Job Card: {job_data.get('job_no', 'N/A')}")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title.setStyleSheet("color: #2d7a5f; padding: 4px;")
        layout.addWidget(title)

        # Form grid (compact two-column layout)
        grid = QGridLayout()
        grid.setHorizontalSpacing(6)
        grid.setVerticalSpacing(6)

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
        desc_label.setStyleSheet("color: #2d7a5f; font-size: 14px; padding-top: 8px;")
        layout.addWidget(desc_label)
        self.description_input = QTextEdit()
        self.description_input.setPlainText(job_data.get('description', ''))
        # Keep description compact so the dialog fits on screen without scrolling
        self.description_input.setMaximumHeight(90)
        layout.addWidget(self.description_input)

        # Store work data
        self.spare_parts_data = job_data.get('spare_parts', '[]')
        self.labour_works_data = job_data.get('labour_works', '[]')
        self.outsource_works_data = job_data.get('outsource_works', '[]')

        # Main dialog layout — add container directly (no scroll)
        main_layout = QVBoxLayout()
        main_layout.setSpacing(4)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.addWidget(container)

        # Footer: move the three edit buttons to the bottom and keep them with Save/Cancel
        footer_layout = QHBoxLayout()
        footer_layout.setSpacing(8)

        # Small secondary edit buttons (left side)
        self.edit_spare_btn = QPushButton("🔧 Edit Spare Parts")
        self.edit_spare_btn.setObjectName("secondary")
        self.edit_spare_btn.setFixedHeight(32)
        self.edit_spare_btn.setFixedWidth(140)
        self.edit_spare_btn.clicked.connect(self.edit_spare_parts)
        footer_layout.addWidget(self.edit_spare_btn)

        self.edit_labour_btn = QPushButton("👷 Edit Labour Works")
        self.edit_labour_btn.setObjectName("secondary")
        self.edit_labour_btn.setFixedHeight(32)
        self.edit_labour_btn.setFixedWidth(140)
        self.edit_labour_btn.clicked.connect(self.edit_labour_works)
        footer_layout.addWidget(self.edit_labour_btn)

        self.edit_outsource_btn = QPushButton("🔨 Edit Outsource Works")
        self.edit_outsource_btn.setObjectName("secondary")
        self.edit_outsource_btn.setFixedHeight(32)
        self.edit_outsource_btn.setFixedWidth(140)
        self.edit_outsource_btn.clicked.connect(self.edit_outsource_works)
        footer_layout.addWidget(self.edit_outsource_btn)

        footer_layout.addStretch()

        # Dialog buttons (Save/Cancel) on the right side of the footer - explicit buttons for consistency
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("secondary")
        cancel_btn.setFixedHeight(32)
        cancel_btn.setFixedWidth(100)
        cancel_btn.clicked.connect(self.reject)
        footer_layout.addWidget(cancel_btn)

        save_btn = QPushButton("Save")
        save_btn.setFixedHeight(32)
        save_btn.setFixedWidth(100)
        save_btn.setDefault(True)
        save_btn.setAutoDefault(True)
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.clicked.connect(self.save_changes)
        footer_layout.addWidget(save_btn)

        main_layout.addLayout(footer_layout)

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
    
    def edit_labour_works(self):
        dialog = LabourWorkEditDialog(self.labour_works_data, self)
        if dialog.exec():
            self.labour_works_data = dialog.get_data()
    
    def edit_outsource_works(self):
        dialog = OutsourceWorkEditDialog(self.outsource_works_data, self)
        if dialog.exec():
            self.outsource_works_data = dialog.get_data()
    
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
                    description=?, spare_parts=?, labour_works=?, outsource_works=?
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
                self.labour_works_data,
                self.outsource_works_data,
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
        self.setWindowTitle(f"Job Card - {job_data.get('job_no', 'N/A')}")
        self.setMinimumSize(1100, 750)
        
        # Simple and professional styling
        self.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
            }
            QLabel {
                background-color: transparent;
            }
            QTextEdit, QTableWidget {
                background-color: #ffffff;
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                padding: 10px;
                font-size: 11px;
            }
            QPushButton {
                background-color: #2d7a5f;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: 600;
                min-height: 32px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #246651;
            }
            QTabWidget::pane {
                border: 1px solid #d0d0d0;
            }
            QTabBar::tab {
                background-color: #f5f5f5;
                border: 1px solid #d0d0d0;
                padding: 6px 12px;
                margin-right: 1px;
                font-size: 11px;
            }
            QTabBar::tab:selected {
                background-color: #2d7a5f;
                color: white;
                border: 1px solid #2d7a5f;
            }
        """)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(12)
        
        # Title bar with job number and dates
        title_layout = QHBoxLayout()
        title = QLabel(f"JOB CARD: {job_data.get('job_no', 'N/A')}")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title.setStyleSheet("color: #2d7a5f;")
        title_layout.addWidget(title)
        title_layout.addStretch()
        
        date_range = QLabel(f"{job_data.get('start_date', 'N/A')} → {job_data.get('end_date', 'N/A')}")
        date_range.setFont(QFont("Segoe UI", 10))
        date_range.setStyleSheet("color: #666; padding: 4px 10px; background-color: #f0f0f0; border-radius: 3px;")
        title_layout.addWidget(date_range)
        main_layout.addLayout(title_layout)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("color: #d0d0d0;")
        main_layout.addWidget(separator)
        
        # Job Information Table
        info_table = QTableWidget()
        info_table.setRowCount(5)
        info_table.setColumnCount(4)
        info_table.setHorizontalHeaderLabels(["Driver", "Value", "Site", "Value"])
        info_table.horizontalHeader().setStyleSheet("background-color: #2d7a5f; color: white; font-weight: bold;")
        
        info_data = [
            ("Driver:", job_data.get('driver', 'N/A'), "Site:", job_data.get('site', 'N/A')),
            ("Company No:", job_data.get('company_no', 'N/A'), "Section:", job_data.get('section', 'N/A')),
            ("Vehicle No:", job_data.get('vehicle_no', 'N/A'), "Type:", job_data.get('type', 'N/A')),
            ("Make/Model:", f"{job_data.get('make', 'N/A')} / {job_data.get('model', 'N/A')}", "Hr/Km:", job_data.get('hr_km', 'N/A')),
            ("Start:", job_data.get('start_date', 'N/A'), "End:", job_data.get('end_date', 'N/A')),
        ]
        
        for row, (label1, val1, label2, val2) in enumerate(info_data):
            info_table.setItem(row, 0, QTableWidgetItem(label1))
            info_table.setItem(row, 1, QTableWidgetItem(val1))
            info_table.setItem(row, 2, QTableWidgetItem(label2))
            info_table.setItem(row, 3, QTableWidgetItem(val2))
        
        info_table.setColumnWidth(0, 120)
        info_table.setColumnWidth(1, 200)
        info_table.setColumnWidth(2, 120)
        info_table.setColumnWidth(3, 200)
        info_table.setMaximumHeight(150)
        info_table.horizontalHeader().setVisible(False)
        info_table.verticalHeader().setVisible(False)
        main_layout.addWidget(info_table)
        
        # Tabs for details
        tabs = QTabWidget()
        
        # Tab 1: Description
        desc_tab = QWidget()
        desc_layout = QVBoxLayout(desc_tab)
        desc_layout.setContentsMargins(10, 10, 10, 10)
        desc_text = QTextEdit()
        desc_text.setPlainText(job_data.get('description', 'No description provided.'))
        desc_text.setReadOnly(True)
        desc_text.setMinimumHeight(200)
        desc_layout.addWidget(desc_text)
        tabs.addTab(desc_tab, "Description")
        
        # Tab 2: Spare Parts
        spare_tab = QWidget()
        spare_layout = QVBoxLayout(spare_tab)
        spare_layout.setContentsMargins(10, 10, 10, 10)
        
        spare_parts = job_data.get('spare_parts', '[]')
        try:
            parts = json.loads(spare_parts) if spare_parts else []
            if parts:
                spare_table = QTableWidget()
                spare_table.setRowCount(len(parts))
                spare_table.setColumnCount(7)
                spare_table.setHorizontalHeaderLabels(["#", "Description", "Ref No", "Qty", "Unit", "Unit Price", "Total"])
                
                grand_total = 0.0
                for row, part in enumerate(parts):
                    spare_table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
                    spare_table.setItem(row, 1, QTableWidgetItem(part.get('description', '')))
                    spare_table.setItem(row, 2, QTableWidgetItem(part.get('ref_no', '')))
                    spare_table.setItem(row, 3, QTableWidgetItem(part.get('quantity', '')))
                    spare_table.setItem(row, 4, QTableWidgetItem(part.get('unit', '')))
                    spare_table.setItem(row, 5, QTableWidgetItem(f"Rs. {float(part.get('unit_price', 0)):,.2f}"))
                    total_val = float(part.get('total', 0))
                    spare_table.setItem(row, 6, QTableWidgetItem(f"Rs. {total_val:,.2f}"))
                    grand_total += total_val
                
                spare_table.setColumnWidth(0, 30)
                spare_table.setColumnWidth(1, 250)
                spare_table.setColumnWidth(2, 100)
                spare_table.setColumnWidth(3, 50)
                spare_table.setColumnWidth(4, 60)
                spare_table.setColumnWidth(5, 90)
                spare_table.setColumnWidth(6, 90)
                spare_table.horizontalHeader().setStyleSheet("background-color: #2d7a5f; color: white; font-weight: bold;")
                spare_layout.addWidget(spare_table)
                
                total_frame = QFrame()
                total_frame.setStyleSheet("background-color: #f0f0f0; border-radius: 3px;")
                total_layout = QHBoxLayout(total_frame)
                total_layout.setContentsMargins(10, 5, 10, 5)
                total_layout.addStretch()
                total_label = QLabel(f"Spare Parts Total: Rs. {grand_total:,.2f}")
                total_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
                total_label.setStyleSheet("color: #2d7a5f;")
                total_layout.addWidget(total_label)
                spare_layout.addWidget(total_frame)
            else:
                no_data = QLabel("No spare parts recorded.")
                no_data.setStyleSheet("color: #999; font-style: italic; padding: 20px;")
                spare_layout.addWidget(no_data)
        except Exception as e:
            error = QLabel(f"Error loading spare parts: {str(e)}")
            error.setStyleSheet("color: #c84343;")
            spare_layout.addWidget(error)
        
        spare_layout.addStretch()
        tabs.addTab(spare_tab, "Spare Parts")
        
        # Tab 3: Labour Works
        labour_tab = QWidget()
        labour_layout = QVBoxLayout(labour_tab)
        labour_layout.setContentsMargins(10, 10, 10, 10)
        
        labour_works = job_data.get('labour_works', '[]')
        try:
            works = json.loads(labour_works) if labour_works else []
            if works:
                labour_table = QTableWidget()
                labour_table.setRowCount(len(works))
                labour_table.setColumnCount(6)
                labour_table.setHorizontalHeaderLabels(["#", "Date", "Description", "Hours", "Labour", "Cost"])
                
                total_cost = 0.0
                for row, work in enumerate(works):
                    labour_table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
                    labour_table.setItem(row, 1, QTableWidgetItem(work.get('work_date', '')))
                    labour_table.setItem(row, 2, QTableWidgetItem(work.get('description', '')))
                    labour_table.setItem(row, 3, QTableWidgetItem(f"{float(work.get('hours', 0)):.2f} hrs"))
                    
                    labour_list = []
                    try:
                        labour_items = json.loads(work.get('labour_list', '[]'))
                        labour_list = [f"{item['name']} ({item['grade']})" for item in labour_items]
                    except:
                        pass
                    
                    labour_table.setItem(row, 4, QTableWidgetItem(', '.join(labour_list)))
                    cost_val = float(work.get('work_cost', 0))
                    labour_table.setItem(row, 5, QTableWidgetItem(f"Rs. {cost_val:,.2f}"))
                    total_cost += cost_val
                
                labour_table.setColumnWidth(0, 30)
                labour_table.setColumnWidth(1, 80)
                labour_table.setColumnWidth(2, 180)
                labour_table.setColumnWidth(3, 70)
                labour_table.setColumnWidth(4, 200)
                labour_table.setColumnWidth(5, 90)
                labour_table.horizontalHeader().setStyleSheet("background-color: #2d7a5f; color: white; font-weight: bold;")
                labour_layout.addWidget(labour_table)
                
                total_frame = QFrame()
                total_frame.setStyleSheet("background-color: #f0f0f0; border-radius: 3px;")
                total_layout = QHBoxLayout(total_frame)
                total_layout.setContentsMargins(10, 5, 10, 5)
                total_layout.addStretch()
                total_label = QLabel(f"Labour Cost Total: Rs. {total_cost:,.2f}")
                total_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
                total_label.setStyleSheet("color: #2d7a5f;")
                total_layout.addWidget(total_label)
                labour_layout.addWidget(total_frame)
            else:
                no_data = QLabel("No labour works recorded.")
                no_data.setStyleSheet("color: #999; font-style: italic; padding: 20px;")
                labour_layout.addWidget(no_data)
        except Exception as e:
            error = QLabel(f"Error loading labour works: {str(e)}")
            error.setStyleSheet("color: #c84343;")
            labour_layout.addWidget(error)
        
        labour_layout.addStretch()
        tabs.addTab(labour_tab, "Labour Works")
        
        # Tab 4: Outsource Works
        outsource_tab = QWidget()
        outsource_layout = QVBoxLayout(outsource_tab)
        outsource_layout.setContentsMargins(10, 10, 10, 10)
        
        outsource_works = job_data.get('outsource_works', '[]')
        try:
            works = json.loads(outsource_works) if outsource_works else []
            if works:
                outsource_table = QTableWidget()
                outsource_table.setRowCount(len(works))
                outsource_table.setColumnCount(6)
                outsource_table.setHorizontalHeaderLabels(["#", "Date", "Work Type", "Description", "Cost", "Remark"])
                
                total_cost = 0.0
                for row, work in enumerate(works):
                    outsource_table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
                    outsource_table.setItem(row, 1, QTableWidgetItem(work.get('work_date', '')))
                    outsource_table.setItem(row, 2, QTableWidgetItem(work.get('work_type', '')))
                    outsource_table.setItem(row, 3, QTableWidgetItem(work.get('description', '')))
                    cost_val = float(work.get('cost', 0))
                    outsource_table.setItem(row, 4, QTableWidgetItem(f"Rs. {cost_val:,.2f}"))
                    outsource_table.setItem(row, 5, QTableWidgetItem(work.get('remark', '')))
                    total_cost += cost_val
                
                outsource_table.setColumnWidth(0, 30)
                outsource_table.setColumnWidth(1, 80)
                outsource_table.setColumnWidth(2, 120)
                outsource_table.setColumnWidth(3, 200)
                outsource_table.setColumnWidth(4, 90)
                outsource_table.setColumnWidth(5, 150)
                outsource_table.horizontalHeader().setStyleSheet("background-color: #2d7a5f; color: white; font-weight: bold;")
                outsource_layout.addWidget(outsource_table)
                
                total_frame = QFrame()
                total_frame.setStyleSheet("background-color: #f0f0f0; border-radius: 3px;")
                total_layout = QHBoxLayout(total_frame)
                total_layout.setContentsMargins(10, 5, 10, 5)
                total_layout.addStretch()
                total_label = QLabel(f"Outsource Total: Rs. {total_cost:,.2f}")
                total_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
                total_label.setStyleSheet("color: #2d7a5f;")
                total_layout.addWidget(total_label)
                outsource_layout.addWidget(total_frame)
            else:
                no_data = QLabel("No outsource works recorded.")
                no_data.setStyleSheet("color: #999; font-style: italic; padding: 20px;")
                outsource_layout.addWidget(no_data)
        except Exception as e:
            error = QLabel(f"Error loading outsource works: {str(e)}")
            error.setStyleSheet("color: #c84343;")
            outsource_layout.addWidget(error)
        
        outsource_layout.addStretch()
        tabs.addTab(outsource_tab, "Outsource Works")
        
        main_layout.addWidget(tabs)
        
        # Financial Summary
        summary_frame = QFrame()
        summary_frame.setStyleSheet("background-color: #f9f9f9; border: 1px solid #d0d0d0; border-radius: 4px; padding: 12px;")
        summary_layout = QHBoxLayout(summary_frame)
        summary_layout.setContentsMargins(15, 10, 15, 10)
        
        spare_total = 0.0
        try:
            parts = json.loads(spare_parts) if spare_parts else []
            for part in parts:
                spare_total += float(part.get('total', 0))
        except:
            pass
        
        labour_total = 0.0
        try:
            works = json.loads(labour_works) if labour_works else []
            for work in works:
                labour_total += float(work.get('work_cost', 0))
        except:
            pass
        
        outsource_total = 0.0
        try:
            works = json.loads(outsource_works) if outsource_works else []
            for work in works:
                outsource_total += float(work.get('cost', 0))
        except:
            pass
        
        grand_total = spare_total + labour_total + outsource_total
        
        summary_layout.addWidget(QLabel(f"Spare Parts: Rs. {spare_total:,.2f}"))
        summary_layout.addSpacing(20)
        summary_layout.addWidget(QLabel(f"Labour Cost: Rs. {labour_total:,.2f}"))
        summary_layout.addSpacing(20)
        summary_layout.addWidget(QLabel(f"Outsource: Rs. {outsource_total:,.2f}"))
        summary_layout.addStretch()
        
        grand_label = QLabel(f"GRAND TOTAL: Rs. {grand_total:,.2f}")
        grand_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        grand_label.setStyleSheet("color: #2d7a5f;")
        summary_layout.addWidget(grand_label)
        
        main_layout.addWidget(summary_frame)
        
        # Action buttons
        button_layout = QHBoxLayout()
        if HAS_REPORTLAB:
            export_btn = QPushButton("Export PDF")
            export_btn.clicked.connect(lambda: self.export_to_pdf(job_data, spare_total, labour_total, outsource_total, grand_total))
            export_btn.setFixedHeight(32)
            button_layout.addWidget(export_btn)
        
        button_layout.addStretch()
        close_btn = QPushButton("Close")
        close_btn.setFixedWidth(100)
        close_btn.setFixedHeight(32)
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
        self.job_data = job_data
    
    def export_to_pdf(self, job_data, spare_total, labour_total, outsource_total, grand_total):
        """Export job card details to PDF"""
        if not HAS_REPORTLAB:
            QMessageBox.warning(self, "Not Available", "PDF export requires reportlab library.")
            return
        
        # File save dialog
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Job Card as PDF",
            f"JobCard_{job_data.get('job_no', 'unknown')}.pdf",
            "PDF Files (*.pdf)"
        )
        
        if not file_path:
            return
        
        try:
            doc = SimpleDocTemplate(
                file_path, 
                pagesize=A4,
                topMargin=0.6*inch,
                bottomMargin=0.4*inch,
                leftMargin=0.4*inch,
                rightMargin=0.4*inch
            )
            story = []
            styles = getSampleStyleSheet()
            
            # We'll draw a consistent header and footer on every page using canvas callbacks.
            # Logo original dimensions: 495 x 150 (keep same ratio). We'll scale it to fit
            # inside the header area while preserving ratio.
            logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'assets', 'logo.png')

            def _draw_header_footer(canvas_obj, doc_obj):
                # Header
                page_width, page_height = doc_obj.pagesize
                content_width = doc_obj.width

                # Compute logo size preserving original aspect ratio (495 x 150)
                orig_w, orig_h = 495.0, 150.0
                # Maximum space allocated for logo in header
                max_logo_w = content_width * 0.28
                max_logo_h = 0.6 * inch
                scale = min(max_logo_w / orig_w, max_logo_h / orig_h)
                logo_w = orig_w * scale
                logo_h = orig_h * scale

                # Coordinates: origin is bottom-left. Place logo near left within margins.
                logo_x = doc_obj.leftMargin
                logo_y = page_height - doc_obj.topMargin + (doc_obj.topMargin - logo_h) / 2.0

                # Draw logo if exists
                if os.path.exists(logo_path):
                    try:
                        canvas_obj.drawImage(logo_path, logo_x, logo_y, width=logo_w, height=logo_h, preserveAspectRatio=True, mask='auto')
                    except Exception:
                        pass

                # Header text (centered)
                header_title = 'SENARATH WMS'
                canvas_obj.setFont('Helvetica-Bold', 14)
                canvas_obj.setFillColor(colors.HexColor('#2d7a5f'))
                canvas_obj.drawCentredString(page_width / 2.0, page_height - (doc_obj.topMargin / 2.0) + 6, header_title)

                # Small right aligned date
                canvas_obj.setFont('Helvetica', 8)
                canvas_obj.setFillColor(colors.HexColor('#666666'))
                date_str = datetime.datetime.now().strftime('%d %B %Y')
                canvas_obj.drawRightString(page_width - doc_obj.rightMargin, page_height - (doc_obj.topMargin / 2.0) + 6, date_str)

                # Divider line below header
                canvas_obj.setStrokeColor(colors.HexColor('#dcdcdc'))
                canvas_obj.setLineWidth(0.5)
                y_line = page_height - doc_obj.topMargin + (doc_obj.topMargin * 0.1)
                canvas_obj.line(doc_obj.leftMargin, y_line, page_width - doc_obj.rightMargin, y_line)

                # Footer
                footer_y = doc_obj.bottomMargin / 2.0
                canvas_obj.setFont('Helvetica', 8)
                canvas_obj.setFillColor(colors.HexColor('#666666'))
                footer_text = 'Senarath WMS • Developed by DrkCyph7 • NexCy Technologies'
                canvas_obj.drawCentredString(page_width / 2.0, footer_y + 6, footer_text)
                timestamp = f"v1.0 • Generated on {datetime.datetime.now().strftime('%d %B %Y at %H:%M:%S')}"
                canvas_obj.setFont('Helvetica', 7)
                canvas_obj.drawCentredString(page_width / 2.0, footer_y - 4, timestamp)

                # Divider line above footer
                canvas_obj.setStrokeColor(colors.HexColor('#eeeeee'))
                canvas_obj.setLineWidth(0.4)
                canvas_obj.line(doc_obj.leftMargin, footer_y + 18, page_width - doc_obj.rightMargin, footer_y + 18)
            
            # Separator line
            sep_style = ParagraphStyle(
                'Separator',
                parent=styles['Normal'],
                leftIndent=0,
                rightIndent=0,
            )
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=14,
                textColor=colors.HexColor('#2d7a5f'),
                spaceAfter=8,
                alignment=TA_CENTER,
                fontName='Helvetica-Bold'
            )
            story.append(Paragraph(f"JOB CARD - {job_data.get('job_no', 'N/A')}", title_style))
            story.append(Spacer(1, 0.06*inch))
            
            # Job Information Table
            info_data = [
                ['Driver:', job_data.get('driver', 'N/A'), 'Site:', job_data.get('site', 'N/A')],
                ['Company No:', job_data.get('company_no', 'N/A'), 'Section:', job_data.get('section', 'N/A')],
                ['Vehicle No:', job_data.get('vehicle_no', 'N/A'), 'Type:', job_data.get('type', 'N/A')],
                ['Make/Model:', f"{job_data.get('make', 'N/A')} / {job_data.get('model', 'N/A')}", 'Hr/Km:', job_data.get('hr_km', 'N/A')],
                ['Start:', job_data.get('start_date', 'N/A'), 'End:', job_data.get('end_date', 'N/A')],
            ]
            
            # Make info table occupy full content width by distributing column widths proportionally.
            info_units = [1.5, 2.0, 1.5, 2.0]
            info_sum = sum(info_units)
            info_col_widths = [doc.width * (u / info_sum) for u in info_units]
            info_table = Table(info_data, colWidths=info_col_widths)
            info_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f9f9f9')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#333333')),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
            ]))
            story.append(info_table)
            story.append(Spacer(1, 0.08*inch))
            
            # Description
            desc_style = ParagraphStyle(
                'DescStyle',
                parent=styles['Heading3'],
                fontSize=9,
                textColor=colors.HexColor('#2d7a5f'),
                spaceAfter=5,
                fontName='Helvetica-Bold'
            )
            body_style = ParagraphStyle(
                'BodyStyle',
                parent=styles['Normal'],
                fontSize=9,
                textColor=colors.HexColor('#333333'),
                spaceAfter=8,
            )
            
            if job_data.get('description', '').strip():
                story.append(Paragraph("Description", desc_style))
                story.append(Paragraph(job_data.get('description', ''), body_style))
                story.append(Spacer(1, 0.06*inch))
            
            # Spare Parts
            spare_parts = job_data.get('spare_parts', '[]')
            try:
                parts = json.loads(spare_parts) if spare_parts else []
                if parts:
                    story.append(Paragraph("Spare Parts & Materials", desc_style))
                    spare_data = [['#', 'Description', 'Qty', 'Unit', 'Unit Price', 'Total']]
                    for idx, part in enumerate(parts, 1):
                        spare_data.append([
                            str(idx),
                            part.get('description', ''),
                            part.get('quantity', ''),
                            part.get('unit', ''),
                            f"Rs. {float(part.get('unit_price', 0)):,.2f}",
                            f"Rs. {float(part.get('total', 0)):,.2f}"
                        ])
                    
                    # Make spare parts table full width by assigning proportional column widths
                    spare_units = [0.35, 2.0, 0.5, 0.5, 0.9, 0.9]
                    spare_sum = sum(spare_units)
                    spare_col_widths = [doc.width * (u / spare_sum) for u in spare_units]
                    spare_table = Table(spare_data, colWidths=spare_col_widths)
                    spare_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2d7a5f')),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('ALIGN', (1, 1), (1, -1), 'LEFT'),
                        ('ALIGN', (4, 1), (-1, -1), 'RIGHT'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, -1), 8),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                        ('TOPPADDING', (0, 0), (-1, -1), 3),
                        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d0d0d0')),
                        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#ffffff'), colors.HexColor('#f9f9f9')]),
                    ]))
                    story.append(spare_table)
                    story.append(Spacer(1, 0.06*inch))
            except:
                pass
            
            # Labour Works
            labour_works = job_data.get('labour_works', '[]')
            try:
                works = json.loads(labour_works) if labour_works else []
                if works:
                    story.append(Paragraph("Labour Works", desc_style))
                    labour_data = [['#', 'Date', 'Description', 'Hours', 'Labour', 'Cost']]
                    for idx, work in enumerate(works, 1):
                        labour_list = []
                        try:
                            labour_json = work.get('labour_list', '[]')
                            labour_items = json.loads(labour_json) if isinstance(labour_json, str) else labour_json
                            for item in labour_items:
                                labour_list.append(f"{item.get('name', '')} ({item.get('grade', '')})")
                        except:
                            pass
                        
                        labour_data.append([
                            str(idx),
                            work.get('work_date', ''),
                            work.get('description', ''),
                            f"{float(work.get('hours', 0)):.2f}",
                            ', '.join(labour_list[:1]),
                            f"Rs. {float(work.get('work_cost', 0)):,.2f}"
                        ])
                    
                    # Labour table full width
                    labour_units = [0.35, 0.7, 1.4, 0.65, 1.5, 0.85]
                    labour_sum = sum(labour_units)
                    labour_col_widths = [doc.width * (u / labour_sum) for u in labour_units]
                    labour_table = Table(labour_data, colWidths=labour_col_widths)
                    labour_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2d7a5f')),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('ALIGN', (1, 1), (3, -1), 'LEFT'),
                        ('ALIGN', (-1, 1), (-1, -1), 'RIGHT'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, -1), 8),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                        ('TOPPADDING', (0, 0), (-1, -1), 3),
                        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d0d0d0')),
                        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#ffffff'), colors.HexColor('#f9f9f9')]),
                    ]))
                    story.append(labour_table)
                    story.append(Spacer(1, 0.06*inch))
            except:
                pass
            
            # Outsource Works
            outsource_works = job_data.get('outsource_works', '[]')
            try:
                works = json.loads(outsource_works) if outsource_works else []
                if works:
                    story.append(Paragraph("Outsource Works", desc_style))
                    outsource_data = [['#', 'Date', 'Work Type', 'Description', 'Cost']]
                    for idx, work in enumerate(works, 1):
                        outsource_data.append([
                            str(idx),
                            work.get('work_date', ''),
                            work.get('work_type', ''),
                            work.get('description', ''),
                            f"Rs. {float(work.get('cost', 0)):,.2f}"
                        ])
                    
                    # Outsource table full width
                    outsource_units = [0.35, 0.7, 1.0, 2.0, 0.85]
                    outsource_sum = sum(outsource_units)
                    outsource_col_widths = [doc.width * (u / outsource_sum) for u in outsource_units]
                    outsource_table = Table(outsource_data, colWidths=outsource_col_widths)
                    outsource_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2d7a5f')),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('ALIGN', (1, 1), (3, -1), 'LEFT'),
                        ('ALIGN', (-1, 1), (-1, -1), 'RIGHT'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, -1), 8),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                        ('TOPPADDING', (0, 0), (-1, -1), 3),
                        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d0d0d0')),
                        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#ffffff'), colors.HexColor('#f9f9f9')]),
                    ]))
                    story.append(outsource_table)
                    story.append(Spacer(1, 0.06*inch))
            except:
                pass
            
            # Financial Summary
            story.append(Spacer(1, 0.06*inch))
            summary_data = [
                ['Spare Parts Total:', f"Rs. {spare_total:,.2f}"],
                ['Labour Cost Total:', f"Rs. {labour_total:,.2f}"],
                ['Outsource Total:', f"Rs. {outsource_total:,.2f}"],
                ['GRAND TOTAL:', f"Rs. {grand_total:,.2f}"],
            ]
            
            # Summary table full width
            summary_units = [3.0, 2.5]
            summary_sum = sum(summary_units)
            summary_col_widths = [doc.width * (u / summary_sum) for u in summary_units]
            summary_table = Table(summary_data, colWidths=summary_col_widths)
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 2), colors.HexColor('#f9f9f9')),
                ('BACKGROUND', (0, 3), (-1, 3), colors.HexColor('#2d7a5f')),
                ('TEXTCOLOR', (0, 3), (-1, 3), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (0, 3), (-1, 3), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 2), 9),
                ('FONTSIZE', (0, 3), (-1, 3), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d0d0d0')),
            ]))
            story.append(summary_table)
            
            # Footer is drawn on every page by the canvas callback; no inline footer paragraphs needed.
            
            # Build PDF with header/footer on each page
            doc.build(story, onFirstPage=_draw_header_footer, onLaterPages=_draw_header_footer)
            QMessageBox.information(self, "PDF Exported", f"Job card saved successfully!\n{file_path}")
        except Exception as e:
            QMessageBox.critical(self, "PDF Export Error", f"Failed to export PDF:\n{str(e)}")


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
        filter_layout.setContentsMargins(10, 8, 10, 8)
        filter_layout.setSpacing(6)
        
        # Enhanced stylesheet for better dropdown visibility
        dropdown_style = """
            QComboBox, QLineEdit, QDateEdit, QDoubleSpinBox {
                background-color: #ffffff;
                border: 1px solid #bbb;
                color: #2c2c2c;
                padding: 4px 8px;
                border-radius: 4px;
                min-height: 28px;
                font-size: 11px;
                font-weight: 500;
            }
            QComboBox:focus, QLineEdit:focus, QDateEdit:focus, QDoubleSpinBox:focus {
                border: 2px solid #2d7a5f;
                background-color: #f9f9f9;
            }
            QComboBox::drop-down {
                border: none;
                width: 25px;
                background-color: #f0f0f0;
            }
            QComboBox::down-arrow {
                width: 14px;
                height: 14px;
            }
            QAbstractItemView {
                background-color: #ffffff;
                color: #2c2c2c;
                selection-background-color: #2d7a5f;
                selection-color: white;
                padding: 4px;
                border: 1px solid #bbb;
                min-width: 220px;
            }
        """
        
        # Row 1: Search + Site + Section + Type (4 filters)
        filter_row1 = QHBoxLayout()
        filter_row1.setSpacing(5)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search...")
        self.search_input.setMaximumHeight(28)
        self.search_input.setStyleSheet(dropdown_style)
        filter_row1.addWidget(self.search_input, 1)
        
        self.site_filter = QComboBox()
        self.site_filter.addItem("All Sites")
        self.site_filter.setMaximumHeight(28)
        # allow more visible width, popup will be wider for long names
        self.site_filter.setMaximumWidth(220)
        self.site_filter.setMinimumWidth(140)
        self.site_filter.setStyleSheet(dropdown_style)
        # ensure popup/menu is wide enough to show long entries
        try:
            self.site_filter.view().setMinimumWidth(300)
        except Exception:
            pass
        filter_row1.addWidget(self.site_filter)
        
        self.section_filter = QComboBox()
        self.section_filter.addItem("All Sections")
        self.section_filter.setMaximumHeight(28)
        self.section_filter.setMaximumWidth(260)
        self.section_filter.setMinimumWidth(140)
        self.section_filter.setStyleSheet(dropdown_style)
        try:
            self.section_filter.view().setMinimumWidth(340)
        except Exception:
            pass
        filter_row1.addWidget(self.section_filter)
        
        self.type_filter = QComboBox()
        self.type_filter.addItem("All Types")
        self.type_filter.setMaximumHeight(28)
        self.type_filter.setMaximumWidth(220)
        self.type_filter.setMinimumWidth(140)
        self.type_filter.setStyleSheet(dropdown_style)
        try:
            self.type_filter.view().setMinimumWidth(300)
        except Exception:
            pass
        filter_row1.addWidget(self.type_filter)
        
        filter_layout.addLayout(filter_row1)
        
        # Row 2: Date + Status + Cost (3 filters + buttons on same row)
        filter_row2 = QHBoxLayout()
        filter_row2.setSpacing(5)
        
        self.date_filter_type = QComboBox()
        self.date_filter_type.addItems([
            "All Dates", "Date Range", "This Month", 
            "Last Month", "Last 3 Months", "Last 6 Months", "This Year"
        ])
        self.date_filter_type.setMaximumHeight(28)
        self.date_filter_type.setMaximumWidth(160)
        self.date_filter_type.setStyleSheet(dropdown_style)
        self.date_filter_type.currentTextChanged.connect(self.on_date_filter_changed)
        filter_row2.addWidget(self.date_filter_type)
        
        self.start_date = QDateEdit(QDate.currentDate().addDays(-30))
        self.start_date.setCalendarPopup(True)
        self.start_date.setDisplayFormat("yyyy-MM-dd")
        self.start_date.setVisible(False)
        self.start_date.setMaximumHeight(28)
        self.start_date.setMaximumWidth(100)
        self.start_date.setStyleSheet(dropdown_style)
        filter_row2.addWidget(self.start_date)
        
        self.end_date = QDateEdit(QDate.currentDate())
        self.end_date.setCalendarPopup(True)
        self.end_date.setDisplayFormat("yyyy-MM-dd")
        self.end_date.setVisible(False)
        self.end_date.setMaximumHeight(28)
        self.end_date.setMaximumWidth(100)
        self.end_date.setStyleSheet(dropdown_style)
        filter_row2.addWidget(self.end_date)
        
        self.status_filter = QComboBox()
        self.status_filter.addItems(["All Status", "Completed", "In Progress", "Pending"])
        self.status_filter.setMaximumHeight(28)
        self.status_filter.setMaximumWidth(160)
        try:
            self.status_filter.view().setMinimumWidth(240)
        except Exception:
            pass
        self.status_filter.setStyleSheet(dropdown_style)
        filter_row2.addWidget(self.status_filter)
        
        # Cost inputs
        self.min_cost = QDoubleSpinBox()
        self.min_cost.setPrefix("Rs.")
        self.min_cost.setMinimum(0)
        self.min_cost.setMaximum(9999999)
        self.min_cost.setValue(0)
        self.min_cost.setSingleStep(1000)
        self.min_cost.setMaximumHeight(28)
        self.min_cost.setMaximumWidth(95)
        self.min_cost.setStyleSheet(dropdown_style)
        
        self.max_cost = QDoubleSpinBox()
        self.max_cost.setPrefix("Rs.")
        self.max_cost.setMinimum(0)
        self.max_cost.setMaximum(9999999)
        self.max_cost.setValue(9999999)
        self.max_cost.setSingleStep(1000)
        self.max_cost.setMaximumHeight(28)
        self.max_cost.setMaximumWidth(95)
        self.max_cost.setStyleSheet(dropdown_style)
        
        filter_row2.addWidget(self.min_cost)
        filter_row2.addWidget(self.max_cost)
        
        # Action buttons (on same row)
        btn_apply = QPushButton("Apply")
        btn_apply.setFixedHeight(32)
        btn_apply.setMaximumWidth(65)
        btn_apply.setStyleSheet("background-color: #2d7a5f; color: white; font-weight: 600; font-size: 11px; padding: 4px;")
        btn_apply.clicked.connect(self.apply_filters)
        filter_row2.addWidget(btn_apply)

        btn_clear = QPushButton("Clear")
        btn_clear.setFixedHeight(32)
        btn_clear.setMaximumWidth(65)
        btn_clear.setStyleSheet("background-color: #8b6f47; color: white; font-weight: 600; font-size: 11px; padding: 4px;")
        btn_clear.clicked.connect(self.clear_filters)
        filter_row2.addWidget(btn_clear)

        btn_export = QPushButton("Export")
        btn_export.setFixedHeight(32)
        btn_export.setMaximumWidth(70)
        btn_export.setStyleSheet("background-color: #8b6f47; color: white; font-weight: 600; font-size: 11px; padding: 4px;")
        btn_export.clicked.connect(self.export_data)
        filter_row2.addWidget(btn_export)

        filter_row2.addStretch()
        filter_layout.addLayout(filter_row2)
        layout.addWidget(filter_card)

        # === Navigation & Action Buttons (Compact) ===
        action_bar = QHBoxLayout()
        action_bar.setSpacing(3)
        action_bar.setContentsMargins(0, 0, 0, 0)
        
        # Navigation buttons
        btn_new_job = QPushButton("New Job")
        btn_new_job.setObjectName("nav")
        btn_new_job.setFixedHeight(32)
        btn_new_job.setMaximumWidth(90)
        btn_new_job.setCursor(Qt.PointingHandCursor)
        btn_new_job.clicked.connect(self.go_to_job_card)

        btn_data_manager = QPushButton("Manager")
        btn_data_manager.setObjectName("nav")
        btn_data_manager.setFixedHeight(32)
        btn_data_manager.setMaximumWidth(80)
        btn_data_manager.setCursor(Qt.PointingHandCursor)
        btn_data_manager.clicked.connect(self.go_to_data_manager)

        action_bar.addWidget(btn_new_job)
        action_bar.addWidget(btn_data_manager)
        action_bar.addSpacing(8)

        # Record actions
        btn_view = QPushButton("View")
        btn_view.setFixedHeight(32)
        btn_view.setMaximumWidth(60)
        btn_view.setCursor(Qt.PointingHandCursor)
        btn_view.clicked.connect(self.view_details)

        btn_edit = QPushButton("Edit")
        btn_edit.setObjectName("secondary")
        btn_edit.setFixedHeight(32)
        btn_edit.setMaximumWidth(60)
        btn_edit.setCursor(Qt.PointingHandCursor)
        btn_edit.clicked.connect(self.edit_record)

        btn_delete = QPushButton("Delete")
        btn_delete.setObjectName("danger")
        btn_delete.setFixedHeight(32)
        btn_delete.setMaximumWidth(70)
        btn_delete.setCursor(Qt.PointingHandCursor)
        btn_delete.clicked.connect(self.delete_selected)

        btn_refresh = QPushButton("Refresh")
        btn_refresh.setFixedHeight(32)
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
        
        # Load vehicle types
        c.execute("SELECT DISTINCT type FROM vehicles WHERE type IS NOT NULL AND type != '' ORDER BY type")
        for row in c.fetchall():
            self.type_filter.addItem(row[0])
        
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
                   spare_parts, labour_works, outsource_works
                   FROM job_cards WHERE 1=1"""
        params = []
        
        # Search keyword
        keyword = self.search_input.text().strip()
        if keyword:
            query += " AND (job_no LIKE ? OR company_no LIKE ? OR vehicle_no LIKE ? OR driver LIKE ?)"
            params.extend([f"%{keyword}%"] * 4)
        
        # Site filter
        site_filter = self.site_filter.currentText()
        if site_filter != "All Sites":
            query += " AND site = ?"
            params.append(site_filter)
        
        # Section filter
        section_filter = self.section_filter.currentText()
        if section_filter != "All Sections":
            query += " AND section = ?"
            params.append(section_filter)
        
        # Vehicle type filter
        type_filter = self.type_filter.currentText().replace("� ", "")
        if type_filter != "All Types":
            query += " AND type = ?"
            params.append(type_filter)
        
        # Date filter
        filter_type = self.date_filter_type.currentText()
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
        
        # Filter by cost range and status
        min_cost = self.min_cost.value()
        max_cost = self.max_cost.value()
        status_filter = self.status_filter.currentText()
        
        filtered_rows = []
        for row in all_rows:
            total_cost = 0.0
            
            # Calculate total from spare parts
            try:
                spare_parts = json.loads(row[11]) if row[11] else []
                for part in spare_parts:
                    total_cost += float(part.get('total', 0))
            except:
                pass
            
            # Calculate total from labour works
            try:
                labour_works = json.loads(row[12]) if row[12] else []
                for work in labour_works:
                    total_cost += float(work.get('work_cost', 0))
            except:
                pass
            
            # Calculate total from outsource works
            try:
                outsource_works = json.loads(row[13]) if row[13] else []
                for work in outsource_works:
                    total_cost += float(work.get('cost', 0))
            except:
                pass
            
            # Check cost range
            if not (min_cost <= total_cost <= max_cost):
                continue
            
            # Check status filter
            if status_filter != "All Status":
                # Simple status logic based on end_date
                end_date_str = row[10]  # start_date column
                if end_date_str:
                    try:
                        end_date = QDate.fromString(end_date_str, "yyyy-MM-dd")
                        today = QDate.currentDate()
                        
                        if status_filter == "Completed" and end_date >= today:
                            continue
                        elif status_filter == "In Progress" and not (end_date <= today and row[10]):
                            continue
                        elif status_filter == "Pending" and total_cost > 0:
                            continue
                    except:
                        pass
            
            filtered_rows.append(row[:11])
        
        self.populate_table(filtered_rows)

    def clear_filters(self):
        self.search_input.clear()
        self.site_filter.setCurrentIndex(0)
        self.section_filter.setCurrentIndex(0)
        self.type_filter.setCurrentIndex(0)
        self.status_filter.setCurrentIndex(0)
        self.date_filter_type.setCurrentIndex(0)
        self.start_date.setDate(QDate.currentDate().addDays(-30))
        self.end_date.setDate(QDate.currentDate())
        self.min_cost.setValue(0)
        self.max_cost.setValue(9999999)
        self.load_records()
    
    def export_data(self):
        """Export filtered data to CSV with all costs"""
        try:
            csv_content = "Job No,Company No,Vehicle No,Driver,Make,Model,Type,Site,Section,Start Date,Spare Parts Cost,Labour Cost,Outsource Cost,Grand Total\n"
            
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
                c.execute("SELECT spare_parts, labour_works, outsource_works FROM job_cards WHERE id=?", (record_id,))
                data = c.fetchone()
                conn.close()
                
                spare_cost = 0.0
                labour_cost = 0.0
                outsource_cost = 0.0
                
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
                
                try:
                    outsource_works = json.loads(data[2]) if data[2] else []
                    for work in outsource_works:
                        outsource_cost += float(work.get('cost', 0))
                except:
                    pass
                
                grand_total = spare_cost + labour_cost + outsource_cost
                
                csv_content += f'"{job_no}","{company_no}","{vehicle_no}","{driver}","{make}","{model}","{type_val}","{site}","{section}","{start_date}",{spare_cost:.2f},{labour_cost:.2f},{outsource_cost:.2f},{grand_total:.2f}\n'
            
            # Ask user where to save the CSV
            from datetime import datetime
            default_name = f"job_cards_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            file_path, _ = QFileDialog.getSaveFileName(self, "Save CSV", default_name, "CSV Files (*.csv)")
            if not file_path:
                return
            # Ensure .csv extension
            if not file_path.lower().endswith('.csv'):
                file_path += '.csv'

            with open(file_path, 'w', encoding='utf-8', newline='') as f:
                f.write(csv_content)

            QMessageBox.information(self, "Export Successful ✅", f"Data exported to:\n{file_path}")
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
                     site, section, hr_km, start_date, end_date, description, spare_parts, labour_works, outsource_works
                     FROM job_cards WHERE id=?""", (record_id,))
        row = c.fetchone()
        conn.close()
        
        if row:
            job_data = {
                'job_no': row[0], 'company_no': row[1], 'vehicle_no': row[2],
                'driver': row[3], 'make': row[4], 'model': row[5], 'type': row[6],
                'site': row[7], 'section': row[8], 'hr_km': row[9],
                'start_date': row[10], 'end_date': row[11], 'description': row[12],
                'spare_parts': row[13], 'labour_works': row[14], 'outsource_works': row[15]
            }
            dialog = JobCardDetailDialog(job_data, self)
            dialog.exec()

    def edit_record(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select a record to edit.")
            return
        
        # PIN protection for edit
        pin, ok = QInputDialog.getText(
            self, "Edit Protection", "Enter PIN to edit (1234):",
            QLineEdit.Password
        )
        
        if not ok or pin != "1234":
            QMessageBox.warning(self, "Access Denied", "Incorrect PIN. Cannot edit record.")
            return
        
        record_id = int(self.table.item(selected_rows[0].row(), 0).text())
        
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("""SELECT id, job_no, company_no, vehicle_no, driver, make, model, type, 
                     site, section, hr_km, start_date, end_date, description, spare_parts, labour_works, outsource_works
                     FROM job_cards WHERE id=?""", (record_id,))
        row = c.fetchone()
        conn.close()
        
        if row:
            job_data = {
                'id': row[0], 'job_no': row[1], 'company_no': row[2], 'vehicle_no': row[3],
                'driver': row[4], 'make': row[5], 'model': row[6], 'type': row[7],
                'site': row[8], 'section': row[9], 'hr_km': row[10],
                'start_date': row[11], 'end_date': row[12], 'description': row[13],
                'spare_parts': row[14], 'labour_works': row[15], 'outsource_works': row[16]
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