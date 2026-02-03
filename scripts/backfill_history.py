#!/usr/bin/env python3
"""
Backfill historical P/E ratio data for the past month.
Fetches hourly price data and calculates P/E ratios using trailing EPS.
"""

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import yfinance as yf

from app import create_app
from app.config import Config
from app.models import db, Stock

# Create app instance
app = create_app()


def get_historical_prices(ticker_symbol, days=30):
    """Get hourly price data for the past N days."""
    try:
        ticker = yf.Ticker(ticker_symbol)

        # Get hourly data for the past month
        # yfinance allows up to 730 days of hourly data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        hist = ticker.history(
            start=start_date,
            end=end_date,
            interval='1h'
        )

        if hist.empty:
            print(f"  No historical data found for {ticker_symbol}")
            return []

        # Extract timestamps and closing prices
        data = []
        for timestamp, row in hist.iterrows():
            # Convert to timezone-aware UTC datetime
            ts = timestamp.to_pydatetime()
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
            else:
                ts = ts.astimezone(timezone.utc)

            data.append({
                'timestamp': ts,
                'price': row['Close'],
                'volume': row.get('Volume', 0)
            })

        return data
    except Exception as e:
        print(f"  Error getting historical prices for {ticker_symbol}: {e}")
        return []


def backfill_stock(ticker_symbol, eps, shares_outstanding, days=30):
    """Backfill historical P/E data for a single stock."""
    print(f"\nProcessing {ticker_symbol}...")

    if eps is None or eps <= 0:
        print(f"  Skipping {ticker_symbol}: Invalid EPS ({eps})")
        return 0

    print(f"  Trailing EPS: ${eps:.2f}")

    # Get historical prices
    historical_data = get_historical_prices(ticker_symbol, days)

    if not historical_data:
        return 0

    print(f"  Found {len(historical_data)} hourly data points")

    # Get existing timestamps to avoid duplicates
    existing_timestamps = set()
    with app.app_context():
        existing = Stock.query.filter_by(ticker=ticker_symbol).all()
        for stock in existing:
            if stock.timestamp:
                # Normalize to hour for comparison
                ts = stock.timestamp.replace(minute=0, second=0, microsecond=0)
                existing_timestamps.add(ts)

    # Insert new records
    records_added = 0
    with app.app_context():
        for data_point in historical_data:
            # Normalize timestamp to hour
            ts = data_point['timestamp'].replace(minute=0, second=0, microsecond=0)

            # Skip if we already have data for this hour
            if ts in existing_timestamps:
                continue

            price = data_point['price']
            pe_ratio = price / eps if eps > 0 else None

            # Estimate market cap using cached shares outstanding
            market_cap = price * shares_outstanding if shares_outstanding else None

            stock = Stock(
                ticker=ticker_symbol,
                pe_ratio=pe_ratio,
                price=price,
                market_cap=market_cap,
                timestamp=ts
            )

            db.session.add(stock)
            records_added += 1
            existing_timestamps.add(ts)

        db.session.commit()

    print(f"  Added {records_added} new records")
    return records_added


def get_stock_info(ticker_symbol):
    """Get EPS and shares outstanding for a stock (cached call)."""
    try:
        ticker = yf.Ticker(ticker_symbol)
        info = ticker.info

        eps = info.get('trailingEps')
        if eps is None:
            pe = info.get('trailingPE')
            price = info.get('currentPrice') or info.get('regularMarketPrice')
            if pe and price:
                eps = price / pe

        shares = info.get('sharesOutstanding', 0)
        return eps, shares
    except Exception as e:
        print(f"  Error getting info for {ticker_symbol}: {e}")
        return None, 0


def main():
    """Main function to backfill historical data."""
    days = 30
    print("=" * 60)
    print("Stock Tracker - Historical Data Backfill")
    print("=" * 60)
    print(f"Start time: {datetime.now()}")
    print(f"Backfilling {days} days of hourly P/E ratio data")
    print("=" * 60)

    tickers = Config.STOCKS_TO_TRACK
    total_records = 0

    # First, get EPS and shares for all stocks (do this once to avoid rate limiting)
    print("\nFetching stock info for all tickers...")
    stock_info = {}
    for ticker in tickers:
        eps, shares = get_stock_info(ticker)
        stock_info[ticker] = {'eps': eps, 'shares': shares}
        if eps:
            print(f"  {ticker}: EPS=${eps:.2f}, Shares={shares:,}")
        else:
            print(f"  {ticker}: N/A")

    # Now backfill each stock
    for ticker in tickers:
        info = stock_info.get(ticker, {})
        eps = info.get('eps')
        shares = info.get('shares', 0)
        records = backfill_stock(ticker, eps, shares, days=days)
        total_records += records

    print("\n" + "=" * 60)
    print("Backfill complete!")
    print(f"Total records added: {total_records}")
    print(f"End time: {datetime.now()}")
    print("=" * 60)


if __name__ == '__main__':
    main()
