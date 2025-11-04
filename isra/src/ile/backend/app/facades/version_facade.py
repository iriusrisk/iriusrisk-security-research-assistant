"""
Version facade for IriusRisk Content Manager API
"""

from typing import Collection, List
from fastapi import UploadFile
from isra.src.ile.backend.app.models import (
    ILEVersion, IRCategoryComponent, IRControl, IRLibrary, IRReference, 
    IRStandard, IRSupportedStandard, IRThreat, IRUseCase, IRWeakness,
    IRSuggestions, IRTestReport, IRVersionReport, CategoryRequest, CategoryUpdateRequest,
    ControlRequest, ControlUpdateRequest, LibraryRequest, ReferenceItemRequest,
    StandardItemRequest, ReferenceRequest, ReferenceUpdateRequest, StandardRequest, StandardUpdateRequest, SuggestionRequest,
    SupportedStandardRequest, SupportedStandardUpdateRequest, ThreatRequest, ThreatUpdateRequest, 
    UsecaseRequest, UsecaseUpdateRequest, WeaknessRequest
)
from isra.src.ile.backend.app.models.requests import WeaknessUpdateRequest
from isra.src.ile.backend.app.services.version_service import VersionService
from isra.src.ile.backend.app.services.test_service import TestService


class VersionFacade:
    """Version facade for handling version operations"""
    
    def __init__(self):
        self.version_service = VersionService()
        self.test_service = TestService()
    
    def get_version(self, version_ref: str) -> ILEVersion:
        """Get version"""
        return self.version_service.get_version(version_ref)
    
    def list_stored_versions(self) -> List[str]:
        """List stored versions"""
        return self.version_service.list_stored_versions()
    
    def save_version(self, version_ref: str) -> None:
        """Save version"""
        self.version_service.save_version(version_ref)
    
    def clean_version(self, version_ref: str) -> List[str]:
        """Clean version"""
        return self.version_service.clean_version(version_ref)
    
    def create_version_report(self, version_ref: str) -> IRVersionReport:
        """Create version report"""
        return self.version_service.create_version_report(version_ref)
    
    def run_tests(self, version_ref: str) -> IRTestReport:
        """Run tests"""
        return self.test_service.run_tests(version_ref)
    
    def import_library_to_version(self, version_ref: str, submissions: List[UploadFile]) -> None:
        """Import library to version"""
        self.version_service.import_library_to_version(version_ref, submissions)
    
    def import_libraries_from_folder(self, version_ref: str) -> None:
        """Import libraries from folder"""
        self.version_service.import_libraries_from_folder(version_ref)
    
    def export_version_to_folder(self, version_ref: str, format: str) -> None:
        """Export version to folder"""
        self.version_service.export_version_to_folder(version_ref, format)
    
    def quick_reload_version(self, version_ref: str) -> None:
        """Quick reload version"""
        self.version_service.quick_reload_version(version_ref)
    
    def get_suggestions(self, version_ref: str, type: str, ref: str) -> IRSuggestions:
        """Get suggestions"""
        return self.version_service.get_suggestions(version_ref, type, ref)
    
    def fix_non_ascii_values(self, version_ref: str) -> None:
        """Fix non-ASCII values"""
        self.version_service.fix_non_ascii_values(version_ref)
    
    def list_supported_standards(self, version_ref: str) -> Collection[IRSupportedStandard]:
        """List supported standards"""
        return self.version_service.list_supported_standards(version_ref)
    
    def add_supported_standard(self, version_ref: str, st: SupportedStandardRequest) -> IRSupportedStandard:
        """Add supported standard"""
        return self.version_service.add_supported_standard(version_ref, st)
    
    def update_supported_standard(self, version_ref: str, updated: SupportedStandardUpdateRequest) -> IRSupportedStandard:
        """Update supported standard"""
        return self.version_service.update_supported_standard(version_ref, updated)
    
    def delete_supported_standard(self, version_ref: str, st: IRSupportedStandard) -> None:
        """Delete supported standard"""
        self.version_service.delete_supported_standard(version_ref, st)
    
    def list_standards(self, version_ref: str) -> Collection[IRStandard]:
        """List standards"""
        return self.version_service.list_standards(version_ref)
    
    def add_standard(self, version_ref: str, st: StandardRequest) -> IRStandard:
        """Add standard"""
        return self.version_service.add_standard(version_ref, st)
    
    def update_standard(self, version_ref: str, updated: StandardUpdateRequest) -> IRStandard:
        """Update standard"""
        return self.version_service.update_standard(version_ref, updated)
    
    def delete_standard(self, version_ref: str, st: IRStandard) -> None:
        """Delete standard"""
        self.version_service.delete_standard(version_ref, st)
    
    def get_reference(self, version_ref: str, uuid: str) -> IRReference:
        """Get reference by UUID"""
        return self.version_service.get_reference(version_ref, uuid)
    
    def list_references(self, version_ref: str) -> Collection[IRReference]:
        """List references"""
        return self.version_service.list_references(version_ref)
    
    def add_reference(self, version_ref: str, body: ReferenceRequest) -> IRReference:
        """Add reference"""
        return self.version_service.add_reference(version_ref, body)
    
    def update_reference(self, version_ref: str, body: ReferenceUpdateRequest) -> IRReference:
        """Update reference"""
        return self.version_service.update_reference(version_ref, body)
    
    def delete_reference(self, version_ref: str, body: IRReference) -> None:
        """Delete reference"""
        self.version_service.delete_reference(version_ref, body)
    
    def list_categories(self, version_ref: str) -> Collection[IRCategoryComponent]:
        """List categories"""
        return self.version_service.list_categories(version_ref)
    
    def add_category(self, version_ref: str, body: CategoryRequest) -> IRCategoryComponent:
        """Add category"""
        return self.version_service.add_category(version_ref, body)
    
    def update_category(self, version_ref: str, new_cat: CategoryUpdateRequest) -> IRCategoryComponent:
        """Update category"""
        return self.version_service.update_category(version_ref, new_cat)
    
    def delete_category(self, version_ref: str, ref: str) -> None:
        """Delete category"""
        self.version_service.delete_category(version_ref, ref)
    
    def list_controls(self, version_ref: str) -> Collection[IRControl]:
        """List controls"""
        return self.version_service.list_controls(version_ref)
    
    def add_control(self, version_ref: str, control: ControlRequest) -> IRControl:
        """Add control"""
        return self.version_service.add_control(version_ref, control)
    
    def update_control(self, version_ref: str, new_control: ControlUpdateRequest) -> IRControl:
        """Update control"""
        return self.version_service.update_control(version_ref, new_control)
    
    def delete_control(self, version_ref: str, control: IRControl) -> None:
        """Delete control"""
        self.version_service.delete_control(version_ref, control)
    
    def add_reference_to_control(self, version_ref: str, reference_item_request: ReferenceItemRequest) -> IRControl:
        """Add reference to control"""
        self.version_service.add_reference_to_element(version_ref, reference_item_request)
        return self.version_service.get_control(version_ref, reference_item_request.item_uuid)
    
    def delete_reference_from_control(self, version_ref: str, reference_item_request: ReferenceItemRequest) -> IRControl:
        """Delete reference from control"""
        self.version_service.delete_reference_from_element(version_ref, reference_item_request)
        return self.version_service.get_control(version_ref, reference_item_request.item_uuid)
    
    def add_standard_to_control(self, version_ref: str, standard_item_request: StandardItemRequest) -> IRControl:
        """Add standard to control"""
        self.version_service.add_standard_to_element(version_ref, standard_item_request)
        return self.version_service.get_control(version_ref, standard_item_request.item_uuid)
    
    def delete_standard_from_control(self, version_ref: str, standard_item_request: StandardItemRequest) -> IRControl:
        """Delete standard from control"""
        self.version_service.delete_standard_from_element(version_ref, standard_item_request)
        return self.version_service.get_control(version_ref, standard_item_request.item_uuid)
    
    def list_weaknesses(self, version_ref: str) -> Collection[IRWeakness]:
        """List weaknesses"""
        return self.version_service.list_weaknesses(version_ref)
    
    def add_weakness(self, version_ref: str, weakness: WeaknessRequest) -> IRWeakness:
        """Add weakness"""
        return self.version_service.add_weakness(version_ref, weakness)
    
    def update_weakness(self, version_ref: str, new_weakness: WeaknessUpdateRequest) -> IRWeakness:
        """Update weakness"""
        return self.version_service.update_weakness(version_ref, new_weakness)
    
    def delete_weakness(self, version_ref: str, weakness: IRWeakness) -> None:
        """Delete weakness"""
        self.version_service.delete_weakness(version_ref, weakness)
    
    def add_reference_to_weakness(self, version_ref: str, reference_item_request: ReferenceItemRequest) -> IRWeakness:
        """Add reference to weakness"""
        self.version_service.add_reference_to_element(version_ref, reference_item_request)
        return self.version_service.get_weakness(version_ref, reference_item_request.item_uuid)
    
    def delete_reference_from_weakness(self, version_ref: str, reference_item_request: ReferenceItemRequest) -> IRWeakness:
        """Delete reference from weakness"""
        self.version_service.delete_reference_from_element(version_ref, reference_item_request)
        return self.version_service.get_weakness(version_ref, reference_item_request.item_uuid)
    
    def get_threat(self, version_ref: str, uuid: str) -> IRThreat:
        """Get threat by UUID"""
        return self.version_service.get_threat(version_ref, uuid)
    
    def list_threats(self, version_ref: str) -> Collection[IRThreat]:
        """List threats"""
        return self.version_service.list_threats(version_ref)
    
    def add_threat(self, version_ref: str, threat: ThreatRequest) -> IRThreat:
        """Add threat"""
        return self.version_service.add_threat(version_ref, threat)
    
    def update_threat(self, version_ref: str, new_threat: ThreatUpdateRequest) -> IRThreat:
        """Update threat"""
        return self.version_service.update_threat(version_ref, new_threat)
    
    def delete_threat(self, version_ref: str, threat: IRThreat) -> None:
        """Delete threat"""
        self.version_service.delete_threat(version_ref, threat)
    
    def add_reference_to_threat(self, version_ref: str, reference_item_request: ReferenceItemRequest) -> IRThreat:
        """Add reference to threat"""
        self.version_service.add_reference_to_element(version_ref, reference_item_request)
        return self.version_service.get_threat(version_ref, reference_item_request.item_uuid)
    
    def delete_reference_from_threat(self, version_ref: str, reference_item_request: ReferenceItemRequest) -> IRThreat:
        """Delete reference from threat"""
        self.version_service.delete_reference_from_element(version_ref, reference_item_request)
        return self.version_service.get_threat(version_ref, reference_item_request.item_uuid)
    
    def list_usecases(self, version_ref: str) -> Collection[IRUseCase]:
        """List use cases"""
        return self.version_service.list_usecases(version_ref)
    
    def add_usecase(self, version_ref: str, usecase: UsecaseRequest) -> IRUseCase:
        """Add use case"""
        return self.version_service.add_usecase(version_ref, usecase)
    
    def update_usecase(self, version_ref: str, new_usecase: UsecaseUpdateRequest) -> IRUseCase:
        """Update use case"""
        return self.version_service.update_usecase(version_ref, new_usecase)
    
    def delete_usecase(self, version_ref: str, usecase: IRUseCase) -> None:
        """Delete use case"""
        self.version_service.delete_usecase(version_ref, usecase)
    
    def list_libraries(self, version_ref: str) -> Collection[str]:
        """List libraries"""
        return self.version_service.list_libraries(version_ref)
    
    def create_library(self, version_ref: str, library_ref: str) -> IRLibrary:
        """Create library"""
        return self.version_service.create_library(version_ref, library_ref)
    
    def increment_library_revision(self, version_ref: str, library_ref: str) -> None:
        """Increment library revision"""
        self.version_service.increment_library_revision(version_ref, library_ref)
    
    def delete_library(self, version_ref: str, library_ref: str) -> None:
        """Delete library"""
        self.version_service.delete_library(version_ref, library_ref)
