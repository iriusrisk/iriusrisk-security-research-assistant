import os.path
import time

from typing_extensions import Annotated

from rich import print

from isra.src.component.component import balance_mitigation_values_process, restart_component, create_new_component, \
    create_threat_model, save_yaml, load_init
from isra.src.component.template import check_current_component
from isra.src.config.constants import SYSTEM_LIBRARY_REFERENCE_IDS
from isra.src.screening.screening_service import autoscreening_init, set_default_baseline_standard, fix_mitre_values, \
    fix_component, custom_fix_component
from isra.src.standards.standards import expand_process, set_standard_on_components
from isra.src.utils.api_functions import add_to_batch, get_all_libraries, import_library_xml

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
    with open("functional.txt", "r") as f:
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


@app.command()
def standards(standard_ref: Annotated[str, typer.Option(help="Standard ref")] = "",
              table: Annotated[str, typer.Option(help="Excel file containing the standards to import")] = ""):   
    """Imports standards from an Excel file and applies them to the YSC files in the given folder"""

    if standard_ref == "" or table == "":
        print("Help: isra srt standards --standard-ref custom_ref --table /path/to/excel/file.xlsx")
        raise typer.Exit(-1)

    try:
        set_standard_on_components(standard_ref, table)

        print(f"Standard added successfully")
    except Exception as e:
        print(f"An error happened when fixing the component: {e}")

@app.command()
def libraries():
    """Get all IriusRisk libraries registered in IriusRisk (useful to check IriusRisk API connectivity)"""
    
    try:
        libraries = get_all_libraries()
        print(f"Libraries registered in IriusRisk:")
        excluded_refs = SYSTEM_LIBRARY_REFERENCE_IDS
        for library in libraries:
            if library.get("referenceId") in excluded_refs:
                continue
            print(f"- {library['name']} (ref: {library['referenceId']})")
        visible_libraries = [
            library for library in libraries
            if library.get("referenceId") not in excluded_refs
        ]
        print(f"Total libraries: {len(visible_libraries)}")

    except Exception as e:
        print(f"An error happened when fetching the libraries: {e}")


@app.command()
def import_libraries(
        libraries_dir: Annotated[str, typer.Option(help="Folder containing XML libraries")] = ""):
    """Imports all XML libraries found in the libraries_dir folder into IriusRisk"""

    if libraries_dir == "":
        libraries_dir = get_property("libraries_dir") or get_app_dir()

    if libraries_dir == "":
        print("Help: isra srt import-libraries --libraries-dir /path/to/libraries")
        raise typer.Exit(-1)

    if not os.path.isdir(libraries_dir):
        print(f"Libraries directory not found: {libraries_dir}")
        raise typer.Exit(-1)

    xml_files = []
    for root, dirs, files in os.walk(libraries_dir):
        for file in files:
            if file.endswith(".xml"):
                xml_files.append(os.path.join(root, file))

    if len(xml_files) == 0:
        print(f"No XML libraries found in {libraries_dir}")
        raise typer.Exit(-1)

    expected_library_refs = {}
    for xml_file in sorted(xml_files):
        reference_id = None
        try:
            tree = etree.parse(xml_file)
            root = tree.getroot()
            reference_id = root.attrib.get("ref")
        except Exception:
            reference_id = None

        if not reference_id:
            reference_id = os.path.splitext(os.path.basename(xml_file))[0]

        expected_library_refs[xml_file] = reference_id

    import_failures = []
    for xml_file in sorted(xml_files):
        try:
            print(f"Importing {xml_file}")
            import_library_xml(xml_file)
            print(f"Library imported successfully: {xml_file}")
        except Exception as e:
            print(f"An error happened when importing {xml_file}: {e}")
            import_failures.append(xml_file)

    excluded_refs = SYSTEM_LIBRARY_REFERENCE_IDS
    expected_refs = sorted(
        ref for ref in set(expected_library_refs.values())
        if ref not in excluded_refs
    )
    if not expected_refs:
        return

    try:
        print("Verifying libraries in IriusRisk...")
        remaining_refs = expected_refs
        max_attempts = 5
        wait_seconds = 2

        for attempt in range(1, max_attempts + 1):
            libraries = get_all_libraries()
            existing_refs = {library.get("referenceId") for library in libraries}
            remaining_refs = [ref for ref in expected_refs if ref not in existing_refs]

            if not remaining_refs:
                break

            if attempt < max_attempts:
                print(
                    f"Waiting for {len(remaining_refs)} libraries to appear "
                    f"(attempt {attempt}/{max_attempts})..."
                )
                time.sleep(wait_seconds)

        if not remaining_refs:
            print("Verification successful: all libraries are present in IriusRisk.")
        else:
            print("Verification incomplete: some libraries are still missing in IriusRisk.")
            for ref in remaining_refs:
                file_match = next(
                    (file for file, expected_ref in expected_library_refs.items() if expected_ref == ref),
                    None,
                )
                if file_match:
                    print(f"- {ref} (file: {file_match})")
                else:
                    print(f"- {ref}")

        if import_failures:
            print("Imports with errors (may explain missing libraries):")
            for xml_file in import_failures:
                print(f"- {xml_file}")
    except Exception as e:
        print(f"An error happened when verifying libraries: {e}")
