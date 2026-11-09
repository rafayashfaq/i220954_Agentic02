"""
Vercel Serverless Function entrypoint for GigBid FastAPI Backend.
Exposes the ASGI app directly to Vercel's Python runtime.
Includes path rewrite middleware and startup error diagnostics.
"""
import os
import sys
import traceback

# Add multiple candidate root paths to sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(CURRENT_DIR)
CWD = os.getcwd()

for p in [ROOT_DIR, CWD, CURRENT_DIR]:
    if p and os.path.exists(p) and p not in sys.path:
        sys.path.insert(0, p)

try:
    from apps.api.main import app as _real_app

    class VercelPathMiddleware:
        """
        Ensures request paths from Vercel rewrites (e.g. x-matched-path)
        or /api prefixes are correctly routed to FastAPI routes.
        """
        def __init__(self, app):
            self.app = app

        async def __call__(self, scope, receive, send):
            if scope.get("type") == "http":
                headers = dict(scope.get("headers", []))
                matched_path = headers.get(b"x-matched-path", b"").decode("utf-8")
                forwarded_uri = headers.get(b"x-forwarded-uri", b"").decode("utf-8")

                path = scope.get("path", "")

                # If rewrite directed to /api/index.py or /api/index, restore original matched path
                if path in ("/api/index.py", "/api/index", "/api", "/api/", "api/index.py"):
                    if matched_path and not matched_path.startswith("/api/index"):
                        scope["path"] = matched_path.split("?")[0]
                    elif forwarded_uri and not forwarded_uri.startswith("/api/index"):
                        scope["path"] = forwarded_uri.split("?")[0]

                # If path starts with /api/ but FastAPI routes don't use /api prefix, strip it
                current_path = scope.get("path", "")
                if current_path.startswith("/api/") and not current_path.startswith("/api/index"):
                    scope["path"] = current_path[4:]

            await self.app(scope, receive, send)

        def __getattr__(self, name):
            return getattr(self.app, name)

    app = VercelPathMiddleware(_real_app)

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
