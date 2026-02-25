"""
Vercel API entry point for FastAPI app
"""
from app.main import app

# Export the app for Vercel
__all__ = ["app"]
