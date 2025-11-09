# Developer Guide

## 👨‍💻 Developer Information

### Primary Developer
- **Name**: DrkCyph7
- **Profile**: [Google Search](https://www.google.com/search?q=DrkCyph7)
- **Expertise**: Full-stack Python development, UI/UX design, Database architecture

### Organization
- **Company**: NexCy Technologies
- **Website**: [nexcy.lk](https://nexcy.lk)
- **Focus**: Enterprise solutions and workshop management systems

---

## 🏗️ Architecture Overview

### Application Structure

```
Senarath WMS
├── Core Application (main.py)
│   ├── MainWindow class
│   ├── Page Management
│   ├── Navigation System
│   └── Database Initialization
│
├── UI Layer (ui/)
│   ├── Theme System (theme.py)
│   │   ├── ColorPalette
│   │   ├── Typography
│   │   ├── Spacing
│   │   └── Styles
│   │
│   └── Pages (pages/)
│       ├── LoginPage
│       ├── HomePage
│       ├── JobCardPage
│       ├── DataManagerPage
│       ├── JobCardRecordsPage
│       ├── ReportPage
│       └── BackupRestorePage
│
├── Data Layer (ui/db/)
│   └── SQLite Database
│       ├── Vehicles
│       ├── Drivers
│       ├── Sites
│       ├── Sections
│       ├── Job Cards
│       └── Job Card Parts
│
└── Security Layer
    ├── AES-256 Encryption
    ├── SHA-256 Checksums
    └── PIN Authentication
```

---

## 🎨 Design System

### Color Palette Architecture

```python
class ColorPalette:
    # Primary Colors
    ACCENT_PRIMARY = "#2e7d6e"      # Teal (Main brand)
    ACCENT_SECONDARY = "#a0754f"    # Brown (Secondary)
    
    # Text Colors
    TEXT_PRIMARY = "#111827"        # Dark gray (Main text)
    TEXT_SECONDARY = "#4b5563"      # Medium gray
    TEXT_MUTED = "#6c757d"          # Light gray
    
    # Background Colors
    BG_PRIMARY = "#ffffff"          # White
    BG_SECONDARY = "#f0f2f5"        # Light gray
    
    # Accent Colors
    ACCENT_GREEN = "#059669"
    ACCENT_BLUE = "#2563eb"
    ACCENT_ORANGE = "#d97706"
    ACCENT_RED = "#dc2626"
    ACCENT_YELLOW = "#fef3c7"
    
    # Borders
    BORDER_COLOR = "#d1d5db"
    BORDER_LIGHT = "#dee2e6"
```

### Theme Application Pattern

```python
from ui.theme import ColorPalette, Typography, Spacing, Styles

# In any page:
self.setStyleSheet(f"""
    QLabel {{
        color: {ColorPalette.TEXT_PRIMARY};
        font-size: {Typography.SIZE_BODY}px;
    }}
    QFrame {{
        background-color: {ColorPalette.BG_PRIMARY};
        border: 1px solid {ColorPalette.BORDER_COLOR};
        border-radius: {Spacing.BORDER_RADIUS_LARGE}px;
    }}
""")
```

---

## 🔐 Security Implementation

### Encryption System

```python
from cryptography.fernet import Fernet
import hashlib

# Generate encryption key
encryption_key = Fernet.generate_key()
cipher = Fernet(encryption_key)

# Encrypt data
encrypted_data = cipher.encrypt(data)

# Decrypt data
decrypted_data = cipher.decrypt(encrypted_data)

# Verify integrity
checksum = hashlib.sha256(data).hexdigest()
```

### Backup Format

```json
{
  "metadata": {
    "name": "Backup 20251109_210000",
    "timestamp": "20251109_210000",
    "checksum": "sha256_hash",
    "db_name": "Senarath WMS DB",
    "created_by": "DrkCyph7",
    "organization": "NexCy Technologies"
  },
  "encryption_key": "key_string",
  "encrypted_db": "encrypted_content"
}
```

---

## 📊 Database Schema

### Entity Relationship Diagram

```
┌─────────────┐
│  Vehicles   │
│  ─────────  │
│ • id (PK)   │
│ • name      │
│ • model     │
│ • reg_no    │
└─────────────┘
      ▲
      │
      │ (1:N)
      │
┌─────────────────────┐
│   Job Cards         │
│ ───────────────────  │
│ • id (PK)           │
│ • job_no (UNIQUE)   │
│ • date              │
│ • vehicle_id (FK)   │◄────────┐
│ • driver_id (FK)    │◄────────┤
│ • site_id (FK)      │◄────────┤
│ • status            │         │
│ • created_at        │         │
└─────────────────────┘         │
      ▲                         │
      │                         │
      │ (1:N)          ┌─────────────┐
      │                │   Drivers   │
      │                │  ─────────  │
      │                │ • id (PK)   │
      │                │ • name      │
      │                │ • phone     │
      │                └─────────────┘
      │
┌──────────────────────┐
│ Job Card Parts       │          ┌─────────────┐
│ ──────────────────── │          │    Sites    │
│ • id (PK)            │          │  ─────────  │
│ • job_card_id (FK)   │         │ • id (PK)   │
│ • section_id (FK)    │◄────────┤ • name      │
│ • part_name          │          │ • location  │
│ • quantity           │          └─────────────┘
│ • description        │
└──────────────────────┘          ┌─────────────┐
                                  │  Sections   │
                                  │  ─────────  │
                                  │ • id (PK)   │
                                  │ • name      │
                                  │ • description
                                  └─────────────┘
```

---

## 🛠️ Development Workflow

### Adding a New Page

```python
# 1. Create new page file: ui/pages/new_page.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from ui.theme import ColorPalette, Typography, Spacing, create_page_header

class NewPage(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.init_ui()
    
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(Spacing.PADDING_LARGE, 
                                      Spacing.PADDING_LARGE,
                                      Spacing.PADDING_LARGE, 
                                      Spacing.PADDING_LARGE)
        main_layout.setSpacing(Spacing.MARGIN_LARGE)
        
        # Create header
        header_layout, title_label, back_btn = create_page_header("📄 New Page")
        back_btn.clicked.connect(self.go_back)
        main_layout.addLayout(header_layout)
        
        # Add content
        self.setLayout(main_layout)
    
    def go_back(self):
        if self.parent:
            self.parent.go_to_home()

# 2. Register in main.py
self.pages = [
    LoginPage(),
    HomePage(self),
    JobCardPage(self),
    DataManagerPage(self),
    JobCardRecordsPage(self),
    ReportPage(self),
    BackupRestorePage(self),
    NewPage(self)  # Add here
]

# 3. Add navigation method in MainWindow
def go_to_new_page(self):
    self.stacked_widget.setCurrentIndex(self.PAGE_NEW)
```

### Adding Database Table

```python
# In main.py setup_database()
CREATE_TABLES = """
    CREATE TABLE IF NOT EXISTS new_table (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
"""

# Usage
cur = conn.cursor()
cur.execute(CREATE_TABLES)
conn.commit()
```

---

## 🎯 Key Classes and Methods

### MainWindow (main.py)

```python
class MainWindow(QMainWindow):
    def __init__(self):
        # Initialize pages
        self.pages = [...]
        self.stacked_widget = QStackedWidget()
        
    def go_to_home(self):
        self.stacked_widget.setCurrentIndex(self.PAGE_HOME)
    
    def go_to_jobcard(self):
        self.stacked_widget.setCurrentIndex(self.PAGE_JOBCARD)
    
    def setup_database(self) -> bool:
        # Initialize SQLite database
        pass
```

### Theme System (ui/theme.py)

```python
class ColorPalette:
    # All color constants

class Typography:
    # Font sizes and weights

class Spacing:
    # Padding, margin, border radius

class Styles:
    @staticmethod
    def get_button_primary() -> str:
        # Return stylesheet for primary button
    
    @staticmethod
    def get_page_title() -> str:
        # Return stylesheet for page titles

def create_page_header(title_text: str):
    # Create consistent page header
    # Returns: (layout, title_label, back_button)
```

---

## 🔄 Data Flow

### Job Card Creation Flow

```
User Input (JobCardPage)
    │
    ├─ Validate Input
    │   └─ Check required fields
    │   └─ Validate data types
    │
    ├─ Store in Database
    │   ├─ Insert into job_cards table
    │   └─ Insert parts into job_card_parts
    │
    ├─ Display Status
    │   └─ Show success/error message
    │
    └─ Refresh UI
        └─ Update job list
```

### Backup & Restore Flow

```
Create Backup Request
    │
    ├─ Read Database File
    ├─ Calculate Checksum (SHA-256)
    ├─ Generate Encryption Key
    ├─ Encrypt Database (AES-256)
    ├─ Create Metadata
    ├─ Save Backup File
    └─ Show Confirmation

Restore Backup Request
    │
    ├─ Validate File Format
    ├─ Create Pre-Restore Backup
    ├─ Load Backup File
    ├─ Decrypt Database (AES-256)
    ├─ Verify Checksum (SHA-256)
    ├─ Restore Database
    ├─ Request Application Restart
    └─ Show Confirmation
```

---

## 📝 Code Style Guide

### Naming Conventions

```python
# Classes - PascalCase
class JobCardPage(QWidget):
    pass

# Functions/Methods - snake_case
def create_backup():
    pass

# Constants - UPPER_SNAKE_CASE
DB_PATH = "ui/db/senarath.db"
BACKUP_DIR = "backups"

# Private methods - _leading_underscore
def _get_font(size: int):
    pass
```

### Type Hints

```python
from typing import Optional, List, Dict

def fetch_job_cards(status: Optional[str] = None) -> List[Dict]:
    """Fetch job cards from database."""
    pass

def save_job_card(job_data: Dict) -> bool:
    """Save job card to database."""
    pass
```

### Documentation

```python
def create_backup(self) -> bool:
    """
    Create encrypted backup of database.
    
    Returns:
        bool: True if backup successful, False otherwise
    
    Raises:
        Exception: If encryption or file operations fail
    """
    pass
```

---

## 🧪 Testing

### Unit Testing Pattern

```python
import unittest
from ui.theme import ColorPalette

class TestColorPalette(unittest.TestCase):
    def test_accent_primary_color(self):
        self.assertEqual(ColorPalette.ACCENT_PRIMARY, "#2e7d6e")
    
    def test_text_colors_exist(self):
        self.assertIsNotNone(ColorPalette.TEXT_PRIMARY)
        self.assertIsNotNone(ColorPalette.TEXT_SECONDARY)

if __name__ == '__main__':
    unittest.main()
```

---

## 🚀 Performance Tips

1. **Database Queries**
   - Use indexes on frequently queried columns
   - Batch insert operations
   - Use connection pooling for large operations

2. **UI Rendering**
   - Lazy load data
   - Use QThread for long operations
   - Minimize stylesheet recalculations

3. **Memory Management**
   - Clean up resources in destructors
   - Use context managers for file operations
   - Monitor backup file sizes

---

## 📚 Additional Resources

### PySide6/Qt
- [Qt Documentation](https://doc.qt.io/)
- [PySide6 Official Docs](https://doc.qt.io/qtforpython/)

### Cryptography
- [Cryptography Package](https://cryptography.io/)
- [OWASP Encryption Guide](https://cheatsheetseries.owasp.org/)

### Python
- [Python Documentation](https://docs.python.org/3/)
- [PEP 8 Style Guide](https://www.python.org/dev/peps/pep-0008/)

---

## 🤝 Contributing Guidelines

1. **Fork Repository** - Create your own fork
2. **Create Branch** - `git checkout -b feature/YourFeature`
3. **Follow Style** - Adhere to code style guide
4. **Test Code** - Ensure functionality works
5. **Commit Changes** - Clear commit messages
6. **Push & PR** - Submit pull request with description

---

## 📞 Developer Contact

- **GitHub**: DrkCyph7
- **Company**: NexCy Technologies
- **Website**: [nexcy.lk](https://nexcy.lk)

---

**Version**: 1.0.0
**Last Updated**: November 2025
**Status**: Production Ready ✅
