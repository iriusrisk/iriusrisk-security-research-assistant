"""
Project service for IriusRisk Library Editor API
"""

import json
import logging
import os
import shutil
from pathlib import Path
from typing import List, Dict, Any

from isra.src.ile.backend.app.configuration.constants import ILEConstants
from isra.src.ile.backend.app.models import (
    ILEProject, ILEVersion, IRBaseElement, IRProjectReport, 
    VersionNamesResponse, MergeLibraryRequest, IRLibrary,
    IRComponentDefinition, IRControl, IRRelation, IRRiskPattern,
    IRRule, IRStandard, IRThreat, IRUseCase, IRWeakness
)
from isra.src.ile.backend.app.services.data_service import DataService

logger = logging.getLogger(__name__)


class ProjectService:
    """Service for handling project operations"""
    
    def __init__(self):
        self.data_service = DataService()
    
    def get_current_project(self) -> ILEProject:
        """Get current project"""
        return self.data_service.get_project()
    
    def create_project(self, project: IRBaseElement) -> ILEProject:
        """Create new project"""
        logger.info(f"Creating new project {project.ref}")
        new_project = ILEProject(
            ref=project.ref,
            name=project.name,
            desc=project.desc,
            uuid=project.uuid
        )
        self.data_service.set_project(new_project)
        return self.data_service.get_project()
    
    def list_projects(self) -> List[str]:
        """List all projects"""
        projects_folder = Path(ILEConstants.PROJECTS_FOLDER)
        if not projects_folder.exists():
            return []
        
        return [
            f.name.replace(".irius", "") 
            for f in projects_folder.iterdir() 
            if f.is_file() and f.suffix == ".irius"
        ]
    
    def clean_folder(self, folder: str) -> None:
        """Clean specified folder"""
        allowed_folders = {
            "versions": ILEConstants.VERSIONS_FOLDER,
            "projects": ILEConstants.PROJECTS_FOLDER,
            "output": ILEConstants.OUTPUT_FOLDER
        }
        
        folder_to_clean = Path(allowed_folders.get(folder))
        if not folder_to_clean.exists():
            return
        
        for item in folder_to_clean.iterdir():
            try:
                if item.is_dir():
                    shutil.rmtree(item)
                    delete = True
                else:
                    item.unlink()
                    delete = True
                logger.info(f"Removed {folder}/{item.name}[{delete}]")
            except Exception as e:
                logger.error(f"Folder couldn't be removed: {folder}/{item.name}: {e}")
    
    def delete_version(self, version: str) -> None:
        """Delete version"""
        self.data_service.remove_version(version)
    
    def copy_version(self, version: str, ref: str) -> None:
        """Copy version"""
        v = self.data_service.get_version(version)
        # Deep copy using JSON serialization/deserialization
        deep_copy = ILEVersion.model_validate(json.loads(v.model_dump_json()))
        deep_copy.version = ref
        self.data_service.put_version(deep_copy)
    
    def load_project(self, project: ILEProject) -> ILEProject:
        """Load project"""
        self.data_service.set_project(project)
        return self.data_service.get_project()
    
    def save_project(self) -> None:
        """Save current project"""
        project_ref = self.data_service.get_project().ref
        
        logger.info(f"Saving project {project_ref}")
        project_path = Path(ILEConstants.PROJECTS_FOLDER) / f"{project_ref}.irius"
        
        try:
            with open(project_path, 'w') as f:
                json.dump(self.data_service.get_project().model_dump(), f, indent=2)
            logger.info(f"Saving project success: {project_ref}")
        except Exception as e:
            raise RuntimeError(f"Failed to save project: {e}")
    
    def load_project_from_file(self, project: str) -> ILEProject:
        """Load project from file"""
        new_project_path = Path(ILEConstants.PROJECTS_FOLDER) / f"{project}.irius"
        
        try:
            with open(new_project_path, 'r') as f:
                project_data = json.load(f)
            project_object = ILEProject.model_validate(project_data)
            self.data_service.set_project(project_object)
        except Exception as e:
            raise RuntimeError(f"Failed to load project: {e}")
        
        return self.data_service.get_project()
    
    def load_version_from_file(self, version: str) -> None:
        """Load version from file"""
        new_version_path = Path(ILEConstants.VERSIONS_FOLDER) / f"{version}.irius"
        
        try:
            with open(new_version_path, 'r') as f:
                version_data = json.load(f)
            v = ILEVersion.model_validate(version_data)
            self.data_service.put_version(v)
        except Exception as e:
            raise RuntimeError(f"Failed to load version: {e}")
    
    def list_version_names(self) -> VersionNamesResponse:
        """List version names"""
        project = self.data_service.get_project()
        return VersionNamesResponse(
            project=project.ref,
            versions=list(project.versions.keys())
        )
    
    def create_version(self, ref: str) -> None:
        """Create new version"""
        version = ILEVersion(version=ref)
        self.data_service.put_version(version)
    
    def get_project_report(self) -> IRProjectReport:
        """Get project report"""
        return self.data_service.get_project_report()
    
    def merge_libraries(self, merge_library_request: MergeLibraryRequest) -> List[str]:
        """Merge libraries"""
        src_version = self.data_service.get_version(merge_library_request.src_version)
        src_library = self.data_service.get_library(merge_library_request.src_version, merge_library_request.src_library)
        dst_version = self.data_service.get_version(merge_library_request.dst_version)
        dst_library = self.data_service.get_library(merge_library_request.dst_version, merge_library_request.dst_library)
        result = []
        
        # We have to copy components, risk patterns and rules to dstLibrary
        equal_version = src_version.version == dst_version.version
        
        # Components
        categories = []
        for c in src_library.component_definitions.values():
            if c not in dst_library.component_definitions.values():
                dst_library.component_definitions[c.uuid] = c
                result.append(f"Added component {c.ref}")
                if not equal_version:
                    categories.append(c.category_ref)
        
        # Standards
        for c in src_version.standards.values():
            if c.uuid not in dst_version.standards:
                dst_version.standards[c.uuid] = c
                result.append(f"Added standard {c.uuid}")
        
        # Rules (Naive copy)
        for c in src_library.rules:
            if c not in dst_library.rules:
                dst_library.rules.append(c)
                result.append(f"Added rule {c.name}")
        
        # Risk patterns
        for rp in src_library.risk_patterns.values():
            if rp.uuid not in dst_library.risk_patterns:
                dst_library.risk_patterns[rp.uuid] = rp
                result.append(f"Added risk pattern {rp.ref}")
        
        # Copy relations for risk patterns
        for rel in src_library.relations.values():
            if rel.uuid not in dst_library.relations:
                dst_library.relations[rel.uuid] = rel
                result.append(f"Added relation {rel.uuid}")
        
        # If the versions are different we need to copy more things
        if not equal_version:
            for c in categories:
                if c not in dst_version.categories:
                    dst_version.categories[c] = src_version.categories[c]
                    result.append(f"Added category {c}")
            
            for uc in src_version.usecases.values():
                if uc.uuid not in dst_version.usecases:
                    dst_version.usecases[uc.uuid] = uc
                    result.append(f"Added use case {uc.ref}")
            
            for t in src_version.threats.values():
                if t.uuid not in dst_version.threats:
                    dst_version.threats[t.uuid] = t
                    result.append(f"Added threat {t.ref}")
                    
                    for ref_key, ref_uuid in t.references.items():
                        if ref_uuid not in dst_version.references:
                            dst_version.references[ref_uuid] = src_version.references[ref_uuid]
                            result.append(f"Added reference {ref_uuid}")
                else:
                    dst_threat = dst_version.threats[t.uuid]
                    for ref_key, ref_uuid in t.references.items():
                        if ref_key not in dst_threat.references:
                            dst_threat.references[ref_key] = ref_uuid
                            if ref_uuid not in dst_version.references:
                                dst_version.references[ref_uuid] = src_version.references[ref_uuid]
                                result.append(f"Added reference {ref_uuid}")
            
            for w in src_version.weaknesses.values():
                if w.uuid not in dst_version.weaknesses:
                    dst_version.weaknesses[w.uuid] = w
                    result.append(f"Added weakness {w.ref}")
                    
                    for ref_key, ref_uuid in w.test.references.items():
                        if ref_uuid not in dst_version.references:
                            dst_version.references[ref_uuid] = src_version.references[ref_uuid]
                            result.append(f"Added reference {ref_uuid}")
                else:
                    dst_weakness = dst_version.weaknesses[w.uuid]
                    
                    for ref_key, ref_uuid in w.test.references.items():
                        if ref_key not in dst_weakness.test.references:
                            dst_weakness.test.references[ref_key] = ref_uuid
                            if ref_uuid not in dst_version.references:
                                dst_version.references[ref_uuid] = src_version.references[ref_uuid]
                                result.append(f"Added reference {ref_uuid}")
            
            for c in src_version.controls.values():
                if c.uuid not in dst_version.controls:
                    dst_version.controls[c.uuid] = c
                    result.append(f"Added control {c.ref}")
                    
                    for ref_key, ref_uuid in c.references.items():
                        if ref_uuid not in dst_version.references:
                            dst_version.references[ref_uuid] = src_version.references[ref_uuid]
                            result.append(f"Added reference {ref_uuid}")
                    
                    for ref_key, ref_uuid in c.test.references.items():
                        if ref_uuid not in dst_version.references:
                            dst_version.references[ref_uuid] = src_version.references[ref_uuid]
                            result.append(f"Added reference {ref_uuid}")
                else:
                    dst_control = dst_version.controls[c.uuid]
                    for ref_key, ref_uuid in c.references.items():
                        if ref_key not in dst_control.references:
                            dst_control.references[ref_key] = ref_uuid
                            if ref_uuid not in dst_version.references:
                                dst_version.references[ref_uuid] = src_version.references[ref_uuid]
                                result.append(f"Added reference {ref_uuid}")
                    
                    for ref_key, ref_uuid in c.test.references.items():
                        if ref_key not in dst_control.test.references:
                            dst_control.test.references[ref_key] = ref_uuid
                            if ref_uuid not in dst_version.references:
                                dst_version.references[ref_uuid] = src_version.references[ref_uuid]
                                result.append(f"Added reference {ref_uuid}")
        
        return result
    
    def generate_full_library_from_version(self, source: str) -> ILEVersion:
        """Generate full library from version"""
        full_version_name = f"full-version-{source}"
        full_library_name = f"full-library-{source}"
        
        if self.data_service.get_version(full_version_name) is not None:
            self.delete_version(full_version_name)
        
        full_version = ILEVersion(full_version_name)
        self.data_service.put_version(full_version)
        full_library = IRLibrary(
            ref=full_library_name,
            name=full_library_name,
            desc="",
            version="1",
            filename=f"{full_library_name}.xml",
            visible="true"
        )
        full_version.libraries[full_library_name] = full_library
        
        v = self.data_service.get_version(source)
        for l in v.libraries.values():
            merge_library_request = MergeLibraryRequest(
                src_version=v.version,
                src_library=l.ref,
                dst_version=full_version.version,
                dst_library=full_library.ref
            )
            self.merge_libraries(merge_library_request)
        
        self.data_service.get_project().versions[full_version.version] = full_version
        return full_version
