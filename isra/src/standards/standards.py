import os
import uuid
from typing import Annotated

import pandas as pd
import typer
from rich import print
from rich.table import Table

from isra.src.component.component import read_current_component, write_current_component
from isra.src.config.config import get_resource
from isra.src.config.constants import OPENCRE_PLUS, CRE_MAPPING_NAME, CUSTOM_FIELD_STANDARD_BASELINE_REF, \
    CUSTOM_FIELD_STANDARD_BASELINE_SECTION
from isra.src.utils.gpt_functions import get_prompt, query_chatgpt

app = typer.Typer(no_args_is_help=True, add_help_option=False)


def extract_standard_from_table(text):
    messages = [
        {"role": "system",
         "content": get_prompt("extract_standard_from_table.md")},
        {"role": "user", "content": text}
    ]

    return query_chatgpt(messages)


def set_standard_on_components(standard_ref, table):
    print(standard_ref)
    print(table)

    template = read_current_component()

    try:
        df = pd.read_excel(table)

        # Validate DataFrame structure
        required_columns = ['ID', 'Name', 'Description']
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            print(f"Error: Missing required columns: {', '.join(missing_columns)}")
            print("The Excel file must contain a table with the following columns: ID, Name, Description")
            raise typer.Exit(-1)

    except Exception as e:
        print(
            "Couldn't read Excel file. Ensure that the file only has one sheet and a table with the following columns: ID, Name, Description")
        raise typer.Exit(-1)

    for control_ref, control in template["controls"].items():
        control_name = control["name"]
        print(f"{control_ref}: {control_name}")
        control_desc = control["desc"]

        control_part = f"<countermeasure>Name:{control_name}{os.linesep}Description:{control_desc}</countermeasure>"
        # Convert DataFrame rows to string format for the table part
        table_content = df.apply(
            lambda row: f"ID:{row['ID']}{os.linesep}Name:{row['Name']}{os.linesep}Description:{row['Description']}",
            axis=1)
        table_part = f"<table>{os.linesep.join(table_content)}</table>"

        result = extract_standard_from_table(control_part + table_part)

        # Validate that the extracted ID exists in the DataFrame
        if result not in df['ID'].values:
            print(f"Warning: Extracted ID '{result}' not found in the table for control {control_ref}")
            continue

        # Get the Name associated with the ID
        standard_name = df[df['ID'] == result]['Name'].iloc[0]
        print(f"Result: {result} - {standard_name}")

        control["standards"].append({
            "standard-ref": standard_ref,
            "standard-section": result
        })

    write_current_component(template)


def get_standard_from_opencre(mappings_yaml, baseline_ref, base_standard_section):
    opencre_standard_name = CRE_MAPPING_NAME[baseline_ref]

    # If OpenCRE+ contains the base standard and section we'll include the other standards related
    standards_to_add = dict()
    # By default, CRE is included in the dict but we haven't found any valid CRE yet

    # Now we iterate over the OpenCRE+ keys searching for the standard
    for cre_id, cre_values in mappings_yaml.items():
        if opencre_standard_name in cre_values:
            # Now it may happen that the section doesn't appear exactly as it is in the OpenCRE+, so we
            # apply special techniques to look for the best match
            adapted = base_standard_section

            if adapted in cre_values[opencre_standard_name]:
                # If the section of the standard can be found inside the CRE we add all values
                # of that standard and the CRE ID
                standards_to_add.update(cre_values)
                if "CRE" not in standards_to_add:
                    standards_to_add["CRE"] = set()
                standards_to_add["CRE"].add(cre_id)

                # At this point we have a dictionary of the standards that have to be added in this control
    # We convert the lists to sets to remove duplicates
    standards_to_add = {key: set(value) for key, value in standards_to_add.items()}

    return standards_to_add


