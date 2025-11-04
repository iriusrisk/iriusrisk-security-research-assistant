"""
YSC import service for IriusRisk Library Editor API
"""

import logging
import uuid
import yaml
from typing import BinaryIO, List, Optional, Dict

from isra.src.ile.backend.app.models import (
    ILEVersion, IRCategoryComponent, IRComponentDefinition, IRControl,
    IRLibrary, IRReference, IRRelation, IRRiskPattern, IRRiskRating,
    IRRule, IRRuleAction, IRRuleCondition, IRStandard, IRSupportedStandard,
    IRTest, IRThreat, IRUseCase, IRWeakness
)
from isra.src.config.constants import OUTPUT_NAME, CATEGORIES_LIST, STRIDE_LIST
from isra.src.utils.text_functions import generate_identifier_from_ref
from isra.src.utils.cwe_functions import get_original_cwe_weaknesses, get_cwe_description, get_cwe_impact

logger = logging.getLogger(__name__)


class YSCImportService:
    """Service for importing YSC component files"""
    
    def __init__(self):
        pass
    
    def _find_library_by_category(self, category_ref: str, version_element: ILEVersion) -> Optional[IRLibrary]:
        """Find existing library that matches the category pattern"""
        if not category_ref:
            return None
        
        # Look for libraries with names like "{category}-components" or containing the category
        category_variations = [
            f"{category_ref}-components",
            f"{category_ref}-component",
            category_ref
        ]
        
        for library in version_element.libraries.values():
            # Check if library ref or name matches category pattern
            if library.ref in category_variations or library.name in category_variations:
                return library
            # Also check if library ref/name contains the category
            if category_ref in library.ref or category_ref in library.name:
                return library
        
        return None
    
    def import_ysc_component(self, filename: str, library: BinaryIO, version_element: ILEVersion) -> None:
        """Import YSC component from stream"""
        try:
            # Parse YAML content
            yaml_content = yaml.safe_load(library)
            
            if not yaml_content or "component" not in yaml_content:
                raise ValueError("Invalid YSC file: missing component section")
            
            component = yaml_content["component"]
            component_ref = component.get("ref", "")
            component_name = component.get("name", "")
            component_desc = component.get("description", "")
            component_category = component.get("category", "")
            
            # Check if there's an existing library matching the category
            existing_library = self._find_library_by_category(component_category, version_element)
            
            if existing_library:
                # Use existing library
                new_library = existing_library
                print(f"Importing YSC component into existing library: {new_library.ref}")
            else:
                # Create new library
                library_ref = component_ref
                new_library = IRLibrary(
                    ref=library_ref,
                    name=component_name,
                    desc=component_desc,
                    revision="1",
                    filename=filename,
                    enabled="true"
                )
                print(f"Importing YSC component: {new_library.ref}")
                version_element.libraries[new_library.ref] = new_library
            
            # Import various elements
            self._set_category_components(component_category, version_element)
            self._set_component_definitions(component, new_library)
            
            # Get risk pattern from component
            risk_pattern_data = component.get("risk_pattern", {})
            if risk_pattern_data:
                self._set_risk_patterns(risk_pattern_data, new_library, version_element)
                self._set_rules(component, new_library)
            
            logger.debug(f"Component added to library {new_library.ref} in version {version_element.version}")
            
        except Exception as e:
            logger.error(f"Error importing YSC component {filename}: {e}")
            raise RuntimeError(f"Failed to import YSC component: {e}") from e
    
    def _set_component_definitions(self, component: Dict, new_library: IRLibrary) -> None:
        """Set component definitions from YSC"""
        component_ref = component.get("ref", "")
        component_name = component.get("name", "")
        component_desc = component.get("description", "")
        component_category = component.get("category", "")
        
        risk_pattern_ref = ""
        risk_pattern_data = component.get("risk_pattern", {})
        if risk_pattern_data:
            risk_pattern_ref = risk_pattern_data.get("ref", "")
        
        component_definition = IRComponentDefinition(
            ref=component_ref,
            name=component_name,
            desc=component_desc,
            category_ref=component_category,
            visible="true"
        )
        
        if risk_pattern_ref:
            component_definition.risk_pattern_refs.append(risk_pattern_ref)
        
        new_library.component_definitions[component_definition.uuid] = component_definition
    
    def _set_category_components(self, category_ref: str, version: ILEVersion) -> None:
        """Set category components from YSC"""
        if not category_ref:
            return
        
        # Check if category exists in constants
        if category_ref in CATEGORIES_LIST:
            category_info = CATEGORIES_LIST[category_ref]
            category_component = IRCategoryComponent(
                ref=category_ref,
                name=category_info.get("name", category_ref),
                desc=category_info.get("desc", "")
            )
            # Check if category already exists by ref
            existing_category = None
            for cat in version.categories.values():
                if cat.ref == category_ref:
                    existing_category = cat
                    break
            
            if not existing_category:
                version.categories[category_component.uuid] = category_component
        else:
            # Create category with default name
            category_component = IRCategoryComponent(
                ref=category_ref,
                name=category_ref,
                desc=""
            )
            # Check if category already exists by ref
            existing_category = None
            for cat in version.categories.values():
                if cat.ref == category_ref:
                    existing_category = cat
                    break
            
            if not existing_category:
                version.categories[category_component.uuid] = category_component
    
    def _set_risk_patterns(self, risk_pattern_data: Dict, new_library: IRLibrary, version_element: ILEVersion) -> None:
        """Set risk patterns from YSC"""
        risk_pattern_ref = risk_pattern_data.get("ref", "")
        risk_pattern_name = risk_pattern_data.get("name", "")
        risk_pattern_desc = risk_pattern_data.get("description", "")
        
        risk_pattern = IRRiskPattern(
            ref=risk_pattern_ref,
            name=risk_pattern_name,
            desc=risk_pattern_desc
        )
        
        # Process threats
        threats_data = risk_pattern_data.get("threats", [])
        controls_dict = {}  # Track controls by ref
        
        for threat_data in threats_data:
            threat = self._create_threat_from_yaml(threat_data, version_element)
            version_element.threats[threat.uuid] = threat
            
            # Process countermeasures for this threat
            countermeasures_data = threat_data.get("countermeasures", [])
            for countermeasure_data in countermeasures_data:
                control = self._create_control_from_yaml(countermeasure_data, version_element)
                controls_dict[control.ref] = control
                version_element.controls[control.uuid] = control
        
        # Create usecases and relations based on STRIDE groups
        original_cwe_weaknesses = get_original_cwe_weaknesses()
        
        for threat_data in threats_data:
            threat_ref = threat_data.get("ref", "")
            threat = None
            for t in version_element.threats.values():
                if t.ref == threat_ref:
                    threat = t
                    break
            
            if not threat:
                continue
            
            # Create usecase based on STRIDE group (like in load_yaml_file)
            threat_group = threat_data.get("group", "")
            if isinstance(threat_group, list) and len(threat_group) > 0:
                stride_key = threat_group[0][0] if threat_group[0] else ""
            elif isinstance(threat_group, str) and len(threat_group) > 0:
                stride_key = threat_group[0]
            else:
                stride_key = ""
            
            if stride_key in STRIDE_LIST:
                use_case_info = STRIDE_LIST[stride_key]
                usecase_ref = use_case_info["ref"]
                usecase_name = use_case_info["name"]
                usecase_desc = use_case_info["desc"]
            else:
                # Default to General usecase
                usecase_ref = "General"
                usecase_name = "General"
                usecase_desc = ""
            
            # Check if usecase already exists
            existing_usecase = None
            for uc in version_element.usecases.values():
                if uc.ref == usecase_ref:
                    existing_usecase = uc
                    break
            
            if not existing_usecase:
                usecase = IRUseCase(
                    ref=usecase_ref,
                    name=usecase_name,
                    desc=usecase_desc
                )
                version_element.usecases[usecase.uuid] = usecase
            else:
                usecase = existing_usecase
            
            # Create relations for countermeasures (with weaknesses from CWE)
            countermeasures_data = threat_data.get("countermeasures", [])
            for countermeasure_data in countermeasures_data:
                countermeasure_ref = countermeasure_data.get("ref", "")
                control = None
                for c in version_element.controls.values():
                    if c.ref == countermeasure_ref:
                        control = c
                        break
                
                if not control:
                    continue
                
                # Check for CWE weakness (like in load_yaml_file)
                weakness_uuid = ""
                cwe = countermeasure_data.get("cwe", "")
                if cwe and cwe != "":
                    # Create or find weakness from CWE
                    cwe_ref = cwe.strip()
                    if not cwe_ref.startswith("CWE-"):
                        cwe_ref = f"CWE-{cwe_ref}" if "-" not in cwe_ref else cwe_ref
                    
                    # Check if weakness already exists
                    existing_weakness = None
                    for w in version_element.weaknesses.values():
                        if w.ref == cwe_ref:
                            existing_weakness = w
                            break
                    
                    if not existing_weakness:
                        # Create new weakness from CWE
                        cwe_ids = cwe_ref.split(" ")
                        cwe_desc = get_cwe_description(original_cwe_weaknesses, cwe_ids)
                        cwe_impact = countermeasure_data.get("cwe_impact", "100")
                        
                        # Try to get impact from CWE if not provided
                        if cwe_impact == "100" and len(cwe_ids) > 0:
                            for cwe_id in cwe_ids:
                                if "-" in cwe_id:
                                    cwe_id_number = cwe_id.split("-")[1]
                                    if cwe_id_number in original_cwe_weaknesses:
                                        cwe_impact = get_cwe_impact(original_cwe_weaknesses, cwe_id_number)
                                        break
                        
                        weakness = IRWeakness(
                            ref=cwe_ref,
                            name=cwe_ref,
                            desc=cwe_desc,
                            impact=cwe_impact
                        )
                        version_element.weaknesses[weakness.uuid] = weakness
                        weakness_uuid = weakness.uuid
                    else:
                        weakness_uuid = existing_weakness.uuid
                
                # Create relation: threat -> weakness -> countermeasure (or threat -> countermeasure if no weakness)
                relation = IRRelation(
                    risk_pattern_uuid=risk_pattern.uuid,
                    usecase_uuid=usecase.uuid,
                    threat_uuid=threat.uuid,
                    weakness_uuid=weakness_uuid,
                    control_uuid=control.uuid,
                    mitigation=""
                )
                new_library.relations[relation.uuid] = relation
        
        new_library.risk_patterns[risk_pattern.uuid] = risk_pattern
    
    def _create_threat_from_yaml(self, threat_data: Dict, version_element: ILEVersion) -> IRThreat:
        """Create threat from YAML data"""
        threat_ref = threat_data.get("ref", "")
        threat_name = threat_data.get("name", "")
        threat_desc = threat_data.get("description", "")
        
        threat = IRThreat(
            ref=threat_ref,
            name=threat_name,
            desc=threat_desc
        )
        
        # Risk score
        risk_score_data = threat_data.get("risk_score", {})
        if risk_score_data:
            risk_rating = IRRiskRating(
                confidentiality=risk_score_data.get("confidentiality", "100"),
                integrity=risk_score_data.get("integrity", "100"),
                availability=risk_score_data.get("availability", "100"),
                ease_of_exploitation=risk_score_data.get("ease_of_exploitation", "100")
            )
            threat.risk_rating = risk_rating
        
        # Taxonomies - STRIDE
        taxonomies_data = threat_data.get("taxonomies", {})
        stride_data = taxonomies_data.get("stride", [])
        if stride_data:
            threat.stride = stride_data
        
        # Taxonomies - MITRE
        attack_enterprise_technique = taxonomies_data.get("attack_enterprise_technique", [])
        if attack_enterprise_technique:
            threat.mitre = attack_enterprise_technique
        
        # References
        references_data = threat_data.get("references", [])
        for ref_data in references_data:
            ref_name = ref_data.get("name", "")
            ref_url = ref_data.get("url", "")
            
            if ref_name and ref_url:
                existing_ref = self._check_reference_exists_in_version(
                    version_element, ref_name, ref_url
                )
                if existing_ref:
                    threat.references[ref_data.get("uuid", "")] = existing_ref.uuid
                else:
                    new_reference = IRReference(name=ref_name, url=ref_url)
                    version_element.references[new_reference.uuid] = new_reference
                    threat.references[ref_data.get("uuid", "")] = new_reference.uuid
        
        return threat
    
    def _create_control_from_yaml(self, countermeasure_data: Dict, version_element: ILEVersion) -> IRControl:
        """Create control from YAML countermeasure data"""
        control_ref = countermeasure_data.get("ref", "")
        control_name = countermeasure_data.get("name", "")
        control_desc = countermeasure_data.get("description", "")
        cost = countermeasure_data.get("cost", "0")
        
        control = IRControl(
            ref=control_ref,
            name=control_name,
            desc=control_desc,
            cost=cost,
            state="Recommended"
        )
        
        # References
        references_data = countermeasure_data.get("references", [])
        for ref_data in references_data:
            ref_name = ref_data.get("name", "")
            ref_url = ref_data.get("url", "")
            
            if ref_name and ref_url:
                existing_ref = self._check_reference_exists_in_version(
                    version_element, ref_name, ref_url
                )
                if existing_ref:
                    control.references[ref_data.get("uuid", "")] = existing_ref.uuid
                else:
                    new_reference = IRReference(name=ref_name, url=ref_url)
                    version_element.references[new_reference.uuid] = new_reference
                    control.references[ref_data.get("uuid", "")] = new_reference.uuid
        
        # Standards
        standards_data = countermeasure_data.get("standards", {})
        base_standard = countermeasure_data.get("base_standard", "")
        base_standard_section = countermeasure_data.get("base_standard_section", [])
        
        if base_standard and base_standard_section:
            # Map base_standard to supported_standard_ref using OUTPUT_NAME
            if base_standard in OUTPUT_NAME:
                supported_standard_ref = OUTPUT_NAME[base_standard]["ref"]
                supported_standard_name = OUTPUT_NAME[base_standard]["name"]
                
                # Add supported standard if not exists
                existing_supported_standard = None
                for ss in version_element.supported_standards.values():
                    if ss.supported_standard_ref == supported_standard_ref:
                        existing_supported_standard = ss
                        break
                
                if not existing_supported_standard:
                    supported_standard = IRSupportedStandard(
                        supported_standard_ref=supported_standard_ref,
                        supported_standard_name=supported_standard_name
                    )
                    version_element.supported_standards[supported_standard.uuid] = supported_standard
                
                # Add standards for each section
                for section in base_standard_section:
                    existing_standard = self._check_standard_exists_in_version(
                        version_element, supported_standard_ref, section
                    )
                    if existing_standard:
                        control.standards[str(uuid.uuid4())] = existing_standard.uuid
                    else:
                        new_standard = IRStandard(
                            supported_standard_ref=supported_standard_ref,
                            standard_ref=section
                        )
                        version_element.standards[new_standard.uuid] = new_standard
                        control.standards[str(uuid.uuid4())] = new_standard.uuid
        
        # Handle standards from standards dict
        for standard_name, standard_sections in standards_data.items():
            if standard_name in OUTPUT_NAME:
                supported_standard_ref = OUTPUT_NAME[standard_name]["ref"]
                supported_standard_name = OUTPUT_NAME[standard_name]["name"]
                
                # Add supported standard if not exists
                existing_supported_standard = None
                for ss in version_element.supported_standards.values():
                    if ss.supported_standard_ref == supported_standard_ref:
                        existing_supported_standard = ss
                        break
                
                if not existing_supported_standard:
                    supported_standard = IRSupportedStandard(
                        supported_standard_ref=supported_standard_ref,
                        supported_standard_name=supported_standard_name
                    )
                    version_element.supported_standards[supported_standard.uuid] = supported_standard
                
                # Add standards for each section
                if isinstance(standard_sections, list):
                    for section in standard_sections:
                        existing_standard = self._check_standard_exists_in_version(
                            version_element, supported_standard_ref, section
                        )
                        if existing_standard:
                            control.standards[str(uuid.uuid4())] = existing_standard.uuid
                        else:
                            new_standard = IRStandard(
                                supported_standard_ref=supported_standard_ref,
                                standard_ref=section
                            )
                            version_element.standards[new_standard.uuid] = new_standard
                            control.standards[str(uuid.uuid4())] = new_standard.uuid
        
        # Base standard and base standard section
        if base_standard:
            control.base_standard = [base_standard]
        if base_standard_section:
            control.base_standard_section = base_standard_section if isinstance(base_standard_section, list) else [base_standard_section]
        
        # Taxonomies - Scope
        taxonomies_data = countermeasure_data.get("taxonomies", {})
        scope_data = taxonomies_data.get("scope", [])
        if scope_data:
            control.scope = scope_data
        
        # Taxonomies - MITRE
        attack_enterprise_mitigation = taxonomies_data.get("attack_enterprise_mitigation", [])
        if attack_enterprise_mitigation:
            control.mitre = attack_enterprise_mitigation
        
        return control
    
    def _set_rules(self, component: Dict, new_library: IRLibrary) -> None:
        """Set rules from YSC component data"""
        risk_pattern_data = component.get("risk_pattern", {})
        if not risk_pattern_data:
            return
        
        threats_data = risk_pattern_data.get("threats", [])
        component_ref = component.get("ref", "")
        comp_ref = generate_identifier_from_ref(component_ref)
        
        # Collect questions from countermeasures
        questions = []
        dataflow_tags_map = {}  # Map control_ref -> list of tags
        
        for threat_data in threats_data:
            countermeasures_data = threat_data.get("countermeasures", [])
            for countermeasure_data in countermeasures_data:
                control_ref = countermeasure_data.get("ref", "")
                question = countermeasure_data.get("question", "")
                question_desc = countermeasure_data.get("question_desc", "")
                dataflow_tags = countermeasure_data.get("dataflow_tags", [])
                
                if question:
                    questions.append((control_ref, question, question_desc))
                
                if dataflow_tags:
                    dataflow_tags_map[control_ref] = dataflow_tags
        
        # Create question group rule
        if questions:
            rule = IRRule(
                name=f"Q - Security Context - {component_ref}",
                module="component",
                gui="true"
            )
            
            # Add condition
            condition = IRRuleCondition(name="CONDITION_COMPONENT_DEFINITION",
            field="id",
            value=component_ref
            )
            rule.conditions.append(condition)
            
            # Add actions for questions
            priority = 7000
            for question in questions:
                control_ref, question_text, question_desc_text = question
                control_name = ""
                # Find control name
                for threat_data in threats_data:
                    countermeasures_data = threat_data.get("countermeasures", [])
                    for cm in countermeasures_data:
                        if cm.get("ref") == control_ref:
                            control_name = cm.get("name", "")
                            break
                    if control_name:
                        break
                
                cont = generate_identifier_from_ref(control_name)
                qg_id = f"{comp_ref}.{cont}"
                
                action_value = (
                    f"provided.question.{control_ref}_::_Security Context_::_{question_text}_::_{priority}_::_true_::_false_::_{question_desc_text}"
                )
                action = IRRuleAction(
                    name="INSERT_COMPONENT_QUESTION_GROUP",
                    value=action_value,
                    project=""
                )
                rule.actions.append(action)
                priority += 1
            
            new_library.rules.append(rule)
        
        # Create dataflow tag rules
        for control_ref, tags in dataflow_tags_map.items():
            control_name = ""
            # Find control name
            for threat_data in threats_data:
                countermeasures_data = threat_data.get("countermeasures", [])
                for cm in countermeasures_data:
                    if cm.get("ref") == control_ref:
                        control_name = cm.get("name", "")
                        break
                if control_name:
                    break
            
            cont = generate_identifier_from_ref(control_name)
            qg_id = f"{comp_ref}.{cont}"
            
            for tag in tags:
                rule = IRRule(
                    name=f"Implement countermeasure if tag {tag} in dataflow: {qg_id}",
                    module="dataflow",
                    gui="true"
                )
                
                # Add condition
                condition = IRRuleCondition(
                    name="CONDITION_DATAFLOW_CONTAINS_TAG",
                    field="id",
                    value=tag
                )
                rule.conditions.append(condition)
                
                # Add action
                action = IRRuleAction(
                    name="IMPLEMENT_CONTROL_DESTINATION",
                    value=f"{control_ref}_::_false",
                    project=component_ref
                )
                rule.actions.append(action)
                
                new_library.rules.append(rule)
    
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
