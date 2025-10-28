"""
Test controller for IriusRisk Library Editor API
"""

from fastapi import APIRouter, Depends
from isra.src.ile.backend.app.models import IRTestReport
from isra.src.ile.backend.app.facades.version_facade import VersionFacade

router = APIRouter()


def get_version_facade() -> VersionFacade:
    """Dependency injection for VersionFacade"""
    return VersionFacade()


@router.get("/version/{version_ref}/test")
async def run_tests(version_ref: str, version_facade: VersionFacade = Depends(get_version_facade)) -> IRTestReport:
    """Run tests for version"""
    return version_facade.run_tests(version_ref)
