from typing import Annotated

import typer
from rich import print
from rich.table import Table

from isra.src.v2.component2 import read_current_component, write_current_component
from isra.src.config.config import get_resource
from isra.src.v2.constants2 import OPENCRE_PLUS, CRE_MAPPING_NAME

app = typer.Typer(no_args_is_help=True, add_help_option=False)


def expand_init():
    template = read_current_component()

    mappings_yaml = get_resource(OPENCRE_PLUS)

    for control in template.get_controls():
        control_ref = control.get_ref()
        # Set a empty list to start from a blank state
        control.set_standards([])
        # Get the baseline standard that should have been set
        try:
            assert control.get_base_standard().get_ref() != "", "Empty base standard"
            assert len(control.get_base_standard().get_sections()) > 0, "Empty base standard section"
        except AssertionError as e:
            print(f"Control {control_ref} error: {e}. Skipping...")
            continue

        baseline_ref = control.get_base_standard().get_ref()
        baseline_sections = control.get_base_standard().get_sections()
        baseline_ref_opencre = CRE_MAPPING_NAME[baseline_ref]

        for baseline_section in baseline_sections:
            # Now we are looking for the base standard in the OpenCRE+, so we need to use the name that is in the file
            print(f"{control_ref}: [yellow]Looking for {baseline_ref_opencre} - {baseline_section}")

            # If OpenCRE+ contains the base standard and section we'll include the other standards related
            # Now we iterate over the OpenCRE+ keys searching for the standard
            for cre_id, cre_values in mappings_yaml.items():
                if baseline_ref_opencre in cre_values:
                    # Now it may happen that the section doesn't appear exactly as it is in the OpenCRE+, so we
                    # apply special techniques to look for the best match
                    if baseline_section in cre_values[baseline_ref_opencre]:
                        control.add_standard("CRE", cre_id)
                        print(f"Added [green]CRE[/green] -> [blue]{cre_id}")
                        for k, v in cre_values.items():
                            for elem in v:
                                control.add_standard(k, elem)
                                print(f"Added [green]{k}[/green] -> [blue]{elem}")

        if len(control.get_standards()) == 0:
            print(f"[red]Nothing found in OpenCRE+. Added base standard")
            for baseline_section in baseline_sections:
                control.add_standard(baseline_ref_opencre, baseline_section)
                print(f"Added [green]{baseline_ref_opencre}[/green] -> [blue]{baseline_section}")

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
