"""
Database creation script for the data analysis project.

This module creates the SQLite database and defines the schema for:
- users: User information and signup data
- user_logs: User behavior event logs
- ab_test_results: A/B test assignment and conversion data
"""

import sqlite3
import os
from pathlib import Path


def create_database(db_path: str = "data/app_data.db") -> None:
    """
    Create SQLite database with required tables.
    
    Args:
        db_path: Path to the SQLite database file
    """
    # Ensure data directory exists
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    
    # Connect to database (creates if doesn't exist)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            signup_date TEXT NOT NULL,
            channel TEXT,
            segment TEXT
        )
    """)
    
    # Create user_logs table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_logs (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            event_name TEXT NOT NULL,
            event_timestamp TEXT NOT NULL,
            value REAL,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """)
    
    # Create ab_test_results table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ab_test_results (
            user_id INTEGER PRIMARY KEY,
            group_name TEXT NOT NULL,
            is_converted INTEGER NOT NULL,
            conversion_timestamp TEXT,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """)
    
    # Create indexes for better query performance
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_user_logs_user_id 
        ON user_logs(user_id)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_user_logs_event_name 
        ON user_logs(event_name)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_user_logs_timestamp 
        ON user_logs(event_timestamp)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_ab_test_group 
        ON ab_test_results(group_name)
    """)
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    
    print(f"[OK] Database created successfully at: {db_path}")
    print("[OK] Tables created: users, user_logs, ab_test_results")
    print("[OK] Indexes created for optimized queries")


if __name__ == "__main__":
    create_database()
