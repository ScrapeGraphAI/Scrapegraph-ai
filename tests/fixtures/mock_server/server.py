"""
Mock HTTP server for consistent testing without external dependencies.

This server provides:
- Static HTML pages with predictable content
- JSON/XML/CSV endpoints
- Rate limiting simulation
- Error condition simulation
- Dynamic content generation
"""

import json
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
from typing import Dict, Optional
from urllib.parse import parse_qs, urlparse


class MockHTTPRequestHandler(BaseHTTPRequestHandler):
    """Request handler for the mock HTTP server."""

    # Track request count for rate limiting simulation
    request_count: Dict[str, int] = {}

    def log_message(self, format, *args):
        """Suppress default logging."""
        pass

    def do_GET(self):
        """Handle GET requests."""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        query_params = parse_qs(parsed_path.query)

        # Route requests
        if path == "/":
            self._serve_home()
        elif path == "/products":
            self._serve_products()
        elif path == "/projects":
            self._serve_projects()
        elif path == "/api/data.json":
            self._serve_json_data()
        elif path == "/api/data.xml":
            self._serve_xml_data()
        elif path == "/api/data.csv":
            self._serve_csv_data()
        elif path == "/slow":
            self._serve_slow_response()
        elif path == "/error/404":
            self._serve_404()
        elif path == "/error/500":
            self._serve_500()
        elif path == "/rate-limited":
            self._serve_rate_limited()
        elif path == "/dynamic":
            self._serve_dynamic_content()
        elif path == "/pagination":
            self._serve_pagination(query_params)
        else:
            self._serve_404()

    def _serve_home(self):
        """Serve home page."""
        html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Mock Test Website</title>
        </head>
        <body>
            <h1>Welcome to Mock Test Website</h1>
            <p>This is a test website for ScrapeGraphAI testing.</p>
            <nav>
                <a href="/products">Products</a>
                <a href="/projects">Projects</a>
            </nav>
        </body>
        </html>
        """
        self._send_html_response(html)

    def _serve_products(self):
        """Serve products page."""
        html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Products</title>
        </head>
        <body>
            <h1>Our Products</h1>
            <div class="products">
                <article class="product" data-id="1">
                    <h2 class="product-name">Product Alpha</h2>
                    <p class="product-description">High-quality product for testing</p>
                    <span class="product-price">$99.99</span>
                    <span class="product-stock">In Stock</span>
                </article>
                <article class="product" data-id="2">
                    <h2 class="product-name">Product Beta</h2>
                    <p class="product-description">Another great product</p>
                    <span class="product-price">$149.99</span>
                    <span class="product-stock">Limited Stock</span>
                </article>
                <article class="product" data-id="3">
                    <h2 class="product-name">Product Gamma</h2>
                    <p class="product-description">Premium product option</p>
                    <span class="product-price">$199.99</span>
                    <span class="product-stock">Out of Stock</span>
                </article>
            </div>
        </body>
        </html>
        """
        self._send_html_response(html)

    def _serve_projects(self):
        """Serve projects page."""
        html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Projects</title>
        </head>
        <body>
            <h1>Our Projects</h1>
            <div class="projects">
                <article class="project">
                    <h2>Project Alpha</h2>
                    <p class="description">A comprehensive web scraping solution</p>
                    <a href="https://github.com/example/alpha">GitHub</a>
                </article>
                <article class="project">
                    <h2>Project Beta</h2>
                    <p class="description">AI-powered data extraction tool</p>
                    <a href="https://github.com/example/beta">GitHub</a>
                </article>
            </div>
        </body>
        </html>
        """
        self._send_html_response(html)

    def _serve_json_data(self):
        """Serve JSON endpoint."""
        data = {
            "company": "Test Company",
            "description": "A mock company for testing",
            "employees": [
                {"name": "Alice", "role": "Engineer", "department": "Engineering"},
                {"name": "Bob", "role": "Designer", "department": "Design"},
                {"name": "Charlie", "role": "Manager", "department": "Operations"},
            ],
            "founded": "2020",
            "location": "San Francisco",
        }
        self._send_json_response(data)

    def _serve_xml_data(self):
        """Serve XML endpoint."""
        xml = """<?xml version="1.0" encoding="UTF-8"?>
        <company>
            <name>Test Company</name>
            <description>A mock company for testing</description>
            <employees>
                <employee>
                    <name>Alice</name>
                    <role>Engineer</role>
                </employee>
                <employee>
                    <name>Bob</name>
                    <role>Designer</role>
                </employee>
            </employees>
        </company>
        """
        self._send_xml_response(xml)

    def _serve_csv_data(self):
        """Serve CSV endpoint."""
        csv = """name,role,department
