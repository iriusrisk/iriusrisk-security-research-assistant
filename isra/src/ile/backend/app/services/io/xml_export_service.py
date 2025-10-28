"""
XML export service for IriusRisk Library Editor API
"""

import logging
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Optional
from xml.etree.ElementTree import Element

from isra.src.ile.backend.app.models import (
    ILEVersion, IRCategoryComponent, IRComponentDefinition, IRControl,
    IRLibrary, IRReference, IRRelation, IRRiskPattern, IRRule,
    IRRuleAction, IRRuleCondition, IRStandard, IRSupportedStandard,
    IRTest, IRThreat, IRUseCase, IRWeakness
)
from isra.src.ile.backend.app.services.data_service import DataService
from isra.src.ile.backend.app.services.io.xml_service import XMLService

logger = logging.getLogger(__name__)


class XMLExportService:
    """Service for exporting libraries to XML format"""
    
    def __init__(self):
        self.data_service = DataService()
        self.xml_service = XMLService()
    
    def export_library_xml(self, lib: IRLibrary, version: ILEVersion, version_path: str) -> None:
        """Export library to XML file"""
        xml_file_path = Path(version_path) / lib.filename
        if not xml_file_path.suffix == ".xml":
            xml_file_path = xml_file_path.with_suffix(".xml")
        
        try:
            # Create root element
            root = ET.Element("library")
            root.set("ref", lib.ref)
            root.set("name", lib.name)
            root.set("enabled", lib.enabled)
            root.set("revision", lib.revision)
            root.set("tags", "")
            
            # Add description
            desc_elem = ET.SubElement(root, "desc")
            desc_elem.text = lib.desc
            
            # Add copyright comment
            year = datetime.now().year
            comment = f"Copyright (c) 2012-{year} IriusRisk SL. All rights reserved. The content of this library is the property of IriusRisk SL and may only be used in whole or in part with a valid license for IriusRisk."
            root.insert(0, ET.Comment(comment))
            
            # Add various elements
            self._set_component_definitions_and_categories(root, lib, version)
            self._set_supported_standards(root, lib, version)
            self._set_risk_patterns(root, lib, version)
            self._set_rules(root, lib)
            
            # Create tree and write to file
            tree = ET.ElementTree(root)
            tree.write(xml_file_path, encoding="utf-8", xml_declaration=True)
            
            # Validate XML
            is_valid = self.xml_service.validate_xml_schema(str(xml_file_path))
            logger.info(f"XSD Validation of {lib.ref}: {is_valid}")
            
        except Exception as e:
            logger.error(f"Error exporting library {lib.ref} to XML: {e}")
            raise RuntimeError(f"Failed to export library to XML: {e}") from e
    
    def _set_supported_standards(self, root: Element, lib: IRLibrary, version: ILEVersion) -> None:
        """Set supported standards in XML"""
        supported_standards_elem = ET.SubElement(root, "supportedStandards")
        supported_standard_uuids = set()
        
        # Get all controls used in this library
        control_uuids = set()
        for rp in lib.risk_patterns.values():
            relations = {rel for rel in lib.relations.values() if rel.risk_pattern_uuid == rp.uuid}
            for rel in relations:
                if rel.control_uuid:
                    control_uuids.add(rel.control_uuid)
        
        # Find all standards used by these controls
        for control_uuid in control_uuids:
            control = version.controls.get(control_uuid)
            if control:
                for standard_uuid in control.standards.values():
                    standard = version.standards.get(standard_uuid)
                    if standard:
                        # Find the supported standard by its ref
                        for supported_standard in version.supported_standards.values():
                            if supported_standard.ref == standard.supported_standard_ref:
                                supported_standard_uuids.add(supported_standard.uuid)
                                break
        
        # Export only the supported standards that are actually used
        if supported_standard_uuids:
            sorted_supported_standards = sorted(
                [version.supported_standards[uuid] for uuid in supported_standard_uuids if uuid in version.supported_standards],
                key=lambda x: x.ref
            )
            
            for supported_standard in sorted_supported_standards:
                std_elem = ET.SubElement(supported_standards_elem, "supportedStandard")
                std_elem.set("uuid", supported_standard.uuid)
                std_elem.set("ref", supported_standard.ref)
                std_elem.set("name", supported_standard.name)
    
    def _set_component_definitions_and_categories(self, root: Element, lib: IRLibrary, version: ILEVersion) -> None:
        """Set component definitions and categories in XML"""
        # Category components
        categories_elem = ET.SubElement(root, "categoryComponents")
        categories = set()
        for cd in lib.component_definitions.values():
            categories.add(cd.category_ref)
        
        # Collect and sort category components by ref
        sorted_categories = sorted(
            [cat for cat in version.categories.values() if cat.ref in categories],
            key=lambda x: x.ref
        )
        
        for cat in sorted_categories:
            cat_elem = ET.SubElement(categories_elem, "categoryComponent")
            cat_elem.set("uuid", cat.uuid)
            cat_elem.set("ref", cat.ref)
            cat_elem.set("name", cat.name)
        
        # Component definitions
        component_definitions_elem = ET.SubElement(root, "componentDefinitions")
        
        # Sort component definitions by ref
        sorted_component_definitions = sorted(lib.component_definitions.values(), key=lambda x: x.ref)
        
        for cd in sorted_component_definitions:
            cd_elem = ET.SubElement(component_definitions_elem, "componentDefinition")
            cd_elem.set("uuid", cd.uuid)
            cd_elem.set("ref", cd.ref)
            cd_elem.set("name", cd.name)
            cd_elem.set("desc", cd.desc)
            cd_elem.set("categoryRef", cd.category_ref)
            cd_elem.set("visible", cd.visible)
            
            risk_patterns_elem = ET.SubElement(cd_elem, "riskPatterns")
            for rp in cd.risk_pattern_refs:
                rp_elem = ET.SubElement(risk_patterns_elem, "riskPattern")
                rp_elem.set("ref", rp)
    
    def _set_risk_patterns(self, root: Element, lib: IRLibrary, version: ILEVersion) -> None:
        """Set risk patterns in XML"""
        risk_patterns_elem = ET.SubElement(root, "riskPatterns")
        
        # Sort risk patterns by ref
        sorted_risk_patterns = sorted(lib.risk_patterns.values(), key=lambda x: x.ref)
        
        for rp in sorted_risk_patterns:
            rp_elem = ET.SubElement(risk_patterns_elem, "riskPattern")
            rp_elem.set("uuid", rp.uuid)
            rp_elem.set("ref", rp.ref)
            rp_elem.set("name", rp.name)
            rp_elem.set("desc", rp.desc)
            
            # Tags
            ET.SubElement(rp_elem, "tags")
            
            # Get controls and weaknesses used in this risk pattern
            control_refs, weakness_refs = self._fill_controls_and_weaknesses(rp, lib)
            
            # Weaknesses
            self._set_weaknesses(rp_elem, version, weakness_refs)
            
            # Controls
            self._set_controls(rp_elem, version, control_refs)
            
            # Use cases
            self._set_usecases(rp_elem, version, rp, lib)
    
    def _fill_controls_and_weaknesses(self, rp: IRRiskPattern, lib: IRLibrary) -> tuple[Set[str], Set[str]]:
        """Fill controls and weaknesses used in risk pattern"""
        control_refs = set()
        weakness_refs = set()
        
        risk_pattern_tree = self.data_service.get_relations_in_tree(lib)
        rp_item = risk_pattern_tree.get(rp.uuid)
        
        if rp_item:
            for uc in rp_item.usecases.values():
                for t in uc.threats.values():
                    for w in t.weaknesses.values():
                        weakness_refs.add(w.ref)
                        for c in w.controls.values():
                            control_refs.add(c.ref)
                    
                    for c in t.orphaned_controls.values():
                        control_refs.add(c.ref)
        
        return control_refs, weakness_refs
    
    def _set_usecases(self, rp_elem: Element, version: ILEVersion, rp: IRRiskPattern, lib: IRLibrary) -> None:
        """Set use cases in XML"""
        usecases_elem = ET.SubElement(rp_elem, "usecases")
        
        risk_pattern_tree = self.data_service.get_relations_in_tree(lib)
        rp_item = risk_pattern_tree.get(rp.uuid)
        
        if rp_item:
            # Sort use cases by ref
            sorted_usecases = sorted(
                [version.usecases[uc.ref] for uc in rp_item.usecases.values() if uc.ref in version.usecases],
                key=lambda x: x.ref
            )
            
            for usecase in sorted_usecases:
                # Find the corresponding use case item
                uc = next((item for item in rp_item.usecases.values() if item.ref == usecase.uuid), None)
                if not uc:
                    continue
                
                uc_elem = ET.SubElement(usecases_elem, "usecase")
                uc_elem.set("uuid", usecase.uuid)
                uc_elem.set("ref", usecase.ref)
                uc_elem.set("name", usecase.name)
                uc_elem.set("desc", usecase.desc)
                uc_elem.set("library", "")
                
                # Threats
                threats_elem = ET.SubElement(uc_elem, "threats")
                
                # Sort threats by ref
                sorted_threats = sorted(
                    [version.threats[threat_item.ref] for threat_item in uc.threats.values() 
                     if threat_item.ref in version.threats],
                    key=lambda x: x.ref
                )
                
                for th in sorted_threats:
                    # Find the corresponding threat item
                    threat_item = next((item for item in uc.threats.values() 
                                      if version.threats.get(item.ref) and 
                                      version.threats[item.ref].uuid == th.uuid), None)
                    if not threat_item:
                        continue
                    
                    th_elem = ET.SubElement(threats_elem, "threat")
                    th_elem.set("uuid", th.uuid)
                    th_elem.set("ref", th.ref)
                    th_elem.set("name", th.name)
                    th_elem.set("state", "Expose")
                    th_elem.set("source", "MANUAL")
                    th_elem.set("library", "")
                    
                    # Description
                    desc_elem = ET.SubElement(th_elem, "desc")
                    desc_elem.text = th.desc
                    
                    # Risk rating
                    rr_elem = ET.SubElement(th_elem, "riskRating")
                    if th.risk_rating:
                        rr_elem.set("confidentiality", th.risk_rating.confidentiality)
                        rr_elem.set("integrity", th.risk_rating.integrity)
                        rr_elem.set("availability", th.risk_rating.availability)
                        rr_elem.set("easeOfExploitation", th.risk_rating.ease_of_exploitation)
                    else:
                        rr_elem.set("confidentiality", "")
                        rr_elem.set("integrity", "")
                        rr_elem.set("availability", "")
                        rr_elem.set("easeOfExploitation", "")
                    
                    # References
                    refs_elem = ET.SubElement(th_elem, "references")
                    for ref_key, ref_uuid in th.references.items():
                        reference = version.references.get(ref_uuid)
                        if reference:
                            ref_elem = ET.SubElement(refs_elem, "reference")
                            ref_elem.set("uuid", ref_key)
                            ref_elem.set("name", reference.name)
                            ref_elem.set("url", reference.url)
                    
                    # Weaknesses
                    weaknesses_elem = ET.SubElement(th_elem, "weaknesses")
                    for w_ref, w_item in threat_item.weaknesses.items():
                        w_elem = ET.SubElement(weaknesses_elem, "weakness")
                        w_elem.set("ref", version.weaknesses[w_ref].ref)
                        
                        # Countermeasures
                        countermeasures_elem = ET.SubElement(w_elem, "countermeasures")
                        for c_ref, c_item in w_item.controls.items():
                            cm_elem = ET.SubElement(countermeasures_elem, "countermeasure")
                            cm_elem.set("ref", version.controls[c_item.ref].ref)
                            cm_elem.set("mitigation", c_item.mitigation)
                    
                    # Countermeasures
                    countermeasures_elem = ET.SubElement(th_elem, "countermeasures")
                    for c_ref, mitigation in threat_item.controls.items():
                        cm_elem = ET.SubElement(countermeasures_elem, "countermeasure")
                        cm_elem.set("ref", version.controls[c_ref].ref)
                        cm_elem.set("mitigation", mitigation)
                    
                    # Orphaned controls
                    for c_ref, c_item in threat_item.orphaned_controls.items():
                        cm_elem = ET.SubElement(countermeasures_elem, "countermeasure")
                        cm_elem.set("ref", version.controls[c_item.ref].ref)
                        cm_elem.set("mitigation", c_item.mitigation)
                    
                    # Custom fields
                    custom_fields_elem = ET.SubElement(th_elem, "customFields")
                    
                    mitre_elem = ET.SubElement(custom_fields_elem, "customField")
                    mitre_elem.set("ref", "SF-T-MITRE")
                    mitre_elem.set("value", "|".join(th.mitre or []))
                    
                    stride_elem = ET.SubElement(custom_fields_elem, "customField")
                    stride_elem.set("ref", "SF-T-STRIDE-LM")
                    stride_elem.set("value", "|".join(th.stride or []))
    
    def _set_controls(self, rp_elem: Element, version: ILEVersion, control_refs: Set[str]) -> None:
        """Set controls in XML"""
        countermeasures_elem = ET.SubElement(rp_elem, "countermeasures")
        
        # Sort controls by ref
        sorted_controls = sorted(
            [control for control in version.controls.values() if control.uuid in control_refs],
            key=lambda x: x.ref
        )
        
        for ctr in sorted_controls:
            cm_elem = ET.SubElement(countermeasures_elem, "countermeasure")
            cm_elem.set("uuid", ctr.uuid)
            cm_elem.set("ref", ctr.ref)
            cm_elem.set("name", ctr.name)
            cm_elem.set("platform", "")
            cm_elem.set("cost", ctr.cost)
            cm_elem.set("risk", "0")
            cm_elem.set("state", ctr.state)
            cm_elem.set("library", "")
            cm_elem.set("source", "MANUAL")
            
            # Description
            desc_elem = ET.SubElement(cm_elem, "desc")
            desc_elem.text = ctr.desc
            
            # Implementations
            impls_elem = ET.SubElement(cm_elem, "implementations")
            for imp in ctr.implementations:
                imp_parts = imp.split("_::_", 1)
                platform = imp_parts[0] if len(imp_parts) > 0 else ""
                desc = imp_parts[1] if len(imp_parts) > 1 else ""
                
                impl_elem = ET.SubElement(impls_elem, "implementation")
                impl_elem.set("platform", platform)
                
                impl_desc_elem = ET.SubElement(impl_elem, "desc")
                impl_desc_elem.text = desc
            
            # References
            refs_elem = ET.SubElement(cm_elem, "references")
            for ref_key, ref_uuid in ctr.references.items():
                reference = version.references.get(ref_uuid)
                if reference:
                    ref_elem = ET.SubElement(refs_elem, "reference")
                    ref_elem.set("uuid", ref_key)
                    ref_elem.set("name", reference.name)
                    ref_elem.set("url", reference.url)
            
            # Standards
            standards_elem = ET.SubElement(cm_elem, "standards")
            for std_key, std_uuid in ctr.standards.items():
                standard = version.standards.get(std_uuid)
                if standard:
                    std_elem = ET.SubElement(standards_elem, "standard")
                    std_elem.set("uuid", std_key)
                    std_elem.set("ref", standard.standard_ref)
                    std_elem.set("supportedStandardRef", standard.supported_standard_ref)
            
            # Custom fields
            custom_fields_elem = ET.SubElement(cm_elem, "customFields")
            
            mitre_elem = ET.SubElement(custom_fields_elem, "customField")
            mitre_elem.set("ref", "SF-C-MITRE")
            mitre_elem.set("value", "|".join(ctr.mitre or []))
            
            base_standard_elem = ET.SubElement(custom_fields_elem, "customField")
            base_standard_elem.set("ref", "SF-C-STANDARD-BASELINE")
            base_standard_elem.set("value", "|".join(ctr.base_standard or []))
            
            base_standard_section_elem = ET.SubElement(custom_fields_elem, "customField")
            base_standard_section_elem.set("ref", "SF-C-STANDARD-SECTION")
            base_standard_section_elem.set("value", "|".join(ctr.base_standard_section or []))
            
            scope_elem = ET.SubElement(custom_fields_elem, "customField")
            scope_elem.set("ref", "SF-C-SCOPE")
            scope_elem.set("value", "|".join(ctr.scope or []))
            
            # Test
            self._set_test(cm_elem, version, ctr.test)
    
    def _set_weaknesses(self, rp_elem: Element, version: ILEVersion, weakness_refs: Set[str]) -> None:
        """Set weaknesses in XML"""
        weaknesses_elem = ET.SubElement(rp_elem, "weaknesses")
        
        # Sort weaknesses by ref
        sorted_weaknesses = sorted(
            [weakness for weakness in version.weaknesses.values() if weakness.uuid in weakness_refs],
            key=lambda x: x.ref
        )
        
        for weak in sorted_weaknesses:
            w_elem = ET.SubElement(weaknesses_elem, "weakness")
            w_elem.set("uuid", weak.uuid)
            w_elem.set("ref", weak.ref)
            w_elem.set("name", weak.name)
            w_elem.set("state", "0")
            w_elem.set("impact", weak.impact)
            
            # Description
            desc_elem = ET.SubElement(w_elem, "desc")
            desc_elem.text = weak.desc
            
            # Test
            self._set_test(w_elem, version, weak.test)
    
    def _set_test(self, parent_elem: Element, version: ILEVersion, test: IRTest) -> None:
        """Set test in XML"""
        test_elem = ET.SubElement(parent_elem, "test")
        test_elem.set("uuid", test.uuid)
        test_elem.set("expiryDate", "")
        test_elem.set("expiryPeriod", "0")
        
        # Steps
        if test.steps:
            steps_elem = ET.SubElement(test_elem, "steps")
            steps_elem.text = test.steps
        else:
            ET.SubElement(test_elem, "steps")
        
        # Notes
        ET.SubElement(test_elem, "notes")
        
        # Source
        source_elem = ET.SubElement(test_elem, "source")
        source_elem.set("filename", "")
        source_elem.set("args", "")
        source_elem.set("enabled", "true")
        ET.SubElement(source_elem, "output")
        
        # References
        refs_elem = ET.SubElement(test_elem, "references")
        for ref_key, ref_uuid in test.references.items():
            reference = version.references.get(ref_uuid)
            if reference:
                ref_elem = ET.SubElement(refs_elem, "reference")
                ref_elem.set("uuid", ref_key)
                ref_elem.set("name", reference.name)
                ref_elem.set("url", reference.url)
        
        # Custom fields
        ET.SubElement(test_elem, "customFields")
    
    def _set_rules(self, root: Element, lib: IRLibrary) -> None:
        """Set rules in XML"""
        rules_elem = ET.SubElement(root, "rules")
        
        # Sort rules by name
        sorted_rules = sorted(lib.rules, key=lambda x: x.name)
        
        for r in sorted_rules:
            rule_elem = ET.SubElement(rules_elem, "rule")
            rule_elem.set("name", r.name)
            rule_elem.set("module", r.module)
            rule_elem.set("generatedByGui", r.generated_by_gui)
            rule_elem.set("matchesAllConditions", "true")
            
            # Conditions
            conditions_elem = ET.SubElement(rule_elem, "conditions")
            for cond in r.conditions:
                cond_elem = ET.SubElement(conditions_elem, "condition")
                cond_elem.set("name", cond.name)
                cond_elem.set("field", cond.field)
                cond_elem.set("value", cond.value)
            
            # Actions
            actions_elem = ET.SubElement(rule_elem, "actions")
            for act in r.actions:
                act_elem = ET.SubElement(actions_elem, "action")
                act_elem.set("project", act.project)
                act_elem.set("value", act.value)
                act_elem.set("name", act.name)
