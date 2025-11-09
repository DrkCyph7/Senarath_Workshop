# Senarath WMS - Workshop Management System

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.13.3-blue.svg)
![PySide6](https://img.shields.io/badge/PySide6-6.10.0-brightgreen.svg)

A professional workshop management system for creating, tracking, and reporting job cards. Built with PySide6, SQLite3, and AES-256 encryption.

## ✨ Features

- **Job Card Management** - Create, edit, and track job cards with vehicle and driver assignments
- **Data Management** - Manage vehicles, drivers, sites, and work sections
- **Job Records** - View complete job history with filtering and search
- **Reports** - Generate job card reports with export options
- **Encrypted Backups** - AES-256 encrypted database backups with integrity verification
- **User Authentication** - PIN-based secure login
- **Modern UI** - Professional design with consistent theme system

## 🚀 Quick Start

### Prerequisites
- Python 3.13.3+
- pip

### Installation

```bash
# Clone repository
git clone https://github.com/DrkCyph7/Senarath_Workshop.git
cd Senarath_Workshop

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# or
.venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### Run Application

```bash
python main.py
```

**Default PIN**: 2345

## 📁 Project Structure

```
Senarath_Workshop/
├── main.py                      # Application entry point
├── ui/
│   ├── theme.py                # Theme & design system
│   ├── db/
│   │   └── senarath.db         # SQLite database
│   └── pages/
│       ├── login_page.py
│       ├── home_page.py
│       ├── job_card_page.py
│       ├── data_manager_page.py
│       ├── jobcard_records_page.py
│       ├── report_page.py
│       └── backup_restore_page.py
├── backups/                    # Encrypted backups
└── README.md                   # This file
```

## 🔐 Security

- **Encryption**: AES-256 Fernet for database backups
- **Checksum**: SHA-256 verification for data integrity
- **Authentication**: PIN-based login system
- **Auto Backup**: Pre-restore backup creation for safety

## 🛠️ Technology Stack

| Component | Version |
|-----------|---------|
| Python | 3.13.3 |
| PySide6 | 6.10.0 |
| SQLite3 | Latest |
| Cryptography | Latest |

## 📊 Database Tables

- `vehicles` - Vehicle information
- `drivers` - Driver details
- `sites` - Work sites/locations
- `sections` - Work sections
- `job_cards` - Job card records
- `job_card_parts` - Job card line items

## 🎨 Design System

- **Primary Color**: #2e7d6e (Teal)
- **Secondary Color**: #a0754f (Brown)
- **Typography**: Professional sans-serif with consistent sizing
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
