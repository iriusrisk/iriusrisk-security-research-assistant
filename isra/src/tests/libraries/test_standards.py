"""This file provides tests for all libraries"""
import unittest
from pathlib import Path

from isra.src.config.config import get_property
from isra.src.config.constants import get_app_dir
from isra.src.tests.integrity_tests_standards import *


class TestStandards(unittest.TestCase):
    """This class initializes by retrieving all standards"""
    maxDiff = None

    @classmethod
    def setUpClass(cls):
        libraries_dir = get_property("libraries_dir") or get_app_dir()
        libraries_path = Path(libraries_dir)
        cls.standards = getStandardsFromCountermeasures(libraries_path)

    # def test_standard_asvs_v4_level_1(self):
    #     """Check that the libraries have the standard references for ASVS3 Level 1"""
    #     asvs4ListLevel1 = ['2.1.1', '2.1.10', '2.1.11', '2.1.12', '2.1.2', '2.1.3', '2.1.4', '2.1.5', '2.1.6', '2.1.7',
    #                        '2.1.8', '2.1.9', '2.2.1', '2.2.2', '2.2.3', '2.3.1', '2.5.1', '2.5.2', '2.5.3', '2.5.4',
    #                        '2.5.5', '2.5.6', '2.7.1', '2.7.2', '2.7.3', '2.7.4', '2.8.1',
    #                        '3.1.1', '3.2.1', '3.2.2', '3.2.3', '3.3.1', '3.3.2', '3.4.1', '3.4.2', '3.4.3', '3.4.4',
    #                        '3.4.5', '3.7.1',
    #                        '4.1.1', '4.1.2', '4.1.3', '4.1.5', '4.2.1', '4.2.2', '4.3.1', '4.3.2',
    #                        '5.1.1', '5.1.2', '5.1.3', '5.1.4', '5.1.5', '5.2.1', '5.2.2', '5.2.3', '5.2.4', '5.2.5',
    #                        '5.2.6', '5.2.7', '5.2.8', '5.3.1', '5.3.10', '5.3.2', '5.3.3', '5.3.4', '5.3.5', '5.3.6',
    #                        '5.3.7', '5.3.8', '5.3.9', '5.5.1', '5.5.2', '5.5.3', '5.5.4',
    #                        '6.2.1',
    #                        '7.1.1', '7.1.2', '7.4.1',
    #                        '8.2.1', '8.2.2', '8.2.3', '8.3.1', '8.3.2', '8.3.3', '8.3.4',
    #                        '9.1.1', '9.1.2', '9.1.3',
    #                        '10.3.1', '10.3.2', '10.3.3',
    #                        '11.1.1', '11.1.2', '11.1.3', '11.1.4', '11.1.5',
    #                        '12.1.1', '12.3.1', '12.3.2', '12.3.3', '12.3.4', '12.3.5', '12.4.1', '12.4.2', '12.5.1',
    #                        '12.5.2', '12.6.1',
    #                        '13.1.1', '13.1.3', '13.2.1', '13.2.2', '13.2.3', '13.3.1',
    #                        '14.2.1', '14.2.2', '14.2.3', '14.3.2', '14.3.3', '14.4.1', '14.4.2', '14.4.3',
    #                        '14.4.4', '14.4.5', '14.4.6', '14.4.7', '14.5.1', '14.5.2', '14.5.3'
    #                        ]
    #     errors = findStandardReference('owasp-asvs4-level-1', asvs4ListLevel1, self.standards)
    #     self.assertEqual(errors, "")
    #
    # def test_standard_asvs_v4_level_2(self):
    #     """Check that the libraries have the standard references for ASVS4 Level 2"""
    #     asvs4ListLevel2 = ['1.11.2', '1.12.2', '1.14.1', '1.14.2', '1.14.3', '1.14.4', '1.14.5', '1.14.6',
    #                        '1.2.1', '1.2.2', '1.2.3', '1.2.4', '1.4.1', '1.4.4', '1.4.5', '1.5.2',
    #                        '1.5.3', '1.5.4', '1.6.2', '1.7.1', '1.7.2', '1.9.1', '1.9.2',
    #                        '2.1.1', '2.1.10', '2.1.11', '2.1.12', '2.1.2', '2.1.3', '2.1.4', '2.1.5', '2.1.6', '2.1.7',
    #                        '2.1.8', '2.1.9', '2.10.1', '2.10.2', '2.10.3', '2.10.4', '2.2.1', '2.2.2', '2.2.3', '2.3.1',
    #                        '2.3.2', '2.3.3', '2.4.1', '2.4.2', '2.4.3', '2.4.4', '2.4.5', '2.5.1', '2.5.2', '2.5.3',
    #                        '2.5.4', '2.5.5', '2.5.6', '2.5.7', '2.6.1', '2.6.2', '2.6.3', '2.7.1', '2.7.2', '2.7.3',
    #                        '2.7.4', '2.7.5', '2.7.6', '2.8.1', '2.8.2', '2.8.3', '2.8.4', '2.8.5', '2.8.6', '2.8.7',
    #                        '2.9.1', '2.9.2', '2.9.3',
    #                        '3.1.1', '3.2.1', '3.2.2', '3.2.3', '3.2.4', '3.3.1', '3.3.2', '3.3.3', '3.3.4', '3.4.1',
    #                        '3.4.2', '3.4.3', '3.4.4', '3.4.5',
    #                        '3.5.1', '3.5.2', '3.5.3', '3.7.1',
    #                        '4.1.1', '4.1.2', '4.1.3', '4.1.5', '4.2.1', '4.2.2', '4.3.1', '4.3.2', '4.3.3',
    #                        '5.1.1', '5.1.2', '5.1.3', '5.1.4', '5.1.5', '5.2.1', '5.2.2', '5.2.3', '5.2.4', '5.2.5',
    #                        '5.2.6', '5.2.7', '5.2.8', '5.3.1', '5.3.10', '5.3.2', '5.3.3',
    #                        '5.3.4', '5.3.5', '5.3.6', '5.3.7', '5.3.8', '5.3.9', '5.4.1', '5.4.2', '5.4.3', '5.5.1',
    #                        '5.5.2', '5.5.3', '5.5.4',
    #                        '6.1.1', '6.1.2', '6.1.3', '6.2.1', '6.2.2', '6.2.3', '6.2.4', '6.2.5', '6.2.6', '6.3.1',
    #                        '6.3.2', '6.4.1', '6.4.2',
    #                        '7.1.1', '7.1.2', '7.1.3', '7.1.4', '7.2.1', '7.2.2', '7.3.1', '7.3.3', '7.3.4',
    #                        '7.4.1', '7.4.2', '7.4.3',
    #                        '8.1.1', '8.1.2', '8.1.3', '8.1.4', '8.2.1', '8.2.2', '8.2.3', '8.3.1', '8.3.2', '8.3.3',
    #                        '8.3.4', '8.3.5', '8.3.6', '8.3.7', '8.3.8',
    #                        '9.1.1', '9.1.2', '9.1.3', '9.2.1', '9.2.2', '9.2.3', '9.2.4',
    #                        '10.2.1', '10.2.2', '10.3.1', '10.3.2', '10.3.3',
    #                        '11.1.1', '11.1.2', '11.1.3', '11.1.4', '11.1.5', '11.1.6', '11.1.7', '11.1.8',
    #                        '12.1.1', '12.1.2', '12.1.3', '12.2.1', '12.3.1', '12.3.2', '12.3.3', '12.3.4', '12.3.5',
    #                        '12.3.6', '12.4.1', '12.4.2', '12.5.1', '12.5.2', '12.6.1',
    #                        '13.1.1', '13.1.3', '13.1.4', '13.1.5', '13.2.1', '13.2.2', '13.2.3',
    #                        '13.2.5', '13.2.6', '13.3.1', '13.3.2', '13.4.1', '13.4.2',
    #                        '14.1.2', '14.1.3', '14.2.1', '14.2.2', '14.2.3', '14.2.4', '14.2.5', '14.2.6',
    #                        '14.3.2', '14.3.3', '14.4.1', '14.4.2', '14.4.3', '14.4.4', '14.4.5', '14.4.6', '14.4.7',
    #                        '14.5.1', '14.5.2', '14.5.3', '14.5.4'
    #                        ]
    #     errors = findStandardReference('owasp-asvs4-level-2', asvs4ListLevel2, self.standards)
    #     self.assertEqual(errors, "")
    #
    # def test_standard_asvs_v4_level_3(self):
    #     """Check that the libraries have the standard references for ASVS3 Level 3"""
    #     asvs4ListLevel3 = ['1.11.2', '1.11.3', '1.12.2', '1.14.1', '1.14.2', '1.14.3', '1.14.4', '1.14.5',
    #                        '1.14.6', '1.2.1', '1.2.2', '1.2.3', '1.2.4', '1.4.1', '1.4.4', '1.4.5',
    #                        '1.5.2', '1.5.3', '1.5.4', '1.6.2', '1.7.1', '1.7.2', '1.9.1', '1.9.2',
    #                        '2.1.1', '2.1.10', '2.1.11', '2.1.12', '2.1.2', '2.1.3', '2.1.4', '2.1.5', '2.1.6', '2.1.7',
    #                        '2.1.8', '2.1.9', '2.10.1', '2.10.2', '2.10.3', '2.10.4', '2.2.1', '2.2.2', '2.2.3', '2.2.4',
    #                        '2.2.5', '2.2.6', '2.2.7', '2.3.1', '2.3.2', '2.3.3', '2.4.1', '2.4.2', '2.4.3', '2.4.4',
    #                        '2.4.5', '2.5.1', '2.5.2', '2.5.3', '2.5.4', '2.5.5', '2.5.6', '2.5.7', '2.6.1', '2.6.2',
    #                        '2.6.3', '2.7.1', '2.7.2', '2.7.3', '2.7.4', '2.7.5', '2.7.6', '2.8.1', '2.8.2', '2.8.3',
    #                        '2.8.4', '2.8.5', '2.8.6', '2.8.7', '2.9.1', '2.9.2', '2.9.3',
    #                        '3.1.1', '3.2.1', '3.2.2', '3.2.3', '3.2.4', '3.3.1', '3.3.2', '3.3.3', '3.3.4', '3.4.1',
    #                        '3.4.2', '3.4.3', '3.4.4', '3.4.5',
    #                        '3.5.1', '3.5.2', '3.5.3', '3.6.1', '3.6.2', '3.7.1',
    #                        '4.1.1', '4.1.2', '4.1.3', '4.1.5', '4.2.1', '4.2.2', '4.3.1', '4.3.2', '4.3.3',
    #                        '5.1.1', '5.1.2', '5.1.3', '5.1.4', '5.1.5', '5.2.1', '5.2.2', '5.2.3', '5.2.4', '5.2.5',
    #                        '5.2.6', '5.2.7', '5.2.8', '5.3.1', '5.3.10', '5.3.2', '5.3.3',
    #                        '5.3.4', '5.3.5', '5.3.6', '5.3.7', '5.3.8', '5.3.9', '5.4.1', '5.4.2', '5.4.3', '5.5.1',
    #                        '5.5.2', '5.5.3', '5.5.4',
    #                        '6.1.1', '6.1.2', '6.1.3', '6.2.1', '6.2.2', '6.2.3', '6.2.4', '6.2.5', '6.2.6', '6.2.7',
    #                        '6.2.8', '6.3.1', '6.3.2', '6.3.3', '6.4.1', '6.4.2',
    #                        '7.1.1', '7.1.2', '7.1.3', '7.1.4', '7.2.1', '7.2.2', '7.3.1', '7.3.3', '7.3.4',
    #                        '7.4.1', '7.4.2', '7.4.3',
    #                        '8.1.1', '8.1.2', '8.1.3', '8.1.4', '8.1.5', '8.1.6', '8.2.1', '8.2.2', '8.2.3', '8.3.1',
    #                        '8.3.2', '8.3.3', '8.3.4', '8.3.5', '8.3.6', '8.3.7', '8.3.8',
    #                        '9.1.1', '9.1.2', '9.1.3', '9.2.1', '9.2.2', '9.2.3', '9.2.4', '9.2.5',
    #                        '10.1.1', '10.2.1', '10.2.2', '10.2.3', '10.2.4', '10.2.5', '10.2.6', '10.3.1', '10.3.2',
    #                        '10.3.3',
    #                        '11.1.1', '11.1.2', '11.1.3', '11.1.4', '11.1.5', '11.1.6', '11.1.7', '11.1.8',
    #                        '12.1.1', '12.1.2', '12.1.3', '12.2.1', '12.3.1', '12.3.2', '12.3.3', '12.3.4', '12.3.5',
    #                        '12.3.6', '12.4.1', '12.4.2', '12.5.1', '12.5.2', '12.6.1',
    #                        '13.1.1', '13.1.3', '13.1.4', '13.1.5', '13.2.1', '13.2.2', '13.2.3',
    #                        '13.2.5', '13.2.6', '13.3.1', '13.3.2', '13.4.1', '13.4.2',
    #                        '14.1.2', '14.1.3', '14.1.5', '14.2.1', '14.2.2', '14.2.3', '14.2.4', '14.2.5', '14.2.6',
    #                        '14.3.2', '14.3.3', '14.4.1', '14.4.2', '14.4.3', '14.4.4', '14.4.5', '14.4.6',
    #                        '14.4.7', '14.5.1', '14.5.2', '14.5.3', '14.5.4'
    #                        ]
    #     errors = findStandardReference('owasp-asvs4-level-3', asvs4ListLevel3, self.standards)
    #     self.assertEqual(errors, "")
    #
    # def test_standard_owasp_api_security_top_10(self):
    #     """Check that the libraries have the standard references for OWASP API Security Top 10"""
    #     owaspApiTop10 = ['API1:2023-Broken Object Level Authorization',
    #                      'API2:2023-Broken Authentication',
    #                      'API3:2023-Broken Object Property Level Authorization',
    #                      'API4:2023-Lack of Resources and Rate Limiting',
    #                      'API5:2023-Broken Function Level Authorization',
    #                      'API6:2023-Unrestricted Access to Sensitive Business Flows',
    #                      'API7:2023-Server Side Request Forgery',
    #                      'API8:2023-Security Misconfiguration',
    #                      'API9:2023-Improper Inventory Management',
    #                      'API10:2023-Unsafe Consumption of APIs']
    #     errors = findStandardReference('owasp-api-security-top-10', owaspApiTop10, self.standards)
    #     self.assertEqual(errors, "")
    #
    # def test_standard_nist_800_63(self):
    #     """Check that the libraries have the standard references for NIST 800-63"""
    #     nist_800_63 = ['5.1.1.1', '5.1.1.2', '5.1.2.2', '5.1.3.2', '5.1.4.2', '5.1.5.2', '5.1.7.2', '5.2.1', '5.2.10',
    #                    '5.2.2', '5.2.3', '5.2.5', '5.2.6', '5.2.8', '5.2.9', '6.1.2.3', '6.1.3', '6.1.4', '7.1',
    #                    '7.1.1', '7.1.2', '7.2', '7.2.1', 'A.3']
    #     errors = findStandardReference('nist-800-63', nist_800_63, self.standards)
    #     self.assertEqual(errors, "")
    #
    # def test_standard_docker_cis_level1(self):
    #     """Check that the libraries have the standard references for Docker CIS Level 1"""
    #     dockerLevel1List = ['2.1', '2.13', '2.14', '2.15', '2.17', '2.18', '2.2', '2.3', '2.4', '2.5', '2.6', '2.7',
    #                         '3.1', '3.10', '3.11', '3.12', '3.13', '3.14', '3.15', '3.16', '3.17', '3.18', '3.19',
    #                         '3.2', '3.20', '3.3', '3.4', '3.5', '3.6', '3.7', '3.8', '3.9', '4.1', '4.10', '4.2', '4.3',
    #                         '4.4', '4.6', '4.7', '4.9', '5.1', '5.10', '5.11', '5.12', '5.13', '5.14', '5.15', '5.16',
    #                         '5.17', '5.18', '5.19', '5.20', '5.21', '5.24', '5.25', '5.26', '5.27', '5.28', '5.3',
    #                         '5.30', '5.31', '5.4', '5.5', '5.6', '5.7', '5.8', '5.9', '7.1', '7.2', '7.3', '7.4', '7.6',
    #                         '7.7']
    #     errors = findStandardReference('Level 1 - Docker', dockerLevel1List, self.standards)
    #     self.assertEqual(errors, "")
    #
    # def test_standard_docker_cis_level2(self):
    #     """Check that the libraries have the standard references for Docker CIS Level 2"""
    #     dockerLevel2List = ['2.1', '2.10', '2.11', '2.12', '2.13', '2.14', '2.15', '2.16', '2.17', '2.18', '2.2', '2.3',
    #                         '2.4', '2.5', '2.6', '2.7', '2.8', '2.9', '3.1', '3.10', '3.11', '3.12', '3.13', '3.14',
    #                         '3.15', '3.16', '3.17', '3.18', '3.19', '3.2', '3.20', '3.3', '3.4', '3.5', '3.6', '3.7',
    #                         '3.8', '3.9', '4.1', '4.10', '4.11', '4.2', '4.3', '4.4', '4.5', '4.6', '4.7', '4.8', '4.9',
    #                         '5.1', '5.10', '5.11', '5.12', '5.13', '5.14', '5.15', '5.16', '5.17', '5.18', '5.19',
    #                         '5.2', '5.20', '5.21', '5.22', '5.23', '5.24', '5.25', '5.26', '5.27', '5.28', '5.29',
    #                         '5.3', '5.30', '5.31', '5.4', '5.5', '5.6', '5.7', '5.8', '5.9', '7.1', '7.10', '7.2',
    #                         '7.3', '7.4', '7.5', '7.6', '7.7', '7.8', '7.9']
    #     errors = findStandardReference('Level 2 - Docker', dockerLevel2List, self.standards)
    #     self.assertEqual(errors, "")
    #
    # def test_standard_docker_cis_linux_level1(self):
    #     """Check that the libraries have the standard references for Docker CIS Linux Level 1"""
    #     dockerLinuxLevel1List = ["1.1", "1.2", "1.3", "1.4", "1.5", "1.6", "1.7", "1.8", "1.9", "1.10", "1.11", "1.12",
    #                              "1.13", "6.1", "6.2"]
    #     errors = findStandardReference('Level 1 - Linux Host OS', dockerLinuxLevel1List, self.standards)
    #     self.assertEqual(errors, "")
    #
    # def test_standard_iso_27002(self):
    #     """Check that the libraries have the standard references for ISO 27002"""
    #     iso27002list = ["6.2.1", "9.1.1", "9.2.2", "9.2.3", "9.2.4", "9.3.1", "9.4.1", "9.4.2", "9.4.3", "9.4.4",
    #                     "9.4.5",
    #                     "10.1.1", "10.1.2", "12.1.2", "12.2.1", "12.3.1", "12.4.1", "12.4.2", "12.4.4", "12.5.1",
    #                     "12.6.1",
    #                     "13.1.1", "13.2.1"]
    #     errors = findStandardReference('ISO/IEC 27002:2013', iso27002list, self.standards)
    #     self.assertEqual(errors, "")
    #
    # def test_standard_nist_800_53(self):
    #     """Check that the libraries have the standard references for NIST 800-53"""
    #     nist800_53list = ["AC-2", "AC-3", "AC-4", "AC-5", "AC-6", "AC-7", "AC-8", "AC-10", "AC-12",
    #
    #                       "AC-17", "AC-18", "AC-19", "AC-20", "AC-22", "AC-23", 'AU-1',
    #                       "AU-2", "AU-3", "AU-4", 'AU-5',
    #                       'AU-6', 'AU-7', "AU-8", "AU-9", "AU-10", "AU-11", "AU-12", "AU-13", "AU-14", "CA-7",
    #                       'IA-2', 'IA-4', 'IA-5', 'IA-6',
    #                       'IA-7',
    #                       "IA-11", 'SC-2',
    #                       'SC-4',
    #                       'SC-5', 'SC-6', 'SC-7', "SC-8", 'SC-10', "SC-13", 'SC-15', 'SC-18',
    #                       'SC-20', 'SC-21', 'SC-22', 'SC-23', 'SC-24', "SC-28", 'SC-39',
    #
    #                       "SI-2", "SI-5", "SI-7", "SI-8", "SI-10", "SI-11",
    #                       "SI-15", "SI-16", "SI-17", "SI-21"]
    #     errors = findStandardReference('NIST 800-53', nist800_53list, self.standards)
    #     self.assertEqual(errors, "")
    #
    # def test_standard_aws_cis_standard_level_1(self):
    #     """Check that the libraries have the standard references for AWS CIS Standard"""
    #     cisAwsStandard = ['1.1', '1.10', '1.11', '1.12', '1.13', '1.14', '1.15', '1.16', '1.17', '1.19', '1.2', '1.20',
    #                       '1.3', '1.4', '1.5', '1.7', '1.8', '1.9', '2.1.3', '2.1.5', '2.2.1', '2.3.1', '2.3.2',
    #                       '2.3.3', '2.4.1', '3.1', '3.3',
    #                       '3.4', '3.6', '4.1', '4.12', '4.13', '4.14', '4.15', '4.2', '4.3', '4.4', '4.5', '4.8', '5.1',
    #                       '5.2']
    #     errors = findStandardReference('CIS AWS Standard', cisAwsStandard, self.standards)
    #     self.assertEqual(errors, "")
    #
    # def test_standard_aws_cis_standard_level_2(self):
    #     """Check that the libraries have the standard references for AWS CIS Standard"""
    #     cisAwsStandard = ['1.1', '1.10', '1.11', '1.12', '1.13', '1.14', '1.15', '1.16', '1.17', '1.18', '1.19', '1.2',
    #                       '1.20', '1.21', '1.3', '1.4', '1.5', '1.6', '1.7', '1.8', '1.9', '2.1.1', '2.1.2', '2.1.3',
    #                       '2.1.4', '2.1.5', '2.2.1', '2.3.1', '2.3.2', '2.3.3', '2.4.1', '3.1', '3.10', '3.11', '3.2',
    #                       '3.3', '3.4', '3.5', '3.6',
    #                       '3.7', '3.8', '3.9', '4.1', '4.10', '4.11', '4.12', '4.13', '4.14', '4.15', '4.16', '4.2',
    #                       '4.3',
    #                       '4.4', '4.5', '4.6', '4.7', '4.8', '4.9', '5.1', '5.2', '5.3', '5.4']
    #     errors = findStandardReference('CIS-AWS-Standard-Level-2', cisAwsStandard, self.standards)
    #     self.assertEqual(errors, "")
    #
    # def test_standard_aws_cis_three_tier_standard_level_1(self):
    #     """Check that the libraries have the standard references for AWS CIS Three Tier Standard"""
    #     cisAwsTierStandard = ['1.10', '1.16', '1.4', '1.5', '1.6', '1.7', '1.8', '1.9', '2.1', '2.10', '2.2', '2.3',
    #                           '2.4', '2.5', '2.6', '2.7', '2.8', '2.9', '3.1', '3.10', '3.11', '3.14', '3.15', '3.2',
    #                           '3.3', '3.4', '3.5', '3.6', '3.8', '3.9', '4.1', '4.2', '4.3', '4.4', '4.6', '4.7', '4.8',
    #                           '5.1', '5.10', '5.11', '5.12', '5.2', '5.3', '5.4', '5.5', '5.6', '5.7', '5.8', '5.9',
    #                           '6.10', '6.11', '6.12', '6.13', '6.14', '6.15', '6.16', '6.17', '6.18', '6.19', '6.20',
    #                           '6.21', '6.22', '6.23', '6.24', '6.25', '6.26', '6.27', '6.28', '6.29', '6.3', '6.32',
    #                           '6.33', '6.34', '6.5', '6.6', '6.7', '6.8', '6.9']
    #     errors = findStandardReference('cis-amazon-web-services-three-tier-web-architecture-benchmark',
    #                                    cisAwsTierStandard, self.standards)
    #     self.assertEqual(errors, "")
    #
    # def test_standard_aws_cis_three_tier_standard_level_2(self):
    #     """Check that the libraries have the standard references for AWS CIS Three Tier Standard"""
    #     cisAwsTierStandard = ['1.1', '1.10', '1.11', '1.12', '1.13', '1.14', '1.15', '1.16', '1.17', '1.2', '1.3',
    #                           '1.4', '1.5', '1.6', '1.7', '1.8', '1.9', '2.1', '2.10', '2.2', '2.3', '2.4', '2.5',
    #                           '2.6', '2.7', '2.8', '2.9', '3.1', '3.10', '3.11', '3.12', '3.13', '3.14', '3.15', '3.2',
    #                           '3.3', '3.4', '3.5', '3.6', '3.8', '3.9', '4.1', '4.2', '4.3', '4.4', '4.6', '4.7', '4.8',
    #                           '5.1', '5.10', '5.11', '5.12', '5.2', '5.3', '5.4', '5.5', '5.6', '5.7', '5.8', '5.9',
    #                           '6.1', '6.10', '6.11', '6.12', '6.13', '6.14', '6.15', '6.16', '6.17', '6.18', '6.19',
    #                           '6.2', '6.20', '6.21', '6.22', '6.23', '6.24', '6.25', '6.26', '6.27', '6.28', '6.29',
    #                           '6.3', '6.30', '6.31', '6.32', '6.33', '6.34', '6.4', '6.5', '6.6', '6.7', '6.8', '6.9']
    #     errors = findStandardReference('cis-amazon-web-services-three-tier-web-architecture-benchmark-level-2',
    #                                    cisAwsTierStandard, self.standards)
    #     self.assertEqual(errors, "")
    #
    # def test_standard_eu_gdpr_standard(self):
    #     """Check that the libraries have the standard references for EU GDPR"""
    #     euGdprStandard = ['Art.6', 'Art.7', 'Art.12', 'Art.13', 'Art.14', 'Art.15', 'Art.17', 'Art.20', 'Art.21',
    #                       'Art.22', 'Art.30', 'Art.32', 'Art.33', 'Art.34', 'Art.44', 'Art.45', 'Art.46', 'Art.47',
    #                       'Art.48', 'Art.49', 'Art.5', 'Art.50']
    #     errors = findStandardReference('EU-GDPR', euGdprStandard, self.standards)
    #     self.assertEqual(errors, "")
    #
    # def test_standard_pci_dss_v3_2_1(self):
    #     """Check that the libraries have the standard references for PCI-DSS v3.2.1"""
    #     pci_dss = ['10.5.1', '10.5.2', '10.5.3', '10.5.4', '10.5.5', '3.1', '3.2.1', '3.2.2', '3.2.3', '3.3', '3.4',
    #                '3.5.3', '3.5.4', '4.1', '4.2', '6.1', '6.2', '6.3', '6.3.1', '6.3.2', '6.4.3', '6.4.4', '6.5',
    #                '6.5.10', '6.5.1a', '6.5.1b', '6.5.2', '6.5.3', '6.5.4', '6.5.5', '6.5.6', '6.5.7', '6.5.8', '6.5.9',
    #                '7.1', '7.1.1', '7.1.2', '7.1.3', '7.1.4', '8.1.6', '8.1.7', '8.2.3', '8.2.4', '8.2.5', '8.2.6',
    #                '8.7']
    #     errors = findStandardReference('PCI-DSS-v3.2.1', pci_dss, self.standards)
    #     self.assertEqual(errors, "")
    #
    # def test_standard_pci_dss_v4_0(self):
    #     """Check that the libraries have the standard references for PCI-DSS 4.0"""
    #     pci_dss = ['1.3.1', '1.3.2', '1.4.2', '1.4.4', '10.2.1', '10.2.1.1', '10.2.1.2', '10.2.1.3', '10.2.1.4',
    #                '10.2.1.5', '10.2.1.6', '10.2.1.7', '10.2.2', '10.3.1', '10.3.2', '10.3.3', '10.3.4', '11.4',
    #                '12.10.5', '12.5.1', '2.2.1', '2.2.2', '2.2.4', '2.2.7', '3.2.1', '3.3.1', '3.3.1.1', '3.3.1.2',
    #                '3.3.1.3', '3.3.2', '3.3.3', '3.4.1', '3.4.2', '3.5.1', '3.5.1.1', '3.5.1.2', '3.5.1.3', '3.6.1.2',
    #                '3.6.1.4', '3.7.4', '3.7.5', '4.2.1', '4.2.1.2', '4.2.2', '6.2.1', '6.2.2', '6.2.3', '6.2.3.1',
    #                '6.2.4', '6.3.1', '6.3.3', '6.4.3', '6.5.5', '6.5.6', '7.2.1', '7.2.2', '7.2.6', '7.3.1', '7.3.2',
    #                '7.3.3', '8.2.5', '8.2.6', '8.2.8', '8.3.1', '8.3.2', '8.3.3', '8.3.4', '8.3.5', '8.3.6', '8.3.7',
    #                '8.3.9', '8.4.1', '8.4.2', '8.4.3', '8.5.1', '8.6.1', '8.6.2', '8.6.3', 'A2.1.1']
    #     errors = findStandardReference('PCI-DSS-v4.0', pci_dss, self.standards)
    #     self.assertEqual(errors, "")
    #
    # def test_standard_pci_sss(self):
    #     """Check that the libraries have the standard references for PCI-SSS"""
    #     pci_sss = ['10.1', '10.2', '11.1', '11.2', '2.1', '2.2', '2.3', '2.4', '2.5', '3.1', '3.2', '3.3', '3.4', '3.5',
    #                '3.6', '4.1', '4.2', '5.1', '5.2', '5.3', '5.4', '6.1', '6.2', '6.3', '7.1', '7.2', '7.3', '7.4',
    #                '8.1', '8.2', '8.3', '8.4', '9.1', 'A.1.1', 'A.2.2', 'A.2.3', 'B.2.2', 'B.2.2.1', 'B.2.2.2', 'B.2.3',
    #                'B.2.4', 'B.2.5', 'B.2.6', 'B.2.7', 'B.2.8', 'B.2.9', 'B.3.1', 'B.3.2', 'B.3.3']
    #     errors = findStandardReference('pci-sss', pci_sss, self.standards)
    #     self.assertEqual(errors, "")
    #
    # def test_standard_hipaa_required(self):
    #     """Check that the libraries have the standard references for HIPAA Required"""
    #     hipaaRequired = ['164.308(a)(1)(ii)(A)', '164.308(a)(1)(ii)(B)', '164.308(a)(1)(ii)(C)', '164.308(a)(1)(ii)(D)',
    #                      '164.308(a)(2)', '164.308(a)(4)(A)', '164.308(a)(6)', '164.308(a)(7)(A)', '164.308(a)(7)(B)',
    #                      '164.308(a)(7)(C)', '164.308(a)(8)', '164.308(b)(1)', '164.310(b)', '164.310(c)',
    #                      '164.310(d)(1)(A)', '164.310(d)(1)(B)', '164.312(a)(1)(A)', '164.312(a)(1)(B)', '164.312(b)',
    #                      '164.312(d)', '164.314(a)(2)(i)', '164.314(a)(2)(ii)', '164.314(b)(2)', '164.316(a)',
    #                      '164.316(b)(2)(i)', '164.316(b)(2)(ii)', '164.316(b)(2)(iii)']
    #     errors = findStandardReference('hipaa-required', hipaaRequired, self.standards)
    #     self.assertEqual(errors, "")
    #
    # def test_standard_hipaa_addressable(self):
    #     """Check that the libraries have the standard references for HIPAA Addressable"""
    #     hipaaAddressable = ['164.308(a)(3)(ii)(A)', '164.308(a)(3)(ii)(B)', '164.308(a)(3)(ii)(C)', '164.308(a)(4)(B)',
    #                         '164.308(a)(4)(C)', '164.308(A)(5)(A)', '164.308(A)(5)(B)', '164.308(A)(5)(C)',
    #                         '164.308(A)(5)(D)', '164.308(a)(7)(D)', '164.308(a)(7)(E)', '164.310(a)(1)(A)',
    #                         '164.310(a)(1)(B)', '164.310(a)(1)(C)', '164.310(a)(1)(D)', '164.310(d)(1)(C)',
    #                         '164.310(d)(1)(D)', '164.312(a)(1)(D)', '164.312(c)(1)', '164.312(e)(1)(A)',
    #                         '164.312(e)(1)(B)']
    #     errors = findStandardReference('hipaa-addressable', hipaaAddressable, self.standards)
    #     self.assertEqual(errors, "")
    #
    # def test_standard_owasp_mobile_top_10_2016(self):
    #     """Check that the libraries have the standard references for OWASP Mobile Top 10 2016"""
    #     owasp_mobile_top_10_2016 = ['M1: Improper Platform Usage', 'M2: Insecure Data Storage',
    #                                 'M3: Insecure Communication', 'M4: Insecure Authentication',
    #                                 'M5: Insufficient Cryptography', 'M6: Insecure Authorization',
    #                                 'M7: Client Code Quality', 'M8: Code Tampering', 'M9: Reverse Engineering',
    #                                 'M10: Extraneous Functionality']
    #     errors = findStandardReference('owasp-mobile-top-10-2016', owasp_mobile_top_10_2016, self.standards)
    #     self.assertEqual(errors, "")
    #
    # def test_standard_owasp_docker_top_10_2018(self):
    #     """Check that the libraries have the standard references for OWASP Docker Top 10 2018"""
    #     owasp_docker_top_10_2018 = ['D01 - Secure User Mapping', 'D02 - Patch Management Strategy',
    #                                 'D03 - Network Segmentation and Firewalling', 'D04 - Secure Defaults and Hardening',
    #                                 'D05 - Maintain Security Contexts', 'D06 - Protect Secrets',
    #                                 'D07 - Resource Protection', 'D08 - Container Image Integrity and Origin',
    #                                 'D09 - Follow Immutable Paradigm', 'D10 - Logging']
    #     errors = findStandardReference('owasp-docker-top-10-2018', owasp_docker_top_10_2018, self.standards)
    #     self.assertEqual(errors, "")
    #
    # def test_standard_iotsf_class_0(self):
    #     """Check that the libraries have the standard references for IoTSF Class 0"""
    #     iotsf_class_0 = ['2.4.10.10', '2.4.10.11', '2.4.10.12', '2.4.10.2', '2.4.11.7', '2.4.11.9', '2.4.12.1',
    #                      '2.4.12.13', '2.4.12.14', '2.4.12.3', '2.4.12.4', '2.4.12.7', '2.4.12.8', '2.4.5.1', '2.4.5.2',
    #                      '2.4.5.29', '2.4.5.3', '2.4.5.30', '2.4.5.8', '2.4.6.9', '2.4.7.17', '2.4.7.24', '2.4.7.5',
    #                      '2.4.8.17', '2.4.8.2', '2.4.13.25', '2.4.13.27', '2.4.13.29', '2.4.13.30', '2.4.13.31',
    #                      '2.4.13.32']
    #     errors = findStandardReference('iotsf-class-0', iotsf_class_0, self.standards)
    #     self.assertEqual(errors, "")
    #
    # def test_standard_iotsf_class_1(self):
    #     """Check that the libraries have the standard references for IoTSF Class 1"""
    #     iotsf_class_1 = ['2.4.10.1', '2.4.10.10', '2.4.10.11', '2.4.10.12', '2.4.10.13', '2.4.10.14', '2.4.10.2',
    #                      '2.4.10.3', '2.4.10.4', '2.4.10.5', '2.4.10.6', '2.4.10.7', '2.4.11.1', '2.4.11.2', '2.4.11.3',
    #                      '2.4.11.4', '2.4.11.5', '2.4.11.6', '2.4.11.7', '2.4.11.8', '2.4.11.9', '2.4.12.1',
    #                      '2.4.12.13', '2.4.12.14', '2.4.12.2', '2.4.12.3', '2.4.12.4', '2.4.12.7', '2.4.12.8',
    #                      '2.4.16.4', '2.4.5.1', '2.4.5.2', '2.4.5.29', '2.4.5.3', '2.4.5.30', '2.4.5.8', '2.4.6.10',
    #                      '2.4.6.5', '2.4.6.8', '2.4.6.9', '2.4.7.1', '2.4.7.10', '2.4.7.11', '2.4.7.12', '2.4.7.13',
    #                      '2.4.7.14', '2.4.7.17', '2.4.7.18', '2.4.7.21', '2.4.7.24', '2.4.7.3', '2.4.7.5', '2.4.7.8',
    #                      '2.4.8.11', '2.4.8.15', '2.4.8.17', '2.4.8.2', '2.4.8.3', '2.4.8.4', '2.4.8.5', '2.4.8.6',
    #                      '2.4.8.7', '2.4.8.8', '2.4.8.9', '2.4.9.4', '2.4.13.11', '2.4.13.14', '2.4.13.16', '2.4.13.17',
    #                      '2.4.13.18', '2.4.13.2', '2.4.13.21', '2.4.13.22', '2.4.13.23', '2.4.13.24', '2.4.13.25',
    #                      '2.4.13.27', '2.4.13.29', '2.4.13.3', '2.4.13.30', '2.4.13.31', '2.4.13.32', '2.4.13.4',
    #                      '2.4.13.7', '2.4.13.8', '2.4.13.9']
    #     errors = findStandardReference('iotsf-class-1', iotsf_class_1, self.standards)
    #     self.assertEqual(errors, "")
    #
    # def test_standard_iotsf_class_2(self):
    #     """Check that the libraries have the standard references for IoTSF Class 2"""
    #     iotsf_class_2 = ['2.4.10.1', '2.4.10.10', '2.4.10.11', '2.4.10.12', '2.4.10.13', '2.4.10.14', '2.4.10.2',
    #                      '2.4.10.3', '2.4.10.4', '2.4.10.5', '2.4.10.6', '2.4.10.7', '2.4.11.1', '2.4.11.2', '2.4.11.3',
    #                      '2.4.11.4', '2.4.11.5', '2.4.11.6', '2.4.11.7', '2.4.11.8', '2.4.11.9', '2.4.12.1',
    #                      '2.4.12.13', '2.4.12.14', '2.4.12.2', '2.4.12.3', '2.4.12.4', '2.4.12.7', '2.4.12.8',
    #                      '2.4.16.4', '2.4.5.1', '2.4.5.2', '2.4.5.21', '2.4.5.24', '2.4.5.29', '2.4.5.3', '2.4.5.30',
    #                      '2.4.5.33', '2.4.5.4', '2.4.5.5', '2.4.5.8', '2.4.6.10', '2.4.6.12', '2.4.6.13', '2.4.6.5',
    #                      '2.4.6.8', '2.4.6.9', '2.4.7.1', '2.4.7.10', '2.4.7.11', '2.4.7.12', '2.4.7.13', '2.4.7.14',
    #                      '2.4.7.17', '2.4.7.18', '2.4.7.21', '2.4.7.24', '2.4.7.3', '2.4.7.5', '2.4.7.8', '2.4.8.11',
    #                      '2.4.8.15', '2.4.8.17', '2.4.8.2', '2.4.8.3', '2.4.8.4', '2.4.8.5', '2.4.8.6', '2.4.8.7',
    #                      '2.4.8.8', '2.4.8.9', '2.4.9.4', '2.4.13.1', '2.4.13.11', '2.4.13.14', '2.4.13.15',
    #                      '2.4.13.16', '2.4.13.17', '2.4.13.18', '2.4.13.2', '2.4.13.20', '2.4.13.21', '2.4.13.22',
    #                      '2.4.13.23', '2.4.13.24', '2.4.13.25', '2.4.13.26', '2.4.13.27', '2.4.13.28', '2.4.13.29',
    #                      '2.4.13.3', '2.4.13.30', '2.4.13.31', '2.4.13.32', '2.4.13.33', '2.4.13.4', '2.4.13.7',
    #                      '2.4.13.8', '2.4.13.9']
    #     errors = findStandardReference('iotsf-class-2', iotsf_class_2, self.standards)
    #     self.assertEqual(errors, "")
    #
    # def test_standard_owasp_top_10_2017(self):
    #     """Check that the libraries have the standard references for OWASP Top 10 2017"""
    #     owasp_top_10_2017 = ['A1:2017-Injection', 'A2:2017-Broken Authentication', 'A3:2017-Sensitive Data Exposure',
    #                          'A4:2017-XML External Entities (XXE)', 'A5:2017-Broken Access Control',
    #                          'A6:2017-Security Misconfiguration', 'A7:2017-Cross-Site Scripting (XSS)',
    #                          'A8:2017-Insecure Deserialization', 'A9:2017-Using Components with Known Vulnerabilities',
    #                          'A10:2017-Insufficient Logging-Monitoring']
    #     errors = findStandardReference('owasp-top-10-2017', owasp_top_10_2017, self.standards)
    #     self.assertEqual(errors, "")
    #
    # def test_standard_owasp_top_10_2021(self):
    #     """Check that the libraries have the standard references for OWASP Top 10 2017"""
    #     owasp_top_10_2021 = ['A01:2021-Broken Access Control',
    #                          'A02:2021-Cryptographic Failures',
    #                          'A03:2021-Injection',
    #                          'A04:2021-Insecure Design',
    #                          'A05:2021-Security Misconfiguration',
    #                          'A06:2021-Vulnerable and Outdated Components',
    #                          'A07:2021-Identification and Authentication Failures',
    #                          'A08:2021-Software and Data Integrity Failures',
    #                          'A09:2021-Security Logging and Monitoring Failures',
    #                          'A10:2021-Server-Side Request Forgery (SSRF)']
    #     errors = findStandardReference('owasp-top-10-2021', owasp_top_10_2021, self.standards)
    #     self.assertEqual(errors, "")
    #
    # def test_standard_unece_wp29_csms(self):
    #     """Check that the libraries have the standard references for UNECE WP.29 Cybersecurity Regulation (CSMS)"""
    #     unece_wp29_csms = ['M1', 'M2', 'M3', 'M4', 'M5', 'M6', 'M7', 'M8', 'M9', 'M10', 'M11', 'M12', 'M13', 'M14',
    #                        'M15', 'M16', 'M18', 'M19', 'M20', 'M21', 'M22', 'M23', 'M24']
    #     errors = findStandardReference('unece-wp29-csms', unece_wp29_csms, self.standards)
    #     self.assertEqual(errors, "")
    #
    # def test_standard_nist_secure_microservice_strategies(self):
    #     """Check that the libraries have the standard references for NIST Security Strategies for Microservices-based Application Systems"""
    #     standardRefs = ['MS-SS-1', 'MS-SS-12', 'MS-SS-13', 'MS-SS-2']
    #     errors = findStandardReference('NIST-Secure-Microservice-Strategies', standardRefs, self.standards)
    #     self.assertEqual(errors, "")
    #
    # def test_standard_csa_container_architectures(self):
    #     """Check that the libraries have the standard references for CSA Best Practices for Implementing a Secure Application Container Architecture"""
    #     standardRefs = ['3.1.1', '3.1.10', '3.1.11', '3.1.12', '3.1.13', '3.1.14', '3.1.15', '3.1.16', '3.1.17',
    #                     '3.1.2', '3.1.3', '3.1.5', '3.1.6', '3.1.7', '3.1.8', '3.1.9']
    #     errors = findStandardReference('csa-container-architectures', standardRefs, self.standards)
    #     self.assertEqual(errors, "")
    #
    # def test_standard_cis_kubernetes_level_1(self):
    #     """Check that the libraries have the standard references for CIS Kubernetes - Level 1"""
    #     standardRefs = ['1.1.1', '1.1.10', '1.1.11', '1.1.12', '1.1.13', '1.1.14', '1.1.15', '1.1.16', '1.1.17',
    #                     '1.1.18', '1.1.19', '1.1.2', '1.1.20', '1.1.21', '1.1.3', '1.1.4', '1.1.5', '1.1.6', '1.1.7',
    #                     '1.1.8', '1.1.9', '1.2.1', '1.2.10', '1.2.11', '1.2.12', '1.2.13', '1.2.14', '1.2.15', '1.2.16',
    #                     '1.2.17', '1.2.18', '1.2.19', '1.2.2', '1.2.20', '1.2.21', '1.2.22', '1.2.23', '1.2.24',
    #                     '1.2.25', '1.2.26', '1.2.27', '1.2.28', '1.2.29', '1.2.3', '1.2.30', '1.2.31', '1.2.4', '1.2.5',
    #                     '1.2.6', '1.2.7', '1.2.8', '1.2.9', '1.3.1',
    #                     '1.3.2', '1.3.3', '1.3.4', '1.3.5', '1.3.7', '1.4.1', '1.4.2', '2.1', '2.2', '2.3', '2.4',
    #                     '2.5', '2.6', '3.1.1', '3.1.2', '3.1.3', '3.2.1', '4.1.1', '4.1.10', '4.1.2', '4.1.3', '4.1.4',
    #                     '4.1.5', '4.1.6',
    #                     '4.1.7', '4.1.8', '4.1.9', '4.2.1', '4.2.10', '4.2.11', '4.2.12', '4.2.13', '4.2.2', '4.2.3',
    #                     '4.2.4', '4.2.5', '4.2.6', '4.2.7', '4.2.9', '5.1.1', '5.1.2', '5.1.3', '5.1.4',
    #                     '5.1.5',
    #                     '5.1.6', '5.1.7', '5.1.8', '5.1.9', '5.1.10', '5.1.11', '5.1.12', '5.1.13', '5.2.1', '5.2.2',
    #                     '5.2.3', '5.2.4', '5.2.5', '5.2.6', '5.2.8', '5.2.9', '5.2.11', '5.2.12', '5.2.13',
    #                     '5.3.1', '5.7.1']
    #     errors = findStandardReference('cis-kubernetes-level-1', standardRefs, self.standards)
    #     self.assertEqual(errors, "")
    #
    # def test_standard_cis_kubernetes_level_2(self):
    #     """Check that the libraries have the standard references for CIS Kubernetes - Level 2"""
    #     standardRefs = ['1.1.1', '1.1.10', '1.1.11', '1.1.12', '1.1.13', '1.1.14', '1.1.15', '1.1.16', '1.1.17',
    #                     '1.1.18', '1.1.19', '1.1.2', '1.1.20', '1.1.21', '1.1.3', '1.1.4', '1.1.5', '1.1.6', '1.1.7',
    #                     '1.1.8', '1.1.9', '1.2.1', '1.2.10', '1.2.11', '1.2.12', '1.2.13', '1.2.14', '1.2.15', '1.2.16',
    #                     '1.2.17', '1.2.18', '1.2.19', '1.2.2', '1.2.20', '1.2.21', '1.2.22', '1.2.23', '1.2.24',
    #                     '1.2.25', '1.2.26', '1.2.27', '1.2.28', '1.2.29', '1.2.3', '1.2.30', '1.2.31', '1.2.4', '1.2.5',
    #                     '1.2.6', '1.2.7', '1.2.8', '1.2.9', '1.3.1',
    #                     '1.3.2', '1.3.3', '1.3.4', '1.3.5', '1.3.6', '1.3.7', '1.4.1', '1.4.2', '2.1', '2.2', '2.3',
    #                     '2.4', '2.5', '2.6', '2.7', '3.1.1', '3.1.2', '3.1.3', '3.2.1', '3.2.2', '4.1.1', '4.1.10',
    #                     '4.1.2', '4.1.3',
    #                     '4.1.4', '4.1.5', '4.1.6', '4.1.7', '4.1.8', '4.1.9', '4.2.1', '4.2.10', '4.2.11', '4.2.12',
    #                     '4.2.13', '4.2.2', '4.2.3', '4.2.4', '4.2.5', '4.2.6', '4.2.7', '4.2.8', '4.2.9', '5.1.1',
    #                     '5.1.2', '5.1.3', '5.1.4', '5.1.5', '5.1.6', '5.1.7', '5.1.8', '5.1.9', '5.1.10', '5.1.11',
    #                     '5.1.12', '5.1.13', '5.2.1', '5.2.2', '5.2.3', '5.2.4', '5.2.5',
    #                     '5.2.6', '5.2.8', '5.2.9', '5.2.11', '5.2.12', '5.2.13', '5.3.1', '5.3.2', '5.4.1',
    #                     '5.4.2', '5.5.1', '5.7.1',
    #                     '5.7.2', '5.7.3', '5.7.4']
    #     errors = findStandardReference('cis-kubernetes-level-2', standardRefs, self.standards)
    #     self.assertEqual(errors, "")
    #
    # def test_standard_gcp_cis_standard_level_1(self):
    #     """Check that the libraries have the standard references for GCP CIS Standard Level 1"""
    #     standardRefs = ['1.1', '1.10', '1.13', '1.14', '1.15', '1.16', '1.18', '1.2', '1.4', '1.5', '1.6', '1.7', '1.9',
    #                     '2.12', '2.13', '2.16', '2.2', '2.3', '2.4', '2.5', '2.6', '3.9', '4.1', '4.2', '4.3', '4.4',
    #                     '4.5',
    #                     '4.6',
    #                     '5.1', '6.1.1', '6.1.2', '6.1.3', '6.2.2', '6.2.3', '6.2.4', '6.2.5', '6.2.6', '6.2.7', '6.2.8',
    #                     '6.2.9',
    #                     '6.3.1', '6.3.2', '6.3.3', '6.3.4', '6.3.5', '6.3.6', '6.3.7', '6.4', '6.5', '6.7', '7.1']
    #     errors = findStandardReference('cis-gcp-standard', standardRefs, self.standards)
    #     self.assertEqual(errors, "")
    #
    # def test_standard_gcp_cis_standard_level_2(self):
    #     """Check that the libraries have the standard references for GCP CIS Standard Level 2"""
    #     standardRefs = ['1.1', '1.10', '1.11', '1.12', '1.13', '1.14', '1.15', '1.16', '1.17', '1.18', '1.2', '1.3',
    #                     '1.4', '1.5', '1.6', '1.7', '1.8', '1.9', '2.10', '2.11', '2.12', '2.13', '2.14', '2.15',
    #                     '2.16', '2.2',
    #                     '2.3', '2.4', '2.5', '2.6', '2.7', '2.8', '2.9', '3.1', '3.10', '3.2', '3.3', '3.4', '3.5',
    #                     '3.6', '3.7', '3.8', '4.1', '4.10', '4.11', '4.12', '4.2', '4.3', '4.4', '4.5', '4.6', '4.7',
    #                     '4.8', '4.9', '5.1', '5.2', '6.1.1', '6.1.2', '6.1.3', '6.2.1', '6.2.2', '6.2.3', '6.2.4',
    #                     '6.2.6', '6.2.7', '6.2.8', '6.2.9', '6.3.1', '6.3.2', '6.3.3', '6.3.4', '6.3.5', '6.3.6',
    #                     '6.3.7',
    #                     '6.4', '6.5', '6.6', '6.7', '7.1', '7.2', '7.3']
    #     errors = findStandardReference('cis-gcp-standard-level-2', standardRefs, self.standards)
    #     self.assertEqual(errors, "")
    #
    # def test_standard_azure_cis_standard(self):
    #     """Check that the libraries have the standard references for CIS Azure Foundations Benchmark Level 1"""
    #     standardRefs = ["1.1.1", "1.1.2", "1.1.4", "1.2.1", "1.2.2", "1.2.3", "1.2.4", "1.2.5", "1.2.6", "1.3", "1.5",
    #                     "1.6", "1.7", "1.8", "1.9", "1.10", "1.11", "1.13", "1.14", "1.15", "1.17", "1.22", "1.23",
    #                     "2.1.13", "2.1.14", "2.1.15", "2.1.18", "2.1.19", "2.1.20", "3.1", "3.3", "3.4", "3.5", "3.6",
    #                     "3.7", "3.8", "3.10", "3.11", "3.15", "4.1.1", "4.1.2", "4.1.4", "4.1.5", "4.1.6", "4.2.5",
    #                     "4.3.1", "4.3.2", "4.3.3", "4.3.4", "4.3.5", "4.3.6", "4.3.7", "4.3.8", "4.4.1", "4.4.2",
    #                     "4.5.3", "5.1.1", "5.1.2", "5.1.3", "5.1.5", "5.2.1", "5.2.2", "5.2.3", "5.2.4", "5.2.5",
    #                     "5.2.6", "5.2.7", "5.2.8", "5.2.9", "5.2.10", "5.4", "6.1", "6.2", "6.3", "6.4", "6.7", "7.2",
    #                     "7.5", "8.1", "8.2", "8.3", "8.4", "8.5", "9.2", "9.3", "9.5", "9.6", "9.7", "9.8", "9.9",
    #                     "9.10"]
    #
    #     errors = findStandardReference('cis-azure-standard', standardRefs, self.standards)
    #     self.assertEqual(errors, "")
    #
    # def test_standard_azure_cis_standard_level_2(self):
    #     """Check that the libraries have the standard references for CIS Azure Foundations Benchmark Level 2"""
    #     standardRefs = ["1.1.1", "1.1.2", "1.1.3", "1.1.4", "1.2.1", "1.2.2", "1.2.3", "1.2.4", "1.2.5", "1.2.6",
    #                     "1.3", "1.4", "1.5", "1.6", "1.7", "1.8", "1.9", "1.10", "1.11", "1.12", "1.13", "1.14",
    #                     "1.15", "1.16", "1.17", "1.18", "1.19", "1.20", "1.21", "1.22", "1.23", "1.24", "1.25",
    #                     "2.1.1", "2.1.2", "2.1.3", "2.1.4", "2.1.5", "2.1.6", "2.1.7", "2.1.8", "2.1.9", "2.1.10",
    #                     "2.1.11", "2.1.12", "2.1.13", "2.1.14", "2.1.15", "2.1.16", "2.1.17", "2.1.18", "2.1.19",
    #                     "2.1.20", "2.1.21", "2.1.22", "2.2.1", "3.1", "3.2", "3.3", "3.4", "3.5", "3.6", "3.7",
    #                     "3.8", "3.9", "3.10", "3.11", "3.12", "3.13", "3.14", "3.15", "4.1.1", "4.1.2", "4.1.3",
    #                     "4.1.4", "4.1.5", "4.1.6", "4.2.1", "4.2.2", "4.2.3", "4.2.4", "4.2.5", "4.3.1", "4.3.2",
    #                     "4.3.3", "4.3.4", "4.3.5", "4.3.6", "4.3.7", "4.3.8", "4.4.1", "4.4.2", "4.4.3", "4.4.4",
    #                     "4.5.1", "4.5.2", "4.5.3", "5.1.1", "5.1.2", "5.1.3", "5.1.4", "5.1.5", "5.1.6", "5.1.7",
    #                     "5.2.1", "5.2.2", "5.2.3", "5.2.4", "5.2.5", "5.2.6", "5.2.7", "5.2.8", "5.2.9", "5.2.10",
    #                     "5.3.1", "5.4", "5.5", "6.1", "6.2", "6.3", "6.4", "6.5", "6.6", "6.7", "7.1", "7.2", "7.3",
    #                     "7.4", "7.5", "7.6", "8.1", "8.2", "8.3", "8.4", "8.5", "8.6", "8.7", "8.8", "9.1", "9.2",
    #                     "9.3", "9.4", "9.5", "9.6", "9.7", "9.8", "9.9", "9.10", "9.11", "10.1"]
    #
    #     errors = findStandardReference('cis-azure-standard-level-2', standardRefs, self.standards)
    #     self.assertEqual(errors, "")
    #
    # def test_standard_cwe_top_25_dangerous_weaknesses(self):
    #     """Check that the libraries have the standard references for CWE Top 25 Dangerous Weaknesses"""
    #     standardRefs = ['cwe-top-25']
    #     errors = findStandardReference('cwe-top-25-dangerous-weaknesses', standardRefs, self.standards)
    #     self.assertEqual(errors, "")
    #
    # def test_standard_nist_csf(self):
    #     """Check that the libraries have the standard references for NIST CSF"""
    #     standardRefs = ['DE.AE-1', 'DE.AE-2', 'DE.AE-3', 'DE.CM-1', 'DE.CM-2', 'DE.CM-3',
    #                     'DE.CM-4', 'DE.CM-5', 'DE.CM-6', 'DE.CM-7', 'DE.DP-1', 'DE.DP-2', 'DE.DP-3', 'DE.DP-4',
    #                     'DE.DP-5', 'ID.AM-3', 'ID.AM-4', 'ID.AM-5', 'ID.RA-1', 'ID.RA-2',
    #                     'ID.RA-3', 'ID.RA-5',
    #                     'ID.SC-4', 'PR.AC-1', 'PR.AC-3', 'PR.AC-4', 'PR.AC-5', 'PR.AC-6', 'PR.AC-7',
    #                     'PR.DS-1', 'PR.DS-2', 'PR.DS-4', 'PR.DS-5', 'PR.DS-6',
    #                     'PR.IP-12', 'PR.IP-7', 'PR.IP-8', 'PR.PT-1', 'PR.PT-3', 'PR.PT-4', 'PR.PT-5',
    #                     'RS.AN-1',
    #                     'RS.AN-3', 'RS.AN-5', 'RS.CO-2', 'RS.CO-5', 'RS.MI-3']
    #     errors = findStandardReference('nist-csf', standardRefs, self.standards)
    #     self.assertEqual(errors, "")
    #
    # def test_standard_csa_api_security_guidelines(self):
    #     """Check that the libraries have the standard references for CSA API Security Guidelines"""
    #     standardRefs = ['1', '2', '3', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18',
    #                     '19', '20', '21', '22', '23', '24', '26', '27', '29', '30', '31']
    #     errors = findStandardReference('csa-api-security-guidelines', standardRefs, self.standards)
    #     self.assertEqual(errors, "")
    #
    # def test_standard_iso_sae_21434(self):
    #     """Check that the libraries have the standard references for ISO/SAE 21434"""
    #     standardRefs = ['10.4.2', '10.4.3', '11.3', '5.4.1', '5.4.2', '6.4.2', '6.4.7', '7.3', '7.4', '7.5', '7.6',
    #                     '8.3', '8.4', '8.5', '8.6', '8.7', '8.8', '8.9']
    #     errors = findStandardReference('iso-sae-21434', standardRefs, self.standards)
    #     self.assertEqual(errors, "")
    #
    # def test_standard_azure_security_benchmark(self):
    #     """Check that the libraries have the standard references for ASB"""
    #     standardRefs = ["AM-1", "AM-2", "AM-3", "AM-5", "BR-1", "BR-2", "BR-3", "BR-4", "DP-2", "DP-3", "DP-4", "DP-5",
    #                     "DP-6", "DP-7", "DP-8", "ES-1", "ES-2", "ES-3", "GS-1", "GS-2", "GS-4", "GS-5", "GS-6", "GS-7",
    #                     "GS-8", "GS-9", "IM-1", "IM-2", "IM-3", "IM-4", "IM-5", "IM-6", "IM-7", "IM-8", "IM-9", "IR-1",
    #                     "IR-2", "IR-3", "IR-4", "IR-5", "IR-6", "LT-1", "LT-2", "LT-3", "LT-4", "LT-5", "LT-6", "LT-7",
    #                     "NS-1", "NS-10", "NS-2", "NS-3", "NS-4", "NS-5", "NS-6", "NS-7", "NS-8", "NS-9", "PA-1", "PA-2",
    #                     "PA-3", "PA-4", "PA-5", "PA-6", "PA-7", "PA-8", "PV-2", "PV-3", "PV-4", "PV-5", "PV-6", "PV-7"]
    #     errors = findStandardReference('azure-security-benchmark', standardRefs, self.standards)
    #     self.assertEqual(errors, "")
    #
    # def test_standard_fedramp_low_baseline(self):
    #     """Check that the libraries have the standard references for FedRAMP Low"""
    #     standardRefs = [
    #         'AC-2', 'AC-3', 'AC-7', 'AC-8', 'AC-17', 'AC-18', 'AC-19', 'AC-20', 'AC-22',
    #         'AU-1', 'AU-2', 'AU-3', 'AU-4', 'AU-5', 'AU-6', 'AU-8', 'AU-9', 'AU-11', 'AU-12',
    #         'IA-2', 'IA-4', 'IA-5', 'IA-6', 'IA-7', 'IA-11',
    #         'SC-5', 'SC-7', 'SC-8', 'SC-13', 'SC-15', 'SC-20', 'SC-21', 'SC-22', 'SC-28', 'SC-39'
    #     ]
    #     errors = findStandardReference('fedramp-low-baseline', standardRefs, self.standards)
    #     self.assertEqual(errors, "")
    #
    # def test_standard_fedramp_moderate_baseline(self):
    #     """Check that the libraries have the standard references for FedRAMP Moderate"""
    #     standardRefs = [
    #         'AC-2', 'AC-3', 'AC-4', 'AC-5', 'AC-6', 'AC-7', 'AC-8', 'AC-12', 'AC-17',
    #         'AC-18', 'AC-19', 'AC-20', 'AC-22',
    #         'AU-1', 'AU-2', 'AU-3', 'AU-4', 'AU-5', 'AU-6', 'AU-7', 'AU-8', 'AU-9', 'AU-11', 'AU-12',
    #         'IA-2', 'IA-4', 'IA-5', 'IA-6', 'IA-7', 'IA-11',
    #         'SC-2', 'SC-4', 'SC-5', 'SC-7', 'SC-8', 'SC-10', 'SC-13', 'SC-15',
    #         'SC-18', 'SC-20', 'SC-21', 'SC-22', 'SC-23', 'SC-28', 'SC-39'
    #     ]
    #     errors = findStandardReference('fedramp-moderate-baseline', standardRefs, self.standards)
    #     self.assertEqual(errors, "")
    #
    # def test_standard_fedramp_high_baseline(self):
    #     """Check that the libraries have the standard references for FedRAMP High"""
    #     standardRefs = [
    #         'AC-2', 'AC-3', 'AC-4', 'AC-5', 'AC-6', 'AC-7', 'AC-8', 'AC-10', 'AC-12', 'AC-17',
    #         'AC-18', 'AC-19', 'AC-20', 'AC-22',
    #         'AU-1', 'AU-2', 'AU-3', 'AU-4', 'AU-5', 'AU-6', 'AU-7', 'AU-8', 'AU-9', 'AU-10', 'AU-11', 'AU-12',
    #         'IA-2', 'IA-4', 'IA-5', 'IA-6', 'IA-7', 'IA-11',
    #         'SC-2', 'SC-4', 'SC-5', 'SC-7', 'SC-8', 'SC-10', 'SC-13', 'SC-15',
    #         'SC-18', 'SC-20', 'SC-21', 'SC-22', 'SC-23', 'SC-24', 'SC-28', 'SC-39'
    #     ]
    #     errors = findStandardReference('fedramp-high-baseline', standardRefs, self.standards)
    #     self.assertEqual(errors, "")
    #
    # def test_standard_owasp_csvs_l1(self):
    #     """Check that the libraries have the standard references for OWASP CSVS L1"""
    #     sts = ['11.1', '11.2', '2.10', '2.13', '2.14', '2.15', '2.4', '3.11', '3.12', '3.13', '3.15', '3.5', '3.8',
    #            '4.1', '4.2', '5.2', '5.4', '6.3', '6.9', '7.1', '7.11', '7.12', '7.6', '7.7', '8.1', '8.2', '8.3',
    #            '8.4', '8.5', '9.6']
    #     errors = findStandardReference('OWASP-CSVS-L1', sts, self.standards)
    #     self.assertEqual(errors, "")
    #
    # def test_standard_owasp_csvs_l2(self):
    #     """Check that the libraries have the standard references for OWASP CSVS L2"""
    #     sts = ['10.1', '10.2', '10.3', '10.4', '10.5', '11.1', '11.2', '11.4', '11.5', '2.10', '2.11', '2.13', '2.14',
    #            '2.15', '2.4', '2.5', '2.8', '2.9', '3.1', '3.10', '3.11', '3.12', '3.13', '3.15', '3.5', '3.8', '3.9',
    #            '4.1', '4.2', '4.3', '5.2', '5.3', '5.4', '5.5', '6.1', '6.10', '6.3', '6.5', '6.8', '6.9', '7.1',
    #            '7.11', '7.12', '7.2', '7.3', '7.5', '7.6', '7.7', '7.9', '8.1', '8.2', '8.3', '8.4', '8.5', '9.2',
    #            '9.3', '9.4', '9.6']
    #     errors = findStandardReference('OWASP-CSVS-L2', sts, self.standards)
    #     self.assertEqual(errors, "")
    #
    # def test_standard_owasp_csvs_l3(self):
    #     """Check that the libraries have the standard references for OWASP CSVS L3"""
    #     sts = ['10.1', '10.2', '10.3', '10.4', '10.5', '10.6', '11.1', '11.2', '11.3', '11.4', '11.5', '2.10', '2.11',
    #            '2.12', '2.13', '2.14', '2.15', '2.4', '2.5', '2.6', '2.8', '2.9', '3.1', '3.10', '3.11', '3.12', '3.13',
    #            '3.14', '3.15', '3.3', '3.5', '3.6', '3.7', '3.8', '3.9', '4.1', '4.2', '4.3', '4.4', '5.1', '5.2',
    #            '5.3', '5.4', '5.5', '6.1', '6.10', '6.3', '6.5', '6.8', '6.9', '7.1', '7.11', '7.12', '7.2', '7.3',
    #            '7.5', '7.6', '7.7', '7.9', '8.1', '8.2', '8.3', '8.4', '8.5', '9.2', '9.3', '9.4', '9.6']
    #     errors = findStandardReference('OWASP-CSVS-L3', sts, self.standards)
    #     self.assertEqual(errors, "")
    #
    # def test_standard_nist_800_190(self):
    #     """Check that the libraries have the standard references for OWASP CSVS L1"""
    #     sts = ['4.1.1', '4.1.2', '4.1.3', '4.1.4', '4.1.5', '4.2.1', '4.2.2', '4.2.3', '4.3.1', '4.3.2', '4.3.3',
    #            '4.3.4', '4.3.5', '4.4.1', '4.4.2', '4.4.3', '4.4.4', '4.4.5', '4.5.1', '4.5.2', '4.5.3', '4.5.4',
    #            '4.5.5']
    #     errors = findStandardReference('nist-800-190', sts, self.standards)
    #     self.assertEqual(errors, "")
    #
    # def test_standard_owasp_kubernetes_top_10_2022(self):
    #     """Check that the libraries have the standard references for CIS Kubernetes - Level 1"""
    #     standardRefs = ['K01 - Insecure Workload Configurations', 'K02 - Supply Chain Vulnerabilities',
    #                     'K03 - Overly Permissive RBAC', 'K04 - Policy Enforcement', 'K05 - Inadequate Logging',
    #                     'K06 - Broken Authentication', 'K07 - Network Segmentation', 'K08 - Secrets Management',
    #                     'K09 - Misconfigured Cluster Components',
    #                     'K10 - Vulnerable Components']
    #     errors = findStandardReference('owasp-kubernetes-top-10-2022', standardRefs, self.standards)
    #     self.assertEqual(errors, "")
    #
    # def test_standard_cis_oracle_cloud_level_1(self):
    #     """Check that the libraries have the standard references for CIS Oracle Cloud Infrastructure Foundations Level 1"""
    #     standardRefs = ["1.1", "1.10", "1.11", "1.12", "1.13", "1.2", "1.3", "1.4", "1.5", "1.6", "1.7", "1.8", "1.9",
    #                     "2.1", "2.2", "2.3",
    #                     "2.4", "2.5", "2.6", "2.7", "2.8", "3.1", "3.10", "3.11", "3.12", "3.13", "3.15", "3.16", "3.2",
    #                     "3.3", "3.4",
    #                     "3.5", "3.6", "3.7", "3.8", "3.9", "4.1.1", "5.1", "5.2"]
    #     errors = findStandardReference('cis-oracle-cloud-level-1', standardRefs, self.standards)
    #     self.assertEqual(errors, "")
    #
    # def test_standard_cis_oracle_cloud_level_2(self):
    #     """Check that the libraries have the standard references for CIS Oracle Cloud Infrastructure Foundations Level 1"""
    #     standardRefs = ["1.1", "1.10", "1.11", "1.12", "1.13", "1.14", "1.2", "1.3", "1.4", "1.5", "1.6", "1.7", "1.8",
    #                     "1.9", "2.1",
    #                     "2.2", "2.3", "2.4", "2.5", "2.6", "2.7", "2.8", "3.1", "3.10", "3.11", "3.12", "3.13", "3.14",
    #                     "3.15", "3.16",
    #                     "3.17", "3.2", "3.3", "3.4", "3.5", "3.6", "3.7", "3.8", "3.9", "4.1.1", "4.1.2", "4.1.3",
    #                     "4.2.1", "4.2.2",
    #                     "4.3.1", "5.1", "5.2"]
    #     errors = findStandardReference('cis-oracle-cloud-level-2', standardRefs, self.standards)
    #     self.assertEqual(errors, "")
    #
    # def test_standard_owasp_masvs(self):
    #     """Check that the libraries have the standard references for CIS Oracle Cloud Infrastructure Foundations Level 1"""
    #     standardRefs = ['MASVS-AUTH-2', 'MASVS-CODE-2', 'MASVS-CODE-3', 'MASVS-CODE-4', 'MASVS-CRYPTO-1',
    #                     'MASVS-CRYPTO-2', 'MASVS-NETWORK-1', 'MASVS-NETWORK-2', 'MASVS-PLATFORM-1', 'MASVS-PLATFORM-2',
    #                     'MASVS-PLATFORM-3', 'MASVS-RESILIENCE-1', 'MASVS-RESILIENCE-2', 'MASVS-RESILIENCE-3',
    #                     'MASVS-RESILIENCE-4', 'MASVS-STORAGE-1', 'MASVS-STORAGE-2']
    #     errors = findStandardReference('owasp-masvs-testing-guide', standardRefs, self.standards)
    #     self.assertEqual(errors, "")
    #
    # def test_standard_iso_27002_2022(self):
    #     """Check that the libraries have the standard references for CIS Oracle Cloud Infrastructure Foundations Level 1"""
    #     standardRefs = ['5.14', '5.15', '5.17', '5.18', '8.1', '8.13', '8.15', '8.17', '8.18', '8.19', '8.2', '8.20',
    #                     '8.24', '8.3', '8.32', '8.4', '8.5', '8.8']
    #     errors = findStandardReference('iso-27002-2022', standardRefs, self.standards)
    #     self.assertEqual(errors, "")
    #
    # def test_standard_swift_cscf(self):
    #     """Check that the libraries have the standard references for CIS Oracle Cloud Infrastructure Foundations Level 1"""
    #     standardRefs = ['1.1', '1.2', '1.4', '1.5', '2.1', '2.11A', '2.2', '2.4A', '2.5A', '2.6', '2.7',
    #                     '2.8A', '2.9', '4.1', '4.2', '5.1', '5.2', '5.3A', '5.4', '6.1', '6.2', '6.3', '6.4', '6.5A',
    #                     '7.3A', '7.4A']
    #     errors = findStandardReference('swift-cscf', standardRefs, self.standards)
    #     self.assertEqual(errors, "")


if __name__ == "__main__":
    unittest.main()
