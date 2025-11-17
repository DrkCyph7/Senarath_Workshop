import sqlite3
import json
import os
import datetime
from xml.sax.saxutils import escape
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QTableWidget, QTableWidgetItem, QMessageBox, QComboBox,
    QDateEdit, QCheckBox, QFrame, QDialog, QTextEdit, QGridLayout,
    QDialogButtonBox, QScrollArea, QSpinBox, QDoubleSpinBox, QTabWidget,
    QHeaderView, QFileDialog, QInputDialog, QRadioButton, QCompleter
)
from PySide6.QtCore import Qt, QDate, QTimer
from PySide6.QtGui import QFont, QColor, QPixmap
from ui.theme import ColorPalette, Typography, Spacing, Styles, create_page_header

DB_PATH = "ui/db/senarath.db"

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    from reportlab.pdfgen import canvas
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False
    
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


class SparePartEditDialog(QDialog):
    """Compact editor for spare parts."""

    def __init__(self, spare_parts_json, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Spare Parts")
        self.setMinimumSize(860, 520)

        try:
            self.spare_parts_data = json.loads(spare_parts_json) if spare_parts_json else []
        except Exception:
            self.spare_parts_data = []

        self.setStyleSheet(f"""
            QDialog {{
                background-color: {ColorPalette.BG_SECONDARY};
            }}
            QLabel#dialog_title {{
                color: {ColorPalette.TEXT_PRIMARY};
                font-size: 16px;
                font-weight: 700;
            }}
            QLabel#dialog_subtitle {{
                color: {ColorPalette.TEXT_SECONDARY};
                font-size: 12px;
            }}
            QFrame#table_card {{
                background-color: {ColorPalette.BG_PRIMARY};
                border: 1px solid {ColorPalette.BORDER_LIGHT};
                border-radius: {Spacing.BORDER_RADIUS_MEDIUM}px;
            }}
            QTableWidget {{
                background-color: {ColorPalette.BG_PRIMARY};
                border: none;
                gridline-color: {ColorPalette.BORDER_LIGHT};
                alternate-background-color: #f9fafb;
            }}
            QHeaderView::section {{
                background-color: {ColorPalette.ACCENT_PRIMARY};
                color: white;
                padding: 8px;
                border: none;
                font-weight: 600;
            }}
        """)

        root = QVBoxLayout(self)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(14)

        header = QVBoxLayout()
        header.setSpacing(2)
        title = QLabel("Spare Parts & Materials")
        title.setObjectName("dialog_title")
        subtitle = QLabel("Maintain the parts list for this job card.")
        subtitle.setObjectName("dialog_subtitle")
        header.addWidget(title)
        header.addWidget(subtitle)
        root.addLayout(header)

        actions = QHBoxLayout()
        actions.setSpacing(8)

        add_btn = QPushButton("+ Add")
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.setFixedWidth(110)
        add_btn.setStyleSheet(Styles.get_button_primary())
        add_btn.clicked.connect(self.add_part)

        edit_btn = QPushButton("Edit")
        edit_btn.setCursor(Qt.PointingHandCursor)
        edit_btn.setFixedWidth(110)
        edit_btn.setStyleSheet(Styles.get_button_secondary())
        edit_btn.clicked.connect(self.edit_part)

        delete_btn = QPushButton("Delete")
        delete_btn.setCursor(Qt.PointingHandCursor)
        delete_btn.setFixedWidth(110)
        delete_btn.setStyleSheet(Styles.get_button_danger())
        delete_btn.clicked.connect(self.delete_part)

        actions.addWidget(add_btn)
        actions.addWidget(edit_btn)
        actions.addWidget(delete_btn)
        actions.addStretch()
        root.addLayout(actions)

        table_card = QFrame()
        table_card.setObjectName("table_card")
        table_layout = QVBoxLayout(table_card)
        table_layout.setContentsMargins(12, 12, 12, 12)
        table_layout.setSpacing(12)

        # Updated to reflect DB-driven spare part fields
        self.table = QTableWidget(0, 8)
        self.table.setHorizontalHeaderLabels(["#", "ID Code", "Description", "Category", "Quantity", "Unit", "Unit Price", "Total"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setFocusPolicy(Qt.NoFocus)
        table_layout.addWidget(self.table)

        summary_row = QHBoxLayout()
        summary_row.addStretch()
        self.grand_total_label = QLabel("Total: Rs. 0.00")
        self.grand_total_label.setStyleSheet(
            f"color: {ColorPalette.ACCENT_PRIMARY}; font-weight: 600;"
            f" background-color: rgba(46, 125, 110, 0.12); padding: 6px 12px;"
            f" border-radius: {Spacing.BORDER_RADIUS_SMALL}px;"
        )
        summary_row.addWidget(self.grand_total_label)
        table_layout.addLayout(summary_row)

        root.addWidget(table_card)

        footer = QHBoxLayout()
        footer.setSpacing(10)
        footer.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.setFixedWidth(100)
        cancel_btn.setStyleSheet(Styles.get_button_secondary())
        cancel_btn.clicked.connect(self.reject)

        save_btn = QPushButton("Save")
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.setFixedWidth(110)
        save_btn.setStyleSheet(Styles.get_button_primary())
        save_btn.clicked.connect(self.accept)

        footer.addWidget(cancel_btn)
        footer.addWidget(save_btn)
        root.addLayout(footer)

        self.refresh_table()

    def refresh_table(self):
        self.table.setRowCount(len(self.spare_parts_data))
        grand_total = 0.0
        for row_idx, part in enumerate(self.spare_parts_data):
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(row_idx + 1)))
            self.table.setItem(row_idx, 1, QTableWidgetItem(part.get("id_code", "")))
            self.table.setItem(row_idx, 2, QTableWidgetItem(part.get("description", "")))
            self.table.setItem(row_idx, 3, QTableWidgetItem(part.get("category", "")))
            self.table.setItem(row_idx, 4, QTableWidgetItem(str(part.get("quantity", ""))))
            self.table.setItem(row_idx, 5, QTableWidgetItem(part.get("unit", "")))
            self.table.setItem(row_idx, 6, QTableWidgetItem(str(part.get("unit_price", ""))))
            self.table.setItem(row_idx, 7, QTableWidgetItem(str(part.get("total", ""))))
            try:
                grand_total += float(part.get("total", 0) or 0)
            except (ValueError, TypeError):
                pass
        self.grand_total_label.setText(f"Total: Rs. {grand_total:,.2f}")
        self.table.resizeRowsToContents()

    def add_part(self):
        from ui.pages.job_card_page import SparePartDialog

        dialog = SparePartDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            if data.get("description", "").strip():
                self.spare_parts_data.append(data)
                self.refresh_table()

    def edit_part(self):
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "No Selection", "Select a spare part to edit.")
            return

        from ui.pages.job_card_page import SparePartDialog

        current_data = self.spare_parts_data[current_row]
        dialog = SparePartDialog(self, edit_data=current_data)
        if dialog.exec():
            data = dialog.get_data()
            if data.get("description", "").strip():
                self.spare_parts_data[current_row] = data
                self.refresh_table()

    def delete_part(self):
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "No Selection", "Select a spare part to delete.")
            return

        confirm = QMessageBox.question(
            self,
            "Confirm Delete",
            "Remove the selected spare part?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if confirm == QMessageBox.Yes:
            del self.spare_parts_data[current_row]
            self.refresh_table()

    def get_data(self):
        return json.dumps(self.spare_parts_data)


class LabourWorkEditDialog(QDialog):
    """Compact editor for labour works."""

    def __init__(self, labour_works_json, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Labour Works")
        self.setMinimumSize(900, 540)

        try:
            self.labour_works_data = json.loads(labour_works_json) if labour_works_json else []
        except Exception:
            self.labour_works_data = []

        self.setStyleSheet(f"""
            QDialog {{
                background-color: {ColorPalette.BG_SECONDARY};
            }}
            QLabel#dialog_title {{
                color: {ColorPalette.TEXT_PRIMARY};
                font-size: 16px;
                font-weight: 700;
            }}
            QLabel#dialog_subtitle {{
                color: {ColorPalette.TEXT_SECONDARY};
                font-size: 12px;
            }}
            QFrame#table_card {{
                background-color: {ColorPalette.BG_PRIMARY};
                border: 1px solid {ColorPalette.BORDER_LIGHT};
                border-radius: {Spacing.BORDER_RADIUS_MEDIUM}px;
            }}
            QTableWidget {{
                background-color: {ColorPalette.BG_PRIMARY};
                border: none;
                gridline-color: {ColorPalette.BORDER_LIGHT};
                alternate-background-color: #f9fafb;
            }}
            QHeaderView::section {{
                background-color: {ColorPalette.ACCENT_PRIMARY};
                color: white;
                padding: 8px;
                border: none;
                font-weight: 600;
            }}
        """)

        root = QVBoxLayout(self)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(14)

        header = QVBoxLayout()
        header.setSpacing(2)
        title = QLabel("Labour Works & Time Entries")
        title.setObjectName("dialog_title")
        subtitle = QLabel("Track labour usage, hours, and costs.")
        subtitle.setObjectName("dialog_subtitle")
        header.addWidget(title)
        header.addWidget(subtitle)
        root.addLayout(header)

        actions = QHBoxLayout()
        actions.setSpacing(8)

        add_btn = QPushButton("+ Add")
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.setFixedWidth(110)
        add_btn.setStyleSheet(Styles.get_button_primary())
        add_btn.clicked.connect(self.add_work)

        edit_btn = QPushButton("Edit")
        edit_btn.setCursor(Qt.PointingHandCursor)
        edit_btn.setFixedWidth(110)
        edit_btn.setStyleSheet(Styles.get_button_secondary())
        edit_btn.clicked.connect(self.edit_work)

        delete_btn = QPushButton("Delete")
        delete_btn.setCursor(Qt.PointingHandCursor)
        delete_btn.setFixedWidth(110)
        delete_btn.setStyleSheet(Styles.get_button_danger())
        delete_btn.clicked.connect(self.delete_work)

        actions.addWidget(add_btn)
        actions.addWidget(edit_btn)
        actions.addWidget(delete_btn)
        actions.addStretch()
        root.addLayout(actions)

        table_card = QFrame()
        table_card.setObjectName("table_card")
        table_layout = QVBoxLayout(table_card)
        table_layout.setContentsMargins(12, 12, 12, 12)
        table_layout.setSpacing(12)

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["#", "Date", "Description", "Hours", "Labour Team", "Cost"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setFocusPolicy(Qt.NoFocus)
        table_layout.addWidget(self.table)

        summary_row = QHBoxLayout()
        summary_row.setSpacing(8)
        summary_row.addStretch()
        self.total_hours_label = QLabel("Hours: 0.00")
        self.total_hours_label.setStyleSheet(
            f"color: {ColorPalette.TEXT_SECONDARY}; font-weight: 600;"
            f" background-color: rgba(17, 24, 39, 0.05); padding: 6px 12px;"
            f" border-radius: {Spacing.BORDER_RADIUS_SMALL}px;"
        )
        summary_row.addWidget(self.total_hours_label)

        self.total_cost_label = QLabel("Total: Rs. 0.00")
        self.total_cost_label.setStyleSheet(
            f"color: {ColorPalette.ACCENT_PRIMARY}; font-weight: 600;"
            f" background-color: rgba(46, 125, 110, 0.12); padding: 6px 12px;"
            f" border-radius: {Spacing.BORDER_RADIUS_SMALL}px;"
        )
        summary_row.addWidget(self.total_cost_label)
        table_layout.addLayout(summary_row)

        root.addWidget(table_card)

        footer = QHBoxLayout()
        footer.setSpacing(10)
        footer.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.setFixedWidth(100)
        cancel_btn.setStyleSheet(Styles.get_button_secondary())
        cancel_btn.clicked.connect(self.reject)

        save_btn = QPushButton("Save")
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.setFixedWidth(110)
        save_btn.setStyleSheet(Styles.get_button_primary())
        save_btn.clicked.connect(self.accept)

        footer.addWidget(cancel_btn)
        footer.addWidget(save_btn)
        root.addLayout(footer)

        self.refresh_table()

    def refresh_table(self):
        self.table.setRowCount(len(self.labour_works_data))
        total_hours = 0.0
        total_cost = 0.0
        for row_idx, work in enumerate(self.labour_works_data):
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(row_idx + 1)))
            self.table.setItem(row_idx, 1, QTableWidgetItem(work.get("work_date", "")))
            self.table.setItem(row_idx, 2, QTableWidgetItem(work.get("description", "")))
            self.table.setItem(row_idx, 3, QTableWidgetItem(str(work.get("hours", ""))))
            labour_names = []
            try:
                raw_list = work.get("labour_list", "[]")
                labour_items = json.loads(raw_list) if isinstance(raw_list, str) else raw_list
                labour_names = [item.get("name", "") for item in labour_items]
            except Exception:
                labour_names = []
            self.table.setItem(row_idx, 4, QTableWidgetItem(", ".join([name for name in labour_names if name])))
            self.table.setItem(row_idx, 5, QTableWidgetItem(str(work.get("work_cost", ""))))
            try:
                total_hours += float(work.get("hours", 0) or 0)
            except (ValueError, TypeError):
                pass
            try:
                total_cost += float(work.get("work_cost", 0) or 0)
            except (ValueError, TypeError):
                pass
        self.total_hours_label.setText(f"Hours: {total_hours:.2f}")
        self.total_cost_label.setText(f"Total: Rs. {total_cost:,.2f}")
        self.table.resizeRowsToContents()

    def add_work(self):
        from ui.pages.job_card_page import LabourWorkDialog

        labour_names = []
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM labour ORDER BY name")
            labour_names = [row[0] for row in cursor.fetchall()]
            conn.close()
        except Exception:
            labour_names = []

        dialog = LabourWorkDialog(parent=self, labour_list=labour_names)
        if dialog.exec():
            data = dialog.get_data()
            if data.get("description", "").strip():
                self.labour_works_data.append(data)
                self.refresh_table()

    def edit_work(self):
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "No Selection", "Select a labour work to edit.")
            return

        from ui.pages.job_card_page import LabourWorkDialog

        labour_names = []
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM labour ORDER BY name")
            labour_names = [row[0] for row in cursor.fetchall()]
            conn.close()
        except Exception:
            labour_names = []

        current_data = self.labour_works_data[current_row]
        dialog = LabourWorkDialog(parent=self, edit_data=current_data, labour_list=labour_names)
        if dialog.exec():
            data = dialog.get_data()
            if data.get("description", "").strip():
                self.labour_works_data[current_row] = data
                self.refresh_table()

    def delete_work(self):
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "No Selection", "Select a labour work to delete.")
            return

        confirm = QMessageBox.question(
            self,
            "Confirm Delete",
            "Remove the selected labour work?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if confirm == QMessageBox.Yes:
            del self.labour_works_data[current_row]
            self.refresh_table()

    def get_data(self):
        return json.dumps(self.labour_works_data)


class OutsourceWorkEditDialog(QDialog):
    """Compact editor for outsource works."""

    def __init__(self, outsource_works_json, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Outsource Works")
        self.setMinimumSize(860, 500)

        try:
            self.outsource_works_data = json.loads(outsource_works_json) if outsource_works_json else []
        except Exception:
            self.outsource_works_data = []

        self.setStyleSheet(f"""
            QDialog {{
                background-color: {ColorPalette.BG_SECONDARY};
            }}
            QLabel#dialog_title {{
                color: {ColorPalette.TEXT_PRIMARY};
                font-size: 16px;
                font-weight: 700;
            }}
            QLabel#dialog_subtitle {{
                color: {ColorPalette.TEXT_SECONDARY};
                font-size: 12px;
            }}
            QFrame#table_card {{
                background-color: {ColorPalette.BG_PRIMARY};
                border: 1px solid {ColorPalette.BORDER_LIGHT};
                border-radius: {Spacing.BORDER_RADIUS_MEDIUM}px;
            }}
            QTableWidget {{
                background-color: {ColorPalette.BG_PRIMARY};
                border: none;
                gridline-color: {ColorPalette.BORDER_LIGHT};
                alternate-background-color: #f9fafb;
            }}
            QHeaderView::section {{
                background-color: {ColorPalette.ACCENT_PRIMARY};
                color: white;
                padding: 8px;
                border: none;
                font-weight: 600;
            }}
        """)

        root = QVBoxLayout(self)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(14)

        header = QVBoxLayout()
        header.setSpacing(2)
        title = QLabel("Outsource Works")
        title.setObjectName("dialog_title")
        subtitle = QLabel("Capture external services, costs, and remarks.")
        subtitle.setObjectName("dialog_subtitle")
        header.addWidget(title)
        header.addWidget(subtitle)
        root.addLayout(header)

        actions = QHBoxLayout()
        actions.setSpacing(8)

        add_btn = QPushButton("+ Add")
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.setFixedWidth(110)
        add_btn.setStyleSheet(Styles.get_button_primary())
        add_btn.clicked.connect(self.add_work)

        edit_btn = QPushButton("Edit")
        edit_btn.setCursor(Qt.PointingHandCursor)
        edit_btn.setFixedWidth(110)
        edit_btn.setStyleSheet(Styles.get_button_secondary())
        edit_btn.clicked.connect(self.edit_work)

        delete_btn = QPushButton("Delete")
        delete_btn.setCursor(Qt.PointingHandCursor)
        delete_btn.setFixedWidth(110)
        delete_btn.setStyleSheet(Styles.get_button_danger())
        delete_btn.clicked.connect(self.delete_work)

        actions.addWidget(add_btn)
        actions.addWidget(edit_btn)
        actions.addWidget(delete_btn)
        actions.addStretch()
        root.addLayout(actions)

        table_card = QFrame()
        table_card.setObjectName("table_card")
        table_layout = QVBoxLayout(table_card)
        table_layout.setContentsMargins(12, 12, 12, 12)
        table_layout.setSpacing(12)

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["#", "Date", "Work Type", "Description", "Cost", "Remarks"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setFocusPolicy(Qt.NoFocus)
        table_layout.addWidget(self.table)

        summary_row = QHBoxLayout()
        summary_row.addStretch()
        self.total_cost_label = QLabel("Total: Rs. 0.00")
        self.total_cost_label.setStyleSheet(
            f"color: {ColorPalette.ACCENT_PRIMARY}; font-weight: 600;"
            f" background-color: rgba(46, 125, 110, 0.12); padding: 6px 12px;"
            f" border-radius: {Spacing.BORDER_RADIUS_SMALL}px;"
        )
        summary_row.addWidget(self.total_cost_label)
        table_layout.addLayout(summary_row)

        root.addWidget(table_card)

        footer = QHBoxLayout()
        footer.setSpacing(10)
        footer.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.setFixedWidth(100)
        cancel_btn.setStyleSheet(Styles.get_button_secondary())
        cancel_btn.clicked.connect(self.reject)

        save_btn = QPushButton("Save")
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.setFixedWidth(110)
        save_btn.setStyleSheet(Styles.get_button_primary())
        save_btn.clicked.connect(self.accept)

        footer.addWidget(cancel_btn)
        footer.addWidget(save_btn)
        root.addLayout(footer)

        self.refresh_table()

    def refresh_table(self):
        self.table.setRowCount(len(self.outsource_works_data))
        total_cost = 0.0
        for row_idx, work in enumerate(self.outsource_works_data):
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(row_idx + 1)))
            self.table.setItem(row_idx, 1, QTableWidgetItem(work.get("work_date", "")))
            self.table.setItem(row_idx, 2, QTableWidgetItem(work.get("work_type", "")))
            self.table.setItem(row_idx, 3, QTableWidgetItem(work.get("description", "")))
            self.table.setItem(row_idx, 4, QTableWidgetItem(str(work.get("cost", ""))))
            self.table.setItem(row_idx, 5, QTableWidgetItem(work.get("remark", "")))
            try:
                total_cost += float(work.get("cost", 0) or 0)
            except (ValueError, TypeError):
                pass
        self.total_cost_label.setText(f"Total: Rs. {total_cost:,.2f}")
        self.table.resizeRowsToContents()

    def add_work(self):
        from ui.pages.job_card_page import OutsourceWorkDialog

        dialog = OutsourceWorkDialog(parent=self)
        if dialog.exec():
            data = dialog.get_data()
            if data.get("description", "").strip():
                self.outsource_works_data.append(data)
                self.refresh_table()

    def edit_work(self):
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "No Selection", "Select an outsource work to edit.")
            return

        from ui.pages.job_card_page import OutsourceWorkDialog

        current_data = self.outsource_works_data[current_row]
        dialog = OutsourceWorkDialog(parent=self, edit_data=current_data)
        if dialog.exec():
            data = dialog.get_data()
            if data.get("description", "").strip():
                self.outsource_works_data[current_row] = data
                self.refresh_table()

    def delete_work(self):
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "No Selection", "Select an outsource work to delete.")
            return

        confirm = QMessageBox.question(
            self,
            "Confirm Delete",
            "Remove the selected outsource work?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if confirm == QMessageBox.Yes:
            del self.outsource_works_data[current_row]
            self.refresh_table()

    def get_data(self):
        return json.dumps(self.outsource_works_data)


class JobCardEditDialog(QDialog):
    def __init__(self, job_data, parent=None):
        super().__init__(parent)
        # Ultra-compact edit dialog
        self.setWindowTitle(f"Edit Job Card — {job_data.get('job_no', 'N/A')}")
        self.setMinimumSize(800, 440)
        self.resize(840, 460)
        self.job_id = job_data.get('id')

        # Load dropdown data
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT company_no, number, make, model, type FROM vehicles")
        self.vehicles = c.fetchall()
        c.execute("SELECT name FROM drivers")
        self.drivers = [row[0] for row in c.fetchall()]
        c.execute("SELECT name FROM sites")
        self.sites = [row[0] for row in c.fetchall()]
        c.execute("SELECT name FROM sections")
        self.sections = [row[0] for row in c.fetchall()]
        conn.close()

        # Ultra-compact styling using theme (reduced paddings)
        self.setStyleSheet(f"""
            QDialog {{ background-color: {ColorPalette.BG_SECONDARY}; }}
            QLabel {{ color: {ColorPalette.TEXT_PRIMARY}; font-size: 11px; }}
            QLineEdit, QComboBox, QDateEdit {{
                background-color: {ColorPalette.BG_PRIMARY};
                border: 1px solid {ColorPalette.BORDER_LIGHT};
                border-radius: {Spacing.BORDER_RADIUS_SMALL}px;
                padding: 4px 6px;
                min-height: 26px;
                font-size: 12px;
            }}
            QTextEdit {{ background-color: {ColorPalette.BG_PRIMARY}; border: 1px solid {ColorPalette.BORDER_LIGHT}; padding: 6px; min-height: 72px; font-size: 12px; }}
            QTabBar::tab {{ padding: 6px 10px; font-size: 12px; }}
        """)

        # Layout: vertical compact
        main = QVBoxLayout(self)
        main.setContentsMargins(10, 10, 10, 10)
        main.setSpacing(8)

        # Top quick facts presented as soft chips
        info_row = QHBoxLayout()
        info_row.setSpacing(6)
        info_row.setContentsMargins(0, 0, 0, 0)

        def build_chip(label_text, value_text):
            pill = QLabel(f"{label_text}: {value_text or '—'}")
            pill.setStyleSheet(
                "padding: 4px 10px; border-radius: 12px; "
                f"background-color: {ColorPalette.BG_PRIMARY}; border: 1px solid {ColorPalette.BORDER_LIGHT}; "
                f"color: {ColorPalette.TEXT_SECONDARY}; font-size: 11px;"
            )
            return pill

        chip_data = [
            ("Driver", job_data.get('driver', '—')),
            ("Vehicle", job_data.get('vehicle_no', '—')),
            ("Site", job_data.get('site', '—')),
            ("Section", job_data.get('section', '—')),
            ("Schedule", f"{job_data.get('start_date', 'N/A')} → {job_data.get('end_date', 'N/A')}")
        ]
        for label_text, value_text in chip_data:
            info_row.addWidget(build_chip(label_text, value_text))
        info_row.addStretch()
        main.addLayout(info_row)

        # Content split: left = general info, right = works summary
        content_row = QHBoxLayout()
        content_row.setSpacing(10)

        # General details card
        details_card = QFrame()
        details_card.setStyleSheet(
            f"QFrame {{ background-color: {ColorPalette.BG_PRIMARY}; border: 1px solid {ColorPalette.BORDER_LIGHT}; "
            f"border-radius: {Spacing.BORDER_RADIUS_SMALL}px; }}"
        )
        details_layout = QVBoxLayout(details_card)
        details_layout.setContentsMargins(10, 10, 10, 10)
        details_layout.setSpacing(8)

        heading = QLabel('General Information')
        heading.setStyleSheet(f"color: {ColorPalette.ACCENT_PRIMARY}; font-weight: 600; font-size: 12px;")
        details_layout.addWidget(heading)

        form_layout = QGridLayout()
        form_layout.setHorizontalSpacing(10)
        form_layout.setVerticalSpacing(6)
        form_layout.setColumnStretch(1, 1)
        form_layout.setColumnStretch(3, 1)

        # Inputs (compact two columns)
        self.job_no_input = QLineEdit(job_data.get('job_no', ''))
        self.job_no_input.setReadOnly(True)
        self.job_no_input.setStyleSheet('background-color: #f5f5f5;')

        self.driver_input = QComboBox()
        self.driver_input.setEditable(True)
        self.driver_input.addItems(self.drivers)
        self.driver_input.setCurrentText(job_data.get('driver',''))
        self.company_no_input = QComboBox()
        self.company_no_input.setEditable(True)
        self.company_no_input.addItems(list(set([v[0] for v in self.vehicles if v[0]])))
        self.company_no_input.setCurrentText(job_data.get('company_no',''))
        self.company_no_input.currentTextChanged.connect(self.auto_fill_from_company)
        self.site_input = QComboBox()
        self.site_input.addItems(self.sites)
        self.site_input.setCurrentText(job_data.get('site',''))
        self.vehicle_input = QComboBox()
        self.vehicle_input.setEditable(True)
        self.vehicle_input.addItems(list(set([v[1] for v in self.vehicles if v[1] and v[1] != '-'])))
        self.vehicle_input.setCurrentText(job_data.get('vehicle_no',''))
        self.vehicle_input.currentTextChanged.connect(self.auto_fill_from_vehicle)
        self.section_input = QComboBox()
        self.section_input.addItems(self.sections)
        self.section_input.setCurrentText(job_data.get('section',''))

        self.make_input = QLineEdit(job_data.get('make',''))
        self.make_input.setReadOnly(True)
        self.model_input = QLineEdit(job_data.get('model',''))
        self.model_input.setReadOnly(True)
        self.type_input = QLineEdit(job_data.get('type',''))
        self.type_input.setReadOnly(True)
        self.hr_km_input = QLineEdit(job_data.get('hr_km',''))
        self.start_date_input = QDateEdit()
        self.start_date_input.setCalendarPopup(True)
        self.start_date_input.setDisplayFormat('yyyy-MM-dd')
        if job_data.get('start_date',''):
            self.start_date_input.setDate(QDate.fromString(job_data.get('start_date',''), 'yyyy-MM-dd'))
        self.end_date_input = QDateEdit()
        self.end_date_input.setCalendarPopup(True)
        self.end_date_input.setDisplayFormat('yyyy-MM-dd')
        if job_data.get('end_date',''):
            self.end_date_input.setDate(QDate.fromString(job_data.get('end_date',''), 'yyyy-MM-dd'))
        
        # Status dropdown
        self.status_input = QComboBox()
        self.status_input.setEditable(False)
        self.status_input.addItems(['In Progress', 'Completed'])
        self.status_input.setCurrentText(job_data.get('status', 'In Progress'))
        self.status_input.setStyleSheet(f"""
            QComboBox {{
                background-color: {ColorPalette.BG_PRIMARY};
                border: 1px solid {ColorPalette.BORDER_LIGHT};
                border-radius: {Spacing.BORDER_RADIUS_SMALL}px;
                padding: 4px 6px;
                padding-right: 25px;
                min-height: 26px;
                font-size: 12px;
            }}
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left: 1px solid {ColorPalette.BORDER_LIGHT};
            }}
            QComboBox::down-arrow {{
                image: none;
                width: 0;
                height: 0;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid {ColorPalette.TEXT_PRIMARY};
            }}
            QComboBox:hover {{
                border: 1px solid {ColorPalette.ACCENT_PRIMARY};
            }}
            QComboBox QAbstractItemView {{
                background-color: white;
                border: 1px solid {ColorPalette.BORDER_LIGHT};
                selection-background-color: {ColorPalette.ACCENT_PRIMARY};
                selection-color: white;
            }}
        """)

        # place fields compactly (two-column small form)
        form_layout.addWidget(QLabel('Job No:'), 0, 0); form_layout.addWidget(self.job_no_input, 0, 1)
        form_layout.addWidget(QLabel('Driver:'), 0, 2); form_layout.addWidget(self.driver_input, 0, 3)
        form_layout.addWidget(QLabel('Company No:'), 1, 0); form_layout.addWidget(self.company_no_input, 1, 1)
        form_layout.addWidget(QLabel('Site:'), 1, 2); form_layout.addWidget(self.site_input, 1, 3)
        form_layout.addWidget(QLabel('Vehicle No:'), 2, 0); form_layout.addWidget(self.vehicle_input, 2, 1)
        form_layout.addWidget(QLabel('Section:'), 2, 2); form_layout.addWidget(self.section_input, 2, 3)
        form_layout.addWidget(QLabel('Make:'), 3, 0); form_layout.addWidget(self.make_input, 3, 1)
        form_layout.addWidget(QLabel('Hr/Km:'), 3, 2); form_layout.addWidget(self.hr_km_input, 3, 3)
        form_layout.addWidget(QLabel('Model:'), 4, 0); form_layout.addWidget(self.model_input, 4, 1)
        form_layout.addWidget(QLabel('Start Date:'), 4, 2); form_layout.addWidget(self.start_date_input, 4, 3)
        form_layout.addWidget(QLabel('Type:'), 5, 0); form_layout.addWidget(self.type_input, 5, 1)
        form_layout.addWidget(QLabel('End Date:'), 5, 2); form_layout.addWidget(self.end_date_input, 5, 3)
        form_layout.addWidget(QLabel('Status:'), 6, 0); form_layout.addWidget(self.status_input, 6, 1)

        details_layout.addLayout(form_layout)

        # Description (compact)
        desc = QLabel('Job Description')
        desc.setStyleSheet(f'color: {ColorPalette.ACCENT_PRIMARY}; font-weight: 600;')
        details_layout.addWidget(desc)
        self.description_input = QTextEdit()
        self.description_input.setPlainText(job_data.get('description',''))
        self.description_input.setMaximumHeight(90)
        self.description_input.setPlaceholderText('Add a clear description of the work completed...')
        details_layout.addWidget(self.description_input)

        content_row.addWidget(details_card, 1)

        # Works summary card (right column)
        works_card = QFrame()
        works_card.setStyleSheet(
            f"QFrame {{ background-color: {ColorPalette.BG_PRIMARY}; border: 1px solid {ColorPalette.BORDER_LIGHT}; "
            f"border-radius: {Spacing.BORDER_RADIUS_SMALL}px; }}"
        )
        works_layout = QVBoxLayout(works_card)
        works_layout.setContentsMargins(10, 10, 10, 10)
        works_layout.setSpacing(10)

        works_heading = QLabel('Work Breakdown')
        works_heading.setStyleSheet(f"color: {ColorPalette.ACCENT_PRIMARY}; font-weight: 600; font-size: 12px;")
        works_layout.addWidget(works_heading)

        def add_summary_section(title_text, edit_handler):
            section = QVBoxLayout()
            section.setSpacing(4)

            header_line = QHBoxLayout()
            header_line.setSpacing(4)
            title_label = QLabel(title_text)
            title_label.setStyleSheet(f"color: {ColorPalette.TEXT_PRIMARY}; font-weight: 600; font-size: 12px;")
            edit_button = QPushButton('Edit')
            edit_button.setObjectName('secondary')
            edit_button.setFixedHeight(24)
            edit_button.setFixedWidth(64)
            edit_button.clicked.connect(edit_handler)
            header_line.addWidget(title_label)
            header_line.addStretch()
            header_line.addWidget(edit_button)
            section.addLayout(header_line)

            summary_label = QLabel('No data added yet.')
            summary_label.setStyleSheet(f"color: {ColorPalette.TEXT_SECONDARY}; font-size: 11px;")
            summary_label.setWordWrap(True)
            section.addWidget(summary_label)

            works_layout.addLayout(section)
            return summary_label

        self.spare_summary_label = add_summary_section('Spare Parts', self.edit_spare_parts)
        self.labour_summary_label = add_summary_section('Labour Works', self.edit_labour_works)
        self.outsource_summary_label = add_summary_section('Outsource Works', self.edit_outsource_works)

        works_layout.addStretch()
        content_row.addWidget(works_card)

        main.addLayout(content_row)

        # store data and init summaries
        self.spare_parts_data = job_data.get('spare_parts', '[]')
        self.labour_works_data = job_data.get('labour_works', '[]')
        self.outsource_works_data = job_data.get('outsource_works', '[]')
        self.refresh_works_summary()

        # compact footer: Save / Cancel small
        footer = QHBoxLayout(); footer.setSpacing(8)
        footer.addStretch()
        cancel = QPushButton('Cancel'); cancel.setFixedHeight(30); cancel.setFixedWidth(90); cancel.setObjectName('secondary'); cancel.clicked.connect(self.reject)
        save = QPushButton('Save'); save.setFixedHeight(30); save.setFixedWidth(100); save.clicked.connect(self.save_changes); save.setDefault(True)
        footer.addWidget(cancel); footer.addWidget(save)
        main.addLayout(footer)
    
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
            self.refresh_works_summary()
    
    def edit_labour_works(self):
        dialog = LabourWorkEditDialog(self.labour_works_data, self)
        if dialog.exec():
            self.labour_works_data = dialog.get_data()
            self.refresh_works_summary()
    
    def edit_outsource_works(self):
        dialog = OutsourceWorkEditDialog(self.outsource_works_data, self)
        if dialog.exec():
            self.outsource_works_data = dialog.get_data()
            self.refresh_works_summary()

    def refresh_works_summary(self):
        """Refresh the summary labels in the Works tab.
        Handles both JSON string and Python list representations.
        """
        def _parse(data):
            if not data:
                return []
            if isinstance(data, str):
                try:
                    return json.loads(data)
                except Exception:
                    return []
            if isinstance(data, list):
                return data
            return []

        spares = _parse(self.spare_parts_data)
        labours = _parse(self.labour_works_data)
        outs = _parse(self.outsource_works_data)

        # Spare parts totals
        spare_count = len(spares)
        spare_total = 0.0
        for p in spares:
            try:
                spare_total += float(p.get('total', 0))
            except Exception:
                pass
        self.spare_summary_label.setText(f"{spare_count} parts — Total: Rs. {spare_total:,.2f}")

        # Labour totals
        labour_count = len(labours)
        labour_hours = 0.0
        labour_total = 0.0
        for l in labours:
            try:
                labour_hours += float(l.get('hours', 0))
            except Exception:
                pass
            try:
                labour_total += float(l.get('work_cost', 0))
            except Exception:
                pass
        self.labour_summary_label.setText(f"{labour_count} entries — Hours: {labour_hours:.2f} — Cost: Rs. {labour_total:,.2f}")

        # Outsource totals
        out_count = len(outs)
        out_total = 0.0
        for o in outs:
            try:
                out_total += float(o.get('cost', 0))
            except Exception:
                pass
        self.outsource_summary_label.setText(f"{out_count} entries — Total: Rs. {out_total:,.2f}")
    
    def save_changes(self):
        if not self.company_no_input.currentText().strip():
            QMessageBox.warning(self, "Missing Field", "Company No is required.")
            return
        
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute(
                "UPDATE job_cards SET company_no=?, vehicle_no=?, driver=?, make=?, model=?, type=?, "
                "site=?, section=?, hr_km=?, start_date=?, end_date=?, description=?, spare_parts=?, "
                "labour_works=?, outsource_works=?, status=? WHERE id=?",
                (
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
                    self.status_input.currentText(),
                    self.job_id
                )
            )
            
            conn.commit()
            conn.close()
            
            QMessageBox.information(self, "Success ✅", "Job card updated successfully!")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update job card:\n{str(e)}")


class JobCardDetailDialog(QDialog):
    """Professional view for job card details."""

    def __init__(self, job_data, parent=None):
        super().__init__(parent)
        self.job_data = job_data
        self.setWindowTitle(f"Job Card Details — {job_data.get('job_no', 'N/A')}")
        self.setMinimumSize(1100, 780)

        self.spare_parts = self._load_items(job_data.get('spare_parts'))
        self.labour_works = self._load_items(job_data.get('labour_works'))
        self.outsource_works = self._load_items(job_data.get('outsource_works'))

        self.spare_total = self._sum_numeric(self.spare_parts, 'total')
        self.labour_total = self._sum_numeric(self.labour_works, 'work_cost')
        self.labour_hours = self._sum_numeric(self.labour_works, 'hours')
        self.outsource_total = self._sum_numeric(self.outsource_works, 'cost')
        self.grand_total = self.spare_total + self.labour_total + self.outsource_total

        self.setStyleSheet(f"""
            QDialog {{
                background-color: {ColorPalette.BG_SECONDARY};
            }}
            QLabel#title {{
                color: {ColorPalette.TEXT_PRIMARY};
                font-size: 20px;
                font-weight: 700;
            }}
            QLabel#subtitle {{
                color: {ColorPalette.TEXT_SECONDARY};
                font-size: 12px;
            }}
            QFrame#header_card, QFrame#details_card {{
                background-color: {ColorPalette.BG_PRIMARY};
                border: 1px solid {ColorPalette.BORDER_LIGHT};
                border-radius: {Spacing.BORDER_RADIUS_MEDIUM}px;
            }}
            QFrame#chip {{
                background-color: {ColorPalette.BG_PRIMARY};
                border: 1px solid {ColorPalette.BORDER_LIGHT};
                border-radius: {Spacing.BORDER_RADIUS_SMALL}px;
            }}
            QFrame#metric_card {{
                background-color: {ColorPalette.BG_PRIMARY};
                border: 1px solid {ColorPalette.BORDER_LIGHT};
                border-radius: {Spacing.BORDER_RADIUS_MEDIUM}px;
            }}
            QLabel#metric_label {{
                color: {ColorPalette.TEXT_SECONDARY};
                font-size: 12px;
                font-weight: 600;
            }}
            QLabel#metric_value {{
                color: {ColorPalette.TEXT_PRIMARY};
                font-size: 22px;
                font-weight: 700;
            }}
            QLabel#tab_summary {{
                color: {ColorPalette.TEXT_SECONDARY};
                font-size: 12px;
                font-weight: 600;
            }}
            QLabel#empty_state {{
                color: {ColorPalette.TEXT_MUTED};
                font-style: italic;
            }}
            QTextEdit {{
                background-color: {ColorPalette.BG_PRIMARY};
                border: 1px solid {ColorPalette.BORDER_LIGHT};
                border-radius: {Spacing.BORDER_RADIUS_SMALL}px;
                padding: 10px;
                font-size: 12px;
                color: {ColorPalette.TEXT_PRIMARY};
            }}
            QTableWidget {{
                background-color: {ColorPalette.BG_PRIMARY};
                border: 1px solid {ColorPalette.BORDER_LIGHT};
                border-radius: {Spacing.BORDER_RADIUS_SMALL}px;
                gridline-color: {ColorPalette.BORDER_LIGHT};
                alternate-background-color: #f9fafb;
            }}
            QHeaderView::section {{
                background-color: {ColorPalette.ACCENT_PRIMARY};
                color: white;
                border: none;
                padding: 8px;
                font-weight: 600;
                font-size: 12px;
            }}
            QTabWidget::pane {{
                border: none;
                margin-top: 6px;
            }}
            QTabBar::tab {{
                background-color: transparent;
                padding: 8px 16px;
                font-weight: 600;
                color: {ColorPalette.TEXT_SECONDARY};
            }}
            QTabBar::tab:selected {{
                color: {ColorPalette.ACCENT_PRIMARY};
                border-bottom: 3px solid {ColorPalette.ACCENT_PRIMARY};
            }}
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(18, 18, 18, 18)
        main_layout.setSpacing(14)

        header_frame = QFrame()
        header_frame.setObjectName("header_card")
        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(18, 18, 18, 18)
        header_layout.setSpacing(14)

        title_row = QHBoxLayout()
        title_row.setSpacing(10)

        title_label = QLabel("Job Card Details")
        title_label.setObjectName("title")

        job_no_label = QLabel(f"#{job_data.get('job_no', 'N/A')}")
        job_no_label.setStyleSheet(
            f"color: {ColorPalette.ACCENT_PRIMARY}; font-weight: 600; "
            f"background-color: rgba(46, 125, 110, 0.12); padding: 6px 12px; "
            f"border-radius: {Spacing.BORDER_RADIUS_SMALL}px;"
        )

        title_row.addWidget(title_label)
        title_row.addWidget(job_no_label)

        start_date = job_data.get('start_date', 'N/A')
        end_date = job_data.get('end_date', 'N/A')
        date_label = QLabel(f"{start_date} → {end_date}")
        date_label.setObjectName("subtitle")
        date_label.setStyleSheet(
            f"background-color: rgba(37, 99, 235, 0.1); border-radius: {Spacing.BORDER_RADIUS_SMALL}px; "
            f"padding: 6px 12px;"
        )
        title_row.addWidget(date_label)
        
        # Status badge with edit button
        status_container = QHBoxLayout()
        status_container.setSpacing(4)
        current_status = job_data.get('status', 'In Progress')
        status_color = '#059669' if current_status == 'Completed' else '#f59e0b'
        status_text_color = 'white' if current_status == 'Completed' else '#78350f'
        self.status_label = QLabel(f"● {current_status.upper()}")
        self.status_label.setStyleSheet(
            f"color: {status_text_color}; font-weight: 700; font-size: 11px; "
            f"background-color: {status_color}; padding: 6px 12px; "
            f"border-radius: {Spacing.BORDER_RADIUS_SMALL}px;"
        )
        status_container.addWidget(self.status_label)
        
        edit_status_btn = QPushButton("✏️")
        edit_status_btn.setFixedSize(28, 28)
        edit_status_btn.setCursor(Qt.PointingHandCursor)
        edit_status_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {ColorPalette.BG_SECONDARY};
                border: 1px solid {ColorPalette.BORDER_LIGHT};
                border-radius: 4px;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {ColorPalette.ACCENT_PRIMARY};
                color: white;
            }}
        """)
        edit_status_btn.clicked.connect(self.edit_status)
        status_container.addWidget(edit_status_btn)
        
        title_row.addLayout(status_container)
        title_row.addStretch()
        header_layout.addLayout(title_row)

        chips_layout = QHBoxLayout()
        chips_layout.setSpacing(8)
        driver_chip_value = job_data.get('driver', '—')
        driver_uid = job_data.get('driver_id') or ''
        if driver_uid:
            base_name = job_data.get('driver') or ''
            driver_chip_value = f"{base_name} ({driver_uid})" if base_name else driver_uid

        chips = [
            ("Driver", driver_chip_value),
            ("Vehicle", job_data.get('vehicle_no', '—')),
            ("Site", job_data.get('site', '—')),
            ("Section", job_data.get('section', '—')),
            ("Hr / Km", job_data.get('hr_km', '—')),
        ]
        for label, value in chips:
            chips_layout.addWidget(self._build_chip(label, value))
        chips_layout.addStretch()
        header_layout.addLayout(chips_layout)

        details_frame = QFrame()
        details_frame.setObjectName("details_card")
        details_layout = QGridLayout(details_frame)
        details_layout.setContentsMargins(16, 12, 16, 12)
        details_layout.setHorizontalSpacing(18)
        details_layout.setVerticalSpacing(10)

        details = [
            ("Company No", job_data.get('company_no', '—')),
            ("Vehicle Make", job_data.get('make', '—')),
            ("Vehicle Model", job_data.get('model', '—')),
            ("Vehicle Type", job_data.get('type', '—')),
            ("Start Date", start_date),
            ("End Date", end_date),
        ]
        for idx, (label, value) in enumerate(details):
            row = idx // 3
            col = idx % 3
            details_layout.addWidget(self._detail_label(label), row, col * 2)
            details_layout.addWidget(self._detail_value(value), row, col * 2 + 1)

        header_layout.addWidget(details_frame)
        main_layout.addWidget(header_frame)

        main_layout.addWidget(self._build_metrics_frame())

        tabs = QTabWidget()
        tabs.addTab(self._build_overview_tab(), "Overview")
        tabs.addTab(self._build_spare_tab(), f"Spare Parts ({len(self.spare_parts)})")
        tabs.addTab(self._build_labour_tab(), f"Labour Works ({len(self.labour_works)})")
        tabs.addTab(self._build_outsource_tab(), f"Outsource ({len(self.outsource_works)})")
        main_layout.addWidget(tabs, 1)

        main_layout.addLayout(self._build_footer())

    def _build_chip(self, label, value):
        frame = QFrame()
        frame.setObjectName("chip")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(2)

        label_widget = QLabel(label.upper())
        label_widget.setStyleSheet(
            f"color: {ColorPalette.TEXT_SECONDARY}; font-size: 11px; font-weight: 600; letter-spacing: 0.5px;"
        )
        value_widget = QLabel(str(value) if value else "—")
        value_widget.setStyleSheet(f"color: {ColorPalette.TEXT_PRIMARY}; font-size: 13px; font-weight: 600;")
        value_widget.setWordWrap(True)

        layout.addWidget(label_widget)
        layout.addWidget(value_widget)
        return frame

    def _detail_label(self, text):
        label = QLabel(text)
        label.setStyleSheet(f"color: {ColorPalette.TEXT_SECONDARY}; font-weight: 600; font-size: 12px;")
        return label

    def _detail_value(self, text):
        label = QLabel(str(text) if text else "—")
        label.setStyleSheet(f"color: {ColorPalette.TEXT_PRIMARY}; font-weight: 600; font-size: 12px;")
        label.setWordWrap(True)
        return label

    def _build_metrics_frame(self):
        frame = QFrame()
        frame.setStyleSheet("QFrame { border: none; }")
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        cards = [
            self._create_metric_card("Spare Parts", self._format_currency(self.spare_total), ColorPalette.ACCENT_PRIMARY),
            self._create_metric_card(
                "Labour Cost",
                self._format_currency(self.labour_total),
                ColorPalette.ACCENT_SECONDARY,
                subtitle=f"Hours: {self.labour_hours:.2f}"
            ),
            self._create_metric_card("Outsource Cost", self._format_currency(self.outsource_total), ColorPalette.ACCENT_BLUE),
            self._create_metric_card("Grand Total", self._format_currency(self.grand_total), ColorPalette.ACCENT_PRIMARY),
        ]
        for card in cards:
            layout.addWidget(card, 1)
        return frame

    def _create_metric_card(self, title, value, accent_color, subtitle=None):
        card = QFrame()
        card.setObjectName("metric_card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(4)

        title_label = QLabel(title)
        title_label.setObjectName("metric_label")
        value_label = QLabel(value)
        value_label.setObjectName("metric_value")
        value_label.setStyleSheet(f"color: {accent_color};")

        layout.addWidget(title_label)
        layout.addWidget(value_label)

        if subtitle:
            subtitle_label = QLabel(subtitle)
            subtitle_label.setStyleSheet(f"color: {ColorPalette.TEXT_SECONDARY}; font-size: 11px;")
            layout.addWidget(subtitle_label)

        return card

    def _build_overview_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        desc_frame = QFrame()
        desc_frame.setObjectName("details_card")
        desc_layout = QVBoxLayout(desc_frame)
        desc_layout.setContentsMargins(16, 16, 16, 16)
        desc_layout.setSpacing(8)

        desc_label = QLabel("Job Description")
        desc_label.setStyleSheet(f"color: {ColorPalette.ACCENT_PRIMARY}; font-weight: 600; font-size: 13px;")
        desc_layout.addWidget(desc_label)

        desc_text = QTextEdit()
        desc_text.setReadOnly(True)
        desc_text.setMinimumHeight(160)
        desc_text.setPlainText(self.job_data.get('description', 'No description provided.'))
        desc_layout.addWidget(desc_text)

        layout.addWidget(desc_frame)

        remarks = self.job_data.get('remarks')
        if remarks:
            remarks_frame = QFrame()
            remarks_frame.setObjectName("details_card")
            remarks_layout = QVBoxLayout(remarks_frame)
            remarks_layout.setContentsMargins(16, 16, 16, 16)
            remarks_layout.setSpacing(8)

            remarks_label = QLabel("Remarks")
            remarks_label.setStyleSheet(f"color: {ColorPalette.ACCENT_PRIMARY}; font-weight: 600; font-size: 13px;")
            remarks_layout.addWidget(remarks_label)

            remarks_text = QTextEdit()
            remarks_text.setReadOnly(True)
            remarks_text.setMinimumHeight(120)
            remarks_text.setPlainText(str(remarks))
            remarks_layout.addWidget(remarks_text)

            layout.addWidget(remarks_frame)

        layout.addStretch()
        return tab

    def _build_spare_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        if not self.spare_parts:
            layout.addWidget(self._build_empty_state("No spare parts recorded."))
            layout.addStretch()
            return tab

        table = QTableWidget(len(self.spare_parts), 9)
        table.setHorizontalHeaderLabels(["#", "ID Code", "Description", "Category", "Quantity", "Unit", "Unit Price", "Total", "Remark"])
        self._configure_table(table)
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(8, QHeaderView.Stretch)

        for row, part in enumerate(self.spare_parts):
            table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
            table.setItem(row, 1, QTableWidgetItem(part.get('id_code', '')))
            table.setItem(row, 2, QTableWidgetItem(part.get('description', '')))
            table.setItem(row, 3, QTableWidgetItem(part.get('category', '')))
            table.setItem(row, 4, QTableWidgetItem(str(part.get('quantity', ''))))
            table.setItem(row, 5, QTableWidgetItem(part.get('unit', '')))
            table.setItem(row, 6, QTableWidgetItem(self._format_currency(part.get('unit_price', 0))))
            table.setItem(row, 7, QTableWidgetItem(self._format_currency(part.get('total', 0))))
            table.setItem(row, 8, QTableWidgetItem(part.get('remark', '')))

        table.resizeRowsToContents()
        layout.addWidget(table)

        summary = QLabel(f"Total: {self._format_currency(self.spare_total)}")
        summary.setObjectName("tab_summary")
        summary.setAlignment(Qt.AlignRight)
        layout.addWidget(summary)
        layout.addStretch()
        return tab

    def _build_labour_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        if not self.labour_works:
            layout.addWidget(self._build_empty_state("No labour works recorded."))
            layout.addStretch()
            return tab

        table = QTableWidget(len(self.labour_works), 6)
        table.setHorizontalHeaderLabels(["#", "Date", "Description", "Hours", "Team", "Cost"])
        self._configure_table(table)
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.Stretch)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)

        for row, work in enumerate(self.labour_works):
            table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
            table.setItem(row, 1, QTableWidgetItem(work.get('work_date', '')))
            table.setItem(row, 2, QTableWidgetItem(work.get('description', '')))
            table.setItem(row, 3, QTableWidgetItem(self._format_hours(work.get('hours'))))
            table.setItem(row, 4, QTableWidgetItem(self._labour_names(work.get('labour_list'))))
            table.setItem(row, 5, QTableWidgetItem(self._format_currency(work.get('work_cost', 0))))

        table.resizeRowsToContents()
        layout.addWidget(table)

        summary_row = QHBoxLayout()
        summary_row.addStretch()
        hours_label = QLabel(f"Total Hours: {self.labour_hours:.2f}")
        hours_label.setObjectName("tab_summary")
        summary_row.addWidget(hours_label)
        cost_label = QLabel(f"Total Cost: {self._format_currency(self.labour_total)}")
        cost_label.setObjectName("tab_summary")
        summary_row.addWidget(cost_label)
        layout.addLayout(summary_row)
        layout.addStretch()
        return tab

    def _build_outsource_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        if not self.outsource_works:
            layout.addWidget(self._build_empty_state("No outsource works recorded."))
            layout.addStretch()
            return tab

        table = QTableWidget(len(self.outsource_works), 6)
        table.setHorizontalHeaderLabels(["#", "Date", "Work Type", "Description", "Cost", "Remarks"])
        self._configure_table(table)
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.Stretch)

        for row, work in enumerate(self.outsource_works):
            table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
            table.setItem(row, 1, QTableWidgetItem(work.get('work_date', '')))
            table.setItem(row, 2, QTableWidgetItem(work.get('work_type', '')))
            table.setItem(row, 3, QTableWidgetItem(work.get('description', '')))
            table.setItem(row, 4, QTableWidgetItem(self._format_currency(work.get('cost', 0))))
            table.setItem(row, 5, QTableWidgetItem(work.get('remark', '')))

        table.resizeRowsToContents()
        layout.addWidget(table)

        summary = QLabel(f"Total: {self._format_currency(self.outsource_total)}")
        summary.setObjectName("tab_summary")
        summary.setAlignment(Qt.AlignRight)
        layout.addWidget(summary)
        layout.addStretch()
        return tab

    def _configure_table(self, table):
        table.verticalHeader().setVisible(False)
        table.setAlternatingRowColors(True)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setSelectionMode(QTableWidget.NoSelection)
        table.setFocusPolicy(Qt.NoFocus)

    def _build_empty_state(self, message):
        label = QLabel(message)
        label.setObjectName("empty_state")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet(
            f"background-color: rgba(17, 24, 39, 0.04); border-radius: {Spacing.BORDER_RADIUS_SMALL}px; padding: 32px 12px;"
        )
        return label

    def _build_footer(self):
        footer = QHBoxLayout()
        footer.setSpacing(10)
        footer.addStretch()

        if HAS_REPORTLAB:
            export_btn = QPushButton("Export PDF")
            export_btn.setCursor(Qt.PointingHandCursor)
            export_btn.setFixedWidth(140)
            export_btn.setStyleSheet(Styles.get_button_secondary())
            export_btn.clicked.connect(self.export_to_pdf)
            footer.addWidget(export_btn)

        close_btn = QPushButton("Close")
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setFixedWidth(120)
        close_btn.setStyleSheet(Styles.get_button_primary())
        close_btn.clicked.connect(self.accept)
        footer.addWidget(close_btn)
        return footer

    @staticmethod
    def _load_items(raw):
        if not raw:
            return []
        if isinstance(raw, list):
            return raw
        try:
            return json.loads(raw)
        except Exception:
            return []

    @staticmethod
    def _sum_numeric(items, key):
        total = 0.0
        for item in items:
            try:
                total += float(item.get(key, 0) or 0)
            except (ValueError, TypeError, AttributeError):
                continue
        return total

    @staticmethod
    def _format_currency(value):
        try:
            return f"Rs. {float(value):,.2f}"
        except (ValueError, TypeError):
            return "Rs. 0.00"

    @staticmethod
    def _format_hours(value):
        try:
            return f"{float(value):.2f} h"
        except (ValueError, TypeError):
            return "0.00 h"

    def _labour_names(self, labour_list):
        if not labour_list:
            return ""
        try:
            items = json.loads(labour_list) if isinstance(labour_list, str) else labour_list
            names = []
            for item in items:
                name = item.get('name', '')
                grade = item.get('grade') or ""
                names.append(f"{name} ({grade})" if grade else name)
            return ", ".join([name for name in names if name])
        except Exception:
            return ""

    def edit_status(self):
        """Edit job card status"""
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QComboBox, QPushButton, QHBoxLayout
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Update Job Status")
        dialog.setMinimumWidth(350)
        dialog.setStyleSheet(f"""
            QDialog {{
                background-color: {ColorPalette.BG_PRIMARY};
            }}
        """)
        
        layout = QVBoxLayout(dialog)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title_label = QLabel("Update Status")
        title_label.setStyleSheet(f"color: {ColorPalette.TEXT_PRIMARY}; font-weight: 700; font-size: 16px;")
        layout.addWidget(title_label)
        
        # Current status info
        current_status = self.job_data.get('status', 'In Progress')
        info_label = QLabel(f"Current Status: {current_status}")
        info_label.setStyleSheet(f"color: {ColorPalette.TEXT_SECONDARY}; font-size: 12px;")
        layout.addWidget(info_label)
        
        # Status dropdown
        label = QLabel("Select new status:")
        label.setStyleSheet(f"color: {ColorPalette.TEXT_PRIMARY}; font-weight: 600; font-size: 13px; margin-top: 8px;")
        layout.addWidget(label)
        
        status_combo = QComboBox()
        status_combo.setEditable(False)
        status_combo.addItems(["In Progress", "Completed"])
        status_combo.setCurrentText(current_status)
        status_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: white;
                border: 2px solid {ColorPalette.BORDER_LIGHT};
                border-radius: 6px;
                padding: 10px;
                padding-right: 35px;
                font-size: 13px;
                min-height: 20px;
            }}
            QComboBox:hover {{
                border: 2px solid {ColorPalette.ACCENT_PRIMARY};
            }}
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 30px;
                border-left: 1px solid {ColorPalette.BORDER_LIGHT};
            }}
            QComboBox::down-arrow {{
                image: none;
                width: 0;
                height: 0;
                border-left: 6px solid transparent;
                border-right: 6px solid transparent;
                border-top: 8px solid {ColorPalette.TEXT_PRIMARY};
            }}
            QComboBox QAbstractItemView {{
                background-color: white;
                border: 1px solid {ColorPalette.BORDER_LIGHT};
                selection-background-color: {ColorPalette.ACCENT_PRIMARY};
                selection-color: white;
                padding: 4px;
            }}
        """)
        layout.addWidget(status_combo)
        
        layout.addSpacing(8)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setMinimumWidth(100)
        cancel_btn.setStyleSheet(Styles.get_button_secondary())
        cancel_btn.clicked.connect(dialog.reject)
        
        save_btn = QPushButton("Update Status")
        save_btn.setMinimumWidth(100)
        save_btn.setStyleSheet(Styles.get_button_primary())
        save_btn.clicked.connect(dialog.accept)
        
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)
        
        if dialog.exec():
            new_status = status_combo.currentText()
            
            # Don't update if status hasn't changed
            if new_status == current_status:
                return
            
            job_id = self.job_data.get('id')
            
            try:
                conn = sqlite3.connect(DB_PATH)
                c = conn.cursor()
                c.execute("UPDATE job_cards SET status = ? WHERE id = ?", (new_status, job_id))
                conn.commit()
                conn.close()
                
                # Update UI
                self.job_data['status'] = new_status
                status_color = '#059669' if new_status == 'Completed' else '#f59e0b'
                status_text_color = 'white' if new_status == 'Completed' else '#78350f'
                self.status_label.setText(f"● {new_status.upper()}")
                self.status_label.setStyleSheet(
                    f"color: {status_text_color}; font-weight: 700; font-size: 11px; "
                    f"background-color: {status_color}; padding: 6px 12px; "
                    f"border-radius: {Spacing.BORDER_RADIUS_SMALL}px;"
                )
                
                QMessageBox.information(self, "Success", f"Status updated to '{new_status}'")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to update status: {str(e)}")

    def export_to_pdf(self):
        """Export job card details to PDF."""
        if not HAS_REPORTLAB:
            QMessageBox.warning(self, "Not Available", "PDF export requires reportlab library.")
            return

        # Use the status from job data
        status_display = self.job_data.get('status', 'In Progress')

        job_data = self.job_data
        spare_total = self.spare_total
        labour_total = self.labour_total
        outsource_total = self.outsource_total
        grand_total = self.grand_total

        timestamp = datetime.datetime.now()
        timestamp_str = timestamp.strftime('%d %b %Y %H:%M')

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Job Card as PDF",
            f"JobCard_{job_data.get('job_no', 'unknown')}.pdf",
            "PDF Files (*.pdf)"
        )

        if not file_path:
            return

        try:
            accent_primary = colors.HexColor('#2d7a5f')
            neutral_bg = colors.HexColor('#f8fafc')
            neutral_border = colors.HexColor('#d4dce9')
            slate = colors.HexColor('#475569')
            muted = colors.HexColor('#94a3b8')

            doc = SimpleDocTemplate(
                file_path,
                pagesize=A4,
                topMargin=0.9 * inch,
                bottomMargin=0.6 * inch,
                leftMargin=0.6 * inch,
                rightMargin=0.6 * inch,
            )

            story = []
            styles = getSampleStyleSheet()

            chip_style = ParagraphStyle(
                'ChipStyle',
                parent=styles['BodyText'],
                fontSize=9,
                leading=13,
                textColor=colors.HexColor('#0f172a'),
                spaceBefore=0,
                spaceAfter=0,
            )
            info_label_style = ParagraphStyle(
                'InfoLabel',
                parent=styles['Normal'],
                fontSize=8,
                textColor=colors.HexColor('#64748b'),
                leading=10,
                spaceBefore=0,
                spaceAfter=2,
            )
            info_value_style = ParagraphStyle(
                'InfoValue',
                parent=styles['Heading4'],
                fontSize=10,
                textColor=colors.HexColor('#111827'),
                leading=12,
                spaceBefore=0,
                spaceAfter=0,
            )
            section_heading = ParagraphStyle(
                'SectionHeading',
                parent=styles['Heading2'],
                fontSize=10,
                textColor=colors.HexColor('#1f2937'),
                spaceBefore=0,
                spaceAfter=6,
            )
            body_style = ParagraphStyle(
                'BodyStyle',
                parent=styles['Normal'],
                fontSize=9,
                textColor=colors.HexColor('#1f2937'),
                leading=13,
                spaceBefore=0,
                spaceAfter=0,
            )
            note_style = ParagraphStyle(
                'NoteStyle',
                parent=styles['Normal'],
                fontSize=8.5,
                textColor=muted,
                leading=12,
                spaceBefore=4,
                spaceAfter=6,
            )
            table_body_style = ParagraphStyle(
                'TableBody',
                parent=styles['Normal'],
                fontSize=8.5,
                leading=11,
                textColor=colors.HexColor('#1f2937'),
                spaceBefore=0,
                spaceAfter=0,
            )
            summary_detail_style = ParagraphStyle(
                'SummaryDetail',
                parent=styles['Normal'],
                fontSize=9,
                textColor=slate,
                leading=12,
                alignment=TA_RIGHT,
                spaceBefore=6,
                spaceAfter=0,
            )
            summary_total_style = ParagraphStyle(
                'SummaryTotal',
                parent=info_value_style,
                textColor=colors.white,
            )

            logo_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                'assets',
                'logo.png'
            )

            def _draw_header_footer(canvas_obj, doc_obj):
                canvas_obj.saveState()
                page_width, page_height = doc_obj.pagesize
                header_height = 0.85 * inch

                canvas_obj.setFillColor(colors.white)
                canvas_obj.rect(0, page_height - header_height, page_width, header_height, fill=1, stroke=0)
                canvas_obj.setFillColor(accent_primary)
                canvas_obj.rect(0, page_height - header_height, page_width, 10, fill=1, stroke=0)

                if os.path.exists(logo_path):
                    try:
                        canvas_obj.drawImage(
                            logo_path,
                            doc_obj.leftMargin,
                            page_height - header_height + 18,
                            width=100,
                            height=34,
                            preserveAspectRatio=True,
                            mask='auto'
                        )
                    except Exception:
                        pass

                title_x = doc_obj.leftMargin + 120
                canvas_obj.setFont('Helvetica-Bold', 15)
                canvas_obj.setFillColor(accent_primary)
                canvas_obj.drawString(title_x, page_height - 0.38 * inch, 'Job Card')
                canvas_obj.setFont('Helvetica', 9)
                canvas_obj.setFillColor(colors.HexColor('#1f2937'))
                canvas_obj.drawString(
                    title_x,
                    page_height - 0.56 * inch,
                    f"Job No: {job_data.get('job_no', 'N/A')}"
                )
                status_label = f"STATUS · {status_display.upper()}"
                canvas_obj.setFont('Helvetica-Bold', 9)
                label_width = canvas_obj.stringWidth(status_label, 'Helvetica-Bold', 9)
                pad_x = 6
                pad_y = 3
                box_width = label_width + (pad_x * 2)
                box_height = 14 + pad_y
                box_x = page_width - doc_obj.rightMargin - box_width
                box_y = page_height - 0.48 * inch
                status_clean = status_display.strip().lower()
                if status_clean == 'completed':
                    status_bg = colors.HexColor('#059669')
                    status_text = colors.white
                else:
                    status_bg = colors.HexColor('#f59e0b')
                    status_text = colors.HexColor('#78350f')
                canvas_obj.setFillColor(status_bg)
                canvas_obj.roundRect(box_x, box_y, box_width, box_height, 4, fill=1, stroke=0)
                canvas_obj.setFillColor(status_text)
                canvas_obj.drawString(box_x + pad_x, box_y + pad_y + 2, status_label)

                footer_y = doc_obj.bottomMargin * 0.55
                canvas_obj.setStrokeColor(colors.HexColor('#d9e3f5'))
                canvas_obj.setLineWidth(0.5)
                canvas_obj.line(doc_obj.leftMargin, footer_y + 12, page_width - doc_obj.rightMargin, footer_y + 12)
                canvas_obj.setFillColor(muted)
                canvas_obj.setFont('Helvetica', 8)
                canvas_obj.drawString(
                    doc_obj.leftMargin,
                    footer_y,
                    'Senarath Workshop Management Suite — System developed by DrkCyph7'
                )
                canvas_obj.drawString(
                    doc_obj.leftMargin,
                    footer_y - 10,
                    f"Computer generated job card on {timestamp_str}."
                )
                canvas_obj.drawRightString(
                    page_width - doc_obj.rightMargin,
                    footer_y,
                    f"Page {canvas_obj.getPageNumber()}"
                )
                canvas_obj.restoreState()

            def clean_paragraph_text(value, placeholder='—'):
                if value is None:
                    value = ''
                text = str(value).strip()
                if not text:
                    return placeholder
                return "<br/>".join(escape(text).splitlines())

            driver_name = job_data.get('driver', '—') or '—'
            driver_id = job_data.get('driver_id') or ''
            driver_display = driver_name if driver_name != '—' else '—'
            if driver_id:
                driver_display = f"{driver_display} ({driver_id})"

            chips = [
                ('Driver', driver_display),
                ('Vehicle', job_data.get('vehicle_no', '—')),
                ('Site', job_data.get('site', '—')),
                ('Section', job_data.get('section', '—')),
                ('Hr / Km', job_data.get('hr_km', '—')),
            ]
            chip_cells = []
            for label, value in chips:
                chip_cells.append(Paragraph(
                    f"<font color='#6b7280' size=7>{escape(str(label).upper())}</font><br/><font color='#0f172a' size=10><b>{clean_paragraph_text(value)}</b></font>",
                    chip_style
                ))
            chips_table = Table([chip_cells], colWidths=[doc.width / len(chip_cells)] * len(chip_cells))
            chips_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), neutral_bg),
                ('BOX', (0, 0), (-1, -1), 0.6, neutral_border),
                ('INNERGRID', (0, 0), (-1, -1), 0.6, neutral_border),
                ('LEFTPADDING', (0, 0), (-1, -1), 10),
                ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            story.append(chips_table)
            story.append(Spacer(1, 0.12 * inch))

            info_pairs = [
                ('Company No', job_data.get('company_no', '—'), 'Vehicle Make', job_data.get('make', '—')),
                ('Start Date', job_data.get('start_date', '—'), 'Vehicle Model', job_data.get('model', '—')),
                ('End Date', job_data.get('end_date', '—'), 'Vehicle Type', job_data.get('type', '—')),
            ]
            info_rows = []
            for left_label, left_value, right_label, right_value in info_pairs:
                info_rows.append([
                    Paragraph(escape(str(left_label)), info_label_style),
                    Paragraph(clean_paragraph_text(left_value), info_value_style),
                    Paragraph(escape(str(right_label)), info_label_style),
                    Paragraph(clean_paragraph_text(right_value), info_value_style),
                ])
            info_col_units = [1.25, 2.2, 1.25, 2.2]
            col_sum = sum(info_col_units)
            info_col_widths = [doc.width * (u / col_sum) for u in info_col_units]
            info_table = Table(info_rows, colWidths=info_col_widths)
            info_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.white),
                ('BOX', (0, 0), (-1, -1), 0.6, neutral_border),
                ('INNERGRID', (0, 0), (-1, -1), 0.6, neutral_border),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            story.append(info_table)
            story.append(Spacer(1, 0.12 * inch))

            story.append(Paragraph('Job Description', section_heading))
            description_text = clean_paragraph_text(job_data.get('description'), 'No description provided.')
            story.append(Paragraph(description_text, body_style))
            story.append(Spacer(1, 0.08 * inch))

            remarks_text = job_data.get('remarks')
            if remarks_text:
                story.append(Paragraph('Remarks', section_heading))
                remarks_box = Table([[Paragraph(clean_paragraph_text(remarks_text), body_style)]], colWidths=[doc.width])
                remarks_box.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, -1), colors.white),
                    ('BOX', (0, 0), (-1, -1), 0.6, neutral_border),
                    ('LEFTPADDING', (0, 0), (-1, -1), 10),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                    ('TOPPADDING', (0, 0), (-1, -1), 8),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ]))
                story.append(remarks_box)

            def build_dataset_section(title, headers, rows, column_units, summary_line, style_extras=None):
                flow = [Paragraph(title, section_heading)]
                if not rows:
                    flow.append(Paragraph('No records available for this section.', note_style))
                    story.append(KeepTogether(flow))
                    story.append(Spacer(1, 0.12 * inch))
                    return

                col_sum_units = sum(column_units)
                col_widths = [doc.width * (u / col_sum_units) for u in column_units]
                table = Table([headers] + rows, colWidths=col_widths, repeatRows=1)
                table_style = [
                    ('BACKGROUND', (0, 0), (-1, 0), accent_primary),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 9),
                    ('FONTSIZE', (0, 1), (-1, -1), 8.5),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
                    ('GRID', (0, 0), (-1, -1), 0.45, neutral_border),
                    ('LEFTPADDING', (0, 0), (-1, -1), 6),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                    ('TOPPADDING', (0, 0), (-1, -1), 4),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                    ('ALIGN', (0, 1), (0, -1), 'CENTER'),
                ]
                if style_extras:
                    table_style.extend(style_extras)
                table.setStyle(TableStyle(table_style))
                flow.append(table)
                flow.append(Paragraph(summary_line, summary_detail_style))
                story.append(KeepTogether(flow))
                story.append(Spacer(1, 0.12 * inch))

            spare_rows = []
            for idx, part in enumerate(self.spare_parts, 1):
                spare_rows.append([
                    str(idx),
                    Paragraph(clean_paragraph_text(part.get('id_code', '—')), table_body_style),
                    Paragraph(clean_paragraph_text(part.get('description', '—')), table_body_style),
                    Paragraph(clean_paragraph_text(part.get('category', '—')), table_body_style),
                    str(part.get('quantity', '') or '—'),
                    Paragraph(clean_paragraph_text(part.get('unit', '—')), table_body_style),
                    self._format_currency(part.get('unit_price', 0)),
                    self._format_currency(part.get('total', 0)),
                    Paragraph(clean_paragraph_text(part.get('remark', '')), table_body_style),
                ])
            spare_summary = (
                f"<b>{len(self.spare_parts)}</b> items captured &bull; Total spend {escape(self._format_currency(spare_total))}"
            )
            build_dataset_section(
                'Spare Parts & Materials',
                ['#', 'ID Code', 'Description', 'Category', 'Qty', 'Unit', 'Unit Price', 'Total', 'Remark'],
                spare_rows,
                [0.4, 0.9, 2.0, 1.1, 0.6, 0.7, 0.9, 0.9, 1.2],
                spare_summary,
                style_extras=[
                    ('ALIGN', (4, 1), (4, -1), 'CENTER'),
                    ('ALIGN', (5, 1), (5, -1), 'CENTER'),
                    ('ALIGN', (6, 1), (7, -1), 'RIGHT'),
                ],
            )

            labour_rows = []
            for idx, work in enumerate(self.labour_works, 1):
                labour_names = []
                try:
                    labour_entries = work.get('labour_list', [])
                    if isinstance(labour_entries, str):
                        labour_entries = json.loads(labour_entries)
                    for item in labour_entries:
                        name = item.get('name', '')
                        grade = item.get('grade') or ''
                        labour_names.append(f"{name} ({grade})" if grade else name)
                except Exception:
                    pass
                labour_rows.append([
                    str(idx),
                    Paragraph(clean_paragraph_text(work.get('work_date', '—')), table_body_style),
                    Paragraph(clean_paragraph_text(work.get('description', '—')), table_body_style),
                    f"{float(work.get('hours', 0) or 0):.2f}",
                    Paragraph(clean_paragraph_text(', '.join(labour_names) or '—'), table_body_style),
                    self._format_currency(work.get('work_cost', 0)),
                ])
            labour_summary = (
                f"<b>{len(self.labour_works)}</b> entries logged &bull; Hours {self.labour_hours:.2f} &bull; Cost {escape(self._format_currency(labour_total))}"
            )
            build_dataset_section(
                'Labour Works',
                ['#', 'Date', 'Description', 'Hours', 'Labour Team', 'Cost'],
                labour_rows,
                [0.4, 0.8, 2.1, 0.7, 1.6, 0.9],
                labour_summary,
                style_extras=[
                    ('ALIGN', (1, 1), (1, -1), 'CENTER'),
                    ('ALIGN', (3, 1), (3, -1), 'CENTER'),
                    ('ALIGN', (5, 1), (5, -1), 'RIGHT'),
                ],
            )

            outsource_rows = []
            for idx, work in enumerate(self.outsource_works, 1):
                outsource_rows.append([
                    str(idx),
                    Paragraph(clean_paragraph_text(work.get('work_date', '—')), table_body_style),
                    Paragraph(clean_paragraph_text(work.get('work_type', '—')), table_body_style),
                    Paragraph(clean_paragraph_text(work.get('description', '—')), table_body_style),
                    self._format_currency(work.get('cost', 0)),
                    Paragraph(clean_paragraph_text(work.get('remark', '')), table_body_style),
                ])
            outsource_summary = (
                f"<b>{len(self.outsource_works)}</b> outsource tasks &bull; Total {escape(self._format_currency(outsource_total))}"
            )
            build_dataset_section(
                'Outsource Works',
                ['#', 'Date', 'Work Type', 'Description', 'Cost', 'Remarks'],
                outsource_rows,
                [0.4, 0.8, 1.1, 2.2, 0.9, 1.3],
                outsource_summary,
                style_extras=[
                    ('ALIGN', (1, 1), (1, -1), 'CENTER'),
                    ('ALIGN', (4, 1), (4, -1), 'RIGHT'),
                ],
            )

            story.append(Paragraph('Financial Summary', section_heading))
            summary_table = Table([
                [
                    Paragraph('<b>Spare Parts Total</b>', info_value_style),
                    Paragraph(self._format_currency(spare_total), info_value_style),
                ],
                [
                    Paragraph('<b>Labour Cost Total</b>', info_value_style),
                    Paragraph(self._format_currency(labour_total), info_value_style),
                ],
                [
                    Paragraph('<b>Outsource Total</b>', info_value_style),
                    Paragraph(self._format_currency(outsource_total), info_value_style),
                ],
                [
                    Paragraph('<b>Grand Total</b>', summary_total_style),
                    Paragraph(self._format_currency(grand_total), summary_total_style),
                ],
            ], colWidths=[doc.width * 0.55, doc.width * 0.45])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -2), colors.white),
                ('BACKGROUND', (0, -1), (-1, -1), accent_primary),
                ('TEXTCOLOR', (0, -1), (-1, -1), colors.white),
                ('TEXTCOLOR', (0, 0), (-1, -2), slate),
                ('BOX', (0, 0), (-1, -1), 0.6, neutral_border),
                ('LEFTPADDING', (0, 0), (-1, -1), 12),
                ('RIGHTPADDING', (0, 0), (-1, -1), 12),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('ALIGN', (-1, 0), (-1, -1), 'RIGHT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LINEABOVE', (0, -1), (-1, -1), 1.0, colors.HexColor('#a7d7c8')),
            ]))
            story.append(summary_table)

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
        self.status_filter.addItems(["All Status", "In Progress", "Completed"])
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

        # Row 3: Driver + Vehicle No + Spare Part + Labour
        filter_row3 = QHBoxLayout()
        filter_row3.setSpacing(5)

        self.driver_filter = QComboBox()
        self.driver_filter.addItem("All Drivers")
        self.driver_filter.setMaximumHeight(28)
        self.driver_filter.setMaximumWidth(220)
        self.driver_filter.setMinimumWidth(140)
        self.driver_filter.setStyleSheet(dropdown_style)
        try:
            self.driver_filter.view().setMinimumWidth(300)
        except Exception:
            pass
        filter_row3.addWidget(self.driver_filter)

        self.vehicle_no_filter = QComboBox()
        self.vehicle_no_filter.addItem("All Vehicles")
        self.vehicle_no_filter.setMaximumHeight(28)
        self.vehicle_no_filter.setMaximumWidth(220)
        self.vehicle_no_filter.setMinimumWidth(140)
        self.vehicle_no_filter.setStyleSheet(dropdown_style)
        try:
            self.vehicle_no_filter.view().setMinimumWidth(300)
        except Exception:
            pass
        filter_row3.addWidget(self.vehicle_no_filter)

        self.spare_part_filter = QLineEdit()
        self.spare_part_filter.setPlaceholderText("Filter by Spare Part (name or ID code)")
        self.spare_part_filter.setMaximumHeight(28)
        self.spare_part_filter.setStyleSheet(dropdown_style)
        filter_row3.addWidget(self.spare_part_filter, 1)

        self.labour_name_filter = QLineEdit()
        self.labour_name_filter.setPlaceholderText("Filter by Labour (name/team)")
        self.labour_name_filter.setMaximumHeight(28)
        self.labour_name_filter.setStyleSheet(dropdown_style)
        filter_row3.addWidget(self.labour_name_filter, 1)

        filter_layout.addLayout(filter_row3)
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
        self.table.setColumnCount(12)
        self.table.setHorizontalHeaderLabels([
            "ID", "Job No", "Company No", "Vehicle No", "Driver",
            "Make", "Model", "Type", "Site", "Section", "Start Date", "Status"
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
        # Initialize type-ahead suggestions after loading data
        try:
            self._setup_completers()
        except Exception:
            pass

    def _configure_combobox_completion(self, combo: QComboBox):
        try:
            combo.setEditable(True)
            combo.setInsertPolicy(QComboBox.NoInsert)
            comp = QCompleter(combo.model(), self)
            comp.setCaseSensitivity(Qt.CaseInsensitive)
            comp.setFilterMode(Qt.MatchContains)
            comp.setCompletionMode(QCompleter.PopupCompletion)
            combo.setCompleter(comp)
        except Exception:
            pass

    def _setup_completers(self):
        """Attach QCompleter to search fields and editable combos."""
        # 1) Global search suggestions from job_cards key fields
        suggestions = set()
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("SELECT job_no, company_no, vehicle_no, driver, site, section, make, model, type FROM job_cards")
            for row in c.fetchall():
                for val in row:
                    if val and isinstance(val, str):
                        v = val.strip()
                        if v:
                            suggestions.add(v)
            conn.close()
        except Exception:
            pass
        try:
            comp_all = QCompleter(sorted(suggestions), self)
            comp_all.setCaseSensitivity(Qt.CaseInsensitive)
            comp_all.setFilterMode(Qt.MatchContains)
            comp_all.setCompletionMode(QCompleter.PopupCompletion)
            self.search_input.setCompleter(comp_all)
        except Exception:
            pass

        # 2) Spare parts suggestions from spare_parts table
        spare_suggestions = []
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("SELECT id_code, item_description FROM spare_parts")
            for idc, desc in c.fetchall():
                idc = (idc or '').strip()
                desc = (desc or '').strip()
                if idc and desc:
                    spare_suggestions.append(f"{idc} — {desc}")
                elif idc:
                    spare_suggestions.append(idc)
                elif desc:
                    spare_suggestions.append(desc)
            conn.close()
        except Exception:
            pass
        try:
            comp_sp = QCompleter(sorted(set(spare_suggestions)), self)
            comp_sp.setCaseSensitivity(Qt.CaseInsensitive)
            comp_sp.setFilterMode(Qt.MatchContains)
            comp_sp.setCompletionMode(QCompleter.PopupCompletion)
            self.spare_part_filter.setCompleter(comp_sp)
        except Exception:
            pass

        # 3) Labour suggestions from labour table
        labour_suggestions = []
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("SELECT DISTINCT name FROM labour WHERE name IS NOT NULL AND name != ''")
            labour_suggestions = [r[0] for r in c.fetchall() if r and r[0]]
            conn.close()
        except Exception:
            pass
        try:
            comp_lb = QCompleter(sorted(set(labour_suggestions)), self)
            comp_lb.setCaseSensitivity(Qt.CaseInsensitive)
            comp_lb.setFilterMode(Qt.MatchContains)
            comp_lb.setCompletionMode(QCompleter.PopupCompletion)
            self.labour_name_filter.setCompleter(comp_lb)
        except Exception:
            pass

        # 4) Enable type-ahead on combo filters
        for combo in [
            self.site_filter,
            self.section_filter,
            self.type_filter,
            self.driver_filter,
            self.vehicle_no_filter,
        ]:
            self._configure_combobox_completion(combo)

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

        # Load drivers
        c.execute("SELECT DISTINCT name FROM drivers WHERE name IS NOT NULL AND name != '' ORDER BY name")
        for row in c.fetchall():
            self.driver_filter.addItem(row[0])

        # Load vehicle numbers
        c.execute("SELECT DISTINCT number FROM vehicles WHERE number IS NOT NULL AND number != '' AND number != '-' ORDER BY number")
        for row in c.fetchall():
            self.vehicle_no_filter.addItem(row[0])
        
        conn.close()
        # Refresh completers when filters are loaded
        try:
            self._setup_completers()
        except Exception:
            pass

    def load_records(self):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("""SELECT id, job_no, company_no, vehicle_no, driver, make, model, type, site, section, start_date,
                     COALESCE(status, 'In Progress'),
                     spare_parts, labour_works
                     FROM job_cards ORDER BY id DESC""")
        rows = c.fetchall()
        conn.close()
        
        # Extract table data (first 12 columns including status)
        table_rows = [row[:12] for row in rows]
        self.populate_table(table_rows)

    def apply_filters(self):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        query = """SELECT id, job_no, company_no, vehicle_no, driver, make, model, type, site, section, start_date,
                   COALESCE(status, 'In Progress'),
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

        # Driver filter
        driver_val = self.driver_filter.currentText()
        if driver_val != "All Drivers":
            query += " AND driver = ?"
            params.append(driver_val)

        # Vehicle number filter
        vehicle_no_val = self.vehicle_no_filter.currentText()
        if vehicle_no_val != "All Vehicles":
            query += " AND vehicle_no = ?"
            params.append(vehicle_no_val)
        
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

        # Text filters for JSON contents
        spare_text = self.spare_part_filter.text().strip().lower()
        labour_text = self.labour_name_filter.text().strip().lower()
        for row in all_rows:
            total_cost = 0.0
            
            # Calculate total from spare parts
            spare_parts = []
            try:
                spare_parts = json.loads(row[11]) if row[11] else []
                for part in spare_parts:
                    total_cost += float(part.get('total', 0))
            except Exception:
                pass
            
            # Calculate total from labour works
            labour_works = []
            try:
                labour_works = json.loads(row[12]) if row[12] else []
                for work in labour_works:
                    total_cost += float(work.get('work_cost', 0))
            except Exception:
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
            
            # Check status filter using actual DB status column (row[11])
            if status_filter != "All Status":
                actual_status = row[11] if len(row) > 11 else 'In Progress'
                if status_filter != actual_status:
                    continue
            
            # Spare part content filter (matches id_code, description, category, unit)
            if spare_text:
                found = False
                for p in spare_parts:
                    try:
                        hay = " ".join([
                            str(p.get('id_code', '')),
                            str(p.get('description', '')),
                            str(p.get('category', '')),
                            str(p.get('unit', '')),
                        ]).lower()
                        if spare_text in hay:
                            found = True
                            break
                    except Exception:
                        continue
                if not found:
                    continue

            # Labour content filter (matches labour names/grades and description)
            if labour_text:
                found_labour = False
                for w in labour_works:
                    try:
                        desc = str(w.get('description', '')).lower()
                        if labour_text and labour_text in desc:
                            found_labour = True
                            break
                        labour_list = w.get('labour_list', [])
                        if isinstance(labour_list, str):
                            labour_list = json.loads(labour_list)
                        for item in labour_list:
                            nm = str(item.get('name', '')).lower()
                            gr = str(item.get('grade', '')).lower()
                            if labour_text in nm or (gr and labour_text in gr):
                                found_labour = True
                                break
                        if found_labour:
                            break
                    except Exception:
                        continue
                if not found_labour:
                    continue

            filtered_rows.append(row[:12])
        
        self.populate_table(filtered_rows)

    def clear_filters(self):
        self.search_input.clear()
        self.site_filter.setCurrentIndex(0)
        self.section_filter.setCurrentIndex(0)
        self.type_filter.setCurrentIndex(0)
        self.driver_filter.setCurrentIndex(0)
        self.vehicle_no_filter.setCurrentIndex(0)
        self.spare_part_filter.clear()
        self.labour_name_filter.clear()
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
                     site, section, hr_km, start_date, end_date, description, spare_parts, labour_works, outsource_works,
                     COALESCE(status, 'In Progress')
                     FROM job_cards WHERE id=?""", (record_id,))
        row = c.fetchone()
        conn.close()
        
        if row:
            job_data = {
                'job_no': row[0],
                'company_no': row[1],
                'vehicle_no': row[2],
                'driver': row[3],
                'driver_id': '',  # No driver_uid column in database
                'make': row[4],
                'model': row[5],
                'type': row[6],
                'site': row[7],
                'section': row[8],
                'hr_km': row[9],
                'start_date': row[10],
                'end_date': row[11],
                'description': row[12],
                'spare_parts': row[13],
                'labour_works': row[14],
                'outsource_works': row[15],
                'status': row[16],
                'id': record_id  # Pass ID for status updates
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
                     site, section, hr_km, start_date, end_date, description, spare_parts, labour_works, outsource_works,
                     COALESCE(status, 'In Progress')
                     FROM job_cards WHERE id=?""", (record_id,))
        row = c.fetchone()
        conn.close()
        
        if row:
            job_data = {
                'id': row[0], 'job_no': row[1], 'company_no': row[2], 'vehicle_no': row[3],
                'driver': row[4], 'make': row[5], 'model': row[6], 'type': row[7],
                'site': row[8], 'section': row[9], 'hr_km': row[10],
                'start_date': row[11], 'end_date': row[12], 'description': row[13],
                'spare_parts': row[14], 'labour_works': row[15], 'outsource_works': row[16],
                'status': row[17]
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