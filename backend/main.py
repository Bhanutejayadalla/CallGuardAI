"""
CallGuard AI - Main Application Entry Point
Real-time Audio Call Analysis Platform
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from loguru import logger
import sys

from app.core.config import settings
from app.api.v1 import api_router
from app.core.database import init_db
from app.ml.model_loader import load_models


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("🚀 Starting CallGuard AI Platform...")
    
    # Initialize database
    await init_db()
    logger.info("✅ Database initialized")
    
    # Load ML models
    await load_models()
    logger.info("✅ ML models loaded")
    
    yield
    
    # Shutdown
    logger.info("👋 Shutting down CallGuard AI Platform...")


# Configure logging
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level=settings.LOG_LEVEL
)
if settings.LOG_FILE:
    logger.add(settings.LOG_FILE, rotation="10 MB", retention="7 days")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="AI-Powered Real-Time Audio Call Analysis Platform for Spam, Fraud, Phishing, and Robocall Detection",
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/api/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
