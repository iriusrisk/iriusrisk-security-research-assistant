"""This file provides tests where we need to check every component of every library"""
import unittest
import pytest
import os
from pathlib import Path
from lxml import etree

from isra.src.config.config import get_property
from isra.src.config.constants import get_app_dir
from isra.src.tests.integrity_tests_all_libraries import *


class TestAllLibraries(unittest.TestCase):
    """This class initializes by retrieving all weaknesses, controls and the folder path"""
    roots = dict()
    libraries = list()
    libraries_ok = True
    path = None
    maxDiff = None

    @classmethod
    def setUpClass(cls):
        libraries_dir = Path(get_property("libraries_dir") or get_app_dir())
        print(f"\nLibraries directory: {libraries_dir}")

        cls.path = libraries_dir
        cls.libraries = []
        cls.roots = {}

        def collect_xml_files(base_dir: Path):
            if not base_dir.exists():
                return []
            return [p for p in base_dir.iterdir() if p.suffix == ".xml"]

        for version in ("v1", "v2"):
            version_path = libraries_dir / version
            cls.libraries.extend(collect_xml_files(version_path))

        for lib in cls.libraries:
            cls.roots[lib] = etree.parse(str(lib))

    def setUp(self):
        if not self.__class__.libraries_ok and self._testMethodName != "test_00_libraries_present":
            self.skipTest("No libraries found; skipping remaining tests in this class.")

    def test_00_libraries_present(self):
        """Check that there is at least one library to test"""
        print(f"Number of libraries: {len(self.libraries)}")
        if len(self.libraries) == 0:
            self.__class__.libraries_ok = False
            self.fail("Expected at least one library to be present.")

    def test_duplicated_components(self):
        """Check that there are no duplicated risk patterns"""
        errors = checkDuplicatedComponentsFromLibrary(self.path)
        self.assertCountEqual(errors, [])

    @pytest.mark.skip(reason="not needed anymore")
    def test_duplicated_threats_different_data(self):
        """Check if a weakness is duplicated in another threat but with different data"""
        errors = checkDuplicatedThreatsWithDifferentData(self.roots)
        self.assertCountEqual(errors, [])

    @pytest.mark.skip(reason="not needed anymore")
    def test_duplicated_weaknesses_different_data(self):
        """Check if a weakness is duplicated in another threat but with different data"""
        errors = checkDuplicatedWeaknessesWithDifferentData(self.roots)
        self.assertCountEqual(errors, [])

    @pytest.mark.skip(reason="not needed anymore")
    def test_duplicated_controls_different_data(self):
        """Check if a weakness is duplicated in another threat but with different data"""
        errors = checkDuplicatedControlsWithDifferentData(self.roots)
        self.assertCountEqual(errors, [])

    @pytest.mark.skip(reason="Deprecated test")
    def test_check_ascii(self):
        """Check that the countermeasure descriptions don't have non-ASCII characters"""
        errors = checkAscii(self.roots)
        self.assertCountEqual(errors, [])

    @pytest.mark.skip(reason="Deprecated test")
    def test_check_inconsistent_control_names(self):
        """Check that countermeasures with the same ref also have the same name"""
        errors = checkInconsistentControlNames(self.roots)
        self.assertCountEqual(errors, [])

    def test_duplicated_risk_pattern_refs(self):
        """Check that a risk pattern ref cannot be duplicated"""
        errors = checkDuplicatedRiskPatternRefs(self.roots)
        self.assertCountEqual(errors, [])

    def test_check_incorrect_library_ref_on_rule(self):
        """Check that the library referenced in a rule is correct and that the risk pattern exists in that library"""
        errors = checkIncorrectLibraryRefOnRule(self.roots)
        self.assertCountEqual(errors, [])

    def test_check_disabled_libraries_are_disabled(self):
        """Check that there is no component missing in the libraries and that those new are listed"""
        disabled = []
        errors = checkDisabledLibrariesAreDisabled(self.roots, disabled)
        self.assertCountEqual(errors, [])

    def test_check_duplicated_rules(self):
        """Check that there is no component missing in the libraries and that those new are listed"""
        disabled = []
        errors = checkDuplicatedRules(self.roots, disabled)
        self.assertCountEqual(errors, [])

    def test_check_placeholder_components_are_disabled(self):
        """Check that there is no component missing in the libraries and that those new are listed"""
        disabled = []
        errors = checkPlaceholderComponentsAreDisabled(self.roots, disabled)
        self.assertCountEqual(errors, [])

    def test_check_rule_references_are_not_broken(self):
        """Check that there is no component missing in the libraries and that those new are listed"""
        disabled = []
        errors = checkRuleReferencesAreNotBroken(self.roots, disabled)
        self.assertCountEqual(errors, [])

    @pytest.mark.skip(reason="element refs and names pending to be fixed in the future")
    def test_check_inconsistent_threat_names(self):
        """Check that the threats and weaknesses with the same ref don't have different names"""
        errors = checkInconsistentThreatNames(self.roots)
        self.assertCountEqual(errors, [])

    @pytest.mark.skip(reason="element refs and names pending to be fixed in the future")
    def test_check_inconsistent_weakness_names(self):
        """Check that the threats and weaknesses with the same ref don't have different names"""
        errors = checkInconsistentWeaknessNames(self.roots)
        self.assertCountEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
