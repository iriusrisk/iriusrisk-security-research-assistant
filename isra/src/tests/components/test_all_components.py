"""This file provides tests to verify the integrity of the YAML file components"""
import os
import unittest
from pathlib import Path

from isra.src.config.config import get_property, get_app_dir
from isra.src.tests.integrity_tests_all_components import *


class TestAllComponents(unittest.TestCase):
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
