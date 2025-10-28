"""
Main FastAPI application for IriusRisk Library Editor
"""

import os
import logging
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager

from isra.src.ile.backend.app.configuration import config_factory
from isra.src.ile.backend.app.controllers.project_controller import router as project_router
from isra.src.ile.backend.app.controllers.library_controller import router as library_router
from isra.src.ile.backend.app.controllers.version_controller import router as version_router
from isra.src.ile.backend.app.controllers.changelog_controller import router as changelog_router
from isra.src.ile.backend.app.controllers.test_controller import router as test_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager for startup and shutdown events
    """
    # Startup
    logger.info("Starting IriusRisk Library Editor API...")
    
    # Initialize configuration
    env_config = config_factory.get_environment_config()
    
    # Validate environment
    if not config_factory.validate_environment():
        logger.error("Environment validation failed")
        raise RuntimeError("Environment validation failed")
    
    # Ensure directories exist
    env_config._ensure_directories()
    
    # Initialize default config if needed
    env_config.initialize_default_config()
    
    logger.info("IriusRisk Library Editor API started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down IriusRisk Library Editor API...")


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application
    """
    # Get server configuration
    env_config = config_factory.get_environment_config()
    server_config = env_config.get_server_config()
    
    # Create FastAPI app
    app = FastAPI(
        title="IriusRisk Library Editor API",
        description="API for managing IriusRisk security libraries and components",
        version="2.0.0",
        lifespan=lifespan
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
    app.include_router(project_router)
    app.include_router(library_router)
    app.include_router(version_router)
    app.include_router(changelog_router)
    app.include_router(test_router)
    

    # Health check endpoint
    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        return {"status": "healthy", "service": "IriusRisk Library Editor API"}
    
    # Root endpoint
    @app.get("/")
    async def root():
        """Root endpoint"""
        return {
            "message": "IriusRisk Library Editor API",
            "version": "2.0.0",
            "docs": "/docs"
        }
    
    return app


# Create the app instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    
    # Get server configuration
    env_config = config_factory.get_environment_config()
    server_config = env_config.get_server_config()
    
    # Run the server
    uvicorn.run(
        "main:app",
        host=server_config["host"],
        port=server_config["port"],
        reload=server_config["reload"],
        log_level="info"
    )
