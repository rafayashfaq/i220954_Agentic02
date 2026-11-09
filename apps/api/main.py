"""
GigBid Backend FastAPI Application.
Hosts typed API endpoints, SSE streaming bridge, and OpenAPI documentation contract.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apps.api.routers import auth, jobs, proposals, approvals, messages, runs, analytics, settings

app = FastAPI(
    title="GigBid Freelancer Copilot API",
    version="1.0.0",
    description="Multi-Agent Freelancer Copilot API for AI-4016 R&D Assignment."
)

# CORS Middleware for Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Routers
app.include_router(auth.router)
app.include_router(jobs.router)
app.include_router(proposals.router)
app.include_router(approvals.router)
app.include_router(messages.router)
app.include_router(runs.router)
app.include_router(analytics.router)
app.include_router(settings.router)

@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "gigbid-api",
        "version": "1.0.0",
        "marketplace_mode": "gigsim"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("apps.api.main:app", host="127.0.0.1", port=8000, reload=True)
