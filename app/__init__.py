"""Flask application factory."""

import os

from flask import Flask

from app.config import Config
from app.models import db


def create_app(config_class=Config):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Ensure instance directory exists for SQLite databases
    os.makedirs(app.instance_path, exist_ok=True)

    # Initialize database
    db.init_app(app)

    with app.app_context():
        db.create_all()
        from app.services.stock_service import StockService
        added = StockService.populate_nyse_cache_from_csv()
        if added:
            app.logger.info("Populated %s NYSE tickers into stock cache", added)

    # Register routes
    from app import routes
    routes.init_app(app)

    return app
