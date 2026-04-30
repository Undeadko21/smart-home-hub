import os, json, time, sqlite3, logging, asyncio, hashlib
from pathlib import Path
from contextlib import asynccontextmanager
from typing import Any, Optional, List, Dict

from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import httpx

DATA_DIR = Path(os.getenv("DATA_DIR", "/app/data"))
DB_PATH = DATA_DIR / "app.db"
LOG_DIR = DATA_DIR / "logs"
for d in [LOG_DIR, DATA_DIR / "cache"]: d.mkdir(parents=True, exist_ok=True)

logging.basicConfig(filename=LOG_DIR / "app.log", level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS config (key TEXT PRIMARY KEY, value TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS ai_cache (hash TEXT PRIMARY KEY, response TEXT, expires REAL)")
    c.execute("CREATE TABLE IF NOT EXISTS notification_queue (id INTEGER PRIMARY KEY AUTOINCREMENT, provider TEXT, payload TEXT, status TEXT DEFAULT 'pending', retries INT DEFAULT 0, next_retry REAL)")
    conn.commit(); conn.close()

def get_config(key: str, default: Any = None) -> Any:
    try:
        conn = sqlite3.connect(DB_PATH)
        res = conn.execute("SELECT value FROM config WHERE key=?", (key,)).fetchone()
        conn.close()
        return json.loads(res[0]) if res and res[0] else default
    except: return default

def set_config(key: str, value: Any):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)", (key, json.dumps(value)))
    conn.commit(); conn.close()

class HAClient:
    def __init__(self, url: str, token: str):
        self.url = url.rstrip("/")
        self.headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"} if token else {}
        self.client = httpx.AsyncClient(timeout=10)
    async def get_entities(self, domain: Optional[str] = None) -> List[Dict]:
        r = await self.client.get(f"{self.url}/api/states", headers=self.headers)
        r.raise_for_status()
        data = r.json()
        if domain:
            return [e for e in data if e["entity_id"].startswith(f"{domain}.")]
        return data
    async def get_entity_state(self, entity_id: str) -> Optional[Dict]:
        r = await self.client.get(f"{self.url}/api/states/{entity_id}", headers=self.headers)
        if r.status_code == 404:
            return None
        r.raise_for_status()
        return r.json()
    async def call_service(self, domain: str, service: str, data: Optional[Dict] = None, target: Optional[Dict] = None) -> Dict:
        payload = {}
        if data:
            payload.update(data)
        if target:
            payload["target"] = target
        r = await self.client.post(f"{self.url}/api/services/{domain}/{service}", headers=self.headers, json=payload)
        r.raise_for_status()
        return {"status": "ok", "result": r.json() if r.text else {}}
    async def get_services(self) -> Dict:
        r = await self.client.get(f"{self.url}/api/services", headers=self.headers)
        r.raise_for_status()
        return r.json()

class DeepSeekClient:
    def __init__(self, api_key: str, db_path: Path):
        self.api_key = api_key
        self.db_path = db_path
        self.client = httpx.AsyncClient(timeout=30)
        self.times: List[float] = []
    def _hash(self, msg: str) -> str: return hashlib.sha256(msg.encode()).hexdigest()[:32]
    def _check_cache(self, h: str) -> Optional[Dict]:
        try:
            conn = sqlite3.connect(self.db_path)
            row = conn.execute("SELECT response, expires FROM ai_cache WHERE hash=? AND expires>?", (h, time.time())).fetchone()
            conn.close()
            return json.loads(row[0]) if row else None
        except: return None
    def _save_cache(self, h: str, resp: Dict):
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute("INSERT OR REPLACE INTO ai_cache (hash, response, expires) VALUES (?,?,?)", (h, json.dumps(resp), time.time()+3600))
            conn.commit(); conn.close()
        except: pass
    def _rate_ok(self) -> bool:
        now = time.time()
        self.times = [t for t in self.times if now - t < 60]
        if len(self.times) >= 10: return False
        self.times.append(now); return True
    async def query(self, messages: List[Dict], sys_prompt: Optional[str] = None) -> Dict:
        try: await self.client.get("https://api.deepseek.com/v1", timeout=2)
        except: return {"error": "Нет сети", "offline": True}
        if not self._rate_ok(): return {"error": "Лимит запросов", "rate_limited": True}
        last = next((m["content"] for m in reversed(messages) if m["role"]=="user"), "")
        h = self._hash(last)
        cached = self._check_cache(h)
        if cached: return cached
        payload = {"model": "deepseek-chat", "messages": [{"role":"system","content": sys_prompt or "Ты помощник для умного дома. Отвечай кратко."}] + messages, "max_tokens": 512}
        r = await self.client.post("https://api.deepseek.com/v1/chat/completions", headers={"Authorization":f"Bearer {self.api_key}", "Content-Type":"application/json"}, json=payload)
        r.raise_for_status()
        resp = r.json()
        self._save_cache(h, resp)
        return resp

class NotifyQueue:
    def __init__(self, db_path: Path):
        self.db_path = db_path; self.running = False
        self.client = httpx.AsyncClient(timeout=15)
    async def push(self, provider: str, payload: Dict):
        conn = sqlite3.connect(self.db_path)
        conn.execute("INSERT INTO notification_queue (provider, payload, next_retry) VALUES (?,?,?)", (provider, json.dumps(payload), time.time()))
        conn.commit(); conn.close()
    async def worker(self):
        self.running = True
        while self.running:
            try:
                conn = sqlite3.connect(self.db_path)
                tasks = conn.execute("SELECT id, provider, payload, retries FROM notification_queue WHERE status='pending' AND next_retry<=? LIMIT 3", (time.time(),)).fetchall()
                conn.close()
                for tid, prov, pl, retr in tasks:
                    cfg = get_config(f"notify_{prov}", {})
                    if not cfg: continue
                    pl = json.loads(pl)
                    try:
                        url = f"{cfg['endpoint']}/{cfg.get('topic','')}" if prov=="ntfy" else f"{cfg['endpoint']}/message"
                        headers = {"Authorization":f"Bearer {cfg.get('token','')}", "X-Gotify-Key":cfg.get('token',''), "Title":pl.get("title","Kiosk"), "Priority":"default"}
                        r = await self.client.post(url, data=pl.get("message",""), json={"title":pl.get("title"), "message":pl.get("message"), "priority":4} if prov=="gotify" else None, headers={k:v for k,v in headers.items() if v})
                        if r.status_code < 400:
                            conn = sqlite3.connect(self.db_path)
                            conn.execute("DELETE FROM notification_queue WHERE id=?", (tid,)); conn.commit(); conn.close()
                        else: raise Exception(f"HTTP {r.status_code}")
                    except Exception as e:
                        backoff = min(300, (2**retr)*10)
                        conn = sqlite3.connect(self.db_path)
                        conn.execute("UPDATE notification_queue SET retries=?, next_retry=? WHERE id=?", (retr+1, time.time()+backoff, tid)); conn.commit(); conn.close()
                await asyncio.sleep(10)
            except: await asyncio.sleep(30)

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    app.state.ha = HAClient(get_config("ha_url",""), get_config("ha_token",""))
    app.state.ai = DeepSeekClient(get_config("ai_key",""), DB_PATH)
    app.state.notifier = NotifyQueue(DB_PATH)
    app.state.worker_task = asyncio.create_task(app.state.notifier.worker())
    logging.info("✅ Full stack ready")
    yield
    app.state.notifier.running = False
    await app.state.ai.client.aclose()

def create_app():
    app = FastAPI(title="Smart Kiosk", lifespan=lifespan)
    limiter = Limiter(key_func=get_remote_address); app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
    STATIC_DIR = Path(__file__).parent.parent / "static"
    @app.get("/")
    async def root():
        idx = STATIC_DIR / "index.html"
        return FileResponse(str(idx), media_type="text/html") if idx.exists() else JSONResponse({"error":"UI missing"}, status_code=404)
    if STATIC_DIR.exists(): app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
    @app.get("/api/health")
    @limiter.limit("30/minute")
    async def health(request: Request):
        try: t=DATA_DIR/".h"; t.touch(); t.unlink(); ok=True
        except: ok=False
        return {"status":"ok", "ha":"configured" if get_config("ha_token") else "no", "ai":"configured" if get_config("ai_key") else "no", "db":ok}
    class ConfigUpdate(BaseModel): key: str; value: Any
    @app.post("/api/config")
    @limiter.limit("20/minute")
    async def update_config(request: Request, cfg: ConfigUpdate):
        set_config(cfg.key, cfg.value); return {"status":"saved"}
    class HAService(BaseModel): domain: str; service: str; data: Optional[Dict] = None; target: Optional[Dict] = None
    @app.post("/api/ha/call_service")
    @limiter.limit("30/minute")
    async def ha_call(request: Request, c: HAService):
        return await app.state.ha.call_service(c.domain, c.service, c.data, c.target)
    @app.get("/api/ha/entities")
    @limiter.limit("20/minute")
    async def ha_ent(request: Request, domain: Optional[str] = None):
        return await app.state.ha.get_entities(domain)
    @app.get("/api/ha/entity/{entity_id}")
    @limiter.limit("30/minute")
    async def ha_entity_state(request: Request, entity_id: str):
        state = await app.state.ha.get_entity_state(entity_id)
        if state is None:
            raise HTTPException(status_code=404, detail="Entity not found")
        return state
    @app.get("/api/ha/services")
    @limiter.limit("20/minute")
    async def ha_services(request: Request):
        return await app.state.ha.get_services()
    class AIQuery(BaseModel): messages: List[Dict]; system_prompt: Optional[str] = None
    @app.post("/api/ai/query")
    @limiter.limit("10/minute")
    async def ai_q(request: Request, q: AIQuery):
        return await app.state.ai.query(q.messages, q.system_prompt)
    class NotifyTest(BaseModel): provider: str; message: str; title: Optional[str] = "Test"
    @app.post("/api/notify/test")
    @limiter.limit("5/minute")
    async def notify_t(request: Request, t: NotifyTest):
        await app.state.notifier.push(t.provider, {"title": t.title, "message": t.message}); return {"status":"queued"}
    return app

app = create_app()
if __name__ == "__main__":
    import uvicorn; uvicorn.run(app, host="0.0.0.0", port=8080, log_level="info")
