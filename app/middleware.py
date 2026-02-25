"""
Production-grade middleware for API security and monitoring
"""

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
import time
import logging


logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Add security headers to all responses
    """
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        # Allow CDN for Swagger UI while maintaining security
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; img-src 'self' https:"
        
        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Log all incoming requests and responses
    """
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Log request
        logger.info(
            f"Request: {request.method} {request.url.path} "
            f"Client: {request.client.host if request.client else 'unknown'}"
        )
        
        try:
            response = await call_next(request)
            
            process_time = time.time() - start_time
            
            # Log response
            logger.info(
                f"Response: {response.status_code} "
                f"Duration: {process_time:.3f}s"
            )
            
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(
                f"Request Error: {request.method} {request.url.path} "
                f"Duration: {process_time:.3f}s Error: {str(e)}"
            )
            raise


def add_cors_middleware(app):
    """
    Add CORS middleware with production configurations
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Change to specific domains in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Process-Time"],
        max_age=600,
    )


def add_trusted_host_middleware(app, allowed_hosts=None):
    """
    Add trusted host middleware
    """
    if allowed_hosts is None:
        allowed_hosts = ["localhost", "127.0.0.1", "*.example.com"]
    
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=allowed_hosts)


def setup_middleware(app, enable_cors=True, enable_trusted_host=False):
    """
    Setup all middleware for the application
    
    Args:
        app: FastAPI application instance
        enable_cors: Whether to enable CORS
        enable_trusted_host: Whether to enable trusted host validation
    """
    # Add middleware in reverse order (first added is last to execute)
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(SecurityHeadersMiddleware)
    
    if enable_cors:
        add_cors_middleware(app)
    
    if enable_trusted_host:
        add_trusted_host_middleware(app)
