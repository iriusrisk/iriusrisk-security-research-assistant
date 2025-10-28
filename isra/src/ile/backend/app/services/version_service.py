"""
Version service for IriusRisk Library Editor API
"""

import json
import logging
import os
import uuid
from pathlib import Path
from typing import Collection, List, Set, BinaryIO

from fastapi import UploadFile

from isra.src.ile.backend.app.configuration.constants import ILEConstants
from isra.src.ile.backend.app.configuration.properties_manager import PropertiesManager
from isra.src.ile.backend.app.models import (
    ILEVersion, IRCategoryComponent, IRComponentDefinition, IRControl,
    IRLibrary, IRReference, IRRelation, IRRiskPattern, IRRiskRating,
    IRStandard, IRSupportedStandard, IRThreat, IRUseCase, IRWeakness,
    IRSuggestions, IRVersionReport, CategoryRequest, ControlRequest,
    ControlUpdateRequest, ReferenceItemRequest, ReferenceRequest,
    StandardItemRequest, StandardRequest, SupportedStandardRequest,
    ThreatRequest, ThreatUpdateRequest, UsecaseRequest, WeaknessRequest
)
from isra.src.ile.backend.app.services.data_service import DataService
from isra.src.ile.backend.app.facades.io_facade import IOFacade

logger = logging.getLogger(__name__)


