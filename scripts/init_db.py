#!/usr/bin/env python3
"""
Database initialization script.
Run this script to create the database tables.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import create_app
from app.models import db


def init_db():
    """Initialize the database."""
    app = create_app()

    with app.app_context():
        # Create all tables
        db.create_all()
        print("Database tables created successfully!")

        # Print table information
        print("\nTables created:")
        for table in db.metadata.sorted_tables:
            print(f"  - {table.name}")


if __name__ == '__main__':
    init_db()
