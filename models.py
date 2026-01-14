from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Stock(db.Model):
    """Model for storing stock information and P/E ratios."""
    
    __tablename__ = 'stocks'
    
    id = db.Column(db.Integer, primary_key=True)
    ticker = db.Column(db.String(10), nullable=False, index=True)
    pe_ratio = db.Column(db.Float, nullable=True)
    price = db.Column(db.Float, nullable=True)
    market_cap = db.Column(db.Float, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    def __repr__(self):
        return f'<Stock {self.ticker} PE:{self.pe_ratio} at {self.timestamp}>'
    
    def to_dict(self):
        """Convert stock data to dictionary."""
        return {
            'id': self.id,
            'ticker': self.ticker,
            'pe_ratio': self.pe_ratio,
            'price': self.price,
            'market_cap': self.market_cap,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }
