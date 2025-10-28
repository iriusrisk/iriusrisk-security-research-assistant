"""
XML import service for IriusRisk Library Editor API
"""

import logging
import xml.etree.ElementTree as ET
from typing import BinaryIO, List, Optional, Dict, Set
from xml.etree.ElementTree import Element

from isra.src.ile.backend.app.models import (
    ILEVersion, IRCategoryComponent, IRComponentDefinition, IRControl,
    IRLibrary, IRReference, IRRelation, IRRiskPattern, IRRiskRating,
    IRRule, IRRuleAction, IRRuleCondition, IRStandard, IRSupportedStandard,
    IRTest, IRThreat, IRUseCase, IRWeakness
)
from isra.src.ile.backend.app.services.io.xml_service import XMLService

logger = logging.getLogger(__name__)


class XMLImportService:
    """Service for importing XML library files"""
    
    def __init__(self):
        self.xml_service = XMLService()
    
    def import_library_xml(self, filename: str, library: BinaryIO, version_element: ILEVersion) -> None:
        """Import library from XML stream"""
        try:
            # Parse XML with security features
            tree = ET.parse(library)
            root = tree.getroot()
            
            # Library properties
            library_name = root.get("name", "")
            library_ref = root.get("ref", "")
            library_desc = root.find("desc")
            library_desc_text = library_desc.text if library_desc is not None else ""
            library_revision = root.get("revision", "1")
            library_enabled = root.get("enabled", "true")
            
            if not library_enabled:
                library_enabled = "true"
            
            new_library = IRLibrary(
                ref=library_ref,
                name=library_name,
                desc=library_desc_text,
                revision=library_revision,
                filename=filename,
                enabled=library_enabled
            )
            
            # Import various elements
            self._set_category_components(root, version_element)
            self._set_component_definitions(root, new_library)
            self._set_supported_standards(root, version_element)
            self._set_risk_patterns(root, new_library, version_element)
            self._set_rules(root, new_library)
            
            logger.debug(f"Adding new library {library_ref} to version {version_element.version}")
            version_element.libraries[new_library.ref] = new_library
            
        except Exception as e:
            logger.error(f"Error importing XML library {filename}: {e}")
            raise RuntimeError(f"Failed to import XML library: {e}") from e
    
    def _set_component_definitions(self, root: Element, new_library: IRLibrary) -> None:
        """Set component definitions from XML"""
        for e in self.xml_service.get_nodes(root.findall("componentDefinition")):
            component_definition = self._get_component_definition_from_xml(e)
            
            for ee in self.xml_service.get_nodes(e.findall("riskPattern")):
                component_definition.risk_pattern_refs.append(ee.get("ref"))
            
            new_library.component_definitions[component_definition.uuid] = component_definition
    
    def _get_component_definition_from_xml(self, e: Element) -> IRComponentDefinition:
        """Extract component definition from XML element"""
        uuid = e.get("uuid", "")
        component_definition_ref = e.get("ref", "")
        component_definition_name = e.get("name", "")
        component_definition_desc = e.get("desc", "")
        component_definition_category_ref = e.get("categoryRef", "")
        visible = e.get("visible", "true")
        
        return IRComponentDefinition(
            uuid=uuid,
            ref=component_definition_ref,
            name=component_definition_name,
            desc=component_definition_desc,
            category_ref=component_definition_category_ref,
            visible=visible
        )
    
    def _set_category_components(self, root: Element, version: ILEVersion) -> None:
        """Set category components from XML"""
        for e in self.xml_service.get_nodes(root.findall("categoryComponent")):
            category_component = IRCategoryComponent(
                uuid=e.get("uuid", ""),
                ref=e.get("ref", ""),
                name=e.get("name", "")
            )
            if category_component.uuid not in version.categories:
                version.categories[category_component.uuid] = category_component
    
    def _set_supported_standards(self, root: Element, version_element: ILEVersion) -> None:
        """Set supported standards from XML"""
        for e in self.xml_service.get_nodes(root.findall("supportedStandard")):
            uuid = e.get("uuid", "")
            if uuid not in version_element.supported_standards:
                supported_standard = IRSupportedStandard(
                    uuid=uuid,
                    ref=e.get("ref", ""),
                    name=e.get("name", "")
                )
                version_element.supported_standards[uuid] = supported_standard
    
    def _set_risk_patterns(self, root: Element, new_library: IRLibrary, version_element: ILEVersion) -> None:
        """Set risk patterns from XML"""
        risk_patterns_elem = self.xml_service.get_element_by_name(root, "riskPatterns")
        if risk_patterns_elem is not None:
            for e in self.xml_service.get_nodes(risk_patterns_elem.findall("riskPattern")):
                # Weaknesses will be compiled in version
                weaknesses = self._set_weaknesses(e, version_element)
                
                # Controls will be compiled in version
                controls = self._set_controls(e, version_element)
                
                # Usecases
                risk_pattern = IRRiskPattern(
                    ref=e.get("ref", ""),
                    name=e.get("name", ""),
                    desc=e.get("desc", ""),
                    uuid=e.get("uuid", "")
                )
                self._set_usecases(e, version_element, new_library, weaknesses, controls, risk_pattern)
                
                new_library.risk_patterns[risk_pattern.uuid] = risk_pattern
    
    def _set_rules(self, root: Element, new_library: IRLibrary) -> None:
        """Set rules from XML"""
        for e in self.xml_service.get_nodes(root.findall("rule")):
            rule = IRRule(
                name=e.get("name", ""),
                module=e.get("module", ""),
                generated_by_gui=e.get("generatedByGui", "")
            )
            
            # Conditions
            for cond in self.xml_service.get_nodes(e.findall("condition")):
                condition = IRRuleCondition(
                    name=cond.get("name", ""),
                    field=cond.get("field", ""),
                    value=cond.get("value", "")
                )
                rule.conditions.append(condition)
            
            # Actions
            for act in self.xml_service.get_nodes(e.findall("action")):
                action = IRRuleAction(
                    name=act.get("name", ""),
                    value=act.get("value", ""),
                    project=act.get("project", "")
                )
                rule.actions.append(action)
            
            new_library.rules.append(rule)
    
    def _set_weaknesses(self, e: Element, version_element: ILEVersion) -> Dict[str, IRWeakness]:
        """Set weaknesses from XML"""
        weaknesses_in_risk_pattern = {}
        for weakness_element in self.xml_service.get_nodes(e.findall("weakness")):
            if weakness_element.hasAttribute("impact"):
                ref = weakness_element.get("ref", "")
                if ref not in version_element.weaknesses:
                    weakness_uuid = weakness_element.get("uuid", "")
                    weakness_ref = weakness_element.get("ref", "")
                    weakness_name = weakness_element.get("name", "")
                    weakness_desc_elem = weakness_element.find("desc")
                    weakness_desc = weakness_desc_elem.text if weakness_desc_elem is not None else ""
                    impact = weakness_element.get("impact", "")
                    
                    test_element = self.xml_service.get_element_by_name(weakness_element, "test")
                    if test_element is not None:
                        steps_element = self.xml_service.get_element_by_name(test_element, "steps")
                        test_steps = steps_element.text if steps_element is not None else ""
                        
                        test_object = IRTest(steps=test_steps)
                        test_object.uuid = test_element.get("uuid", "")
                        
                        reference_list = self._get_references_from_xml(test_element)
                        for reference in reference_list:
                            reference_from_element = self._check_reference_exists_in_version(
                                version_element, reference.name, reference.url
                            )
                            if reference_from_element:
                                test_object.references[reference.uuid] = reference_from_element.uuid
                            else:
                                new_reference = IRReference(name=reference.name, url=reference.url)
                                version_element.references[new_reference.uuid] = new_reference
                                test_object.references[reference.uuid] = new_reference.uuid
                        
                        weakness = IRWeakness(
                            uuid=weakness_uuid,
                            ref=weakness_ref,
                            name=weakness_name,
                            desc=weakness_desc,
                            impact=impact,
                            test=test_object
                        )
                        version_element.weaknesses[weakness.uuid] = weakness
                        weaknesses_in_risk_pattern[weakness_ref] = weakness
        
        return weaknesses_in_risk_pattern
    
    def _set_controls(self, e: Element, version_element: ILEVersion) -> Dict[str, IRControl]:
        """Set controls from XML"""
        controls_in_risk_pattern = {}
        for control_element in self.xml_service.get_nodes(e.findall("countermeasure")):
            if control_element.hasAttribute("state"):
                ref = control_element.get("ref", "")
                if ref not in version_element.controls:
                    control_uuid = control_element.get("uuid", "")
                    control_ref = control_element.get("ref", "")
                    control_name = control_element.get("name", "")
                    control_desc_elem = control_element.find("desc")
                    control_desc = control_desc_elem.text if control_desc_elem is not None else ""
                    state = control_element.get("state", "")
                    cost = control_element.get("cost", "")
                    
                    test_element = self.xml_service.get_element_by_name(control_element, "test")
                    if test_element is not None:
                        steps_element = self.xml_service.get_element_by_name(test_element, "steps")
                        test_steps = steps_element.text if steps_element is not None else ""
                        
                        test_object = IRTest(steps=test_steps)
                        test_object.uuid = test_element.get("uuid", "")
                        
                        reference_list = self._get_references_from_xml(test_element)
                        for reference in reference_list:
                            reference_from_element = self._check_reference_exists_in_version(
                                version_element, reference.name, reference.url
                            )
                            if reference_from_element:
                                test_object.references[reference.uuid] = reference_from_element.uuid
                            else:
                                new_reference = IRReference(name=reference.name, url=reference.url)
                                version_element.references[new_reference.uuid] = new_reference
                                test_object.references[reference.uuid] = new_reference.uuid
                        
                        control = IRControl(
                            uuid=control_uuid,
                            ref=control_ref,
                            name=control_name,
                            desc=control_desc,
                            test=test_object,
                            state=state,
                            cost=cost
                        )
                        
                        # Handle implementations
                        for st in self.xml_service.get_nodes(control_element.findall("implementation")):
                            platform = st.get("platform", "")
                            desc_elem = self.xml_service.get_element_by_name(st, "desc")
                            desc = desc_elem.text if desc_elem is not None else ""
                            desc = desc.replace("\n", "").replace(" ", "")
                            control.implementations.append(f"{platform}_::_{desc}")
                        
                        # Handle standards
                        for st in self.xml_service.get_nodes(control_element.findall("standard")):
                            xml_standard_uuid = st.get("uuid", "")
                            supported_standard_ref = st.get("supportedStandardRef", "")
                            standard_ref = st.get("ref", "")
                            
                            existing_standard = self._check_standard_exists_in_version(
                                version_element, supported_standard_ref, standard_ref
                            )
                            if existing_standard:
                                control.standards[xml_standard_uuid] = existing_standard.uuid
                            else:
                                new_standard = IRStandard(
                                    supported_standard_ref=supported_standard_ref,
                                    standard_ref=standard_ref
                                )
                                version_element.standards[new_standard.uuid] = new_standard
                                control.standards[xml_standard_uuid] = new_standard.uuid
                        
                        # Handle custom fields
                        for custom_field in self.xml_service.get_nodes(control_element.findall("customField")):
                            ref = custom_field.get("ref", "")
                            value = custom_field.get("value", "")
                            
                            if ref == "SF-C-STANDARD-BASELINE":
                                control.base_standard = value.split("|")
                            elif ref == "SF-C-STANDARD-SECTION":
                                control.base_standard_section = value.split("|")
                            elif ref == "SF-C-SCOPE":
                                control.scope = value.split("|")
                            elif ref == "SF-C-MITRE":
                                control.mitre = value.split("|")
                        
                        # Handle control references
                        control_reference_list = self._get_references_from_xml(control_element)
                        for reference in control_reference_list:
                            reference_from_element = self._check_reference_exists_in_version(
                                version_element, reference.name, reference.url
                            )
                            if reference_from_element:
                                control.references[reference.uuid] = reference_from_element.uuid
                            else:
                                new_reference = IRReference(name=reference.name, url=reference.url)
                                version_element.references[new_reference.uuid] = new_reference
                                control.references[reference.uuid] = new_reference.uuid
                        
                        version_element.controls[control.uuid] = control
                        controls_in_risk_pattern[control.ref] = control
        
        return controls_in_risk_pattern
    
    def _check_reference_exists_in_version(self, version: ILEVersion, name: str, url: str) -> Optional[IRReference]:
        """Check if reference exists in version"""
        for ref in version.references.values():
            if ref.name == name and ref.url == url:
                return ref
        return None
    
    def _check_standard_exists_in_version(self, version: ILEVersion, supported_standard_ref: str, standard_ref: str) -> Optional[IRStandard]:
        """Check if standard exists in version"""
        for standard in version.standards.values():
            if standard.supported_standard_ref == supported_standard_ref and standard.standard_ref == standard_ref:
                return standard
        return None
    
    def _set_usecases(self, e: Element, version_element: ILEVersion, new_library: IRLibrary, 
                     weaknesses: Dict[str, IRWeakness], controls: Dict[str, IRControl], risk_pattern: IRRiskPattern) -> None:
        """Set use cases from XML"""
        for a in self.xml_service.get_nodes(e.findall("usecase")):
            usecase = IRUseCase(
                uuid=a.get("uuid", ""),
                ref=a.get("ref", ""),
                name=a.get("name", ""),
                desc=a.get("desc", "")
            )
            
            threats = self.xml_service.get_nodes(a.findall("threat"))
            if not threats:
                relation = IRRelation(
                    risk_pattern_uuid=risk_pattern.uuid,
                    usecase_uuid=usecase.uuid,
                    threat_uuid="",
                    weakness_uuid="",
                    control_uuid="",
                    mitigation=""
                )
                new_library.relations[relation.uuid] = relation
            else:
                for th in threats:
                    threat_uuid = th.get("uuid", "")
                    
                    if threat_uuid not in version_element.threats:
                        threat_desc_elem = th.find("desc")
                        threat_desc = threat_desc_elem.text if threat_desc_elem is not None else ""
                        threat = IRThreat(
                            uuid=threat_uuid,
                            ref=th.get("ref", ""),
                            name=th.get("name", ""),
                            desc=threat_desc
                        )
                        
                        threat_rr = self.xml_service.get_nodes(th.findall("riskRating"))
                        if threat_rr:
                            rr = threat_rr[0]
                            risk_rating = IRRiskRating(
                                confidentiality=rr.get("confidentiality", ""),
                                integrity=rr.get("integrity", ""),
                                availability=rr.get("availability", ""),
                                ease_of_exploitation=rr.get("easeOfExploitation", "")
                            )
                            threat.risk_rating = risk_rating
                        
                        # Handle custom fields
                        for custom_field in self.xml_service.get_nodes(a.findall("customField")):
                            ref = custom_field.get("ref", "")
                            value = custom_field.get("value", "")
                            
                            if ref == "SF-T-STRIDE-LM":
                                threat.stride = value.split("|")
                            elif ref == "SF-T-MITRE":
                                threat.mitre = value.split("|")
                        
                        # Handle threat references
                        threat_references = self._get_references_from_xml(th)
                        for reference in threat_references:
                            reference_from_element = self._check_reference_exists_in_version(
                                version_element, reference.name, reference.url
                            )
                            if reference_from_element:
                                threat.references[reference.uuid] = reference_from_element.uuid
                            else:
                                new_reference = IRReference(name=reference.name, url=reference.url)
                                version_element.references[new_reference.uuid] = new_reference
                                threat.references[reference.uuid] = new_reference.uuid
                        
                        version_element.threats[threat.uuid] = threat
                    
                    th_control_refs = set()
                    
                    for w in self.xml_service.get_nodes(th.findall("weakness")):
                        weakness_ref = w.get("ref", "")
                        
                        wc_list = self.xml_service.get_nodes(w.findall("countermeasure"))
                        if not wc_list:
                            relation = IRRelation(
                                risk_pattern_uuid=risk_pattern.uuid,
                                usecase_uuid=usecase.uuid,
                                threat_uuid=threat_uuid,
                                weakness_uuid=weaknesses[weakness_ref].uuid,
                                control_uuid="",
                                mitigation=""
                            )
                            new_library.relations[relation.uuid] = relation
                        else:
                            for wc in wc_list:
                                control_ref = wc.get("ref", "")
                                relation = IRRelation(
                                    risk_pattern_uuid=risk_pattern.uuid,
                                    usecase_uuid=usecase.uuid,
                                    threat_uuid=threat_uuid,
                                    weakness_uuid=weaknesses[weakness_ref].uuid,
                                    control_uuid=controls[control_ref].uuid,
                                    mitigation=wc.get("mitigation", "")
                                )
                                th_control_refs.add(wc.get("ref", ""))
                                new_library.relations[relation.uuid] = relation
                    
                    for c in self.xml_service.get_nodes(th.findall("countermeasure")):
                        if c.get("ref", "") not in th_control_refs:
                            relation = IRRelation(
                                risk_pattern_uuid=risk_pattern.ref,
                                usecase_uuid=usecase.uuid,
                                threat_uuid=threat_uuid,
                                weakness_uuid="",
                                control_uuid=controls[c.get("ref", "")].uuid,
                                mitigation=c.get("mitigation", "")
                            )
                            new_library.relations[relation.uuid] = relation
            
            if usecase.uuid not in version_element.usecases:
                version_element.usecases[usecase.uuid] = usecase
    
    def _get_references_from_xml(self, e: Element) -> List[IRReference]:
        """Get references from XML element"""
        references_list = []
        references = self.xml_service.get_element_by_name(e, "references")
        if references is not None:
            for r in self.xml_service.get_nodes(references.findall("reference")):
                uuid = r.get("uuid", "")
                name = r.get("name", "")
                url = r.get("url", "")
                reference = IRReference(uuid=uuid, name=name, url=url)
                references_list.append(reference)
        
        return references_list
