#!/usr/bin/env python3
"""
DIC Analyzer System Launcher
Launches HTTP server for frontend files
"""

import http.server
import socketserver
import os
import sys
from pathlib import Path

def main():
    # Set the port for the HTTP server
    PORT = 8080

    # Get the directory where this script is located (project root)
    web_dir = Path(__file__).parent

    # Change to the web directory
    os.chdir(web_dir)

    # Create a custom handler to serve files with proper MIME types
    class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
        def end_headers(self):
            # Add CORS headers for development
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            super().end_headers()

        def log_message(self, format, *args):
            # Custom logging with timestamp
            import datetime
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f'[{timestamp}] {format % args}')

    try:
        with socketserver.TCPServer(("", PORT), CustomHTTPRequestHandler) as httpd:
            print("=" * 50)
            print("    DIC Analyzer - HTTP Frontend Server")
            print("=" * 50)
            print(f"Serving files from: {web_dir}")
            print(f"Server running at: http://localhost:{PORT}")
            print("Main application: http://localhost:8080/working_app.html")
            print("=" * 50)
            print("Press Ctrl+C to stop the server")
            print()

            httpd.serve_forever()

    except KeyboardInterrupt:
        print("\nServer stopped by user")
        sys.exit(0)
    except OSError as e:
        if e.errno == 48:  # Address already in use
            print(f"ERROR: Port {PORT} is already in use.")
            print("Please close other applications using this port or change the port in run_system.py")
        else:
            print(f"ERROR: Failed to start server: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
