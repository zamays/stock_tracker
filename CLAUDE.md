# Stock Tracker Project

## Overview

A Flask web application that tracks P/E ratios of major stocks and displays them in graphs. Alerts when P/E ratios fall below a configurable threshold (default: 20), indicating potential investment opportunities.

## Current Status

- App is functional with production-ready folder structure
- Uses SQLite for local development (`USE_SQLITE=True` in .env)
- MySQL support available for production deployment
- Historical data backfill script available

## Project Structure

```text
stock_tracker/
├── app/                      # Application package
│   ├── __init__.py           # App factory (create_app)
│   ├── config.py             # Configuration (reads from .env)
│   ├── models.py             # Stock model (SQLAlchemy)
│   ├── routes.py             # All route handlers
│   ├── services/
│   │   └── stock_service.py  # Yahoo Finance integration
│   └── templates/            # Jinja2 HTML templates
├── scripts/                  # Utility scripts
│   ├── backfill_history.py   # Backfill 30 days of hourly P/E data
│   ├── create_sample_data.py # Create fake test data
│   └── init_db.py            # Initialize database tables
├── instance/                 # SQLite database location
├── tests/                    # Test package (empty)
├── run.py                    # Entry point (python run.py)
├── setup.sh                  # Idempotent setup script
└── wsgi.py                   # WSGI for PythonAnywhere
```

## Quick Start

```bash
./setup.sh                    # One-time setup (creates venv, installs deps, creates .env, init db)
source .venv/bin/activate
python run.py                 # Runs on http://localhost:5001
```

## Key Commands

```bash
python scripts/backfill_history.py    # Backfill historical P/E data from Yahoo Finance
python scripts/create_sample_data.py  # Create sample test data (clears existing)
python scripts/init_db.py             # Initialize/reset database tables
```

## Configuration

- `.env` file controls all settings (created from `.env.example` by setup.sh)
- `USE_SQLITE=True` for local SQLite, `False` for MySQL
- `PE_THRESHOLD=20` default alert threshold
- Port 5001 (macOS uses 5000 for AirPlay)

## Tracked Stocks

AAPL, MSFT, GOOGL, AMZN, META, TSLA, NVDA, JPM, V, WMT

## API Endpoints

- `GET /` - Dashboard with all stocks
- `GET /stock/<ticker>` - Stock detail with P/E chart
- `POST /update` - Fetch latest data from Yahoo Finance
- `GET /api/stocks` - JSON of latest stock data
- `GET /api/stock/<ticker>/history` - JSON historical data

## Tech Stack

- Flask 3.0 with app factory pattern
- SQLAlchemy ORM (SQLite/MySQL)
- yfinance for stock data
- matplotlib for chart generation

## Known Issues / TODO

- Yahoo Finance rate limiting can occur during bulk backfill
- Hourly auto-update not yet implemented (currently manual via /update)
- No tests written yet
