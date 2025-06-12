#!/usr/bin/env python3
"""
Simple script to run the web interface.
"""

import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from web_app import app
    print("Starting SimpleSubCipher Web Interface...")
    print("Open your browser and go to: http://localhost:5000")
    print("Press Ctrl+C to stop the server")
    print("-" * 50)
    
    # Run without debug mode to avoid issues
    app.run(host='127.0.0.1', port=5000, debug=False)
    
except Exception as e:
    print(f"Error starting server: {e}")
    import traceback
    traceback.print_exc()