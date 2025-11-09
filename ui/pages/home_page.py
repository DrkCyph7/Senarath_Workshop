import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QGridLayout, QMessageBox
)
from PySide6.QtCore import Qt, QTimer, QDateTime
from PySide6.QtGui import QFont, QPixmap


class HomePage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        # === Fixed UI Colors ===
        bg_color = "#ffffff"
        card_color = "#ffffff"
        accent_color = "#2d7a5f"
        text_color = "#2c2c2c"
        border_color = "#e0e0e0"
        secondary_color = "#8b6f47"

        self.setStyleSheet(f"""
            QWidget {{
                background-color: {bg_color};
                color: {text_color};
                font-family: 'Segoe UI', Arial, sans-serif;
            }}
            QLabel#system_title {{
                font-size: 26px;
                font-weight: 700;
                color: #1a1a1a;
            }}
            QLabel#datetime {{
                font-size: 15px;
                color: #555555;
                font-weight: 600;
                line-height: 1.5;
            }}
            QFrame#header_card {{
                background-color: {card_color};
                border-radius: 12px;
                padding: 28px 32px;
                border: 1px solid {border_color};
            }}
            QFrame#dashboard_card {{
                background-color: {card_color};
                border-radius: 12px;
                padding: 32px;
                border: 1px solid {border_color};
            }}
            QLabel#section_title {{
                font-size: 20px;
                font-weight: 700;
                color: #1a1a1a;
                padding-bottom: 24px;
            }}
            QPushButton#tile_primary {{
                background-color: {accent_color};
                color: white;
                font-size: 15px;
                font-weight: 600;
                padding: 0px;
                border-radius: 10px;
                border: none;
            }}
            QPushButton#tile_primary:hover {{
                background-color: #246651;
            }}
            QPushButton#tile_secondary {{
                background-color: {secondary_color};
                color: white;
                font-size: 15px;
                font-weight: 600;
                padding: 0px;
                border-radius: 10px;
                border: none;
            }}
            QPushButton#tile_secondary:hover {{
                background-color: #735a38;
            }}
            QPushButton#tile_disabled {{
                background-color: #f5f5f5;
                color: #999999;
                font-size: 15px;
                font-weight: 600;
                padding: 0px;
                border-radius: 10px;
                border: 1px solid {border_color};
            }}
            QPushButton#logout_btn {{
                background-color: #c84343;
                color: white;
                font-weight: 600;
                padding: 11px 24px;
                border-radius: 8px;
                font-size: 13px;
                border: none;
            }}
            QPushButton#logout_btn:hover {{
                background-color: #b03636;
            }}
            QLabel#footer_text {{
                color: #2d7a5f;
                font-size: 14px;
                font-weight: 600;
                background: transparent;
                text-decoration: none;
            }}
            QLabel#footer_text:hover {{
                color: #246651;
                text-decoration: underline;
            }}
        """)

        # Main layout
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 32, 40, 32)
        layout.setSpacing(24)

        # === Header Card ===
        header_card = QFrame()
        header_card.setObjectName("header_card")
        header_layout = QHBoxLayout(header_card)
        header_layout.setSpacing(24)

        # Logo - Bigger size for 495x150 resolution
        logo_label = QLabel()
        logo_path = "assets/logo.png"
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            # Scale to 198x60 (40% of original, maintains aspect ratio)
            pixmap = pixmap.scaled(198, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(pixmap)
            logo_label.setFixedSize(198, 60)
        else:
            logo_label.setText("🏭")
            logo_label.setStyleSheet("font-size: 52px;")
            logo_label.setFixedSize(198, 60)
        header_layout.addWidget(logo_label)
        
        # System Title
        title_layout = QVBoxLayout()
        title_layout.setSpacing(4)
        
        system_title = QLabel("Workshop Management System")
        system_title.setObjectName("system_title")
        title_layout.addWidget(system_title)
        
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        
        # Date & Time - Bigger font
        self.datetime_label = QLabel()
        self.datetime_label.setObjectName("datetime")
        self.datetime_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        header_layout.addWidget(self.datetime_label)
        
        self.update_datetime()
        timer = QTimer(self)
        timer.timeout.connect(self.update_datetime)
        timer.start(1000)
        
        layout.addWidget(header_card)

        # === Dashboard Card ===
        dashboard_card = QFrame()
        dashboard_card.setObjectName("dashboard_card")
        dashboard_layout = QVBoxLayout(dashboard_card)
        dashboard_layout.setSpacing(0)
        
        section_title = QLabel("Quick Access")
        section_title.setObjectName("section_title")
        dashboard_layout.addWidget(section_title)
        
        # Grid for tiles
        grid = QGridLayout()
        grid.setSpacing(16)
        grid.setContentsMargins(0, 0, 0, 0)

        # Row 1 - New Job Card
        jobcard_btn = QPushButton()
        jobcard_btn.setObjectName("tile_primary")
        jobcard_btn.setFixedHeight(130)
        jobcard_btn.setCursor(Qt.PointingHandCursor)
        jobcard_btn.clicked.connect(self.main_window.go_to_jobcard)
        jobcard_layout = QVBoxLayout(jobcard_btn)
        jobcard_layout.setContentsMargins(20, 20, 20, 20)
        jobcard_layout.setSpacing(10)
        
        icon1 = QLabel("📝")
        icon1.setStyleSheet("font-size: 40px; color: white; background: transparent;")
        jobcard_layout.addWidget(icon1)
        
        title1 = QLabel("New Job Card")
        title1.setStyleSheet("font-size: 17px; font-weight: 700; color: white; background: transparent;")
        jobcard_layout.addWidget(title1)
        
        desc1 = QLabel("Create new job entry")
        desc1.setStyleSheet("font-size: 14px; font-weight: 500; color: white; background: transparent;")
        jobcard_layout.addWidget(desc1)
        
        jobcard_layout.addStretch()
        grid.addWidget(jobcard_btn, 0, 0)

        # Row 1 - Job Card Records
        records_btn = QPushButton()
        records_btn.setObjectName("tile_secondary")
        records_btn.setFixedHeight(130)
        records_btn.setCursor(Qt.PointingHandCursor)
        records_btn.clicked.connect(self.main_window.go_to_records)
        records_layout = QVBoxLayout(records_btn)
        records_layout.setContentsMargins(20, 20, 20, 20)
        records_layout.setSpacing(10)
        
        icon2 = QLabel("📋")
        icon2.setStyleSheet("font-size: 40px; color: white; background: transparent;")
        records_layout.addWidget(icon2)
        
        title2 = QLabel("Job Card Records")
        title2.setStyleSheet("font-size: 17px; font-weight: 700; color: white; background: transparent;")
        records_layout.addWidget(title2)
        
        desc2 = QLabel("View all job records")
        desc2.setStyleSheet("font-size: 14px; font-weight: 500; color: white; background: transparent;")
        records_layout.addWidget(desc2)
        
        records_layout.addStretch()
        grid.addWidget(records_btn, 0, 1)
        
        # Row 1 - Data Manager
        data_btn = QPushButton()
        data_btn.setObjectName("tile_primary")
        data_btn.setFixedHeight(130)
        data_btn.setCursor(Qt.PointingHandCursor)
        data_btn.clicked.connect(self.main_window.go_to_data_manager)
        data_layout = QVBoxLayout(data_btn)
        data_layout.setContentsMargins(20, 20, 20, 20)
        data_layout.setSpacing(10)
        
        icon3 = QLabel("🔧")
        icon3.setStyleSheet("font-size: 40px; color: white; background: transparent;")
        data_layout.addWidget(icon3)
        
        title3 = QLabel("Data Manager")
        title3.setStyleSheet("font-size: 17px; font-weight: 700; color: white; background: transparent;")
        data_layout.addWidget(title3)
        
        desc3 = QLabel("Manage system data")
        desc3.setStyleSheet("font-size: 14px; font-weight: 500; color: white; background: transparent;")
        data_layout.addWidget(desc3)
        
        data_layout.addStretch()
        grid.addWidget(data_btn, 0, 2)

        # Row 2 - Running Chart
        running_btn = QPushButton()
        running_btn.setObjectName("tile_secondary")
        running_btn.setFixedHeight(130)
        running_btn.setCursor(Qt.PointingHandCursor)
        running_btn.clicked.connect(self.main_window.go_to_running_chart)
        running_layout = QVBoxLayout(running_btn)
        running_layout.setContentsMargins(20, 20, 20, 20)
        running_layout.setSpacing(10)
        
        icon4 = QLabel("🚚")
        icon4.setStyleSheet("font-size: 40px; color: white; background: transparent;")
        running_layout.addWidget(icon4)
        
        title4 = QLabel("Running Chart")
        title4.setStyleSheet("font-size: 17px; font-weight: 700; color: white; background: transparent;")
        running_layout.addWidget(title4)
        
        desc4 = QLabel("Track vehicle status")
        desc4.setStyleSheet("font-size: 14px; font-weight: 500; color: white; background: transparent;")
        running_layout.addWidget(desc4)
        
        running_layout.addStretch()
        grid.addWidget(running_btn, 1, 0)
        
        # Row 2 - Backup & Restore
        backup_btn = QPushButton()
        backup_btn.setObjectName("tile_primary")
        backup_btn.setFixedHeight(130)
        backup_btn.setCursor(Qt.PointingHandCursor)
        backup_btn.clicked.connect(self.main_window.go_to_backup)
        backup_layout = QVBoxLayout(backup_btn)
        backup_layout.setContentsMargins(20, 20, 20, 20)
        backup_layout.setSpacing(10)
        
        icon5 = QLabel("💾")
        icon5.setStyleSheet("font-size: 40px; color: white; background: transparent;")
        backup_layout.addWidget(icon5)
        
        title5 = QLabel("Backup & Restore")
        title5.setStyleSheet("font-size: 17px; font-weight: 700; color: white; background: transparent;")
        backup_layout.addWidget(title5)
        
        desc5 = QLabel("Protect your data")
        desc5.setStyleSheet("font-size: 14px; font-weight: 500; color: white; background: transparent;")
        backup_layout.addWidget(desc5)
        
        backup_layout.addStretch()
        grid.addWidget(backup_btn, 1, 1)

        # Row 2 - Reports (Coming Soon)
        reports_btn = QPushButton()
        reports_btn.setObjectName("tile_disabled")
        reports_btn.setFixedHeight(130)
        reports_btn.setEnabled(False)
        reports_layout = QVBoxLayout(reports_btn)
        reports_layout.setContentsMargins(20, 20, 20, 20)
        reports_layout.setSpacing(10)
        
        icon6 = QLabel("📊")
        icon6.setStyleSheet("font-size: 40px; color: #999999; background: transparent;")
        reports_layout.addWidget(icon6)
        
        title6 = QLabel("Reports")
        title6.setStyleSheet("font-size: 17px; font-weight: 700; color: #999999; background: transparent;")
        reports_layout.addWidget(title6)
        
        desc6 = QLabel("Coming soon...")
        desc6.setStyleSheet("font-size: 14px; font-weight: 500; color: #999999; background: transparent;")
        reports_layout.addWidget(desc6)
        
        reports_layout.addStretch()
        grid.addWidget(reports_btn, 1, 2)

        dashboard_layout.addLayout(grid)
        layout.addWidget(dashboard_card)

        # === Footer ===
        footer_layout = QHBoxLayout()
        footer_layout.setContentsMargins(8, 28, 8, 0)
        
        developer_label = QLabel("Developed by DrkCyph7")
        developer_label.setObjectName("footer_text")
        footer_layout.addWidget(developer_label)
        
        footer_layout.addStretch()
        
        logout_btn = QPushButton("🚪 Logout")
        logout_btn.setObjectName("logout_btn")
        logout_btn.setCursor(Qt.PointingHandCursor)
        logout_btn.clicked.connect(self.logout)
        logout_btn.setFixedHeight(40)
        footer_layout.addWidget(logout_btn)
        
        layout.addLayout(footer_layout)
        layout.addStretch()
        self.setLayout(layout)

    def update_datetime(self):
        """Update live date and time"""
        current = QDateTime.currentDateTime()
        date_str = current.toString("dddd, MMMM d, yyyy")
        time_str = current.toString("hh:mm:ss AP")
        self.datetime_label.setText(f"{date_str}\n{time_str}")

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