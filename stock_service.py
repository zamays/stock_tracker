import yfinance as yf
from datetime import datetime
from models import db, Stock
from config import Config


class StockService:
    """Service for fetching and storing stock data."""
    
    @staticmethod
    def fetch_stock_data(ticker):
        """Fetch stock data from Yahoo Finance."""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Extract P/E ratio (trailing P/E)
            pe_ratio = info.get('trailingPE') or info.get('forwardPE')
            price = info.get('currentPrice') or info.get('regularMarketPrice')
            market_cap = info.get('marketCap')
            
            return {
                'ticker': ticker,
                'pe_ratio': pe_ratio,
                'price': price,
                'market_cap': market_cap
            }
        except Exception as e:
            print(f"Error fetching data for {ticker}: {str(e)}")
            return None
    
    @staticmethod
    def save_stock_data(stock_data):
        """Save stock data to database."""
        if not stock_data:
            return None
        
        stock = Stock(
            ticker=stock_data['ticker'],
            pe_ratio=stock_data['pe_ratio'],
            price=stock_data['price'],
            market_cap=stock_data['market_cap'],
            timestamp=datetime.utcnow()
        )
        
        db.session.add(stock)
        db.session.commit()
        
        return stock
    
    @staticmethod
    def check_pe_threshold(ticker, pe_ratio, threshold):
        """Check if P/E ratio is below threshold and print alert."""
        if pe_ratio is not None and pe_ratio < threshold:
            print(f"⚠️  ALERT: {ticker} has a P/E ratio of {pe_ratio:.2f}, which is below the threshold of {threshold}")
            print(f"   This may be a good investment opportunity during hard times!")
            return True
        return False
    
    @staticmethod
    def update_all_stocks(tickers, threshold=None):
        """Fetch and save data for all tracked stocks."""
        if threshold is None:
            threshold = Config.PE_THRESHOLD
        
        results = []
        for ticker in tickers:
            print(f"Fetching data for {ticker}...")
            stock_data = StockService.fetch_stock_data(ticker)
            
            if stock_data:
                saved_stock = StockService.save_stock_data(stock_data)
                results.append(saved_stock)
                
                # Check threshold and print alert
                if stock_data['pe_ratio']:
                    StockService.check_pe_threshold(
                        ticker, 
                        stock_data['pe_ratio'], 
                        threshold
                    )
        
        return results
    
    @staticmethod
    def get_historical_pe_data(ticker, limit=100):
        """Get historical P/E ratio data for a ticker."""
        stocks = Stock.query.filter_by(ticker=ticker)\
            .order_by(Stock.timestamp.desc())\
            .limit(limit)\
            .all()
        
        return list(reversed([stock.to_dict() for stock in stocks]))
    
    @staticmethod
    def get_latest_stocks():
        """Get the latest data for each tracked ticker."""
        latest_stocks = {}
        
        tickers = Config.STOCKS_TO_TRACK
        for ticker in tickers:
            stock = Stock.query.filter_by(ticker=ticker)\
                .order_by(Stock.timestamp.desc())\
                .first()
            
            if stock:
                latest_stocks[ticker] = stock.to_dict()
        
        return latest_stocks
