"""
Senarath WMS - Main Application Module
Manages application initialization, database setup, and page navigation
"""
import sys
import sqlite3
import os
import logging
from typing import Optional
from PySide6.QtWidgets import QApplication, QStackedWidget, QMessageBox
from PySide6.QtCore import Qt

# Import all pages
from ui.pages.login_page import LoginPage
from ui.pages.home_page import HomePage
from ui.pages.job_card_page import JobCardPage
from ui.pages.data_manager_page import DataManagerPage
from ui.pages.jobcard_records_page import JobCardRecordsPage
from ui.pages.report_page import ReportPage
from ui.pages.backup_restore_page import BackupRestorePage

# Configuration
DB_PATH = "ui/db/senarath.db"
APP_NAME = "Senarath WMS"
APP_VERSION = "1.0.0"
ORG_NAME = "Senarath Group"
MIN_WIDTH = 1280
MIN_HEIGHT = 800

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def setup_database() -> bool:
    """
    Initialize database and create tables if they don't exist.
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        # Define table creation SQL statements
        tables = {
            'vehicles': '''CREATE TABLE IF NOT EXISTS vehicles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_no TEXT NOT NULL,
                number TEXT,
                make TEXT,
                model TEXT,
                type TEXT
            )''',
            'drivers': '''CREATE TABLE IF NOT EXISTS drivers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL
            )''',
            'sites': '''CREATE TABLE IF NOT EXISTS sites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL
            )''',
            'sections': '''CREATE TABLE IF NOT EXISTS sections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL
            )''',
            'job_cards': '''CREATE TABLE IF NOT EXISTS job_cards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_no TEXT,
                company_no TEXT,
                vehicle_no TEXT,
                driver TEXT,
                make TEXT,
                model TEXT,
                type TEXT,
                site TEXT,
                section TEXT,
                hr_km TEXT,
                start_date TEXT,
                end_date TEXT,
                description TEXT,
                spare_parts TEXT
            )'''
        }
        
        # Create all tables
        for table_name, sql in tables.items():
            c.execute(sql)
        
        # Insert sample data if tables are empty
        _insert_sample_data(c)
        
        conn.commit()
        conn.close()
        logger.info("✅ Database initialized successfully!")
        return True
        
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during database setup: {e}")
        return False


def _insert_sample_data(cursor: sqlite3.Cursor) -> None:
    """
    Insert sample data into tables if they are empty.
    
    Args:
        cursor: SQLite cursor object
    """
    # Sample vehicles
    cursor.execute("SELECT COUNT(*) FROM vehicles")
    if cursor.fetchone()[0] == 0:
        sample_vehicles = [
            ('CP-001', 'KA-1234', 'Toyota', 'Hilux', 'Double Cab'),
            ('CP-001', 'KA-5678', 'Toyota', 'Land Cruiser', 'SUV'),
            ('CP-002', 'KA-9012', 'Isuzu', 'D-Max', 'Single Cab'),
            ('CP-003', 'KA-3456', 'Mitsubishi', 'L200', 'Double Cab'),
        ]
        cursor.executemany(
            "INSERT INTO vehicles (company_no, number, make, model, type) VALUES (?, ?, ?, ?, ?)",
            sample_vehicles
        )
    
    # Sample drivers
    cursor.execute("SELECT COUNT(*) FROM drivers")
    if cursor.fetchone()[0] == 0:
        sample_drivers = [
            ('John Silva',),
            ('Kasun Perera',),
            ('Nimal Fernando',),
            ('Sunil Jayawardena',),
        ]
        cursor.executemany("INSERT INTO drivers (name) VALUES (?)", sample_drivers)
    
    # Sample sites
    cursor.execute("SELECT COUNT(*) FROM sites")
    if cursor.fetchone()[0] == 0:
        sample_sites = [
            ('Main Workshop',),
            ('Site A - Colombo',),
            ('Site B - Gampaha',),
            ('Site C - Kandy',),
        ]
        cursor.executemany("INSERT INTO sites (name) VALUES (?)", sample_sites)
    
    # Sample sections
    cursor.execute("SELECT COUNT(*) FROM sections")
    if cursor.fetchone()[0] == 0:
        sample_sections = [
            ('Mechanical',),
            ('Electrical',),
            ('Body Work',),
            ('Tire & Battery',),
            ('Engine Repair',),
        ]
        cursor.executemany("INSERT INTO sections (name) VALUES (?)", sample_sections)


class MainWindow(QStackedWidget):
    """
    Main application window managing page navigation and application state.
    Uses QStackedWidget to manage multiple pages.
    """
    
    # Page indices as constants
    PAGE_LOGIN = 0
    PAGE_HOME = 1
    PAGE_JOBCARD = 2
    PAGE_DATA_MANAGER = 3
    PAGE_RECORDS = 4
    PAGE_REPORT = 5
    PAGE_BACKUP = 6
    
    def __init__(self):
        """Initialize main window and all pages"""
        super().__init__()
        self._setup_window()
        self._initialize_pages()
        self._show_login()
    
    def _setup_window(self) -> None:
        """Configure main window properties"""
        self.setWindowTitle(APP_NAME)
        self.setMinimumSize(MIN_WIDTH, MIN_HEIGHT)
        self.setStyleSheet("""
            QStackedWidget {
                background-color: #f0f2f5;
            }
        """)
        logger.info(f"Main window initialized: {APP_NAME} v{APP_VERSION}")
    
    def _initialize_pages(self) -> None:
        """Initialize all application pages"""
        try:
            self.login_page = LoginPage(self)
            self.home_page = HomePage(self)
            self.jobcard_page = JobCardPage(self)
            self.data_manager_page = DataManagerPage(self)
            self.jobcard_records_page = JobCardRecordsPage(self)
            self.report_page = ReportPage(self)
            self.backup_restore_page = BackupRestorePage(self)
            
            # Add pages to stacked widget
            self.addWidget(self.login_page)              # Index 0
            self.addWidget(self.home_page)               # Index 1
            self.addWidget(self.jobcard_page)            # Index 2
            self.addWidget(self.data_manager_page)       # Index 3
            self.addWidget(self.jobcard_records_page)    # Index 4
            self.addWidget(self.report_page)             # Index 5
            self.addWidget(self.backup_restore_page)     # Index 6
            
            logger.info("All pages initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing pages: {e}")
            raise
    
    def _show_login(self) -> None:
        """Show login page"""
        self.setCurrentIndex(self.PAGE_LOGIN)
    
    # ==========================================
    # Navigation Methods
    # ==========================================
    
    def go_to_home(self) -> None:
        """Navigate to home page"""
        self.setCurrentIndex(self.PAGE_HOME)
        logger.debug("Navigated to: Home")
    
    def go_to_jobcard(self) -> None:
        """Navigate to job card entry page"""
        self.jobcard_page.refresh_dropdowns()
        self.setCurrentIndex(self.PAGE_JOBCARD)
        logger.debug("Navigated to: Job Card")
    
    def go_to_data_manager(self) -> None:
        """Navigate to data manager page"""
        self.data_manager_page.refresh_all()
        self.setCurrentIndex(self.PAGE_DATA_MANAGER)
        logger.debug("Navigated to: Data Manager")
    
    def go_to_records(self) -> None:
        """Navigate to job card records page"""
        self.jobcard_records_page.load_records()
        self.setCurrentIndex(self.PAGE_RECORDS)
        logger.debug("Navigated to: Records")
    
    def go_to_running_chart(self) -> None:
        """Navigate to running chart page (placeholder)"""
        QMessageBox.information(
            self,
            "Coming Soon 🚚",
            "Running Chart module is under development.\n\n"
            "This feature will allow you to:\n"
            "• Track vehicle running schedules\n"
            "• Monitor mileage and usage\n"
            "• Manage vehicle assignments\n\n"
            "Stay tuned for the next update!"
        )
    
    def go_to_backup(self) -> None:
        """Navigate to backup/restore page"""
        self.setCurrentIndex(self.PAGE_BACKUP)
        logger.debug("Navigated to: Backup & Restore")
    
    def go_to_report(self) -> None:
        """Navigate to report page"""
        self.setCurrentIndex(self.PAGE_REPORT)
        logger.debug("Navigated to: Reports")


def main() -> int:
    """
    Main application entry point.
    
    Returns:
        int: Application exit code
    """
    # Create application
    app = QApplication(sys.argv)
    
    # Set application-wide settings
    app.setApplicationName(APP_NAME)
    app.setOrganizationName(ORG_NAME)
    app.setApplicationVersion(APP_VERSION)
    
    logger.info(f"Starting {APP_NAME} v{APP_VERSION}")
    
    # Setup database
    if not setup_database():
        logger.error("Failed to initialize database")
        QMessageBox.critical(
            None,
            "Database Error",
            f"Failed to initialize database.\n\n"
            f"Please check that the directory '{os.path.dirname(DB_PATH)}' is writable."
        )
        return 1
    
    try:
        # Create and show main window
        window = MainWindow()
        window.show()
        logger.info("Application window displayed")
        
        # Run application
        return app.exec()
        
    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        QMessageBox.critical(
            None,
            "Application Error",
            f"An unexpected error occurred:\n{str(e)}"
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())