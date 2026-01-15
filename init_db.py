"""
Database initialization script.
Run this script to create the database tables.
"""
from app import app, db

def init_db():
    """Initialize the database."""
    with app.app_context():
        # Create all tables
        db.create_all()
        print("✅ Database tables created successfully!")
        
        # Print table information
        print("\nTables created:")
        for table in db.metadata.sorted_tables:
            print(f"  - {table.name}")

if __name__ == '__main__':
    init_db()
