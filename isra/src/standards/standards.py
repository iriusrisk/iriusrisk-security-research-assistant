from typing import Annotated

import typer
from rich import print
from rich.table import Table

from isra.src.component.component import read_current_component, write_current_component
from isra.src.config.config import get_resource
from isra.src.config.constants import OPENCRE_PLUS, CRE_MAPPING_NAME, CUSTOM_FIELD_STANDARD_BASELINE_REF, \
    CUSTOM_FIELD_STANDARD_BASELINE_SECTION

app = typer.Typer(no_args_is_help=True, add_help_option=False)


def expand_process(template, verbose=False):

    mappings_yaml = get_resource(OPENCRE_PLUS)

    for control_ref, control in template["controls"].items():
        # Set a empty list to start from a blank state
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

            # Now we are looking for the base standard in the OpenCRE+, so we need to use the name that is in the file
            opencre_standard_name = CRE_MAPPING_NAME[baseline_ref]
            if verbose:
                print(f"{control_ref}: [yellow]Looking for {opencre_standard_name} - {base_standard_sections}")

            # If OpenCRE+ contains the base standard and section we'll include the other standards related
            standards_to_add = dict()
            # By default, CRE is included in the dict but we haven't found any valid CRE yet

            # Now we iterate over the OpenCRE+ keys searching for the standard
            for cre_id, cre_values in mappings_yaml.items():
                if opencre_standard_name in cre_values:
                    # Now it may happen that the section doesn't appear exactly as it is in the OpenCRE+, so we
                    # apply special techniques to look for the best match
                    adapted = base_standard_sections

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

def expand_init():
    template = read_current_component()
    template = expand_process(template)
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


@app.callback()
def callback():
    """
    Standard mapping processes
    """


@app.command()
def expand():
    """
    This function will expand the standard set of a countermeasure by using the base standard
    """
    expand_init()


@app.command()
def show(standard_name: Annotated[str, typer.Option(help="Filter by standard name")] = "",
         standard_section: Annotated[str, typer.Option(help="Filter by standard section")] = ""):
    """
    Shows the current standard mapping used to propagate standards
    """
    show_init(standard_name, standard_section)
