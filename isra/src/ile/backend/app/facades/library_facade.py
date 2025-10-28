"""
Library facade for IriusRisk Library Editor API
"""

from typing import Collection
from isra.src.ile.backend.app.models import (
    IRComponentDefinition, IRRelation, IRRiskPattern, Graph, 
    IRLibraryReport, IRMitigationReport, ComponentRequest, 
    LibraryUpdateRequest, RelationRequest, RiskPatternRequest
)
from isra.src.ile.backend.app.services.library_service import LibraryService


class LibraryFacade:
    """Library facade for handling library operations"""
    
    def __init__(self):
        self.library_service = LibraryService()
    
    def create_library_report(self, version_ref: str, library_ref: str) -> IRLibraryReport:
        """Create library report"""
        return self.library_service.create_library_report(version_ref, library_ref)
    
    def create_rules_graph(self, version_ref: str, library_ref: str) -> Graph:
        """Create rules graph"""
        return self.library_service.create_rules_graph(version_ref, library_ref)
    
    def check_mitigation(self, version_ref: str, library_ref: str) -> IRMitigationReport:
        """Check mitigation"""
        return self.library_service.check_mitigation(version_ref, library_ref)
    
    def balance_mitigation(self, version_ref: str, library_ref: str) -> None:
        """Balance mitigation"""
        self.library_service.balance_mitigation(version_ref, library_ref)
    
    def export_library(self, version_ref: str, library_ref: str, format: str) -> None:
        """Export library"""
        self.library_service.export_library(version_ref, library_ref, format)
    
    def update_library(self, version_ref: str, library_ref: str, new_lib: LibraryUpdateRequest) -> None:
        """Update library"""
        self.library_service.update_library(version_ref, library_ref, new_lib)
    
    def list_components(self, version_ref: str, library: str) -> Collection[IRComponentDefinition]:
        """List components"""
        return self.library_service.list_components(version_ref, library)
    
    def add_component(self, version_ref: str, lib: str, comp: ComponentRequest) -> IRComponentDefinition:
        """Add component"""
        return self.library_service.add_component(version_ref, lib, comp)
    
    def update_component(self, version_ref: str, lib: str, new_comp: IRComponentDefinition) -> IRComponentDefinition:
        """Update component"""
        return self.library_service.update_component(version_ref, lib, new_comp)
    
    def delete_component(self, version_ref: str, lib: str, comp: IRComponentDefinition) -> None:
        """Delete component"""
        self.library_service.delete_component(version_ref, lib, comp)
    
    def list_risk_patterns(self, version_ref: str, library: str) -> Collection[IRRiskPattern]:
        """List risk patterns"""
        return self.library_service.list_risk_patterns(version_ref, library)
    
    def add_risk_pattern(self, version_ref: str, library_ref: str, rp: RiskPatternRequest) -> IRRiskPattern:
        """Add risk pattern"""
        return self.library_service.add_risk_pattern(version_ref, library_ref, rp)
    
    def update_risk_pattern(self, version_ref: str, lib: str, new_rp: RiskPatternRequest) -> IRRiskPattern:
        """Update risk pattern"""
        return self.library_service.update_risk_pattern(version_ref, lib, new_rp)
    
    def delete_risk_pattern(self, version_ref: str, lib: str, rp: IRRiskPattern) -> None:
        """Delete risk pattern"""
        self.library_service.delete_risk_pattern(version_ref, lib, rp)
    
    def list_relations(self, version_ref: str, library: str) -> Collection[IRRelation]:
        """List relations"""
        return self.library_service.list_relations(version_ref, library)
    
    def add_relation(self, version_ref: str, lib: str, rel: RelationRequest) -> IRRelation:
        """Add relation"""
        return self.library_service.add_relation(version_ref, lib, rel)
    
    def update_relation(self, version_ref: str, lib: str, new_rel: IRRelation) -> IRRelation:
        """Update relation"""
        return self.library_service.update_relation(version_ref, lib, new_rel)
    
    def delete_relation(self, version_ref: str, lib: str, rel: IRRelation) -> None:
        """Delete relation"""
        self.library_service.delete_relation(version_ref, lib, rel)
