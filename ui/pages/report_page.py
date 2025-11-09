import sqlite3
import csv
import json
from datetime import datetime, timedelta
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QCheckBox,
    QTableWidget, QTableWidgetItem, QMessageBox, QComboBox, QDateEdit,
    QFrame, QFileDialog, QSpinBox, QGridLayout, QTextEdit,
    QDialog, QListWidget, QListWidgetItem, QScrollArea
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont, QTransform
from ui.theme import ColorPalette, Typography, Spacing, Styles, create_page_header

DB_PATH = "ui/db/senarath.db"


class ReportPage(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.current_table = "job_cards"
        self.visible_columns = None
        self.zoom_level = 100  # Default zoom level
        
        # === UI Colors ===
        bg_color = "#f5f5f5"
        card_color = "#ffffff"
        accent_color = "#2d7a5f"
        text_color = "#2c2c2c"
        border_color = "#e0e0e0"
        
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {bg_color};
                color: {text_color};
                font-family: 'Segoe UI', Arial;
                font-size: 12px;
            }}
            QLabel {{
                background-color: transparent;
            }}
            QLabel#title {{
                font-size: 26px;
                font-weight: 700;
                color: #1a1a1a;
            }}
            QFrame#card {{
                background-color: {card_color};
                border-radius: 6px;
                border: none;
            }}
            QPushButton {{
                background-color: {accent_color};
                border-radius: 5px;
                padding: 6px 14px;
                color: white;
                font-weight: 600;
                border: none;
                font-size: 11px;
                text-transform: uppercase;
                letter-spacing: 0.2px;
            }}
            QPushButton:hover {{
                background-color: #246651;
            }}
            QPushButton:pressed {{
                background-color: #1f5443;
            }}
            QPushButton#secondary {{
                background-color: #8b6f47;
            }}
            QPushButton#secondary:hover {{
                background-color: #735a38;
            }}
            QPushButton#ghost {{
                background-color: transparent;
                color: #555;
                border: 1px solid #ccc;
                text-transform: none;
                letter-spacing: 0px;
                font-weight: 500;
            }}
            QPushButton#ghost:hover {{
                background-color: #f5f5f5;
                border-color: #999;
            }}
            QComboBox, QDateEdit, QSpinBox {{
                background-color: #fafafa;
                border: 1px solid {border_color};
                border-radius: 4px;
                padding: 6px 8px;
                font-size: 11px;
            }}
            QComboBox:focus, QDateEdit:focus, QSpinBox:focus {{
                border: 2px solid {accent_color};
                background-color: #ffffff;
            }}
            QTableWidget {{
                background-color: {card_color};
                border: 1px solid {border_color};
                color: {text_color};
                gridline-color: #f0f0f0;
                border-radius: 4px;
                font-size: 10px;
                alternate-background-color: #fafafa;
            }}
            QTableWidget::item {{
                padding: 4px;
                border: none;
            }}
            QTableWidget::item:selected {{
                background-color: #d4f1eb;
            }}
            QHeaderView::section {{
                background-color: {accent_color};
                color: white;
                padding: 6px 4px;
                border: none;
                font-weight: 700;
                font-size: 9px;
                text-transform: uppercase;
            }}
        """)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(18, 14, 18, 14)
        main_layout.setSpacing(10)
        
        # === Header ===
        header_layout, title_label, back_btn = create_page_header("📊 Job Cards Report")
        back_btn.clicked.connect(self.go_back)
        main_layout.addLayout(header_layout)
        
        # === Quick Actions & Shortcuts ===
        action_bar = QFrame()
        action_bar.setObjectName("card")
        action_layout = QHBoxLayout(action_bar)
        action_layout.setContentsMargins(10, 8, 10, 8)
        action_layout.setSpacing(7)
        
        # Shortcuts
        this_week_btn = QPushButton("This Week")
        this_week_btn.setMaximumWidth(100)
        this_week_btn.setFixedHeight(28)
        this_week_btn.setObjectName("ghost")
        this_week_btn.clicked.connect(self.filter_this_week)
        
        this_month_btn = QPushButton("This Month")
        this_month_btn.setMaximumWidth(110)
        this_month_btn.setFixedHeight(28)
        this_month_btn.setObjectName("ghost")
        this_month_btn.clicked.connect(self.filter_this_month)
        
        action_layout.addWidget(this_week_btn)
        action_layout.addWidget(this_month_btn)
        
        action_layout.addSpacing(12)
        
        # Quick Actions
        self.columns_btn = QPushButton("Columns")
        self.columns_btn.setMaximumWidth(85)
        self.columns_btn.setFixedHeight(28)
        self.columns_btn.setObjectName("ghost")
        self.columns_btn.clicked.connect(self.show_column_selector)
        
        self.preview_btn = QPushButton("Preview")
        self.preview_btn.setMaximumWidth(90)
        self.preview_btn.setFixedHeight(28)
        self.preview_btn.clicked.connect(self.preview_data)
        
        self.export_csv_btn = QPushButton("Export")
        self.export_csv_btn.setMaximumWidth(85)
        self.export_csv_btn.setFixedHeight(28)
        self.export_csv_btn.setObjectName("secondary")
        self.export_csv_btn.clicked.connect(self.export_to_csv)
        
        action_layout.addStretch()
        
        # Zoom controls
        zoom_out_btn = QPushButton("🔍−")
        zoom_out_btn.setMaximumWidth(50)
        zoom_out_btn.setFixedHeight(28)
        zoom_out_btn.setObjectName("ghost")
        zoom_out_btn.setToolTip("Zoom Out")
        zoom_out_btn.clicked.connect(self.zoom_out_table)
        
        self.zoom_label = QLabel("100%")
        self.zoom_label.setAlignment(Qt.AlignCenter)
        self.zoom_label.setMaximumWidth(45)
        self.zoom_label.setStyleSheet("font-weight: 600; font-size: 10px;")
        
        zoom_in_btn = QPushButton("🔍+")
        zoom_in_btn.setMaximumWidth(50)
        zoom_in_btn.setFixedHeight(28)
        zoom_in_btn.setObjectName("ghost")
        zoom_in_btn.setToolTip("Zoom In")
        zoom_in_btn.clicked.connect(self.zoom_in_table)
        
        action_layout.addWidget(zoom_out_btn)
        action_layout.addWidget(self.zoom_label)
        action_layout.addWidget(zoom_in_btn)
        
        action_layout.addWidget(self.columns_btn)
        action_layout.addWidget(self.preview_btn)
        action_layout.addWidget(self.export_csv_btn)
        
        main_layout.addWidget(action_bar)
        
        # === Advanced Filters Panel ===
        filter_card = QFrame()
        filter_card.setObjectName("card")
        filter_layout = QVBoxLayout(filter_card)
        filter_layout.setContentsMargins(10, 10, 10, 10)
        filter_layout.setSpacing(8)
        
        # Row 1: Date Range & Driver
        row1_layout = QHBoxLayout()
        row1_layout.setSpacing(8)
        
        date_label = QLabel("Date:")
        date_label.setStyleSheet("font-weight: 600; color: #555; font-size: 10px;")
        date_label.setMaximumWidth(30)
        row1_layout.addWidget(date_label)
        
        self.from_date = QDateEdit()
        self.from_date.setCalendarPopup(True)
        self.from_date.setDisplayFormat("yyyy-MM-dd")
        self.from_date.setDate(QDate.currentDate().addDays(-30))
        self.from_date.setMaximumWidth(110)
        self.from_date.setFixedHeight(26)
        row1_layout.addWidget(self.from_date)
        
        to_label = QLabel("to")
        to_label.setStyleSheet("font-weight: 500; color: #999; font-size: 9px;")
        to_label.setMaximumWidth(20)
        row1_layout.addWidget(to_label)
        
        self.to_date = QDateEdit()
        self.to_date.setCalendarPopup(True)
        self.to_date.setDisplayFormat("yyyy-MM-dd")
        self.to_date.setDate(QDate.currentDate())
        self.to_date.setMaximumWidth(110)
        self.to_date.setFixedHeight(26)
        row1_layout.addWidget(self.to_date)
        
        driver_label = QLabel("Driver:")
        driver_label.setStyleSheet("font-weight: 600; color: #555; font-size: 10px;")
        driver_label.setMaximumWidth(40)
        row1_layout.addWidget(driver_label)
        
        self.driver_filter = QComboBox()
        self.driver_filter.addItem("All")
        self.load_drivers()
        self.driver_filter.setMaximumWidth(110)
        self.driver_filter.setFixedHeight(26)
        row1_layout.addWidget(self.driver_filter)
        
        row1_layout.addStretch()
        filter_layout.addLayout(row1_layout)
        
        # Row 2: Site, Vehicle, Status, Rows, Reset
        row2_layout = QHBoxLayout()
        row2_layout.setSpacing(8)
        
        site_label = QLabel("Site:")
        site_label.setStyleSheet("font-weight: 600; color: #555; font-size: 10px;")
        site_label.setMaximumWidth(30)
        row2_layout.addWidget(site_label)
        
        self.site_filter = QComboBox()
        self.site_filter.addItem("All")
        self.load_sites()
        self.site_filter.setMaximumWidth(110)
        self.site_filter.setFixedHeight(26)
        row2_layout.addWidget(self.site_filter)
        
        vehicle_label = QLabel("Vehicle:")
        vehicle_label.setStyleSheet("font-weight: 600; color: #555; font-size: 10px;")
        vehicle_label.setMaximumWidth(50)
        row2_layout.addWidget(vehicle_label)
        
        self.vehicle_filter = QComboBox()
        self.vehicle_filter.addItem("All")
        self.load_vehicles()
        self.vehicle_filter.setMaximumWidth(110)
        self.vehicle_filter.setFixedHeight(26)
        row2_layout.addWidget(self.vehicle_filter)
        
        # Advanced: Job Status Filter
        status_label = QLabel("Status:")
        status_label.setStyleSheet("font-weight: 600; color: #555; font-size: 10px;")
        status_label.setMaximumWidth(40)
        row2_layout.addWidget(status_label)
        
        self.status_filter = QComboBox()
        self.status_filter.addItems(["All", "Completed", "In Progress", "Pending"])
        self.status_filter.setMaximumWidth(100)
        self.status_filter.setFixedHeight(26)
        row2_layout.addWidget(self.status_filter)
        
        # Sort: Job Card Number
        sort_label = QLabel("Sort:")
        sort_label.setStyleSheet("font-weight: 600; color: #555; font-size: 10px;")
        sort_label.setMaximumWidth(35)
        row2_layout.addWidget(sort_label)
        
        self.sort_filter = QComboBox()
        self.sort_filter.addItems(["Smallest to Highest", "Highest to Smallest"])
        self.sort_filter.setMaximumWidth(140)
        self.sort_filter.setFixedHeight(26)
        row2_layout.addWidget(self.sort_filter)
        
        rows_label = QLabel("Max Rows:")
        rows_label.setStyleSheet("font-weight: 600; color: #555; font-size: 10px;")
        rows_label.setMaximumWidth(60)
        row2_layout.addWidget(rows_label)
        
        self.row_limit = QSpinBox()
        self.row_limit.setMinimum(10)
        self.row_limit.setMaximum(10000)
        self.row_limit.setValue(500)
        self.row_limit.setSingleStep(100)
        self.row_limit.setMaximumWidth(75)
        self.row_limit.setFixedHeight(26)
        row2_layout.addWidget(self.row_limit)
        
        row2_layout.addStretch()
        
        reset_btn = QPushButton("Reset")
        reset_btn.setObjectName("ghost")
        reset_btn.setMaximumWidth(75)
        reset_btn.setFixedHeight(26)
        reset_btn.clicked.connect(self.reset_filters)
        row2_layout.addWidget(reset_btn)
        
        filter_layout.addLayout(row2_layout)
        
        main_layout.addWidget(filter_card)
        
        # === Data Table (Main Preview) ===
        data_card = QFrame()
        data_card.setObjectName("card")
        data_layout = QVBoxLayout(data_card)
        data_layout.setContentsMargins(0, 0, 0, 0)
        data_layout.setSpacing(0)
        
        self.table = QTableWidget()
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setAlternatingRowColors(True)
        data_layout.addWidget(self.table)
        
        main_layout.addWidget(data_card, 1)
        
        self.setLayout(main_layout)
        
        # Initial setup
        self.select_report_type("job_cards")
    
    def go_back(self):
        """Navigate back to home page"""
        if self.parent:
            self.parent.go_to_home()
    
    def load_drivers(self):
        """Load drivers from database"""
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("SELECT DISTINCT name FROM drivers ORDER BY name")
            drivers = c.fetchall()
            conn.close()
            
            for driver in drivers:
                self.driver_filter.addItem(driver[0])
        except Exception as e:
            print(f"Error loading drivers: {e}")
    
    def load_sites(self):
        """Load sites from database"""
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("SELECT DISTINCT name FROM sites ORDER BY name")
            sites = c.fetchall()
            conn.close()
            
            for site in sites:
                self.site_filter.addItem(site[0])
        except Exception as e:
            print(f"Error loading sites: {e}")
    
    def load_vehicles(self):
        """Load vehicles from database"""
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("SELECT DISTINCT number FROM vehicles ORDER BY number")
            vehicles = c.fetchall()
            conn.close()
            
            for vehicle in vehicles:
                if vehicle[0] and vehicle[0] != "-":
                    self.vehicle_filter.addItem(vehicle[0])
        except Exception as e:
            print(f"Error loading vehicles: {e}")
    
    def reset_filters(self):
        """Reset all filters to default values"""
        self.from_date.setDate(QDate.currentDate().addDays(-30))
        self.to_date.setDate(QDate.currentDate())
        self.driver_filter.setCurrentIndex(0)
        self.site_filter.setCurrentIndex(0)
        self.vehicle_filter.setCurrentIndex(0)
        self.status_filter.setCurrentIndex(0)
        self.sort_filter.setCurrentIndex(0)  # Reset to "Smallest to Highest"
        self.row_limit.setValue(500)
    
    def filter_this_week(self):
        """Filter to show this week's records"""
        today = QDate.currentDate()
        start = today.addDays(-today.dayOfWeek() + 1)
        self.from_date.setDate(start)
        self.to_date.setDate(today)
    
    def filter_this_month(self):
        """Filter to show this month's records"""
        today = QDate.currentDate()
        start = QDate(today.year(), today.month(), 1)
        self.from_date.setDate(start)
        self.to_date.setDate(today)
    
    def select_report_type(self, report_type):
        """Select report type"""
        self.current_table = report_type
        
        if report_type == "job_cards":
            self.visible_columns = [
                "Start Date", "Job No", "Job description", "Driver", "Company No",
                "Vehicle No", "Make", "Model", "Type", "Site", "Section", "End Date"
            ]
        else:
            self.visible_columns = ["Company No", "Vehicle No", "Make", "Model", "Type"]
    
    def show_column_selector(self):
        """Show column selection dialog"""
        if self.current_table == "job_cards":
            categories = {
                "Basic Info": ["Start Date", "Job No", "Job description", "Driver"],
                "Company & Vehicle": ["Company No", "Vehicle No", "Make", "Model", "Type"],
                "Location": ["Site", "Section"],
                "Dates": ["End Date"],
                "Spare Parts": ["description", "ref no", "Qty", "Unit", "unit price", "total"]
            }
        else:
            categories = {
                "Basic Info": ["Company No", "Vehicle No"],
                "Details": ["Make", "Model", "Type"]
            }
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Select Columns to Display & Export")
        dialog.setFixedSize(400, 500)
        dialog.setStyleSheet(self.styleSheet())
        
        layout = QVBoxLayout(dialog)
        layout.setSpacing(10)
        layout.setContentsMargins(12, 12, 12, 12)
        
        # Header
        title = QLabel("📊 Customize Report Columns")
        title.setStyleSheet("font-weight: 700; font-size: 13px; margin-bottom: 5px;")
        layout.addWidget(title)
        
        info_label = QLabel("Select which columns to show in preview and export")
        info_label.setStyleSheet("font-size: 10px; color: #777;")
        layout.addWidget(info_label)
        
        # Scrollable list
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(8)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        
        self.column_checkboxes = {}
        
        for category, columns in categories.items():
            cat_label = QLabel(f"▼ {category}")
            cat_label.setStyleSheet("font-weight: 700; color: #2d7a5f; font-size: 11px; margin-top: 8px;")
            scroll_layout.addWidget(cat_label)
            
            for col in columns:
                checkbox = QCheckBox(col)
                checkbox.setCheckState(Qt.Checked if col in self.visible_columns else Qt.Unchecked)
                checkbox.setStyleSheet("padding: 5px 0px; font-size: 11px;")
                self.column_checkboxes[col] = checkbox
                scroll_layout.addWidget(checkbox)
        
        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        select_all_btn = QPushButton("Select All")
        select_all_btn.setFixedHeight(28)
        select_all_btn.setObjectName("ghost")
        select_all_btn.clicked.connect(lambda: self.toggle_all_columns(True))
        
        deselect_all_btn = QPushButton("Deselect All")
        deselect_all_btn.setFixedHeight(28)
        deselect_all_btn.setObjectName("ghost")
        deselect_all_btn.clicked.connect(lambda: self.toggle_all_columns(False))
        
        btn_layout.addWidget(select_all_btn)
        btn_layout.addWidget(deselect_all_btn)
        btn_layout.addStretch()
        
        ok_btn = QPushButton("Apply")
        ok_btn.setFixedHeight(28)
        ok_btn.setMinimumWidth(80)
        ok_btn.clicked.connect(lambda: self.apply_columns(dialog))
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFixedHeight(28)
        cancel_btn.setMinimumWidth(80)
        cancel_btn.setObjectName("ghost")
        cancel_btn.clicked.connect(dialog.reject)
        
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        
        dialog.exec()
    
    def toggle_all_columns(self, state):
        """Toggle all columns on/off"""
        for checkbox in self.column_checkboxes.values():
            checkbox.setCheckState(Qt.Checked if state else Qt.Unchecked)
    
    def apply_columns(self, dialog):
        """Apply selected columns"""
        self.visible_columns = []
        for col, checkbox in self.column_checkboxes.items():
            if checkbox.checkState() == Qt.Checked:
                self.visible_columns.append(col)
        
        if not self.visible_columns:
            QMessageBox.warning(self, "No Columns", "Please select at least one column!")
            return
        
        dialog.accept()
        self.preview_data()
    
    def get_filtered_data(self):
        """Get filtered data from database with spare parts expanded"""
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            
            query = """SELECT id, job_no, company_no, vehicle_no, driver, site, section, 
                              start_date, end_date, make, model, type, hr_km, description, spare_parts
                       FROM job_cards WHERE 1=1"""
            params = []
            
            # Date filter
            from_date = self.from_date.date().toString("yyyy-MM-dd")
            to_date = self.to_date.date().toString("yyyy-MM-dd")
            query += " AND start_date >= ? AND start_date <= ?"
            params.extend([from_date, to_date])
            
            # Driver filter
            if self.driver_filter.currentText() != "All":
                query += " AND driver = ?"
                params.append(self.driver_filter.currentText())
            
            # Site filter
            if self.site_filter.currentText() != "All":
                query += " AND site = ?"
                params.append(self.site_filter.currentText())
            
            # Vehicle filter
            if self.vehicle_filter.currentText() != "All":
                query += " AND vehicle_no = ?"
                params.append(self.vehicle_filter.currentText())
            
            # Sort by job number
            sort_option = self.sort_filter.currentText()
            if sort_option == "Smallest to Highest":
                query += " ORDER BY job_no ASC LIMIT ?"
            else:  # Highest to Smallest
                query += " ORDER BY job_no DESC LIMIT ?"
            
            params.append(self.row_limit.value())
            
            c.execute(query, params)
            data = c.fetchall()
            conn.close()
            
            # Expand spare parts data - Reorder to match CSV format
            # CSV order: Start Date, Job No, Job description, Driver, Company No, Vehicle No, Make, Model, Type, Site, Section, End Date, description, ref no, Qty, Unit, unit price, total
            expanded_data = []
            for row in data:
                # row indices: 0=id, 1=job_no, 2=company_no, 3=vehicle_no, 4=driver, 5=site, 6=section, 7=start_date, 8=end_date, 9=make, 10=model, 11=type, 12=hr_km, 13=description, 14=spare_parts
                spare_parts_json = row[14] if len(row) > 14 else ""
                
                try:
                    if spare_parts_json:
                        spare_parts = json.loads(spare_parts_json)
                        if isinstance(spare_parts, list) and len(spare_parts) > 0:
                            # Create a row for each spare part - Reordered to CSV format
                            for idx, part in enumerate(spare_parts):
                                new_row = [
                                    row[7],   # Start Date
                                    row[1],   # Job No
                                    row[13],  # Job description
                                    row[4],   # Driver
                                    row[2],   # Company No
                                    row[3],   # Vehicle No
                                    row[9],   # Make
                                    row[10],  # Model
                                    row[11],  # Type
                                    row[5],   # Site
                                    row[6],   # Section
                                    row[8],   # End Date
                                    part.get('description', ''),  # spare part description
                                    part.get('ref_no', ''),        # ref no
                                    part.get('quantity', ''),      # Qty
                                    part.get('unit', ''),          # Unit
                                    part.get('unit_price', ''),    # unit price
                                    part.get('total', '')          # total
                                ]
                                expanded_data.append(new_row)
                        else:
                            new_row = [row[7], row[1], row[13], row[4], row[2], row[3], row[9], row[10], row[11], row[5], row[6], row[8], '', '', '', '', '', '']
                            expanded_data.append(new_row)
                    else:
                        new_row = [row[7], row[1], row[13], row[4], row[2], row[3], row[9], row[10], row[11], row[5], row[6], row[8], '', '', '', '', '', '']
                        expanded_data.append(new_row)
                except:
                    new_row = [row[7], row[1], row[13], row[4], row[2], row[3], row[9], row[10], row[11], row[5], row[6], row[8], '', '', '', '', '', '']
                    expanded_data.append(new_row)
            
            return expanded_data
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to retrieve data:\n{str(e)}")
            return []
    
    def preview_data(self):
        """Preview filtered data in table"""
        data = self.get_filtered_data()
        
        if not data:
            QMessageBox.warning(self, "No Data", "No records found. Please adjust your filters.")
            return
        
        # All headers in CSV order
        all_headers = [
            "Start Date", "Job No", "Job description", "Driver", "Company No", "Vehicle No",
            "Make", "Model", "Type", "Site", "Section", "End Date",
            "description", "ref no", "Qty", "Unit", "unit price", "total"
        ]
        
        visible_indices = []
        for col in self.visible_columns:
            if col in all_headers:
                visible_indices.append(all_headers.index(col))
        
        filtered_headers = [all_headers[i] for i in visible_indices]
        
        self.table.clear()
        self.table.setColumnCount(len(filtered_headers))
        self.table.setHorizontalHeaderLabels(filtered_headers)
        
        # Add 1 extra row for grand total
        self.table.setRowCount(len(data) + 1)
        
        # Add data rows
        for row_idx, row_data in enumerate(data):
            for col_idx, header_idx in enumerate(visible_indices):
                if header_idx < len(row_data):
                    value = row_data[header_idx]
                    item = QTableWidgetItem(str(value) if value else "")
                    self.table.setItem(row_idx, col_idx, item)
        
        # Add grand total row
        total_index = all_headers.index("total") if "total" in all_headers else -1
        if total_index in visible_indices:
            total_col_idx = visible_indices.index(total_index)
            grand_total = 0
            
            # Calculate grand total
            for row_data in data:
                try:
                    total_val = float(row_data[total_index]) if row_data[total_index] else 0
                    grand_total += total_val
                except (ValueError, TypeError):
                    pass
            
            # Add grand total label
            label_item = QTableWidgetItem("GRAND TOTAL:")
            label_item.setFont(QFont("Arial", 11, QFont.Bold))
            self.table.setItem(len(data), 0, label_item)
            
            # Add grand total value in the total column
            total_item = QTableWidgetItem(f"{grand_total:.2f}")
            total_item.setFont(QFont("Arial", 11, QFont.Bold))
            self.table.setItem(len(data), total_col_idx, total_item)
        
        self.table.resizeColumnsToContents()
        
        # Apply current zoom level
        self.apply_zoom()
        
        QMessageBox.information(self, "Preview Loaded", f"✅ Loaded {len(data)} records\n\nAll details and spare parts included in preview!")
    
    def export_to_csv(self):
        """Export filtered data to CSV"""
        data = self.get_filtered_data()
        
        if not data:
            QMessageBox.warning(self, "No Data", "No records to export. Please check your filters.")
            return
        
        try:
            # All headers in CSV order
            all_headers = [
                "Start Date", "Job No", "Job description", "Driver", "Company No", "Vehicle No",
                "Make", "Model", "Type", "Site", "Section", "End Date",
                "description", "ref no", "Qty", "Unit", "unit price", "total"
            ]
            
            visible_indices = []
            for col in self.visible_columns:
                if col in all_headers:
                    visible_indices.append(all_headers.index(col))
            
            filtered_headers = [all_headers[i] for i in visible_indices]
            
            # File dialog
            home_dir = str(Path.home())
            filename, _ = QFileDialog.getSaveFileName(
                self,
                "Export Report as CSV",
                f"{home_dir}/JobCards_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                "CSV Files (*.csv);;All Files (*)"
            )
            
            if not filename:
                return
            
            # Write CSV
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write headers
                writer.writerow(filtered_headers)
                
                # Write data rows with only visible columns
                for row_data in data:
                    filtered_row = [row_data[i] if i < len(row_data) else "" for i in visible_indices]
                    writer.writerow(filtered_row)
                
                # Add grand total row
                total_index = all_headers.index("total") if "total" in all_headers else -1
                if total_index in visible_indices:
                    grand_total = 0
                    
                    # Calculate grand total
                    for row_data in data:
                        try:
                            total_val = float(row_data[total_index]) if row_data[total_index] else 0
                            grand_total += total_val
                        except (ValueError, TypeError):
                            pass
                    
                    # Create grand total row
                    grand_total_row = [""] * len(visible_indices)
                    grand_total_row[0] = "GRAND TOTAL:"
                    total_col_idx = visible_indices.index(total_index)
                    grand_total_row[total_col_idx] = f"{grand_total:.2f}"
                    writer.writerow(grand_total_row)
            
            record_count = len(data)
            QMessageBox.information(
                self,
                "Export Successful ✅",
                f"Report exported successfully!\n\n"
                f"📁 File: {filename}\n"
                f"📊 Records: {record_count}\n"
                f"📋 Columns: {len(filtered_headers)}\n\n"
                f"✨ All details included!"
            )
        
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export:\n{str(e)}")
    
    def zoom_in_table(self):
        """Increase table zoom level"""
        self.zoom_level = min(250, self.zoom_level + 25)
        self.apply_zoom()
    
    def zoom_out_table(self):
        """Decrease table zoom level"""
        self.zoom_level = max(50, self.zoom_level - 25)
        self.apply_zoom()
    
    def apply_zoom(self):
        """Apply zoom level to table by scaling rows and columns"""
        zoom_factor = self.zoom_level / 100.0
        
        # Create font at the zoomed size
        cell_font = QFont("Arial", int(10 * zoom_factor))
        header_font = QFont("Arial", int(11 * zoom_factor), QFont.Bold)
        
        # Apply font to all cells
        for row in range(self.table.rowCount()):
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if item:
                    item.setFont(cell_font)
        
        # Apply font to headers
        self.table.horizontalHeader().setFont(header_font)
        self.table.verticalHeader().setFont(header_font)
        
        # Scale row heights
        row_height = int(24 * zoom_factor)
        for row in range(self.table.rowCount()):
            self.table.setRowHeight(row, row_height)
        
        # Scale header height
        header_height = int(24 * zoom_factor)
        self.table.horizontalHeader().setFixedHeight(header_height)
        
        # Scale column widths - get all column widths and scale them
        for col in range(self.table.columnCount()):
            # Start with a base width and scale it
            base_width = 80
            new_width = int(base_width * zoom_factor)
            self.table.setColumnWidth(col, new_width)
        
        # Update zoom label
        self.zoom_label.setText(f"{self.zoom_level}%")
