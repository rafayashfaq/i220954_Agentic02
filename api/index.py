"""
Vercel Serverless Function entrypoint for GigBid FastAPI Backend.
Exposes the ASGI app directly to Vercel's Python runtime.
"""
import os
import sys

# Ensure repository root is in Python module search path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from apps.api.main import app

# Export app for Vercel
__all__ = ["app"]
