"""
Changelog controller for IriusRisk Library Editor API
"""

from fastapi import APIRouter, Depends
from isra.src.ile.backend.app.models import ChangelogRequest, Graph, GraphList, LibrarySummariesResponse, ChangelogReport
from isra.src.ile.backend.app.facades.project_facade import ProjectFacade

router = APIRouter()


def get_project_facade() -> ProjectFacade:
    """Dependency injection for ProjectFacade"""
    return ProjectFacade()


@router.post("/project/diff/libraries")
async def changelog_between_libraries(request: ChangelogRequest, project_facade: ProjectFacade = Depends(get_project_facade)) -> Graph:
    """Create changelog between libraries"""
    return project_facade.create_changelog_between_libraries(request)


@router.post("/project/diff/versions")
async def changelog_between_versions(request: ChangelogRequest, project_facade: ProjectFacade = Depends(get_project_facade)) -> GraphList:
    """Create changelog between versions"""
    return project_facade.create_changelog_between_versions(request)


@router.post("/project/diff/versions/summaries")
async def get_library_summaries(request: ChangelogRequest, project_facade: ProjectFacade = Depends(get_project_facade)) -> LibrarySummariesResponse:
    """Get library summaries"""
    return project_facade.get_library_summaries(request)


@router.post("/project/diff/versions/library")
async def get_library_specific_changes(request: ChangelogRequest, project_facade: ProjectFacade = Depends(get_project_facade)) -> Graph:
    """Get library specific changes"""
    return project_facade.get_library_specific_changes(request)


@router.post("/project/diff/versions/simple")
async def changelog_between_versions_simple(request: ChangelogRequest, project_facade: ProjectFacade = Depends(get_project_facade)) -> str:
    """Create simple changelog between versions"""
    return project_facade.create_changelog_between_versions_simple(request)


@router.post("/project/diff/versions/relations")
async def changelog_between_versions_relations(request: ChangelogRequest, project_facade: ProjectFacade = Depends(get_project_facade)) -> ChangelogReport:
    """Generate relations changelog"""
    return project_facade.generate_relations_changelog(request)
