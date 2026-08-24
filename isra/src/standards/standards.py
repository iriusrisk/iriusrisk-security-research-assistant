import csv
import io
import os
import uuid
from collections import defaultdict
from enum import Enum
from pathlib import Path
from typing import Annotated, Optional

import pandas as pd
import typer
import yaml
from rich import print
from rich.table import Table

from isra.src.component.component import read_current_component, write_current_component
from isra.src.config.config import get_resource
from isra.src.config.constants import OPENCRE_PLUS, CRE_MAPPING_NAME, CUSTOM_FIELD_STANDARD_BASELINE_REF, \
    CUSTOM_FIELD_STANDARD_BASELINE_SECTION, OUTPUT_NAME
from isra.src.utils.gpt_functions import get_prompt, query_chatgpt

app = typer.Typer(no_args_is_help=True, add_help_option=False)


class CoverageReportFormat(str, Enum):
    markdown = "markdown"
    csv = "csv"


def _standard_ref(mapping_name):
    """Return the IriusRisk standard ref used in component repositories."""
    return OUTPUT_NAME.get(mapping_name, {}).get("ref", mapping_name)


def _requested_standards(std_refs, mappings_yaml):
    refs = [ref.strip() for ref in std_refs.split(",") if ref.strip()]
    if not refs:
        raise typer.BadParameter("Provide at least one comma-separated standard ref", param_hint="--std-refs")

    mapping_names = {name for values in mappings_yaml.values() for name in values}
    aliases = {name: name for name in mapping_names}
    aliases.update({_standard_ref(name): name for name in mapping_names})

    unknown = [ref for ref in refs if ref not in aliases]
    if unknown:
        raise typer.BadParameter(
            f"Unknown standard ref(s): {', '.join(unknown)}",
            param_hint="--std-refs"
        )

    # Preserve input order while removing duplicates.
    return list(dict.fromkeys((_standard_ref(aliases[ref]), aliases[ref]) for ref in refs))


def _countermeasure_standards(countermeasure, mappings_yaml, expansion_cache=None):
    """Get explicit and OpenCRE-expanded standards without modifying the component."""
    standards = defaultdict(set)
    for name, sections in (countermeasure.get("standards") or {}).items():
        for section in sections or []:
            standards[_standard_ref(name)].add(str(section))

    baseline_ref = countermeasure.get("base_standard", "")
    baseline_sections = countermeasure.get("base_standard_section") or []
    if isinstance(baseline_sections, str):
        baseline_sections = baseline_sections.split("||")

    if baseline_ref not in CRE_MAPPING_NAME:
        return standards

    for section in baseline_sections:
        cache_key = (baseline_ref, str(section))
        if expansion_cache is not None and cache_key in expansion_cache:
            expanded = expansion_cache[cache_key]
        else:
            expanded = get_standard_from_opencre(mappings_yaml, *cache_key)
            if expansion_cache is not None:
                expansion_cache[cache_key] = expanded
        if not expanded:
            expanded = {CRE_MAPPING_NAME[baseline_ref]: {str(section)}}
        for name, mapped_sections in expanded.items():
            for mapped_section in mapped_sections:
                standards[_standard_ref(name)].add(str(mapped_section))
    return standards


def collect_standard_coverage(component_repo, requested_standards, mappings_yaml):
    """Collect matching standard sections from every YAML component in a repository."""
    coverage = defaultdict(list)
    requested_refs = {ref for ref, _ in requested_standards}
    expansion_cache = {}
    total_components = 0
    category_totals = defaultdict(int)

    component_paths = sorted(component_repo.rglob("*.yaml")) + sorted(component_repo.rglob("*.yml"))
    for component_path in component_paths:
        try:
            with component_path.open("r", encoding="utf8") as component_file:
                # CSafeLoader has the same safe semantics and is substantially faster
                # for repositories containing many large component files.
                loader = getattr(yaml, "CSafeLoader", yaml.SafeLoader)
                document = yaml.load(component_file, Loader=loader)
        except (OSError, yaml.YAMLError) as exc:
            raise typer.BadParameter(
                f"Could not read YAML '{component_path}': {exc}",
                param_hint="--yaml-component-repo"
            ) from exc

        # Component repositories can also contain CI workflows and other YAML metadata.
        if not isinstance(document, dict) or "component" not in document:
            continue
        component = document["component"]
        if not isinstance(component, dict):
            raise typer.BadParameter(
                f"Invalid component node in '{component_path}'",
                param_hint="--yaml-component-repo"
            )
        total_components += 1
        category = str(component.get("category", "uncategorized"))
        category_totals[category] += 1
        risk_pattern = component.get("risk_pattern") or {}

        countermeasure_matches = defaultdict(lambda: defaultdict(set))
        for threat in risk_pattern.get("threats") or []:
            for countermeasure in threat.get("countermeasures") or []:
                standards = _countermeasure_standards(countermeasure, mappings_yaml, expansion_cache)
                countermeasure_ref = str(countermeasure.get("ref") or "(missing ref)")
                for standard_ref in requested_refs:
                    sections = standards.get(standard_ref, set())
                    if sections:
                        countermeasure_matches[countermeasure_ref][standard_ref].update(sections)

        if countermeasure_matches:
            coverage[category].append({
                "ref": str(component.get("ref", component_path.stem)),
                "name": str(component.get("name", component_path.stem)).strip(),
                "countermeasures": countermeasure_matches,
            })

    return coverage, total_components, category_totals


