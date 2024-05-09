import unittest
from time import sleep

import pytest
from typer.testing import CliRunner

from isra.main import app
from isra.src.utils.text_functions import compare_elements
from isra.test.aux_test_functions import get_template, set_component_from_file, assert_process


class CLITests(unittest.TestCase):
    runner = CliRunner()

    @pytest.fixture(scope="function", autouse=True)
    def setup(self):
        self.runner.invoke(app, ["component", "restart", "--force"])

    def run_component_save(self, format):
        result = self.runner.invoke(app, ["component", "save", "--format", format])
        assert_process(result)

    def run_component_restart(self):
        result = self.runner.invoke(app, ["component", "restart", "--force"])
        assert_process(result)

    def run_component_load(self, input_commands):
        result = self.runner.invoke(app, ["component", "load"], input=input_commands)
        assert_process(result)

    def run_component_upload(self):
        result = self.runner.invoke(app, ["component", "upload"])
        assert_process(result)

    def run_component_pull(self):
        result = self.runner.invoke(app, ["component", "pull"])
        assert_process(result)

    def run_standards_expand(self):
        result = self.runner.invoke(app, ["standards", "expand"])
        assert_process(result)

    def test_component_upload_and_pull(self):
        set_component_from_file("test_files/test1.irius")
        self.run_standards_expand()
        self.run_component_upload()
        template1 = get_template()
        print(template1)
        sleep(30)
        self.run_component_pull()
        self.run_standards_expand()
        template2 = get_template()
        print(template2)
        result = compare_elements(template1, template2)
        assert result
