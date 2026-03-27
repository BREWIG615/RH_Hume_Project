"""
FastAPI Application - Agent API Service

Main entry point for the REST API serving:
- Chat endpoint for agent interactions
- Narrative generation
- Health checks
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from src.config.loader import get_config

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    logger.info("Starting RH Hume API...")
    config = get_config()
    
    # Initialize connections
    # TODO: Initialize Neo4j, Kafka, etc.
    
    logger.info("API startup complete")
    
    yield
    
    # Shutdown
    logger.info("Shutting down API...")
    # TODO: Close connections
    logger.info("API shutdown complete")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    
    config = get_config()
    
    app = FastAPI(
        title="RH Hume Project API",
        description="Contested Logistics Intelligence Platform - Agent API",
        version="0.1.0",
        lifespan=lifespan,
    )
    
    # CORS configuration
    cors_origins = config.get("api.cors_origins", ["http://localhost:3000"])
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
    from src.api.routes import health, chat, narratives
    
    app.include_router(health.router, tags=["Health"])
    app.include_router(chat.router, prefix="/api", tags=["Chat"])
    app.include_router(narratives.router, prefix="/api", tags=["Narratives"])
    
    return app


# Application instance
app = create_app()
