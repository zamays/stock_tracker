# Stock Tracker

A web application for tracking stock P/E ratios over time to identify investment opportunities during market downturns.

## Features

- 📊 Track P/E ratios for major stocks (AAPL, MSFT, GOOGL, AMZN, META, TSLA, NVDA, JPM, V, WMT)
- 📈 Visualize P/E ratio trends over time with interactive charts
- ⚠️ Terminal alerts when P/E ratios fall below user-defined threshold (default: 20)
- 💾 MySQL database backend for historical data storage
- 🌐 Web interface for easy monitoring
- ☁️ Ready for deployment on PythonAnywhere

## Installation

### Local Development

1. Clone the repository:
```bash
git clone https://github.com/zamays/stock_tracker.git
cd stock_tracker
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up MySQL database:
```bash
# Create a database named 'stock_tracker'
mysql -u root -p
CREATE DATABASE stock_tracker;
exit;
```

4. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your database credentials
```

5. Run the application:
```bash
python app.py
```

6. Open your browser and navigate to `http://localhost:5000`

## PythonAnywhere Deployment

### Step 1: Set up MySQL Database

1. Log in to PythonAnywhere
2. Go to the "Databases" tab
3. Create a new MySQL database (note the hostname, username, and password)

### Step 2: Upload Files

1. Open a Bash console on PythonAnywhere
2. Clone your repository:
```bash
git clone https://github.com/zamays/stock_tracker.git
cd stock_tracker
```

3. Install dependencies:
```bash
pip3 install --user -r requirements.txt
```

### Step 3: Configure the Web App

1. Go to the "Web" tab
2. Click "Add a new web app"
3. Choose "Manual configuration" and select Python 3.10 (or latest available)
4. Set the source code directory to: `/home/yourusername/stock_tracker`
5. Edit the WSGI configuration file and replace its contents with the content from `wsgi.py`
6. Update the path in WSGI file to match your directory

### Step 4: Set Environment Variables

In the WSGI file or in a .env file, set:
```python
os.environ['DB_USER'] = 'yourusername'
os.environ['DB_PASSWORD'] = 'your_db_password'
os.environ['DB_HOST'] = 'yourusername.mysql.pythonanywhere-services.com'
os.environ['DB_NAME'] = 'yourusername$stock_tracker'
os.environ['SECRET_KEY'] = 'your-secret-key'
```

### Step 5: Initialize the Database

1. Open a Bash console
2. Navigate to your app directory
3. Run Python and initialize the database:
```bash
cd stock_tracker
python3
>>> from app import app, db
>>> with app.app_context():
...     db.create_all()
>>> exit()
```

### Step 6: Reload and Test

1. Click the "Reload" button in the Web tab
2. Visit your site at `https://yourusername.pythonanywhere.com`

## Usage

### Updating Stock Data

1. Navigate to the main dashboard
2. Optionally adjust the P/E threshold
3. Click "Update Stock Data" button
4. Check the terminal/console for alerts about stocks below the threshold

### Viewing Historical Data

1. Click on any stock card to view its historical P/E ratio chart
2. The chart shows trends over time with the threshold line
3. Historical data table shows all recorded data points

### Terminal Alerts

When updating stock data, the application will print alerts to the terminal:

```
⚠️  ALERT: AAPL has a P/E ratio of 18.50, which is below the threshold of 20
   This may be a good investment opportunity during hard times!
```

## Configuration

Edit `config.py` to customize:

- `PE_THRESHOLD`: Default P/E ratio threshold (default: 20)
- `STOCKS_TO_TRACK`: List of stock tickers to monitor
- Database connection settings

## API Endpoints

- `GET /api/stocks` - Get latest data for all tracked stocks
- `GET /api/stock/<ticker>/history` - Get historical data for a specific stock

## Technology Stack

- **Backend**: Flask (Python web framework)
- **Database**: MySQL with SQLAlchemy ORM
- **Data Source**: Yahoo Finance (via yfinance library)
- **Visualization**: Matplotlib for chart generation
- **Frontend**: HTML/CSS with minimal JavaScript

## Requirements

- Python 3.8+
- MySQL 5.7+
- See `requirements.txt` for Python package dependencies

## License

See LICENSE file for details.

## Disclaimer

This application is for educational purposes only. The data provided should not be considered financial advice. Always conduct your own research before making investment decisions.
