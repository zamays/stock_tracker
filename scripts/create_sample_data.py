#!/usr/bin/env python3
"""
Test script to populate the database with sample stock data.
This is useful for testing the application when Yahoo Finance API is not accessible.
"""

import random
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import create_app
from app.models import db, Stock


def create_sample_data():
    """Create sample stock data for testing."""
    app = create_app()

    tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'TSLA', 'NVDA', 'JPM', 'V', 'WMT']

    # Sample P/E ratios (some below threshold of 20)
    sample_pe_ratios = {
        'AAPL': 28.5,
        'MSFT': 32.1,
        'GOOGL': 24.3,
        'AMZN': 45.2,
        'META': 18.9,   # Below threshold
        'TSLA': 52.7,
        'NVDA': 41.3,
        'JPM': 11.2,    # Below threshold
        'V': 29.8,
        'WMT': 17.5,    # Below threshold
    }

    sample_prices = {
        'AAPL': 175.25,
        'MSFT': 378.50,
        'GOOGL': 142.80,
        'AMZN': 168.90,
        'META': 492.30,
        'TSLA': 248.15,
        'NVDA': 875.40,
        'JPM': 189.60,
        'V': 282.70,
        'WMT': 165.50,
    }

    sample_market_caps = {
        'AAPL': 2700000000000,
        'MSFT': 2800000000000,
        'GOOGL': 1800000000000,
        'AMZN': 1750000000000,
        'META': 1240000000000,
        'TSLA': 780000000000,
        'NVDA': 2150000000000,
        'JPM': 560000000000,
        'V': 550000000000,
        'WMT': 480000000000,
    }

    with app.app_context():
        # Clear existing data
        Stock.query.delete()
        db.session.commit()

        print("Creating sample stock data...")
        print("=" * 60)

        # Create historical data (last 30 days)
        for i in range(30):
            timestamp = datetime.now(timezone.utc) - timedelta(days=29-i)

            for ticker in tickers:
                # Add some variation to the P/E ratio
                base_pe = sample_pe_ratios[ticker]
                variation = random.uniform(-0.1, 0.1) * base_pe
                pe_ratio = base_pe + variation

                # Add some variation to price
                base_price = sample_prices[ticker]
                price_variation = random.uniform(-0.05, 0.05) * base_price
                price = base_price + price_variation

                stock = Stock(
                    ticker=ticker,
                    pe_ratio=round(pe_ratio, 2),
                    price=round(price, 2),
                    market_cap=sample_market_caps[ticker],
                    timestamp=timestamp
                )
                db.session.add(stock)

        db.session.commit()
        print(f"Created {Stock.query.count()} sample stock records")

        # Check which stocks are below threshold
        threshold = 20
        print(f"\nStocks below P/E threshold of {threshold}:")
        for ticker in tickers:
            latest = Stock.query.filter_by(ticker=ticker).order_by(Stock.timestamp.desc()).first()
            if latest and latest.pe_ratio < threshold:
                print(f"  {ticker}: P/E = {latest.pe_ratio:.2f}")


if __name__ == '__main__':
    create_sample_data()
