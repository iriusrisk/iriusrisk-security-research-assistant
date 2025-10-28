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
    app.include_router(project_router, prefix="/api")
    app.include_router(library_router, prefix="/api")
    app.include_router(version_router, prefix="/api")
    app.include_router(changelog_router, prefix="/api")
    app.include_router(test_router, prefix="/api")
    
    # Check if we should serve static files
    serve_static = os.environ.get('SERVE_STATIC', 'false').lower() == 'true'
    static_dir = os.environ.get('STATIC_DIR', '')
    
    if serve_static and static_dir and Path(static_dir).exists():
        # Mount static files
        app.mount("/static", StaticFiles(directory=Path(static_dir) / "static"), name="static")
        
        # Serve the main React app for all non-API routes
        @app.get("/{full_path:path}")
        async def serve_react_app(full_path: str):
            """Serve the React app for all non-API routes"""
            # Don't serve React app for API routes and FastAPI built-in routes
            api_routes = [
                'project', 'version', 'changelog', 'test',  # API route prefixes
                'docs', 'redoc', 'openapi.json', 'health',  # FastAPI built-in routes
                'static'  # Static files
            ]
            
            if any(full_path.startswith(route) for route in api_routes):
                return {"error": "Not found"}
            
            # Serve index.html for all other routes (React Router will handle routing)
            index_file = Path(static_dir) / "index.html"
            if index_file.exists():
                return FileResponse(str(index_file))
            else:
                return {"error": "Frontend not found"}
        
        # Override the root endpoint to serve the React app
        @app.get("/")
        async def serve_root():
            """Serve the React app root"""
            index_file = Path(static_dir) / "index.html"
            if index_file.exists():
                return FileResponse(str(index_file))
            else:
                return {
                    "message": "IriusRisk Library Editor API",
                    "version": "2.0.0",
                    "docs": "/docs"
                }
    else:
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
