"""
Vercel Serverless Function entrypoint for GigBid FastAPI Backend.
Exposes the ASGI app directly to Vercel's Python runtime.
Includes path rewrite middleware and container diagnostic routes.
"""
import os
import sys
import traceback

# Add candidate root paths to sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(CURRENT_DIR)
CWD = os.getcwd()

for p in [ROOT_DIR, CWD, CURRENT_DIR]:
    if p and os.path.exists(p) and p not in sys.path:
        sys.path.insert(0, p)

try:
    from apps.api.main import app

    @app.middleware("http")
    async def vercel_rewrite_middleware(request, call_next):
        """
        Normalize request paths rewritten by Vercel.
        Restores x-matched-path or strips /api prefix when necessary.
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
            "cwd": CWD,
            "root_dir": ROOT_DIR,
            "files_in_cwd": os.listdir(CWD) if os.path.exists(CWD) else [],
            "files_in_root": os.listdir(ROOT_DIR) if os.path.exists(ROOT_DIR) else [],
            "data_exists": os.path.exists(os.path.join(ROOT_DIR, "data")),
            "stream_exists": os.path.exists(os.path.join(ROOT_DIR, "data", "processed", "jobs_stream.json")),
            "sample_exists": os.path.exists(os.path.join(ROOT_DIR, "data", "sample", "jobs.json")),
        }

except Exception as exc:
    err_tb = traceback.format_exc()
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse

    app = FastAPI(title="GigBid Startup Diagnostic Gateway")

    @app.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"])
    async def diagnostic_fallback(full_path: str = ""):
        return JSONResponse(
            status_code=500,
            content={
                "error": "Backend initialization failed on Vercel",
                "exception": str(exc),
                "traceback": err_tb,
                "sys_path": sys.path,
                "root_dir": ROOT_DIR,
                "cwd": CWD,
                "files_in_cwd": os.listdir(CWD) if os.path.exists(CWD) else [],
                "files_in_root": os.listdir(ROOT_DIR) if os.path.exists(ROOT_DIR) else [],
            }
        )

__all__ = ["app"]
