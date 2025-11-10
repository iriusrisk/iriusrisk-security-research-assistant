"""
YSC import service for IriusRisk Content Manager API
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
from isra.src.config.constants import OUTPUT_NAME, CATEGORIES_LIST, STRIDE_LIST, OPENCRE_PLUS, CRE_MAPPING_NAME
from isra.src.config.config import get_resource
from isra.src.utils.text_functions import generate_identifier_from_ref
from isra.src.utils.cwe_functions import get_original_cwe_weaknesses, get_cwe_description, get_cwe_impact

logger = logging.getLogger(__name__)


class YSCImportService:
    """Service for importing YSC component files"""
    
    def __init__(self):
        self._opencre_mappings = None
    
    def _get_opencre_mappings(self):
        """Get OpenCRE+ mappings, caching the result"""
        if self._opencre_mappings is None:
            self._opencre_mappings = get_resource(OPENCRE_PLUS)
        return self._opencre_mappings
    
    def _get_standard_from_opencre(self, baseline_ref: str, base_standard_section: str) -> Dict[str, set]:
        """
        Get expanded standards from OpenCRE+ mappings for a given baseline standard and section.
        Returns a dictionary mapping standard names to sets of sections.
        """
        mappings_yaml = self._get_opencre_mappings()
        
        # Check if baseline_ref is in CRE_MAPPING_NAME
        if baseline_ref not in CRE_MAPPING_NAME:
            return {}
        
        opencre_standard_name = CRE_MAPPING_NAME[baseline_ref]
        standards_to_add = dict()
        
        # Now we iterate over the OpenCRE+ keys searching for the standard
        for cre_id, cre_values in mappings_yaml.items():
            if opencre_standard_name in cre_values:
                # Now it may happen that the section doesn't appear exactly as it is in the OpenCRE+, so we
                # apply special techniques to look for the best match
                adapted = base_standard_section
                
                if adapted in cre_values[opencre_standard_name]:
                    # If the section of the standard can be found inside the CRE we add all values
                    # of that standard and the CRE ID
                    standards_to_add.update(cre_values)
                    if "CRE" not in standards_to_add:
                        standards_to_add["CRE"] = set()
                    standards_to_add["CRE"].add(cre_id)
        
        # We convert the lists to sets to remove duplicates
        standards_to_add = {key: set(value) for key, value in standards_to_add.items()}
        
        return standards_to_add
    
    def _expand_standards_from_base(self, base_standard: str, base_standard_sections: List[str]) -> Dict[str, List[str]]:
        """
        Expand standards from base_standard and base_standard_sections using OpenCRE+ mappings.
        Returns a dictionary mapping standard names (from OUTPUT_NAME) to lists of sections.
        """
        expanded_standards = {}
        
        if not base_standard or not base_standard_sections:
            return expanded_standards
        
        # Process each section
        for base_section in base_standard_sections:
            if not base_section:
                continue
            
            # Get expanded standards from OpenCRE
            standards_to_add = self._get_standard_from_opencre(base_standard, base_section)
            
            if len(standards_to_add) == 0:
                # If no standards found, add the base standard itself
                if base_standard in OUTPUT_NAME:
                    supported_standard_ref = OUTPUT_NAME[base_standard]["ref"]
                    if supported_standard_ref not in expanded_standards:
                        expanded_standards[supported_standard_ref] = []
                    if base_section not in expanded_standards[supported_standard_ref]:
                        expanded_standards[supported_standard_ref].append(base_section)
            else:
                # Add all expanded standards
                for standard_name, sections in standards_to_add.items():
                    # Map standard_name to supported_standard_ref using OUTPUT_NAME
                    # standard_name from OpenCRE is typically a key in OUTPUT_NAME (like "NIST 800-53 v5", "ASVS", etc.)
                    supported_standard_ref = None
                    
                    # First, check if standard_name is a direct key in OUTPUT_NAME
                    if standard_name in OUTPUT_NAME:
                        supported_standard_ref = OUTPUT_NAME[standard_name]["ref"]
                    else:
                        # Try to find by matching ref or name
                        for key, value in OUTPUT_NAME.items():
                            if value["ref"] == standard_name or value["name"] == standard_name:
                                supported_standard_ref = value["ref"]
                                break
                        
                        # If not found in OUTPUT_NAME, use the standard_name as-is (might be CRE or other)
                        if supported_standard_ref is None:
                            # For CRE, map to OpenCRE
                            if standard_name == "CRE":
                                supported_standard_ref = "OpenCRE"
                            else:
                                supported_standard_ref = standard_name
                    
                    if supported_standard_ref not in expanded_standards:
                        expanded_standards[supported_standard_ref] = []
                    
                    for section in sections:
                        if section not in expanded_standards[supported_standard_ref]:
                            expanded_standards[supported_standard_ref].append(section)
        
        return expanded_standards
    
    def _merge_and_deduplicate_standards(
        self, 
        expanded_standards: Dict[str, List[str]], 
        manual_standards: Dict[str, List[str]]
    ) -> Dict[str, List[str]]:
        """
        Merge expanded standards with manual standards and remove duplicates.
        Returns a dictionary mapping supported_standard_ref to list of standard_ref sections.
        """
        merged = {}
        
        # Add expanded standards
        for supported_standard_ref, sections in expanded_standards.items():
            if supported_standard_ref not in merged:
                merged[supported_standard_ref] = []
            for section in sections:
                if section not in merged[supported_standard_ref]:
                    merged[supported_standard_ref].append(section)
        
        # Add manual standards (from standards dict in YAML)
        for standard_name, standard_sections in manual_standards.items():
            if standard_name in OUTPUT_NAME:
                supported_standard_ref = OUTPUT_NAME[standard_name]["ref"]
                if supported_standard_ref not in merged:
                    merged[supported_standard_ref] = []
                
                if isinstance(standard_sections, list):
                    for section in standard_sections:
                        if section not in merged[supported_standard_ref]:
                            merged[supported_standard_ref].append(section)
        
        return merged
    
    def _find_library_by_category(self, category_ref: str, version_element: ILEVersion) -> Optional[IRLibrary]:
        """Find existing library that matches the category pattern for components"""
        if not category_ref:
            return None
        
        # Look for libraries with names like "{category}-components" or containing the category
        # Exclude rules libraries (those ending with -rules)
        category_variations = [
            f"{category_ref}-components",
            f"{category_ref}-component",
            category_ref
        ]
        
        for library in version_element.libraries.values():
            # Skip rules libraries
            if library.ref.endswith("-rules") or library.name.endswith("-rules"):
                continue
            
            # Check if library ref or name matches category pattern
            if library.ref in category_variations or library.name in category_variations:
                return library
            # Also check if library ref/name contains the category
            if category_ref in library.ref or category_ref in library.name:
                return library
        
        return None
    
    def _find_rules_library_by_category(self, category_ref: str, version_element: ILEVersion) -> Optional[IRLibrary]:
        """Find existing rules library that matches the category pattern"""
        if not category_ref:
            return None
        
        # Look for libraries with names like "{category}-rules" or "{category}-components-rules"
        # First, try exact match with -rules suffix
        rules_variations = [
            f"{category_ref}-rules",
            f"{category_ref}-rules-library"
        ]
        
        # If category already ends with -components, also try replacing it with -rules
        if category_ref.endswith("-components"):
            base_category = category_ref[:-len("-components")]
            rules_variations.extend([
                f"{base_category}-rules",
                f"{category_ref}-rules"
            ])
        
        for library in version_element.libraries.values():
            # Check if library ref or name matches rules pattern
            if library.ref in rules_variations or library.name in rules_variations:
                return library
            # Also check if library ref/name contains the category and ends with -rules
            if category_ref in library.ref and library.ref.endswith("-rules"):
                return library
            if category_ref in library.name and library.name.endswith("-rules"):
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
            
            # Check if there's an existing library matching the category for components
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
            
            # Check if there's an existing rules library matching the category
            existing_rules_library = self._find_rules_library_by_category(component_category, version_element)
            
            if existing_rules_library:
                # Use existing rules library
                rules_library = existing_rules_library
                print(f"Importing YSC rules into existing rules library: {rules_library.ref}")
            else:
                # Create new rules library
                # Determine rules library ref based on category
                rules_library_ref = f"{component_category}-rules"
                
                rules_library = IRLibrary(
                    ref=rules_library_ref,
                    name=f"{component_category} - Rules",
                    desc=f"This library holds the rules for the components in the {component_category} library",
                    revision="1",
                    filename="",
                    enabled="true"
                )
                print(f"Importing YSC rules: {rules_library.ref}")
                version_element.libraries[rules_library.ref] = rules_library
            
            # Import various elements
            self._set_category_components(component_category, version_element)
            self._set_component_definitions(component, new_library)
            
            # Get risk pattern from component
            risk_pattern_data = component.get("risk_pattern", {})
            if risk_pattern_data:
                self._set_risk_patterns(risk_pattern_data, new_library, version_element)
                self._set_rules(component, rules_library)
            
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
        
        # Check if component definition already exists by ref
        existing_component_def = self._find_component_definition_by_ref(new_library, component_ref)
        
        if existing_component_def:
            # Update existing component definition with imported content
            component_definition = existing_component_def
            logger.debug(f"Updating existing component definition: {component_ref}")
            
            # Update attributes
            component_definition.name = component_name
            component_definition.desc = component_desc
            component_definition.category_ref = component_category
            
            # Update risk pattern refs (replace list with imported content)
            risk_pattern_data = component.get("risk_pattern", {})
            if risk_pattern_data:
                risk_pattern_ref = risk_pattern_data.get("ref", "")
                component_definition.risk_pattern_refs = [risk_pattern_ref] if risk_pattern_ref else []
            else:
                component_definition.risk_pattern_refs = []
        else:
            # Create new component definition
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
        
        # Check if risk pattern already exists by ref
        existing_risk_pattern = self._find_risk_pattern_by_ref(new_library, risk_pattern_ref)
        
        if existing_risk_pattern:
            # Update existing risk pattern with imported content
            risk_pattern = existing_risk_pattern
            logger.debug(f"Updating existing risk pattern: {risk_pattern_ref}")
            
            # Update attributes
            risk_pattern.name = risk_pattern_name
            risk_pattern.desc = risk_pattern_desc
        else:
            # Create new risk pattern
            risk_pattern = IRRiskPattern(
                ref=risk_pattern_ref,
                name=risk_pattern_name,
                desc=risk_pattern_desc
            )
            new_library.risk_patterns[risk_pattern.uuid] = risk_pattern
        
        # Process threats
        threats_data = risk_pattern_data.get("threats", [])
        controls_dict = {}  # Track controls by ref

        for threat_data in threats_data:
            threat_ref = threat_data.get("ref", "")
            # Check if threat already exists by ref
            existing_threat = self._find_threat_by_ref(version_element, threat_ref)

            if existing_threat:
                # Update existing threat with imported content
                threat = existing_threat
                logger.debug(f"Updating existing threat: {threat_ref}")
                self._update_threat_from_yaml(threat, threat_data, version_element)
            else:
                threat = self._create_threat_from_yaml(threat_data, version_element)
                version_element.threats[threat.uuid] = threat

            # Process countermeasures for this threat
            countermeasures_data = threat_data.get("countermeasures") or []
            for countermeasure_data in countermeasures_data:
                control_ref = countermeasure_data.get("ref", "")
                # Check if control already exists by ref
                existing_control = self._find_control_by_ref(version_element, control_ref)

                if existing_control:
                    # Update existing control with imported content
                    control = existing_control
                    logger.debug(f"Updating existing control: {control_ref}")
                    self._update_control_from_yaml(control, countermeasure_data, version_element)
                else:
                    control = self._create_control_from_yaml(countermeasure_data, version_element)
                    version_element.controls[control.uuid] = control

                controls_dict[control.ref] = control

        # Create usecases and relations based on STRIDE groups
        original_cwe_weaknesses = get_original_cwe_weaknesses()
        
        # Track expected relations from YSC file (as tuples for comparison)
        expected_relations = set()

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

                    # Check if weakness already exists by ref, considering relation context
                    existing_weakness = self._find_weakness_by_ref(
                        version_element, 
                        cwe_ref, 
                        new_library, 
                        risk_pattern.uuid, 
                        usecase.uuid, 
                        threat.uuid, 
                        control.uuid
                    )

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
                        # Update existing weakness with imported content
                        logger.debug(f"Updating existing weakness: {cwe_ref}")
                        existing_weakness.name = cwe_ref
                        cwe_ids = cwe_ref.split(" ")
                        existing_weakness.desc = get_cwe_description(original_cwe_weaknesses, cwe_ids)
                        cwe_impact = countermeasure_data.get("cwe_impact", "100")
                        existing_weakness.impact = cwe_impact
                        weakness_uuid = existing_weakness.uuid

                # Create relation: threat -> weakness -> countermeasure (or threat -> countermeasure if no weakness)
                # Check if relation already exists by checking if a relation with the same UUIDs exists
                relation_exists = False
                existing_relation_uuid = None
                for existing_relation in new_library.relations.values():
                    if (existing_relation.risk_pattern_uuid == risk_pattern.uuid and
                        existing_relation.usecase_uuid == usecase.uuid and
                        existing_relation.threat_uuid == threat.uuid and
                        existing_relation.weakness_uuid == weakness_uuid and
                        existing_relation.control_uuid == control.uuid):
                        relation_exists = True
                        existing_relation_uuid = existing_relation.uuid
                        logger.debug(f"Relation already exists, skipping: {threat.ref} -> {control.ref}")
                        break

                if not relation_exists:
                    relation = IRRelation(
                        risk_pattern_uuid=risk_pattern.uuid,
                        usecase_uuid=usecase.uuid,
                        threat_uuid=threat.uuid,
                        weakness_uuid=weakness_uuid,
                        control_uuid=control.uuid,
                        mitigation=""
                    )
                    new_library.relations[relation.uuid] = relation
                    expected_relations.add((risk_pattern.uuid, usecase.uuid, threat.uuid, weakness_uuid, control.uuid))
                else:
                    # Track existing relation as expected
                    expected_relations.add((risk_pattern.uuid, usecase.uuid, threat.uuid, weakness_uuid, control.uuid))

        # Remove relations that exist in the library but are not in the YSC file
        # Only remove relations for this specific risk pattern
        relations_to_remove = []
        for relation_uuid, relation in new_library.relations.items():
            if relation.risk_pattern_uuid == risk_pattern.uuid:
                relation_key = (
                    relation.risk_pattern_uuid,
                    relation.usecase_uuid,
                    relation.threat_uuid,
                    relation.weakness_uuid,
                    relation.control_uuid
                )
                if relation_key not in expected_relations:
                    relations_to_remove.append(relation_uuid)
                    logger.debug(f"Removing relation not in YSC: {relation_uuid} (threat: {relation.threat_uuid}, control: {relation.control_uuid})")
        
        for relation_uuid in relations_to_remove:
            del new_library.relations[relation_uuid]
            logger.debug(f"Removed relation: {relation_uuid}")

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
        risk_score_data = threat_data.get("risk_score") or {}
        if risk_score_data:
            risk_rating = IRRiskRating(
                confidentiality=risk_score_data.get("confidentiality", "100"),
                integrity=risk_score_data.get("integrity", "100"),
                availability=risk_score_data.get("availability", "100"),
                ease_of_exploitation=risk_score_data.get("ease_of_exploitation", "100")
            )
            threat.risk_rating = risk_rating
        
        # Taxonomies - STRIDE
        taxonomies_data = threat_data.get("taxonomies") or {}
        stride_data = taxonomies_data.get("stride") or []
        if stride_data:
            threat.stride = stride_data
        
        # Taxonomies - MITRE
        attack_enterprise_technique = taxonomies_data.get("attack_enterprise_technique") or []
        if attack_enterprise_technique:
            threat.mitre = attack_enterprise_technique
        
        # References
        references_data = threat_data.get("references") or []
        for ref_data in references_data:
            ref_name = ref_data.get("name", "")
            ref_url = ref_data.get("url", "")
            
            if ref_name and ref_url:
                # Check if reference already exists in this threat by name
                existing_ref_key = self._find_reference_in_item(
                    threat.references, version_element, ref_name, ref_url
                )
                
                if existing_ref_key:
                    # Reference already exists in this threat, skip it
                    logger.debug(f"Reference already exists in threat: {ref_name}")
                    continue
                
                # Check if reference exists in version
                existing_ref = self._check_reference_exists_in_version(
                    version_element, ref_name, ref_url
                )
                
                if existing_ref:
                    # Use existing reference, generate new key for this threat
                    threat.references[str(uuid.uuid4())] = existing_ref.uuid
                else:
                    # Create new reference
                    new_reference = IRReference(name=ref_name, url=ref_url)
                    version_element.references[new_reference.uuid] = new_reference
                    threat.references[str(uuid.uuid4())] = new_reference.uuid
        
        return threat
    
    def _update_threat_from_yaml(self, threat: IRThreat, threat_data: Dict, version_element: ILEVersion) -> None:
        """Update existing threat with imported YAML data"""
        threat.name = threat_data.get("name", "")
        threat.desc = threat_data.get("description", "")
        
        # Update risk score
        risk_score_data = threat_data.get("risk_score") or {}
        if risk_score_data:
            if threat.risk_rating is None:
                threat.risk_rating = IRRiskRating(
                    confidentiality="100",
                    integrity="100",
                    availability="100",
                    ease_of_exploitation="100"
                )
            threat.risk_rating.confidentiality = risk_score_data.get("confidentiality", "100")
            threat.risk_rating.integrity = risk_score_data.get("integrity", "100")
            threat.risk_rating.availability = risk_score_data.get("availability", "100")
            threat.risk_rating.ease_of_exploitation = risk_score_data.get("ease_of_exploitation", "100")
        
        # Update taxonomies - STRIDE (replace list)
        taxonomies_data = threat_data.get("taxonomies") or {}
        stride_data = taxonomies_data.get("stride") or []
        threat.stride = stride_data if stride_data else []
        
        # Update taxonomies - MITRE (replace list)
        attack_enterprise_technique = taxonomies_data.get("attack_enterprise_technique") or []
        threat.mitre = attack_enterprise_technique if attack_enterprise_technique else []
        
        # Update references - preserve existing mapping UUIDs when possible
        references_data = threat_data.get("references") or []
        
        # Build set of references that should exist (by name/url)
        expected_refs = set()
        for ref_data in references_data:
            ref_name = ref_data.get("name", "")
            ref_url = ref_data.get("url", "")
            if ref_name and ref_url:
                expected_refs.add((ref_name, ref_url))
        
        # Process references from YSC - preserve existing mapping UUIDs
        for ref_data in references_data:
            ref_name = ref_data.get("name", "")
            ref_url = ref_data.get("url", "")
            
            if ref_name and ref_url:
                # Check if reference already exists in this threat by name/url
                existing_ref_key = self._find_reference_in_item(
                    threat.references, version_element, ref_name, ref_url
                )
                
                if existing_ref_key:
                    # Reference already exists in this threat, preserve the mapping UUID
                    logger.debug(f"Preserving existing reference mapping in threat: {ref_name}")
                    continue
                
                # Check if reference exists in version
                existing_ref = self._check_reference_exists_in_version(
                    version_element, ref_name, ref_url
                )
                
                if existing_ref:
                    # Use existing reference, generate new mapping UUID for this threat
                    threat.references[str(uuid.uuid4())] = existing_ref.uuid
                else:
                    # Create new reference
                    new_reference = IRReference(name=ref_name, url=ref_url)
                    version_element.references[new_reference.uuid] = new_reference
                    threat.references[str(uuid.uuid4())] = new_reference.uuid
        
        # Remove references that are no longer in YSC
        refs_to_remove = []
        for ref_key, ref_uuid in threat.references.items():
            if ref_uuid in version_element.references:
                ref = version_element.references[ref_uuid]
                if (ref.name, ref.url) not in expected_refs:
                    refs_to_remove.append(ref_key)
        
        for ref_key in refs_to_remove:
            del threat.references[ref_key]
            logger.debug(f"Removed reference from threat: {ref_key}")
    
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
        references_data = countermeasure_data.get("references") or []
        for ref_data in references_data:
            ref_name = ref_data.get("name", "")
            ref_url = ref_data.get("url", "")
            
            if ref_name and ref_url:
                # Check if reference already exists in this control by name
                existing_ref_key = self._find_reference_in_item(
                    control.references, version_element, ref_name, ref_url
                )
                
                if existing_ref_key:
                    # Reference already exists in this control, skip it
                    logger.debug(f"Reference already exists in control: {ref_name}")
                    continue
                
                # Check if reference exists in version
                existing_ref = self._check_reference_exists_in_version(
                    version_element, ref_name, ref_url
                )
                
                if existing_ref:
                    # Use existing reference, generate new key for this control
                    control.references[str(uuid.uuid4())] = existing_ref.uuid
                else:
                    # Create new reference
                    new_reference = IRReference(name=ref_name, url=ref_url)
                    version_element.references[new_reference.uuid] = new_reference
                    control.references[str(uuid.uuid4())] = new_reference.uuid
        
        # Standards - expand from base_standard/base_standard_section and merge with manual standards
        standards_data = countermeasure_data.get("standards") or {}
        base_standard = countermeasure_data.get("base_standard") or ""
        base_standard_section = countermeasure_data.get("base_standard_section") or []
        
        # Ensure base_standard_section is a list
        if isinstance(base_standard_section, str):
            base_standard_section = [base_standard_section]
        
        # Expand standards from base_standard and base_standard_section
        expanded_standards = self._expand_standards_from_base(base_standard, base_standard_section)
        
        # Merge expanded standards with manual standards and deduplicate
        all_standards = self._merge_and_deduplicate_standards(expanded_standards, standards_data)
        
        # Add all standards to the control
        for supported_standard_ref, sections in all_standards.items():
            # Get supported standard name from OUTPUT_NAME
            supported_standard_name = supported_standard_ref
            for key, value in OUTPUT_NAME.items():
                if value["ref"] == supported_standard_ref:
                    supported_standard_name = value["name"]
                    break
            
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
            for section in sections:
                existing_standard = self._check_standard_exists_in_version(
                    version_element, supported_standard_ref, section
                )
                if existing_standard:
                    # Check if this standard is already in the control to avoid duplicates
                    standard_already_in_control = False
                    for std_uuid in control.standards.values():
                        if std_uuid == existing_standard.uuid:
                            standard_already_in_control = True
                            break
                    if not standard_already_in_control:
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
        taxonomies_data = countermeasure_data.get("taxonomies") or {}
        scope_data = taxonomies_data.get("scope") or []
        if scope_data:
            control.scope = scope_data
        
        # Taxonomies - MITRE
        attack_enterprise_mitigation = taxonomies_data.get("attack_enterprise_mitigation") or []
        if attack_enterprise_mitigation:
            control.mitre = attack_enterprise_mitigation
        
        return control
    
    def _update_control_from_yaml(self, control: IRControl, countermeasure_data: Dict, version_element: ILEVersion) -> None:
        """Update existing control with imported YAML data"""
        control.name = countermeasure_data.get("name", "")
        control.desc = countermeasure_data.get("description", "")
        control.cost = countermeasure_data.get("cost", "0")
        
        # Update references - preserve existing mapping UUIDs when possible
        references_data = countermeasure_data.get("references") or []
        
        # Build set of references that should exist (by name/url)
        expected_refs = set()
        for ref_data in references_data:
            ref_name = ref_data.get("name", "")
            ref_url = ref_data.get("url", "")
            if ref_name and ref_url:
                expected_refs.add((ref_name, ref_url))
        
        # Process references from YSC - preserve existing mapping UUIDs
        for ref_data in references_data:
            ref_name = ref_data.get("name", "")
            ref_url = ref_data.get("url", "")
            
            if ref_name and ref_url:
                # Check if reference already exists in this control by name/url
                existing_ref_key = self._find_reference_in_item(
                    control.references, version_element, ref_name, ref_url
                )
                
                if existing_ref_key:
                    # Reference already exists in this control, preserve the mapping UUID
                    logger.debug(f"Preserving existing reference mapping in control: {ref_name}")
                    continue
                
                # Check if reference exists in version
                existing_ref = self._check_reference_exists_in_version(
                    version_element, ref_name, ref_url
                )
                
                if existing_ref:
                    # Use existing reference, generate new mapping UUID for this control
                    control.references[str(uuid.uuid4())] = existing_ref.uuid
                else:
                    # Create new reference
                    new_reference = IRReference(name=ref_name, url=ref_url)
                    version_element.references[new_reference.uuid] = new_reference
                    control.references[str(uuid.uuid4())] = new_reference.uuid
        
        # Remove references that are no longer in YSC
        refs_to_remove = []
        for ref_key, ref_uuid in control.references.items():
            if ref_uuid in version_element.references:
                ref = version_element.references[ref_uuid]
                if (ref.name, ref.url) not in expected_refs:
                    refs_to_remove.append(ref_key)
        
        for ref_key in refs_to_remove:
            del control.references[ref_key]
            logger.debug(f"Removed reference from control: {ref_key}")
        
        # Update standards (replace dictionary) - expand from base_standard/base_standard_section and merge with manual standards
        control.standards.clear()
        standards_data = countermeasure_data.get("standards") or {}
        base_standard = countermeasure_data.get("base_standard") or ""
        base_standard_section = countermeasure_data.get("base_standard_section") or []
        
        # Ensure base_standard_section is a list
        if isinstance(base_standard_section, str):
            base_standard_section = [base_standard_section]
        
        # Expand standards from base_standard and base_standard_section
        expanded_standards = self._expand_standards_from_base(base_standard, base_standard_section)
        
        # Merge expanded standards with manual standards and deduplicate
        all_standards = self._merge_and_deduplicate_standards(expanded_standards, standards_data)
        
        # Add all standards to the control
        for supported_standard_ref, sections in all_standards.items():
            # Get supported standard name from OUTPUT_NAME
            supported_standard_name = supported_standard_ref
            for key, value in OUTPUT_NAME.items():
                if value["ref"] == supported_standard_ref:
                    supported_standard_name = value["name"]
                    break
            
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
            for section in sections:
                existing_standard = self._check_standard_exists_in_version(
                    version_element, supported_standard_ref, section
                )
                if existing_standard:
                    # Check if this standard is already in the control to avoid duplicates
                    standard_already_in_control = False
                    for std_uuid in control.standards.values():
                        if std_uuid == existing_standard.uuid:
                            standard_already_in_control = True
                            break
                    if not standard_already_in_control:
                        control.standards[str(uuid.uuid4())] = existing_standard.uuid
                else:
                    new_standard = IRStandard(
                        supported_standard_ref=supported_standard_ref,
                        standard_ref=section
                    )
                    version_element.standards[new_standard.uuid] = new_standard
                    control.standards[str(uuid.uuid4())] = new_standard.uuid
        
        # Update base standard and base standard section (replace lists)
        if base_standard:
            control.base_standard = [base_standard]
        else:
            control.base_standard = []
        if base_standard_section:
            control.base_standard_section = base_standard_section if isinstance(base_standard_section, list) else [base_standard_section]
        else:
            control.base_standard_section = []
        
        # Update taxonomies - Scope (replace list)
        taxonomies_data = countermeasure_data.get("taxonomies") or {}
        scope_data = taxonomies_data.get("scope") or []
        control.scope = scope_data if scope_data else []
        
        # Update taxonomies - MITRE (replace list)
        attack_enterprise_mitigation = taxonomies_data.get("attack_enterprise_mitigation") or []
        control.mitre = attack_enterprise_mitigation if attack_enterprise_mitigation else []
    
    def _set_rules(self, component: Dict, rules_library: IRLibrary) -> None:
        """Set rules from YSC component data"""
        risk_pattern_data = component.get("risk_pattern", {})
        if not risk_pattern_data:
            return
        
        threats_data = risk_pattern_data.get("threats", [])
        component_ref = component.get("ref", "")

        # Collect questions from countermeasures
        questions = []

        for threat_data in threats_data:
            countermeasures_data = threat_data.get("countermeasures") or []
            for countermeasure_data in countermeasures_data:
                control_ref = countermeasure_data.get("ref", "")
                question = countermeasure_data.get("question") or ""
                question_desc = countermeasure_data.get("question_desc") or ""

                if question:
                    questions.append((control_ref, question, question_desc))

        # Create or update question group rule
        rule_name = f"Q - Security Context - {component_ref}"
        
        # Check if rule already exists by name
        existing_rule = None
        existing_rule_index = -1
        for idx, rule in enumerate(rules_library.rules):
            if rule.name == rule_name:
                existing_rule = rule
                existing_rule_index = idx
                break
        
        if questions:
            # Create or update rule with questions
            if existing_rule:
                # Update existing rule: clear actions and rebuild from YSC
                logger.debug(f"Updating existing rule: {rule_name}")
                existing_rule.actions.clear()
            else:
                # Create new rule
                existing_rule = IRRule(
                    name=rule_name,
                    module="component",
                    gui="true"
                )
                # Add condition
                condition = IRRuleCondition(name="CONDITION_COMPONENT_DEFINITION", field="id", value=component_ref)
                existing_rule.conditions.append(condition)
            
            # Add actions for questions (rebuild from current YSC content)
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

                action_value = (
                    f"provided.question.{control_ref}_::_Security Context_::_{question_text}_::_{priority}_::_true_::_false_::_{question_desc_text}"
                )
                action = IRRuleAction(
                    name="INSERT_COMPONENT_QUESTION_GROUP",
                    value=action_value,
                    project=""
                )
                existing_rule.actions.append(action)
                priority += 1
            
            # Add rule to library if it's new
            if existing_rule_index == -1:
                rules_library.rules.append(existing_rule)
        else:
            # No questions in YSC - remove rule if it exists
            if existing_rule:
                logger.debug(f"Removing rule with no questions: {rule_name}")
                rules_library.rules.pop(existing_rule_index)
    
    def _check_reference_exists_in_version(self, version: ILEVersion, name: str, url: str) -> Optional[IRReference]:
        """Check if reference exists in version"""
        for ref in version.references.values():
            if ref.name == name and ref.url == url:
                return ref
        return None
    
    def _find_reference_in_item(self, item_references: Dict[str, str], version: ILEVersion, ref_name: str, ref_url: str) -> Optional[str]:
        """
        Find if a reference already exists in a threat or control by name.
        Returns the key (UUID) in the item's references dictionary if found, None otherwise.
        """
        for ref_key, ref_uuid in item_references.items():
            if ref_uuid in version.references:
                ref = version.references[ref_uuid]
                if ref.name == ref_name and ref.url == ref_url:
                    return ref_key
        return None
    
    def _check_standard_exists_in_version(self, version: ILEVersion, supported_standard_ref: str, standard_ref: str) -> Optional[IRStandard]:
        """Check if standard exists in version"""
        for standard in version.standards.values():
            if standard.supported_standard_ref == supported_standard_ref and standard.standard_ref == standard_ref:
                return standard
        return None
    
    def _find_component_definition_by_ref(self, library: IRLibrary, component_ref: str) -> Optional[IRComponentDefinition]:
        """Find component definition by ref in library"""
        for comp_def in library.component_definitions.values():
            if comp_def.ref == component_ref:
                return comp_def
        return None
    
    def _find_risk_pattern_by_ref(self, library: IRLibrary, risk_pattern_ref: str) -> Optional[IRRiskPattern]:
        """Find risk pattern by ref in library"""
        for rp in library.risk_patterns.values():
            if rp.ref == risk_pattern_ref:
                return rp
        return None
    
    def _find_threat_by_ref(self, version: ILEVersion, threat_ref: str) -> Optional[IRThreat]:
        """Find threat by ref in version"""
        for threat in version.threats.values():
            if threat.ref == threat_ref:
                return threat
        return None
    
    def _find_control_by_ref(self, version: ILEVersion, control_ref: str) -> Optional[IRControl]:
        """Find control by ref in version"""
        for control in version.controls.values():
            if control.ref == control_ref:
                return control
        return None
    
    def _find_weakness_by_ref(
        self, 
        version: ILEVersion, 
        weakness_ref: str, 
        library: Optional[IRLibrary] = None,
        risk_pattern_uuid: Optional[str] = None,
        usecase_uuid: Optional[str] = None,
        threat_uuid: Optional[str] = None,
        control_uuid: Optional[str] = None
    ) -> Optional[IRWeakness]:
        """
        Find weakness by ref in version, considering relation context.
        
        If relation context is provided (library, risk_pattern_uuid, usecase_uuid, 
        threat_uuid, control_uuid), first tries to find a weakness that:
        1. Has the matching ref
        2. Is part of a relation that matches all the provided UUIDs
        
        If no such weakness is found, also checks if the threat is already related
        to a weakness with the same ref (even if other relation parts don't match).
        
        If still not found or no context is provided, falls back to searching by ref only.
        """
        # If relation context is provided, try to find weakness via relations
        if library and threat_uuid:
            # First, try to find a relation that matches ALL the context
            if risk_pattern_uuid and usecase_uuid and control_uuid:
                for relation in library.relations.values():
                    if (relation.risk_pattern_uuid == risk_pattern_uuid and
                        relation.usecase_uuid == usecase_uuid and
                        relation.threat_uuid == threat_uuid and
                        relation.control_uuid == control_uuid and
                        relation.weakness_uuid != ""):
                        # Found a matching relation, check if the weakness has the matching ref
                        weakness_uuid = relation.weakness_uuid
                        if weakness_uuid in version.weaknesses:
                            weakness = version.weaknesses[weakness_uuid]
                            if weakness.ref == weakness_ref:
                                logger.debug(f"Found weakness by ref and full relation context: {weakness_ref}")
                                return weakness
            
            # If not found, check if the threat is already related to a weakness with the same ref
            # (even if other relation parts don't match)
            for relation in library.relations.values():
                if (relation.threat_uuid == threat_uuid and
                    relation.weakness_uuid != ""):
                    weakness_uuid = relation.weakness_uuid
                    if weakness_uuid in version.weaknesses:
                        weakness = version.weaknesses[weakness_uuid]
                        if weakness.ref == weakness_ref:
                            logger.debug(f"Found weakness by ref and threat relation: {weakness_ref}")
                            return weakness
        
        # Fall back to searching by ref only (original behavior)
        for weakness in version.weaknesses.values():
            if weakness.ref == weakness_ref:
                return weakness
        return None
    
