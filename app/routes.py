"""Flask route handlers."""

import base64
import io
from datetime import datetime, timezone

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
from flask import current_app, jsonify, render_template, request

from app.services.stock_service import StockService


def init_app(app):
    """Register routes with the Flask app."""

    @app.route('/')
    def index():
        """Main dashboard showing all tracked stocks."""
        latest_stocks = StockService.get_latest_stocks()
        favorite_stocks = StockService.get_favorite_stocks()
        threshold = current_app.config['PE_THRESHOLD']

        return render_template(
            'index.html',
            stocks=latest_stocks,
            favorite_stocks=favorite_stocks,
            threshold=threshold,
            tracked_tickers=current_app.config['STOCKS_TO_TRACK']
        )

    @app.route('/stocks')
    def stocks():
        """Stock Explorer page showing NYSE-listed stocks with search and pagination."""
        page = request.args.get('page', 1, type=int)
        per_page = 20
        query = request.args.get('q', '').strip()
        
        # Get stocks (either search results or all stocks)
        # fetch_data=True will fetch current data for stocks on the page
        if query:
            result = StockService.search_stocks(query, page, per_page, fetch_data=True)
        else:
            result = StockService.get_popular_stocks(page, per_page, fetch_data=True)
        
        threshold = current_app.config['PE_THRESHOLD']
        
        return render_template(
            'stocks.html',
            stocks=result['stocks'],
            page=result['page'],
            per_page=result['per_page'],
            total=result['total'],
            pages=result['pages'],
            query=query,
            threshold=threshold
        )

    @app.route('/stock/<ticker>')
    def stock_detail(ticker):
        """Detail page for a specific stock showing P/E ratio over time."""
        # Validate ticker symbol (alphanumeric only, max 10 chars)
        if not ticker.isalnum() or len(ticker) > 10:
            return "Invalid ticker symbol", 400

        # Check if ticker is in our tracked list
        if ticker not in current_app.config['STOCKS_TO_TRACK']:
            return "Ticker not found", 404

        historical_data = StockService.get_historical_pe_data(ticker)
        threshold = current_app.config['PE_THRESHOLD']

        # Generate plot
        chart_data = generate_pe_chart(ticker, historical_data, threshold)

        return render_template(
            'stock_detail.html',
            ticker=ticker,
            historical_data=historical_data,
            chart_data=chart_data,
            threshold=threshold
        )

    @app.route('/update', methods=['POST'])
    def update_stocks():
        """Update stock data for all tracked tickers."""
        # Validate and sanitize threshold input
        try:
            threshold = float(
                request.form.get('threshold', current_app.config['PE_THRESHOLD'])
            )
            # Ensure threshold is within reasonable bounds
            if threshold <= 0 or threshold > 1000:
                return jsonify({
                    'success': False,
                    'message': 'Threshold must be between 0 and 1000'
                }), 400
        except (ValueError, TypeError):
            return jsonify({
                'success': False,
                'message': 'Invalid threshold value'
            }), 400

        print(f"\n{'='*60}")
        print(f"Updating stock data at {datetime.now(timezone.utc)}")
        print(f"P/E Ratio threshold: {threshold}")
        print(f"{'='*60}\n")

        results = StockService.update_all_stocks(
            current_app.config['STOCKS_TO_TRACK'],
            threshold
        )

        print(f"\n{'='*60}")
        print(f"Update complete. {len(results)} stocks updated.")
        print(f"{'='*60}\n")

        return jsonify({
            'success': True,
            'updated': len(results),
            'message': f'Successfully updated {len(results)} stocks'
        })

    @app.route('/api/stocks')
    def api_stocks():
        """API endpoint to get latest stock data."""
        latest_stocks = StockService.get_latest_stocks()
        return jsonify(latest_stocks)

    @app.route('/api/stock/<ticker>/history')
    def api_stock_history(ticker):
        """API endpoint to get historical data for a stock."""
        # Validate ticker symbol
        if not ticker.isalnum() or len(ticker) > 10:
            return jsonify({'error': 'Invalid ticker symbol'}), 400

        if ticker not in current_app.config['STOCKS_TO_TRACK']:
            return jsonify({'error': 'Ticker not found'}), 404

        limit = request.args.get('limit', 100, type=int)
        # Validate limit to prevent excessive data retrieval
        if limit < 1 or limit > 1000:
            return jsonify({'error': 'Limit must be between 1 and 1000'}), 400

        historical_data = StockService.get_historical_pe_data(ticker, limit)
        return jsonify(historical_data)

    @app.route('/api/stock/<ticker>/favorite', methods=['POST'])
    def toggle_favorite(ticker):
        """API endpoint to toggle favorite status for a stock."""
        # Validate ticker symbol
        if not ticker.isalnum() or len(ticker) > 10:
            return jsonify({'error': 'Invalid ticker symbol'}), 400

        result = StockService.toggle_favorite(ticker.upper())
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 404


def generate_pe_chart(ticker, historical_data, threshold):
    """Generate a P/E ratio chart over time."""
    if not historical_data:
        return None

    # Extract data for plotting with error handling
    dates = []
    pe_ratios = []
    for d in historical_data:
        if d['pe_ratio'] is not None and d['timestamp']:
            try:
                dates.append(datetime.fromisoformat(d['timestamp']))
                pe_ratios.append(d['pe_ratio'])
            except (ValueError, TypeError):
                # Skip invalid timestamps
                continue

    if not dates or not pe_ratios:
        return None

    # Create plot
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(dates, pe_ratios, marker='o', linestyle='-', linewidth=2, markersize=4)
    ax.axhline(y=threshold, color='r', linestyle='--', label=f'Threshold ({threshold})')

    ax.set_xlabel('Date')
    ax.set_ylabel('P/E Ratio')
    ax.set_title(f'{ticker} P/E Ratio Over Time')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Rotate x-axis labels for better readability
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Convert plot to base64 string
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
    plt.close(fig)

    return image_base64
