import json
import os
import unittest

import pytest
from typer.testing import CliRunner

from isra.main import app
from isra.src.config.config import get_app_dir
from isra.src.utils.text_functions import compare_elements
from isra.test.aux_test_functions import get_template, set_component_from_file, assert_process


def get_threat_answers():
    properties_dir = get_app_dir()

    template_path = os.path.join(properties_dir, "temp.irius")
    with open(template_path, "r") as f:
        template = json.loads(f.read())

    answers = "I want to replace existing values with new ones\n"

    answers += "".join(["y\n" for _ in range(0, len(template["threats"]))])
    # Last answer is to save or not
    answers += "y\n"

    return answers


def get_control_answers():
    properties_dir = get_app_dir()
    template_path = os.path.join(properties_dir, "temp.irius")
    with open(template_path, "r") as f:
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

    def run_component_upload(self, input_commands):
        result = self.runner.invoke(app, ["component", "upload"], input=input_commands)
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
