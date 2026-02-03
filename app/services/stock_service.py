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
    def get_popular_stocks(page=1, per_page=20):
        """Get popular NYSE stocks with pagination.
        
        Args:
            page: Page number (1-indexed)
            per_page: Number of stocks per page
            
        Returns:
            Dictionary with 'stocks', 'total', 'page', 'per_page', 'pages'
        """
        # Ensure all popular stocks are in cache
        StockService._ensure_popular_stocks_cached()
        
        # Get tickers for this page
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        page_stocks = StockService.POPULAR_NYSE_STOCKS[start_idx:end_idx]
        
        # Get cached data for these stocks
        stocks = []
        for stock_info in page_stocks:
            cached = StockCache.query.filter_by(ticker=stock_info['ticker']).first()
            if cached:
                stocks.append(cached.to_dict())
        
        total = len(StockService.POPULAR_NYSE_STOCKS)
        total_pages = (total + per_page - 1) // per_page
        
        return {
            'stocks': stocks,
            'total': total,
            'page': page,
            'per_page': per_page,
            'pages': total_pages
        }

    @staticmethod
    def search_stocks(query, page=1, per_page=20):
        """Search stocks by ticker or company name.
        
        Args:
            query: Search query (ticker or company name)
            page: Page number (1-indexed)
            per_page: Number of stocks per page
            
        Returns:
            Dictionary with 'stocks', 'total', 'page', 'per_page', 'pages'
        """
        if not query:
            return StockService.get_popular_stocks(page, per_page)
        
        # Ensure stocks are cached
        StockService._ensure_popular_stocks_cached()
        
        # Search in cache by ticker or company name
        query_lower = query.lower()
        search_filter = db.or_(
            StockCache.ticker.ilike(f'%{query}%'),
            StockCache.company_name.ilike(f'%{query}%')
        )
        
        # Get total count
        total = StockCache.query.filter(search_filter).count()
        
        # Get paginated results
        stocks_query = StockCache.query.filter(search_filter)\
            .order_by(StockCache.ticker)\
            .paginate(page=page, per_page=per_page, error_out=False)
        
        stocks = [stock.to_dict() for stock in stocks_query.items]
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
    def _ensure_popular_stocks_cached():
        """Ensure all popular stocks are in cache (only adds missing ones)."""
        for stock_info in StockService.POPULAR_NYSE_STOCKS:
            ticker = stock_info['ticker']
            cached = StockCache.query.filter_by(ticker=ticker).first()
            
            if not cached:
                # Add to cache without fetching yet (lazy loading)
                new_cache = StockCache(
                    ticker=ticker,
                    company_name=stock_info['name'],
                    pe_ratio=None,
                    price=None,
                    market_cap=None,
                    last_updated=datetime.now(timezone.utc) - timedelta(hours=2)  # Mark as stale
                )
                db.session.add(new_cache)
        
        db.session.commit()

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
