import os

import pytest
import typer

rootdir = os.path.dirname(os.path.abspath(__file__))

app = typer.Typer(no_args_is_help=True, add_help_option=False)

yaml_components = typer.Typer(no_args_is_help=True, add_help_option=False)
xml_libraries = typer.Typer(no_args_is_help=True, add_help_option=False)

app.add_typer(yaml_components, name="components")
app.add_typer(xml_libraries, name="libraries")


@app.callback()
def callback():
    """
    Testing suite
    """


@yaml_components.callback()
def yaml_components_callback():
    """Tests that run for YAML components"""


@yaml_components.command()
def all():
    """
    Run all tests
    """
    exit(pytest.main(['-v', '-p no:warnings', f'{rootdir}/components']))


@yaml_components.command()
def component():
    """
    Run pytest with tests that affect each component separately
    """
    exit(pytest.main(['-v', '-p no:warnings', f'{rootdir}/components/test_component.py']))


@yaml_components.command()
def components():
    """
    Run pytest with tests that affect all components at the same time
    """
    exit(pytest.main(['-v', '-p no:warnings', f'{rootdir}/components/test_all_components.py']))


@xml_libraries.callback()
def xml_libraries_callback():
    """Tests that run for XML libraries"""


@xml_libraries.command()
def all():
    """
    Run all tests
    """
    exit(pytest.main(['-v', '-p no:warnings', f'{rootdir}/libraries']))
