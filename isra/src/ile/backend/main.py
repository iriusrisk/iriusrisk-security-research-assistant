"""
Main FastAPI application for IriusRisk Library Editor
"""

import os
import logging
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager

from isra.src.ile.backend.app.configuration import config_factory
from isra.src.ile.backend.app.configuration.properties_manager import PropertiesManager
from isra.src.ile.backend.app.controllers.project_controller import router as project_router
from isra.src.ile.backend.app.controllers.library_controller import router as library_router
from isra.src.ile.backend.app.controllers.version_controller import router as version_router
from isra.src.ile.backend.app.controllers.changelog_controller import router as changelog_router
from isra.src.ile.backend.app.controllers.test_controller import router as test_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_project_on_startup():
    """
    Load project on startup if configured in properties
    """
    try:
        load_on_startup = PropertiesManager.get_property("load-project-on-startup")
        if load_on_startup and load_on_startup.strip():
            logger.info(f"Loading project on startup: {load_on_startup}")
            
            # Import here to avoid circular references
            from isra.src.ile.backend.app.services.project_service import ProjectService
            
            project_service = ProjectService()
            project_service.load_project_from_file(load_on_startup.strip())
            logger.info(f"Successfully loaded project: {load_on_startup}")
        else:
            logger.debug("No project configured for startup loading")
    except Exception as e:
        logger.error(f"Failed to load project on startup: {e}")


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
    
    # Load project on startup if configured
    load_project_on_startup()
    
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
    
    # Check if we should serve static files
    serve_static = os.environ.get('SERVE_STATIC', 'false').lower() == 'true'
    static_dir = os.environ.get('STATIC_DIR', '')
    logger.info(f"Static file serving check: serve_static={serve_static}, static_dir='{static_dir}'")
    
    # Resolve the path to handle relative paths and Windows path issues
    static_dir_path = None
    if static_dir:
        static_dir_path = Path(static_dir).resolve()
        logger.info(f"Resolved static directory path: {static_dir_path}")
        logger.info(f"Static directory exists: {static_dir_path.exists()}")
    
    # Include routers with /api prefix - API routes are always under /api/
    # These are registered first so they take precedence
    app.include_router(project_router, prefix="/api", tags=["project"])
    app.include_router(version_router, prefix="/api", tags=["version"])
    app.include_router(library_router, prefix="/api", tags=["library"])
    app.include_router(changelog_router, prefix="/api", tags=["changelog"])
    app.include_router(test_router, prefix="/api", tags=["test"])
    
    # Health check endpoint (always available, not under /api)
    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        return {"status": "healthy", "service": "IriusRisk Library Editor API"}
    
    # Determine if we should actually serve static files
    actually_serve_static = False
    index_file = None
    
    if serve_static and static_dir_path and static_dir_path.exists():
        index_file = static_dir_path / "index.html"
        if index_file.exists():
            actually_serve_static = True
            logger.info(f"✓ Static file serving ENABLED")
            logger.info(f"  Serving static files from: {static_dir_path}")
            logger.info(f"  Index file path: {index_file}")
        else:
            logger.error(f"✗ index.html not found at {index_file}")
            logger.warning("  Static file serving disabled - index.html missing")
    
    # Handle static file serving
    if actually_serve_static:
        # Mount static assets (CSS, JS, etc.) under /static
        app.mount("/static", StaticFiles(directory=static_dir_path / "static"), name="static")
        
        # Serve index.html for root path - register this BEFORE catch-all
        @app.get("/")
        async def serve_root():
            """Serve the React app root"""
            logger.info(f"Root route called - serving React app index.html")
            return FileResponse(
                path=str(index_file),
                media_type="text/html"
            )
        
        # Catch-all route for all other non-API paths - serves React app for client-side routing
        # This must be defined LAST so it doesn't interfere with API routes
        @app.get("/{full_path:path}")
        async def serve_react_app(full_path: str):
            """Serve the React app for all non-API routes"""
            # Don't serve React app for API routes and FastAPI built-in routes
            excluded_paths = ['api/', 'docs', 'redoc', 'openapi.json', 'health', 'static']
            if any(full_path.startswith(excluded) for excluded in excluded_paths):
                raise HTTPException(status_code=404, detail="Not found")
            
            # Serve index.html for all other routes (React Router will handle routing)
            logger.info(f"Serving React app for path: /{full_path}")
            return FileResponse(
                path=str(index_file),
                media_type="text/html"
            )
    else:
        # If static files are not being served, register API root endpoint
        # Log why static files are not being served
        logger.warning("✗ Static file serving DISABLED")
        if not os.environ.get('SERVE_STATIC', 'false').lower() == 'true':
            logger.warning("  Reason: SERVE_STATIC != 'true'")
        elif not static_dir:
            logger.warning("  Reason: STATIC_DIR environment variable is empty")
        elif static_dir_path and not static_dir_path.exists():
            logger.warning(f"  Reason: Static directory does not exist: {static_dir_path}")
        
        # Root endpoint - only available when static files are NOT being served
        @app.get("/")
        async def root():
            """Root endpoint - API information"""
            logger.info("Root endpoint called - returning API information")
            return {
                "message": "IriusRisk Library Editor API",
                "version": "2.0.0",
                "docs": "/docs",
                "api": "/api"
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
