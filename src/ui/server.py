"""
TchaDomains Tactical HUD Server
Lightweight, zero-bloat HTTP API & Web Dashboard server on port 5520.
"""

import json
import mimetypes
from datetime import date
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse, parse_qs

from src.db.storage import DomainStore

PORT = 5520
PUBLIC_DIR = Path("src/ui/public")

class TacticalHUDHandler(BaseHTTPRequestHandler):
    store = None

    @classmethod
    def get_store(cls):
        if cls.store is None:
            cls.store = DomainStore()
        return cls.store

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        if path == "/api/drops":
            self.handle_get_drops(query)
        elif path == "/api/stats":
            self.handle_get_stats()
        elif path == "/api/watchlist":
            self.handle_get_watchlist()
        else:
            self.serve_static(path)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/api/watchlist":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")
            data = json.loads(body) if body else {}
            domain = data.get("domain_name")
            notes = data.get("notes", "")
            max_bid = float(data.get("max_bid", 50.0))

            if domain:
                self.get_store().add_to_watchlist(domain, notes=notes, max_bid=max_bid)
                self.send_json({"status": "success", "domain": domain})
            else:
                self.send_json({"error": "domain_name required"}, status=400)
        else:
            self.send_error(404, "Endpoint not found")

    def handle_get_drops(self, query):
        limit = int(query.get("limit", [50])[0])
        min_score = float(query.get("min_score", [70.0])[0])
        max_len = int(query.get("max_len", [10])[0])
        category = query.get("category", ["all"])[0]

        drops = self.get_store().query_top_alpha(
            limit=limit,
            min_score=min_score,
            max_length=max_len,
            category=category
        )
        self.send_json({"count": len(drops), "domains": drops})

    def handle_get_stats(self):
        store = self.get_store()
        try:
            total_count = store.conn.execute("SELECT COUNT(*) FROM dropping_domains").fetchone()[0]
            gems_count = store.conn.execute("SELECT COUNT(*) FROM dropping_domains WHERE alpha_score >= 80").fetchone()[0]
            avg_score = store.conn.execute("SELECT AVG(alpha_score) FROM dropping_domains").fetchone()[0] or 0.0
            categories = store.conn.execute("SELECT primary_category, COUNT(*) FROM dropping_domains GROUP BY primary_category").fetchall()
            cat_dict = {cat: count for cat, count in categories}
        except Exception:
            total_count, gems_count, avg_score, cat_dict = 0, 0, 0.0, {}

        self.send_json({
            "total_dropping": total_count,
            "alpha_gems": gems_count,
            "avg_alpha_score": round(avg_score, 1),
            "categories": cat_dict,
            "cycle_date": str(date.today())
        })

    def handle_get_watchlist(self):
        watchlist = self.get_store().get_watchlist()
        self.send_json({"count": len(watchlist), "watchlist": watchlist})

    def serve_static(self, path):
        if path in ("/", ""):
            path = "/index.html"

        file_path = PUBLIC_DIR / path.lstrip("/")
        if not file_path.exists() or not file_path.is_file():
            self.send_error(404, f"File {path} not found")
            return

        mime_type, _ = mimetypes.guess_type(str(file_path))
        mime_type = mime_type or "application/octet-stream"

        try:
            with open(file_path, "rb") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", mime_type)
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        except Exception as e:
            self.send_error(500, f"Error reading file: {e}")

    def send_json(self, data, status=200):
        body = json.dumps(data, default=str).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        # Clean logging
        return

def start_server(port=PORT):
    server_address = ("", port)
    httpd = HTTPServer(server_address, TacticalHUDHandler)
    print(f">> TchaDomains Tactical HUD running at http://localhost:{port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n>> Shutting down TchaDomains HUD server.")
        httpd.server_close()

if __name__ == "__main__":
    start_server()
