#!/usr/bin/env python3
"""Initialize the database with tables"""
import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database.connection import init_db

if __name__ == "__main__":
    print("Initializing database...")
    try:
        init_db()
        print("Database initialization complete!")
    except Exception as e:
        print(f"Error initializing database: {e}")
        print("Make sure PostgreSQL is running and DATABASE_URL is set correctly in .env")
        sys.exit(1)
