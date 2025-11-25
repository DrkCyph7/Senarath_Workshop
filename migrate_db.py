#!/usr/bin/env python3
"""
Database Migration Script for Senarath Workshop
Ensures all required columns exist in the database
"""

import sqlite3
import os

DB_PATH = "ui/db/senarath.db"

def migrate_database():
    """Add missing columns to existing database tables"""
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    print("Starting database migration...")
    
    # Get existing columns in vehicles table
    c.execute("PRAGMA table_info(vehicles)")
    vehicles_columns = {row[1] for row in c.fetchall()}
    
    # Add missing columns to vehicles table
    vehicles_migrations = [
        ("engine_no", "TEXT"),
        ("chassis_no", "TEXT"),
        ("year", "TEXT")
    ]
    
    for column_name, column_type in vehicles_migrations:
        if column_name not in vehicles_columns:
            try:
                c.execute(f"ALTER TABLE vehicles ADD COLUMN {column_name} {column_type}")
                print(f"✓ Added column '{column_name}' to vehicles table")
            except sqlite3.OperationalError as e:
                print(f"✗ Column '{column_name}' already exists or error: {e}")
    
    # Get existing columns in drivers table
    c.execute("PRAGMA table_info(drivers)")
    drivers_columns = {row[1] for row in c.fetchall()}
    
    # Add missing columns to drivers table
    drivers_migrations = [
        ("mobile", "TEXT"),
        ("address", "TEXT"),
        ("license_no", "TEXT")
    ]
    
    for column_name, column_type in drivers_migrations:
        if column_name not in drivers_columns:
            try:
                c.execute(f"ALTER TABLE drivers ADD COLUMN {column_name} {column_type}")
                print(f"✓ Added column '{column_name}' to drivers table")
            except sqlite3.OperationalError as e:
                print(f"✗ Column '{column_name}' already exists or error: {e}")
    
    # Get existing columns in job_cards table
    c.execute("PRAGMA table_info(job_cards)")
    job_cards_columns = {row[1] for row in c.fetchall()}
    
    # Add missing columns to job_cards table
    job_cards_migrations = [
        ("engine_no", "TEXT"),
        ("chassis_no", "TEXT"),
        ("year", "TEXT")
    ]
    
    for column_name, column_type in job_cards_migrations:
        if column_name not in job_cards_columns:
            try:
                c.execute(f"ALTER TABLE job_cards ADD COLUMN {column_name} {column_type}")
                print(f"✓ Added column '{column_name}' to job_cards table")
            except sqlite3.OperationalError as e:
                print(f"✗ Column '{column_name}' already exists or error: {e}")
    
    conn.commit()
    conn.close()
    
    print("\n✅ Database migration completed successfully!")
    print(f"Database location: {DB_PATH}")

if __name__ == "__main__":
    migrate_database()