def render_coverage_report(coverage, requested_standards, component_repo, total_components, category_totals):
    component_count = sum(len(components) for components in coverage.values())
    lines = [
        "# Security standards coverage report",
        "",
        f"Component repository: `{component_repo}`",
        "",
        "Requested standards: " + ", ".join(f"`{ref}`" for ref, _ in requested_standards),
        "",
        f"Matching components: **{component_count} of {total_components}**",
        "",
        "## Coverage by category",
        "",
        "| Component category | Matching components | Total components |",
        "|---|---:|---:|",
    ]

    for category in sorted(category_totals, key=str.casefold):
        escaped_category = category.replace("|", "\\|")
        lines.append(
            f"| {escaped_category} | {len(coverage.get(category, []))} | {category_totals[category]} |"
        )
    lines.append("")

    if not coverage:
        lines.extend(["No components cover any of the requested standards.", ""])
        return "\n".join(lines)

    for category in sorted(coverage, key=str.casefold):
        lines.extend([f"## {category}", ""])
        for component in sorted(coverage[category], key=lambda item: (item["name"].casefold(), item["ref"])):
            name = component["name"].replace("|", "\\|")
            ref = component["ref"].replace("|", "\\|")
            lines.extend([
                f"### {name} (`{ref}`)",
                "",
                "| Countermeasure ref | " + " | ".join(ref for ref, _ in requested_standards) + " |",
                "|---|" + "---|" * len(requested_standards),
            ])
            for countermeasure_ref in sorted(component["countermeasures"]):
                standard_matches = component["countermeasures"][countermeasure_ref]
                cells = []
                for standard_ref, _ in requested_standards:
                    sections = sorted(standard_matches.get(standard_ref, set()))
                    cells.append(
                        "<br>".join(section.replace("|", "\\|") for section in sections) or "—"
                    )
                escaped_countermeasure_ref = countermeasure_ref.replace("|", "\\|")
                lines.append(f"| `{escaped_countermeasure_ref}` | " + " | ".join(cells) + " |")
            lines.append("")
    return "\n".join(lines)


def render_coverage_csv(coverage, requested_standards, total_components, category_totals):
    """Render one CSV row per matching countermeasure."""
    output = io.StringIO(newline="")
    writer = csv.writer(output)
    matching_components = sum(len(components) for components in coverage.values())
    writer.writerow([
        "repository_matching_components",
        "repository_total_components",
        "component_category",
        "category_matching_components",
        "category_total_components",
        "component_name",
        "component_ref",
        "countermeasure_ref",
        *(ref for ref, _ in requested_standards),
    ])

    for category in sorted(coverage, key=str.casefold):
        category_matching_components = len(coverage[category])
        for component in sorted(coverage[category], key=lambda item: (item["name"].casefold(), item["ref"])):
            for countermeasure_ref in sorted(component["countermeasures"]):
                standard_matches = component["countermeasures"][countermeasure_ref]
                writer.writerow([
                    matching_components,
                    total_components,
                    category,
                    category_matching_components,
                    category_totals[category],
                    component["name"],
                    component["ref"],
                    countermeasure_ref,
                    *(
                        "; ".join(sorted(standard_matches.get(standard_ref, set())))
                        for standard_ref, _ in requested_standards
                    ),
                ])
    return output.getvalue()


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
    if standard_name not in CRE_MAPPING_NAME:
        supported_names = ", ".join(sorted(CRE_MAPPING_NAME))
        raise typer.BadParameter(
            f"Unknown baseline standard '{standard_name}'. Supported names: {supported_names}",
            param_hint="--standard-name"
        )

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
    Removes all standards from every countermeasure in the current component
    """
    reset_init()


@app.command()
def test(
    standard_name: Annotated[str, typer.Option(help="Baseline standard name (for example: ASVS)")],
    standard_section: Annotated[str, typer.Option(help="Baseline standard section (for example: V3.2.1)")]
):
    """
    Tests OpenCRE expansion and outputs the resulting IriusRisk XML standard elements
    """
    test_standard(standard_name, standard_section)


@app.command()
def show(standard_name: Annotated[str, typer.Option(help="Filter by standard name")] = "",
         standard_section: Annotated[str, typer.Option(help="Filter by standard section")] = ""):
    """
    Shows the current standard mapping used to propagate standards
    """
    show_init(standard_name, standard_section)


@app.command("coverage-report")
def coverage_report(
    std_refs: Annotated[str, typer.Option(help="Comma-separated security standard refs")],
    yaml_component_repo: Annotated[
        Path,
        typer.Option(exists=True, file_okay=False, dir_okay=True, readable=True,
                     help="Path to the YAML component repository")
    ],
    report_format: Annotated[
        CoverageReportFormat,
        typer.Option("--format", help="Output format")
    ] = CoverageReportFormat.markdown,
    output: Annotated[
        Optional[Path],
        typer.Option(help="Path for the generated report")
    ] = None
):
    """Generates a Markdown or CSV report of components covering the requested standards."""
    mappings_yaml = get_resource(OPENCRE_PLUS)
    requested_standards = _requested_standards(std_refs, mappings_yaml)
    coverage, total_components, category_totals = collect_standard_coverage(
        yaml_component_repo, requested_standards, mappings_yaml
    )
    if report_format == CoverageReportFormat.csv:
        report = render_coverage_csv(coverage, requested_standards, total_components, category_totals)
        output = output or Path("standards-coverage-report.csv")
    else:
        report = render_coverage_report(
            coverage, requested_standards, yaml_component_repo, total_components, category_totals
        )
        output = output or Path("standards-coverage-report.md")

    try:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(report, encoding="utf8")
    except OSError as exc:
        raise typer.BadParameter(f"Could not write report '{output}': {exc}", param_hint="--output") from exc

    print(f"Coverage report written to [green]{output}[/green]")
