"""This file provides tests for every individual library"""
import os
import unittest
from pathlib import Path

import pytest
from lxml import etree

from isra.src.config.config import get_property
from isra.src.config.constants import get_app_dir
from isra.src.tests.integrity_tests_library import *


class TestLibrary(unittest.TestCase):
    """This class initializes by retrieving all libraries in the /libraries folder. Then it checks every test for every library detected"""
    roots = None
    path = None
    libraries = None
    maxDiff = None

    @classmethod
    def setUpClass(cls):
        libraries_dir = Path(get_property("libraries_dir") or get_app_dir())

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

    @pytest.mark.skip(reason="not needed anymore")
    def test_copyright(self):
        """Check if the library has the IriusRisk copyright comment under the first line"""
        for lib in self.libraries:
            with self.subTest(lib=lib):
                errors = checkCopyrightInAllLibraries(lib)
                self.assertCountEqual(errors, [])

    def test_check_CRLF(self):
        """Check that the line break of the library is always LF and not CRLF or CR"""
        for lib in self.libraries:
            with self.subTest(lib=lib):
                errors = checkCRLF(lib)
                self.assertCountEqual(errors, [])

    def test_xsd_schema(self):
        """Check if the library is consistent with the XSD schema"""
        filename_xsd = Path(__file__).parent.parent.parent / "ile" / "backend" / "app" / "resources" / "XSD_Schema" / "library.xsd"
        #filename_xsd = Path.cwd() / "inputFiles" / "XSD_Schema" / "library.xsd"
        for lib in self.libraries:
            with self.subTest(lib=lib):
                errors = xmlValidator(str(lib), str(filename_xsd))
                self.assertCountEqual(errors, [])

    def test_threat_mitigation(self):
        """Check that the mitigation values sum of a weakness's countermeasures is always between 100 and 140"""
        for lib in self.libraries:
            with self.subTest(lib=lib):
                errors = checkCorrectMitigationSum(self.roots[lib])
                self.assertCountEqual(errors, [])

    def test_duplicated_standards_per_control(self):
        """Check that there are no countermeasures with duplicated standards"""
        for lib in self.libraries:
            with self.subTest(lib=lib):
                errors = checkDuplicatedStandards(self.roots[lib])
                self.assertCountEqual(errors, [])

    def test_duplicated_references_per_control(self):
        """Check that there are no countermeasures with duplicated references"""
        for lib in self.libraries:
            with self.subTest(lib=lib):
                errors = checkDuplicatedReferences(self.roots[lib])
                self.assertCountEqual(errors, [])

    def test_duplicated_implementations_per_control(self):
        """Check that there are no countermeasures with duplicated implementations"""
        for lib in self.libraries:
            with self.subTest(lib=lib):
                errors = checkDuplicatedImplementations(self.roots[lib])
                self.assertCountEqual(errors, [])

    def test_integrity_category_components(self):
        """Check that there are no category components without empty ref or name"""
        for lib in self.libraries:
            with self.subTest(lib=lib):
                errors = checkIntegrityOfCategoryComponentsFromLibrary(self.roots[lib])
                self.assertCountEqual(errors, [])

    def test_duplicated_controls_per_component(self):
        """Check that there are no duplicated countermeasures in any risk pattern"""
        for lib in self.libraries:
            with self.subTest(lib=lib):
                errors = checkDuplicatedControlsPerComponentFromLibrary(self.roots[lib])
                self.assertCountEqual(errors, [])

    def test_duplicated_weaknesses_per_component(self):
        """Check that there are no duplicated weaknesses in any risk pattern"""
        for lib in self.libraries:
            with self.subTest(lib=lib):
                errors = checkDuplicatedWeaknessesPerComponentFromLibrary(self.roots[lib])
                self.assertCountEqual(errors, [])

    def test_duplicated_threats_per_component_and_usecase(self):
        """Check that there are no duplicated threats in any risk pattern"""
        for lib in self.libraries:
            with self.subTest(lib=lib):
                errors = checkDuplicatedThreatsPerUseCaseAndComponentFromLibrary(self.roots[lib])
                self.assertCountEqual(errors, [])

    def test_integrity_component_definitions(self):
        """Check that there are no component definitions without empty ref, name, categoryRef and that there aren't any reference to a non-existent risk pattern"""
        for lib in self.libraries:
            with self.subTest(lib=lib):
                errors = checkIntegrityOfComponentDefinitionsFromLibrary(self.roots[lib])
                self.assertCountEqual(errors, [])

    def test_recommended_countermeasures_by_default(self):
        """Check that every countermeasure has the state 'Recommended'"""
        for lib in self.libraries:
            with self.subTest(lib=lib):
                errors = checkIfAllCountermeasuresAreWithRecommendedStatus(self.roots[lib])
                self.assertCountEqual(errors, [])

    def test_unassigned_weakness_to_threat(self):
        """Check that a weakness cannot exist inside a risk pattern if it isn't referenced in a threat"""
        for lib in self.libraries:
            with self.subTest(lib=lib):
                errors = checkIfExistsUnassignedWeaknesses(self.roots[lib])
                self.assertCountEqual(errors, [])

    def test_unassigned_countermeasure(self):
        """Check that a countermeasure cannot exist inside a risk pattern if it isn't referenced in a threat"""
        for lib in self.libraries:
            with self.subTest(lib=lib):
                errors = checkIfExistsUnassignedCountermeasures(self.roots[lib])
                self.assertCountEqual(errors, [])

    def test_not_empty_standard_ref(self):
        """Check if a standard reference inside a countermeasure is empty"""
        for lib in self.libraries:
            with self.subTest(lib=lib):
                errors = checkIfStandardReferenceIsEmpty(self.roots[lib])
                self.assertCountEqual(errors, [])

    def test_check_empty_threat_description(self):
        """Check if a threat description is empty"""
        for lib in self.libraries:
            with self.subTest(lib=lib):
                errors = checkIfThreatDescriptionIsEmpty(self.roots[lib])
                self.assertCountEqual(errors, [])

    def test_check_incorrect_name_suffix(self):
        """Check that the names in the elements don't end with a character that is not a letter or a number"""
        for lib in self.libraries:
            with self.subTest(lib=lib):
                errors = checkIncorrectNameSuffix(self.roots[lib])
                self.assertCountEqual(errors, [])

    def test_check_missing_category_refs(self):
        """Check that the category components set always contain all risk patterns defined in the library"""
        for lib in self.libraries:
            with self.subTest(lib=lib):
                errors = checkMissingCategoryRefs(self.roots[lib])
                self.assertCountEqual(errors, [])

    def test_check_missing_supported_standards(self):
        """Check that the supported standards set always contain all standards defined in the countermeasures"""
        for lib in self.libraries:
            with self.subTest(lib=lib):
                errors = checkMissingSupportedStandards(self.roots[lib])
                self.assertCountEqual(errors, [])

    def test_check_whitespaces_in_reference_URLs(self):
        """Check that no reference in a risk pattern has a whitespace in its URLs"""
        for lib in self.libraries:
            with self.subTest(lib=lib):
                errors = checkWhitespacesInReferenceUrls(self.roots[lib])
                self.assertCountEqual(errors, [])

    def test_check_orphaned_controls(self):
        """Check that a countermeasure cannot exist under the threat node if it doesn't also appear under a weakness node"""
        for lib in self.libraries:
            with self.subTest(lib=lib):
                if lib.name in ["IR-Functional-Components.xml", "mitre-attack-framework.xml",
                                "IR-Machine-Learning-Artificial-Intelligence.xml"]:
                    pass
                else:
                    errors = checkOrphanedControls(self.roots[lib])
                    self.assertCountEqual(errors, [])

    def test_check_empty_weaknesses(self):
        """Check that there are no weakness without any countermeasure, except CWE-7-KINGDOMS"""
        for lib in self.libraries:
            with self.subTest(lib=lib):
                exceptions = ['CWE-7-KINGDOMS']
                errors = checkEmptyWeaknesses(self.roots[lib], exceptions)
                self.assertCountEqual(errors, [])

    @pytest.mark.skip(reason="element refs pending to be fixed in the future")
    def test_check_whitespaces_in_component_references(self):
        """Check that the element refs don't contain any whitespace"""
        for lib in self.libraries:
            with self.subTest(lib=lib):
                errors = checkWhitespacesInRefs(self.roots[lib])
                self.assertCountEqual(errors, [])

    def test_check_empty_control_description(self):
        """Check if a threat description is empty"""
        for lib in self.libraries:
            with self.subTest(lib=lib):
                errors = checkIfControlDescriptionIsEmpty(self.roots[lib])
                self.assertCountEqual(errors, [])

    def test_check_risk_rating_values_stride(self):
        """Check if the risk values are right according to the STRIDE catgory"""
        for lib in self.libraries:
            with self.subTest(lib=lib):
                errors = checkRiskRatingValuesStride(self.roots[lib])
                self.assertCountEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