class VersionService:
    """Service for handling version operations"""
    
    def __init__(self):
        self.data_service = DataService()
        self.io_facade = IOFacade()
    
    def get_version(self, version_ref: str) -> ILEVersion:
        """Get version by reference"""
        return self.data_service.get_version(version_ref)
    
    def list_stored_versions(self) -> List[str]:
        """List stored versions"""
        versions_folder = Path(ILEConstants.VERSIONS_FOLDER)
        if not versions_folder.exists():
            return []
        
        return [
            f.name.replace(".irius", "") 
            for f in versions_folder.iterdir() 
            if f.is_file() and f.suffix == ".irius"
        ]
    
    def save_version(self, version_ref: str) -> None:
        """Save version to file"""
        logger.info(f"Saving version {version_ref}")
        version_path = Path(ILEConstants.VERSIONS_FOLDER) / f"{version_ref}.irius"
        
        try:
            v = self.data_service.get_version(version_ref)
            with open(version_path, 'w') as f:
                json.dump(v.model_dump(), f, indent=2)
            logger.info(f"Saving version success: {version_ref}")
        except Exception as e:
            raise RuntimeError("Failed to save version") from e
    
    def clean_version(self, version_ref: str) -> List[str]:
        """Clean unused elements from version"""
        logger.info(f"Cleaning version {version_ref}")
        removed_items = []
        v = self.data_service.get_version(version_ref)
        
        # Collect used elements
        used_risk_patterns: Set[str] = set()
        used_usecases: Set[str] = set()
        used_threats: Set[str] = set()
        used_weaknesses: Set[str] = set()
        used_controls: Set[str] = set()
        used_categories: Set[str] = set()
        used_references: Set[IRReference] = set()
        used_standards: Set[IRStandard] = set()
        used_supported_standards: Set[IRSupportedStandard] = set()
        
        for l in v.libraries.values():
            for comp in l.component_definitions.values():
                used_categories.add(comp.category_ref)
                used_risk_patterns.update(comp.risk_pattern_refs)
        
        # Remove unused elements (simplified implementation)
        # In a full implementation, you would remove unused elements here
        
        return removed_items
    
    def quick_reload_version(self, version_ref: str) -> None:
        """Quick reload version"""
        self.data_service.remove_version(version_ref)
        self.data_service.put_version(ILEVersion(version_ref))
        self.import_libraries_from_folder(version_ref)
    
    def create_version_report(self, version_ref: str) -> IRVersionReport:
        """Create version report"""
        return self.data_service.create_version_report(version_ref)
    
    def import_libraries_from_folder(self, version_ref: str) -> None:
        """Import libraries from configured folder"""
        folder = PropertiesManager.get_property(ILEConstants.MAIN_LIBRARY_FOLDER)
        if folder:
            folder_path = Path(folder)
            if folder_path.is_dir():
                self._import_files_recursively(folder_path, version_ref)
    
    def _import_files_recursively(self, directory: Path, version_ref: str) -> None:
        """Import files recursively from directory"""
        for file_path in directory.iterdir():
            if file_path.is_dir():
                self._import_files_recursively(file_path, version_ref)
            elif file_path.is_file():
                try:
                    if file_path.suffix == ".xml":
                        with open(file_path, 'rb') as f:
                            self.io_facade.import_library_xml(file_path.name, f, self.data_service.get_version(version_ref))
                    elif file_path.suffix == ".xlsx":
                        with open(file_path, 'rb') as f:
                            self.io_facade.import_library_xlsx(file_path.name, f, self.data_service.get_version(version_ref))
                except Exception as e:
                    logger.error(f"Error when importing {file_path.name}: {e}")
    
    def import_library_to_version(self, version_ref: str, submissions: List[UploadFile]) -> None:
        """Import library files to version"""
        for file in submissions:
            try:
                filename = file.filename
                if filename.endswith(".xml"):
                    self.io_facade.import_library_xml(filename, file.file, self.data_service.get_version(version_ref))
                elif filename.endswith(".xlsx"):
                    self.io_facade.import_library_xlsx(filename, file.file, self.data_service.get_version(version_ref))
            except Exception as e:
                logger.error(f"Error when importing {filename}: {e}")
                raise RuntimeError("Error when importing") from e
    
    def export_version_to_folder(self, version_ref: str, format: str) -> None:
        """Export version to folder"""
        logger.info(f"Exporting {version_ref} to {format}")
        version = self.data_service.get_version(version_ref)
        
        version_path = Path(ILEConstants.OUTPUT_FOLDER) / version.version
        version_path.mkdir(parents=True, exist_ok=True)
        
        try:
            for lib in version.libraries.values():
                if format == "xml":
                    self.io_facade.export_library_xml(lib, version, str(version_path))
                elif format == "xlsx":
                    self.io_facade.export_library_xlsx(lib, version, str(version_path))
        except Exception as e:
            logger.error(f"Error exporting version {version_ref}: {e}")
            raise RuntimeError("Error exporting version") from e
    
    def get_suggestions(self, version_ref: str, element_type: str, ref: str) -> IRSuggestions:
        """Get suggestions for element"""
        suggestions = IRSuggestions()
        # Simplified implementation - in full version would provide actual suggestions
        suggestions.suggestions = []
        return suggestions
    
    def fix_non_ascii_values(self, version_ref: str) -> None:
        """Fix non-ASCII values in version"""
        logger.info(f"Fixing non-ASCII values in version {version_ref}")
        # Simplified implementation - would fix non-ASCII characters
        pass
    
    # CRUD operations for various elements
    
    def list_supported_standards(self, version_ref: str) -> Collection[IRSupportedStandard]:
        """List supported standards"""
        return self.data_service.get_version(version_ref).supported_standards.values()
    
    def add_supported_standard(self, version_ref: str, st: SupportedStandardRequest) -> IRSupportedStandard:
        """Add supported standard"""
        v = self.data_service.get_version(version_ref)
        standard = IRSupportedStandard(
            ref=st.ref,
            name=st.name,
            desc=st.desc
        )
        v.supported_standards[standard.uuid] = standard
        return standard
    
    def update_supported_standard(self, version_ref: str, updated: IRSupportedStandard) -> IRSupportedStandard:
        """Update supported standard"""
        v = self.data_service.get_version(version_ref)
        v.supported_standards[updated.uuid] = updated
        return updated
    
    def delete_supported_standard(self, version_ref: str, st: IRSupportedStandard) -> None:
        """Delete supported standard"""
        v = self.data_service.get_version(version_ref)
        v.supported_standards.pop(st.uuid, None)
    
    def list_standards(self, version_ref: str) -> Collection[IRStandard]:
        """List standards"""
        return self.data_service.get_version(version_ref).standards.values()
    
    def add_standard(self, version_ref: str, st: StandardRequest) -> IRStandard:
        """Add standard"""
        v = self.data_service.get_version(version_ref)
        standard = IRStandard(
            ref=st.ref,
            name=st.name,
            desc=st.desc
        )
        v.standards[standard.uuid] = standard
        return standard
    
    def update_standard(self, version_ref: str, updated: IRStandard) -> IRStandard:
        """Update standard"""
        v = self.data_service.get_version(version_ref)
        v.standards[updated.uuid] = updated
        return updated
    
    def delete_standard(self, version_ref: str, st: IRStandard) -> None:
        """Delete standard"""
        v = self.data_service.get_version(version_ref)
        v.standards.pop(st.uuid, None)
    
    def get_reference(self, version_ref: str, uuid: str) -> IRReference:
        """Get reference by UUID"""
        return self.data_service.get_version(version_ref).references.get(uuid)
    
    def list_references(self, version_ref: str) -> Collection[IRReference]:
        """List references"""
        return self.data_service.get_version(version_ref).references.values()
    
    def add_reference(self, version_ref: str, body: ReferenceRequest) -> IRReference:
        """Add reference"""
        v = self.data_service.get_version(version_ref)
        ref = IRReference(
            ref=body.ref,
            name=body.name,
            desc=body.desc,
            url=body.url
        )
        v.references[ref.uuid] = ref
        return ref
    
    def update_reference(self, version_ref: str, body: IRReference) -> IRReference:
        """Update reference"""
        v = self.data_service.get_version(version_ref)
        v.references[body.uuid] = body
        return body
    
    def delete_reference(self, version_ref: str, body: IRReference) -> None:
        """Delete reference"""
        v = self.data_service.get_version(version_ref)
        v.references.pop(body.uuid, None)
    
    def list_categories(self, version_ref: str) -> Collection[IRCategoryComponent]:
        """List categories"""
        return self.data_service.get_version(version_ref).categories.values()
    
    def add_category(self, version_ref: str, body: CategoryRequest) -> IRCategoryComponent:
        """Add category"""
        v = self.data_service.get_version(version_ref)
        category = IRCategoryComponent(
            ref=body.ref,
            name=body.name,
            desc=body.desc
        )
        v.categories[category.uuid] = category
        return category
    
    def update_category(self, version_ref: str, new_cat: IRCategoryComponent) -> IRCategoryComponent:
        """Update category"""
        v = self.data_service.get_version(version_ref)
        v.categories[new_cat.uuid] = new_cat
        return new_cat
    
    def delete_category(self, version_ref: str, ref: str) -> None:
        """Delete category"""
        v = self.data_service.get_version(version_ref)
        # Find category by ref and remove
        for uuid, cat in v.categories.items():
            if cat.ref == ref:
                v.categories.pop(uuid)
                break
    
    def list_controls(self, version_ref: str) -> Collection[IRControl]:
        """List controls"""
        return self.data_service.get_version(version_ref).controls.values()
    
    def add_control(self, version_ref: str, control: ControlRequest) -> IRControl:
        """Add control"""
        v = self.data_service.get_version(version_ref)
        ctrl = IRControl(
            ref=control.ref,
            name=control.name,
            desc=control.desc,
            state=control.state
        )
        v.controls[ctrl.uuid] = ctrl
        return ctrl
    
    def update_control(self, version_ref: str, new_control: ControlUpdateRequest) -> IRControl:
        """Update control"""
        v = self.data_service.get_version(version_ref)
        control = v.controls[new_control.uuid]
        
        if new_control.ref is not None:
            control.ref = new_control.ref
        if new_control.name is not None:
            control.name = new_control.name
        if new_control.desc is not None:
            control.desc = new_control.desc
        if new_control.state is not None:
            control.state = new_control.state
        
        v.controls[control.uuid] = control
        return control
    
    def delete_control(self, version_ref: str, control: IRControl) -> None:
        """Delete control"""
        v = self.data_service.get_version(version_ref)
        v.controls.pop(control.uuid, None)
    
    def get_control(self, version_ref: str, uuid: str) -> IRControl:
        """Get control by UUID"""
        return self.data_service.get_version(version_ref).controls.get(uuid)
    
    def add_reference_to_element(self, version_ref: str, reference_item_request: ReferenceItemRequest) -> None:
        """Add reference to element"""
        v = self.data_service.get_version(version_ref)
        ref_uuid = reference_item_request.reference_uuid
        item_uuid = reference_item_request.item_uuid
        
        # Find the element and add reference
        # This is a simplified implementation
        pass
    
    def delete_reference_from_element(self, version_ref: str, reference_item_request: ReferenceItemRequest) -> None:
        """Delete reference from element"""
        # Simplified implementation
        pass
    
    def add_standard_to_element(self, version_ref: str, standard_item_request: StandardItemRequest) -> None:
        """Add standard to element"""
        # Simplified implementation
        pass
    
    def delete_standard_from_element(self, version_ref: str, standard_item_request: StandardItemRequest) -> None:
        """Delete standard from element"""
        # Simplified implementation
        pass
    
    def list_weaknesses(self, version_ref: str) -> Collection[IRWeakness]:
        """List weaknesses"""
        return self.data_service.get_version(version_ref).weaknesses.values()
    
    def add_weakness(self, version_ref: str, weakness: WeaknessRequest) -> IRWeakness:
        """Add weakness"""
        v = self.data_service.get_version(version_ref)
        w = IRWeakness(
            ref=weakness.ref,
            name=weakness.name,
            desc=weakness.desc,
            impact=weakness.impact
        )
        v.weaknesses[w.uuid] = w
        return w
    
    def update_weakness(self, version_ref: str, new_weakness: WeaknessRequest) -> IRWeakness:
        """Update weakness"""
        v = self.data_service.get_version(version_ref)
        weakness = v.weaknesses[new_weakness.uuid]
        
        if new_weakness.ref is not None:
            weakness.ref = new_weakness.ref
        if new_weakness.name is not None:
            weakness.name = new_weakness.name
        if new_weakness.desc is not None:
            weakness.desc = new_weakness.desc
        if new_weakness.impact is not None:
            weakness.impact = new_weakness.impact
        
        v.weaknesses[weakness.uuid] = weakness
        return weakness
    
    def delete_weakness(self, version_ref: str, weakness: IRWeakness) -> None:
        """Delete weakness"""
        v = self.data_service.get_version(version_ref)
        v.weaknesses.pop(weakness.uuid, None)
    
    def get_weakness(self, version_ref: str, uuid: str) -> IRWeakness:
        """Get weakness by UUID"""
        return self.data_service.get_version(version_ref).weaknesses.get(uuid)
    
    def get_threat(self, version_ref: str, uuid: str) -> IRThreat:
        """Get threat by UUID"""
        return self.data_service.get_version(version_ref).threats.get(uuid)
    
    def list_threats(self, version_ref: str) -> Collection[IRThreat]:
        """List threats"""
        return self.data_service.get_version(version_ref).threats.values()
    
    def add_threat(self, version_ref: str, threat: ThreatRequest) -> IRThreat:
        """Add threat"""
        v = self.data_service.get_version(version_ref)
        t = IRThreat(
            ref=threat.ref,
            name=threat.name,
            desc=threat.desc,
            risk_rating=threat.risk_rating
        )
        v.threats[t.uuid] = t
        return t
    
    def update_threat(self, version_ref: str, new_threat: ThreatUpdateRequest) -> IRThreat:
        """Update threat"""
        v = self.data_service.get_version(version_ref)
        threat = v.threats[new_threat.uuid]
        
        if new_threat.ref is not None:
            threat.ref = new_threat.ref
        if new_threat.name is not None:
            threat.name = new_threat.name
        if new_threat.desc is not None:
            threat.desc = new_threat.desc
        if new_threat.risk_rating is not None:
            threat.risk_rating = new_threat.risk_rating
        
        v.threats[threat.uuid] = threat
        return threat
    
    def delete_threat(self, version_ref: str, threat: IRThreat) -> None:
        """Delete threat"""
        v = self.data_service.get_version(version_ref)
        v.threats.pop(threat.uuid, None)
    
    def list_usecases(self, version_ref: str) -> Collection[IRUseCase]:
        """List use cases"""
        return self.data_service.get_version(version_ref).usecases.values()
    
    def add_usecase(self, version_ref: str, usecase: UsecaseRequest) -> IRUseCase:
        """Add use case"""
        v = self.data_service.get_version(version_ref)
        uc = IRUseCase(
            ref=usecase.ref,
            name=usecase.name,
            desc=usecase.desc
        )
        v.usecases[uc.uuid] = uc
        return uc
    
    def update_usecase(self, version_ref: str, new_usecase: IRUseCase) -> IRUseCase:
        """Update use case"""
        v = self.data_service.get_version(version_ref)
        v.usecases[new_usecase.uuid] = new_usecase
        return new_usecase
    
    def delete_usecase(self, version_ref: str, usecase: IRUseCase) -> None:
        """Delete use case"""
        v = self.data_service.get_version(version_ref)
        v.usecases.pop(usecase.uuid, None)
    
    def list_libraries(self, version_ref: str) -> Collection[str]:
        """List libraries"""
        return self.data_service.get_version(version_ref).libraries.keys()
    
    def create_library(self, version_ref: str, library_ref: str) -> IRLibrary:
        """Create library"""
        v = self.data_service.get_version(version_ref)
        library = IRLibrary(
            ref=library_ref,
            name=library_ref,
            desc="",
            version="1",
            filename=f"{library_ref}.xml",
            visible="true"
        )
        v.libraries[library_ref] = library
        return library
    
    def increment_library_revision(self, version_ref: str, library_ref: str) -> None:
        """Increment library revision"""
        v = self.data_service.get_version(version_ref)
        library = v.libraries[library_ref]
        current_rev = int(library.revision)
        library.revision = str(current_rev + 1)
    
    def delete_library(self, version_ref: str, library_ref: str) -> None:
        """Delete library"""
        v = self.data_service.get_version(version_ref)
        v.libraries.pop(library_ref, None)
