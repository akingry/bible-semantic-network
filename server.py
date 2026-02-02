"""
Simple HTTP server to serve the Bible network visualization.
"""

import http.server
import socketserver
import webbrowser
import os
import socket
from pathlib import Path

PORT = 8080
DIRECTORY = Path(__file__).parent

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIRECTORY), **kwargs)

def find_open_port(start=8080, end=8100):
    """Find an available port."""
    for port in range(start, end):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', port))
                return port
        except OSError:
            continue
    return None

def main():
    os.chdir(DIRECTORY)
    
    # Check if network_data.json exists
    if not (DIRECTORY / "network_data.json").exists():
        print("network_data.json not found. Building network...")
        import build_network
        build_network.main()
        print()
    
    # Find available port
    port = find_open_port(PORT)
    if port is None:
        print("Error: No available ports found (8080-8100)")
        return
    
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", port), Handler) as httpd:
        url = f"http://localhost:{port}/visualization.html"
        print(f"=" * 50)
        print(f"Bible Keywords Network Visualization")
        print(f"=" * 50)
        print(f"Server running at: http://localhost:{port}")
        print(f"Opening browser...")
        print(f"Press Ctrl+C to stop")
        print(f"=" * 50)
        
        webbrowser.open(url)
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")

if __name__ == "__main__":
    main()
