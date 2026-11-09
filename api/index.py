"""
Vercel Serverless Function entrypoint for GigBid Backend.
Exposes ASGI application with foolproof route normalization and diagnostic fallback.
"""
import os
import sys
import json
import traceback

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(CURRENT_DIR)
CWD = os.getcwd()

for p in [CURRENT_DIR, ROOT_DIR, CWD]:
    if p and os.path.exists(p) and p not in sys.path:
        sys.path.insert(0, p)

try:
    from apps.api.main import app as _real_app

    @_real_app.middleware("http")
    async def vercel_rewrite_middleware(request, call_next):
        path = request.scope.get("path", "")
        
        # Check all headers where Vercel passes the original requested path
        candidate_headers = [
            "x-matched-path",
            "x-invoke-path",
            "x-forwarded-uri",
            "x-now-route-matches"
        ]
        orig_path = ""
        for h in candidate_headers:
            val = request.headers.get(h)
            if val and not val.startswith("/api/index") and not val.startswith("/index.py"):
                orig_path = val.split("?")[0]
                break

        if path in ("/api/index.py", "/api/index", "/api", "/api/", "/index.py") and orig_path:
            request.scope["path"] = orig_path
        elif path.startswith("/api/"):
            candidate = path[4:]
            for r in request.app.routes:
                if getattr(r, "path", None) == candidate:
                    request.scope["path"] = candidate
                    break

        return await call_next(request)

    @_real_app.get("/diagnostic")
    @_real_app.get("/api/diagnostic")
    def vercel_diagnostic():
        return {
            "status": "ok",
            "service": "gigbid-api",
            "cwd": CWD,
            "api_dir": CURRENT_DIR,
            "api_files": os.listdir(CURRENT_DIR) if os.path.exists(CURRENT_DIR) else [],
        }

    app = _real_app

except BaseException as exc:
    err_info = {
        "error": str(exc),
        "exception_type": type(exc).__name__,
        "traceback": traceback.format_exc(),
        "sys_path": sys.path,
        "cwd": CWD,
        "files_in_api": os.listdir(CURRENT_DIR) if os.path.exists(CURRENT_DIR) else [],
        "files_in_root": os.listdir(ROOT_DIR) if os.path.exists(ROOT_DIR) else [],
    }

    async def app(scope, receive, send):
        if scope.get("type") == "http":
            body = json.dumps(err_info, indent=2).encode("utf-8")
            await send({
                "type": "http.response.start",
                "status": 200,
                "headers": [
                    [b"content-type", b"application/json"],
                    [b"content-length", str(len(body)).encode("utf-8")]
                ]
            })
            await send({
                "type": "http.response.body",
                "body": body
            })

__all__ = ["app"]
