import sqlite3
import os
import shutil
import json
import hashlib
from datetime import datetime
from pathlib import Path
from cryptography.fernet import Fernet
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QFileDialog, QMessageBox, QProgressBar, QScrollArea, QTabWidget
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from ui.theme import ColorPalette, Typography, Spacing, Styles, create_page_header

DB_PATH = "ui/db/senarath.db"
BACKUP_DIR = "backups"


class BackupCard(QFrame):
    """Reusable backup item card"""
    def __init__(self, name, size, date, parent=None):
        super().__init__(parent)
        self.setObjectName("backup_card")
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(12)
        
        # Icon and info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(4)
        
        name_label = QLabel(f"📦 {name}")
        name_label.setFont(self._get_font(13, 600))
        info_layout.addWidget(name_label)
        
        meta_text = f"{size} • {date}"
        meta_label = QLabel(meta_text)
        meta_label.setStyleSheet(f"color: {ColorPalette.TEXT_SECONDARY}; font-size: 12px;")
        info_layout.addWidget(meta_label)
        
        layout.addLayout(info_layout, 1)
    
    def _get_font(self, size, weight):
        font = QFont()
        font.setPointSize(size)
        if weight >= 700:
            font.setBold(True)
        return font


class BackupRestorePage(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        
        # Ensure backup directory exists
        Path(BACKUP_DIR).mkdir(exist_ok=True)
        
        self.apply_stylesheet()
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(Spacing.PADDING_LARGE, Spacing.PADDING_LARGE, 
                                       Spacing.PADDING_LARGE, Spacing.PADDING_LARGE)
        main_layout.setSpacing(Spacing.MARGIN_LARGE)
        
        # Header
        header_layout, title_label, back_btn = create_page_header("🔐 Backup & Restore")
        back_btn.clicked.connect(self.go_back)
        main_layout.addLayout(header_layout)
        
        # Tabs
        tabs = QTabWidget()
        tabs.setObjectName("main_tabs")
        
        backup_tab = self.create_backup_tab()
        restore_tab = self.create_restore_tab()
        
        tabs.addTab(backup_tab, "📦  Create Backup")
        tabs.addTab(restore_tab, "📥  Restore Backup")
        
        main_layout.addWidget(tabs, 1)
        
        # Footer
        footer_frame = QFrame()
        footer_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {ColorPalette.CARD_BG};
                border: none;
                padding: 16px 32px;
            }}
        """)
        footer_layout = QHBoxLayout(footer_frame)
        footer_layout.setContentsMargins(0, 0, 0, 0)

        footer_text = QLabel("Senarath WMS • Developed by <a href='https://www.google.com/search?q=DrkCyph7' style='color: {ColorPalette.ACCENT_PRIMARY}; text-decoration: none;'>DrkCyph7</a> • <a href='https://nexcy.lk' style='color: {ColorPalette.ACCENT_PRIMARY}; text-decoration: none;'>NexCy Technologies</a>")
        footer_text.setOpenExternalLinks(True)
        footer_text.setStyleSheet(f"font-size: 13px; color: {ColorPalette.TEXT_SECONDARY};")
        footer_layout.addWidget(footer_text)
        footer_layout.addStretch()

        version_text = QLabel("v1.0")
        version_text.setStyleSheet(f"font-size: 13px; color: {ColorPalette.TEXT_SECONDARY}; font-weight: 500;")
        footer_layout.addWidget(version_text)

        main_layout.addWidget(footer_frame)
    
    def apply_stylesheet(self):
        """Apply modern theme-consistent stylesheet"""
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {ColorPalette.BG_PRIMARY};
                color: {ColorPalette.TEXT_PRIMARY};
                font-family: {Typography.FONT_FAMILY_PRIMARY};
                font-size: 13px;
            }}
            
            QLabel {{
                background-color: transparent;
            }}
            
            QFrame#card {{
                background-color: {ColorPalette.BG_SECONDARY};
                border: 1px solid {ColorPalette.BORDER_LIGHT};
                border-radius: {Spacing.BORDER_RADIUS_LARGE}px;
                padding: 0px;
            }}
            
            QFrame#backup_card {{
                background-color: {ColorPalette.CARD_BG};
                border: 1px solid {ColorPalette.BORDER_COLOR};
                border-radius: {Spacing.BORDER_RADIUS_MEDIUM}px;
                margin-bottom: 6px;
            }}
            
            QFrame#backup_card:hover {{
                background-color: {ColorPalette.HOVER_BG};
                border: 1px solid {ColorPalette.ACCENT_PRIMARY};
            }}
            
            QFrame#action_card {{
                background-color: {ColorPalette.CARD_BG};
                border: 2px solid {ColorPalette.ACCENT_PRIMARY};
                border-radius: {Spacing.BORDER_RADIUS_LARGE}px;
                padding: 0px;
            }}
            
            QFrame#warning_card {{
                background-color: {ColorPalette.ACCENT_YELLOW};
                border: 1px solid #fcd34d;
                border-radius: {Spacing.BORDER_RADIUS_LARGE}px;
                padding: 0px;
            }}
            
            QLabel#card_title {{
                font-size: 16px;
                font-weight: 600;
                color: {ColorPalette.ACCENT_PRIMARY};
            }}
            
            QLabel#section_title {{
                font-size: 14px;
                font-weight: 600;
                color: {ColorPalette.TEXT_PRIMARY};
            }}
            
            QLabel#info_text {{
                font-size: 13px;
                color: {ColorPalette.TEXT_SECONDARY};
                line-height: 1.5;
            }}
            
            QLabel#warning_title {{
                font-size: 14px;
                font-weight: 600;
                color: #92400e;
            }}
            
            QPushButton {{
                border: none;
                border-radius: {Spacing.BORDER_RADIUS_MEDIUM}px;
                font-weight: 600;
                padding: 10px 16px;
                min-height: 38px;
                font-size: 13px;
            }}
            
            QPushButton#primary {{
                background-color: {ColorPalette.ACCENT_PRIMARY};
                color: white;
            }}
            
            QPushButton#primary:hover {{
                background-color: #1f5444;
            }}
            
            QPushButton#primary:pressed {{
                background-color: #1a4439;
            }}
            
            QPushButton#success {{
                background-color: {ColorPalette.ACCENT_GREEN};
                color: white;
            }}
            
            QPushButton#success:hover {{
                background-color: #047857;
            }}
            
            QPushButton#secondary {{
                background-color: {ColorPalette.BG_SECONDARY};
                color: {ColorPalette.TEXT_PRIMARY};
                border: 1px solid {ColorPalette.BORDER_COLOR};
            }}
            
            QPushButton#secondary:hover {{
                background-color: {ColorPalette.BORDER_COLOR};
                border: 1px solid {ColorPalette.ACCENT_PRIMARY};
            }}
            
            QPushButton#danger {{
                background-color: {ColorPalette.ACCENT_RED};
                color: white;
            }}
            
            QPushButton#danger:hover {{
                background-color: #b91c1c;
            }}
            
            QPushButton#link_btn {{
                color: {ColorPalette.ACCENT_PRIMARY};
                text-decoration: underline;
                padding: 0px;
            }}
            
            QPushButton#link_btn:hover {{
                color: #1f5444;
            }}
            
            QProgressBar {{
                background-color: {ColorPalette.BG_SECONDARY};
                border: none;
                border-radius: 4px;
                text-align: center;
                color: white;
                height: 22px;
                font-weight: 600;
            }}
            
            QProgressBar::chunk {{
                background-color: {ColorPalette.ACCENT_PRIMARY};
                border-radius: 3px;
            }}
            
            QTabWidget::pane {{
                border: 1px solid {ColorPalette.BORDER_LIGHT};
                border-radius: {Spacing.BORDER_RADIUS_MEDIUM}px;
            }}
            
            QTabBar::tab {{
                background-color: {ColorPalette.BG_SECONDARY};
                padding: 10px 20px;
                margin-right: 4px;
                border: none;
                font-weight: 500;
                color: {ColorPalette.TEXT_SECONDARY};
            }}
            
            QTabBar::tab:hover {{
                background-color: {ColorPalette.BORDER_COLOR};
            }}
            
            QTabBar::tab:selected {{
                background-color: {ColorPalette.ACCENT_PRIMARY};
                color: white;
            }}
        """)
    
    def create_backup_tab(self):
        """Create backup tab with modern design"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(Spacing.PADDING_MEDIUM, Spacing.PADDING_MEDIUM, 
                                 Spacing.PADDING_MEDIUM, Spacing.PADDING_MEDIUM)
        layout.setSpacing(Spacing.MARGIN_LARGE)
        
        # Description
        desc = QLabel("Create an encrypted backup of your database. Backups are secure and can be restored anytime.")
        desc.setObjectName("info_text")
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        # Action card
        action_card = QFrame()
        action_card.setObjectName("action_card")
        action_layout = QVBoxLayout(action_card)
        action_layout.setContentsMargins(Spacing.PADDING_LARGE, Spacing.PADDING_LARGE, 
                                        Spacing.PADDING_LARGE, Spacing.PADDING_LARGE)
        action_layout.setSpacing(Spacing.MARGIN_LARGE)
        
        action_title = QLabel("🚀 Ready to backup?")
        action_title.setObjectName("section_title")
        action_layout.addWidget(action_title)
        
        action_desc = QLabel("Click the button below to create a new encrypted backup of your database.")
        action_desc.setObjectName("info_text")
        action_desc.setWordWrap(True)
        action_layout.addWidget(action_desc)
        
        # Progress bar
        self.backup_progress = QProgressBar()
        self.backup_progress.setVisible(False)
        self.backup_progress.setMaximumHeight(20)
        action_layout.addWidget(self.backup_progress)
        
        # Status
        self.backup_status = QLabel("")
        self.backup_status.setObjectName("info_text")
        action_layout.addWidget(self.backup_status)
        
        # Buttons - side by side
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(Spacing.MARGIN_LARGE)
        
        backup_btn = QPushButton("💾  Create Backup Now")
        backup_btn.setObjectName("primary")
        backup_btn.setMinimumHeight(42)
        backup_btn.clicked.connect(self.create_backup)
        btn_layout.addWidget(backup_btn, 1)
        
        folder_btn = QPushButton("📂  Open Backups Folder")
        folder_btn.setObjectName("secondary")
        folder_btn.setMinimumHeight(42)
        folder_btn.clicked.connect(self.open_backup_folder)
        btn_layout.addWidget(folder_btn, 1)
        
        action_layout.addLayout(btn_layout)
        layout.addWidget(action_card)
        
        # Recent backups section
        backups_card = QFrame()
        backups_card.setObjectName("card")
        backups_layout = QVBoxLayout(backups_card)
        backups_layout.setContentsMargins(Spacing.PADDING_LARGE, Spacing.PADDING_LARGE, 
                                         Spacing.PADDING_LARGE, Spacing.PADDING_LARGE)
        backups_layout.setSpacing(Spacing.MARGIN_MEDIUM)
        
        backups_title = QLabel("📦  Recent Backups")
        backups_title.setObjectName("card_title")
        backups_layout.addWidget(backups_title)
        
        # Backup list with scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(6)
        
        self.backup_list_layout = scroll_layout
        scroll.setWidget(scroll_widget)
        
        backups_layout.addWidget(scroll)
        layout.addWidget(backups_card, 1)
        
        self.refresh_backup_list()
        return widget
    
    def create_restore_tab(self):
        """Create restore tab with modern design"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(Spacing.PADDING_MEDIUM, Spacing.PADDING_MEDIUM, 
                                 Spacing.PADDING_MEDIUM, Spacing.PADDING_MEDIUM)
        layout.setSpacing(Spacing.MARGIN_LARGE)
        
        # Warning section
        warning_card = QFrame()
        warning_card.setObjectName("warning_card")
        warning_layout = QVBoxLayout(warning_card)
        warning_layout.setContentsMargins(Spacing.PADDING_LARGE, Spacing.PADDING_LARGE, 
                                         Spacing.PADDING_LARGE, Spacing.PADDING_LARGE)
        warning_layout.setSpacing(Spacing.MARGIN_MEDIUM)
        
        warning_title = QLabel("⚠️  Important Notice")
        warning_title.setObjectName("warning_title")
        warning_layout.addWidget(warning_title)
        
        warning_text = QLabel(
            "Restoring a backup will replace your current data. "
            "A pre-restore backup will be created automatically for safety."
        )
        warning_text.setObjectName("info_text")
        warning_text.setWordWrap(True)
        warning_layout.addWidget(warning_text)
        
        layout.addWidget(warning_card)
        
        # Description
        desc = QLabel("Select a backup file to restore. Your current data will be backed up first.")
        desc.setObjectName("info_text")
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        # Available backups section
        backups_card = QFrame()
        backups_card.setObjectName("card")
        backups_layout = QVBoxLayout(backups_card)
        backups_layout.setContentsMargins(Spacing.PADDING_LARGE, Spacing.PADDING_LARGE, 
                                         Spacing.PADDING_LARGE, Spacing.PADDING_LARGE)
        backups_layout.setSpacing(Spacing.MARGIN_MEDIUM)
        
        backups_title = QLabel("📋  Available Backups")
        backups_title.setObjectName("card_title")
        backups_layout.addWidget(backups_title)
        
        # Backup list with scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(6)
        
        self.restore_list_layout = scroll_layout
        scroll.setWidget(scroll_widget)
        
        backups_layout.addWidget(scroll)
        layout.addWidget(backups_card, 1)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(Spacing.MARGIN_LARGE)
        
        choose_btn = QPushButton("📁  Choose File to Restore")
        choose_btn.setObjectName("primary")
        choose_btn.setMinimumHeight(42)
        choose_btn.clicked.connect(self.choose_and_restore_backup)
        btn_layout.addWidget(choose_btn, 1)
        
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)
        
        self.refresh_restore_list()
        return widget
    
    def refresh_backup_list(self):
        """Refresh the backup list display"""
        # Clear existing items
        while self.backup_list_layout.count():
            item = self.backup_list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        backup_files = sorted(
            [f for f in os.listdir(BACKUP_DIR) if f.endswith(".senarath.backup")],
            reverse=True
        )
        
        if not backup_files:
            no_backup = QLabel("No backups yet. Create one to get started!")
            no_backup.setStyleSheet(f"color: {ColorPalette.TEXT_MUTED}; font-style: italic;")
            self.backup_list_layout.addWidget(no_backup)
        else:
            for backup_file in backup_files:
                filepath = os.path.join(BACKUP_DIR, backup_file)
                size = os.path.getsize(filepath) / (1024 * 1024)
                timestamp = os.path.getmtime(filepath)
                date = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
                
                card = BackupCard(
                    backup_file.replace(".senarath.backup", ""),
                    f"{size:.2f} MB",
                    date
                )
                self.backup_list_layout.addWidget(card)
        
        self.backup_list_layout.addStretch()
    
    def refresh_restore_list(self):
        """Refresh the restore list display"""
        # Clear existing items
        while self.restore_list_layout.count():
            item = self.restore_list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        backup_files = sorted(
            [f for f in os.listdir(BACKUP_DIR) if f.endswith(".senarath.backup")],
            reverse=True
        )
        
        if not backup_files:
            no_backup = QLabel("No backups available. Create one first!")
            no_backup.setStyleSheet(f"color: {ColorPalette.TEXT_MUTED}; font-style: italic;")
            self.restore_list_layout.addWidget(no_backup)
        else:
            for backup_file in backup_files:
                filepath = os.path.join(BACKUP_DIR, backup_file)
                size = os.path.getsize(filepath) / (1024 * 1024)
                timestamp = os.path.getmtime(filepath)
                date = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
                
                card = BackupCard(
                    backup_file.replace(".senarath.backup", ""),
                    f"{size:.2f} MB",
                    date
                )
                self.restore_list_layout.addWidget(card)
        
        self.restore_list_layout.addStretch()
    
    def create_backup(self):
        """Create encrypted backup"""
        try:
            self.backup_progress.setVisible(True)
            self.backup_status.setText("⏳ Creating backup...")
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"backup_{timestamp}.senarath.backup"
            backup_path = os.path.join(BACKUP_DIR, backup_filename)
            
            # Generate encryption key
            encryption_key = Fernet.generate_key()
            cipher = Fernet(encryption_key)
            
            # Read database
            with open(DB_PATH, 'rb') as db_file:
                db_data = db_file.read()
            
            # Calculate checksum
            checksum = hashlib.sha256(db_data).hexdigest()
            
            # Encrypt database
            encrypted_db = cipher.encrypt(db_data)
            
            # Create backup metadata
            metadata = {
                "name": f"Backup {timestamp}",
                "timestamp": timestamp,
                "checksum": checksum,
                "db_name": "Senarath WMS DB",
                "created_by": "DrkCyph7",
                "organization": "NexCy Technologies"
            }
            
            # Save backup
            backup_data = {
                "metadata": metadata,
                "encryption_key": encryption_key.decode(),
                "encrypted_db": encrypted_db.decode('utf-8', errors='ignore')
            }
            
            with open(backup_path, 'w') as f:
                json.dump(backup_data, f)
            
            self.backup_progress.setValue(100)
            self.backup_status.setText("✅ Backup created successfully!")
            self.refresh_backup_list()
            
            QMessageBox.information(self, "Success", f"Backup created successfully!\n\n{backup_filename}")
            
        except Exception as e:
            self.backup_status.setText(f"❌ Error: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to create backup:\n{str(e)}")
        
        finally:
            self.backup_progress.setVisible(False)
    
    def open_backup_folder(self):
        """Open backup folder in file explorer"""
        try:
            os.system(f"open '{os.path.abspath(BACKUP_DIR)}'")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open folder:\n{str(e)}")
    
    def choose_and_restore_backup(self):
        """Choose and restore a backup"""
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Select Backup to Restore", BACKUP_DIR,
            "Backup Files (*.senarath.backup)"
        )
        
        if not filepath:
            return
        
        reply = QMessageBox.warning(
            self, "Confirm Restore",
            "This will replace your current database. A backup will be created first.\n\nContinue?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.No:
            return
        
        try:
            # Create pre-restore backup
            self.create_backup()
            
            # Load backup
            with open(filepath, 'r') as f:
                backup_data = json.load(f)
            
            # Decrypt
            cipher = Fernet(backup_data["encryption_key"].encode())
            encrypted_db = backup_data["encrypted_db"].encode('utf-8', errors='ignore')
            decrypted_db = cipher.decrypt(encrypted_db)
            
            # Verify checksum
            checksum = hashlib.sha256(decrypted_db).hexdigest()
            if checksum != backup_data["metadata"]["checksum"]:
                raise Exception("Backup corrupted - checksum mismatch")
            
            # Restore database
            with open(DB_PATH, 'wb') as f:
                f.write(decrypted_db)
            
            QMessageBox.information(self, "Success", "Database restored successfully!\n\nPlease restart the application.")
            self.refresh_restore_list()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to restore backup:\n{str(e)}")
    
    def go_back(self):
        """Go back to previous page"""
        if self.parent:
            self.parent.go_to_home()
