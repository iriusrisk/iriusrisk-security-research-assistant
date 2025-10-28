"""
Project facade for IriusRisk Library Editor API
"""

from typing import List
from isra.src.ile.backend.app.models import (
    ILEProject, ILEVersion, IRBaseElement, IRProjectReport, 
    VersionNamesResponse, MergeLibraryRequest, ChangelogRequest,
    Graph, GraphList, LibrarySummariesResponse, ChangelogReport
)
from isra.src.ile.backend.app.services.project_service import ProjectService
from isra.src.ile.backend.app.services.changelog_service import ChangelogService


class ProjectFacade:
    """Project facade for handling project operations"""
    
    def __init__(self):
        self.project_service = ProjectService()
        self.changelog_service = ChangelogService()
    
    def get_current_project(self) -> ILEProject:
        """Get current project"""
        return self.project_service.get_current_project()
    
    def create_new_project(self, project: IRBaseElement) -> ILEProject:
        """Create new project"""
        return self.project_service.create_project(project)
    
    def list_projects(self) -> List[str]:
        """List all projects"""
        return self.project_service.list_projects()
    
    def clean_folder(self, folder: str) -> None:
        """Clean specified folder"""
        self.project_service.clean_folder(folder)
    
    def delete_version(self, version: str) -> None:
        """Delete version"""
        self.project_service.delete_version(version)
    
    def copy_version(self, version: str, ref: str) -> None:
        """Copy version"""
        self.project_service.copy_version(version, ref)
    
    def load_project(self, project: ILEProject) -> ILEProject:
        """Load project"""
        return self.project_service.load_project(project)
    
    def save_project(self) -> None:
        """Save current project"""
        self.project_service.save_project()
    
    def load_project_from_file(self, project: str) -> ILEProject:
        """Load project from file"""
        return self.project_service.load_project_from_file(project)
    
    def load_version_from_file(self, version: str) -> None:
        """Load version from file"""
        self.project_service.load_version_from_file(version)
    
    def list_version_names(self) -> VersionNamesResponse:
        """List version names"""
        return self.project_service.list_version_names()
    
    def create_version(self, ref: str) -> None:
        """Create new version"""
        self.project_service.create_version(ref)
    
    def get_project_report(self) -> IRProjectReport:
        """Get project report"""
        return self.project_service.get_project_report()
    
    def merge_libraries(self, merge_library_request: MergeLibraryRequest) -> List[str]:
        """Merge libraries"""
        return self.project_service.merge_libraries(merge_library_request)
    
    def generate_full_library_from_version(self, source: str) -> ILEVersion:
        """Generate full library from version"""
        return self.project_service.generate_full_library_from_version(source)
    
    def create_changelog_between_libraries(self, changelog_request: ChangelogRequest) -> Graph:
        """Create changelog between libraries"""
        self.changelog_service.set_changelog_items(changelog_request)
        return self.changelog_service.get_library_changes()
    
    def create_changelog_between_versions(self, changelog_request: ChangelogRequest) -> GraphList:
        """Create changelog between versions"""
        self.changelog_service.set_changelog_items(changelog_request)
        return self.changelog_service.get_version_changes()
    
    def create_changelog_between_versions_simple(self, changelog_request: ChangelogRequest) -> str:
        """Create simple changelog between versions"""
        self.changelog_service.set_changelog_items(changelog_request)
        return self.changelog_service.create_changelog_between_versions_simple()
    
    def generate_relations_changelog(self, changelog_request: ChangelogRequest) -> ChangelogReport:
        """Generate relations changelog"""
        self.changelog_service.set_changelog_items(changelog_request)
        return self.changelog_service.generate_relations_changelog()
    
    def get_library_summaries(self, changelog_request: ChangelogRequest) -> LibrarySummariesResponse:
        """Get library summaries"""
        self.changelog_service.set_changelog_items(changelog_request)
        return self.changelog_service.get_library_summaries()
    
    def get_library_specific_changes(self, changelog_request: ChangelogRequest) -> Graph:
        """Get library specific changes"""
        self.changelog_service.set_changelog_items(changelog_request)
        return self.changelog_service.get_library_specific_changes(changelog_request.library_ref)
