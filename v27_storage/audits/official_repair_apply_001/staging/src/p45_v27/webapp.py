"""Minimal read-only HTTP server for P45 web integration v1."""
from __future__ import annotations
import argparse, json, mimetypes, socket
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse
from .web_adapter import FrozenWebAdapter

PROJECT_ROOT=Path(__file__).resolve().parents[2]; WEB_ROOT=PROJECT_ROOT/"web"; ADAPTER=FrozenWebAdapter(PROJECT_ROOT)

class Handler(BaseHTTPRequestHandler):
    server_version="P45-Web/1.0"
    def _json(self,value:object,status:int=200)->None:
        body=json.dumps(value,ensure_ascii=False,separators=(",",":")).encode("utf-8");self.send_response(status)
        self.send_header("Content-Type","application/json; charset=utf-8");self.send_header("Content-Length",str(len(body)))
        self.send_header("Cache-Control","no-store");self.send_header("X-Content-Type-Options","nosniff");self.end_headers();self.wfile.write(body)
    def do_GET(self)->None:
        path=urlparse(self.path).path
        if path=="/api/status":
            try:self._json(ADAPTER.read())
            except Exception as exc:self._json({"error":str(exc),"official_final_numbers":[]},409)
            return
        relative="index.html" if path in ("","/") else path.lstrip("/");target=(WEB_ROOT/relative).resolve()
        try:target.relative_to(WEB_ROOT.resolve())
        except ValueError:self.send_error(HTTPStatus.NOT_FOUND);return
        if not target.is_file():self.send_error(HTTPStatus.NOT_FOUND);return
        body=target.read_bytes();content_type=mimetypes.guess_type(target.name)[0] or "application/octet-stream";self.send_response(200)
        self.send_header("Content-Type",content_type+("; charset=utf-8" if content_type.startswith(("text/","application/javascript")) else ""))
        self.send_header("Content-Length",str(len(body)));self.send_header("Cache-Control","no-store, max-age=0");self.send_header("Pragma","no-cache");self.send_header("Expires","0");self.send_header("X-Content-Type-Options","nosniff");self.end_headers();self.wfile.write(body)
    def do_POST(self)->None:self._json({"error":"READ_ONLY_WEB"},405)
    def log_message(self,format:str,*args:object)->None:return

class ExclusiveThreadingHTTPServer(ThreadingHTTPServer):
    """Prevent two P45 processes from sharing the same Windows port."""
    allow_reuse_address=False
    def server_bind(self)->None:
        if hasattr(socket,"SO_EXCLUSIVEADDRUSE"):
            self.socket.setsockopt(socket.SOL_SOCKET,socket.SO_EXCLUSIVEADDRUSE,1)
        super().server_bind()

def serve(host:str="127.0.0.1",port:int=8045)->None:
    server=ExclusiveThreadingHTTPServer((host,port),Handler);print(f"P45 WEB V1: http://{host}:{port}")
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:server.server_close()
def main(argv:list[str]|None=None)->int:
    parser=argparse.ArgumentParser(description="P45 frozen read-only web");parser.add_argument("--host",default="127.0.0.1");parser.add_argument("--port",type=int,default=8045);args=parser.parse_args(argv);serve(args.host,args.port);return 0
if __name__=="__main__":raise SystemExit(main())
