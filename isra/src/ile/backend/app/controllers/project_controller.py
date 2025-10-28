"""
Project controller for IriusRisk Library Editor API
"""

from fastapi import APIRouter, Depends
from typing import List
from isra.src.ile.backend.app.models import (
    ILEProject, ILEVersion, IRBaseElement, IRProjectReport, 
    VersionNamesResponse, CopyVersionRequest, MergeLibraryRequest
)
from isra.src.ile.backend.app.facades.project_facade import ProjectFacade

router = APIRouter()


def get_project_facade() -> ProjectFacade:
    """Dependency injection for ProjectFacade"""
    return ProjectFacade()


@router.get("/project")
async def get_current_project(project_facade: ProjectFacade = Depends(get_project_facade)) -> ILEProject:
    """Get current project"""
    print("test")
    return project_facade.get_current_project()


@router.get("/project/list")
async def list_projects(project_facade: ProjectFacade = Depends(get_project_facade)) -> List[str]:
    """List all projects"""
    return project_facade.list_projects()


@router.get("/project/cleanFolder/{folder}")
async def clean_folder(folder: str, project_facade: ProjectFacade = Depends(get_project_facade)) -> None:
    """Clean specified folder"""
    project_facade.clean_folder(folder)


@router.post("/project")
async def create_new_project(project: IRBaseElement, project_facade: ProjectFacade = Depends(get_project_facade)) -> ILEProject:
    """Create new project"""
    return project_facade.create_new_project(project)


@router.post("/project/load")
async def load_project(project: ILEProject, project_facade: ProjectFacade = Depends(get_project_facade)) -> ILEProject:
    """Load project (deprecated)"""
    return project_facade.load_project(project)


@router.get("/project/load/{project}")
async def load_project_from_file(project: str, project_facade: ProjectFacade = Depends(get_project_facade)) -> ILEProject:
    """Load project from file"""
    return project_facade.load_project_from_file(project)


@router.get("/project/save")
async def save_project(project_facade: ProjectFacade = Depends(get_project_facade)) -> None:
    """Save current project"""
    project_facade.save_project()


@router.get("/project/versions")
async def list_version_names(project_facade: ProjectFacade = Depends(get_project_facade)) -> VersionNamesResponse:
    """List version names"""
    return project_facade.list_version_names()


@router.post("/project/version/{version}")
async def create_version(version: str, project_facade: ProjectFacade = Depends(get_project_facade)) -> VersionNamesResponse:
    """Create new version"""
    project_facade.create_version(version)
    return project_facade.list_version_names()


@router.delete("/project/version/{version}")
async def delete_version(version: str, project_facade: ProjectFacade = Depends(get_project_facade)) -> VersionNamesResponse:
    """Delete version"""
    project_facade.delete_version(version)
    return project_facade.list_version_names()


@router.post("/project/version/copy")
async def copy_version(body: CopyVersionRequest, project_facade: ProjectFacade = Depends(get_project_facade)) -> VersionNamesResponse:
    """Copy version"""
    project_facade.copy_version(body.src_version, body.ref)
    return project_facade.list_version_names()


@router.get("/project/version/load/{version}")
async def load_version_from_file(version: str, project_facade: ProjectFacade = Depends(get_project_facade)) -> VersionNamesResponse:
    """Load version from file"""
    project_facade.load_version_from_file(version)
    return project_facade.list_version_names()


@router.get("/project/report")
async def get_project_report(project_facade: ProjectFacade = Depends(get_project_facade)) -> IRProjectReport:
    """Get project report"""
    return project_facade.get_project_report()


@router.post("/project/mergeLibraries")
async def merge_libraries(body: MergeLibraryRequest, project_facade: ProjectFacade = Depends(get_project_facade)) -> List[str]:
    """Merge libraries"""
    return project_facade.merge_libraries(body)


@router.post("/project/generateFullLibrary")
async def generate_full_library_from_version(body: MergeLibraryRequest, project_facade: ProjectFacade = Depends(get_project_facade)) -> ILEVersion:
    """Generate full library from version"""
    return project_facade.generate_full_library_from_version(body.src_version)
