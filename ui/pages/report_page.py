"""
Advanced Analytics & Reporting Module
Professional analytics with powerful filters and intelligent insights
"""
import sqlite3
import csv
import json
import datetime
import os
from collections import defaultdict
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox, QComboBox, QDateEdit,
    QFrame, QFileDialog, QHeaderView, QGridLayout, QLineEdit, QTabWidget,
    QDialog, QCheckBox, QDialogButtonBox
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont
from ui.theme import ColorPalette, Typography, Spacing, Styles, create_page_header

DB_PATH = "ui/db/senarath.db"

# Optional export libraries
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    from reportlab.pdfgen import canvas
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False

try:
    import openpyxl
    from openpyxl.styles import Font as XLFont, Alignment, PatternFill, Border, Side
    HAS_OPENPYXL = True
except ImportError:
    HAS_OPENPYXL = False


class ReportPage(QWidget):
    """Advanced analytics with professional filters and insights"""
    
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.all_records = []
        self.filtered_records = []
        self._setup_ui()
        self.load_initial_data()
    
    def _setup_ui(self):
        """Setup clean, professional UI"""
        self.setStyleSheet(f"""
            QWidget {{
                background-color: #f5f5f0;
                font-family: 'Segoe UI', Arial;
                color: #2c2c2c;
            }}
            QLabel {{
                background-color: transparent;
                color: #2c2c2c;
            }}
            QLabel#page_title {{
                font-size: 26px;
                font-weight: 700;
                color: #1a1a1a;
            }}
            QFrame#card {{
                background-color: white;
                border: 1px solid #d4d4d4;
                border-radius: 8px;
            }}
            QLabel#stat_value {{
                color: {ColorPalette.ACCENT_PRIMARY};
                font-size: 24px;
                font-weight: 700;
                background-color: transparent;
            }}
            QLabel#stat_label {{
                color: #6b7280;
                font-size: 11px;
                font-weight: 600;
                text-transform: uppercase;
                background-color: transparent;
            }}
            QComboBox, QDateEdit, QLineEdit {{
                background-color: white;
                border: 1px solid #d4d4d4;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 12px;
                min-height: 24px;
            }}
            QComboBox:focus, QDateEdit:focus, QLineEdit:focus {{
                border: 2px solid {ColorPalette.ACCENT_PRIMARY};
            }}
            QTableWidget {{
                background-color: white;
                border: 1px solid #d4d4d4;
                border-radius: 6px;
                gridline-color: #e5e7eb;
                alternate-background-color: #f9fafb;
            }}
            QHeaderView::section {{
                background-color: {ColorPalette.ACCENT_PRIMARY};
                color: white;
                padding: 8px;
                border: none;
                font-weight: 600;
                font-size: 11px;
            }}
            QTableWidget::item {{
                padding: 6px;
            }}
            QTableWidget::item:selected {{
                background-color: rgba(46, 125, 110, 0.15);
            }}
            QTabWidget::pane {{
                border: 1px solid #d4d4d4;
                border-radius: 6px;
                background-color: white;
            }}
            QTabBar::tab {{
                background-color: transparent;
                padding: 8px 16px;
                font-weight: 600;
                color: #6b7280;
                border: none;
            }}
            QTabBar::tab:selected {{
                color: {ColorPalette.ACCENT_PRIMARY};
                border-bottom: 3px solid {ColorPalette.ACCENT_PRIMARY};
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
                background-color: #2d7a5f;
                color: white;
                padding: 11px 22px;
            }}
            QPushButton#primary:hover {{
                background-color: #246651;
            }}
            QPushButton#secondary {{
                background-color: #8b6f47;
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
        """)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(16)
        
        # Header
        header_layout, title_label, back_btn = create_page_header("📊 Analytics & Reports")
        back_btn.clicked.connect(self.go_back)
        main_layout.addLayout(header_layout)
        
        # Filters Card
        filter_card = QFrame()
        filter_card.setObjectName("card")
        filter_layout = QVBoxLayout(filter_card)
        filter_layout.setContentsMargins(10, 8, 10, 8)
        filter_layout.setSpacing(6)
        
        filter_title = QLabel("Filters")
        filter_title.setStyleSheet("font-size: 13px; font-weight: 600; color: #374151; background-color: transparent;")
        filter_layout.addWidget(filter_title)
        
        # Filter controls in grid
        controls_grid = QGridLayout()
        controls_grid.setHorizontalSpacing(6)
        controls_grid.setVerticalSpacing(3)
        controls_grid.setContentsMargins(0, 0, 0, 0)
        
        # Period selector
        lbl = QLabel("Period:")
        lbl.setStyleSheet("background-color: transparent; font-size: 11px;")
        lbl.setFixedWidth(50)
        controls_grid.addWidget(lbl, 0, 0, Qt.AlignRight)
        self.period_combo = QComboBox()
        self.period_combo.addItems(["Last 7 Days", "Last 30 Days", "Last 3 Months", 
                                    "Last 6 Months", "This Year", "All Time", "Custom Range"])
        self.period_combo.setCurrentText("Last 30 Days")
        self.period_combo.currentTextChanged.connect(self.on_period_changed)
        controls_grid.addWidget(self.period_combo, 0, 1)
        
        # Date range
        lbl = QLabel("From:")
        lbl.setStyleSheet("background-color: transparent; font-size: 11px;")
        lbl.setFixedWidth(40)
        controls_grid.addWidget(lbl, 0, 2, Qt.AlignRight)
        self.from_date = QDateEdit()
        self.from_date.setCalendarPopup(True)
        self.from_date.setDisplayFormat("yyyy-MM-dd")
        self.from_date.setDate(QDate.currentDate().addDays(-30))
        self.from_date.setEnabled(False)
        controls_grid.addWidget(self.from_date, 0, 3)
        
        lbl = QLabel("To:")
        lbl.setStyleSheet("background-color: transparent; font-size: 11px;")
        lbl.setFixedWidth(30)
        controls_grid.addWidget(lbl, 0, 4, Qt.AlignRight)
        self.to_date = QDateEdit()
        self.to_date.setCalendarPopup(True)
        self.to_date.setDisplayFormat("yyyy-MM-dd")
        self.to_date.setDate(QDate.currentDate())
        self.to_date.setEnabled(False)
        controls_grid.addWidget(self.to_date, 0, 5)
        
        # Site, Status, Vehicle filters
        lbl = QLabel("Site:")
        lbl.setStyleSheet("background-color: transparent; font-size: 11px;")
        lbl.setFixedWidth(50)
        controls_grid.addWidget(lbl, 1, 0, Qt.AlignRight)
        self.site_filter = QComboBox()
        self.site_filter.addItem("All Sites")
        controls_grid.addWidget(self.site_filter, 1, 1)
        
        lbl = QLabel("Status:")
        lbl.setStyleSheet("background-color: transparent; font-size: 11px;")
        lbl.setFixedWidth(40)
        controls_grid.addWidget(lbl, 1, 2, Qt.AlignRight)
        self.status_filter = QComboBox()
        self.status_filter.addItems(["All Status", "Completed", "In Progress"])
        controls_grid.addWidget(self.status_filter, 1, 3)
        
        lbl = QLabel("Vehicle:")
        lbl.setStyleSheet("background-color: transparent; font-size: 11px;")
        lbl.setFixedWidth(50)
        controls_grid.addWidget(lbl, 1, 4, Qt.AlignRight)
        self.vehicle_filter = QComboBox()
        self.vehicle_filter.setEditable(True)
        self.vehicle_filter.addItem("All Vehicles")
        controls_grid.addWidget(self.vehicle_filter, 1, 5)
        
        # Search and Sort
        lbl = QLabel("Search:")
        lbl.setStyleSheet("background-color: transparent; font-size: 11px;")
        lbl.setFixedWidth(50)
        controls_grid.addWidget(lbl, 2, 0, Qt.AlignRight)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Job no, driver, spare part name/ID, section, site...")
        self.search_input.textChanged.connect(self.apply_filters)
        controls_grid.addWidget(self.search_input, 2, 1, 1, 3)
        
        lbl = QLabel("Sort:")
        lbl.setStyleSheet("background-color: transparent; font-size: 11px;")
        lbl.setFixedWidth(40)
        controls_grid.addWidget(lbl, 2, 4, Qt.AlignRight)
        self.sort_combo = QComboBox()
        self.sort_combo.addItems([
            "Latest First",
            "Oldest First", 
            "Highest Cost",
            "Lowest Cost",
            "Vehicle (A-Z)",
            "Site (A-Z)"
        ])
        self.sort_combo.currentTextChanged.connect(self.apply_filters)
        controls_grid.addWidget(self.sort_combo, 2, 5)
        
        # Action buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)
        
        generate_btn = QPushButton("Generate Report")
        generate_btn.setObjectName("secondary")
        generate_btn.setFixedHeight(32)
        generate_btn.setMinimumWidth(140)
        generate_btn.setCursor(Qt.PointingHandCursor)
        generate_btn.clicked.connect(self.apply_filters)
        btn_row.addWidget(generate_btn)
        
        clear_btn = QPushButton("Clear Filters")
        clear_btn.setObjectName("muted")
        clear_btn.setFixedHeight(32)
        clear_btn.setMinimumWidth(110)
        clear_btn.setCursor(Qt.PointingHandCursor)
        clear_btn.clicked.connect(self.clear_filters)
        btn_row.addWidget(clear_btn)
        
        btn_row.addStretch()
        controls_grid.addLayout(btn_row, 3, 0, 1, 6)
        
        filter_layout.addLayout(controls_grid)
        main_layout.addWidget(filter_card)
        
        # Stats Cards
        self.stats_container = QHBoxLayout()
        self.stats_container.setSpacing(10)
        main_layout.addLayout(self.stats_container)
        
        # Tabs for different analytics views
        self.tabs = QTabWidget()
        self.tabs.currentChanged.connect(self.on_tab_changed)
        
        # Overview Tab
        self.overview_table = self._create_table()
        self.tabs.addTab(self.overview_table, "Overview")
        
        # Spare Parts Analysis
        self.parts_table = self._create_table()
        self.tabs.addTab(self.parts_table, "Spare Parts")
        
        # Vehicle Analysis
        self.vehicle_table = self._create_table()
        self.tabs.addTab(self.vehicle_table, "Vehicles")
        
        # Cost Analysis
        self.cost_table = self._create_table()
        self.tabs.addTab(self.cost_table, "Cost Breakdown")
        
        main_layout.addWidget(self.tabs, 1)
        
        # Export buttons
        export_layout = QHBoxLayout()
        export_layout.addStretch()
        
        csv_btn = QPushButton("Export CSV")
        csv_btn.setObjectName("muted")
        csv_btn.setFixedHeight(32)
        csv_btn.setMinimumWidth(110)
        csv_btn.setCursor(Qt.PointingHandCursor)
        csv_btn.clicked.connect(self.export_csv)
        export_layout.addWidget(csv_btn)
        
        if HAS_OPENPYXL:
            xlsx_btn = QPushButton("Export Excel")
            xlsx_btn.setObjectName("muted")
            xlsx_btn.setFixedHeight(32)
            xlsx_btn.setMinimumWidth(115)
            xlsx_btn.setCursor(Qt.PointingHandCursor)
            xlsx_btn.clicked.connect(self.export_xlsx)
            export_layout.addWidget(xlsx_btn)
        
        if HAS_REPORTLAB:
            pdf_btn = QPushButton("Export PDF")
            pdf_btn.setObjectName("muted")
            pdf_btn.setFixedHeight(32)
            pdf_btn.setMinimumWidth(110)
            pdf_btn.setCursor(Qt.PointingHandCursor)
            pdf_btn.clicked.connect(self.export_pdf)
            export_layout.addWidget(pdf_btn)
        
        main_layout.addLayout(export_layout)
    
    def _create_table(self):
        """Create standardized table widget"""
        table = QTableWidget()
        table.setAlternatingRowColors(True)
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        return table
    
    def load_initial_data(self):
        """Load filter options and initial data"""
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            
            # Load sites
            c.execute("SELECT DISTINCT name FROM sites ORDER BY name")
            for row in c.fetchall():
                self.site_filter.addItem(row[0])
            
            # Load vehicles
            c.execute("SELECT DISTINCT number FROM vehicles WHERE number != '-' ORDER BY number")
            for row in c.fetchall():
                if row[0]:
                    self.vehicle_filter.addItem(row[0])
            
            conn.close()
            
            # Initial report generation
            self.apply_filters()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load data:\n{str(e)}")
    
    def on_period_changed(self, period):
        """Handle period selection"""
        is_custom = period == "Custom Range"
        self.from_date.setEnabled(is_custom)
        self.to_date.setEnabled(is_custom)
        
        if not is_custom:
            today = QDate.currentDate()
            if period == "Last 7 Days":
                self.from_date.setDate(today.addDays(-7))
            elif period == "Last 30 Days":
                self.from_date.setDate(today.addDays(-30))
            elif period == "Last 3 Months":
                self.from_date.setDate(today.addMonths(-3))
            elif period == "Last 6 Months":
                self.from_date.setDate(today.addMonths(-6))
            elif period == "This Year":
                self.from_date.setDate(QDate(today.year(), 1, 1))
            elif period == "All Time":
                self.from_date.setDate(QDate(2020, 1, 1))
            self.to_date.setDate(today)
    
    def clear_filters(self):
        """Reset all filters"""
        self.period_combo.setCurrentText("Last 30 Days")
        self.site_filter.setCurrentText("All Sites")
        self.status_filter.setCurrentText("All Status")
        self.vehicle_filter.setCurrentText("All Vehicles")
        self.search_input.clear()
        self.sort_combo.setCurrentText("Latest First")
        self.apply_filters()
    
    def apply_filters(self):
        """Apply all filters and regenerate report"""
        try:
            # Build SQL query
            from_str = self.from_date.date().toString("yyyy-MM-dd")
            to_str = self.to_date.date().toString("yyyy-MM-dd")
            
            conditions = ["start_date >= ?", "start_date <= ?"]
            params = [from_str, to_str]
            
            if self.site_filter.currentText() != "All Sites":
                conditions.append("site = ?")
                params.append(self.site_filter.currentText())
            
            if self.status_filter.currentText() != "All Status":
                conditions.append("status = ?")
                params.append(self.status_filter.currentText())
            
            if self.vehicle_filter.currentText() != "All Vehicles":
                conditions.append("vehicle_no = ?")
                params.append(self.vehicle_filter.currentText())
            
            where_clause = "WHERE " + " AND ".join(conditions)
            
            # Fetch filtered records
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            
            query = f"""
                SELECT id, job_no, company_no, vehicle_no, driver, make, model, type,
                       site, section, start_date, end_date, status,
                       spare_parts, labour_works, outsource_works, description
                FROM job_cards
                {where_clause}
                ORDER BY start_date DESC, id DESC
            """
            
            c.execute(query, params)
            rows = c.fetchall()
            conn.close()
            
            # Process records
            self.all_records = []
            for row in rows:
                spare_parts = self._safe_json_loads(row['spare_parts'])
                labour_works = self._safe_json_loads(row['labour_works'])
                outsource_works = self._safe_json_loads(row['outsource_works'])
                
                spare_cost = sum(self._to_float(p.get('total', 0)) for p in spare_parts)
                labour_cost = sum(self._to_float(w.get('work_cost', 0)) for w in labour_works)
                outsource_cost = sum(self._to_float(w.get('cost', 0)) for w in outsource_works)
                
                record = {
                    'id': row['id'],
                    'job_no': row['job_no'] or '',
                    'company_no': row['company_no'] or '',
                    'vehicle_no': row['vehicle_no'] or '',
                    'driver': row['driver'] or '',
                    'make': row['make'] or '',
                    'model': row['model'] or '',
                    'type': row['type'] or '',
                    'site': row['site'] or '',
                    'section': row['section'] or '',
                    'start_date': row['start_date'] or '',
                    'end_date': row['end_date'] or '',
                    'status': row['status'] or '',
                    'description': row['description'] or '',
                    'spare_parts': spare_parts,
                    'labour_works': labour_works,
                    'outsource_works': outsource_works,
                    'spare_cost': spare_cost,
                    'labour_cost': labour_cost,
                    'outsource_cost': outsource_cost,
                    'total_cost': spare_cost + labour_cost + outsource_cost
                }
                self.all_records.append(record)
            
            # Apply search filter
            search_text = self.search_input.text().strip().lower()
            if search_text:
                self.filtered_records = []
                for r in self.all_records:
                    # Check basic fields
                    if (search_text in r['job_no'].lower()
                        or search_text in r['vehicle_no'].lower()
                        or search_text in r['driver'].lower()
                        or search_text in r['section'].lower()
                        or search_text in r['site'].lower()):
                        self.filtered_records.append(r)
                        continue
                    
                    # Check spare parts (name and ID)
                    found_in_parts = False
                    for part in r['spare_parts']:
                        part_desc = (part.get('description') or part.get('item_description') or '').lower()
                        part_id = (part.get('id_code') or '').lower()
                        if search_text in part_desc or search_text in part_id:
                            found_in_parts = True
                            break
                    
                    if found_in_parts:
                        self.filtered_records.append(r)
            else:
                self.filtered_records = self.all_records
            
            # Apply sorting
            sort_mode = self.sort_combo.currentText()
            if sort_mode == "Latest First":
                self.filtered_records.sort(key=lambda x: x['start_date'], reverse=True)
            elif sort_mode == "Oldest First":
                self.filtered_records.sort(key=lambda x: x['start_date'])
            elif sort_mode == "Highest Cost":
                self.filtered_records.sort(key=lambda x: x['total_cost'], reverse=True)
            elif sort_mode == "Lowest Cost":
                self.filtered_records.sort(key=lambda x: x['total_cost'])
            elif sort_mode == "Vehicle (A-Z)":
                self.filtered_records.sort(key=lambda x: x['vehicle_no'])
            elif sort_mode == "Site (A-Z)":
                self.filtered_records.sort(key=lambda x: x['site'])
            
            # Update stats and tables
            self._update_stats()
            self._update_overview()
            self._update_parts_analysis()
            self._update_vehicle_analysis()
            self._update_cost_analysis()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate report:\n{str(e)}")
    
    def _update_stats(self):
        """Update statistics cards"""
        # Clear existing cards
        while self.stats_container.count():
            item = self.stats_container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        total_jobs = len(self.filtered_records)
        completed = sum(1 for r in self.filtered_records if r['status'] == 'Completed')
        in_progress = total_jobs - completed
        total_cost = sum(r['total_cost'] for r in self.filtered_records)
        
        self._add_stat_card("Total Jobs", str(total_jobs), ColorPalette.ACCENT_PRIMARY)
        self._add_stat_card("Completed", str(completed), ColorPalette.ACCENT_GREEN)
        self._add_stat_card("In Progress", str(in_progress), ColorPalette.ACCENT_ORANGE)
        self._add_stat_card("Total Cost", self._format_currency(total_cost), ColorPalette.ACCENT_SECONDARY)
    
    def _add_stat_card(self, label, value, color):
        """Add a statistics card"""
        card = QFrame()
        card.setObjectName("card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(4)
        
        value_label = QLabel(value)
        value_label.setObjectName("stat_value")
        value_label.setStyleSheet(f"color: {color}; background-color: transparent;")
        
        text_label = QLabel(label)
        text_label.setObjectName("stat_label")
        text_label.setStyleSheet("background-color: transparent;")
        
        layout.addWidget(value_label)
        layout.addWidget(text_label)
        
        self.stats_container.addWidget(card)
    
    def _update_overview(self):
        """Update overview table with key metrics"""
        metrics = [
            ("Total Job Cards", str(len(self.filtered_records))),
            ("Completed Jobs", str(sum(1 for r in self.filtered_records if r['status'] == 'Completed'))),
            ("In Progress Jobs", str(sum(1 for r in self.filtered_records if r['status'] == 'In Progress'))),
            ("Unique Vehicles", str(len(set(r['vehicle_no'] for r in self.filtered_records if r['vehicle_no'] not in ['', '-'])))),
            ("Active Sites", str(len(set(r['site'] for r in self.filtered_records if r['site'])))),
            ("Total Spare Parts Cost", self._format_currency(sum(r['spare_cost'] for r in self.filtered_records))),
            ("Total Labour Cost", self._format_currency(sum(r['labour_cost'] for r in self.filtered_records))),
            ("Total Outsource Cost", self._format_currency(sum(r['outsource_cost'] for r in self.filtered_records))),
            ("Grand Total Cost", self._format_currency(sum(r['total_cost'] for r in self.filtered_records))),
        ]
        
        self._populate_table(self.overview_table, ["Metric", "Value"], 
                           [[m[0], m[1]] for m in metrics])
    
    def _update_parts_analysis(self):
        """Analyze spare parts usage"""
        parts_stats = defaultdict(lambda: {'qty': 0, 'cost': 0, 'jobs': set(), 'vehicles': set(), 'dates': []})
        
        for record in self.filtered_records:
            for part in record['spare_parts']:
                desc = part.get('description') or part.get('item_description') or 'Unknown'
                id_code = part.get('id_code', '')
                key = f"{id_code} - {desc}" if id_code else desc
                
                parts_stats[key]['qty'] += self._to_float(part.get('quantity', 0))
                parts_stats[key]['cost'] += self._to_float(part.get('total', 0))
                parts_stats[key]['jobs'].add(record['job_no'])
                if record['vehicle_no'] not in ['', '-']:
                    parts_stats[key]['vehicles'].add(record['vehicle_no'])
                if record['start_date']:
                    parts_stats[key]['dates'].append(record['start_date'])
        
        # Sort by cost
        sorted_parts = sorted(parts_stats.items(), key=lambda x: x[1]['cost'], reverse=True)
        
        rows = []
        for part_name, stats in sorted_parts[:50]:  # Top 50
            # Get latest date
            latest_date = max(stats['dates']) if stats['dates'] else '-'
            rows.append([
                part_name,
                latest_date,
                f"{stats['qty']:.2f}",
                str(len(stats['jobs'])),
                str(len(stats['vehicles'])),
                self._format_currency(stats['cost'])
            ])
        
        self._populate_table(self.parts_table, 
                           ["Spare Part", "Latest Use", "Total Qty", "Jobs", "Vehicles", "Total Cost"],
                           rows)
    
    def _update_vehicle_analysis(self):
        """Analyze vehicle service records"""
        vehicle_stats = defaultdict(lambda: {
            'jobs': 0, 'cost': 0, 'spare': 0, 'labour': 0, 'outsource': 0,
            'last_service': None, 'sections': set()
        })
        
        for record in self.filtered_records:
            vehicle = record['vehicle_no']
            if vehicle in ['', '-']:
                continue
            
            vehicle_stats[vehicle]['jobs'] += 1
            vehicle_stats[vehicle]['cost'] += record['total_cost']
            vehicle_stats[vehicle]['spare'] += record['spare_cost']
            vehicle_stats[vehicle]['labour'] += record['labour_cost']
            vehicle_stats[vehicle]['outsource'] += record['outsource_cost']
            
            if record['start_date']:
                if not vehicle_stats[vehicle]['last_service'] or record['start_date'] > vehicle_stats[vehicle]['last_service']:
                    vehicle_stats[vehicle]['last_service'] = record['start_date']
            
            if record['section']:
                vehicle_stats[vehicle]['sections'].add(record['section'])
        
        # Sort by jobs count
        sorted_vehicles = sorted(vehicle_stats.items(), key=lambda x: x[1]['jobs'], reverse=True)
        
        rows = []
        for vehicle, stats in sorted_vehicles[:50]:  # Top 50
            rows.append([
                vehicle,
                str(stats['jobs']),
                stats['last_service'] or '—',
                str(len(stats['sections'])),
                self._format_currency(stats['cost']),
                self._format_currency(stats['cost'] / stats['jobs'] if stats['jobs'] > 0 else 0)
            ])
        
        self._populate_table(self.vehicle_table,
                           ["Vehicle", "Jobs", "Last Service", "Sections", "Total Cost", "Avg Cost/Job"],
                           rows)
    
    def _update_cost_analysis(self):
        """Break down costs by month"""
        monthly_costs = defaultdict(lambda: {
            'jobs': 0, 'spare': 0, 'labour': 0, 'outsource': 0, 'total': 0
        })
        
        for record in self.filtered_records:
            if not record['start_date']:
                continue
            
            try:
                date_obj = datetime.datetime.strptime(record['start_date'], '%Y-%m-%d')
                month_key = date_obj.strftime('%Y-%m')
                
                monthly_costs[month_key]['jobs'] += 1
                monthly_costs[month_key]['spare'] += record['spare_cost']
                monthly_costs[month_key]['labour'] += record['labour_cost']
                monthly_costs[month_key]['outsource'] += record['outsource_cost']
                monthly_costs[month_key]['total'] += record['total_cost']
            except:
                pass
        
        # Sort by month (newest first)
        sorted_months = sorted(monthly_costs.items(), key=lambda x: x[0], reverse=True)
        
        rows = []
        for month, costs in sorted_months:
            rows.append([
                month,
                str(costs['jobs']),
                self._format_currency(costs['spare']),
                self._format_currency(costs['labour']),
                self._format_currency(costs['outsource']),
                self._format_currency(costs['total'])
            ])
        
        self._populate_table(self.cost_table,
                           ["Month", "Jobs", "Spare Parts", "Labour", "Outsource", "Total"],
                           rows)
    
    def _populate_table(self, table, headers, rows):
        """Populate table with data"""
        table.clear()
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.setRowCount(len(rows))
        
        for row_idx, row_data in enumerate(rows):
            for col_idx, value in enumerate(row_data):
                item = QTableWidgetItem(str(value))
                item.setFlags(item.flags() ^ Qt.ItemIsEditable)
                
                # Right-align numbers
                if col_idx > 0 and ('Rs.' in str(value) or self._is_number(str(value))):
                    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                
                table.setItem(row_idx, col_idx, item)
        
        # Set all tables to full width with proportional column sizing
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.horizontalHeader().setStretchLastSection(True)
    
    def on_tab_changed(self, index):
        """Handle tab changes"""
        pass  # All data already loaded
    
    def export_csv(self):
        """Export selected tabs to CSV"""
        # Ask which pages to export
        dialog = QDialog(self)
        dialog.setWindowTitle("Select Pages to Export")
        dialog.setMinimumWidth(300)
        
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        
        lbl = QLabel("Select the pages you want to export:")
        layout.addWidget(lbl)
        
        checkboxes = []
        tab_names = ["Overview", "Spare Parts", "Vehicles", "Cost Breakdown"]
        for i, name in enumerate(tab_names):
            cb = QCheckBox(name)
            cb.setChecked(i == self.tabs.currentIndex())
            checkboxes.append(cb)
            layout.addWidget(cb)
        
        btn_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btn_box.accepted.connect(dialog.accept)
        btn_box.rejected.connect(dialog.reject)
        layout.addWidget(btn_box)
        
        if dialog.exec() != QDialog.Accepted:
            return
        
        selected_indices = [i for i, cb in enumerate(checkboxes) if cb.isChecked()]
        if not selected_indices:
            QMessageBox.warning(self, "No Selection", "Please select at least one page to export.")
            return
        
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Export to CSV",
            f"Report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            "CSV Files (*.csv)"
        )
        
        if not filename:
            return
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                for idx in selected_indices:
                    table = [self.overview_table, self.parts_table, self.vehicle_table, self.cost_table][idx]
                    tab_name = tab_names[idx]
                    
                    # Section header
                    writer.writerow([])
                    writer.writerow([f"=== {tab_name} ==="])
                    writer.writerow([])
                    
                    # Headers
                    headers = [table.horizontalHeaderItem(i).text() if table.horizontalHeaderItem(i) else ""
                              for i in range(table.columnCount())]
                    writer.writerow(headers)
                    
                    # Data
                    for row in range(table.rowCount()):
                        row_data = [table.item(row, col).text() if table.item(row, col) else ""
                                   for col in range(table.columnCount())]
                        writer.writerow(row_data)
            
            QMessageBox.information(self, "Success", f"Report exported to:\\n{filename}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Export failed:\\n{str(e)}")
    
    def export_xlsx(self):
        """Export selected tabs to Excel with multiple sheets"""
        if not HAS_OPENPYXL:
            QMessageBox.warning(self, "Not Available", 
                              "Excel export requires openpyxl.\\nInstall: pip install openpyxl")
            return
        
        # Ask which pages to export
        dialog = QDialog(self)
        dialog.setWindowTitle("Select Pages to Export")
        dialog.setMinimumWidth(300)
        
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        
        lbl = QLabel("Select the pages you want to export:")
        layout.addWidget(lbl)
        
        checkboxes = []
        tab_names = ["Overview", "Spare Parts", "Vehicles", "Cost Breakdown"]
        for i, name in enumerate(tab_names):
            cb = QCheckBox(name)
            cb.setChecked(i == self.tabs.currentIndex())
            checkboxes.append(cb)
            layout.addWidget(cb)
        
        btn_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btn_box.accepted.connect(dialog.accept)
        btn_box.rejected.connect(dialog.reject)
        layout.addWidget(btn_box)
        
        if dialog.exec() != QDialog.Accepted:
            return
        
        selected_indices = [i for i, cb in enumerate(checkboxes) if cb.isChecked()]
        if not selected_indices:
            QMessageBox.warning(self, "No Selection", "Please select at least one page to export.")
            return
        
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Export to Excel",
            f"Report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            "Excel Files (*.xlsx)"
        )
        
        if not filename:
            return
        
        try:
            wb = openpyxl.Workbook()
            wb.remove(wb.active)  # Remove default sheet
            
            # Styling
            header_fill = PatternFill(start_color="2E7D6E", end_color="2E7D6E", fill_type="solid")
            header_font = XLFont(color="FFFFFF", bold=True)
            border = Border(
                left=Side(style='thin'),
                right=Side(style='thin'),
                top=Side(style='thin'),
                bottom=Side(style='thin')
            )
            
            for idx in selected_indices:
                table = [self.overview_table, self.parts_table, self.vehicle_table, self.cost_table][idx]
                sheet_name = tab_names[idx][:31]  # Excel sheet name limit
                ws = wb.create_sheet(title=sheet_name)
                
                # Headers
                for col in range(table.columnCount()):
                    cell = ws.cell(row=1, column=col+1)
                    cell.value = table.horizontalHeaderItem(col).text() if table.horizontalHeaderItem(col) else ""
                    cell.fill = header_fill
                    cell.font = header_font
                    cell.border = border
                    cell.alignment = Alignment(horizontal='center')
                
                # Data
                for row in range(table.rowCount()):
                    for col in range(table.columnCount()):
                        item = table.item(row, col)
                        cell = ws.cell(row=row+2, column=col+1)
                        cell.value = item.text() if item else ""
                        cell.border = border
            
            # Auto-fit columns
            for column in ws.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    if cell.value:
                        max_length = max(max_length, len(str(cell.value)))
                ws.column_dimensions[column_letter].width = min(max_length + 2, 50)
            
            wb.save(filename)
            QMessageBox.information(self, "Success", f"Report exported to:\n{filename}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Export failed:\n{str(e)}")
    
    def export_pdf(self):
        """Export selected tabs to professional PDF with headers and footers"""
        if not HAS_REPORTLAB:
            QMessageBox.warning(self, "Not Available",
                              "PDF export requires reportlab.\\nInstall: pip install reportlab")
            return
        
        # Ask which pages to export
        dialog = QDialog(self)
        dialog.setWindowTitle("Select Pages to Export")
        dialog.setMinimumWidth(300)
        
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        
        lbl = QLabel("Select the pages you want to export:")
        layout.addWidget(lbl)
        
        checkboxes = []
        tab_names = ["Overview", "Spare Parts", "Vehicles", "Cost Breakdown"]
        for i, name in enumerate(tab_names):
            cb = QCheckBox(name)
            cb.setChecked(i == self.tabs.currentIndex())
            checkboxes.append(cb)
            layout.addWidget(cb)
        
        btn_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btn_box.accepted.connect(dialog.accept)
        btn_box.rejected.connect(dialog.reject)
        layout.addWidget(btn_box)
        
        if dialog.exec() != QDialog.Accepted:
            return
        
        selected_indices = [i for i, cb in enumerate(checkboxes) if cb.isChecked()]
        if not selected_indices:
            QMessageBox.warning(self, "No Selection", "Please select at least one page to export.")
            return
        
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Export to PDF",
            f"Report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            "PDF Files (*.pdf)"
        )
        
        if not filename:
            return
        
        try:
            # Professional colors
            accent_primary = colors.HexColor('#2E7D6E')
            neutral_bg = colors.HexColor('#f8fafc')
            neutral_border = colors.HexColor('#d4dce9')
            slate = colors.HexColor('#475569')
            muted = colors.HexColor('#94a3b8')
            
            timestamp = datetime.datetime.now()
            timestamp_str = timestamp.strftime('%d %b %Y %H:%M')
            
            logo_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                'assets',
                'logo.png'
            )
            
            # Custom header/footer function
            def add_header_footer(canvas_obj, doc_obj):
                canvas_obj.saveState()
                page_width, page_height = doc_obj.pagesize
                header_height = 0.85 * inch
                
                # Header background
                canvas_obj.setFillColor(colors.white)
                canvas_obj.rect(0, page_height - header_height, page_width, header_height, fill=1, stroke=0)
                canvas_obj.setFillColor(accent_primary)
                canvas_obj.rect(0, page_height - header_height, page_width, 10, fill=1, stroke=0)
                
                # Logo
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
                
                # Title
                title_x = doc_obj.leftMargin + 120
                canvas_obj.setFont('Helvetica-Bold', 15)
                canvas_obj.setFillColor(accent_primary)
                canvas_obj.drawString(title_x, page_height - 0.38 * inch, 'Analytics Report')
                canvas_obj.setFont('Helvetica', 9)
                canvas_obj.setFillColor(colors.HexColor('#1f2937'))
                canvas_obj.drawString(
                    title_x,
                    page_height - 0.56 * inch,
                    f"Generated: {timestamp_str}"
                )
                
                # Footer
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
                    f"Computer generated analytics report on {timestamp_str}."
                )
                canvas_obj.drawRightString(
                    page_width - doc_obj.rightMargin,
                    footer_y,
                    f"Page {canvas_obj.getPageNumber()}"
                )
                
                canvas_obj.restoreState()
            
            # Create PDF document
            doc = SimpleDocTemplate(
                filename,
                pagesize=A4,
                topMargin=0.9 * inch,
                bottomMargin=0.7 * inch,
                leftMargin=0.6 * inch,
                rightMargin=0.6 * inch
            )
            
            story = []
            styles = getSampleStyleSheet()
            
            # Define professional styles
            section_heading = ParagraphStyle(
                'SectionHeading',
                parent=styles['Heading2'],
                fontSize=12,
                textColor=accent_primary,
                spaceBefore=0,
                spaceAfter=10,
                fontName='Helvetica-Bold'
            )
            
            body_style = ParagraphStyle(
                'BodyStyle',
                parent=styles['Normal'],
                fontSize=8,
                textColor=slate,
                leading=11
            )
            
            # Build content for each selected tab
            for idx in selected_indices:
                table = [self.overview_table, self.parts_table, self.vehicle_table, self.cost_table][idx]
                tab_name = tab_names[idx]
                
                # Section header
                story.append(Paragraph(tab_name, section_heading))
                story.append(Spacer(1, 0.1 * inch))
                
                # Table data
                data = []
                headers = [table.horizontalHeaderItem(i).text() if table.horizontalHeaderItem(i) else ""
                          for i in range(table.columnCount())]
                data.append(headers)
                
                for row in range(min(table.rowCount(), 100)):  # Limit rows per section
                    row_data = [table.item(row, col).text() if table.item(row, col) else ""
                               for col in range(table.columnCount())]
                    data.append(row_data)
                
                # Calculate column widths based on content type
                num_cols = len(headers)
                available_width = doc.width  # Full page width minus margins
                
                # Adjust column widths based on table type
                if tab_name == "Spare Parts":
                    # Spare Part: 40%, Latest Use: 12%, Total Qty: 12%, Jobs: 12%, Vehicles: 12%, Total Cost: 12%
                    col_widths = [
                        available_width * 0.40,  # Spare Part (wider for long names)
                        available_width * 0.12,  # Latest Use
                        available_width * 0.12,  # Total Qty
                        available_width * 0.12,  # Jobs
                        available_width * 0.12,  # Vehicles
                        available_width * 0.12   # Total Cost
                    ]
                else:
                    # Equal width for other tables
                    col_widths = [available_width / num_cols] * num_cols
                
                # Create PDF table with full width
                pdf_table = Table(data, colWidths=col_widths)
                pdf_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), accent_primary),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 9),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                    ('TOPPADDING', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
                    ('TOPPADDING', (0, 1), (-1, -1), 6),
                    ('GRID', (0, 0), (-1, -1), 0.5, neutral_border),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, neutral_bg]),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('WORDWRAP', (0, 0), (-1, -1), True),
                ]))
                
                story.append(pdf_table)
                
                # Add page break between sections except for last one
                if idx != selected_indices[-1]:
                    story.append(PageBreak())
                else:
                    story.append(Spacer(1, 0.2 * inch))
            
            # Build PDF with custom header/footer
            doc.build(story, onFirstPage=add_header_footer, onLaterPages=add_header_footer)
            
            QMessageBox.information(self, "Success", f"Report exported to:\\n{filename}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Export failed:\\n{str(e)}")
    
    def _safe_json_loads(self, payload):
        """Safely parse JSON"""
        if not payload:
            return []
        try:
            data = json.loads(payload)
            return data if isinstance(data, list) else []
        except:
            return []
    
    def _to_float(self, value):
        """Convert to float safely"""
        if value in (None, "", "-"):
            return 0.0
        try:
            return float(str(value).replace(",", "").strip())
        except:
            return 0.0
    
    def _format_currency(self, value):
        """Format as currency"""
        try:
            return f"Rs. {float(value):,.2f}"
        except:
            return "Rs. 0.00"
    
    def _is_number(self, value):
        """Check if value is numeric"""
        try:
            float(str(value).replace(",", "").strip())
            return True
        except:
            return False
    
    def go_back(self):
        """Navigate back"""
        if self.parent:
            self.parent.go_to_home()
