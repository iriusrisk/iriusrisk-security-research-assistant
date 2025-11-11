"""
Changelog service for IriusRisk Content Manager API
"""

import logging
import json
from typing import List, Set, Dict, Optional
from collections import OrderedDict

from isra.src.ile.backend.app.models import (
    ILEVersion, IRCategoryComponent, IRComponentDefinition, IRControl,
    IRLibrary, IRReference, IRRelation, IRRiskPattern, IRRule,
    IRStandard, IRSupportedStandard, IRThreat, IRUseCase, IRWeakness,
    Change, ChangelogItem, ChangelogReport, Graph, GraphList,
    IRNode, Link, LibrarySummary, LibrarySummariesResponse,
    ChangelogRequest, IRExtendedRelation,
    IRRiskPatternItem, IRUseCaseItem, IRThreatItem, IRWeaknessItem, IRControlItem
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
        fv = self.data_service.get_version(changelog_request.from_version)
        first = None
        if changelog_request.first_library:
            first = self.data_service.get_library(fv.version, changelog_request.library_ref)
        
        sv = self.data_service.get_version(changelog_request.to_version)
        second = None
        if changelog_request.second_library:
            second = self.data_service.get_library(sv.version, changelog_request.library_ref)
        
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
        
        self.graph.revFirst = self.first.revision
        self.graph.revSecond = self.second.revision
        
        if self.graph.changelogList and self.first.revision == self.second.revision:
            logger.info("This library has the same revision number but it has changes")
            self.graph.equalRevisionNumber = True
        
        return self.graph
    
    def get_version_changes(self) -> GraphList:
        """Get changes between two versions"""
        gl = GraphList()
        
        for l1 in self.fv.libraries.keys():
            if l1 in self.sv.libraries:
                self.first = self.fv.libraries[l1]
                self.second = self.sv.libraries[l1]
                # Initialize self.graph before calling get_library_changes() which uses it
                self.graph = Graph()
                gl.graphs[l1] = self.get_library_changes()
            else:
                gl.deleted_libraries.append(self.fv.libraries[l1].name)
        
        for l2 in self.sv.libraries.keys():
            if l2 not in self.fv.libraries:
                gl.added_libraries.append(self.sv.libraries[l2].name)
        
        return gl
    
    def create_changelog_between_versions_simple(self) -> str:
        """Create simple changelog between versions"""
        json_obj = {}
        gl = self.get_version_changes()
        
        items_allowed = {"RiskPattern", "Component Definitions", "Supported Standards", 
                        "Usecases", "Threats", "Weaknesses", "Controls", "Rules"}
        
        seen_map = {}
        
        for g in gl.graphs.values():
            for item in g.changelogList:
                if item.element in items_allowed:
                    element = item.element
                    
                    if element not in json_obj:
                        json_obj[element] = []
                        seen_map[element] = set()
                    
                    if item.elementRef not in seen_map[element]:
                        seen_map[element].add(item.elementRef)
                        
                        changes_list = []
                        for change in item.changes:
                            changes_list.append(change.field)
                        
                        if not changes_list:
                            changes_list = []
                        
                        obj = {
                            "ref": item.elementRef,
                            "action": item.action,
                            "changes": changes_list
                        }
                        
                        # Skip if action is E and no changes or only timestamp
                        if item.action == "E" and (not changes_list or (len(changes_list) == 1 and "timestamp" in changes_list)):
                            continue
                        
                        json_obj[element].append(obj)
        
        # Remove empty arrays
        keys_to_remove = [key for key, value in json_obj.items() if not value]
        for key in keys_to_remove:
            del json_obj[key]
        
        return json.dumps(json_obj)
    
    def generate_relations_changelog(self) -> ChangelogReport:
        """Generate relations changelog"""
        report = ChangelogReport()
        
        old_relations = []
        for lib in self.fv.libraries.values():
            for rel in lib.relations.values():
                old_relations.append(IRExtendedRelation.from_relation(lib.ref, "", rel))
        
        new_relations = []
        for lib in self.sv.libraries.values():
            for rel in lib.relations.values():
                new_relations.append(IRExtendedRelation.from_relation(lib.ref, "", rel))
        
        deleted = set(old_relations) - set(new_relations)
        report.deleted = deleted
        
        added = set(new_relations) - set(old_relations)
        report.added = added
        
        new_countermeasures = {}
        for c in new_relations:
            if not c.control_ref or c.control_ref == "":
                continue
            if c.control_ref not in self.fv.controls:
                if c.control_ref not in new_countermeasures:
                    new_countermeasures[c.control_ref] = []
                new_countermeasures[c.control_ref].append(c)
        
        report.new_countermeasures = new_countermeasures
        
        return report
    
    def get_library_summaries(self) -> LibrarySummariesResponse:
        """Get library summaries"""
        response = LibrarySummariesResponse()
        
        if not self.fv or not self.sv:
            return response
        
        # Get added libraries
        for lib_name in self.sv.libraries.keys():
            if lib_name not in self.fv.libraries:
                library = self.sv.libraries[lib_name]
                response.added_libraries.append(LibrarySummary(
                    ref=library.ref,
                    name=library.name,
                    status="ADDED",
                    old_revision=None,
                    new_revision=library.revision,
                    has_changes=True
                ))
        
        # Get deleted libraries
        for lib_name in self.fv.libraries.keys():
            if lib_name not in self.sv.libraries:
                library = self.fv.libraries[lib_name]
                response.deleted_libraries.append(LibrarySummary(
                    ref=library.ref,
                    name=library.name,
                    status="DELETED",
                    old_revision=library.revision,
                    new_revision=None,
                    has_changes=True
                ))
        
        # Get modified libraries
        for lib_name in self.fv.libraries.keys():
            if lib_name in self.sv.libraries:
                old_library = self.fv.libraries[lib_name]
                new_library = self.sv.libraries[lib_name]
                
                # Check if there are actual changes
                has_changes = (old_library.revision != new_library.revision or
                             old_library.name != new_library.name or
                             old_library.desc != new_library.desc or
                             old_library.filename != new_library.filename or
                             old_library.enabled != new_library.enabled)

                # Check if there are changes in the components, supported standards, standards, risk patterns, usecases, threats, weaknesses, controls, rules
                # Here I should call the method that compares two libraries, if the result is not empty, then there are changes
                # library_changes = self.get_library_specific_changes(new_library.ref)
                # if library_changes.changelogList:
                #     has_changes = True
                             
                if has_changes:
                    response.modified_libraries.append(LibrarySummary(
                        ref=new_library.ref,
                        name=new_library.name,
                        status="MODIFIED",
                        old_revision=old_library.revision,
                        new_revision=new_library.revision,
                        has_changes=has_changes
                    ))
        
        return response
    
    def get_library_specific_changes(self, library_ref: str) -> Graph:
        """Get library specific changes"""
        if not self.fv or not self.sv:
            raise ValueError(f"Library not found: {library_ref}")
        
        # Find the library in both versions
        first_library = None
        second_library = None
        
        for lib in self.fv.libraries.values():
            if lib.ref == library_ref:
                first_library = lib
                break
        
        for lib in self.sv.libraries.values():
            if lib.ref == library_ref:
                second_library = lib
                break
        
        if first_library is None and second_library is None:
            raise ValueError(f"Library not found: {library_ref}")
        
        # Create a new graph for this specific library comparison
        graph = Graph()
        
        if first_library is None:
            # This is a new library (added)
            root = IRNode(second_library.ref, [], "N")
            self._add_item_to_changelog_list("Library", second_library.ref, "N", [], graph)
            graph.nodes.append(root)
            graph.revFirst = ""
            graph.revSecond = second_library.revision
        elif second_library is None:
            # This is a deleted library
            root = IRNode(first_library.ref, [], "D")
            self._add_item_to_changelog_list("Library", first_library.ref, "D", [], graph)
            graph.nodes.append(root)
            graph.revFirst = first_library.revision
            graph.revSecond = ""
        else:
            # This is a modified library - use the existing logic
            self.first = first_library
            self.second = second_library
            # Initialize self.graph before calling get_library_changes() which uses it
            self.graph = Graph()
            graph = self.get_library_changes()
        
        return graph
    
    def _get_change(self, changes: List[Change], field: str, old_value: Optional[str], new_value: Optional[str]) -> None:
        """Add change to list if values are different"""
        old_str = old_value if old_value is not None else ""
        new_str = new_value if new_value is not None else ""
        if old_str != new_str:
            change = Change(field=field, old=old_str, new=new_str)
            changes.append(change)
    
    
    def _add_categories_to_graph(self, parent_id: str) -> bool:
        """Add categories to graph"""
        node_list = []
        
        cat_first = self._get_categories_of_components(self.first, self.fv)
        cat_second = self._get_categories_of_components(self.second, self.sv)
        
        for cat1 in cat_first:
            if cat1 in cat_second:
                c1 = self.fv.categories.get(cat1)
                c2 = self.sv.categories.get(cat1)
                if c1 and c2:
                    changes = []
                    self._get_change(changes, "name", c1.name or "", c2.name or "")
                    if changes:
                        c_node = IRNode(c2.ref, changes, "E")
                        self._add_item_to_changelog_list("Categories", c_node.name, "E", changes)
                        node_list.append(c_node)
            else:
                # Deleted
                c_node = IRNode(cat1, [], "D")
                if cat1 in self.fv.categories:
                    self._add_item_to_changelog_list("Categories", self.fv.categories[cat1].ref, "D", [])
                    node_list.append(c_node)
        
        for cat2 in cat_second:
            if cat2 not in cat_first:
                # Added
                c_node = IRNode(cat2, [], "N")
                if cat2 in self.sv.categories:
                    self._add_item_to_changelog_list("Categories", self.sv.categories[cat2].ref, "N", [])
                    node_list.append(c_node)
        
        return self._create_intermediate_node(parent_id, "categories", node_list)
    
    def _add_components_to_graph(self, parent_id: str) -> bool:
        """Add components to graph"""
        node_list = []
        
        # Create a mapping of ref to component for the second library
        components_second_by_ref = {c.ref: c for c in self.second.component_definitions.values()}
        
        # Added
        components_first = {c.ref for c in self.first.component_definitions.values()}
        for c2 in self.second.component_definitions.values():
            if c2.ref not in components_first:
                node = IRNode(c2.ref, [], "N")
                self._add_item_to_changelog_list("Component Definitions", c2.ref, "N", [])
                node_list.append(node)
        
        # Deleted
        components_second = {c.ref for c in self.second.component_definitions.values()}
        for c1 in self.first.component_definitions.values():
            if c1.ref not in components_second:
                node = IRNode(c1.ref, [], "D")
                self._add_item_to_changelog_list("Component Definitions", c1.ref, "D", [])
                node_list.append(node)
        
        # Modified
        for c1 in self.first.component_definitions.values():
            c2 = components_second_by_ref.get(c1.ref)
            if c2:
                changes = []
                self._get_change(changes, "name", c1.name or "", c2.name or "")
                self._get_change(changes, "desc", c1.desc or "", c2.desc or "")
                self._get_change(changes, "categoryRef", c1.category_ref or "", c2.category_ref or "")
                # Sort risk patterns before joining to ensure order-independent comparison
                risk_patterns1 = sorted(c1.risk_pattern_refs or [])
                risk_patterns2 = sorted(c2.risk_pattern_refs or [])
                self._get_change(changes, "riskPatterns", ",".join(risk_patterns1), ",".join(risk_patterns2))
                self._get_change(changes, "visible", c1.visible or "", c2.visible or "")
                
                if changes:
                    c_node = IRNode(c2.ref, changes, "E")
                    self._add_item_to_changelog_list("Component Definitions", c_node.name, "E", changes)
                    node_list.append(c_node)
        
        return self._create_intermediate_node(parent_id, "components", node_list)
    
    def _add_supported_standards_to_graph(self, parent_id: str) -> bool:
        """Add supported standards to graph"""
        node_list = []
        
        standards_first = self.fv.supported_standards
        standards_second = self.sv.supported_standards
        
        for key, st in standards_first.items():
            if key in standards_second:
                changes = []
                self._get_change(changes, "name", st.supported_standard_name or "", standards_second[key].supported_standard_name or "")
                if changes:
                    s_node = IRNode(key, changes, "E")
                    self._add_item_to_changelog_list("Supported Standards", s_node.name, "E", changes)
                    node_list.append(s_node)
            else:
                # Deleted
                s_node = IRNode(key, [], "D")
                self._add_item_to_changelog_list("Supported Standards", st.supported_standard_ref, "D", [])
                node_list.append(s_node)
        
        for key, st in standards_second.items():
            if key not in standards_first:
                # Added
                s_node = IRNode(key, [], "N")
                self._add_item_to_changelog_list("Supported Standards", st.supported_standard_ref, "N", [])
                node_list.append(s_node)
        
        return self._create_intermediate_node(parent_id, "supported_standards", node_list)
    
    def _add_standards_to_graph(self, parent_id: str) -> bool:
        """Add standards to graph at root level"""
        node_list = []
        
        standards_first = list(self.fv.standards.values())
        standards_second = list(self.sv.standards.values())
        
        for st1 in standards_first:
            found = False
            for st2 in standards_second:
                if (st1.standard_ref == st2.standard_ref and 
                    st1.supported_standard_ref == st2.supported_standard_ref):
                    found = True
                    break
            
            if not found:
                # Deleted
                s_node = IRNode(f"{st1.supported_standard_ref}-{st1.standard_ref}", [], "D")
                self._add_item_to_changelog_list("Standards", s_node.name, "D", [])
                node_list.append(s_node)
        
        for st2 in standards_second:
            found = False
            for st1 in standards_first:
                if (st1.standard_ref == st2.standard_ref and 
                    st1.supported_standard_ref == st2.supported_standard_ref):
                    found = True
                    break
            
            if not found:
                # Added
                s_node = IRNode(f"{st2.supported_standard_ref}-{st2.standard_ref}", [], "N")
                self._add_item_to_changelog_list("Standards", s_node.name, "N", [])
                node_list.append(s_node)
        
        return self._create_intermediate_node(parent_id, "standards", node_list)
    
    def _add_standards_to_graph_for_element(self, parent_id: str, element: str, intermediate: str, 
                                           standards1: Dict[str, str], standards2: Dict[str, str]) -> bool:
        """Add standards to graph for a specific element (like Control)"""
        node_list = []
        
        standards_first = set(standards1.keys())
        standards_second = set(standards2.keys())
        
        # Added
        for x in standards_second - standards_first:
            node = IRNode(x, [], "N")
            self._add_item_to_changelog_list(element, x, "N", [])
            node_list.append(node)
        
        # Deleted
        for x in standards_first - standards_second:
            node = IRNode(x, [], "D")
            self._add_item_to_changelog_list(element, x, "D", [])
            node_list.append(node)
        
        if intermediate:
            return self._create_intermediate_node(parent_id, intermediate, node_list)
        else:
            return self._add_nodes_to_graph(parent_id, node_list)
    
    def _add_risk_patterns_to_graph(self, parent_id: str) -> bool:
        """Add risk patterns to graph"""
        node_list = []
        
        for rp_key, rp in self.first.risk_patterns.items():
            if rp_key in self.second.risk_patterns:
                rp2 = self.second.risk_patterns[rp_key]
                changes = []
                self._get_change(changes, "name", rp.name or "", rp2.name or "")
                self._get_change(changes, "desc", rp.desc or "", rp2.desc or "")
                self._get_change(changes, "uuid", rp.uuid, rp2.uuid)
                
                n = IRNode(rp2.ref, changes, "E")
                changed = self._add_usecases_to_graph_for_risk_pattern(n.id, rp, rp2)
                
                if changes or changed:
                    self._add_item_to_changelog_list("RiskPattern", rp2.ref, "E", changes)
                    node_list.append(n)
            else:
                # Deleted
                node = IRNode(rp_key, [], "D")
                self._add_item_to_changelog_list("RiskPattern", rp.ref, "D", [])
                node_list.append(node)
        
        for rp_key, rp in self.second.risk_patterns.items():
            if rp_key not in self.first.risk_patterns:
                # Added
                node = IRNode(rp_key, [], "N")
                self._add_item_to_changelog_list("RiskPattern", rp.ref, "N", [])
                node_list.append(node)
        
        return self._create_intermediate_node(parent_id, "riskPatterns", node_list)
    
    def _add_usecases_to_graph_for_risk_pattern(self, parent_id: str, rp_first: IRRiskPattern, rp_second: IRRiskPattern) -> bool:
        """Add use cases to graph for a risk pattern"""
        node_list = []
        
        risk_pattern_tree1 = self.data_service.get_relations_in_tree(self.first)
        risk_pattern_tree2 = self.data_service.get_relations_in_tree(self.second)
        
        rp_item1 = risk_pattern_tree1.get(rp_first.ref)
        rp_item2 = risk_pattern_tree2.get(rp_second.ref)
        
        if rp_item1 and rp_item2:
            for uc_key, uc_item1 in rp_item1.usecases.items():
                if uc_key in rp_item2.usecases:
                    uc_item2 = rp_item2.usecases[uc_key]
                    
                    n = IRNode(uc_key, [], "E")
                    usecase_id = n.id
                    # Threats
                    t = self._add_threat_relations_to_graph(usecase_id, uc_item1, uc_item2)
                    
                    if t:
                        self._add_item_to_changelog_list("Relation:Threat", uc_item2.ref, "E", [])
                        node_list.append(n)
        
        return self._add_nodes_to_graph(parent_id, node_list)
    
    def _add_threat_relations_to_graph(self, parent_id: str, uc1: IRUseCaseItem, uc2: IRUseCaseItem) -> bool:
        """Add threat relations to graph"""
        node_list = []
        
        th1 = uc1.threats
        th2 = uc2.threats
        
        for threat_key, threat_item1 in th1.items():
            if threat_key in th2:
                threat_item2 = th2[threat_key]
                
                n = IRNode(threat_key, [], "E")
                threat_id = n.id
                # Weaknesses
                w = self._add_weakness_relations_to_graph(threat_id, threat_item1.weaknesses, threat_item2.weaknesses)
                
                # Orphaned Controls
                oc = self._add_control_relations_to_graph(threat_id, threat_item1.orphaned_controls, threat_item2.orphaned_controls)
                
                if w or oc:
                    self._add_item_to_changelog_list("Relation:Threat", threat_item2.ref, "E", [])
                    node_list.append(n)
            else:
                # Deleted
                t_node = IRNode(threat_key, [], "D")
                self._add_item_to_changelog_list("Relation:Threat", threat_item1.ref, "D", [])
                node_list.append(t_node)
        
        for threat_key, threat_item2 in th2.items():
            if threat_key not in th1:
                # Added
                t_node = IRNode(threat_key, [], "N")
                self._add_item_to_changelog_list("Relation:Threat", threat_item2.ref, "N", [])
                node_list.append(t_node)
        
        return self._add_nodes_to_graph(parent_id, node_list)
    
    def _add_weakness_relations_to_graph(self, parent_id: str, weaknesses1: Dict[str, IRWeaknessItem], 
                                         weaknesses2: Dict[str, IRWeaknessItem]) -> bool:
        """Add weakness relations to graph"""
        node_list = []
        
        for weakness_key, weakness1 in weaknesses1.items():
            if weakness_key in weaknesses2:
                weakness2 = weaknesses2[weakness_key]
                
                w_node = IRNode(weakness2.ref, [], "E")
                weakness_id = w_node.id
                
                # Controls
                weakness_changed = self._add_control_relations_to_graph(weakness_id, weakness1.controls, weakness2.controls)
                
                if weakness_changed:
                    self._add_item_to_changelog_list("Relation:Weakness", weakness2.ref, "E", [])
                    node_list.append(w_node)
            else:
                # Deleted weakness
                w_node = IRNode(weakness1.ref, [], "D")
                self._add_item_to_changelog_list("Relation:Weakness", w_node.name, "D", [])
                node_list.append(w_node)
        
        for weakness_key, weakness2 in weaknesses2.items():
            if weakness_key not in weaknesses1:
                # Added weakness
                w_node = IRNode(weakness2.ref, [], "N")
                self._add_item_to_changelog_list("Relation:Weakness", w_node.name, "N", [])
                node_list.append(w_node)
        
        return self._add_nodes_to_graph(parent_id, node_list)
    
    def _add_control_relations_to_graph(self, parent_id: str, controls1: Dict[str, IRControlItem], 
                                        controls2: Dict[str, IRControlItem]) -> bool:
        """Add control relations to graph"""
        node_list = []
        
        for control_key, control1 in controls1.items():
            if control_key in controls2:
                control2 = controls2[control_key]
                
                changes = []
                self._get_change(changes, "mitigation", control1.mitigation or "", control2.mitigation or "")
                
                if changes:
                    if self.graph.showMitigations:
                        c_node = IRNode(control2.ref, changes, "E")
                        node_list.append(c_node)
                        self._add_item_to_changelog_list("Relation:Control", control2.ref, "E", changes)
            else:
                # Deleted control
                c_node = IRNode(control1.ref, [], "D")
                self._add_item_to_changelog_list("Relation:Control", c_node.name, "D", [])
                node_list.append(c_node)
        
        for control_key, control2 in controls2.items():
            if control_key not in controls1:
                # Added control
                c_node = IRNode(control2.ref, [], "N")
                self._add_item_to_changelog_list("Relation:Control", c_node.name, "N", [])
                node_list.append(c_node)
        
        return self._add_nodes_to_graph(parent_id, node_list)
    
    def _add_rules_to_graph(self, parent_id: str) -> bool:
        """Add rules to graph"""
        node_list = []
        
        # Added
        rules_first = {r.name for r in self.first.rules}
        for r2 in self.second.rules:
            if r2.name not in rules_first:
                node = IRNode(r2.name, [], "N")
                self._add_item_to_changelog_list("Rules", r2.name, "N", [])
                node_list.append(node)
        
        # Deleted
        rules_second = {r.name for r in self.second.rules}
        for r1 in self.first.rules:
            if r1.name not in rules_second:
                node = IRNode(r1.name, [], "D")
                self._add_item_to_changelog_list("Rules", r1.name, "D", [])
                node_list.append(node)
        
        # Modified
        for r1 in self.first.rules:
            for r2 in self.second.rules:
                if r1.name == r2.name:
                    changes = []
                    self._get_change(changes, "name", r1.name or "", r2.name or "")
                    self._get_change(changes, "module", r1.module or "", r2.module or "")
                    self._get_change(changes, "gui", r1.gui or "", r2.gui or "")
                    
                    n = IRNode(r2.name, changes, "E")
                    
                    conditions = self._add_conditions_to_rule(n.id, r1, r2)
                    actions = self._add_actions_to_rule(n.id, r1, r2)
                    
                    if changes or conditions or actions:
                        self._add_item_to_changelog_list("Rules", r2.name, "E", changes)
                        node_list.append(n)
                    break
        
        return self._create_intermediate_node(parent_id, "rules", node_list)
    
    def _add_conditions_to_rule(self, parent_id: str, r1: IRRule, r2: IRRule) -> bool:
        """Add conditions to rule"""
        node_list = []
        
        condition_strings1 = {f"{c.field}####{c.name}####{c.value}" for c in r1.conditions}
        condition_strings2 = {f"{c.field}####{c.name}####{c.value}" for c in r2.conditions}
        
        for c1 in condition_strings1 - condition_strings2:
            split = c1.split("####")
            c_node = IRNode(str(split), [], "D")
            self._add_item_to_changelog_list("Rules", f"{r1.name}[Condition]{str(split)}", "D", [])
            node_list.append(c_node)
        
        for c2 in condition_strings2 - condition_strings1:
            split = c2.split("####")
            c_node = IRNode(str(split), [], "N")
            self._add_item_to_changelog_list("Rules", f"{r2.name}[Condition]{str(split)}", "N", [])
            node_list.append(c_node)
        
        return self._add_nodes_to_graph(parent_id, node_list)
    
    def _add_actions_to_rule(self, parent_id: str, r1: IRRule, r2: IRRule) -> bool:
        """Add actions to rule"""
        node_list = []
        
        action_strings1 = {f"{a.project}####{a.name}####{a.value}" for a in r1.actions}
        action_strings2 = {f"{a.project}####{a.name}####{a.value}" for a in r2.actions}
        
        for a1 in action_strings1 - action_strings2:
            split = a1.split("####")
            a_node = IRNode(str(split), [], "D")
            self._add_item_to_changelog_list("Rules", f"{r1.name}[Action]{str(split)}", "D", [])
            node_list.append(a_node)
        
        for a2 in action_strings2 - action_strings1:
            split = a2.split("####")
            a_node = IRNode(str(split), [], "N")
            self._add_item_to_changelog_list("Rules", f"{r2.name}[Action]{str(split)}", "N", [])
            node_list.append(a_node)
        
        return self._add_nodes_to_graph(parent_id, node_list)
    
    def _add_usecases_to_graph(self, parent_id: str) -> bool:
        """Add use cases to graph"""
        node_list = []
        
        usecase_first = self._get_list_from_relations(self.first, "usecases")
        usecase_second = self._get_list_from_relations(self.second, "usecases")
        
        for uc1 in usecase_first:
            if uc1 in usecase_second:
                u1 = self.fv.usecases.get(uc1)
                u2 = self.sv.usecases.get(uc1)
                if u1 and u2:
                    changes = []
                    self._get_change(changes, "name", u1.name or "", u2.name or "")
                    self._get_change(changes, "desc", u1.desc or "", u2.desc or "")
                    
                    node = IRNode(u2.ref, changes, "E")
                    
                    if changes:
                        self._add_item_to_changelog_list("Usecases", node.name, "E", changes)
                        node_list.append(node)
            else:
                # Deleted
                node = IRNode(uc1, [], "D")
                if uc1 in self.fv.usecases:
                    self._add_item_to_changelog_list("Usecases", self.fv.usecases[uc1].ref, "D", [])
                    node_list.append(node)
        
        for uc2 in usecase_second:
            if uc2 not in usecase_first:
                # Added
                node = IRNode(uc2, [], "N")
                if uc2 in self.sv.usecases:
                    self._add_item_to_changelog_list("Usecases", self.sv.usecases[uc2].ref, "N", [])
                    node_list.append(node)
        
        return self._create_intermediate_node(parent_id, "usecases", node_list)
    
    def _add_threats_to_graph(self, parent_id: str) -> bool:
        """Add threats to graph"""
        node_list = []
        
        threats_first = self._get_list_from_relations(self.first, "threats")
        threats_second = self._get_list_from_relations(self.second, "threats")
        
        for th1 in threats_first:
            if th1 in threats_second:
                t1 = self.fv.threats.get(th1)
                t2 = self.sv.threats.get(th1)
                if t1 and t2:
                    changes = []
                    self._get_change(changes, "name", t1.name or "", t2.name or "")
                    self._get_change(changes, "desc", t1.desc or "", t2.desc or "")
                    self._get_change(changes, "confidentiality", t1.risk_rating.confidentiality or "", t2.risk_rating.confidentiality or "")
                    self._get_change(changes, "integrity", t1.risk_rating.integrity or "", t2.risk_rating.integrity or "")
                    self._get_change(changes, "availability", t1.risk_rating.availability or "", t2.risk_rating.availability or "")
                    self._get_change(changes, "easeOfExploitation", t1.risk_rating.ease_of_exploitation or "", t2.risk_rating.ease_of_exploitation or "")
                    # Sort lists before joining to ensure order-independent comparison
                    mitre1 = sorted(t1.mitre or [])
                    mitre2 = sorted(t2.mitre or [])
                    self._get_change(changes, "mitre", ",".join(mitre1), ",".join(mitre2))
                    stride1 = sorted(t1.stride or [])
                    stride2 = sorted(t2.stride or [])
                    self._get_change(changes, "stride", ",".join(stride1), ",".join(stride2))
                    
                    node = IRNode(t2.ref, changes, "E")
                    
                    references = self._add_references_to_graph_for_element(node.id, "Threat:References", "references", 
                                                                        t1.references, t2.references)
                    
                    if changes or references:
                        self._add_item_to_changelog_list("Threats", node.name, "E", changes)
                        node_list.append(node)
            else:
                # Deleted
                node = IRNode(th1, [], "D")
                if th1 in self.fv.threats:
                    self._add_item_to_changelog_list("Threats", self.fv.threats[th1].ref, "D", [])
                    node_list.append(node)
        
        for th2 in threats_second:
            if th2 not in threats_first:
                # Added
                node = IRNode(th2, [], "N")
                if th2 in self.sv.threats:
                    self._add_item_to_changelog_list("Threats", self.sv.threats[th2].ref, "N", [])
                    node_list.append(node)
        
        return self._create_intermediate_node(parent_id, "threats", node_list)
    
    def _add_controls_to_graph(self, parent_id: str) -> bool:
        """Add controls to graph"""
        node_list = []
        
        control_first = self._get_list_from_relations(self.first, "controls")
        control_second = self._get_list_from_relations(self.second, "controls")
        
        for control1 in control_first:
            if control1 in control_second:
                c1 = self.fv.controls.get(control1)
                c2 = self.sv.controls.get(control1)
                if c1 and c2:
                    changes = []
                    self._get_change(changes, "name", c1.name or "", c2.name or "")
                    self._get_change(changes, "desc", c1.desc or "", c2.desc or "")
                    self._get_change(changes, "state", c1.state or "", c2.state or "")
                    self._get_change(changes, "cost", c1.cost or "", c2.cost or "")
                    self._get_change(changes, "steps", c1.test.steps or "", c2.test.steps or "")
                    # Sort lists before joining to ensure order-independent comparison
                    base_standard1 = sorted(c1.base_standard or [])
                    base_standard2 = sorted(c2.base_standard or [])
                    self._get_change(changes, "baseStandard", ",".join(base_standard1), ",".join(base_standard2))
                    base_standard_section1 = sorted(c1.base_standard_section or [])
                    base_standard_section2 = sorted(c2.base_standard_section or [])
                    self._get_change(changes, "baseStandardSection", ",".join(base_standard_section1), ",".join(base_standard_section2))
                    scope1 = sorted(c1.scope or [])
                    scope2 = sorted(c2.scope or [])
                    self._get_change(changes, "scope", ",".join(scope1), ",".join(scope2))
                    mitre1 = sorted(c1.mitre or [])
                    mitre2 = sorted(c2.mitre or [])
                    self._get_change(changes, "mitre", ",".join(mitre1), ",".join(mitre2))
                    
                    node = IRNode(c2.ref, changes, "E")
                    
                    standards = self._add_standards_to_graph_for_element(node.id, "Controls:Standards", "standards", 
                                                                      c1.standards, c2.standards)
                    references = self._add_references_to_graph_for_element(node.id, "Controls:References", "references", 
                                                                           c1.references, c2.references)
                    test_references = self._add_references_to_graph_for_element(node.id, "Controls:TestReferences", "testReferences", 
                                                                               c1.test.references, c2.test.references)
                    implementations = self._add_implementations_to_graph(node.id, "Controls:Implementations", "implementations", 
                                                                        set(c1.implementations or []), set(c2.implementations or []))
                    
                    if changes or references or test_references or standards or implementations:
                        self._add_item_to_changelog_list("Controls", node.name, "E", changes)
                        node_list.append(node)
            else:
                # Deleted
                node = IRNode(control1, [], "D")
                if control1 in self.fv.controls:
                    self._add_item_to_changelog_list("Controls", self.fv.controls[control1].ref, "D", [])
                    node_list.append(node)
        
        for control2 in control_second:
            if control2 not in control_first:
                # Added
                node = IRNode(control2, [], "N")
                if control2 in self.sv.controls:
                    self._add_item_to_changelog_list("Controls", self.sv.controls[control2].ref, "N", [])
                    node_list.append(node)
        
        return self._create_intermediate_node(parent_id, "controls", node_list)
    
    def _add_implementations_to_graph(self, parent_id: str, element: str, intermediate: str, 
                                     impl1: Set[str], impl2: Set[str]) -> bool:
        """Add implementations to graph"""
        node_list = []
        
        # Added
        for x in impl2 - impl1:
            node = IRNode(x, [], "N")
            self._add_item_to_changelog_list(element, x, "N", [])
            node_list.append(node)
        
        # Deleted
        for x in impl1 - impl2:
            node = IRNode(x, [], "D")
            self._add_item_to_changelog_list(element, x, "D", [])
            node_list.append(node)
        
        if intermediate:
            return self._create_intermediate_node(parent_id, intermediate, node_list)
        else:
            return self._add_nodes_to_graph(parent_id, node_list)
    
    def _add_weaknesses_to_graph(self, parent_id: str) -> bool:
        """Add weaknesses to graph"""
        node_list = []
        
        weakness_first = self._get_list_from_relations(self.first, "weaknesses")
        weakness_second = self._get_list_from_relations(self.second, "weaknesses")
        
        for weakness1 in weakness_first:
            if weakness1 in weakness_second:
                w1 = self.fv.weaknesses.get(weakness1)
                w2 = self.sv.weaknesses.get(weakness1)
                if w1 and w2:
                    changes = []
                    self._get_change(changes, "name", w1.name or "", w2.name or "")
                    self._get_change(changes, "desc", w1.desc or "", w2.desc or "")
                    self._get_change(changes, "impact", w1.impact or "", w2.impact or "")
                    self._get_change(changes, "steps", w1.test.steps or "", w2.test.steps or "")
                    
                    node = IRNode(w2.ref, changes, "E")
                    
                    test_references = self._add_references_to_graph_for_element(node.id, "Weaknesses:TestReferences", "testReferences", 
                                                                              w1.test.references, w2.test.references)
                    
                    if changes or test_references:
                        self._add_item_to_changelog_list("Weaknesses", node.name, "E", changes)
                        node_list.append(node)
            else:
                # Deleted
                node = IRNode(weakness1, [], "D")
                if weakness1 in self.fv.weaknesses:
                    self._add_item_to_changelog_list("Weaknesses", self.fv.weaknesses[weakness1].ref, "D", [])
                    node_list.append(node)
        
        for w2 in weakness_second:
            if w2 not in weakness_first:
                # Added
                node = IRNode(w2, [], "N")
                if w2 in self.sv.weaknesses:
                    self._add_item_to_changelog_list("Weaknesses", self.sv.weaknesses[w2].ref, "N", [])
                    node_list.append(node)
        
        return self._create_intermediate_node(parent_id, "weaknesses", node_list)
    
    def _add_references_to_graph(self, parent_id: str) -> bool:
        """Add references to graph at root level"""
        node_list = []
        
        # Collect references from relations in first library
        references_first = set()
        for rel in self.first.relations.values():
            if rel.threat_uuid and rel.threat_uuid in self.fv.threats:
                for ref_key in self.fv.threats[rel.threat_uuid].references.values():
                    if ref_key in self.fv.references:
                        references_first.add(self.fv.references[ref_key])
            
            if rel.weakness_uuid and rel.weakness_uuid in self.fv.weaknesses:
                for ref_key in self.fv.weaknesses[rel.weakness_uuid].test.references.values():
                    if ref_key in self.fv.references:
                        references_first.add(self.fv.references[ref_key])
            
            if rel.control_uuid and rel.control_uuid in self.fv.controls:
                for ref_key in self.fv.controls[rel.control_uuid].references.values():
                    if ref_key in self.fv.references:
                        references_first.add(self.fv.references[ref_key])
                for ref_key in self.fv.controls[rel.control_uuid].test.references.values():
                    if ref_key in self.fv.references:
                        references_first.add(self.fv.references[ref_key])
        
        # Collect references from relations in second library
        references_second = set()
        for rel in self.second.relations.values():
            if rel.threat_uuid and rel.threat_uuid in self.sv.threats:
                for ref_key in self.sv.threats[rel.threat_uuid].references.values():
                    if ref_key in self.sv.references:
                        references_second.add(self.sv.references[ref_key])
            
            if rel.weakness_uuid and rel.weakness_uuid in self.sv.weaknesses:
                for ref_key in self.sv.weaknesses[rel.weakness_uuid].test.references.values():
                    if ref_key in self.sv.references:
                        references_second.add(self.sv.references[ref_key])
            
            if rel.control_uuid and rel.control_uuid in self.sv.controls:
                for ref_key in self.sv.controls[rel.control_uuid].references.values():
                    if ref_key in self.sv.references:
                        references_second.add(self.sv.references[ref_key])
                for ref_key in self.sv.controls[rel.control_uuid].test.references.values():
                    if ref_key in self.sv.references:
                        references_second.add(self.sv.references[ref_key])
        
        for ref1 in references_first:
            found_ref = None
            for ref2 in references_second:
                if ref2.name == ref1.name:
                    found_ref = ref2
                    break
            
            if found_ref:
                # Modified references
                changes = []
                self._get_change(changes, "url", ref1.url or "", found_ref.url or "")
                
                if changes:
                    node = IRNode(ref1.name, changes, "E")
                    self._add_item_to_changelog_list("References", node.name, "E", changes)
                    node_list.append(node)
            else:
                # Deleted
                node = IRNode(ref1.name, [], "D")
                self._add_item_to_changelog_list("References", node.name, "D", [])
                node_list.append(node)
        
        for ref2 in references_second:
            found_ref = None
            for ref1 in references_first:
                if ref1.name == ref2.name:
                    found_ref = ref1
                    break
            
            if not found_ref:
                # Added references
                node = IRNode(ref2.name, [], "N")
                self._add_item_to_changelog_list("References", node.name, "N", [])
                node_list.append(node)
        
        return self._create_intermediate_node(parent_id, "references", node_list)
    
    def _add_references_to_graph_for_element(self, parent_id: str, element: str, intermediate: str, 
                                            references1: Dict[str, str], references2: Dict[str, str]) -> bool:
        """Add references to graph for a specific element"""
        node_list = []
        
        references_one = set(references1.keys())
        references_two = set(references2.keys())
        
        # Added
        for x in references_two - references_one:
            node = IRNode(x, [], "N")
            self._add_item_to_changelog_list(element, x, "N", [])
            node_list.append(node)
        
        # Deleted
        for x in references_one - references_two:
            node = IRNode(x, [], "D")
            self._add_item_to_changelog_list(element, x, "D", [])
            node_list.append(node)
        
        if intermediate:
            return self._create_intermediate_node(parent_id, intermediate, node_list)
        else:
            return self._add_nodes_to_graph(parent_id, node_list)
    
    def _get_list_from_relations(self, library: IRLibrary, element_type: str) -> Set[str]:
        """Get list of elements from relations"""
        elements = set()
        for rel in library.relations.values():
            if element_type == "usecases":
                if rel.usecase_uuid:
                    elements.add(rel.usecase_uuid)
            elif element_type == "threats":
                if rel.threat_uuid:
                    elements.add(rel.threat_uuid)
            elif element_type == "weaknesses":
                if rel.weakness_uuid:
                    elements.add(rel.weakness_uuid)
            elif element_type == "controls":
                if rel.control_uuid:
                    elements.add(rel.control_uuid)
        return elements
    
    def _get_categories_of_components(self, lib: IRLibrary, version: ILEVersion) -> Set[str]:
        """Get all category UUIDs from component definitions in library"""
        category_refs = set()
        for comp_def in lib.component_definitions.values():
            if comp_def.category_ref:
                category_refs.add(comp_def.category_ref)
        
        # Convert category references to UUIDs by looking up in version
        category_uuids = set()
        for category_ref in category_refs:
            for category in version.categories.values():
                if category.ref == category_ref:
                    category_uuids.add(category.uuid)
                    break
        
        return category_uuids
    
    def _add_node(self, node: IRNode) -> None:
        """Add node to graph"""
        self.graph.nodes.append(node)
    
    def _add_link(self, parent_id: str, child_id: str) -> None:
        """Add link to graph"""
        self.graph.links.append(Link(source=parent_id, target=child_id))
    
    def _create_intermediate_node(self, parent_id: str, intermediate_name: str, node_list: List[IRNode]) -> bool:
        """Create intermediate node with child nodes"""
        if not node_list:
            return False
        
        # Create intermediate node
        intermediate_node = IRNode(intermediate_name, "")
        self._add_node(intermediate_node)
        self._add_link(parent_id, intermediate_node.id)
        
        # Add child nodes and link them to intermediate node
        for node in node_list:
            self._add_node(node)
            self._add_link(intermediate_node.id, node.id)
        
        return True
    
    def _add_nodes_to_graph(self, parent_id: str, node_list: List[IRNode]) -> bool:
        """Add nodes directly to parent"""
        if not node_list:
            return False
        
        for node in node_list:
            self._add_node(node)
            self._add_link(parent_id, node.id)
        
        return True
    
    def _add_item_to_changelog_list(self, category: str, name: str, action: str, changes: List[Change], target_graph: Optional[Graph] = None) -> None:
        """Add item to changelog list"""
        graph_to_use = target_graph if target_graph else self.graph
        if not graph_to_use:
            return
        
        item = ChangelogItem()
        item.element = category
        item.elementRef = name
        item.action = action
        item.changes = changes
        # Set info based on action
        if action == "N":
            item.info = f"The element {name} has been added"
        elif action == "D":
            item.info = f"The element {name} has been deleted"
        elif action == "E":
            item.info = f"The element {name} has been modified"
        graph_to_use.changelogList.append(item)
