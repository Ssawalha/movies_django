"""
Test configuration for VS Code test discovery.
This file is automatically loaded during test discovery.
"""

import os
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = str(Path(__file__).resolve().parent.parent.parent)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Set up Django settings for test discovery
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "movie_showings.test_settings")
