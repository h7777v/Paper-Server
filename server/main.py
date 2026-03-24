from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import os
import render

products = {
    "normal ball" : 1, 
    "small ball" : 0.5, 
    "custom ball" : 1.5
}

import os

def openDB(loc, mode, content="", main=True):  
    if main:  
        if mode in ("read", "readline", "readlineback"):
            m = "rt"
        elif mode == "write":
            m = "wt"
        elif mode == "append":
            m = "at"
        else:
            return

        path = f"../data/primary/{loc}"

        if mode == "read":
            with open(path, m) as f:
                return f.read()
        if mode == "readline":
            f = open(path, m)
            return (f.readline, f.close)
        if mode == "readlineback":
            def reverse_reader():
                with open(path, "rb") as f:
                    f.seek(0, os.SEEK_END)
                    pos = f.tell()
                    buffer = b""

                    while pos > 0:
                        read_size = min(4096, pos)
                        pos -= read_size
                        f.seek(pos)
                        block = f.read(read_size)
                        buffer = block + buffer
                        *lines, buffer = buffer.split(b"\n")

                        for line in reversed(lines):
                            yield line.decode("utf-8", errors="replace")

                    if buffer:
                        yield buffer.decode("utf-8", errors="replace")

            return reverse_reader()

        if mode == "write":
            with open(path, m) as f:
                f.write(content)
            return

        if mode == "append":
            with open(path, m) as f:
                f.write(content)
            return
        return
    elif not main:
        if mode in ("read", "readline", "readlineback"):
            m = "rt"
        elif mode == "write":
            m = "wt"
        elif mode == "append":
            m = "at"
        else:
            return

        path = f"../data/secondary/{loc}"

        if mode == "read":
            with open(path, m) as f:
                return f.read()
        if mode == "readline":
            f = open(path, m)
            return (f.readline, f.close)
        if mode == "readlineback":
            def reverse_reader():
                with open(path, "rb") as f:
                    f.seek(0, os.SEEK_END)
                    pos = f.tell()
                    buffer = b""

                    while pos > 0:
                        read_size = min(4096, pos)
                        pos -= read_size
                        f.seek(pos)
                        block = f.read(read_size)
                        buffer = block + buffer
                        *lines, buffer = buffer.split(b"\n")

                        for line in reversed(lines):
                            yield line.decode("utf-8", errors="replace")

                    if buffer:
                        yield buffer.decode("utf-8", errors="replace")

            return reverse_reader()

        if mode == "write":
            with open(path, m) as f:
                f.write(content)
            return

        if mode == "append":
            with open(path, m) as f:
                f.write(content)
            return

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path.lstrip("/")
        query = parsed.query

        if path.endswith(".html"):
            mime = "text/html"
        elif path.endswith(".js"):
            mime = "application/javascript"
        elif path.endswith(".css"):
            mime = "text/css"
        else:
            mime = "text/plain"

        if(path == ""):
            file = open("./_site/pages/success.html", "rb")
            content = file.read()
            file.close()
            mime = "text/html"
        else:
            if not os.path.exists(f"_site/{path}"):
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"Not found")
                return
            with open(f"_site/{path}", "rb") as f:
                content = f.read()
        
        self.send_response(200)
        self.send_header("Content-Type", mime)
        self.end_headers()
        self.wfile.write(content)

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)

        def get_reject():
            with open("./_site/pages/reject.html", "rt") as f:
                return f.read()
        
        def send_html(status, content, self):
            self.send_response(status)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(content)

        raw = body.decode("utf-8", errors="replace")

        if("\uFFFD" in raw):
            send_html(400, 
                render.render(get_reject(), {
                    "status" : 400, 
                    "reason" : "Request was invalid or malformed", 
                    "details" : "Invalid encoding. "
                }).encode("utf-8", "ignore"), 
                self
            )
            return

        data = parse_qs(body)

        for _, values in data.items():
            if len(values) != 1:
                send_html(400, 
                    render.render(get_reject(), {
                        "status" : 400, 
                        "reason" : "Request was invalid or malformed", 
                        "details" : "Multiple values not allowed. "
                    }).encode("utf-8", "ignore"), 
                    self
                )
                return
            
        data = {k: v[0] for k, v in data.items()}

        if "type" not in data.keys():
            send_html(400, 
                render.render(get_reject(), {
                    "status" : 400, 
                    "reason" : "Request was invalid or malformed", 
                    "details" : "Product type was missing. "
                }).encode("utf-8", "ignore"), 
                self
            )
            return
        
        if(data.get("type") not in products.keys()):
            send_html(400, 
                render.render(get_reject(), {
                    "status" : 400, 
                    "reason" : "Request was invalid or malformed", 
                    "details" : f"No product named \"{data.get("type")}\". "
                }).encode("utf-8", "ignore"), 
                self
            )
            return
        
        

        with open("./_site/pages/success.html", "rt") as f:
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()

            self.wfile.write(
                render.render(
                    f.read(), 
                    {
                        "product" : f"{data.get("type")}", 
                        "price" : f"${float(products.get(data.get("type"))):.2f}"
                    }
                ).encode("utf-8", "ingore")
            )

if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", 6060), Handler)
    print("Server running on port 6060")
    server.serve_forever()
