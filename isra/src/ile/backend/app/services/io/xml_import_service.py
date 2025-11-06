"""
XML import service for IriusRisk Content Manager API
"""

import logging
import xml.etree.ElementTree as ET
from typing import BinaryIO, List, Optional, Dict
from xml.etree.ElementTree import Element

from isra.src.ile.backend.app.models import (
    ILEVersion, IRCategoryComponent, IRComponentDefinition, IRControl,
    IRLibrary, IRReference, IRRelation, IRRiskPattern, IRRiskRating,
    IRRule, IRRuleAction, IRRuleCondition, IRStandard, IRSupportedStandard,
    IRTest, IRThreat, IRUseCase, IRWeakness
)

logger = logging.getLogger(__name__)


class XMLImportService:
    """Service for importing XML library files"""
    
    def __init__(self):
        pass
    
    def _get_text_from_element(self, element: Optional[Element]) -> str:
        """Safely get text from XML element, returning empty string if element is None or text cannot be retrieved
        
        Args:
            element: XML Element to extract text from, can be None
        
        Returns:
            Text content of the element, or empty string if element is None, text is None, or any error occurs
        """
        try:
            if element is None:
                return ""
            if element.text is None:
                return ""
            return element.text
        except Exception:
            return ""
    
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
            library_desc_text = self._get_text_from_element(library_desc)
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

            print(f"Importing library: {new_library.ref}")
            
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
        for e in root.iter("componentDefinition"):
            component_definition = self._get_component_definition_from_xml(e)
            
            for ee in e.iter("riskPattern"):
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
        for e in root.iter("categoryComponent"):
            category_component = IRCategoryComponent(
                uuid=e.get("uuid", ""),
                ref=e.get("ref", ""),
                name=e.get("name", "")
            )
            if category_component.uuid not in version.categories:
                version.categories[category_component.uuid] = category_component
    
    def _set_supported_standards(self, root: Element, version_element: ILEVersion) -> None:
        """Set supported standards from XML"""
        for e in root.iter("supportedStandard"):
            uuid = e.get("uuid", "")
            if uuid not in version_element.supported_standards:
                supported_standard = IRSupportedStandard(
                    uuid=uuid,
                    supported_standard_ref=e.get("ref", ""),
                    supported_standard_name=e.get("name", "")
                )
                version_element.supported_standards[uuid] = supported_standard
    
    def _set_risk_patterns(self, root: Element, new_library: IRLibrary, version_element: ILEVersion) -> None:
        """Set risk patterns from XML"""
        risk_patterns_elem = root.find("riskPatterns")
        if risk_patterns_elem is not None:
            for e in risk_patterns_elem.iter("riskPattern"):
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
        for e in root.iter("rule"):
            rule = IRRule(
                name=e.get("name", ""),
                module=e.get("module", ""),
                gui=e.get("generatedByGui", "")
            )
            
            # Conditions
            for cond in e.iter("condition"):
                condition = IRRuleCondition(
                    name=cond.get("name", ""),
                    field=cond.get("field", ""),
                    value=cond.get("value", "")
                )
                rule.conditions.append(condition)
            
            # Actions
            for act in e.iter("action"):
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
        for weakness_element in e.iter("weakness"):
            if weakness_element.get("impact") is not None:
                ref = weakness_element.get("ref", "")
                weakness_uuid = weakness_element.get("uuid", "")
                # Check if weakness with this uuid already exists (UUID is the unique identifier)
                if weakness_uuid not in version_element.weaknesses:
                    weakness_ref = weakness_element.get("ref", "")
                    weakness_name = weakness_element.get("name", "")
                    weakness_desc_elem = weakness_element.find("desc")
                    weakness_desc = self._get_text_from_element(weakness_desc_elem)
                    impact = weakness_element.get("impact", "")
                    
                    test_element = weakness_element.find("test")
                    if test_element is not None:
                        steps_element = test_element.find("steps")
                        test_steps = self._get_text_from_element(steps_element)
                        
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
        for control_element in e.iter("countermeasure"):
            if control_element.get("state") is not None:
                ref = control_element.get("ref", "")
                control_uuid = control_element.get("uuid", "")
                # Check if control with this uuid already exists (UUID is the unique identifier)
                if control_uuid not in version_element.controls:
                    control_ref = control_element.get("ref", "")
                    control_name = control_element.get("name", "")
                    control_desc_elem = control_element.find("desc")
                    control_desc = self._get_text_from_element(control_desc_elem)
                    state = control_element.get("state", "")
                    cost = control_element.get("cost", "")
                    
                    test_element = control_element.find("test")
                    if test_element is not None:
                        steps_element = test_element.find("steps")
                        test_steps = self._get_text_from_element(steps_element)
                        
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
                        for st in control_element.iter("implementation"):
                            imp_uuid = st.get("uuid", "")
                            platform = st.get("platform", "")
                            desc_elem = st.find( "desc")
                            desc = self._get_text_from_element(desc_elem)
                            desc = desc.replace("\n", "").replace(" ", "")
                            control.implementations.append(f"{imp_uuid}_::_{platform}_::_{desc}")
                        
                        # Handle standards
                        for st in control_element.iter("standard"):
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
                        for custom_field in control_element.iter("customField"):
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
        
        def _get_weakness_uuid_by_ref(weakness_ref: str) -> str:
            """Get weakness UUID by ref, checking local dict first, then version_element"""
            if weakness_ref in weaknesses:
                return weaknesses[weakness_ref].uuid
            # Look up in version_element.weaknesses by ref
            for weakness in version_element.weaknesses.values():
                if weakness.ref == weakness_ref:
                    return weakness.uuid
            return ""
        
        def _get_control_uuid_by_ref(control_ref: str) -> str:
            """Get control UUID by ref, checking local dict first, then version_element"""
            if control_ref in controls:
                return controls[control_ref].uuid
            # Look up in version_element.controls by ref
            for control in version_element.controls.values():
                if control.ref == control_ref:
                    return control.uuid
            return ""
        
        for a in e.iter("usecase"):
            usecase = IRUseCase(
                uuid=a.get("uuid", ""),
                ref=a.get("ref", ""),
                name=a.get("name", ""),
                desc=a.get("desc", "")
            )
            
            # Collect all threats for this usecase
            threats_list = list(a.iter("threat"))
            
            # Case 1: Use case without threats
            if not threats_list:
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
                for th in threats_list:
                    threat_uuid = th.get("uuid", "")
                    
                    if threat_uuid not in version_element.threats:
                        threat_desc_elem = th.find("desc")
                        threat_desc = self._get_text_from_element(threat_desc_elem)
                        threat = IRThreat(
                            uuid=threat_uuid,
                            ref=th.get("ref", ""),
                            name=th.get("name", ""),
                            desc=threat_desc
                        )
                        
                        threat_rr = th.find("riskRating")
                        risk_rating = IRRiskRating(
                            confidentiality=threat_rr.get("confidentiality", ""),
                            integrity=threat_rr.get("integrity", ""),
                            availability=threat_rr.get("availability", ""),
                            ease_of_exploitation=threat_rr.get("easeOfExploitation", "")
                        )
                        threat.risk_rating = risk_rating
                        
                        # Handle custom fields
                        for custom_field in th.iter("customField"):
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
                    
                    # Track if any relations were created for this threat
                    threat_has_relations = False
                    th_control_refs = set()
                    
                    # Process weaknesses within the threat
                    weaknesses_list = list(th.iter("weakness"))
                    for w in weaknesses_list:
                        weakness_ref = w.get("ref", "")
                        weakness_uuid = _get_weakness_uuid_by_ref(weakness_ref)
                        
                        # Collect countermeasures for this weakness
                        wc_list = list(w.iter("countermeasure"))
                        
                        # Case 4: Weakness without controls
                        if not wc_list:
                            relation = IRRelation(
                                risk_pattern_uuid=risk_pattern.uuid,
                                usecase_uuid=usecase.uuid,
                                threat_uuid=threat_uuid,
                                weakness_uuid=weakness_uuid,
                                control_uuid="",
                                mitigation=""
                            )
                            new_library.relations[relation.uuid] = relation
                            threat_has_relations = True
                        else:
                            # Weakness with controls
                            for wc in wc_list:
                                control_ref = wc.get("ref", "")
                                control_uuid = _get_control_uuid_by_ref(control_ref)
                                relation = IRRelation(
                                    risk_pattern_uuid=risk_pattern.uuid,
                                    usecase_uuid=usecase.uuid,
                                    threat_uuid=threat_uuid,
                                    weakness_uuid=weakness_uuid,
                                    control_uuid=control_uuid,
                                    mitigation=wc.get("mitigation", "")
                                )
                                th_control_refs.add(wc.get("ref", ""))
                                new_library.relations[relation.uuid] = relation
                                threat_has_relations = True
                    
                    # Case 3: Threat with orphaned controls (controls not associated with any weakness)
                    orphaned_controls_list = list(th.iter("countermeasure"))
                    for c in orphaned_controls_list:
                        control_ref = c.get("ref", "")
                        if control_ref not in th_control_refs:
                            control_uuid = _get_control_uuid_by_ref(control_ref)
                            relation = IRRelation(
                                risk_pattern_uuid=risk_pattern.uuid,
                                usecase_uuid=usecase.uuid,
                                threat_uuid=threat_uuid,
                                weakness_uuid="",
                                control_uuid=control_uuid,
                                mitigation=c.get("mitigation", "")
                            )
                            new_library.relations[relation.uuid] = relation
                            threat_has_relations = True
                    
                    # Case 2: Threat without weaknesses and without orphaned controls
                    if not threat_has_relations:
                        relation = IRRelation(
                            risk_pattern_uuid=risk_pattern.uuid,
                            usecase_uuid=usecase.uuid,
                            threat_uuid=threat_uuid,
                            weakness_uuid="",
                            control_uuid="",
                            mitigation=""
                        )
                        new_library.relations[relation.uuid] = relation
            
            if usecase.uuid not in version_element.usecases:
                version_element.usecases[usecase.uuid] = usecase
    
    def _get_references_from_xml(self, e: Element) -> List[IRReference]:
        """Get references from XML element"""
        references_list = []
        references = e.find("references")
        if references is not None:
            for r in references.iter("reference"):
                uuid = r.get("uuid", "")
                name = r.get("name", "")
                url = r.get("url", "")
                reference = IRReference(uuid=uuid, name=name, url=url)
                references_list.append(reference)
        
        return references_list
