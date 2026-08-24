import csv
import json
import unittest
from pathlib import Path

import pytest
from typer.testing import CliRunner

from isra.main import app
from isra.src.config.constants import TEMPLATE_FILE
from isra.src.utils.text_functions import compare_elements
from isra.test.aux_test_functions import get_template, set_component_from_file, assert_process


def get_threat_answers():

    with open(TEMPLATE_FILE, "r") as f:
        template = json.loads(f.read())

    answers = "I want to replace existing values with new ones\n"

    answers += "".join(["y\n" for _ in range(0, len(template["threats"]))])
    # Last answer is to save or not
    answers += "y\n"

    return answers


def get_control_answers():
    with open(TEMPLATE_FILE, "r") as f:
        template = json.loads(f.read())

    answers = "I want to replace existing values with new ones\n"
    answers += "".join(["y\n" for _ in range(0, len(template["controls"]))])
    # Last answer is to save or not
    answers += "y\n"

    return answers


class CLITests(unittest.TestCase):
    runner = CliRunner()

    @pytest.fixture(scope="function", autouse=True)
    def setup(self):
        self.runner.invoke(app, ["component", "restart", "--force"])

    def run_about(self):
        result = self.runner.invoke(app, ["about"])
        assert_process(result)

    def run_component_new(self):
        result = self.runner.invoke(app, ["component", "new"],
                                    input="Redis Server\nMy description of Redis Server\nservice-side")
        assert_process(result)

    def run_component_save(self, format):
        result = self.runner.invoke(app, ["component", "save", "--format", format])
        assert_process(result)

    def run_component_tm(self):
        result = self.runner.invoke(app, ["component", "tm"], input="y\n")
        assert_process(result)

    def run_component_restart(self):
        result = self.runner.invoke(app, ["component", "restart", "--force"])
        assert_process(result)

    def run_component_load(self, input_commands):
        result = self.runner.invoke(app, ["component", "load"], input=input_commands)
        assert_process(result)

    def run_threat_screening(self, screening):
        result = self.runner.invoke(app, ["screening", screening], input=get_threat_answers())
        assert_process(result)

    def run_control_screening(self, screening):
        result = self.runner.invoke(app, ["screening", screening], input=get_control_answers())
        assert_process(result)

    def run_autoscreening(self):
        result = self.runner.invoke(app, ["screening", "autoscreening"], input="y\n")
        assert_process(result)

    def run_standards_expand(self):
        result = self.runner.invoke(app, ["standards", "expand"])
        assert_process(result)

    def test_about(self):
        self.run_about()

    def test_standards_test_requires_options(self):
        result = self.runner.invoke(app, ["standards", "test"])

        assert result.exit_code == 2
        assert "Missing option '--standard-name'" in result.stdout

    def test_standards_test_rejects_unknown_standard(self):
        result = self.runner.invoke(app, [
            "standards", "test",
            "--standard-name", "invalid",
            "--standard-section", "V3.2.1"
        ])

        assert result.exit_code == 2
        assert "Unknown baseline standard 'invalid'" in result.stdout

    def test_standards_help_descriptions(self):
        test_result = self.runner.invoke(app, ["standards", "test", "--help"])
        reset_result = self.runner.invoke(app, ["standards", "reset", "--help"])
        coverage_result = self.runner.invoke(app, ["standards", "coverage-report", "--help"])

        assert test_result.exit_code == 0
        assert "Tests OpenCRE expansion" in test_result.stdout
        assert reset_result.exit_code == 0
        assert "Removes all standards" in reset_result.stdout
        assert coverage_result.exit_code == 0
        assert "--std-refs" in coverage_result.stdout
        assert "--yaml-component-repo" in coverage_result.stdout
        assert "--format" in coverage_result.stdout

    def test_standards_coverage_report_expands_without_changing_components(self):
        component_yaml = """component:
  ref: CD-V2-TEST-COVERAGE
  name: Test Coverage
  category: test-components
  risk_pattern:
    threats:
    - countermeasures:
      - base_standard: ASVS V4
        ref: C-TEST-COVERAGE
        base_standard_section:
        - V3.2.1
        standards: {}
"""
        with self.runner.isolated_filesystem():
            component_repo = Path("components")
            component_repo.mkdir()
            component_path = component_repo / "component.yaml"
            component_path.write_text(component_yaml, encoding="utf8")
            (component_repo / "workflow.yml").write_text("jobs: {}\n", encoding="utf8")
            (component_repo / "nonmatching.yaml").write_text(
                """component:
  ref: CD-V2-NONMATCHING
  name: Nonmatching
  category: test-components
  risk_pattern:
    threats: []
""",
                encoding="utf8"
            )

            result = self.runner.invoke(app, [
                "standards", "coverage-report",
                "--std-refs",
                "owasp-asvs5-level-1, owasp-asvs5-level-2,owasp-asvs5-level-3,owasp-top-10-2025",
                "--yaml-component-repo", str(component_repo),
                "--output", "report.md",
            ])

            assert_process(result)
            report = Path("report.md").read_text(encoding="utf8")
            assert "## test-components" in report
            assert "Test Coverage" in report
            assert "Matching components: **1 of 2**" in report
            assert "| test-components | 1 | 2 |" in report
            assert "### Test Coverage (`CD-V2-TEST-COVERAGE`)" in report
            assert "| Countermeasure ref | owasp-asvs5-level-1 |" in report
            assert "V7.2.4" in report
            assert "A07:2025 Authentication Failures" in report
            assert "| `C-TEST-COVERAGE` |" in report
            assert "**Countermeasures:**" not in report
            assert component_path.read_text(encoding="utf8") == component_yaml

            csv_result = self.runner.invoke(app, [
                "standards", "coverage-report",
                "--std-refs", "owasp-asvs5-level-1,owasp-top-10-2025",
                "--yaml-component-repo", str(component_repo),
                "--format", "csv",
            ])

            assert_process(csv_result)
            with Path("standards-coverage-report.csv").open(newline="", encoding="utf8") as csv_file:
                rows = list(csv.DictReader(csv_file))
            assert len(rows) == 1
            assert rows[0]["repository_matching_components"] == "1"
            assert rows[0]["repository_total_components"] == "2"
            assert rows[0]["category_matching_components"] == "1"
            assert rows[0]["category_total_components"] == "2"
            assert rows[0]["component_ref"] == "CD-V2-TEST-COVERAGE"
            assert rows[0]["countermeasure_ref"] == "C-TEST-COVERAGE"
            assert rows[0]["owasp-asvs5-level-1"] == "V7.2.4"
            assert rows[0]["owasp-top-10-2025"] == "A07:2025 Authentication Failures"

    def test_standards_coverage_report_rejects_unknown_standard(self):
        with self.runner.isolated_filesystem():
            Path("components").mkdir()
            result = self.runner.invoke(app, [
                "standards", "coverage-report",
                "--std-refs", "not-a-standard",
                "--yaml-component-repo", "components",
            ])

        assert result.exit_code == 2
        assert "Unknown standard ref(s): not-a-standard" in result.stdout

    def test_component_new(self):
        self.run_component_new()

    def test_component_save_xml_empty(self):
        self.run_component_new()
        self.run_component_save("xml")

    def test_component_save_yaml_empty(self):
        self.run_component_new()
        self.run_component_save("yaml")

    def test_component_save_xml(self):
        self.run_component_new()
        self.run_component_tm()
        self.run_component_save("xml")

    def test_component_save_yaml(self):
        self.run_component_new()
        self.run_component_tm()
        self.run_threat_screening("stride")
        self.run_control_screening("cwe")
        self.run_component_save("yaml")

    def test_component_load(self):
        self.run_component_new()
        self.run_component_save("xml")
        self.run_component_restart()
        self.run_component_load("CD-V2-REDIS-SERVER.xml")

    def test_component_xml_yaml_have_same_info(self):
        self.run_component_new()
        self.run_component_tm()
        self.run_autoscreening()
        self.run_control_screening("cwe")
        self.run_component_save("xml")
        self.run_component_save("yaml")
        self.run_component_restart()
        self.run_component_load("CD-V2-REDIS-SERVER.xml")
        template1 = get_template()
        self.run_component_restart()
        self.run_component_load("CD-V2-REDIS-SERVER.yaml")
        template2 = get_template()

        result = compare_elements(template1, template2)
        assert result

    def test_component_xml_yaml_have_same_info_complete(self):
        set_component_from_file("test_files/test1.irius")
        self.run_standards_expand()
        self.run_component_save("xml")
        self.run_component_save("yaml")
        self.run_component_restart()
        self.run_component_load("CD-V2-TEST-COMPONENT.xml")
        self.run_standards_expand()
        template1 = get_template()
        self.run_component_restart()
        self.run_component_load("CD-V2-TEST-COMPONENT.yaml")
        self.run_standards_expand()
        template2 = get_template()
        result = compare_elements(template1, template2)
        assert result

    def test_component_tm(self):
        self.run_component_new()
        self.run_component_tm()

    def test_screening_stride(self):
        self.run_component_new()
        self.run_component_tm()
        self.run_threat_screening("stride")

    def test_screening_cia(self):
        self.run_component_new()
        self.run_component_tm()
        self.run_threat_screening("cia")

    def test_screening_attack(self):
        self.run_component_new()
        self.run_component_tm()
        self.run_threat_screening("attack")

    def test_screening_scope(self):
        self.run_component_new()
        self.run_component_tm()
        self.run_control_screening("scope")
