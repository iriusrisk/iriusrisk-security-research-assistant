import os.path
import sys
import time
from pathlib import Path

from typing_extensions import Annotated

from rich import print

from isra.src.component.component import balance_mitigation_values_process, restart_component, create_new_component, \
    create_threat_model, save_yaml, load_init
from isra.src.component.template import check_current_component
from isra.src.config.constants import SYSTEM_LIBRARY_REFERENCE_IDS, V1_LIBRARIES
from isra.src.screening.screening_service import autoscreening_init, set_default_baseline_standard, fix_mitre_values, \
    fix_component, custom_fix_component
from isra.src.standards.standards import expand_process, set_standard_on_components
from isra.src.utils.api_functions import add_to_batch, get_all_libraries, get_all_libraries_paginated, \
    get_export_library_xml, get_library_by_reference_id, import_library_xml

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

    xml_files = sorted(xml_files)
    expected_library_refs = {}
    for xml_file in xml_files:
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

    start_time = time.time()
    log_path = Path(libraries_dir) / f"import_libraries_report_{time.strftime('%Y%m%d_%H%M%S')}.log"
    log_file = open(log_path, "w", encoding="utf-8")
    last_status_len = 0
    status_active = False

    def clear_status_line():
        nonlocal last_status_len, status_active
        if status_active and last_status_len:
            sys.stdout.write("\r" + (" " * last_status_len) + "\r")
            sys.stdout.flush()
        status_active = False
        last_status_len = 0

    def log(message: str):
        clear_status_line()
        print(message)
        log_file.write(message + "\n")
        log_file.flush()

    def log_inline(message: str):
        nonlocal last_status_len, status_active
        status_active = True
        effective_len = len(message)
        if effective_len < last_status_len:
            message = message + (" " * (last_status_len - effective_len))
        sys.stdout.write("\r" + message)
        sys.stdout.flush()
        last_status_len = max(last_status_len, effective_len)

    import_failures = []
    import_successes = []
    max_attempts = 30
    wait_seconds = 3

    def wait_for_library(reference_id: str):
        attempts_used = 0
        for attempt in range(1, max_attempts + 1):
            attempts_used = attempt
            try:
                if get_library_by_reference_id(reference_id, silent=True) is not None:
                    clear_status_line()
                    return True, attempts_used
            except Exception:
                pass

            if attempt < max_attempts:
                log_inline(f"Waiting for {reference_id} to appear (attempt {attempt}/{max_attempts})...")
                time.sleep(wait_seconds)
        clear_status_line()
        return False, attempts_used

    log(f"Importing {len(xml_files)} libraries from {libraries_dir}")
    log(f"Log file: {log_path}")

    for index, xml_file in enumerate(xml_files, start=1):
        remaining = len(xml_files) - index
        log(f"Importing {xml_file} ({index}/{len(xml_files)}, remaining {remaining})")
        try:
            import_response = import_library_xml(xml_file)
            expected_ref = expected_library_refs.get(xml_file)
            if expected_ref:
                found, attempts_used = wait_for_library(expected_ref)
            else:
                found, attempts_used = False, 0

            if found:
                import_successes.append(xml_file)
                log(f"Library imported successfully: {xml_file} (attempts {attempts_used}/{max_attempts})")
            else:
                import_failures.append(xml_file)
                log(f"Library import did not complete in time: {xml_file} (attempts {attempts_used}/{max_attempts})")
                if import_response is not None:
                    log(f"Import response: {import_response}")
        except Exception as e:
            import_failures.append(xml_file)
            log(f"An error happened when importing {xml_file}: {e}")

    excluded_refs = SYSTEM_LIBRARY_REFERENCE_IDS
    expected_refs = sorted(
        ref for ref in set(expected_library_refs.values())
        if ref not in excluded_refs
    )
    remaining_refs = []

    if expected_refs:
        try:
            log("Verifying libraries in IriusRisk...")
            remaining_refs = expected_refs
            verify_attempts = 5
            wait_seconds = 2

            for attempt in range(1, verify_attempts + 1):
                libraries = get_all_libraries_paginated(silent=True)
                existing_refs = {library.get("referenceId") for library in libraries}
                remaining_refs = [ref for ref in expected_refs if ref not in existing_refs]

                if not remaining_refs:
                    break

                if attempt < verify_attempts:
                    log_inline(
                        f"Waiting for {len(remaining_refs)} libraries to appear "
                        f"(attempt {attempt}/{verify_attempts})..."
                    )
                    time.sleep(wait_seconds)

            clear_status_line()
            if not remaining_refs:
                log("Verification successful: all libraries are present in IriusRisk.")
            else:
                log("Verification incomplete: some libraries are still missing in IriusRisk.")
                for ref in remaining_refs:
                    file_match = next(
                        (file for file, expected_ref in expected_library_refs.items() if expected_ref == ref),
                        None,
                    )
                    if file_match:
                        log(f"- {ref} (file: {file_match})")
                    else:
                        log(f"- {ref}")

            if import_failures:
                log("Imports with errors (may explain missing libraries):")
                for xml_file in import_failures:
                    log(f"- {xml_file}")
        except Exception as e:
            log(f"An error happened when verifying libraries: {e}")

    end_time = time.time()
    duration_seconds = int(end_time - start_time)

    log("Execution summary:")
    log(f"- Total libraries found: {len(xml_files)}")
    log(f"- Imported successfully: {len(import_successes)}")
    log(f"- Failed imports: {len(import_failures)}")
    log(f"- Missing after verification: {len(remaining_refs)}")
    log(f"- Duration: {duration_seconds} seconds")
    log(f"- Report file: {log_path}")

    log_file.close()


