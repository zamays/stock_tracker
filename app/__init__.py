"""Flask application factory."""

import os

from flask import Flask

from app.config import Config
from app.models import db


def create_app(config_class=Config):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize database
    db.init_app(app)

    with app.app_context():
        db.create_all()

    # Register routes
    from app import routes
    routes.init_app(app)

    return app
