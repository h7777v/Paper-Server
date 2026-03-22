from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs

products = ["normal", "small", "custom"]

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()

        self.wfile.write(b"GET OK")

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)

        raw = body.decode("utf-8", errors="replace")

        if("\uFFFD" in raw):
            #reject 400 malformed, invalid decoding
            pass

        data = parse_qs(raw)

        for _, values in data.items():
            if len(values) != 1:
                self.send_error(400, "Multiple values not allowed")
                return
            
        data = {k: v[0] for k, v in data.items()}

        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()

        self.wfile.write(b"POST OK")

if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", 6060), Handler)
    print("Server running on port 6060")
    server.serve_forever()
