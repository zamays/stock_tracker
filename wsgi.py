"""
WSGI configuration for production deployment.

This file is used to configure the application for deployment on PythonAnywhere
or other WSGI-compatible servers.
"""

import os
import sys

# Add your project directory to the sys.path
# Set via environment variable or use default
project_home = os.environ.get('STOCK_TRACKER_PATH', '/home/yourusername/stock_tracker')
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Set environment variables if needed (uncomment and configure)
# os.environ['DB_USER'] = 'your_db_user'
# os.environ['DB_PASSWORD'] = 'your_db_password'
# os.environ['DB_HOST'] = 'your_db_host'
# os.environ['DB_NAME'] = 'stock_tracker'
# os.environ['SECRET_KEY'] = 'your-production-secret-key'

# Import the Flask app using the app factory
from app import create_app

application = create_app()
