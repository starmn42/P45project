"""P45 TRIO ORBIT Prospective Web V1 on the existing standard HTTP server."""
from __future__ import annotations
import argparse, json, mimetypes, secrets, socket, threading, time
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse
from .web_adapter import FrozenWebAdapter
from .draw_update import run_update

PROJECT_ROOT=Path(__file__).resolve().parents[2]; WEB_ROOT=PROJECT_ROOT/"web"; ADAPTER=FrozenWebAdapter(PROJECT_ROOT)
API_TOKEN=secrets.token_urlsafe(32)

class AutoUpdateCoordinator:
    def __init__(self, adapter:FrozenWebAdapter, update=run_update, interval:int=300)->None:
        self.adapter=adapter;self.update=update;self.interval=interval;self.lock=threading.Lock();self.stop=threading.Event()
        self.state={"status":"대기","last_check":None,"last_error":None,"steps":[]}
    def run_once(self)->dict:
        if not self.lock.acquire(blocking=False):return self.state
        try:
            steps=[];updated=self.update();steps.append(updated.get("status","UNKNOWN"))
            status=self.adapter.read()
            if status["current"]["action"]=="RECORD_OUTCOME":
                self.adapter.service.record_outcome(status["current"]["target"]);steps.append("SETTLED")
                status=self.adapter.read()
            if status["current"]["action"]=="PREVIEW_AND_SEAL_NEXT":
                preview=self.adapter.service.preview_next();self.adapter.service.seal_next(preview["preview_sha256"]);steps.append("NEXT_SEALED")
            self.state={"status":"자동 업데이트 반영","last_check":time.time(),"last_error":None,"steps":steps}
        except Exception as exc:
            self.state={"status":"자동 업데이트 오류","last_check":time.time(),"last_error":f"{type(exc).__name__}: {exc}","steps":[]}
        finally:self.lock.release()
        return self.state
    def loop(self)->None:
        while not self.stop.is_set():self.run_once();self.stop.wait(self.interval)

AUTO=AutoUpdateCoordinator(ADAPTER)

class Handler(BaseHTTPRequestHandler):
    server_version="P45-Web-V1/1.0"
    def _json(self,value:object,status:int=200)->None:
        body=json.dumps(value,ensure_ascii=False,separators=(",",":")).encode("utf-8");self.send_response(status)
        self.send_header("Content-Type","application/json; charset=utf-8");self.send_header("Content-Length",str(len(body)))
        self.send_header("Cache-Control","no-store");self.send_header("X-Content-Type-Options","nosniff");self.send_header("Content-Security-Policy","default-src 'self'; style-src 'self'; script-src 'self'; img-src 'self' data:; connect-src 'self'");self.end_headers();self.wfile.write(body)
    def _body(self)->dict:
        length=int(self.headers.get("Content-Length","0"))
        if length>8192:raise RuntimeError("REQUEST_TOO_LARGE")
        value=json.loads(self.rfile.read(length).decode("utf-8") or "{}")
        if not isinstance(value,dict):raise RuntimeError("JSON_OBJECT_REQUIRED")
        return value
    def do_GET(self)->None:
        route=urlparse(self.path).path
        if route=="/api/status":
            try:
                value=ADAPTER.read();value["auto_update"]=AUTO.state;self._json(value)
            except Exception as exc:self._json({"error":str(exc),"write_status":"WRITE_OPERATIONS_BLOCKED"},409)
            return
        if route=="/api/session":self._json({"token":API_TOKEN});return
        if route=="/api/prospective/preview":
            try:self._json({"ok":True,"preview":ADAPTER.service.preview_next()})
            except Exception as exc:self._json({"ok":False,"error":str(exc)},409)
            return
        relative="index.html" if route in ("","/") else route.lstrip("/");target=(WEB_ROOT/relative).resolve()
        try:target.relative_to(WEB_ROOT.resolve())
        except ValueError:self.send_error(HTTPStatus.NOT_FOUND);return
        if not target.is_file():self.send_error(HTTPStatus.NOT_FOUND);return
        body=target.read_bytes();content_type=mimetypes.guess_type(target.name)[0] or "application/octet-stream";self.send_response(200)
        self.send_header("Content-Type",content_type+("; charset=utf-8" if content_type.startswith(("text/","application/javascript")) else ""));self.send_header("Content-Length",str(len(body)))
        self.send_header("Cache-Control","no-store, max-age=0");self.send_header("X-Content-Type-Options","nosniff");self.end_headers();self.wfile.write(body)
    def do_POST(self)->None:
        route=urlparse(self.path).path
        if route not in {"/api/prospective/outcome","/api/prospective/seal"}:self._json({"ok":False,"error":"WRITE_ROUTE_NOT_ALLOWED"},405);return
        if self.headers.get("X-P45-Token")!=API_TOKEN:self._json({"ok":False,"error":"INVALID_SESSION"},403);return
        try:
            body=self._body()
            result=ADAPTER.service.record_outcome(int(body["target"])) if route.endswith("/outcome") else ADAPTER.service.seal_next(str(body["preview_sha256"]))
            self._json({"ok":True,"result":result})
        except Exception as exc:self._json({"ok":False,"error":str(exc)},409)
    def log_message(self,format:str,*args:object)->None:return

class ExclusiveThreadingHTTPServer(ThreadingHTTPServer):
    allow_reuse_address=False
    def server_bind(self)->None:
        if hasattr(socket,"SO_EXCLUSIVEADDRUSE"):self.socket.setsockopt(socket.SOL_SOCKET,socket.SO_EXCLUSIVEADDRUSE,1)
        super().server_bind()

def serve(host:str="127.0.0.1",port:int=8045)->None:
    server=ExclusiveThreadingHTTPServer((host,port),Handler);worker=threading.Thread(target=AUTO.loop,name="p45-auto-update",daemon=True);worker.start();print(f"P45 WEB V1: http://{host}:{port}")
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:AUTO.stop.set();server.server_close()
def main(argv:list[str]|None=None)->int:
    parser=argparse.ArgumentParser(description="P45 TRIO ORBIT prospective web v1");parser.add_argument("--host",default="127.0.0.1");parser.add_argument("--port",type=int,default=8045);args=parser.parse_args(argv);serve(args.host,args.port);return 0
if __name__=="__main__":raise SystemExit(main())
