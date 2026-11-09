"""
Vercel Serverless Function entrypoint for GigBid FastAPI Backend.
Exposes the ASGI app directly to Vercel's Python runtime.
"""
import os
import sys

# Priority 1: Current directory (api/)
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

# Priority 2: Root directory
ROOT_DIR = os.path.dirname(CURRENT_DIR)
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

# Priority 3: CWD
CWD = os.getcwd()
if CWD not in sys.path:
    sys.path.append(CWD)

from apps.api.main import app

@app.middleware("http")
async def vercel_rewrite_middleware(request, call_next):
    """
    Normalize request paths rewritten by Vercel.
    Restores original requested path from x-matched-path if needed.
    """
    path = request.scope.get("path", "")
    matched = request.headers.get("x-matched-path", "")
    forwarded = request.headers.get("x-forwarded-uri", "")

    if path in ("/api/index.py", "/api/index", "/api", "/api/"):
        if matched and not matched.startswith("/api/index"):
            request.scope["path"] = matched.split("?")[0]
        elif forwarded and not forwarded.startswith("/api/index"):
            request.scope["path"] = forwarded.split("?")[0]
    elif path.startswith("/api/"):
        candidate = path[4:]
        for r in request.app.routes:
            if getattr(r, "path", None) == candidate:
                request.scope["path"] = candidate
                break

    return await call_next(request)

@app.get("/diagnostic")
@app.get("/api/diagnostic")
def vercel_diagnostic():
    return {
        "status": "ok",
        "service": "gigbid-api",
        "cwd": CWD,
        "api_dir": CURRENT_DIR,
        "api_files": os.listdir(CURRENT_DIR) if os.path.exists(CURRENT_DIR) else [],
    }

__all__ = ["app"]