def expand_process(template, verbose=False):
    mappings_yaml = get_resource(OPENCRE_PLUS)

    # First, get all standard names that appear in OpenCRE+
    opencre_standards = {'CRE'}
    for cre_values in mappings_yaml.values():
        opencre_standards.update(cre_values.keys())

    for control_ref, control in template["controls"].items():
        # Instead of clearing the list, filter out standards from OpenCRE+
        if "standards" in control:
            control["standards"] = [
                std for std in control["standards"]
                if std["standard-ref"] not in opencre_standards
            ]
        else:
            control["standards"] = list()

        # Get the baseline standard that should have been set
        try:
            assert CUSTOM_FIELD_STANDARD_BASELINE_REF in control["customFields"], "No base standard"
            assert control["customFields"][CUSTOM_FIELD_STANDARD_BASELINE_REF] != "", "Empty base standard"
            assert CUSTOM_FIELD_STANDARD_BASELINE_SECTION in control["customFields"], "No base standard section"
            assert control["customFields"][CUSTOM_FIELD_STANDARD_BASELINE_SECTION] != "", "Empty base standard section"
        except AssertionError as e:
            print(f"Control {control_ref} error: {e}. Skipping...")
            continue

        baseline_ref = control["customFields"][CUSTOM_FIELD_STANDARD_BASELINE_REF]
        baseline_sections = control["customFields"][CUSTOM_FIELD_STANDARD_BASELINE_SECTION].split("||")

        for base_standard_sections in baseline_sections:

            standards_to_add = get_standard_from_opencre(mappings_yaml, baseline_ref, base_standard_sections)

            # If no standards have been found we add the base standard by default
            if len(standards_to_add) == 0:
                for section in base_standard_sections.split("||"):
                    # This line is to remove duplicates in case the same base standard section is added twice
                    current_list = [x["standard-ref"] + x["standard-section"] for x in control["standards"]]
                    if CRE_MAPPING_NAME[baseline_ref] + section not in current_list:
                        control["standards"].append({
                            "standard-ref": CRE_MAPPING_NAME[baseline_ref],
                            "standard-section": section
                        })
                if verbose:
                    print(f"[red]Nothing found in OpenCRE+. Added base standard")
            else:
                for standard_ref, sections in standards_to_add.items():
                    for section in sections:
                        current_list = [x["standard-ref"] + x["standard-section"] for x in control["standards"]]
                        if standard_ref + section not in current_list:
                            control["standards"].append({
                                "standard-ref": standard_ref,
                                "standard-section": section
                            })
                            if verbose:
                                print(f"Added [green]{standard_ref}[/green] -> [blue]{section}")

    return template


def reset_process(template):
    for control_ref, control in template["controls"].items():
        control["standards"] = list()

    return template


def expand_init(verbose):
    template = read_current_component()
    template = expand_process(template, verbose)
    write_current_component(template)


def reset_init():
    template = read_current_component()
    template = reset_process(template)
    write_current_component(template)


def show_init(standard_name, standard_section):
    table = Table("OpenCRE ID", "Standard", "Section")

    mappings_yaml = get_resource(OPENCRE_PLUS)
    for k, v in mappings_yaml.items():
        for k2, v2 in v.items():
            if standard_name.lower() in k2.lower():
                li = [x.lower() for x in v2]
                if any(standard_section.lower() in s for s in li):
                    table.add_row(k, k2, str(sorted(v2)))
    print(table)
    print("This table shows the standards that will be included using OpenCRE as the link standard")
    print("For example, if the countermeasure's base standard is related with ASVS V5.2.3 it will find all the "
          "OpenCRE IDs related with that, and proceed to import every other standard related")
    print("In this example ASVS V5.2.3 is currently related with OpenCRE ID 881-434, so it will also add CWE-147 to "
          "the countermeasure and many others")


def test_standard(standard_name, standard_section):
    mappings_yaml = get_resource(OPENCRE_PLUS)

    standards_to_add = get_standard_from_opencre(mappings_yaml, standard_name, standard_section)
    for k, v in standards_to_add.items():
        for val in v:
            random_uuid = uuid.uuid4()
            print(f'<standard uuid="{random_uuid}" ref="{val}" supportedStandardRef="{k}"/>')


@app.callback()
def callback():
    """
    Standard mapping processes
    """


@app.command()
def expand(verbose: Annotated[bool, typer.Option(help="Verbose (True/False)")] = False):
    """
    This function will expand the standard set of a countermeasure by using the base standard
    """
    expand_init(verbose)


@app.command()
def reset():
    """
    This function will expand the standard set of a countermeasure by using the base standard
    """
    reset_init()


@app.command()
def test(standard_name: Annotated[str, typer.Option(help="Filter by standard name")] = "",
         standard_section: Annotated[str, typer.Option(help="Filter by standard section")] = ""):
    """
    Shows the current standard mapping used to propagate standards
    """
    test_standard(standard_name, standard_section)


@app.command()
def show(standard_name: Annotated[str, typer.Option(help="Filter by standard name")] = "",
         standard_section: Annotated[str, typer.Option(help="Filter by standard section")] = ""):
    """
    Shows the current standard mapping used to propagate standards
    """
    show_init(standard_name, standard_section)
