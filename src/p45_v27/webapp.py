"""P45 TRIO ORBIT Prospective Web V1 on the existing standard HTTP server."""
from __future__ import annotations
import argparse, json, mimetypes, os, secrets, socket, threading, time
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse
from .web_adapter import FrozenWebAdapter
from .draw_update import run_update
from .web_publish import publish

PROJECT_ROOT=Path(__file__).resolve().parents[2]; WEB_ROOT=PROJECT_ROOT/"web"; ADAPTER=FrozenWebAdapter(PROJECT_ROOT)
API_TOKEN=secrets.token_urlsafe(32)
LIFECYCLE_LOG=PROJECT_ROOT/"v27_storage/live/p45_lifecycle_runs.jsonl"

def _append_lifecycle_log(entry: dict) -> None:
    try:
        LIFECYCLE_LOG.parent.mkdir(parents=True, exist_ok=True)
        with LIFECYCLE_LOG.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception:
        pass

class AutoUpdateCoordinator:
    def __init__(self, adapter:FrozenWebAdapter, update=run_update, interval:int=300)->None:
        self.adapter=adapter;self.update=update;self.interval=interval;self.lock=threading.Lock();self.stop=threading.Event()
        self.state={"status":"대기","last_check":None,"last_error":None,"steps":[]}
    def run_once(self, trigger_source: str = "AUTO")->dict:
        if not self.lock.acquire(blocking=False):return self.state
        steps=[];pub_res=None;current_target=None;canonical_latest=None
        try:
            while True:
                updated=self.update();status_val=updated.get("status","UNKNOWN");steps.append(status_val)
                if status_val in ("DRAW_DATA_INVALID","DRAW_UPDATE_FAILED"):
                    raise RuntimeError(f"DRAW_UPDATE_REJECTED:{status_val}:{updated.get('error','')}")
                if status_val!="P45_NEW_DRAW_UPDATE_V1_READY":
                    break
            status=self.adapter.read()
            canonical_latest=status.get("canonical",{}).get("latest")
            current_target=status.get("current",{}).get("target")
            while status["current"]["action"] in ("RECORD_OUTCOME","PREVIEW_AND_SEAL_NEXT"):
                if status["current"]["action"]=="RECORD_OUTCOME":
                    target_to_settle=status["current"]["target"]
                    self.adapter.service.record_outcome(target_to_settle)
                    steps.append(f"SETTLED_{target_to_settle}")
                    status=self.adapter.read()
                    current_target=status.get("current",{}).get("target")
                elif status["current"]["action"]=="PREVIEW_AND_SEAL_NEXT":
                    preview=self.adapter.service.preview_next()
                    self.adapter.service.seal_next(preview["preview_sha256"])
                    steps.append(f"NEXT_SEALED_{preview['target']}")
                    status=self.adapter.read()
                    current_target=status.get("current",{}).get("target")
            if status["current"]["action"]=="WRITE_OPERATIONS_BLOCKED":
                raise RuntimeError(f"PROSPECTIVE_WRITE_OPERATIONS_BLOCKED:{json.dumps(status.get('integrity', {}), ensure_ascii=False)}")
            pub_res=publish(self.adapter.read())
            steps.append(pub_res)
            self.state={"status":"자동 업데이트 반영","last_check":time.time(),"last_error":None,"steps":steps}
        except Exception as exc:
            self.state={"status":"자동 업데이트 오류","last_check":time.time(),"last_error":f"{type(exc).__name__}: {exc}","steps":steps}
        finally:
            self.lock.release()
            _append_lifecycle_log({
                "timestamp":datetime.now(timezone.utc).isoformat(),
                "trigger_source":trigger_source,
                "target":current_target,
                "canonical_latest":canonical_latest,
                "steps":list(steps),
                "success":self.state["last_error"] is None,
                "error":self.state["last_error"],
                "deploy_result":pub_res,
                "final_state":self.state["status"],
            })
        return self.state
    def loop(self)->None:
        while not self.stop.is_set():self.run_once(trigger_source="DAEMON_LOOP");self.stop.wait(self.interval)

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
                if os.environ.get("VERCEL"):
                    value=json.loads((PROJECT_ROOT/"web_runtime/status.json").read_text(encoding="utf-8"))
                else:
                    value=ADAPTER.read();value["auto_update"]=AUTO.state
                self._json(value)
            except Exception as exc:self._json({"error":str(exc),"write_status":"WRITE_OPERATIONS_BLOCKED"},409)
            return
        if os.environ.get("VERCEL") and route.startswith("/api/"):
            self._json({"error":"CLOUD_READ_ONLY"},405);return
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
        if os.environ.get("VERCEL"):
            self._json({"ok":False,"error":"CLOUD_READ_ONLY"},405);return
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
    parser=argparse.ArgumentParser(description="P45 TRIO ORBIT prospective web v1")
    parser.add_argument("--host",default="127.0.0.1")
    parser.add_argument("--port",type=int,default=8045)
    parser.add_argument("--once",action="store_true",help="Run one complete lifecycle pass and exit")
    parser.add_argument("--trigger-source",default=os.environ.get("P45_TRIGGER_SOURCE","CLI_ONCE"),help="Trigger source identifier")
    args=parser.parse_args(argv)
    if args.once:
        res=AUTO.run_once(trigger_source=args.trigger_source)
        print(json.dumps(res,ensure_ascii=False,indent=2))
        return 0 if res.get("last_error") is None else 1
    serve(args.host,args.port)
    return 0
if __name__=="__main__":raise SystemExit(main())
