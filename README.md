<div align="center">

<img src="https://img.shields.io/badge/Senarath%20WMS-v1.0.0-2e7d6e?style=for-the-badge&logo=gear&logoColor=white" alt="Senarath WMS">

# 🏢 Senarath WMS
## Professional Workshop Management System

<p>
  <a href="https://github.com/DrkCyph7/Senarath_Workshop">
    <img src="https://img.shields.io/github/stars/DrkCyph7/Senarath_Workshop?style=social" alt="GitHub Stars">
  </a>
  <img src="https://img.shields.io/badge/Python-3.13.3-3776ab?style=flat&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/PySide6-6.10.0-41cd52?style=flat&logo=qt" alt="PySide6">
  <img src="https://img.shields.io/badge/License-MIT-green?style=flat" alt="License">
</p>

> **Enterprise-Grade Workshop Management Solution**  
> *Real-time job tracking • Encrypted backups • Professional analytics*

**[⚡ Quick Start](#-quick-start)** • **[✨ Features](#-features)** • **[� Docs](#-documentation)** • **[� Deploy](#-deployment)** • **[👨‍💻 About](#-about)**

---

### 🎯 What is Senarath WMS?

A professional desktop application for managing workshop operations with real-time job card tracking, vehicle management, driver assignments, and encrypted data backups. Built with modern Python and enterprise-grade security.

**✅ Production Ready** • **🔐 Enterprise Security** • **🚀 Fast & Reliable** • **📊 Full Analytics**

</div>

---

## ⚡ Quick Start in 60 Seconds

<details open>
<summary><b>🖥️ For End Users (Pre-built Executable)</b></summary>

### macOS
```bash
# Download and run
./Senarath\ WMS.app
# or
./Senarath\ WMS
```

### Windows
```batch
# Simply double-click
Senarath WMS.exe
```

**Login PIN:** `2345`

</details>

<details>
<summary><b>👨‍💻 For Developers (From Source)</b></summary>

```bash
# Clone repository
git clone https://github.com/DrkCyph7/Senarath_Workshop.git
cd Senarath_Workshop

# Setup environment
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# OR
.venv\Scripts\activate     # Windows

# Install & run
pip install -r requirements.txt
python main.py
```

</details>

---

## ✨ Features

## ✨ Features

### Core Functionality

<table>
<tr>
<td width="50%">

**📋 Job Card Management**
- ✅ Auto-numbered job cards
- ✅ Real-time status tracking
- ✅ Multiple job items per card
- ✅ Spare parts inventory
- ✅ Cost calculations

</td>
<td width="50%">

**🗂️ Data Management**
- 🚗 Complete vehicle fleet
- 👤 Driver assignments
- 📍 Work sites catalog
- 🏷️ Work sections
- 🔄 CRUD operations

</td>
</tr>
<tr>
<td width="50%">

**📊 Analytics & Reporting**
- 📈 Job completion stats
- � Revenue tracking
- � Date range filters
- � Advanced search
- 📤 Export to CSV/PDF

</td>
<td width="50%">

**🔐 Security & Backup**
- 🔒 AES-256 encryption
- ✔️ SHA-256 verification
- 🔑 PIN authentication
- 💾 Auto-backup
- ⏮️ One-click restore

</td>
</tr>
</table>

### 🎨 User Experience
- ⚡ **Lightning Fast** - Instant response times
- 🎯 **Intuitive UI** - Professional design system
- 🔗 **Smart Linking** - Auto-fill vehicle & company data
- ✨ **Modern Animations** - Smooth transitions
- 🌈 **Beautiful Colors** - Teal & brown palette
- 📱 **Responsive** - Works on all screen sizes

---

## � Full Installation

### macOS & Linux

```bash
# 1️⃣ Clone repository
git clone https://github.com/DrkCyph7/Senarath_Workshop.git
cd Senarath_Workshop

# 2️⃣ Create virtual environment
python -m venv .venv
source .venv/bin/activate

# 3️⃣ Install dependencies
pip install -r requirements.txt

# 4️⃣ Run application
python main.py
```

### Windows

```batch
# 1️⃣ Clone repository
git clone https://github.com/DrkCyph7/Senarath_Workshop.git
cd Senarath_Workshop

# 2️⃣ Create virtual environment
python -m venv .venv
.venv\Scripts\activate

# 3️⃣ Install dependencies
pip install -r requirements.txt

# 4️⃣ Run application
python main.py
```

### Default Credentials
| Field | Value |
|-------|-------|
| **PIN** | `2345` |
| **Database** | `ui/db/senarath.db` |
| **Backups** | `backups/` folder |

---

## 🏗️ Technical Architecture

### System Design
```
┌─────────────────────────────────────────────────────┐
│                   PySide6 GUI Layer                 │
│  (Login • Home • Job Cards • Reports • Data Mgmt)  │
└──────────────────┬──────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────┐
│          Business Logic Layer                       │
│  (Validation • Calculations • Data Processing)      │
└──────────────────┬──────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────┐
│           Data Persistence Layer                    │
│  (SQLite3 • Encryption • Backup/Restore)           │
└─────────────────────────────────────────────────────┘
```

### Component Breakdown

| Layer | Technology | Responsibility |
|-------|-----------|-----------------|
| **UI** | PySide6 6.10.0 | Widgets, layouts, signals, user interaction |
| **Business** | Python 3.13 | Calculations, validation, state management |
| **Data** | SQLite3 | Persistence, querying, transactions |
| **Security** | Cryptography | AES-256-GCM encryption for backups |
| **Build** | PyInstaller | Standalone executable generation |

---

## 📦 Tech Stack

### Core Dependencies
```
Python 3.13.3                # Runtime
├── PySide6 6.10.0          # GUI Framework (Qt bindings)
├── PySide6-Addons 6.10.0   # Extended widgets
├── shiboken6 6.10.0        # Python↔C++ bridges
├── cryptography >= 41.0.0  # AES-256 encryption
└── pyinstaller 6.10.0      # Executable bundler
```

### Database
- **Type**: SQLite3 (serverless, file-based)
- **Location**: `ui/db/senarath.db`
- **Initialization**: Auto-creates on first launch
- **Encryption**: Backups use AES-256-GCM

### Platform Support
| OS | Status | Format |
|----|--------|--------|
| **macOS** | ✅ Tested | Executable + App Bundle |
| **Windows** | ✅ Fixed | EXE (PyInstaller) |
| **Linux** | ⚠️ Not tested | Run from source |

---

## 🗄️ Database Schema

### Core Tables

<details>
<summary><b>📋 vehicles</b> - Vehicle information</summary>

```sql
CREATE TABLE vehicles (
  id INTEGER PRIMARY KEY,
  company_no TEXT NOT NULL,
  number TEXT UNIQUE NOT NULL,
  make TEXT,
  model TEXT,
  type TEXT,
  status TEXT DEFAULT 'active'
);
```

| Column | Type | Notes |
|--------|------|-------|
| company_no | TEXT | Foreign key reference |
| number | TEXT | Unique identifier |
| make | TEXT | Vehicle manufacturer |
| model | TEXT | Model name |
| type | TEXT | Category (truck, van, etc) |

</details>

<details>
<summary><b>🏢 companies</b> - Company information</summary>

```sql
CREATE TABLE companies (
  id INTEGER PRIMARY KEY,
  company_no TEXT UNIQUE NOT NULL,
  name TEXT NOT NULL,
  contact TEXT,
  status TEXT DEFAULT 'active'
);
```

</details>

<details>
<summary><b>👤 drivers</b> - Driver information</summary>

```sql
CREATE TABLE drivers (
  id INTEGER PRIMARY KEY,
  name TEXT UNIQUE NOT NULL,
  license TEXT,
  contact TEXT,
  status TEXT DEFAULT 'active'
);
```

</details>

<details>
<summary><b>📝 job_cards</b> - Job card records</summary>

```sql
CREATE TABLE job_cards (
  id INTEGER PRIMARY KEY,
  job_no TEXT UNIQUE NOT NULL,
  page_no INTEGER,
  company_no TEXT,
  vehicle_no TEXT,
  driver TEXT,
  status TEXT,
  created_date TIMESTAMP,
  FOREIGN KEY (company_no) REFERENCES companies(company_no),
  FOREIGN KEY (vehicle_no) REFERENCES vehicles(number)
);
```

</details>

---

## 🎨 Design System

### Color Palette

| Name | Hex | Usage |
|------|-----|-------|
| **Primary** | `#2e7d6e` | Headers, buttons, active states |
| **Secondary** | `#a0754f` | Accents, borders |
| **Success** | `#4caf50` | Positive actions |
| **Warning** | `#ff9800` | Caution messages |
| **Danger** | `#f44336` | Destructive actions |
| **Background** | `#f5f5f5` | Page background |

### Typography
- **Font Family**: System default (SF Pro Display on macOS, Segoe UI on Windows)
- **Base Size**: 13px
- **Heading**: 16px bold
- **Small**: 11px
- **Grid Spacing**: 8px multiples

### UI Components
```python
# Consistent styling via theme.py
from ui.theme import colorPalette

# Usage
button.setStyleSheet(f"""
    background-color: {colorPalette['primary']};
    color: white;
    padding: 6px 12px;
    border-radius: 4px;
""")
```

---

## 🛠️ Build Instructions

### Build Executable for Windows

```batch
# Prerequisite: Install PyInstaller
pip install pyinstaller

# Build using spec file
pyinstaller "Senarath WMS.spec"

# Output location
# .\dist\Senarath WMS\Senarath WMS.exe
```

### Build Executable for macOS

```bash
# Prerequisite: Install PyInstaller
pip install pyinstaller

# Build app bundle
pyinstaller "Senarath WMS.spec" \
  --onedir \
  --osx-bundle-identifier=com.senarath.wms

# Create DMG for distribution
hdiutil create -volname "Senarath WMS" \
  -srcfolder dist \
  -ov -format UDZO Senarath_WMS.dmg
```

### Debug Build Issues

**Windows Build Fails**
```
Error: "Unable to find 'ui/db/senarath.db'"
✅ Solution: Database auto-creates on first run. Don't include it in build.
```

**Missing Modules**
```
Error: "ModuleNotFoundError: No module named 'cryptography'"
✅ Solution: Run `pip install -r requirements.txt`
```

**Code Changes Not Reflected**
```
✅ Solution: Rebuild executable with `pyinstaller --clean Senarath\ WMS.spec`
```

---

## 🚀 Deployment

### Standalone Distribution

#### Windows Users
1. Download `Senarath WMS.exe`
2. Double-click to run
3. Database auto-creates on first launch
4. Enter PIN: `2345`

#### macOS Users
1. Download `Senarath WMS.app`
2. Move to `/Applications`
3. Double-click to run
4. **First time?** Allow from Security & Privacy settings
5. Enter PIN: `2345`

### File Structure After Deployment

```
Senarath WMS.app/
├── Contents/
│   ├── MacOS/
│   │   └── Senarath WMS      # Executable
│   ├── Resources/
│   │   └── assets/           # Images, icons, etc
│   └── Info.plist            # macOS metadata
```

### Data Persistence
```
User Home Directory/
└── .senarath_wms/           # Application data folder
    ├── ui/db/
    │   └── senarath.db      # Database (auto-created)
    ├── backups/             # Encrypted backups
    └── reports/             # Generated reports
```

---

## 👨‍💻 Development

### Project Structure
```
Senarath_Workshop/
├── main.py                  # Entry point
├── requirements.txt         # Dependencies
├── Senarath WMS.spec       # macOS build config
├── build_exe.spec          # Windows build config
│
├── ui/
│   ├── theme.py            # Design system & colors
│   ├── pages/
│   │   ├── login_page.py       # 🔐 Authentication
│   │   ├── home_page.py        # 🏠 Dashboard
│   │   ├── job_card_page.py    # 📋 Job card entry
│   │   ├── jobcard_records_page.py  # 📊 Job records
│   │   ├── report_page.py      # 📈 Reports & analytics
│   │   ├── data_manager_page.py    # 🗄️ Data management
│   │   └── backup_restore_page.py  # 💾 Backup/Restore
│   │
│   └── db/
│       └── senarath.db     # SQLite3 database
│
├── assets/                 # Images, icons, themes
├── backups/                # Encrypted backups
├── reports/                # Generated reports
│
└── build_windows.bat       # Windows build script
```

### Key Code Examples

#### Creating a New Page
```python
# ui/pages/new_page.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from ui.theme import colorPalette

class NewPage(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        label = QLabel("New Page Content")
        label.setStyleSheet(f"color: {colorPalette['primary']};")
        layout.addWidget(label)
        self.setLayout(layout)
```

#### Database Query
```python
# Query vehicle by number
import sqlite3
conn = sqlite3.connect('ui/db/senarath.db')
cursor = conn.cursor()
cursor.execute(
    "SELECT make, model, type FROM vehicles WHERE number = ?",
    (vehicle_number,)
)
result = cursor.fetchone()
conn.close()
```

#### Working with QCompleter (Auto-complete)
```python
from PySide6.QtWidgets import QLineEdit, QCompleter
from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItemModel

# Create completer with suggestions
model = QStandardItemModel()
model.appendRow("Company A")
model.appendRow("Company B")

completer = QCompleter(model)
completer.setCompletionMode(QCompleter.PopupCompletion)
completer.setFilterMode(Qt.MatchContains)
completer.setCaseSensitivity(Qt.CaseInsensitive)

input_field = QLineEdit()
input_field.setCompleter(completer)
```

---

## 📋 Contributing

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** changes (`git commit -m 'Add amazing feature'`)
4. **Push** to branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

---

## 📄 License

This project is licensed under the **MIT License** - see [LICENSE](LICENSE) file for details.

---

## 🤝 Support & Feedback

- 📧 **Email**: Report issues via GitHub Issues
- 🐛 **Bug Reports**: Include steps to reproduce
- 💡 **Feature Requests**: Describe use case and benefits
- 📸 **Screenshots**: Helpful for UI-related issues

---

## ✨ Changelog

### Version 1.0.0 (Latest)
- ✅ Core job card management system
- ✅ Multi-page job card support
- ✅ Real-time vehicle↔company field linking
- ✅ Auto-complete suggestions for drivers, companies, vehicles
- ✅ Encrypted backup/restore functionality
- ✅ Cross-platform executables (Windows & macOS)
- ✅ Complete data management interface
- ✅ Advanced reporting and analytics

---

<div align="center">

### Made with ❤️ for Senarath Workshop

⭐ If this project helped you, please consider giving it a star!

[⬆ Back to Top](#senarath-wms)

</div>

## 📁 Project Structure

```
Senarath_Workshop/
│
├── 📄 main.py                          # Application entry point & MainWindow
├── 📄 requirements.txt                 # Python dependencies
├── 📁 ui/                              # UI Layer
│   ├── theme.py                        # 🎨 Theme system (colors, typography, spacing)
│   ├── 📁 db/
│   │   └── senarath.db                # 💾 SQLite database (auto-created on first run)
│   └── 📁 pages/                       # 📄 Application Pages
│       ├── login_page.py               # 🔐 PIN-based authentication
│       ├── home_page.py                # 📊 Dashboard & statistics
│       ├── job_card_page.py            # 📋 Job card CRUD
│       ├── data_manager_page.py        # 🗂️ Vehicle, driver, site management
│       ├── jobcard_records_page.py     # 📈 Job history & records
│       ├── report_page.py              # 📉 Reporting & analytics
│       └── backup_restore_page.py      # 💾 Backup/restore with encryption
│
├── 📁 assets/                          # 🖼️ UI assets and resources
├── 📁 backups/                         # 🔒 Encrypted database backups
└── 📁 build_scripts/                   # 🔨 PyInstaller configurations

```

> 💡 Database is auto-created on first run with sample data

---

## 🔐 Security Architecture

> 🛡️ **Enterprise-Grade Security Standards**

### Encryption & Authentication
| Feature | Implementation | Details |
|---------|-----------------|---------|
| 🔐 **Encryption** | AES-256 Fernet | Military-grade symmetric encryption |
| ✅ **Integrity** | SHA-256 Checksums | Tamper detection & corruption verification |
| 🔑 **Authentication** | PIN-based Login | Secure PIN verification system |
| 💾 **Auto-Backup** | Pre-Restore Backup | Automatic safety snapshots |
| 🛡️ **Key Management** | Secure Generation | Keys from cryptographically secure sources |

### Data Protection Pipeline

```
User Data
    ↓
[Validate Input]
    ↓
[AES-256 Encryption]
    ↓
[Generate SHA-256 Checksum]
    ↓
[Store Encrypted Data + Checksum]
    ↓
[Create Auto-Backup]
    ↓
🔒 Secure Storage
```

---

## 🛠️ Technology Stack

<div align="center">

| Layer | Component | Version | Purpose |
|-------|-----------|---------|---------|
| **Runtime** | Python | 3.13.3 | Core application runtime |
| **UI Framework** | PySide6 | 6.10.0 | Modern desktop GUI framework |
| **Database** | SQLite3 | Latest | Lightweight relational database |
| **Encryption** | Cryptography | Latest | AES-256 & cryptographic operations |
| **Build Tool** | PyInstaller | 6.10.0 | Executable bundling & distribution |

</div>

### Why These Technologies?
- ✅ **PySide6**: Modern, feature-rich GUI with native OS integration
- ✅ **SQLite**: Zero-configuration, file-based database perfect for desktop apps
- ✅ **Cryptography**: Industry-standard encryption library
- ✅ **PyInstaller**: Single-file executable distribution (38MB)

---

## 📊 Database Schema

### Reference Tables
```
📋 Vehicles Table
├── vehicle_id (PK)
├── registration_number (UNIQUE)
├── make, model, year
└── status

👤 Drivers Table
├── driver_id (PK)
├── name, contact
├── license_number
└── assigned_vehicle

📍 Sites Table
├── site_id (PK)
├── site_name
├── location, contact
└── active_status

🏷️ Sections Table
├── section_id (PK)
├── section_name
└── description
```

### Transaction Tables
```
📝 Job Cards
├── job_card_id (PK)
├── vehicle_id (FK)
├── driver_id (FK)
├── site_id (FK)
├── created_date, completion_date
└── status, notes

📋 Job Card Parts (Line Items)
├── part_id (PK)
├── job_card_id (FK)
├── section_id (FK)
├── description, quantity
└── amount
```

> 🔄 **Auto-Created on First Run**: Database is automatically initialized with all tables and sample data

---

## 🎨 Design System

### Color Palette

```
🎯 Primary Brand Colors
├── Accent Primary:    #2e7d6e (Teal) ████████
└── Accent Secondary:  #a0754f (Brown) ████████

📝 Text Colors
├── Text Primary:      #111827 (Dark Gray) - Main content
├── Text Secondary:    #4b5563 (Medium Gray) - Secondary content
└── Text Muted:        #6c757d (Light Gray) - Hints & labels

🎨 Semantic Colors
├── Success:           #059669 (Green) ✅
├── Warning:           #d97706 (Orange) ⚠️
├── Error:             #dc2626 (Red) ❌
└── Info:              #2563eb (Blue) ℹ️

🔲 Background Colors
├── Primary:           #ffffff (White) - Main background
├── Secondary:         #f0f2f5 (Light Gray) - Card backgrounds
└── Border:            #d1d5db (Gray) - Borders & dividers
```

### Typography System
```
📐 Font Stack
├── Family: System Default (San Francisco, Segoe UI, etc.)
├── Hierarchy: 6 weight levels for visual hierarchy
└── Spacing: 8px grid system for precise alignment
```

### Interactive Elements
```
✨ Button States
├── Default → Hover → Active → Disabled
└── Smooth transitions (200ms) for all interactions

📊 Data Visualization
├── Charts with gradient fills
├── Animated transitions
└── Responsive design for all screen sizes
```

---

## 🏗️ Application Architecture

## 🏗️ Application Architecture

### Layered Architecture Pattern

```
┌──────────────────────────────────────────────────┐
│          Presentation Layer (PySide6)            │
│                                                   │
│  ┌─ LoginPage (🔐 Authentication)               │
│  ├─ HomePage (📊 Dashboard & Stats)             │
│  ├─ JobCardPage (📋 Create/Edit)                │
│  ├─ DataManagerPage (🗂️ Reference Data)         │
│  ├─ JobCardRecordsPage (📈 History)             │
│  ├─ ReportPage (📉 Analytics)                   │
│  └─ BackupRestorePage (💾 Maintenance)          │
│                                                   │
├──────────────────────────────────────────────────┤
│  Business Logic & Navigation Layer               │
│  ├─ Page Routing                                │
│  ├─ State Management                            │
│  └─ Event Handling                              │
├──────────────────────────────────────────────────┤
│  Data Access Layer (Repository Pattern)         │
│  ├─ Query Builder                               │
│  ├─ Transaction Management                      │
│  └─ Connection Pooling                          │
├──────────────────────────────────────────────────┤
│  Security & Encryption Layer                    │
│  ├─ AES-256 Encryption                          │
│  ├─ SHA-256 Hashing                             │
│  └─ PIN Validation                              │
├──────────────────────────────────────────────────┤
│  Data Persistence Layer (SQLite3)               │
│  └─ senarath.db                                 │
└──────────────────────────────────────────────────┘
```

### Design Patterns Used

| Pattern | Purpose | Implementation |
|---------|---------|-----------------|
| **MVC** | Model-View-Controller separation | Each page is independent |
| **Page-Based Navigation** | Modular page system | Self-contained page modules |
| **Singleton** | Single theme instance | Global theme management |
| **Factory** | Object creation | Database connection factory |
| **Observer** | Event-driven updates | Signal/slot mechanism |
| **Repository** | Data access abstraction | Data layer encapsulation |

### Module Interaction Flow

```
User Input
    ↓
[Page Event Handler]
    ↓
[Business Logic Layer]
    ↓
[Data Access Layer]
    ↓
[SQLite Database]
    ↓
[Update UI Component]
    ↓
User Sees Result ✅
```

---

### Key Design Patterns
- **MVC Pattern**: Model-View-Controller separation
- **Page-Based Navigation**: Each page is a self-contained module
- **Theme System**: Centralized styling through theme.py
- **Lazy Initialization**: Database created on-demand

---

## 🔨 Building Executables

### macOS Build

```bash
# Run build script
./build.sh

# Output: dist/Senarath WMS (38 MB)
# ✅ ARM64 compatible (Apple Silicon)
# ✅ Single-file executable
# ✅ All dependencies bundled
```

### Windows Build

```batch
# Run batch script
build_windows.bat

# Output: dist/Senarath WMS.exe
```

### Build Verification Checklist

```
✅ Clean Build
   ├─ Previous artifacts removed
   ├─ Fresh build compilation
   └─ No cache conflicts

✅ Contents Verified
   ├─ All 7 pages included
   ├─ Theme system bundled
   ├─ Encryption modules included
   ├─ Asset files packed
   └─ Database NOT included (created on first run)

✅ Distribution Ready
   ├─ Single executable
   ├─ No external dependencies
   ├─ Ready for deployment
   └─ Version tagged
```

### Build Configuration
```bash
pyinstaller --onefile --windowed \
  --name "Senarath WMS" \
  --add-data "ui/theme.py:ui" \
  --add-data "assets:assets" \
  --hidden-import=PySide6 \
  main.py
```

---

## 📈 Features in Detail

### 📋 Job Card Management
Create and manage comprehensive job cards with complete vehicle and driver tracking:

```
Create Job Card
    ↓
[Select Vehicle] → [Assign Driver] → [Choose Site]
    ↓
[Add Job Details] → [Set Job Parts]
    ↓
[Calculate Total] → [Set Status]
    ↓
✅ Save & Archive
```

**Capabilities:**
- ✏️ Create, edit, and delete job cards
- 🚗 Real-time vehicle assignments
- 👤 Driver allocation and tracking
- 📊 Multiple job items per card
- 🔄 Status management (Pending, In Progress, Completed)
- 📅 Automatic timestamp tracking

### 🗂️ Data Management

Comprehensive master data management for all reference information:

| Module | Operations | Features |
|--------|-----------|----------|
| 🚗 **Vehicles** | Create, Read, Update, Delete | Search, filter, bulk operations |
| 👤 **Drivers** | Create, Read, Update, Delete | Assignment tracking |
| 📍 **Sites** | Create, Read, Update, Delete | Location database |
| 🏷️ **Sections** | Create, Read, Update, Delete | Work categories |

### 📊 Records & Reporting

Advanced analytics and historical record tracking:

```
📈 Analytics Dashboard
├── Total Jobs Completed: 150+
├── Revenue Generated: Chart
├── Active Vehicles: 25/30
├── Busy Drivers: 18/22
└── Job Distribution: Pie Chart
```

**Reporting Capabilities:**
- 📉 Job completion statistics
- 💰 Revenue analysis
- 📆 Date range filtering
- 🔍 Advanced search & sort
- 📤 Export to CSV/PDF
- 📊 Visual charts & graphs

### 🔐 Backup & Restore

Enterprise-grade backup with military-grade encryption:

```
Backup Process
    ↓
[Encrypt Database] → [Calculate Checksum]
    ↓
[Create Archive] → [Store Safely]
    ↓
✅ Backup Complete (Encrypted at rest)
```

**Security Features:**
- 🔒 AES-256 Fernet encryption
- ✔️ SHA-256 integrity verification
- 💾 Automatic pre-restore backup
- 🔑 User-controlled encryption keys
- 📅 Timestamped backups
- ⏮️ One-click restore capability

---

## 👨‍💻 Developer Information

<div align="center">

**Primary Developer:** `DrkCyph7`

**Organization:** 🏢 NexCy Technologies  
**Website:** 🌐 [nexcy.lk](https://nexcy.lk)

**Expertise:** Full-stack Python | UI/UX Design | Database Architecture | Enterprise Solutions

</div>

---

## 📚 Resources

- 📖 [Python Documentation](https://docs.python.org/3/)
- 🎨 [PySide6 Documentation](https://doc.qt.io/qtforpython-6/)
- 🔐 [Cryptography Library](https://cryptography.io/)
- 🗄️ [SQLite Documentation](https://www.sqlite.org/docs.html)

---

## 📝 License & Credits

Built with ❤️ using modern Python practices for enterprise reliability, security, and performance.

<div align="center">

### Support & Contribution

If you find this project useful, please consider:
- ⭐ Starring the repository
- 🐛 Reporting issues
- 🔧 Contributing improvements
- 📢 Sharing with others

---

**Made with** 💻 **by** `DrkCyph7`  
**Last Updated:** November 10, 2025

<img src="https://img.shields.io/badge/Made%20with-Python-blue?style=flat&logo=python" alt="Made with Python">
<img src="https://img.shields.io/badge/Powered%20by-PySide6-brightgreen?style=flat&logo=qt" alt="Powered by PySide6">

</div>
- **Spacing**: Unified spacing system across all pages

## 🔄 Backup & Restore

### Create Backup
1. Navigate to **Backup & Restore**
2. Click **"Create Backup Now"**
3. Backup saved to `backups/` folder with encryption

### Restore Backup
1. Go to **Backup & Restore** → **Restore Backup**
2. Select backup file
3. System creates pre-restore backup automatically
4. Restart application

## 📱 Pages

- **Login** - PIN-based authentication
- **Home** - Dashboard with quick stats
- **Job Card** - Create and manage job cards
- **Data Manager** - Manage vehicles, drivers, sites, sections
- **Job Records** - View all job card history
- **Reports** - Generate job reports
- **Backup & Restore** - Secure backup management

## 🐛 Troubleshooting

**Application won't start**
```bash
# Clear database and reinstall
rm ui/db/senarath.db
pip install -r requirements.txt
python main.py
```

**Login issues**
- Default PIN: 2345
- Check terminal output for errors

**Database errors**
- Delete `ui/db/senarath.db` and restart
- Application will recreate database automatically

## 👨‍💻 Developer

- **Lead Developer**: [DrkCyph7](https://www.google.com/search?q=DrkCyph7)
- **Organization**: [NexCy Technologies](https://nexcy.lk)
- **Version**: 1.0.0
- **Status**: ✅ Production Ready

For detailed architecture and development guide, see **DEVELOPER.md**

## 📄 License

MIT License

---

**Built with ❤️ by DrkCyph7 | © 2025 NexCy Technologies**