Alice,Engineer,Engineering
Bob,Designer,Design
Charlie,Manager,Operations"""
        self._send_csv_response(csv)

    def _serve_slow_response(self):
        """Simulate a slow response."""
        time.sleep(2)  # 2 second delay
        self._send_html_response("<html><body><h1>Slow Response</h1></body></html>")

    def _serve_404(self):
        """Serve 404 error."""
        self.send_response(404)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"<html><body><h1>404 Not Found</h1></body></html>")

    def _serve_500(self):
        """Serve 500 error."""
        self.send_response(500)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"<html><body><h1>500 Internal Server Error</h1></body></html>")

    def _serve_rate_limited(self):
        """Simulate rate limiting."""
        client_ip = self.client_address[0]
        self.request_count[client_ip] = self.request_count.get(client_ip, 0) + 1

        if self.request_count[client_ip] > 5:
            self.send_response(429)
            self.send_header("Content-type", "text/html")
            self.send_header("Retry-After", "60")
            self.end_headers()
            self.wfile.write(b"<html><body><h1>429 Too Many Requests</h1></body></html>")
        else:
            self._send_html_response("<html><body><h1>Rate Limited Endpoint</h1></body></html>")

    def _serve_dynamic_content(self):
        """Serve dynamically generated content."""
        timestamp = int(time.time())
        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Dynamic Content</title>
        </head>
        <body>
            <h1>Dynamic Content</h1>
            <p class="timestamp">Generated at: {timestamp}</p>
            <p class="random-data">Random value: {timestamp % 1000}</p>
        </body>
        </html>
        """
        self._send_html_response(html)

    def _serve_pagination(self, query_params):
        """Serve paginated content."""
        page = int(query_params.get("page", ["1"])[0])
        per_page = 10
        total_items = 50

        items = []
        start = (page - 1) * per_page
        end = min(start + per_page, total_items)

        for i in range(start, end):
            items.append(f'<li class="item">Item {i + 1}</li>')

        next_page = page + 1 if end < total_items else None
        prev_page = page - 1 if page > 1 else None

        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Pagination - Page {page}</title>
        </head>
        <body>
            <h1>Paginated Content - Page {page}</h1>
            <ul class="items">
                {''.join(items)}
            </ul>
            <nav class="pagination">
                {f'<a href="/pagination?page={prev_page}">Previous</a>' if prev_page else ''}
                <span>Page {page}</span>
                {f'<a href="/pagination?page={next_page}">Next</a>' if next_page else ''}
            </nav>
        </body>
        </html>
        """
        self._send_html_response(html)

    def _send_html_response(self, html: str, status: int = 200):
        """Send HTML response."""
        self.send_response(status)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))

    def _send_json_response(self, data: dict, status: int = 200):
        """Send JSON response."""
        self.send_response(status)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode("utf-8"))

    def _send_xml_response(self, xml: str, status: int = 200):
        """Send XML response."""
        self.send_response(status)
        self.send_header("Content-type", "application/xml")
        self.end_headers()
        self.wfile.write(xml.encode("utf-8"))

    def _send_csv_response(self, csv: str, status: int = 200):
        """Send CSV response."""
        self.send_response(status)
        self.send_header("Content-type", "text/csv")
        self.end_headers()
        self.wfile.write(csv.encode("utf-8"))


class MockHTTPServer:
    """Mock HTTP server for testing."""

    def __init__(self, host: str = "localhost", port: int = 8888):
        self.host = host
        self.port = port
        self.server: Optional[HTTPServer] = None
        self.thread: Optional[Thread] = None

    def start(self):
        """Start the mock server in a background thread."""
        self.server = HTTPServer((self.host, self.port), MockHTTPRequestHandler)
        self.thread = Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        time.sleep(0.1)  # Give server time to start

    def stop(self):
        """Stop the mock server."""
        if self.server:
            self.server.shutdown()
            self.server.server_close()
        if self.thread:
            self.thread.join(timeout=1)

    def get_url(self, path: str = "") -> str:
        """Get full URL for a given path."""
        return f"http://{self.host}:{self.port}{path}"

    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()