@app.command()
def export_libraries(
        libraries_dir: Annotated[str, typer.Option(help="Folder to create and store exported XML libraries")] = ""):
    """Exports all XML libraries from IriusRisk into the specified folder"""

    if libraries_dir == "":
        libraries_dir = get_property("libraries_dir") or get_app_dir()

    if libraries_dir == "":
        print("Help: isra srt export-libraries --libraries-dir /path/to/libraries")
        raise typer.Exit(-1)

    libraries_base = Path(libraries_dir)
    v1_folder = libraries_base / "v1"
    v2_folder = libraries_base / "v2"

    for folder in (libraries_base, v1_folder, v2_folder):
        os.makedirs(folder, exist_ok=True)

    start_time = time.time()
    try:
        libraries = get_all_libraries_paginated()
    except Exception as e:
        print(f"An error happened when fetching the libraries: {e}")
        raise typer.Exit(-1)

    excluded_refs = SYSTEM_LIBRARY_REFERENCE_IDS
    libraries = [lib for lib in libraries if lib.get("referenceId") not in excluded_refs]

    if not libraries:
        print("There are no libraries to export.")
        return

    total_libraries = len(libraries)
    print(f"Found {total_libraries} libraries to export")

    downloaded = 0
    download_failures = []

    for index, library in enumerate(libraries, start=1):
        reference_id = library.get("referenceId")
        library_id = library.get("id")

        if not reference_id or not library_id:
            print(f"Skipping library with missing identifiers: {library}")
            continue

        remaining = total_libraries - index
        print(f"Downloading {reference_id} ({index}/{total_libraries}, remaining {remaining})")

        try:
            xml_content = get_export_library_xml(library)
            if reference_id in V1_LIBRARIES:
                output_path = v1_folder / V1_LIBRARIES[reference_id]
            else:
                output_path = v2_folder / f"{reference_id}.xml"

            with open(output_path, "wb") as f:
                f.write(xml_content)
            downloaded += 1
        except Exception as e:
            print(f"Couldn't export library {reference_id}: {e}")
            download_failures.append(reference_id)

    expected_files = []
    expected_refs = []
    for lib in libraries:
        ref = lib.get("referenceId")
        if not ref:
            continue
        expected_refs.append(ref)
        if ref in V1_LIBRARIES:
            expected_files.append(v1_folder / V1_LIBRARIES[ref])
        else:
            expected_files.append(v2_folder / f"{ref}.xml")

    missing_files = [path for path in expected_files if not path.exists()]

    if not missing_files:
        print("Verification successful: all expected library files were downloaded.")
    else:
        print("Verification incomplete: some expected library files are missing locally.")
        for path in missing_files:
            print(f"- {path}")

    api_missing_refs = []
    try:
        api_libraries = get_all_libraries_paginated(silent=True)
        api_refs = {
            lib.get("referenceId")
            for lib in api_libraries
            if lib.get("referenceId") not in SYSTEM_LIBRARY_REFERENCE_IDS
        }
        downloaded_refs = set(expected_refs)
        api_missing_refs = sorted(api_refs - downloaded_refs)
    except Exception as e:
        print(f"Verification warning: failed to fetch libraries from API: {e}")

    if not api_missing_refs:
        print("Verification successful: all API-registered libraries were downloaded.")
    else:
        print("Verification incomplete: some API-registered libraries were not downloaded.")
        for ref in api_missing_refs:
            print(f"- {ref}")

    duration_seconds = int(time.time() - start_time)
    print("Execution summary:")
    print(f"- Total libraries expected: {total_libraries}")
    print(f"- Downloaded successfully: {downloaded}")
    print(f"- Download failures: {len(download_failures)}")
    print(f"- Missing files after verification: {len(missing_files)}")
    print(f"- Missing API libraries after verification: {len(api_missing_refs)}")
    print(f"- Duration: {duration_seconds} seconds")
