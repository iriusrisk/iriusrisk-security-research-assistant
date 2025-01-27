import os.path

from typing_extensions import Annotated

from rich import print

from isra.src.component.component import balance_mitigation_values_process, restart_component, create_new_component, \
    create_threat_model, save_yaml, load_init
from isra.src.component.template import check_current_component
from isra.src.screening.screening_service import autoscreening_init, set_default_baseline_standard, fix_mitre_values, \
    fix_component, custom_fix_component
from isra.src.standards.standards import expand_process
from isra.src.utils.api_functions import add_to_batch

from isra.src.utils.xml_functions import *
from isra.src.utils.yaml_functions import load_yaml_file

app = typer.Typer(no_args_is_help=True, add_help_option=False)


@app.command()
def build(file: Annotated[str, typer.Option(help="Path to file to import")] = None):
    """Creates release"""

    components_dir = get_property("components_dir") or get_app_dir()
    file_list = []
    if file:
        with open(file, "r") as f:
            for line in f.read().splitlines():
                file_list.append(line)
    else:
        for root, dirs, files in os.walk(components_dir):
            for file in files:
                if file.endswith(".yaml") and "to_review" not in root and ".git" not in root:
                    file_list.append(os.path.join(root, file))

    for file in file_list:
        try:
            print(f"Reading {file}")
            template = load_yaml_file(file)
            template = balance_mitigation_values_process(template)
            template = expand_process(template)
            add_to_batch(template)
            print(f"Component {template['component']['ref']} added to batch successfully")
        except Exception as e:
            print(f"An error happened when adding the component to batch: {e}")


# Experimental functions


@app.command()
def auto():
    """
    Creates a component automatically
    """
    with open("hardware.txt", "r") as f:
        components = f.read().splitlines()

        for c in components:
            if check_current_component(raise_if_not_exists=False) != "":
                restart_component(remove_temporal_component=True)
            create_new_component(c, "", f.name.replace(".txt", ""))
            create_threat_model(reuse_threat_model=False)
            autoscreening_init(force=True)
            set_default_baseline_standard("NIST 800-53 v5")
            fix_mitre_values()
            save_yaml(preview=False)


@app.command()
def fix():
    """Fixes component"""

    components_dir = get_property("components_dir") or get_app_dir()
    file_list = []

    for root, dirs, files in os.walk(components_dir):
        for file in files:
            if file.endswith(".yaml") and "to_review" not in root and ".git" not in root:
                file_list.append(os.path.join(root, file))

    for file in file_list:
        try:
            print(f"Reading {file}")
            if check_current_component(raise_if_not_exists=False) != "":
                restart_component(remove_temporal_component=True)
            load_init(file)
            fix_mitre_values()
            save_yaml(preview=False)
            print(f"Component fixed successfully")
        except Exception as e:
            print(f"An error happened when fixing the component: {e}")


@app.command()
def fix2():
    """Fixes component"""


    try:
        custom_fix_component()

        print(f"Component fixed successfully")
    except Exception as e:
        print(f"An error happened when fixing the component: {e}")