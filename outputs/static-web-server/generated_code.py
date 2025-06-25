import http.server
import socketserver
import os
import logging
import argparse
import mimetypes
from threading import Thread
from http import HTTPStatus

class StaticFileRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Custom request handler for serving static files with proper MIME types."""

    def __init__(self, *args, **kwargs):
        self.directory = kwargs.pop('directory', None)
        super().__init__(*args, directory=self.directory, **kwargs)

    def guess_type(self, path):
        """Override to provide better MIME type detection."""
        base, ext = os.path.splitext(path)
        if ext in mimetypes.types_map:
            return mimetypes.types_map[ext]
        return 'application/octet-stream'

    def do_GET(self):
        """Handle GET requests with proper error handling."""
        try:
            # Validate path to prevent directory traversal
            if not self.is_valid_path(self.path):
                self.send_error(HTTPStatus.FORBIDDEN, "Invalid path")
                return

            # Serve the file
            super().do_GET()
        except Exception as e:
            logging.error(f"Error serving {self.path}: {str(e)}")
            self.send_error(HTTPStatus.INTERNAL_SERVER_ERROR, "Server error")

    def is_valid_path(self, path):
        """Validate the requested path to prevent directory traversal."""
        # Normalize the path
        path = os.path.normpath(path)
        if path.startswith('/'):
            path = path[1:]

        # Check for path traversal attempts
        if '..' in path.split(os.sep):
            return False

        # Check if path is within the root directory
        full_path = os.path.join(self.directory, path)
        return os.path.abspath(full_path).startswith(os.path.abspath(self.directory))

    def log_message(self, format, *args):
        """Override to customize logging format."""
        logging.info("%s - - [%s] %s" % (
            self.address_string(),
            self.log_date_time_string(),
            format % args
        ))

class StaticFileHTTPServer:
    """Main server class that handles configuration and server lifecycle."""

    def __init__(self, host='localhost', port=8000, directory='public'):
        self.host = host
        self.port = port
        self.directory = directory
        self.server = None
        self.thread = None

    def start(self):
        """Start the HTTP server in a separate thread."""
        try:
            # Create custom handler with directory
            handler = lambda *args, **kwargs: StaticFileRequestHandler(
                *args, directory=self.directory, **kwargs
            )

            # Create and start the server
            with socketserver.ThreadingTCPServer((self.host, self.port), handler) as httpd:
                self.server = httpd
                logging.info(f"Serving files from {self.directory} on {self.host}:{self.port}")

                # Start server in a separate thread
                self.thread = Thread(target=httpd.serve_forever)
                self.thread.daemon = True
                self.thread.start()

                return True
        except Exception as e:
            logging.error(f"Failed to start server: {str(e)}")
            return False

    def stop(self):
        """Stop the HTTP server."""
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            logging.info("Server stopped")
            if self.thread:
                self.thread.join()
        else:
            logging.warning("Server not running")

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Static File Web Server')
    parser.add_argument('--port', type=int, default=8000,
                       help='Port number to listen on (default: 8000)')
    parser.add_argument('--directory', default='public',
                       help='Directory to serve files from (default: public)')
    parser.add_argument('--host', default='localhost',
                       help='Host address to bind to (default: localhost)')
    return parser.parse_args()

def setup_logging():
    """Configure logging format and level."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def main():
    """Main entry point for the application."""
    setup_logging()
    args = parse_arguments()

    # Validate directory exists
    if not os.path.isdir(args.directory):
        logging.error(f"Directory '{args.directory}' does not exist")
        return

    server = StaticFileHTTPServer(
        host=args.host,
        port=args.port,
        directory=args.directory
    )

    try:
        if server.start():
            logging.info("Server started. Press Ctrl+C to stop.")
            # Keep the main thread alive
            while True:
                pass
    except KeyboardInterrupt:
        logging.info("Shutting down server...")
    finally:
        server.stop()

if __name__ == '__main__':
    main()