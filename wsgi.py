"""
WSGI configuration for PythonAnywhere deployment.

This file is used to configure the application for deployment on PythonAnywhere.
Update the path in the sys.path.insert line to match your actual directory.
"""
import sys
import os

# Add your project directory to the sys.path
# IMPORTANT: Update this path to match your PythonAnywhere directory
project_home = '/home/yourusername/stock_tracker'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Set environment variables if needed
# os.environ['DB_USER'] = 'your_db_user'
# os.environ['DB_PASSWORD'] = 'your_db_password'
# os.environ['DB_HOST'] = 'your_db_host'
# os.environ['DB_NAME'] = 'stock_tracker'

# Import the Flask app
from app import app as application
