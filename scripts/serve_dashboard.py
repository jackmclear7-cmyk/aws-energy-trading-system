#!/usr/bin/env python3
"""
Serve the Energy Trading Dashboard

This script serves the frontend dashboard with a simple HTTP server.
"""

import http.server
import socketserver
import os
import sys
from pathlib import Path

def serve_dashboard(port=8080):
    """Serve the dashboard on the specified port"""
    
    # Change to the project root directory
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    # Set up the server
    handler = http.server.SimpleHTTPRequestHandler
    
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"🚀 Energy Trading Dashboard Server")
        print(f"📊 Serving on: http://localhost:{port}")
        print(f"📁 Directory: {project_root}")
        print(f"🌐 Dashboard: http://localhost:{port}/frontend/")
        print(f"⏹️  Press Ctrl+C to stop")
        print("=" * 50)
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print(f"\n🛑 Server stopped")
            httpd.shutdown()

def main():
    """Main function"""
    port = 8080
    
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print("❌ Invalid port number. Using default port 8080.")
    
    serve_dashboard(port)

if __name__ == "__main__":
    main()
