#!/usr/bin/env python3
"""
Populate test data for demonstration purposes.

This script adds mock stock data to demonstrate the Stock Explorer functionality.
In production, real data would be fetched from Yahoo Finance API.
"""

import random
import sys
from pathlib import Path
from datetime import datetime, timezone

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app import create_app
from app.models import db, StockCache


def populate_test_data():
    """Add mock data to a few stocks for demonstration."""
    app = create_app()
    
    with app.app_context():
        # Get first 30 stocks
        stocks = StockCache.query.limit(30).all()
        
        print("Adding mock data to stocks for demonstration...")
        
        for stock in stocks:
            # Generate realistic mock data
            stock.price = round(random.uniform(20, 500), 2)
            stock.pe_ratio = round(random.uniform(8, 45), 2)
            stock.market_cap = round(random.uniform(10, 3000) * 1000000000, 2)
            stock.last_updated = datetime.now(timezone.utc)
        
        db.session.commit()
        
        print(f"Added mock data to {len(stocks)} stocks")
        print("\nSample data:")
        for stock in stocks[:5]:
            print(f"  {stock.ticker}: ${stock.price}, P/E={stock.pe_ratio}, MCap=${stock.market_cap/1e9:.2f}B")


if __name__ == '__main__':
    populate_test_data()
