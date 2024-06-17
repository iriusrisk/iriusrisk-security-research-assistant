import os

import pytest
import typer

rootdir = os.path.dirname(os.path.abspath(__file__))

app = typer.Typer(no_args_is_help=True, add_help_option=False)

yaml_components = typer.Typer(no_args_is_help=True, add_help_option=False)

app.add_typer(yaml_components, name="components")


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
    return pytest.main(
        ['-v', '-p no:warnings', f'{rootdir}/components'])


@yaml_components.command()
def component():
    """
    Run pytest with tests that affect each component separately
    """
    return pytest.main(
        ['-v', '-p no:warnings', f'{rootdir}/components/test_component.py'])


@yaml_components.command()
def components():
    """
    Run pytest with tests that affect all components at the same time
    """
    return pytest.main(
        ['-v', '-p no:warnings', f'{rootdir}/components/test_all_components.py'])
