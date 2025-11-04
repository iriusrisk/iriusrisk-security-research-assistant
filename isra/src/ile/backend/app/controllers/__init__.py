"""
Controllers module for IriusRisk Content Manager API
"""

from isra.src.ile.backend.app.controllers.project_controller import router as project_router
from isra.src.ile.backend.app.controllers.library_controller import router as library_router
from isra.src.ile.backend.app.controllers.version_controller import router as version_router
from isra.src.ile.backend.app.controllers.changelog_controller import router as changelog_router
from isra.src.ile.backend.app.controllers.test_controller import router as test_router

__all__ = [
    'project_router',
    'library_router', 
    'version_router',
    'changelog_router',
    'test_router'
]
