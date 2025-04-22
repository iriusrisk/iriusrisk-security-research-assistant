"""This file provides tests to verify the integrity of the YAML file components"""
import os
import unittest
from pathlib import Path

from isra.src.config.config import get_property, get_app_dir
from isra.src.tests.integrity_tests_component import *


class TestComponent(unittest.TestCase):
    maxDiff = None
    components = []
    roots = dict()

    @classmethod
    def setUpClass(cls):
        components_dir = get_property("components_dir") or get_app_dir()
        cls.path = Path(components_dir)
        cls.components = list()
        for root, dirs, files in os.walk(components_dir):
            for file in files:
                if file.endswith(".yaml") and "to_review" not in root and ".git" not in root:
                    cls.components.append(os.path.join(root, file))
        cls.roots = dict()
        for x in cls.components:
            cls.roots[x] = read_yaml(x)

    def test_yaml_schema(self):
        """Check if the YAML file component is consistent with the JSON schema"""
        for component in self.components:
            with self.subTest(component=component):
                errors = yaml_validator(component)
                self.assertCountEqual(errors, [])

    def test_duplicated_standards_sections_per_control(self):
        """Check that there are no countermeasures with duplicated standards"""
        for component in self.components:
            with self.subTest(component=component):
                errors = check_duplicated_standards_sections(self.roots[component])
                self.assertCountEqual(errors, [])

    def test_empty_standards_sections_per_control(self):
        """Check that there are no countermeasures with duplicated standards"""
        for component in self.components:
            with self.subTest(component=component):
                errors = check_empty_standard_sections(self.roots[component])
                self.assertCountEqual(errors, [])

    def test_duplicated_references(self):
        """Check that there are no elements with duplicated references"""
        for component in self.components:
            with self.subTest(component=component):
                errors = check_duplicated_references(self.roots[component])
                self.assertCountEqual(errors, [])

    def test_duplicated_taxonomies(self):
        """Check that there are no elements with duplicated references"""
        for component in self.components:
            with self.subTest(component=component):
                errors = check_duplicated_taxonomies(self.roots[component])
                self.assertCountEqual(errors, [])

    def test_check_whitespaces_in_reference_URLs(self):
        """Check that no references with a whitespace in its URLs"""
        for component in self.components:
            with self.subTest(component=component):
                errors = check_whitespaces_in_reference_urls(self.roots[component])
                self.assertCountEqual(errors, [])

    def test_duplicated_controls_per_threat(self):
        """Check that there are no duplicated countermeasures in any threat"""
        for component in self.components:
            with self.subTest(component=component):
                errors = check_duplicated_controls_per_threat(self.roots[component])
                self.assertCountEqual(errors, [])

    def test_duplicated_threats_per_component(self):
        """Check that there are no duplicated threats in any risk pattern"""
        for component in self.components:
            with self.subTest(component=component):
                errors = check_duplicated_threats_per_risk_pattern(self.roots[component])
                self.assertCountEqual(errors, [])

    def test_empty_threat_descriptions(self):
        """Check that there are no threats with empty descriptions"""
        for component in self.components:
            with self.subTest(component=component):
                errors = check_empty_threat_descriptions(self.roots[component])
                self.assertCountEqual(errors, [])

    def test_empty_countermeasure_descriptions(self):
        """Check that there are no countermeasures with empty descriptions"""
        for component in self.components:
            with self.subTest(component=component):
                errors = check_empty_countermeasure_descriptions(self.roots[component])
                self.assertCountEqual(errors, [])

    def test_empty_countermeasure_baseline_standards(self):
        """Check that there are no countermeasures with empty baseline_standards"""
        for component in self.components:
            with self.subTest(component=component):
                errors = check_empty_countermeasure_base_standards(self.roots[component])
                self.assertCountEqual(errors, [])

    def test_empty_countermeasure_cwe_impact(self):
        """Check that there are no countermeasures with empty baseline_standards"""
        for component in self.components:
            with self.subTest(component=component):
                errors = check_empty_countermeasure_cwe_impact(self.roots[component])
                self.assertCountEqual(errors, [])

    def test_problematic_characters_in_questions(self):
        """Check that there are no countermeasures with empty descriptions"""
        for component in self.components:
            with self.subTest(component=component):
                errors = check_problematic_characters_in_questions(self.roots[component])
                self.assertCountEqual(errors, [])

    def test_countermeasure_without_question(self):
        """Check that there are no countermeasures with empty descriptions"""
        for component in self.components:
            with self.subTest(component=component):
                errors = check_countermeasure_without_question(self.roots[component])
                self.assertCountEqual(errors, [])

    def test_inconsistent_stride_values(self):
        for component in self.components:
            with self.subTest(component=component):
                errors = check_inconsistent_stride_values(self.roots[component])
                self.assertCountEqual(errors, [])

    def test_trailing_whitespaces(self):
        for component in self.components:
            with self.subTest(component=component):
                errors = check_trailing_whitespaces(self.roots[component])
                self.assertCountEqual(errors, [])

    def test_name_does_not_contain_category(self):
        for component in self.components:
            with self.subTest(component=component):
                errors = check_name_does_not_contain_category(self.roots[component])
                self.assertCountEqual(errors, [])

    def test_custom_fields_are_valid(self):
        for component in self.components:
            with self.subTest(component=component):
                errors = check_custom_fields_are_valid(self.roots[component])
                self.assertCountEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
