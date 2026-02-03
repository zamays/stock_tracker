"""Stock data service for fetching and storing stock information."""

import time
from datetime import datetime, timedelta, timezone

import yfinance as yf

from app.config import Config
from app.models import db, Stock, StockCache


class StockService:
    """Service for fetching and storing stock data."""

    # Rate limiting: track last request time
    _last_request_time = 0
    _min_request_interval = 0.5  # 2 requests per second max

    # Popular NYSE stocks to start with
    POPULAR_NYSE_STOCKS = [
        {'ticker': 'AAPL', 'name': 'Apple Inc.'},
        {'ticker': 'MSFT', 'name': 'Microsoft Corporation'},
        {'ticker': 'GOOGL', 'name': 'Alphabet Inc.'},
        {'ticker': 'AMZN', 'name': 'Amazon.com Inc.'},
        {'ticker': 'META', 'name': 'Meta Platforms Inc.'},
        {'ticker': 'TSLA', 'name': 'Tesla Inc.'},
        {'ticker': 'NVDA', 'name': 'NVIDIA Corporation'},
        {'ticker': 'JPM', 'name': 'JPMorgan Chase & Co.'},
        {'ticker': 'V', 'name': 'Visa Inc.'},
        {'ticker': 'WMT', 'name': 'Walmart Inc.'},
        {'ticker': 'UNH', 'name': 'UnitedHealth Group Inc.'},
        {'ticker': 'JNJ', 'name': 'Johnson & Johnson'},
        {'ticker': 'XOM', 'name': 'Exxon Mobil Corporation'},
        {'ticker': 'PG', 'name': 'Procter & Gamble Co.'},
        {'ticker': 'MA', 'name': 'Mastercard Inc.'},
        {'ticker': 'HD', 'name': 'Home Depot Inc.'},
        {'ticker': 'CVX', 'name': 'Chevron Corporation'},
        {'ticker': 'BAC', 'name': 'Bank of America Corp.'},
        {'ticker': 'ABBV', 'name': 'AbbVie Inc.'},
        {'ticker': 'KO', 'name': 'Coca-Cola Co.'},
        {'ticker': 'PEP', 'name': 'PepsiCo Inc.'},
        {'ticker': 'COST', 'name': 'Costco Wholesale Corp.'},
        {'ticker': 'MRK', 'name': 'Merck & Co. Inc.'},
        {'ticker': 'TMO', 'name': 'Thermo Fisher Scientific'},
        {'ticker': 'AVGO', 'name': 'Broadcom Inc.'},
        {'ticker': 'LLY', 'name': 'Eli Lilly and Co.'},
        {'ticker': 'ORCL', 'name': 'Oracle Corporation'},
        {'ticker': 'NKE', 'name': 'Nike Inc.'},
        {'ticker': 'DIS', 'name': 'Walt Disney Co.'},
        {'ticker': 'ACN', 'name': 'Accenture plc'},
        {'ticker': 'CSCO', 'name': 'Cisco Systems Inc.'},
        {'ticker': 'ADBE', 'name': 'Adobe Inc.'},
        {'ticker': 'WFC', 'name': 'Wells Fargo & Co.'},
        {'ticker': 'VZ', 'name': 'Verizon Communications'},
        {'ticker': 'CRM', 'name': 'Salesforce Inc.'},
        {'ticker': 'NFLX', 'name': 'Netflix Inc.'},
        {'ticker': 'INTC', 'name': 'Intel Corporation'},
        {'ticker': 'ABT', 'name': 'Abbott Laboratories'},
        {'ticker': 'AMD', 'name': 'Advanced Micro Devices'},
        {'ticker': 'PFE', 'name': 'Pfizer Inc.'},
        {'ticker': 'TXN', 'name': 'Texas Instruments Inc.'},
        {'ticker': 'DHR', 'name': 'Danaher Corporation'},
        {'ticker': 'CMCSA', 'name': 'Comcast Corporation'},
        {'ticker': 'UNP', 'name': 'Union Pacific Corp.'},
        {'ticker': 'NEE', 'name': 'NextEra Energy Inc.'},
        {'ticker': 'PM', 'name': 'Philip Morris International'},
        {'ticker': 'RTX', 'name': 'RTX Corporation'},
        {'ticker': 'BMY', 'name': 'Bristol-Myers Squibb'},
        {'ticker': 'UPS', 'name': 'United Parcel Service'},
        {'ticker': 'MS', 'name': 'Morgan Stanley'},
    ]

    @staticmethod
    def _enforce_rate_limit():
        """Enforce rate limiting: max 2 requests per second."""
        current_time = time.time()
        time_since_last_request = current_time - StockService._last_request_time
        
        if time_since_last_request < StockService._min_request_interval:
            sleep_time = StockService._min_request_interval - time_since_last_request
            time.sleep(sleep_time)
        
        StockService._last_request_time = time.time()

    @staticmethod
    def _fetch_stock_info(ticker):
        """Fetch stock info from Yahoo Finance with rate limiting."""
        StockService._enforce_rate_limit()
        
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Extract company name
            company_name = info.get('longName') or info.get('shortName')
            
            # Extract P/E ratio (trailing P/E)
            pe_ratio = info.get('trailingPE') or info.get('forwardPE')
            price = info.get('currentPrice') or info.get('regularMarketPrice')
            market_cap = info.get('marketCap')
            
            return {
                'ticker': ticker,
                'company_name': company_name,
                'pe_ratio': pe_ratio,
                'price': price,
                'market_cap': market_cap
            }
        except Exception as e:
            print(f"Error fetching data for {ticker}: {str(e)}")
            return None

    @staticmethod
    def _update_stock_cache(ticker, company_name=None):
        """Update or create stock cache entry. Only fetches if data is older than 1 hour."""
        # Check if we have cached data
        cached_stock = StockCache.query.filter_by(ticker=ticker).first()
        
        # If we have recent data (less than 1 hour old), return it
        if cached_stock:
            time_since_update = datetime.now(timezone.utc) - cached_stock.last_updated.replace(tzinfo=timezone.utc)
            if time_since_update < timedelta(hours=1):
                return cached_stock
        
        # Fetch new data from Yahoo Finance
        stock_info = StockService._fetch_stock_info(ticker)
        
        if not stock_info:
            # If fetch failed but we have cached data, return it
            if cached_stock:
                return cached_stock
            return None
        
        # Update or create cache entry
        if cached_stock:
            cached_stock.company_name = stock_info.get('company_name') or cached_stock.company_name
            cached_stock.pe_ratio = stock_info.get('pe_ratio')
            cached_stock.price = stock_info.get('price')
            cached_stock.market_cap = stock_info.get('market_cap')
            cached_stock.last_updated = datetime.now(timezone.utc)
        else:
            cached_stock = StockCache(
                ticker=ticker,
                company_name=stock_info.get('company_name') or company_name,
                pe_ratio=stock_info.get('pe_ratio'),
                price=stock_info.get('price'),
                market_cap=stock_info.get('market_cap'),
                last_updated=datetime.now(timezone.utc)
            )
            db.session.add(cached_stock)
        
        db.session.commit()
        return cached_stock

    @staticmethod
    def _is_stock_data_stale(cached_stock):
        """Check if stock data is stale (older than 1 hour).
        
        Args:
            cached_stock: StockCache instance
            
        Returns:
            True if data is stale, False otherwise
        """
        time_since_update = datetime.now(timezone.utc) - cached_stock.last_updated.replace(tzinfo=timezone.utc)
        return time_since_update > timedelta(hours=1)

    @staticmethod
    def get_popular_stocks(page=1, per_page=20, fetch_data=False):
        """Get all NYSE stocks with pagination.
        
        Args:
            page: Page number (1-indexed)
            per_page: Number of stocks per page
            fetch_data: If True, fetch current data for displayed stocks
            
        Returns:
            Dictionary with 'stocks', 'total', 'page', 'per_page', 'pages'
        """
        # Query all stocks from database with pagination
        stocks_query = StockCache.query\
            .order_by(StockCache.ticker)\
            .paginate(page=page, per_page=per_page, error_out=False)
        
        # Get stocks for this page
        stocks = []
        for cached_stock in stocks_query.items:
            # If fetch_data is True and data is stale, update it
            if fetch_data and StockService._is_stock_data_stale(cached_stock):
                # Update the stock data
                StockService._update_stock_cache(cached_stock.ticker)
                # Refresh the object from database
                db.session.refresh(cached_stock)
            
            stocks.append(cached_stock.to_dict())
        
        total = StockCache.query.count()
        total_pages = stocks_query.pages
        
        return {
            'stocks': stocks,
            'total': total,
            'page': page,
            'per_page': per_page,
            'pages': total_pages
        }

    @staticmethod
    def search_stocks(query, page=1, per_page=20, fetch_data=False):
        """Search stocks by ticker or company name.
        
        If no results are found in the cache, attempt to search Yahoo Finance.
        
        Args:
            query: Search query (ticker or company name)
            page: Page number (1-indexed)
            per_page: Number of stocks per page
            fetch_data: If True, fetch current data for displayed stocks
            
        Returns:
            Dictionary with 'stocks', 'total', 'page', 'per_page', 'pages'
        """
        if not query:
            return StockService.get_popular_stocks(page, per_page, fetch_data)
        
        # Search in cache by ticker or company name
        query_lower = query.lower()
        search_filter = db.or_(
            StockCache.ticker.ilike(f'%{query}%'),
            StockCache.company_name.ilike(f'%{query}%')
        )
        
        # Get total count
        total = StockCache.query.filter(search_filter).count()
        
        # If no results found in cache, try to fetch from Yahoo Finance
        if total == 0 and len(query) <= 10:
            # Attempt to fetch from Yahoo Finance
            ticker_upper = query.upper()
            stock_info = StockService._fetch_stock_info(ticker_upper)
            
            if stock_info and stock_info.get('company_name'):
                # Add to cache
                new_cache = StockCache(
                    ticker=ticker_upper,
                    company_name=stock_info.get('company_name'),
                    pe_ratio=stock_info.get('pe_ratio'),
                    price=stock_info.get('price'),
                    market_cap=stock_info.get('market_cap'),
                    is_favorite=False,
                    last_updated=datetime.now(timezone.utc)
                )
                db.session.add(new_cache)
                db.session.commit()
                
                # Return the newly added stock
                return {
                    'stocks': [new_cache.to_dict()],
                    'total': 1,
                    'page': 1,
                    'per_page': per_page,
                    'pages': 1,
                    'query': query
                }
        
        # Get paginated results
        stocks_query = StockCache.query.filter(search_filter)\
            .order_by(StockCache.ticker)\
            .paginate(page=page, per_page=per_page, error_out=False)
        
        # Get stocks and optionally fetch fresh data
        stocks = []
        for cached_stock in stocks_query.items:
            # If fetch_data is True and data is stale, update it
            if fetch_data and StockService._is_stock_data_stale(cached_stock):
                # Update the stock data
                StockService._update_stock_cache(cached_stock.ticker)
                # Refresh the object from database
                db.session.refresh(cached_stock)
            
            stocks.append(cached_stock.to_dict())
        
        total_pages = stocks_query.pages
        
        return {
            'stocks': stocks,
            'total': total,
            'page': page,
            'per_page': per_page,
            'pages': total_pages,
            'query': query
        }

    @staticmethod
    def add_stock_to_cache(ticker, company_name=None):
        """Add a stock to the cache without fetching data.
        
        This is used to populate the database with NYSE stock tickers.
        Data will be fetched on-demand when the stock is viewed.
        
        Args:
            ticker: Stock ticker symbol
            company_name: Optional company name
            
        Returns:
            True if added, False if already exists
        """
        # Check if stock already exists
        existing = StockCache.query.filter_by(ticker=ticker).first()
        if existing:
            return False
        
        # Add to cache without fetching data (lazy loading)
        new_cache = StockCache(
            ticker=ticker,
            company_name=company_name,
            pe_ratio=None,
            price=None,
            market_cap=None,
            last_updated=datetime.now(timezone.utc) - timedelta(hours=2)  # Mark as stale
        )
        db.session.add(new_cache)
        db.session.commit()
        return True

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
            timestamp=datetime.now(timezone.utc)
        )

        db.session.add(stock)
        db.session.commit()

        return stock

    @staticmethod
    def check_pe_threshold(ticker, pe_ratio, threshold):
        """Check if P/E ratio is below threshold and print alert."""
        if pe_ratio is not None and pe_ratio < threshold:
            print(
                f"  ALERT: {ticker} has a P/E ratio of {pe_ratio:.2f}, "
                f"which is below the threshold of {threshold}"
            )
            print("   This may be a good investment opportunity during hard times!")
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

    @staticmethod
    def toggle_favorite(ticker):
        """Toggle favorite status for a stock.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Dictionary with 'success' and 'is_favorite' status
        """
        # Find stock in cache
        cached_stock = StockCache.query.filter_by(ticker=ticker).first()
        
        if not cached_stock:
            return {'success': False, 'error': 'Stock not found'}
        
        # Toggle favorite status
        cached_stock.is_favorite = not cached_stock.is_favorite
        db.session.commit()
        
        return {
            'success': True,
            'is_favorite': cached_stock.is_favorite
        }

    @staticmethod
    def get_favorite_stocks():
        """Get all favorite stocks.
        
        Returns:
            List of favorite stock dictionaries
        """
        favorite_stocks = StockCache.query.filter_by(is_favorite=True)\
            .order_by(StockCache.ticker)\
            .all()
        
        return [stock.to_dict() for stock in favorite_stocks]
