"""
Advanced Analytics & Reporting Module
Provides comprehensive insights into workshop operations with export capabilities
"""
import sqlite3
import csv
import json
import datetime
from collections import defaultdict
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox, QComboBox, QDateEdit,
    QFrame, QFileDialog, QHeaderView, QTabWidget, QGridLayout
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont
from ui.theme import ColorPalette, Typography, Spacing, Styles, create_page_header

DB_PATH = "ui/db/senarath.db"

# Check for optional libraries
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
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
    """Advanced analytics dashboard with comprehensive reporting capabilities"""
    
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.current_report_data = None
        
        bg_color = "#f5f5f0"
        card_color = ColorPalette.CARD_BG
        accent_color = ColorPalette.ACCENT_PRIMARY
        text_primary = "#2c2c2c"
        text_secondary = ColorPalette.TEXT_SECONDARY
        border_color = "#d4d4d4"

        self.setStyleSheet(f"""
            QWidget {{
                background-color: {bg_color};
                font-family: 'Segoe UI', Arial;
                color: {text_primary};
            }}
            QFrame#stat_card {{
                background-color: {card_color};
                border: 1px solid {border_color};
                border-radius: {Spacing.BORDER_RADIUS_MEDIUM}px;
            }}
            QFrame#filter_card {{
                background-color: {card_color};
                border: 1px solid {border_color};
                border-radius: {Spacing.BORDER_RADIUS_SMALL}px;
            }}
            QLabel#stat_value {{
                color: {accent_color};
                font-size: 24px;
                font-weight: 700;
            }}
            QLabel#stat_label {{
                color: {text_secondary};
                font-size: 11px;
                font-weight: 600;
                text-transform: uppercase;
            }}
            QLabel#section_title {{
                color: {text_primary};
                font-size: 14px;
                font-weight: 700;
            }}
            QComboBox, QDateEdit {{
                background-color: #fafafa;
                border: 1px solid {border_color};
                border-radius: {Spacing.BORDER_RADIUS_SMALL}px;
                padding: 6px 8px;
                font-size: 12px;
                min-height: 24px;
                color: {text_primary};
            }}
            QComboBox:focus, QDateEdit:focus {{
                border: 2px solid {accent_color};
                background-color: white;
            }}
            QTableWidget {{
                background-color: {card_color};
                border: 1px solid {border_color};
                border-radius: {Spacing.BORDER_RADIUS_SMALL}px;
                gridline-color: {border_color};
                alternate-background-color: #f8f8f3;
                font-size: 11px;
            }}
            QHeaderView::section {{
                background-color: {accent_color};
                color: white;
                padding: 8px;
                border: none;
                font-weight: 600;
                font-size: 11px;
            }}
            QTableWidget::item {{
                padding: 4px;
                color: {text_primary};
            }}
            QTableWidget::item:selected {{
                background-color: rgba(45, 122, 95, 0.18);
            }}
            QTabWidget::pane {{
                border: 1px solid {border_color};
                border-radius: {Spacing.BORDER_RADIUS_SMALL}px;
                background-color: {card_color};
            }}
            QTabBar::tab {{
                background-color: transparent;
                padding: 8px 16px;
                font-weight: 600;
                color: {text_secondary};
                border: none;
            }}
            QTabBar::tab:selected {{
                color: {accent_color};
                border-bottom: 3px solid {accent_color};
            }}
        """)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(18, 18, 18, 18)
        main_layout.setSpacing(16)
        
        # Header
        header_layout, title_label, back_btn = create_page_header("📊 Analytics & Reports")
        back_btn.clicked.connect(self.go_back)
        main_layout.addLayout(header_layout)
        
        # Filter Panel
        filter_frame = QFrame()
        filter_frame.setObjectName("filter_card")
        filter_layout = QVBoxLayout(filter_frame)
        filter_layout.setContentsMargins(16, 14, 16, 14)
        filter_layout.setSpacing(8)
        
        filter_title = QLabel("Report Filters")
        filter_title.setObjectName("section_title")
        filter_layout.addWidget(filter_title)
        
        # Filter controls laid out on compact grid
        controls_grid = QGridLayout()
        controls_grid.setContentsMargins(0, 0, 0, 0)
        controls_grid.setHorizontalSpacing(12)
        controls_grid.setVerticalSpacing(8)

        def _add_filter(label_text: str, widget, row: int, col: int):
            label = QLabel(label_text)
            label.setStyleSheet(f"color: {text_secondary}; font-size: 11px; font-weight: 600;")
            controls_grid.addWidget(label, row, col)
            controls_grid.addWidget(widget, row, col + 1)

        self.period_combo = QComboBox()
        self.period_combo.addItems(["Last 7 Days", "Last 30 Days", "Last 3 Months", "Last 6 Months", "This Year", "Custom Range"])
        self.period_combo.setMinimumWidth(140)
        self.period_combo.currentTextChanged.connect(self.on_period_changed)
        _add_filter("Period", self.period_combo, 0, 0)

        date_row = 0
        self.from_date = QDateEdit()
        self.from_date.setCalendarPopup(True)
        self.from_date.setDisplayFormat("yyyy-MM-dd")
        self.from_date.setDate(QDate.currentDate().addDays(-30))
        self.from_date.setEnabled(False)
        self.from_date.setMinimumWidth(130)
        _add_filter("From", self.from_date, date_row, 2)

        self.to_date = QDateEdit()
        self.to_date.setCalendarPopup(True)
        self.to_date.setDisplayFormat("yyyy-MM-dd")
        self.to_date.setDate(QDate.currentDate())
        self.to_date.setEnabled(False)
        self.to_date.setMinimumWidth(130)
        _add_filter("To", self.to_date, date_row, 4)

        self.site_filter = QComboBox()
        self.site_filter.addItem("All Sites")
        self.load_sites()
        self.site_filter.setMinimumWidth(150)
        _add_filter("Site", self.site_filter, 1, 0)

        self.status_filter = QComboBox()
        self.status_filter.addItems(["All Status", "Completed", "In Progress"])
        self.status_filter.setMinimumWidth(130)
        _add_filter("Status", self.status_filter, 1, 2)

        # Generate button aligned to the right column spanning rows
        generate_btn = QPushButton("Generate")
        generate_btn.setStyleSheet(Styles.get_button_primary())
        generate_btn.setFixedHeight(28)
        generate_btn.setCursor(Qt.PointingHandCursor)
        generate_btn.clicked.connect(self.generate_report)
        controls_grid.addWidget(generate_btn, 0, 6, 2, 1, alignment=Qt.AlignRight | Qt.AlignVCenter)

        # Spacer to keep grid compact but responsive
        controls_grid.setColumnStretch(5, 1)
        controls_grid.setColumnStretch(6, 0)

        filter_layout.addLayout(controls_grid)
        main_layout.addWidget(filter_frame)
        
        # Stats Cards
        self.stats_container = QHBoxLayout()
        self.stats_container.setSpacing(12)
        main_layout.addLayout(self.stats_container)
        
        # Tabs for different report views
        self.tabs = QTabWidget()
        self.tabs.addTab(self._create_overview_tab(), "📈 Overview")
        self.tabs.addTab(self._create_spare_parts_tab(), "🔧 Spare Parts Analysis")
        self.tabs.addTab(self._create_vehicle_tab(), "🚗 Vehicle Analysis")
        self.tabs.addTab(self._create_cost_tab(), "💰 Cost Analysis")
        self.tabs.addTab(self._create_performance_tab(), "⚡ Performance Metrics")
        main_layout.addWidget(self.tabs, 1)
        
        # Export buttons
        export_layout = QHBoxLayout()
        export_layout.addStretch()
        
        csv_btn = QPushButton("📄 Export CSV")
        csv_btn.setStyleSheet(Styles.get_button_secondary())
        csv_btn.setFixedHeight(28)
        csv_btn.setCursor(Qt.PointingHandCursor)
        csv_btn.clicked.connect(self.export_csv)
        export_layout.addWidget(csv_btn)
        
        if HAS_OPENPYXL:
            xlsx_btn = QPushButton("📊 Export Excel")
            xlsx_btn.setStyleSheet(Styles.get_button_secondary())
            xlsx_btn.setFixedHeight(28)
            xlsx_btn.setCursor(Qt.PointingHandCursor)
            xlsx_btn.clicked.connect(self.export_xlsx)
            export_layout.addWidget(xlsx_btn)
        
        if HAS_REPORTLAB:
            pdf_btn = QPushButton("📑 Export PDF")
            pdf_btn.setStyleSheet(Styles.get_button_secondary())
            pdf_btn.setFixedHeight(28)
            pdf_btn.setCursor(Qt.PointingHandCursor)
            pdf_btn.clicked.connect(self.export_pdf)
            export_layout.addWidget(pdf_btn)
        
        main_layout.addLayout(export_layout)
        
        # Initial data load
        self.generate_report()
    
    def _create_overview_tab(self):
        """Overview statistics and summary"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)
        
        self.overview_table = QTableWidget()
        self.overview_table.setAlternatingRowColors(True)
        self.overview_table.verticalHeader().setVisible(False)
        self.overview_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.overview_table.setSelectionMode(QTableWidget.NoSelection)
        layout.addWidget(self.overview_table)
        
        return tab
    
    def _create_spare_parts_tab(self):
        """Spare parts usage analysis"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)
        
        self.spare_parts_table = QTableWidget()
        self.spare_parts_table.setAlternatingRowColors(True)
        self.spare_parts_table.verticalHeader().setVisible(False)
        self.spare_parts_table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.spare_parts_table)
        
        return tab
    
    def _create_vehicle_tab(self):
        """Vehicle-specific analysis"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)
        
        self.vehicle_table = QTableWidget()
        self.vehicle_table.setAlternatingRowColors(True)
        self.vehicle_table.verticalHeader().setVisible(False)
        self.vehicle_table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.vehicle_table)
        
        return tab
    
    def _create_cost_tab(self):
        """Cost breakdown and analysis"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)
        
        self.cost_table = QTableWidget()
        self.cost_table.setAlternatingRowColors(True)
        self.cost_table.verticalHeader().setVisible(False)
        self.cost_table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.cost_table)
        
        return tab
    
    def _create_performance_tab(self):
        """Performance metrics and KPIs"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)
        
        self.performance_table = QTableWidget()
        self.performance_table.setAlternatingRowColors(True)
        self.performance_table.verticalHeader().setVisible(False)
        self.performance_table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.performance_table)
        
        return tab
    
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
    
    def on_period_changed(self, period):
        """Handle period selection changes"""
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
            self.to_date.setDate(today)
    
    def generate_report(self):
        """Generate comprehensive analytics report"""
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            
            # Build query with filters
            query = """
                SELECT id, job_no, company_no, vehicle_no, driver, make, model, type,
                       site, section, start_date, end_date, description, 
                       spare_parts, labour_works, outsource_works, status
                FROM job_cards WHERE 1=1
            """
            params = []
            
            from_date = self.from_date.date().toString("yyyy-MM-dd")
            to_date = self.to_date.date().toString("yyyy-MM-dd")
            query += " AND start_date >= ? AND start_date <= ?"
            params.extend([from_date, to_date])
            
            if self.site_filter.currentText() != "All Sites":
                query += " AND site = ?"
                params.append(self.site_filter.currentText())
            
            if self.status_filter.currentText() != "All Status":
                query += " AND status = ?"
                params.append(self.status_filter.currentText())
            
            query += " ORDER BY start_date DESC"
            
            c.execute(query, params)
            job_cards = c.fetchall()
            conn.close()
            
            self.current_report_data = job_cards
            
            # Update all tabs
            self._update_stats_cards(job_cards)
            self._update_overview_tab(job_cards)
            self._update_spare_parts_tab(job_cards)
            self._update_vehicle_tab(job_cards)
            self._update_cost_tab(job_cards)
            self._update_performance_tab(job_cards)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate report:\n{str(e)}")
    
    def _update_stats_cards(self, job_cards):
        """Update top-level statistics cards"""
        # Clear existing cards
        while self.stats_container.count():
            item = self.stats_container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        total_jobs = len(job_cards)
        completed_jobs = sum(1 for jc in job_cards if jc[16] == "Completed")
        
        total_spare_cost = 0
        total_labour_cost = 0
        total_outsource_cost = 0
        
        for jc in job_cards:
            # Spare parts
            try:
                spare_parts = json.loads(jc[13]) if jc[13] else []
                for part in spare_parts:
                    total_spare_cost += float(part.get('total', 0))
            except:
                pass
            
            # Labour
            try:
                labour_works = json.loads(jc[14]) if jc[14] else []
                for work in labour_works:
                    total_labour_cost += float(work.get('work_cost', 0))
            except:
                pass
            
            # Outsource
            try:
                outsource_works = json.loads(jc[15]) if jc[15] else []
                for work in outsource_works:
                    total_outsource_cost += float(work.get('cost', 0))
            except:
                pass
        
        total_cost = total_spare_cost + total_labour_cost + total_outsource_cost
        
        # Create stat cards
        self._add_stat_card("Total Jobs", str(total_jobs), ColorPalette.ACCENT_PRIMARY)
        self._add_stat_card("Completed", str(completed_jobs), ColorPalette.ACCENT_GREEN)
        self._add_stat_card("In Progress", str(total_jobs - completed_jobs), ColorPalette.ACCENT_ORANGE)
        self._add_stat_card("Total Cost", f"Rs. {total_cost:,.2f}", ColorPalette.ACCENT_SECONDARY)
    
    def _add_stat_card(self, label, value, color):
        """Add a statistics card"""
        card = QFrame()
        card.setObjectName("stat_card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(4)
        
        value_label = QLabel(value)
        value_label.setObjectName("stat_value")
        value_label.setStyleSheet(f"color: {color};")
        
        text_label = QLabel(label)
        text_label.setObjectName("stat_label")
        
        layout.addWidget(value_label)
        layout.addWidget(text_label)
        
        self.stats_container.addWidget(card)
    
    def _update_overview_tab(self, job_cards):
        """Update overview statistics"""
        headers = ["Metric", "Value"]
        self.overview_table.setColumnCount(2)
        self.overview_table.setHorizontalHeaderLabels(headers)
        
        metrics = []
        
        # Basic counts
        metrics.append(("Total Job Cards", str(len(job_cards))))
        metrics.append(("Completed Jobs", str(sum(1 for jc in job_cards if jc[16] == "Completed"))))
        metrics.append(("In Progress Jobs", str(sum(1 for jc in job_cards if jc[16] == "In Progress"))))
        
        # Unique counts
        unique_vehicles = len(set(jc[3] for jc in job_cards if jc[3]))
        unique_drivers = len(set(jc[4] for jc in job_cards if jc[4]))
        unique_sites = len(set(jc[8] for jc in job_cards if jc[8]))
        
        metrics.append(("Unique Vehicles Serviced", str(unique_vehicles)))
        metrics.append(("Unique Drivers", str(unique_drivers)))
        metrics.append(("Active Sites", str(unique_sites)))
        
        # Cost totals
        total_spare = sum(self._get_spare_cost(jc[13]) for jc in job_cards)
        total_labour = sum(self._get_labour_cost(jc[14]) for jc in job_cards)
        total_outsource = sum(self._get_outsource_cost(jc[15]) for jc in job_cards)
        
        metrics.append(("Total Spare Parts Cost", f"Rs. {total_spare:,.2f}"))
        metrics.append(("Total Labour Cost", f"Rs. {total_labour:,.2f}"))
        metrics.append(("Total Outsource Cost", f"Rs. {total_outsource:,.2f}"))
        metrics.append(("Grand Total Cost", f"Rs. {(total_spare + total_labour + total_outsource):,.2f}"))
        
        # Populate table
        self.overview_table.setRowCount(len(metrics))
        for row, (metric, value) in enumerate(metrics):
            self.overview_table.setItem(row, 0, QTableWidgetItem(metric))
            value_item = QTableWidgetItem(value)
            value_item.setFont(QFont("Arial", 10, QFont.Bold))
            self.overview_table.setItem(row, 1, value_item)
        
        self.overview_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.overview_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
    
    def _update_spare_parts_tab(self, job_cards):
        """Analyze spare parts usage"""
        part_usage = defaultdict(lambda: {"quantity": 0, "cost": 0, "jobs": set(), "vehicles": set()})
        
        for jc in job_cards:
            try:
                spare_parts = json.loads(jc[13]) if jc[13] else []
                for part in spare_parts:
                    key = f"{part.get('id_code', 'N/A')} - {part.get('item_description', 'N/A')}"
                    part_usage[key]["quantity"] += float(part.get('quantity', 0))
                    part_usage[key]["cost"] += float(part.get('total', 0))
                    part_usage[key]["jobs"].add(jc[1])  # job_no
                    if jc[3]:  # vehicle_no
                        part_usage[key]["vehicles"].add(jc[3])
            except:
                pass
        
        # Sort by cost descending
        sorted_parts = sorted(part_usage.items(), key=lambda x: x[1]["cost"], reverse=True)
        
        headers = ["Spare Part", "Total Qty", "Total Cost", "Used in Jobs", "Vehicles"]
        self.spare_parts_table.setColumnCount(5)
        self.spare_parts_table.setHorizontalHeaderLabels(headers)
        self.spare_parts_table.setRowCount(len(sorted_parts))
        
        for row, (part, data) in enumerate(sorted_parts):
            self.spare_parts_table.setItem(row, 0, QTableWidgetItem(part))
            self.spare_parts_table.setItem(row, 1, QTableWidgetItem(f"{data['quantity']:.2f}"))
            self.spare_parts_table.setItem(row, 2, QTableWidgetItem(f"Rs. {data['cost']:,.2f}"))
            self.spare_parts_table.setItem(row, 3, QTableWidgetItem(str(len(data['jobs']))))
            self.spare_parts_table.setItem(row, 4, QTableWidgetItem(", ".join(sorted(data['vehicles'])[:3])))
        
        self.spare_parts_table.resizeColumnsToContents()
        header = self.spare_parts_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
    
    def _update_vehicle_tab(self, job_cards):
        """Analyze vehicle service history"""
        vehicle_stats = defaultdict(lambda: {
            "jobs": 0, "spare_cost": 0, "labour_cost": 0, 
            "outsource_cost": 0, "make": "", "model": ""
        })
        
        for jc in job_cards:
            if not jc[3]:  # vehicle_no
                continue
            
            vehicle = jc[3]
            vehicle_stats[vehicle]["jobs"] += 1
            vehicle_stats[vehicle]["make"] = jc[5] or "N/A"
            vehicle_stats[vehicle]["model"] = jc[6] or "N/A"
            vehicle_stats[vehicle]["spare_cost"] += self._get_spare_cost(jc[13])
            vehicle_stats[vehicle]["labour_cost"] += self._get_labour_cost(jc[14])
            vehicle_stats[vehicle]["outsource_cost"] += self._get_outsource_cost(jc[15])
        
        # Sort by total cost descending
        sorted_vehicles = sorted(
            vehicle_stats.items(), 
            key=lambda x: x[1]["spare_cost"] + x[1]["labour_cost"] + x[1]["outsource_cost"],
            reverse=True
        )
        
        headers = ["Vehicle No", "Make", "Model", "Job Count", "Spare Cost", "Labour Cost", "Outsource Cost", "Total Cost"]
        self.vehicle_table.setColumnCount(8)
        self.vehicle_table.setHorizontalHeaderLabels(headers)
        self.vehicle_table.setRowCount(len(sorted_vehicles))
        
        for row, (vehicle, data) in enumerate(sorted_vehicles):
            total_cost = data["spare_cost"] + data["labour_cost"] + data["outsource_cost"]
            
            self.vehicle_table.setItem(row, 0, QTableWidgetItem(vehicle))
            self.vehicle_table.setItem(row, 1, QTableWidgetItem(data["make"]))
            self.vehicle_table.setItem(row, 2, QTableWidgetItem(data["model"]))
            self.vehicle_table.setItem(row, 3, QTableWidgetItem(str(data["jobs"])))
            self.vehicle_table.setItem(row, 4, QTableWidgetItem(f"Rs. {data['spare_cost']:,.2f}"))
            self.vehicle_table.setItem(row, 5, QTableWidgetItem(f"Rs. {data['labour_cost']:,.2f}"))
            self.vehicle_table.setItem(row, 6, QTableWidgetItem(f"Rs. {data['outsource_cost']:,.2f}"))
            
            total_item = QTableWidgetItem(f"Rs. {total_cost:,.2f}")
            total_item.setFont(QFont("Arial", 10, QFont.Bold))
            self.vehicle_table.setItem(row, 7, total_item)
        
        self.vehicle_table.resizeColumnsToContents()
    
    def _update_cost_tab(self, job_cards):
        """Analyze cost breakdown by category"""
        # Cost by site
        site_costs = defaultdict(lambda: {"spare": 0, "labour": 0, "outsource": 0, "jobs": 0})
        
        for jc in job_cards:
            site = jc[8] or "Unassigned"
            site_costs[site]["jobs"] += 1
            site_costs[site]["spare"] += self._get_spare_cost(jc[13])
            site_costs[site]["labour"] += self._get_labour_cost(jc[14])
            site_costs[site]["outsource"] += self._get_outsource_cost(jc[15])
        
        sorted_sites = sorted(
            site_costs.items(),
            key=lambda x: x[1]["spare"] + x[1]["labour"] + x[1]["outsource"],
            reverse=True
        )
        
        headers = ["Site", "Jobs", "Spare Parts", "Labour", "Outsource", "Total Cost", "Avg per Job"]
        self.cost_table.setColumnCount(7)
        self.cost_table.setHorizontalHeaderLabels(headers)
        self.cost_table.setRowCount(len(sorted_sites))
        
        for row, (site, data) in enumerate(sorted_sites):
            total = data["spare"] + data["labour"] + data["outsource"]
            avg = total / data["jobs"] if data["jobs"] > 0 else 0
            
            self.cost_table.setItem(row, 0, QTableWidgetItem(site))
            self.cost_table.setItem(row, 1, QTableWidgetItem(str(data["jobs"])))
            self.cost_table.setItem(row, 2, QTableWidgetItem(f"Rs. {data['spare']:,.2f}"))
            self.cost_table.setItem(row, 3, QTableWidgetItem(f"Rs. {data['labour']:,.2f}"))
            self.cost_table.setItem(row, 4, QTableWidgetItem(f"Rs. {data['outsource']:,.2f}"))
            
            total_item = QTableWidgetItem(f"Rs. {total:,.2f}")
            total_item.setFont(QFont("Arial", 10, QFont.Bold))
            self.cost_table.setItem(row, 5, total_item)
            
            self.cost_table.setItem(row, 6, QTableWidgetItem(f"Rs. {avg:,.2f}"))
        
        self.cost_table.resizeColumnsToContents()
        header = self.cost_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
    
    def _update_performance_tab(self, job_cards):
        """Calculate performance metrics"""
        # Driver performance
        driver_stats = defaultdict(lambda: {"jobs": 0, "completed": 0, "total_cost": 0})
        
        for jc in job_cards:
            driver = jc[4] or "Unassigned"
            driver_stats[driver]["jobs"] += 1
            if jc[16] == "Completed":
                driver_stats[driver]["completed"] += 1
            
            driver_stats[driver]["total_cost"] += (
                self._get_spare_cost(jc[13]) +
                self._get_labour_cost(jc[14]) +
                self._get_outsource_cost(jc[15])
            )
        
        sorted_drivers = sorted(driver_stats.items(), key=lambda x: x[1]["jobs"], reverse=True)
        
        headers = ["Driver", "Total Jobs", "Completed", "Completion Rate", "Total Cost", "Avg Cost/Job"]
        self.performance_table.setColumnCount(6)
        self.performance_table.setHorizontalHeaderLabels(headers)
        self.performance_table.setRowCount(len(sorted_drivers))
        
        for row, (driver, data) in enumerate(sorted_drivers):
            completion_rate = (data["completed"] / data["jobs"] * 100) if data["jobs"] > 0 else 0
            avg_cost = data["total_cost"] / data["jobs"] if data["jobs"] > 0 else 0
            
            self.performance_table.setItem(row, 0, QTableWidgetItem(driver))
            self.performance_table.setItem(row, 1, QTableWidgetItem(str(data["jobs"])))
            self.performance_table.setItem(row, 2, QTableWidgetItem(str(data["completed"])))
            self.performance_table.setItem(row, 3, QTableWidgetItem(f"{completion_rate:.1f}%"))
            self.performance_table.setItem(row, 4, QTableWidgetItem(f"Rs. {data['total_cost']:,.2f}"))
            self.performance_table.setItem(row, 5, QTableWidgetItem(f"Rs. {avg_cost:,.2f}"))
        
        self.performance_table.resizeColumnsToContents()
        header = self.performance_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
    
    def _get_spare_cost(self, spare_json):
        """Extract total spare parts cost from JSON"""
        try:
            parts = json.loads(spare_json) if spare_json else []
            return sum(float(p.get('total', 0)) for p in parts)
        except:
            return 0.0
    
    def _get_labour_cost(self, labour_json):
        """Extract total labour cost from JSON"""
        try:
            works = json.loads(labour_json) if labour_json else []
            return sum(float(w.get('work_cost', 0)) for w in works)
        except:
            return 0.0
    
    def _get_outsource_cost(self, outsource_json):
        """Extract total outsource cost from JSON"""
        try:
            works = json.loads(outsource_json) if outsource_json else []
            return sum(float(w.get('cost', 0)) for w in works)
        except:
            return 0.0
    
    def export_csv(self):
        """Export current tab data to CSV"""
        current_index = self.tabs.currentIndex()
        tables = [
            self.overview_table, self.spare_parts_table, 
            self.vehicle_table, self.cost_table, self.performance_table
        ]
        tab_names = ["Overview", "Spare_Parts", "Vehicle_Analysis", "Cost_Analysis", "Performance"]
        
        table = tables[current_index]
        tab_name = tab_names[current_index]
        
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Export to CSV",
            f"Report_{tab_name}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            "CSV Files (*.csv)"
        )
        
        if not filename:
            return
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # Write headers
                headers = [table.horizontalHeaderItem(i).text() for i in range(table.columnCount())]
                writer.writerow(headers)
                
                # Write data
                for row in range(table.rowCount()):
                    row_data = []
                    for col in range(table.columnCount()):
                        item = table.item(row, col)
                        row_data.append(item.text() if item else "")
                    writer.writerow(row_data)
            
            QMessageBox.information(self, "Success", f"Report exported successfully to:\n{filename}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export CSV:\n{str(e)}")
    
    def export_xlsx(self):
        """Export current tab data to Excel"""
        if not HAS_OPENPYXL:
            QMessageBox.warning(self, "Not Available", "Excel export requires openpyxl library.\nInstall with: pip install openpyxl")
            return
        
        current_index = self.tabs.currentIndex()
        tables = [
            self.overview_table, self.spare_parts_table,
            self.vehicle_table, self.cost_table, self.performance_table
        ]
        tab_names = ["Overview", "Spare_Parts", "Vehicle_Analysis", "Cost_Analysis", "Performance"]
        
        table = tables[current_index]
        tab_name = tab_names[current_index]
        
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Export to Excel",
            f"Report_{tab_name}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            "Excel Files (*.xlsx)"
        )
        
        if not filename:
            return
        
        try:
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = tab_name
            
            # Styling
            header_fill = PatternFill(start_color="2E7D6E", end_color="2E7D6E", fill_type="solid")
            header_font = XLFont(color="FFFFFF", bold=True)
            border = Border(
                left=Side(style='thin'),
                right=Side(style='thin'),
                top=Side(style='thin'),
                bottom=Side(style='thin')
            )
            
            # Write headers
            for col in range(table.columnCount()):
                cell = ws.cell(row=1, column=col+1)
                cell.value = table.horizontalHeaderItem(col).text()
                cell.fill = header_fill
                cell.font = header_font
                cell.border = border
                cell.alignment = Alignment(horizontal='center', vertical='center')
            
            # Write data
            for row in range(table.rowCount()):
                for col in range(table.columnCount()):
                    item = table.item(row, col)
                    cell = ws.cell(row=row+2, column=col+1)
                    cell.value = item.text() if item else ""
                    cell.border = border
                    
                    # Right-align numbers
                    if item and ("Rs." in item.text() or "%" in item.text() or item.text().replace(".", "").replace(",", "").isdigit()):
                        cell.alignment = Alignment(horizontal='right')
            
            # Auto-fit columns
            for column in ws.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    if cell.value:
                        max_length = max(max_length, len(str(cell.value)))
                ws.column_dimensions[column_letter].width = min(max_length + 2, 50)
            
            wb.save(filename)
            QMessageBox.information(self, "Success", f"Report exported successfully to:\n{filename}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export Excel:\n{str(e)}")
    
    def export_pdf(self):
        """Export current tab data to PDF"""
        if not HAS_REPORTLAB:
            QMessageBox.warning(self, "Not Available", "PDF export requires reportlab library.\nInstall with: pip install reportlab")
            return
        
        current_index = self.tabs.currentIndex()
        tables = [
            self.overview_table, self.spare_parts_table,
            self.vehicle_table, self.cost_table, self.performance_table
        ]
        tab_names = ["Overview", "Spare Parts Analysis", "Vehicle Analysis", "Cost Analysis", "Performance Metrics"]
        
        table = tables[current_index]
        tab_name = tab_names[current_index]
        
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Export to PDF",
            f"Report_{tab_name.replace(' ', '_')}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            "PDF Files (*.pdf)"
        )
        
        if not filename:
            return
        
        try:
            doc = SimpleDocTemplate(filename, pagesize=A4, topMargin=0.75*inch, bottomMargin=0.75*inch)
            story = []
            styles = getSampleStyleSheet()
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=18,
                textColor=colors.HexColor("#2E7D6E"),
                spaceAfter=12,
                alignment=TA_CENTER
            )
            story.append(Paragraph(f"Analytics Report: {tab_name}", title_style))
            story.append(Paragraph(
                f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 
                styles['Normal']
            ))
            story.append(Spacer(1, 0.3*inch))
            
            # Table data
            data = []
            headers = [table.horizontalHeaderItem(i).text() for i in range(table.columnCount())]
            data.append(headers)
            
            for row in range(table.rowCount()):
                row_data = []
                for col in range(table.columnCount()):
                    item = table.item(row, col)
                    row_data.append(item.text() if item else "")
                data.append(row_data)
            
            # Create PDF table
            pdf_table = Table(data)
            pdf_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#2E7D6E")),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F9FAFB")]),
            ]))
            
            story.append(pdf_table)
            
            # Build PDF
            doc.build(story)
            QMessageBox.information(self, "Success", f"Report exported successfully to:\n{filename}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export PDF:\n{str(e)}")
    
    def go_back(self):
        """Navigate back to home page"""
        if self.parent:
            self.parent.go_to_home()
