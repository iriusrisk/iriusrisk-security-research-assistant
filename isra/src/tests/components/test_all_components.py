"""This file provides tests to verify the integrity of the YAML file components"""
import os
import unittest
from pathlib import Path

from isra.src.config.config import get_property
from isra.src.config.constants import get_app_dir
from isra.src.tests.integrity_tests_all_components import *


class TestAllComponents(unittest.TestCase):
    maxDiff = None
    components = []
    roots = dict()
    components_dir = None
    components_ok = True

    @classmethod
    def setUpClass(cls):
        components_dir = os.getenv("ISRA_COMPONENTS_DIR") or get_property("components_dir") or get_app_dir()
        cls.components_dir = components_dir
        cls.path = Path(components_dir)
        cls.components = list()
        for root, dirs, files in os.walk(components_dir):
            for file in files:
                if file.endswith(".yaml") and "to_review" not in root and ".git" not in root:
                    cls.components.append(os.path.join(root, file))
        cls.roots = dict()
        for x in cls.components:
            cls.roots[x] = read_yaml(x)

    def setUp(self):
        if not self.__class__.components_ok and self._testMethodName != "test_00_multiple_components_detected":
            self.skipTest("Component count precheck failed; skipping remaining tests in this class.")

    def test_00_multiple_components_detected(self):
        """Check that there is more than one YAML component to test."""
        print(f"\nComponents directory: {self.components_dir}")
        print(f"Number of YAML components: {len(self.components)}")
        if len(self.components) <= 1:
            self.__class__.components_ok = False
            self.fail("Expected more than one YAML component in the detected components directory.")

    def test_duplicated_components(self):
        """Check that there are no duplicated components"""
        errors = check_duplicated_components(self.roots)
        self.assertCountEqual(errors, [])

    def test_duplicated_risk_pattern_refs(self):
        """Check that a risk pattern ref cannot be duplicated"""
        errors = check_duplicated_risk_pattern_refs(self.roots)
        self.assertCountEqual(errors, [])

    def test_duplicated_risk_pattern_names(self):
        """Check that a risk pattern ref cannot be duplicated"""
        errors = check_duplicated_risk_pattern_names(self.roots)
        self.assertCountEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
