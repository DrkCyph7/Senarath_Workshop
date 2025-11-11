import os
import sqlite3
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QGridLayout, QMessageBox, QScrollArea
)
from PySide6.QtCore import Qt, QTimer, QDateTime, QSize
from PySide6.QtGui import QFont, QPixmap, QColor, QIcon
from ui.theme import ColorPalette, Typography, Spacing, Styles


class StatCard(QFrame):
    """Custom stat card widget"""
    def __init__(self, title, value, icon, color):
        super().__init__()
        self.setObjectName("stat_card")
        self.color = color
        self.title_text = title
        self.icon_text = icon
        
        self.setStyleSheet(f"""
            QFrame#stat_card {{
                background-color: #ffffff;
                border-radius: 10px;
                padding: 20px;
                border: none;
            }}
            QFrame#stat_card:hover {{
                background-color: #f9f9f9;
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        # Icon and title row
        header_layout = QHBoxLayout()
        header_layout.setSpacing(8)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        self.icon_label = QLabel(icon)
        self.icon_label.setStyleSheet(f"font-size: 32px; color: {color}; background: transparent;")
        header_layout.addWidget(self.icon_label)
        
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("font-size: 15px; color: #555; font-weight: 500; background: transparent;")
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Value label
        self.value_label = QLabel(value)
        self.value_label.setStyleSheet(f"font-size: 32px; font-weight: 700; color: {color}; background: transparent;")
        layout.addWidget(self.value_label)
    
    def update_value(self, new_value):
        """Update the displayed value"""
        self.value_label.setText(str(new_value))


class ModernActionTile(QPushButton):
    """Modern action tile button with icon on left and text on right"""
    def __init__(self, icon_name, title, color, hover_color=None):
        super().__init__()
        self.setObjectName("action_tile")
        self.setMinimumHeight(80)
        self.setCursor(Qt.PointingHandCursor)
        
        if hover_color is None:
            hover_color = color
        
        self.setStyleSheet(f"""
            QPushButton#action_tile {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 12px;
                font-weight: 600;
                text-align: left;
                padding: 0px;
            }}
            QPushButton#action_tile:hover {{
                background-color: {hover_color};
            }}
            QPushButton#action_tile:pressed {{
                background-color: {color};
            }}
        """)
        
        # Map icon names to icon characters (using Unicode geometric shapes)
        icon_unicode_map = {
            "document-new": "📄",  # Document
            "folder-open": "📁",   # Folder
            "settings": "⚙",       # Settings gear
            "save": "💾",          # Floppy disk
            "chart": "📊",         # Bar chart
            "truck": "🚛"          # Truck
        }
        
        # Get icon character
        icon_char = icon_unicode_map.get(icon_name, "►")
        
        # Create main horizontal layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(16, 12, 20, 12)
        main_layout.setSpacing(16)
        
        # Icon area - colored square with icon
        icon_frame = QFrame()
        icon_frame.setFixedSize(56, 56)
        icon_frame.setStyleSheet(f"""
            QFrame {{
                background-color: rgba(255, 255, 255, 0.25);
                border-radius: 8px;
                border: 1px solid rgba(255, 255, 255, 0.15);
            }}
        """)
        icon_layout = QVBoxLayout(icon_frame)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        
        icon_label = QLabel(icon_char)
        icon_label.setStyleSheet("background: transparent; color: white; font-size: 28px; font-weight: bold;")
        icon_label.setAlignment(Qt.AlignCenter)
        icon_layout.addWidget(icon_label)
        
        main_layout.addWidget(icon_frame, 0, Qt.AlignLeft | Qt.AlignVCenter)
        
        # Text area
        text_label = QLabel(title)
        text_label.setStyleSheet("font-size: 15px; font-weight: 700; color: white; background: transparent;")
        text_label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        main_layout.addWidget(text_label, 1)
        
        # Arrow indicator
        arrow_label = QLabel("→")
        arrow_label.setStyleSheet("font-size: 18px; color: rgba(255, 255, 255, 0.6); background: transparent;")
        main_layout.addWidget(arrow_label, 0, Qt.AlignRight | Qt.AlignVCenter)


class HomePage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        
        # Database path
        self.db_path = "ui/db/senarath.db"

        # === Use unified theme ===
        self.bg_color = ColorPalette.BG_PRIMARY
        self.card_bg = ColorPalette.CARD_BG
        self.primary_color = ColorPalette.ACCENT_PRIMARY
        self.secondary_color = ColorPalette.ACCENT_SECONDARY
        self.accent_blue = ColorPalette.ACCENT_BLUE
        self.accent_green = ColorPalette.ACCENT_GREEN
        self.accent_orange = ColorPalette.ACCENT_ORANGE
        self.accent_red = ColorPalette.ACCENT_RED
        self.text_primary = ColorPalette.TEXT_PRIMARY
        self.text_secondary = ColorPalette.TEXT_SECONDARY
        self.border_color = "#d1d5db"

        self.setStyleSheet(f"""
            QWidget {{
                background-color: {self.bg_color};
                color: {self.text_primary};
                font-family: 'Segoe UI', 'Inter', Arial, sans-serif;
            }}
            QLabel {{
                background-color: transparent;
            }}
            QLabel#header_title {{
                font-size: 36px;
                font-weight: 800;
                color: {self.text_primary};
                letter-spacing: -0.5px;
            }}
            QLabel#header_subtitle {{
                font-size: 15px;
                color: {self.text_secondary};
                font-weight: 400;
            }}
            QLabel#section_title {{
                font-size: 20px;
                font-weight: 700;
                color: {self.text_primary};
                padding-bottom: 2px;
            }}
            QLabel#section_subtitle {{
                font-size: 13px;
                color: {self.text_secondary};
                font-weight: 400;
            }}
            QLabel#datetime {{
                font-size: 14px;
                color: {self.text_secondary};
                font-weight: 500;
            }}
            QFrame {{
                background-color: transparent;
                border: none;
            }}
            QFrame#header {{
                background-color: transparent;
                border: none;
                padding: 0px;
            }}
            QFrame#section_card {{
                background-color: {self.card_bg};
                border-radius: 14px;
                padding: 28px;
                border: none;
            }}
            QPushButton#logout_btn {{
                background-color: {self.accent_red};
                color: white;
                font-weight: 600;
                padding: 10px 20px;
                border-radius: 8px;
                font-size: 13px;
                border: none;
            }}
            QPushButton#logout_btn:hover {{
                background-color: #dc2626;
            }}
            QPushButton#logout_btn:pressed {{
                background-color: #b91c1c;
            }}
        """)

        # Main scroll area for responsive design
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # === Top Navigation Bar ===
        nav_frame = QFrame()
        nav_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {self.card_bg};
                border: none;
                padding: 16px 32px;
            }}
        """)
        nav_layout = QHBoxLayout(nav_frame)
        nav_layout.setContentsMargins(0, 0, 0, 0)
        nav_layout.setSpacing(16)

        # Logo
        logo_label = QLabel()
        logo_path = "assets/logo.png"
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            pixmap = pixmap.scaledToWidth(100, Qt.SmoothTransformation)
            logo_label.setPixmap(pixmap)
        else:
            logo_label.setText("🏭")
            logo_label.setStyleSheet("font-size: 32px;")
        nav_layout.addWidget(logo_label)

        # Title and subtitle
        header_layout = QVBoxLayout()
        header_layout.setSpacing(4)
        title = QLabel("Senarath WMS Dashboard")
        title.setObjectName("header_title")
        header_layout.addWidget(title)

        self.datetime_label = QLabel()
        self.datetime_label.setObjectName("header_subtitle")
        header_layout.addWidget(self.datetime_label)
        nav_layout.addLayout(header_layout)

        nav_layout.addStretch()

        # Logout button
        logout_btn = QPushButton("Logout")
        logout_btn.setObjectName("logout_btn")
        logout_btn.setCursor(Qt.PointingHandCursor)
        logout_btn.clicked.connect(self.logout)
        logout_btn.setFixedWidth(100)
        logout_btn.setFixedHeight(36)
        nav_layout.addWidget(logout_btn)

        main_layout.addWidget(nav_frame)

        # === Main Content ===
        content_frame = QFrame()
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(32, 32, 32, 32)
        content_layout.setSpacing(28)

        # === Statistics Section ===
        stats_title = QLabel("Quick Overview")
        stats_title.setObjectName("section_title")
        content_layout.addWidget(stats_title)

        stats_grid = QGridLayout()
        stats_grid.setSpacing(16)
        stats_grid.setContentsMargins(0, 0, 0, 0)

        # Get statistics from database
        total_vehicles, total_drivers, total_jobs = self.get_statistics()

        self.stat1 = StatCard("Total Vehicles", str(total_vehicles), "🚗", self.primary_color)
        self.stat2 = StatCard("Total Drivers", str(total_drivers), "👥", self.accent_blue)
        self.stat3 = StatCard("Total Jobs", str(total_jobs), "📋", self.accent_green)
        self.stat4 = StatCard("System Status", "Active", "✓", self.accent_green)

        stats_grid.addWidget(self.stat1, 0, 0)
        stats_grid.addWidget(self.stat2, 0, 1)
        stats_grid.addWidget(self.stat3, 0, 2)
        stats_grid.addWidget(self.stat4, 0, 3)

        content_layout.addLayout(stats_grid)

        # === Quick Actions Section ===
        actions_title = QLabel("Quick Actions")
        actions_title.setObjectName("section_title")
        content_layout.addWidget(actions_title)

        actions_grid = QGridLayout()
        actions_grid.setSpacing(16)
        actions_grid.setContentsMargins(0, 0, 0, 0)

        # Action tiles with horizontal layout - 2 columns
        action_new_job = ModernActionTile(
            "document-new", "New Job Card", self.primary_color
        )
        action_new_job.clicked.connect(self.main_window.go_to_jobcard)
        actions_grid.addWidget(action_new_job, 0, 0)

        action_records = ModernActionTile(
            "folder-open", "View Records", self.primary_color
        )
        action_records.clicked.connect(self.main_window.go_to_records)
        actions_grid.addWidget(action_records, 0, 1)

        action_data = ModernActionTile(
            "settings", "Data Manager", self.primary_color
        )
        action_data.clicked.connect(self.main_window.go_to_data_manager)
        actions_grid.addWidget(action_data, 1, 0)

        action_backup = ModernActionTile(
            "save", "Backup & Restore", self.primary_color
        )
        action_backup.clicked.connect(self.main_window.go_to_backup)
        actions_grid.addWidget(action_backup, 1, 1)

        action_chart = ModernActionTile(
            "chart", "Running Chart", self.primary_color
        )
        action_chart.clicked.connect(self.main_window.go_to_running_chart)
        actions_grid.addWidget(action_chart, 2, 0)

        action_reports = ModernActionTile(
            "truck", "Reports", self.primary_color
        )
        action_reports.clicked.connect(self.main_window.go_to_report)
        actions_grid.addWidget(action_reports, 2, 1)

        content_layout.addLayout(actions_grid)

        # Add stretch at bottom
        content_layout.addStretch()

        main_layout.addWidget(content_frame, 1)

        # === Footer ===
        footer_frame = QFrame()
        footer_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {self.card_bg};
                border: none;
                padding: 16px 32px;
            }}
        """)
        footer_layout = QHBoxLayout(footer_frame)
        footer_layout.setContentsMargins(0, 0, 0, 0)

        footer_text = QLabel("Senarath WMS • Developed by <a href='https://www.google.com/search?q=DrkCyph7' style='color: #2d7a5f; text-decoration: none;'>DrkCyph7</a> • <a href='https://nexcy.lk' style='color: #2d7a5f; text-decoration: none;'>NexCy Technologies</a>")
        footer_text.setOpenExternalLinks(True)
        footer_text.setStyleSheet(f"font-size: 13px; color: {self.text_secondary};")
        footer_layout.addWidget(footer_text)
        footer_layout.addStretch()

        version_text = QLabel("v1.0")
        version_text.setStyleSheet(f"font-size: 13px; color: {self.text_secondary}; font-weight: 500;")
        footer_layout.addWidget(version_text)

        main_layout.addWidget(footer_frame)

        self.setLayout(main_layout)

        # Start datetime and statistics update timer
        self.update_datetime()
        self.refresh_statistics()
        
        # Timer for datetime and statistics (update every 2 seconds for stats, every 1 second for datetime)
        timer = QTimer(self)
        timer.timeout.connect(self.update_datetime)
        timer.start(1000)
        
        # Timer for statistics (update every 3 seconds)
        stats_timer = QTimer(self)
        stats_timer.timeout.connect(self.refresh_statistics)
        stats_timer.start(3000)

    def get_statistics(self):
        """Fetch statistics from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()

            c.execute("SELECT COUNT(*) FROM vehicles")
            total_vehicles = c.fetchone()[0]

            c.execute("SELECT COUNT(*) FROM drivers")
            total_drivers = c.fetchone()[0]

            c.execute("SELECT COUNT(*) FROM job_cards")
            total_jobs = c.fetchone()[0]

            conn.close()
            return total_vehicles, total_drivers, total_jobs
        except Exception as e:
            print(f"Error fetching statistics: {e}")
            return 0, 0, 0

    def update_datetime(self):
        """Update live date and time"""
        current = QDateTime.currentDateTime()
        date_str = current.toString("dddd, MMMM d, yyyy • hh:mm:ss AP")
        self.datetime_label.setText(date_str)

    def refresh_statistics(self):
        """Refresh statistics from database in real-time"""
        total_vehicles, total_drivers, total_jobs = self.get_statistics()
        self.stat1.update_value(total_vehicles)
        self.stat2.update_value(total_drivers)
        self.stat3.update_value(total_jobs)

    def logout(self):
        """Handle logout with confirmation"""
        reply = QMessageBox.question(
            self,
            "Logout Confirmation",
            "Are you sure you want to logout?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.main_window.setCurrentIndex(0)