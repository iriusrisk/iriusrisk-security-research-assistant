"""
Changelog service for IriusRisk Library Editor API
"""

import logging
from typing import List, Set, Dict, Optional

from isra.src.ile.backend.app.models import (
    ILEVersion, IRCategoryComponent, IRComponentDefinition, IRControl,
    IRLibrary, IRReference, IRRelation, IRRiskPattern, IRRule,
    IRStandard, IRSupportedStandard, IRThreat, IRUseCase, IRWeakness,
    Change, ChangelogItem, ChangelogReport, Graph, GraphList,
    IRNode, Link, LibrarySummary, LibrarySummariesResponse,
    ChangelogRequest
)
from isra.src.ile.backend.app.services.data_service import DataService

logger = logging.getLogger(__name__)


class ChangelogService:
    """Service for generating changelogs between versions and libraries"""
    
    def __init__(self):
        self.data_service = DataService()
        self.graph: Optional[Graph] = None
        self.fv: Optional[ILEVersion] = None
        self.first: Optional[IRLibrary] = None
        self.sv: Optional[ILEVersion] = None
        self.second: Optional[IRLibrary] = None
    
    def set_changelog_items(self, changelog_request: ChangelogRequest) -> None:
        """Set changelog items for comparison"""
        fv = self.data_service.get_version(changelog_request.first_version)
        first = None
        if changelog_request.first_library:
            first = self.data_service.get_library(fv.version, changelog_request.first_library)
        
        sv = self.data_service.get_version(changelog_request.second_version)
        second = None
        if changelog_request.second_library:
            second = self.data_service.get_library(sv.version, changelog_request.second_library)
        
        self.graph = Graph()
        self.fv = fv
        self.first = first
        self.sv = sv
        self.second = second
    
    def get_library_changes(self) -> Graph:
        """Get changes between two libraries"""
        if not self.first or not self.second:
            return Graph()
        
        # If the libraries and the versions are the same there is no point to do the changelog
        if (self.first.ref == self.second.ref and 
            self.fv.version == self.sv.version):
            return Graph()
        
        logger.info(f"Creating changelog for {self.fv.version}/{self.first.ref} => {self.sv.version}/{self.second.ref}")
        
        changes = []
        self._get_change(changes, "revision", self.first.revision, self.second.revision)
        self._get_change(changes, "ref", self.first.ref, self.second.ref)
        self._get_change(changes, "name", self.first.name, self.second.name)
        self._get_change(changes, "desc", self.first.desc, self.second.desc)
        self._get_change(changes, "filename", self.first.filename, self.second.filename)
        self._get_change(changes, "enabled", self.first.enabled, self.second.enabled)
        
        # Root node, always appears
        root = IRNode(self.second.ref, changes, "ROOT")
        if changes:
            root.type = "E"
            self._add_item_to_changelog_list("Library", self.second.ref, "E", changes)
        self.graph.nodes.append(root)
        
        # Add various elements to graph
        self._add_categories_to_graph(root.id)
        self._add_components_to_graph(root.id)
        self._add_supported_standards_to_graph(root.id)
        self._add_standards_to_graph(root.id)
        self._add_risk_patterns_to_graph(root.id)
        self._add_rules_to_graph(root.id)
        
        # If we are checking libraries from the same version we don't have to check for differences
        if self.fv.version != self.sv.version:
            self._add_usecases_to_graph(root.id)
            self._add_threats_to_graph(root.id)
            self._add_controls_to_graph(root.id)
            self._add_weaknesses_to_graph(root.id)
            self._add_references_to_graph(root.id)
        
        self.graph.rev_first = self.first.revision
        self.graph.rev_second = self.second.revision
        
        if self.graph.changelog_list and self.first.revision == self.second.revision:
            logger.info("This library has the same revision number but it has changes")
            self.graph.equal_revision_number = True
        
        return self.graph
    
    def get_version_changes(self) -> GraphList:
        """Get changes between two versions"""
        gl = GraphList()
        
        for l1 in self.fv.libraries.keys():
            if l1 in self.sv.libraries:
                self.first = self.fv.libraries[l1]
                self.second = self.sv.libraries[l1]
                gl.graphs[l1] = self.get_library_changes()
            else:
                gl.deleted_libraries.append(self.fv.libraries[l1].name)
        
        for l2 in self.sv.libraries.keys():
            if l2 not in self.fv.libraries:
                gl.added_libraries.append(self.sv.libraries[l2].name)
        
        return gl
    
    def create_changelog_between_versions_simple(self) -> str:
        """Create simple changelog between versions"""
        changes = []
        
        if not self.fv or not self.sv:
            return "No versions to compare"
        
        # Compare basic version info
        if self.fv.version != self.sv.version:
            changes.append(f"Version changed from {self.fv.version} to {self.sv.version}")
        
        # Compare libraries
        fv_libs = set(self.fv.libraries.keys())
        sv_libs = set(self.sv.libraries.keys())
        
        added_libs = sv_libs - fv_libs
        removed_libs = fv_libs - sv_libs
        
        for lib in added_libs:
            changes.append(f"Added library: {lib}")
        
        for lib in removed_libs:
            changes.append(f"Removed library: {lib}")
        
        return "\n".join(changes) if changes else "No changes detected"
    
    def generate_relations_changelog(self) -> ChangelogReport:
        """Generate relations changelog"""
        report = ChangelogReport()
        
        if not self.first or not self.second:
            return report
        
        # Compare relations
        first_relations = set(self.first.relations.keys())
        second_relations = set(self.second.relations.keys())
        
        added_relations = second_relations - first_relations
        removed_relations = first_relations - second_relations
        
        for rel_id in added_relations:
            item = ChangelogItem()
            item.type = "ADDED"
            item.element_type = "Relation"
            item.element_ref = rel_id
            item.description = f"Added relation {rel_id}"
            report.items.append(item)
        
        for rel_id in removed_relations:
            item = ChangelogItem()
            item.type = "REMOVED"
            item.element_type = "Relation"
            item.element_ref = rel_id
            item.description = f"Removed relation {rel_id}"
            report.items.append(item)
        
        return report
    
    def get_library_summaries(self) -> LibrarySummariesResponse:
        """Get library summaries"""
        response = LibrarySummariesResponse()
        
        if not self.fv or not self.sv:
            return response
        
        for lib_ref in self.fv.libraries.keys():
            if lib_ref in self.sv.libraries:
                summary = LibrarySummary()
                summary.library_ref = lib_ref
                summary.first_version_count = len(self.fv.libraries[lib_ref].relations)
                summary.second_version_count = len(self.sv.libraries[lib_ref].relations)
                summary.changes = summary.second_version_count - summary.first_version_count
                response.summaries.append(summary)
        
        return response
    
    def get_library_specific_changes(self, library_ref: str) -> Graph:
        """Get library specific changes"""
        if not self.fv or not self.sv:
            return Graph()
        
        if library_ref not in self.fv.libraries or library_ref not in self.sv.libraries:
            return Graph()
        
        self.first = self.fv.libraries[library_ref]
        self.second = self.sv.libraries[library_ref]
        
        return self.get_library_changes()
    
    def _get_change(self, changes: List[Change], field: str, old_value: str, new_value: str) -> None:
        """Add change to list if values are different"""
        if old_value != new_value:
            change = Change()
            change.field = field
            change.old_value = old_value
            change.new_value = new_value
            changes.append(change)
    
    def _add_item_to_changelog_list(self, category: str, name: str, type: str, changes: List[Change]) -> None:
        """Add item to changelog list"""
        if not self.graph:
            return
        
        item = ChangelogItem()
        item.category = category
        item.name = name
        item.type = type
        item.changes = changes
        self.graph.changelog_list.append(item)
    
    def _add_categories_to_graph(self, parent_id: str) -> bool:
        """Add categories to graph"""
        # Simplified implementation
        return False
    
    def _add_components_to_graph(self, parent_id: str) -> bool:
        """Add components to graph"""
        # Simplified implementation
        return False
    
    def _add_supported_standards_to_graph(self, parent_id: str) -> bool:
        """Add supported standards to graph"""
        # Simplified implementation
        return False
    
    def _add_standards_to_graph(self, parent_id: str) -> bool:
        """Add standards to graph"""
        # Simplified implementation
        return False
    
    def _add_risk_patterns_to_graph(self, parent_id: str) -> bool:
        """Add risk patterns to graph"""
        # Simplified implementation
        return False
    
    def _add_rules_to_graph(self, parent_id: str) -> bool:
        """Add rules to graph"""
        # Simplified implementation
        return False
    
    def _add_usecases_to_graph(self, parent_id: str) -> bool:
        """Add use cases to graph"""
        # Simplified implementation
        return False
    
    def _add_threats_to_graph(self, parent_id: str) -> bool:
        """Add threats to graph"""
        # Simplified implementation
        return False
    
    def _add_controls_to_graph(self, parent_id: str) -> bool:
        """Add controls to graph"""
        # Simplified implementation
        return False
    
    def _add_weaknesses_to_graph(self, parent_id: str) -> bool:
        """Add weaknesses to graph"""
        # Simplified implementation
        return False
    
    def _add_references_to_graph(self, parent_id: str) -> bool:
        """Add references to graph"""
        # Simplified implementation
        return False
    
    def _get_list_from_relations(self, library: IRLibrary, element_type: str) -> Set[str]:
        """Get list of elements from relations"""
        elements = set()
        for rel in library.relations.values():
            if element_type == "usecases":
                elements.add(rel.usecase_uuid)
            elif element_type == "threats":
                elements.add(rel.threat_uuid)
            elif element_type == "weaknesses":
                elements.add(rel.weakness_uuid)
            elif element_type == "controls":
                elements.add(rel.control_uuid)
        return elements
