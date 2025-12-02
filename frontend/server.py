"""
Simple HTTP server for frontend development.
Serves static files on port 8000.
"""
import http.server
import socketserver
import os

PORT = 8000

# Change to frontend directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Create a custom handler class to allow address reuse
class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True

# Create handler
Handler = http.server.SimpleHTTPRequestHandler

# Start server
with ReusableTCPServer(("", PORT), Handler) as httpd:
    print(f"Frontend server running at http://localhost:{PORT}/")
    print(f"Serving files from: {os.getcwd()}")
    print("Press Ctrl+C to stop the server")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
