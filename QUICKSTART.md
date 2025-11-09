# 🚀 Quick Start - Senarath WMS Executable

## Running the Application

### macOS Users

#### Option 1: Command Line
```bash
chmod +x "Senarath WMS"
./Senarath WMS
```

#### Option 2: Double-Click
Simply double-click the `.app` bundle:
```
Senarath WMS.app
```

#### Option 3: Finder
1. Open Finder
2. Navigate to where you downloaded the file
3. Double-click `Senarath WMS.app`

---

### Windows Users

#### Building Windows Executable
First, build the Windows version using the batch script:
```batch
build_windows.bat
```

This creates: `dist/Senarath WMS.exe`

#### Running on Windows
Simply double-click:
```
Senarath WMS.exe
```

---

## First Launch

### What Happens on First Run:

1. **Database Creation**
   - Automatic database creation at: `ui/db/senarath.db`
   - All tables initialized (vehicles, drivers, sites, sections, job_cards)
   - Sample data automatically inserted

2. **Login Screen**
   - Enter PIN: **2345**
   - Click "Login" or press Enter

3. **Dashboard Loads**
   - Welcome to Senarath WMS v1.0.0
   - Ready to start managing jobs!

---

## Default Credentials

| Setting | Value |
|---------|-------|
| PIN | 2345 |
| Database File | `ui/db/senarath.db` |
| Backups Folder | `backups/` |

---

## Application Features

### Dashboard
- View job statistics
- Quick navigation to all modules

### Job Card Management
- Create new job cards
- Track job progress
- Manage job details

### Data Management
- Manage vehicles
- Manage drivers
- Manage sites
- Manage sections

### Job Records
- View all job records
- Filter and search
- Export data

### Reports
- Generate reports
- View analytics
- Export reports

### Backup & Restore
- Create encrypted backups
- Restore from backups
- Automatic pre-restore backup

---

## File Structure After First Run

```
~/ (or installation directory)
├── Senarath WMS                 (Executable)
├── Senarath WMS.app             (macOS bundle)
├── ui/
│   └── db/
│       └── senarath.db          (Created on first run)
├── backups/                     (Created automatically)
│   └── *.senarath.backup        (Encrypted backup files)
└── logs/                        (If logging enabled)
```

---

## Troubleshooting

### "Command not found" Error
**On macOS/Linux:**
```bash
chmod +x "Senarath WMS"
./Senarath WMS
```

### "Permission denied" Error
**On macOS/Linux:**
```bash
chmod +x "Senarath WMS"
```

### Database Not Found
- This is normal on first run
- The application creates it automatically
- If issues persist, restart the application

### PIN not Working
- Default PIN: **2345**
- Make sure Caps Lock is off
- PIN is case-sensitive

### Application Won't Start
1. Make sure Python dependencies are correct
2. Check that the system has sufficient disk space
3. Ensure macOS/Windows is up to date
4. Try deleting the database: `rm ui/db/senarath.db`
5. Restart the application

---

## System Requirements

### macOS
- macOS 10.13 or later
- 100 MB free disk space
- Python 3.10+ (for building from source)

### Windows
- Windows 10 or later
- 100 MB free disk space
- Python 3.10+ (for building from source)

### Linux
- Ubuntu 18.04 or later
- 100 MB free disk space
- Python 3.10+ (for building from source)

---

## Building from Source

If you prefer to run from source instead of the executable:

```bash
# Clone/extract the project
cd Senarath_Workshop

# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # macOS/Linux
# or
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

---

## Build Your Own Executable

### Clean Build (No Database)
```bash
./build_clean.sh
```
Creates: `dist/Senarath WMS`

### Build for Windows
```bash
build_windows.bat
```
Creates: `dist/Senarath WMS.exe`

### Build with Current Database
```bash
./build.sh
```
Creates: `dist/Senarath WMS` (includes current DB)

---

## Backup & Recovery

### Creating a Backup
1. Open application
2. Navigate to Backup & Restore page
3. Click "Create Backup"
4. Choose backup location
5. Backup saved as `.senarath.backup`

### Restoring from Backup
1. Open application
2. Navigate to Backup & Restore page
3. Click "Restore from Backup"
4. Select `.senarath.backup` file
5. Automatic pre-restore backup created
6. Data restored successfully

---

## Security Information

### Encryption
- All backups encrypted with AES-256
- Secure key management
- SHA-256 checksums for integrity

### Authentication
- PIN-based login system
- Default PIN: 2345 (should be changed)
- Secure password storage

### Data Protection
- All sensitive data encrypted
- Automatic backup on restore
- Data integrity verification

---

## Additional Resources

- **README.md** - Full project documentation
- **DEVELOPER.md** - Technical documentation
- **BUILD_SUMMARY.md** - Build details

---

## Support & Contact

**Developer:** DrkCyph7  
**Organization:** NexCy Technologies  
**Website:** https://nexcy.lk  

---

**Version:** 1.0.0  
**Status:** ✅ Production Ready  
**Last Updated:** November 9, 2025

