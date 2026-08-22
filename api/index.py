import os
import sys

# Add project root directory to Python module search path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app import app

# Vercel WSGI Handler Export
app = app
