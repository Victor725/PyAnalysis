from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn

# ----------------------------
# 自定义多线程 HTTPServer
# ----------------------------
class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """支持多线程的 HTTPServer"""
    def __init__(self, server_address, RequestHandlerClass, config=None):
        super().__init__(server_address, RequestHandlerClass)
        self.config = config or {}  # 可以在 Handler 中访问

# ----------------------------
# Handler 定义
# ----------------------------
ROUTES = {}

def route(path):
    """路由装饰器"""
    def decorator(func):
        ROUTES[path] = func
        return func
    return decorator

@route("/hello")
def hello(handler):
    handler.send_response(200)
    handler.end_headers()
    handler.wfile.write(b"Hello World")

@route("/config")
def show_config(handler):
    handler.send_response(200)
    handler.end_headers()
    # 通过 handler.server 访问 HTTPServer 的配置
    config_text = str(handler.server.config)
    handler.wfile.write(config_text.encode())

class MyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        func = ROUTES.get(self.path)
        if func:
            func(self)
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")

# ----------------------------
# 启动服务器
# ----------------------------
if __name__ == "__main__":
    config = {"debug": True, "version": "1.0"}
    server = ThreadedHTTPServer(("localhost", 8000), MyHandler, config=config)
    print("Server running on http://localhost:8000")
    server.serve_forever()
