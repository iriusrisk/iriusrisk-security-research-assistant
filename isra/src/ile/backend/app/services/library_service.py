"""
Library service for IriusRisk Library Editor API
"""

import logging
import os
from pathlib import Path
from typing import Collection, Dict, List, Set

from isra.src.ile.backend.app.configuration.constants import ILEConstants
from isra.src.ile.backend.app.models import (
    ILEVersion, IRBaseElement, IRComponentDefinition, IRLibrary,
    IRRelation, IRRiskPattern, IRRiskPatternItem, IRRule,
    IRRuleAction, IRRuleCondition, IRThreatItem, IRUseCaseItem,
    Graph, Link, RuleNode, IRLibraryReport, IRMitigationItem,
    IRMitigationReport, IRMitigationRiskPattern, ComponentRequest,
    LibraryUpdateRequest, RelationRequest, RiskPatternRequest
)
from isra.src.ile.backend.app.services.data_service import DataService
from isra.src.ile.backend.app.facades.io_facade import IOFacade

logger = logging.getLogger(__name__)


class LibraryService:
    """Service for handling library operations"""
    
    def __init__(self):
        self.data_service = DataService()
        self.io_facade = IOFacade()
        self.exceptions = [
            ["GENERIC-SERVICE:AUTHN-SF", "CAPEC-16"],
            ["GENERIC-SERVICE:DATA-SENS:AUTHZ", "CAPEC-232"]
        ]
    
    def create_library_report(self, version_ref: str, library_ref: str) -> IRLibraryReport:
        """Create library report"""
        return self.data_service.create_library_report(version_ref, library_ref)
    
    def export_library(self, version_ref: str, library_ref: str, format: str) -> None:
        """Export library to specified format"""
        lib = self.data_service.get_library(version_ref, library_ref)
        
        if format == "xml":
            try:
                output_path = Path(ILEConstants.OUTPUT_FOLDER) / version_ref
                output_path.mkdir(parents=True, exist_ok=True)
                self.io_facade.export_library_xml(lib, self.data_service.get_version(version_ref), str(output_path))
            except Exception as e:
                raise RuntimeError("Couldn't export to XML") from e
        elif format == "xlsx":
            try:
                output_path = Path(ILEConstants.OUTPUT_FOLDER) / version_ref
                output_path.mkdir(parents=True, exist_ok=True)
                self.io_facade.export_library_xlsx(lib, self.data_service.get_version(version_ref), str(output_path))
            except Exception as e:
                raise RuntimeError("Couldn't export to XLSX") from e
    
    def create_rules_graph(self, version_ref: str, library_ref: str) -> Graph:
        """Create rules graph"""
        g = Graph()
        g.directed = True
        g.multigraph = False
        
        lib = self.data_service.get_library(version_ref, library_ref)
        rules = lib.rules
        risk_patterns = lib.risk_patterns
        component_definitions = {comp.ref: comp for comp in lib.component_definitions.values()}
        
        for r in rules:
            condition_ids = set()
            for c in r.conditions:
                new_condition = RuleNode(c.name, c.value, "CONDITION", component_definitions)
                if not g.has_node_value(new_condition.id):
                    g.nodes.append(new_condition)
                
                condition_ids.add(new_condition.id)
            
            for a in r.actions:
                new_action = RuleNode(a.name, a.value, "ACTION", risk_patterns)
                
                if not g.has_node_value(new_action.id):
                    g.nodes.append(new_action)
                
                for cond in condition_ids:
                    g.links.append(Link(cond, new_action.id))
        
        return g
    
    def check_mitigation(self, version_ref: str, library_ref: str) -> IRMitigationReport:
        """Check mitigation values"""
        version = self.data_service.get_version(version_ref)
        lib = version.get_library(library_ref)
        
        report = IRMitigationReport()
        
        for rp in lib.risk_patterns.values():
            s = IRMitigationRiskPattern(risk_pattern_ref=rp.ref)
            risk_pattern_tree = self.data_service.get_relations_in_tree(lib)
            rp_item = risk_pattern_tree.get(rp.uuid)
            
            if rp_item is not None:
                for uc in rp_item.usecases.values():
                    for t in uc.threats.values():
                        # If threat is an exception we continue to the next one
                        pass_exception = False
                        for except_item in self.exceptions:
                            if rp.ref == except_item[0] and t.ref == except_item[1]:
                                pass_exception = True
                                break
                        if pass_exception:
                            continue
                        
                        # First part: find if the threat has incorrect mitigation values
                        mitigation_count = 0
                        
                        threat_rels = [
                            rel for rel in lib.relations.values()
                            if (rel.risk_pattern_uuid == rp.uuid and
                                rel.usecase_uuid == uc.ref and
                                rel.threat_uuid == t.ref)
                        ]
                        
                        already_checked = set()
                        for rel in threat_rels:
                            if rel.control_uuid != "" and rel.control_uuid not in already_checked:
                                already_checked.add(rel.control_uuid)
                                mitigation_count += int(rel.mitigation)
                        
                        message = ""
                        error = False
                        
                        if mitigation_count != 100:
                            message = f"Error with mitigation: {mitigation_count}"
                            error = True
                        
                        if error:
                            logger.info(f"Risk pattern: {rp.ref} -> {t.ref}")
                            logger.info(message)
                            logger.info(f"Total mitigation: {mitigation_count}")
                            
                            item = IRMitigationItem(
                                usecase_ref=uc.ref,
                                threat_ref=t.ref,
                                message=message,
                                total=str(mitigation_count),
                                relations=threat_rels,
                                error=True
                            )
                            
                            s.threats.append(item)
            
            if s.threats:
                report.risk_patterns.append(s)
        
        return report
    
    def balance_mitigation(self, version_ref: str, library_ref: str) -> None:
        """Balance mitigation values to be 100 for every threat in the library"""
        version = self.data_service.get_version(version_ref)
        lib = version.get_library(library_ref)
        
        logger.info("Balancing mitigations...")
        for rp in lib.risk_patterns.values():
            logger.info(f"RP: {rp.ref}")
            risk_pattern_tree = self.data_service.get_relations_in_tree(lib)
            rp_item = risk_pattern_tree.get(rp.uuid)
            
            if rp_item is not None:
                for uc in rp_item.usecases.values():
                    for t in uc.threats.values():
                        # If threat is an exception we continue to the next one
                        pass_exception = False
                        for except_item in self.exceptions:
                            if rp.ref == except_item[0] and t.ref == except_item[1]:
                                pass_exception = True
                                break
                        if pass_exception:
                            continue
                        
                        logger.info(f"T: {t.ref}")
                        relation_list = []
                        threat_rels = [
                            rel for rel in lib.relations.values()
                            if (rel.risk_pattern_uuid == rp.uuid and
                                rel.usecase_uuid == uc.ref and
                                rel.threat_uuid == t.ref)
                        ]
                        
                        for rel in threat_rels:
                            if rel.control_uuid != "":
                                relation_list.append(rel)
                        
                        self._fix_mitigation_values(relation_list, 100)
        
        logger.info("Balanced!")
    
    def _fix_mitigation_values(self, all_relations: List[IRRelation], goal: int) -> None:
        """Fix mitigation values to reach goal"""
        if not all_relations:
            return
        
        # Check first if the mitigation sum the given value
        mitigation_sum = sum(int(rel.mitigation) for rel in all_relations)
        
        if mitigation_sum != goal:
            logger.info(f"Sum is {mitigation_sum} (Desired: {goal}). Fixing threat...")
            mean = goal // len(all_relations)
            remainder = goal % len(all_relations)
            
            for rel in all_relations:
                new_mit = mean
                
                if remainder != 0:
                    new_mit += remainder
                    remainder = 0
                
                if rel.mitigation != str(new_mit):
                    logger.info(f"Control: Updated mitigation for {rel.control_uuid}: {rel.mitigation} -> {new_mit}")
                    rel.mitigation = str(new_mit)
                else:
                    logger.info(f"No changes for {rel.control_uuid}")
    
    def update_library(self, version_ref: str, library_ref: str, new_lib: LibraryUpdateRequest) -> None:
        """Update library"""
        current_lib = self.data_service.get_library(version_ref, library_ref)
        current_lib.name = new_lib.name
        current_lib.desc = new_lib.desc
        current_lib.revision = new_lib.revision
        current_lib.filename = new_lib.filename
        current_lib.enabled = new_lib.enabled
    
    def list_components(self, version_ref: str, library: str) -> Collection[IRComponentDefinition]:
        """List components"""
        return self.data_service.get_library(version_ref, library).component_definitions.values()
    
    def add_component(self, version_ref: str, lib: str, body: ComponentRequest) -> IRComponentDefinition:
        """Add component"""
        v = self.data_service.get_version(version_ref)
        l = v.get_library(lib)
        comp = IRComponentDefinition(
            ref=body.ref,
            name=body.name,
            desc=body.desc,
            category_ref=body.category_ref,
            visible=body.visible
        )
        l.component_definitions[comp.uuid] = comp
        return comp
    
    def update_component(self, version_ref: str, lib: str, new_comp: IRComponentDefinition) -> IRComponentDefinition:
        """Update component"""
        v = self.data_service.get_version(version_ref)
        l = v.get_library(lib)
        l.component_definitions[new_comp.uuid] = new_comp
        return new_comp
    
    def delete_component(self, version_ref: str, lib: str, comp: IRComponentDefinition) -> None:
        """Delete component"""
        v = self.data_service.get_version(version_ref)
        l = v.get_library(lib)
        l.component_definitions.pop(comp.uuid, None)
    
    def list_risk_patterns(self, version_ref: str, library: str) -> Collection[IRRiskPattern]:
        """List risk patterns"""
        return self.data_service.get_library(version_ref, library).risk_patterns.values()
    
    def add_risk_pattern(self, version_ref: str, library_ref: str, request: RiskPatternRequest) -> IRRiskPattern:
        """Add risk pattern"""
        v = self.data_service.get_version(version_ref)
        l = v.get_library(library_ref)
        rp = IRRiskPattern(
            ref=request.ref,
            name=request.name,
            desc=request.desc
        )
        l.risk_patterns[rp.uuid] = rp
        return rp
    
    def update_risk_pattern(self, version_ref: str, lib: str, new_rp: RiskPatternRequest) -> IRRiskPattern:
        """Update risk pattern"""
        v = self.data_service.get_version(version_ref)
        l = v.get_library(lib)
        rp = l.risk_patterns[new_rp.uuid]
        
        if new_rp.ref is not None:
            rp.ref = new_rp.ref
        
        if new_rp.name is not None:
            rp.name = new_rp.name
        
        if new_rp.desc is not None:
            rp.desc = new_rp.desc
        
        l.risk_patterns[rp.uuid] = rp
        return rp
    
    def delete_risk_pattern(self, version_ref: str, lib: str, rp: IRRiskPattern) -> None:
        """Delete risk pattern"""
        v = self.data_service.get_version(version_ref)
        l = v.get_library(lib)
        l.risk_patterns.pop(rp.uuid, None)
    
    def list_relations(self, version_ref: str, library: str) -> Collection[IRRelation]:
        """List relations"""
        return self.data_service.get_library(version_ref, library).relations.values()
    
    def add_relation(self, version_ref: str, lib: str, body: RelationRequest) -> IRRelation:
        """Add relation"""
        v = self.data_service.get_version(version_ref)
        l = v.get_library(lib)
        rel = IRRelation(
            risk_pattern_uuid=body.risk_pattern_uuid,
            usecase_uuid=body.usecase_uuid,
            threat_uuid=body.threat_uuid,
            weakness_uuid=body.weakness_uuid,
            control_uuid=body.control_uuid,
            mitigation=body.mitigation
        )
        l.relations[rel.uuid] = rel
        return rel
    
    def update_relation(self, version_ref: str, lib: str, new_rel: IRRelation) -> IRRelation:
        """Update relation"""
        v = self.data_service.get_version(version_ref)
        l = v.get_library(lib)
        l.relations[new_rel.uuid] = new_rel
        return new_rel
    
    def delete_relation(self, version_ref: str, lib: str, rel: IRRelation) -> None:
        """Delete relation"""
        v = self.data_service.get_version(version_ref)
        l = v.get_library(lib)
        l.relations.pop(rel.uuid, None)
