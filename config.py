import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration."""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database settings
    DB_USER = os.environ.get('DB_USER', 'root')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_NAME = os.environ.get('DB_NAME', 'stock_tracker')
    
    # Use SQLite for local development if USE_SQLITE is set
    if os.environ.get('USE_SQLITE', 'False').lower() == 'true':
        SQLALCHEMY_DATABASE_URI = 'sqlite:///stock_tracker.db'
    else:
        SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Stock tracker settings
    PE_THRESHOLD = float(os.environ.get('PE_THRESHOLD', '20'))
    
    # Major stocks to track
    STOCKS_TO_TRACK = [
        'AAPL',  # Apple
        'MSFT',  # Microsoft
        'GOOGL', # Google
        'AMZN',  # Amazon
        'META',  # Meta
        'TSLA',  # Tesla
        'NVDA',  # Nvidia
        'JPM',   # JPMorgan Chase
        'V',     # Visa
        'WMT',   # Walmart
    ]
