"""
Cheque Tally Agent - Production-grade FastAPI Application
Reconciles company-issued cheques with bank-cleared cheques
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from app.db.base import Base, engine
from app.models import (  # noqa: F401 - imports all models for Base.metadata
    User, Session, BankTransaction, CompanyExpense, TallyResult
)
from app.middleware import setup_middleware
from app.core.config import get_settings
from app.routes.auth import router as auth_router
from app.routes.session import router as session_router
import logging
from datetime import datetime


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Get settings
settings = get_settings()

# Initialize database
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    logger.error(f"Failed to create database tables: {str(e)}")
    raise

# Create FastAPI application
app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Setup middleware
setup_middleware(app, enable_cors=True, enable_trusted_host=False)


# ==================== HEALTH CHECK ENDPOINTS ====================

@app.get("/health", tags=["health"])
async def health_check():
    """
    Basic health check endpoint
    
    Returns:
        Health status
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": settings.API_TITLE
    }


@app.get("/health/ready", tags=["health"])
async def readiness_check():
    """
    Readiness check endpoint
    Verifies database connectivity
    
    Returns:
        Readiness status
    """
    try:
        # Test database connection
        from app.db.base import SessionLocal
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        
        return {
            "ready": True,
            "database": "connected",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Readiness check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service not ready"
        )


# ==================== INCLUDE ROUTERS ====================

# Authentication routes
app.include_router(auth_router, prefix="/auth", tags=["authentication"])
app.include_router(session_router, tags=["sessions"])

# Import and include new routers
from app.routes.company import router as company_router
from app.routes.bank import router as bank_router
from app.routes.tally import router as tally_router

app.include_router(company_router)
app.include_router(bank_router)
app.include_router(tally_router)


# ==================== ERROR HANDLERS ====================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """
    Custom HTTP exception handler
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "detail": exc.detail,
            "timestamp": datetime.utcnow().isoformat()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """
    Catch-all exception handler for unexpected errors
    """
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    
    # In development, show error details; in production, be vague
    detail = str(exc) if settings.DEBUG else "Internal server error"
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "detail": detail,
            "timestamp": datetime.utcnow().isoformat()
        }
    )



# ==================== STARTUP AND SHUTDOWN EVENTS ====================

@app.on_event("startup")
async def startup_event():
    """
    Execute on application startup
    """
    logger.info(f"Starting {settings.API_TITLE} v{settings.API_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.DEBUG}")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Execute on application shutdown
    """
    logger.info(f"Shutting down {settings.API_TITLE}")


# ==================== LIFESPAN CONTEXT MANAGER ====================

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifespan
    """
    # Startup
    logger.info("Application startup complete")
    yield
    # Shutdown
    logger.info("Application shutdown complete")


# Note: Attach lifespan if using FastAPI 0.104+
# app.router.lifespan_context = lifespan