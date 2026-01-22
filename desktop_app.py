# Windows Desktop Application Launcher
# This replaces server.py as the main entry point for the desktop app

import sys
import os
import webbrowser
import threading
import time
from pathlib import Path

# Fix paths for PyInstaller
def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Set working directory to resource path
os.chdir(os.path.dirname(resource_path('.')))

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import uvicorn
from server import app

def open_browser():
    """Open browser after server starts"""
    time.sleep(2)  # Wait for server to start
    webbrowser.open('http://localhost:8000')

import traceback

def main():
    try:
        print("=" * 60)
        print("🎯 CrowdSense - Face Detection System")
        print("=" * 60)
        print(f"\n📁 Working directory: {os.getcwd()}")
        print(f"📁 Resource path: {resource_path('.')}")
        
        # Check files existence
        required_files = ['best.pt', 'config.yaml']
        for f in required_files:
            path = resource_path(f)
            if os.path.exists(path):
                print(f"✅ Found {f}")
            else:
                print(f"❌ MISSING {f} at {path}")
        
        print("\n✅ Starting server on http://localhost:8000")
        print("🌐 Browser will open automatically...")
        print("\n⚠️  Press CTRL+C to stop the server\n")
        
        # Open browser in background thread
        browser_thread = threading.Thread(target=open_browser, daemon=True)
        browser_thread.start()
        
        # Start server
        uvicorn.run(
            app,
            host="127.0.0.1",
            port=8000,
            log_level="info"
        )
        
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down CrowdSense...")
    except Exception as e:
        print("\n\n❌ CRITICAL ERROR:")
        print("=" * 60)
        traceback.print_exc()
        print("=" * 60)
    finally:
        input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
