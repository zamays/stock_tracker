"""Database models."""

from datetime import datetime, timezone

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
    timestamp = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True
    )

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


class StockCache(db.Model):
    """Model for caching NYSE stock data."""

    __tablename__ = 'stock_cache'

    id = db.Column(db.Integer, primary_key=True)
    ticker = db.Column(db.String(10), nullable=False, unique=True, index=True)
    company_name = db.Column(db.String(200), nullable=True)
    pe_ratio = db.Column(db.Float, nullable=True)
    price = db.Column(db.Float, nullable=True)
    market_cap = db.Column(db.Float, nullable=True)
    last_updated = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True
    )

    def __repr__(self):
        return f'<StockCache {self.ticker} {self.company_name}>'

    def to_dict(self):
        """Convert stock cache data to dictionary."""
        return {
            'id': self.id,
            'ticker': self.ticker,
            'company_name': self.company_name,
            'pe_ratio': self.pe_ratio,
            'price': self.price,
            'market_cap': self.market_cap,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None
        }
