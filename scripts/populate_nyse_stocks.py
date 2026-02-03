#!/usr/bin/env python3
"""
Populate the database with NYSE stock tickers.

This script reads NYSE stock tickers from a CSV file and adds them to the
StockCache table. Stock data (price, P/E ratio, etc.) is NOT fetched - it will
be fetched on-demand when users view the stocks.

Usage:
    python scripts/populate_nyse_stocks.py
"""

import csv
import os
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app import create_app
from app.models import db
from app.services.stock_service import StockService


def populate_nyse_stocks():
    """Populate database with NYSE stock tickers from CSV file."""
    app = create_app()
    
    with app.app_context():
        # Path to the CSV file
        csv_path = Path(__file__).parent.parent / 'data' / 'nyse_tickers.csv'
        
        if not csv_path.exists():
            print(f"Error: CSV file not found at {csv_path}")
            return
        
        print(f"Reading NYSE tickers from {csv_path}")
        
        added_count = 0
        skipped_count = 0
        
        with open(csv_path, 'r') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                ticker = row['ticker'].strip()
                company_name = row['company_name'].strip()
                
                # Add to database (will skip if already exists)
                if StockService.add_stock_to_cache(ticker, company_name):
                    added_count += 1
                    if added_count % 50 == 0:
                        print(f"  Added {added_count} stocks...")
                else:
                    skipped_count += 1
        
        print(f"\nPopulation complete!")
        print(f"  Added: {added_count} stocks")
        print(f"  Skipped (already exist): {skipped_count} stocks")
        print(f"  Total in database: {added_count + skipped_count} stocks")
        print(f"\nNote: Stock data (price, P/E ratio, etc.) will be fetched on-demand when viewed.")


if __name__ == '__main__':
    populate_nyse_stocks()
