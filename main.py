import sys
import sqlite3
import os
from PySide6.QtWidgets import QApplication, QStackedWidget, QMessageBox
from PySide6.QtCore import Qt
from ui.pages.login_page import LoginPage
from ui.pages.home_page import HomePage
from ui.pages.job_card_page import JobCardPage
from ui.pages.data_manager_page import DataManagerPage
from ui.pages.jobcard_records_page import JobCardRecordsPage

DB_PATH = "ui/db/senarath.db"


def setup_database():
    """Initialize database and create tables if they don't exist"""
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Vehicles table
    c.execute('''CREATE TABLE IF NOT EXISTS vehicles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_no TEXT NOT NULL,
        number TEXT,
        make TEXT,
        model TEXT,
        type TEXT
    )''')
    
    # Drivers table
    c.execute('''CREATE TABLE IF NOT EXISTS drivers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL
    )''')
    
    # Sites table
    c.execute('''CREATE TABLE IF NOT EXISTS sites (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL
    )''')
    
    # Sections table
    c.execute('''CREATE TABLE IF NOT EXISTS sections (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL
    )''')
    
    # Job Cards table
    c.execute('''CREATE TABLE IF NOT EXISTS job_cards (
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
    )''')
    
    # Insert sample data if tables are empty
    c.execute("SELECT COUNT(*) FROM vehicles")
    if c.fetchone()[0] == 0:
        sample_vehicles = [
            ('CP-001', 'KA-1234', 'Toyota', 'Hilux', 'Double Cab'),
            ('CP-001', 'KA-5678', 'Toyota', 'Land Cruiser', 'SUV'),
            ('CP-002', 'KA-9012', 'Isuzu', 'D-Max', 'Single Cab'),
            ('CP-003', 'KA-3456', 'Mitsubishi', 'L200', 'Double Cab'),
        ]
        c.executemany("INSERT INTO vehicles (company_no, number, make, model, type) VALUES (?, ?, ?, ?, ?)", 
                     sample_vehicles)
    
    c.execute("SELECT COUNT(*) FROM drivers")
    if c.fetchone()[0] == 0:
        sample_drivers = [
            ('John Silva',),
            ('Kasun Perera',),
            ('Nimal Fernando',),
            ('Sunil Jayawardena',),
        ]
        c.executemany("INSERT INTO drivers (name) VALUES (?)", sample_drivers)
    
    c.execute("SELECT COUNT(*) FROM sites")
    if c.fetchone()[0] == 0:
        sample_sites = [
            ('Main Workshop',),
            ('Site A - Colombo',),
            ('Site B - Gampaha',),
            ('Site C - Kandy',),
        ]
        c.executemany("INSERT INTO sites (name) VALUES (?)", sample_sites)
    
    c.execute("SELECT COUNT(*) FROM sections")
    if c.fetchone()[0] == 0:
        sample_sections = [
            ('Mechanical',),
            ('Electrical',),
            ('Body Work',),
            ('Tire & Battery',),
            ('Engine Repair',),
        ]
        c.executemany("INSERT INTO sections (name) VALUES (?)", sample_sections)
    
    conn.commit()
    conn.close()
    print("✅ Database initialized successfully!")


class MainWindow(QStackedWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Senarath Workshop System")
        self.setMinimumSize(1280, 800)
        
        # Set application style
        self.setStyleSheet("""
            QStackedWidget {
                background-color: #f0f2f5;
            }
        """)
        
        # Initialize all pages
        self.login_page = LoginPage(self)
        self.home_page = HomePage(self)
        self.jobcard_page = JobCardPage(self)
        self.data_manager_page = DataManagerPage(self)
        self.jobcard_records_page = JobCardRecordsPage(self)
        
        # Add them to stacked widget
        self.addWidget(self.login_page)          # Index 0
        self.addWidget(self.home_page)           # Index 1
        self.addWidget(self.jobcard_page)        # Index 2
        self.addWidget(self.data_manager_page)   # Index 3
        self.addWidget(self.jobcard_records_page) # Index 4
        
        # Start with login page
        self.setCurrentWidget(self.login_page)
    
    # ==========================================
    # Navigation methods
    # ==========================================
    
    def go_to_home(self):
        """Navigate to home page"""
        self.setCurrentWidget(self.home_page)
    
    def go_to_jobcard(self):
        """Navigate to job card entry page"""
        self.jobcard_page.refresh_dropdowns()
        self.setCurrentWidget(self.jobcard_page)
    
    def go_to_data_manager(self):
        """Navigate to data manager page"""
        self.data_manager_page.refresh_all()
        self.setCurrentWidget(self.data_manager_page)
    
    def go_to_records(self):
        """Navigate to job card records page"""
        self.jobcard_records_page.load_records()
        self.setCurrentWidget(self.jobcard_records_page)
    
    def go_to_running_chart(self):
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
    
    def go_to_backup(self):
        """Navigate to backup page (placeholder)"""
        QMessageBox.information(
            self,
            "Coming Soon 💾",
            "Backup & Restore module is under development.\n\n"
            "This feature will allow you to:\n"
            "• Create database backups\n"
            "• Restore from previous backups\n"
            "• Schedule automatic backups\n"
            "• Export data to CSV/Excel\n\n"
            "Stay tuned for the next update!"
        )


def main():
    """Main application entry point"""
    # Create application
    app = QApplication(sys.argv)
    
    # Set application-wide settings
    app.setApplicationName("Senarath Workshop System")
    app.setOrganizationName("Senarath Group")
    
    # Setup database
    try:
        setup_database()
    except Exception as e:
        QMessageBox.critical(
            None,
            "Database Error",
            f"Failed to initialize database:\n{str(e)}"
        )
        sys.exit(1)
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Run application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()