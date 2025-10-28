"""
Test service for IriusRisk Library Editor API
"""

import inspect
import logging
from typing import List, Set, Dict

from isra.src.ile.backend.app.models import (
    ILEVersion, IRCategoryComponent, IRComponentDefinition, IRControl,
    IRLibrary, IRReference, IRRelation, IRRiskPattern, IRRule,
    IRRuleAction, IRRuleCondition, IRThreat, IRWeakness,
    IRMitigationItem, IRMitigationReport, IRMitigationRiskPattern,
    IRTestReport
)
from isra.src.ile.backend.app.services.data_service import DataService
from isra.src.ile.backend.app.services.library_service import LibraryService

logger = logging.getLogger(__name__)


class TestService:
    """Service for running tests on versions"""
    
    def __init__(self):
        self.data_service = DataService()
        self.library_service = LibraryService()
    
    def run_tests(self, version_ref: str) -> IRTestReport:
        """Run all tests on version using reflection-like approach"""
        report = IRTestReport(version_ref=version_ref)
        v = self.data_service.get_version(version_ref)
        
        success = 0
        failed = 0
        
        # Get all methods that start with "test"
        test_methods = [
            method for name, method in inspect.getmembers(self, predicate=inspect.ismethod)
            if name.startswith("test") and name != "run_tests"
        ]
        
        for method in test_methods:
            try:
                errors = method(v)
                report.test_results[method.__name__] = errors
                if not errors:
                    success += 1
                else:
                    failed += 1
            except Exception as e:
                logger.error(f"Error running test {method.__name__}: {e}")
                report.test_results[method.__name__] = [f"Test failed with error: {e}"]
                failed += 1
        
        report.num_success_tests = success
        report.num_failed_tests = failed
        
        return report
    
    def test_ascii_control_desc(self, v: ILEVersion) -> List[str]:
        """Test ASCII characters in control descriptions"""
        errors = []
        for c in v.controls.values():
            non_ascii = self._check_ascii(c.desc)
            if non_ascii:
                errors.append(f"{c.ref} has non-ASCII character {non_ascii}")
        return errors
    
    def test_ascii_control_test_steps(self, v: ILEVersion) -> List[str]:
        """Test ASCII characters in control test steps"""
        errors = []
        for c in v.controls.values():
            non_ascii = self._check_ascii(c.test.steps)
            if non_ascii:
                errors.append(f"{c.ref} has non-ASCII character {non_ascii}")
        return errors
    
    def test_ascii_weakness_desc(self, v: ILEVersion) -> List[str]:
        """Test ASCII characters in weakness descriptions"""
        errors = []
        for c in v.weaknesses.values():
            non_ascii = self._check_ascii(c.desc)
            if non_ascii:
                errors.append(f"{c.ref} has non-ASCII character {non_ascii}")
        return errors
    
    def test_ascii_weakness_test_steps(self, v: ILEVersion) -> List[str]:
        """Test ASCII characters in weakness test steps"""
        errors = []
        for c in v.weaknesses.values():
            non_ascii = self._check_ascii(c.test.steps)
            if non_ascii:
                errors.append(f"{c.ref} has non-ASCII character {non_ascii}")
        return errors
    
    def test_ascii_threat_desc(self, v: ILEVersion) -> List[str]:
        """Test ASCII characters in threat descriptions"""
        errors = []
        for c in v.threats.values():
            non_ascii = self._check_ascii(c.desc)
            if non_ascii:
                errors.append(f"{c.ref} has non-ASCII character {non_ascii}")
        return errors
    
    def test_correct_mitigation(self, v: ILEVersion) -> List[str]:
        """Test correct mitigation values"""
        errors = []
        for library_ref in v.libraries.keys():
            report = self.library_service.check_mitigation(v.version, library_ref)
            for rp in report.risk_patterns:
                for item in rp.threats:
                    if item.error:
                        errors.append(f"{library_ref} -> {rp.ref} -> {item.threat_ref} -> {item.message}")
        return errors
    
    def test_empty_threat_desc(self, v: ILEVersion) -> List[str]:
        """Test for empty threat descriptions"""
        errors = []
        for t in v.threats.values():
            if t.desc == "":
                errors.append(f"{t.ref} has empty description")
        return errors
    
    def test_weaknesses_without_controls(self, v: ILEVersion) -> List[str]:
        """Test for weaknesses without controls"""
        errors = []
        exceptions = ["CWE-7-KINGDOMS"]  # Special risk pattern
        
        for l in v.libraries.values():
            for rel in l.relations.values():
                if (rel.risk_pattern_uuid not in exceptions and 
                    rel.weakness_uuid != "" and 
                    rel.control_uuid == ""):
                    errors.append(f"There is a weakness without controls on {rel.risk_pattern_uuid} -> {rel.usecase_uuid} -> {rel.threat_uuid} -> {rel.weakness_uuid}")
        return errors
    
    def test_empty_control_desc(self, v: ILEVersion) -> List[str]:
        """Test for empty control descriptions"""
        errors = []
        for c in v.controls.values():
            if c.desc == "":
                errors.append(f"{c.ref} has empty description")
        return errors
    
    def test_orphaned_controls(self, v: ILEVersion) -> List[str]:
        """Test for orphaned controls"""
        exceptions = ["IR-Functional-Components", "mitre-attack-framework"]
        errors = []
        
        for l in v.libraries.values():
            if l.ref in exceptions:
                continue
            for rel in l.relations.values():
                if rel.weakness_uuid == "" and rel.control_uuid != "":
                    errors.append(f"There is an orphaned relation on {rel}")
        return errors
    
    def test_whitespaces_in_references(self, v: ILEVersion) -> List[str]:
        """Test for whitespaces in reference URLs"""
        errors = []
        for ref_key, ref in v.references.items():
            if " " in ref.url:
                errors.append(f"Reference '{ref_key}' has whitespaces in URL: {ref.url}")
        return errors
    
    def test_all_controls_are_recommended(self, v: ILEVersion) -> List[str]:
        """Test that all controls are recommended by default"""
        errors = []
        for c in v.controls.values():
            if c.state != "Recommended":
                errors.append(f"Control {c.ref} is not Recommended by default")
        return errors
    
    def test_unused_usecases(self, v: ILEVersion) -> List[str]:
        """Test for unused use cases"""
        return self._get_unused_elements(v, "usecase")
    
    def test_unused_threats(self, v: ILEVersion) -> List[str]:
        """Test for unused threats"""
        return self._get_unused_elements(v, "threat")
    
    def test_unused_weaknesses(self, v: ILEVersion) -> List[str]:
        """Test for unused weaknesses"""
        return self._get_unused_elements(v, "weakness")
    
    def test_unused_controls(self, v: ILEVersion) -> List[str]:
        """Test for unused controls"""
        return self._get_unused_elements(v, "control")
    
    def test_integrity_categories(self, v: ILEVersion) -> List[str]:
        """Test category integrity"""
        errors = []
        for c in v.categories.values():
            if c.ref == "" or c.name == "":
                errors.append(f"Wrong category content: {c}")
        return errors
    
    def test_integrity_component_definitions(self, v: ILEVersion) -> List[str]:
        """Test component definition integrity"""
        errors = []
        for l in v.libraries.values():
            for c in l.component_definitions.values():
                if (c.ref == "" or c.name == "" or 
                    c.category_ref == "" or not c.risk_pattern_refs):
                    errors.append(f"Wrong component content: {c}")
        return errors
    
    def test_unimported_risk_pattern(self, v: ILEVersion) -> List[str]:
        """Test for unimported risk patterns"""
        errors = []
        actions = {
            "IMPORT_RISK_PATTERN", "EXTEND_RISK_PATTERN", 
            "IMPORT_RISK_PATTERN_ORIGIN", "IMPORT_RISK_PATTERN_DESTINATION"
        }
        
        rules = set()
        for l in v.libraries.values():
            rules.update(l.rules)
        
        component_definitions = set()
        for l in v.libraries.values():
            component_definitions.update(l.component_definitions.values())
        
        exceptions = ["mitre-attack-framework"]
        
        for l in v.libraries.values():
            if l.ref in exceptions:
                continue
            for rp in l.risk_patterns.values():
                found = False
                
                # Check if referenced in component definitions
                if any(rp.ref in comp.risk_pattern_refs for comp in component_definitions):
                    found = True
                
                # Check if referenced in rules
                for r in rules:
                    for ra in r.actions:
                        if ra.name in actions and rp.ref in ra.value:
                            found = True
                            break
                
                if not found:
                    errors.append(f"Risk pattern {rp.ref} cannot be imported")
        return errors
    
    def test_wrong_risk_pattern_in_component(self, v: ILEVersion) -> List[str]:
        """Test for wrong risk patterns in components"""
        errors = []
        
        all_risk_patterns = set()
        component_definitions = set()
        for l in v.libraries.values():
            component_definitions.update(l.component_definitions.values())
            for rp in l.risk_patterns.values():
                all_risk_patterns.add(rp.ref)
        
        for c in component_definitions:
            for rp in c.risk_pattern_refs:
                if rp not in all_risk_patterns:
                    errors.append(f"{c.ref}: risk pattern not found: {rp}")
        return errors
    
    def test_wrong_library_reference_in_rule(self, v: ILEVersion) -> List[str]:
        """Test for wrong library references in rules"""
        errors = []
        libraries = set()
        rules = set()
        
        for l in v.libraries.values():
            rules.update(l.rules)
            libraries.add(l.ref)
        
        for r in rules:
            for c in r.conditions:
                if c.name == "CONDITION_RISK_PATTERN_EXISTS":
                    lib = c.value.split("_::_")[0]
                    if lib not in libraries:
                        errors.append(f"A condition on rule '{r.name}' has a library reference wrong: {c.value}")
            
            for a in r.actions:
                if a.name == "IMPORT_RISK_PATTERN":
                    lib = a.value.split("_::_")[0]
                    if lib not in libraries:
                        errors.append(f"An action on rule '{r.name}' has a library reference wrong: {a.value}")
                    if a.project and a.project not in libraries:
                        errors.append(f"An action on rule '{r.name}' has a library reference wrong: {a.project}")
        return errors
    
    def test_unhandled_rules_elements(self, v: ILEVersion) -> List[str]:
        """Test for unhandled rule elements"""
        errors = []
        rules = set()
        for l in v.libraries.values():
            rules.update(l.rules)
        
        # Hardcoded: If the condition/action is not here we need to add them
        handled_conditions = {
            "CONDITION_COMPONENT_DEFINITION", "CONDITION_QUESTION_GROUP_EXISTS",
            "CONDITION_QUESTION", "CONDITION_QUESTION_NOT_ANSWERED",
            "CONDITION_COMPONENT_QUESTION_GROUP_EXISTS", "CONDITION_COMPONENT_QUESTION",
            "CONDITION_COMPONENT_QUESTION_NOT_ANSWERED", "CONDITION_RISK_PATTERN_EXISTS",
            "CONDITION_CONCLUSION_EXISTS", "CONDITION_CONCLUSION_COMPONENT_EXISTS",
            "CONDITION_CONCLUSION_NOT_EXISTS", "CONDITION_CONCLUSION_COMPONENT_NOT_EXISTS",
            "CONDITION_APPLIED_CONTROL", "CONDITION_DATAFLOW_CONTAINS_TAG",
            "CONDITION_CLASSIFICATION", "CONDITION_DATAFLOW_CONTAINS_ASSET",
            "CONDITION_ORIGIN_TRUSTZONE", "CONDITION_DESTINATION_TRUSTZONE",
            "CONDITION_DATAFLOW_CROSS_TRUST_BOUNDARY", "CONDITION_DATAFLOW_RISK_PATTERN_IN_ORIGIN",
            "CONDITION_DATAFLOW_RISK_PATTERN_IN_DESTINATION"
        }
        
        handled_actions = {
            "INSERT_QUESTION_GROUP", "INSERT_COMPONENT_QUESTION_GROUP",
            "INSERT_QUESTION", "INSERT_COMPONENT_QUESTION", "IMPORT_RISK_PATTERN",
            "EXTEND_RISK_PATTERN", "INSERT_CONCLUSION", "INSERT_COMPONENT_CONCLUSION",
            "APPLY_CONTROL", "APPLY_SECURITY_STANDARD", "ANSWER_QUESTION",
            "ANSWER_COMPONENT_QUESTION", "IMPORT_SPECIFIC_UC", "INSERT_CONCLUSION_ORIGIN_COMPONENT",
            "INSERT_CONCLUSION_DESTINATION_COMPONENT", "INSERT_DATAFLOW_NOTIFICATION",
            "INSERT_COMPONENT_NOTIFICATION", "IMPLEMENT_CONTROL_ORIGIN",
            "IMPLEMENT_CONTROL_DESTINATION", "IMPORT_RISK_PATTERN_DESTINATION",
            "MARK_CONTROL_AS", "INSERT_COMPONENT_ALERT", "IMPORT_RISK_PATTERN_ORIGIN"
        }
        
        for r in rules:
            for c in r.conditions:
                if c.name not in handled_conditions:
                    errors.append(f"Unhandled condition: {c.name}")
            
            for a in r.actions:
                if a.name not in handled_actions:
                    errors.append(f"Unhandled action: {a.name}")
        return errors
    
    def test_duplicated_risk_patterns(self, v: ILEVersion) -> List[str]:
        """Test for duplicated risk patterns"""
        errors = []
        seen = set()
        
        for l in v.libraries.values():
            for rp_uuid in l.risk_patterns.keys():
                if rp_uuid not in seen:
                    seen.add(rp_uuid)
                else:
                    errors.append(f"Risk pattern {rp_uuid} appears more than once")
        return errors
    
    def _get_unused_elements(self, v: ILEVersion, element: str) -> List[str]:
        """Get unused elements of specified type"""
        errors = []
        
        used = set()
        for l in v.libraries.values():
            for rel in l.relations.values():
                if element == "usecase":
                    used.add(rel.usecase_uuid)
                elif element == "threat":
                    used.add(rel.threat_uuid)
                elif element == "weakness":
                    used.add(rel.weakness_uuid)
                elif element == "control":
                    used.add(rel.control_uuid)
        
        elements = None
        if element == "usecase":
            elements = set(v.usecases.keys())
        elif element == "threat":
            elements = set(v.threats.keys())
        elif element == "weakness":
            elements = set(v.weaknesses.keys())
        elif element == "control":
            elements = set(v.controls.keys())
        
        if elements is not None:
            unused = elements - used
            if unused:
                errors.append(f"Unused: {unused}")
        
        return errors
    
    def _check_ascii(self, text: str) -> Set[str]:
        """Check for non-ASCII characters in text"""
        found = set()
        for i, char in enumerate(text):
            if ord(char) > 127:
                found.add(f"Char: {char} / Code: {ord(char)}")
        return found
