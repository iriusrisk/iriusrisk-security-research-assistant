import os.path
import os.path
import re
from collections import defaultdict
from json import JSONDecodeError
from typing_extensions import Annotated

import jsonschema
import yaml
from rich import print
from rich.table import Table

from isra.src.config.constants import TEMPLATE_FILE, THREAT_MODEL_FILE, TM_SCHEMA, PREFIX_COMPONENT_DEFINITION, \
    PREFIX_RISK_PATTERN, PREFIX_THREAT, PREFIX_COUNTERMEASURE
from isra.src.utils.api_functions import upload_xml, add_to_batch, release_component_batch, \
    pull_remote_component_xml
from isra.src.utils.decorators import get_time
from isra.src.utils.gpt_functions import query_chatgpt, get_prompt
from isra.src.utils.questionary_wrapper import qconfirm, qselect, qtext, qmulti
from isra.src.utils.text_functions import extract_json, get_company_name_prefix, get_allowed_system_field_values
from isra.src.utils.xml_functions import *
from isra.src.utils.yaml_functions import load_yaml_file, save_yaml_file, validate_yaml

app = typer.Typer(no_args_is_help=True, add_help_option=False)


def generate_threat_model(text):
    messages = [
        {"role": "system",
         "content": get_prompt("generate_threat_model.md")},
        {"role": "user", "content": text}
    ]

    return query_chatgpt(messages)


def generate_component_description(text):
    messages = [
        {"role": "system",
         "content": get_prompt("generate_component_description.md")
         },
        {"role": "user", "content": text}
    ]

    return query_chatgpt(messages)


def check_current_component(raise_if_not_exists=True):
    properties_dir = get_app_dir()
    template_path = os.path.join(properties_dir, TEMPLATE_FILE)

    if os.path.exists(template_path):
        return template_path
    else:
        print("No component initialized")
        if raise_if_not_exists:
            raise typer.Exit(-1)
        else:
            return ""


def read_current_component():
    template_path = check_current_component()
    with open(template_path, "r") as f:
        template = json.load(f)
    return template


def write_current_component(template):
    template_path = check_current_component()
    with open(template_path, "w") as f:
        f.write(json.dumps(template, indent=4))


@get_time
def clean_exported_components(force):
    if force:
        clean_components = True
    else:
        clean_components = qconfirm("Are you sure you want to clean all the component files?")

    if clean_components:
        properties_dir = get_app_dir()
        for file in os.listdir(properties_dir):
            if ".xml" in file or ".yaml" in file:
                os.remove(os.path.join(properties_dir, file))
                print(f"File {file} removed")

    else:
        print("Operation aborted")


def balance_mitigation_values():
    template = read_current_component()

    threat_groups = defaultdict(list)
    for item in template["relations"]:
        threat_groups[item['threat']].append(item)

    for group in threat_groups.values():
        total_controls = len(group)
        mitigation_per_control = 100 // total_controls
        remaining_mitigation = 100 % total_controls
        for i, item in enumerate(group):
            if i < remaining_mitigation:
                item['mitigation'] = f"{mitigation_per_control + 1}"
            else:
                item['mitigation'] = f"{mitigation_per_control}"

    write_current_component(template)


def upload_component():
    # This should use the IR Python client to make requests to the API, but I'll use requests
    template = read_current_component()
    balance_mitigation_values()

    try:
        # TODO: This function should be replaced at some point when the APIv2 is ready
        # upload_component_to_iriusrisk(template)
        upload_xml(template)
        print("Component uploaded successfully")
    except Exception as e:
        print(f"An error happened when uploading the component to IriusRisk: {e}")


def add_component_to_batch():
    template = read_current_component()

    try:
        add_to_batch(template)
        print(f"Component {template['component']['ref']} added to batch successfully")
    except Exception as e:
        print(f"An error happened when adding the component to batch: {e}")


def release_batch():
    try:
        release_component_batch()
        print("Release uploaded successfully")
    except Exception as e:
        print(f"An error happened when uploading the release to IriusRisk: {e}")


@get_time
def load_xml(component):
    template = load_xml_file(component)
    write_current_component(template)


@get_time
def load_yaml(component):
    template = load_yaml_file(component)
    write_current_component(template)


def validate_custom_fields(template):
    custom_field_values = get_allowed_system_field_values()
    custom_field_values.append("")

    def check(val):
        for cf, cfval in val["customFields"].items():
            for item in cfval.split("||"):
                if item not in custom_field_values:
                    print(f"Warning: {k} {cf} [red]{item}[/red] not found in available system fields")

    for k, v in template["controls"].items():
        check(v)

    for k, v in template["threats"].items():
        check(v)


@get_time
def load_init(file):
    template_path = check_current_component(raise_if_not_exists=False)
    if template_path != "":
        restart(force=True)

    if file:
        component_to_load = file
        component = file
    else:
        input_folder = get_property("component_input_path") or get_app_dir()

        choices = [file.name for file in os.scandir(input_folder) if
                   file.name.endswith(".xml") or file.name.endswith(".yaml")]

        if len(choices) == 0:
            print("No components to load")
            raise typer.Exit(-1)
        else:
            component_to_load = qselect("Which component do you want to load?", choices=choices)
            component = str(os.path.join(input_folder, component_to_load))

    initialize_template()
    if os.path.exists(component):
        if component_to_load.endswith(".xml"):
            load_xml(component)
            balance_mitigation_values()
        elif component_to_load.endswith(".yaml"):
            load_yaml(component)
            balance_mitigation_values()
        else:
            print("[red]Invalid file")
            raise typer.Exit(-1)
        print("[green]Loaded")
    else:
        print("No component found in this path")
        raise typer.Exit(-1)

    template = read_current_component()
    validate_custom_fields(template)


@get_time
def save_xml(preview):
    template = read_current_component()

    output_folder = get_property("component_output_path") or get_app_dir()
    xml_template_path = os.path.join(output_folder, f"{template['component']['ref']}.xml")
    root = save_xml_file(template)

    if preview:
        tree = etree.tostring(root, pretty_print=True)
        print(tree.decode())
    else:
        tree = etree.ElementTree(root)
        tree.write(xml_template_path, pretty_print=True, encoding='utf-8', xml_declaration=True)

        print(f"Component saved in {xml_template_path}")


@get_time
def save_yaml(preview):
    template = read_current_component()

    output_folder = get_property("component_output_path") or get_app_dir()
    yaml_template_path = os.path.join(output_folder, f"{template['component']['ref']}.yaml")
    root = save_yaml_file(template)

    yaml_dump = yaml.dump(root, default_flow_style=False, sort_keys=False)
    if preview:
        print(yaml_dump)
    else:
        validate_yaml(yaml_dump)

        with open(yaml_template_path, 'w') as file:
            yaml.dump(root, file, default_flow_style=False, sort_keys=False)
            print(f"Component saved in {yaml_template_path}")


def initialize_template():
    properties_dir = get_app_dir()
    template_path = str(os.path.join(properties_dir, TEMPLATE_FILE))

    if os.path.exists(template_path):
        print("There is already a component. Please restart before creating a new one")
        raise typer.Exit(-1)
    else:
        with open(template_path, "w") as f:
            f.write(json.dumps(json.loads(EMPTY_TEMPLATE)))


def pull_component():
    template = read_current_component()
    balance_mitigation_values()
    pull_remote_component_xml(template)
    write_current_component(template)


# Commands

@app.callback()
def callback():
    """
    Component creation
    """


@app.command()
def new():
    """
    Starts the creation of a new component
    """

    initialize_template()

    template = read_current_component()

    # We need a minimum information about the component that we are creating
    # Name
    component_name = qtext("Component name:")
    component_ref = PREFIX_COMPONENT_DEFINITION + get_company_name_prefix() + component_name.upper()
    # Anything that is not a letter or a number will be replaced by dashes
    component_ref = re.sub(r"[^a-zA-Z0-9]+", "-", component_ref)

    # Description
    description = qtext("Description (leave empty to autocomplete):")
    if description == "":
        component_desc = generate_component_description(component_name)
        # Remove trailing whitespaces and dots at the end
        component_desc = component_desc.strip().rstrip('.')
        print(f"Autogenerated: {component_desc}")
    else:
        component_desc = description

    # Category
    categories = sorted(CATEGORIES_LIST.keys())
    category = qselect("Which category will be used for this component?", choices=categories)
    component_category = category

    # Now we start building the component in the temporal storage
    risk_pattern_ref = component_ref.replace(PREFIX_COMPONENT_DEFINITION, PREFIX_RISK_PATTERN)
    component_definition = dict()
    component_definition["ref"] = component_ref
    component_definition["name"] = component_name
    component_definition["desc"] = component_desc
    component_definition["categoryRef"] = component_category
    component_definition["visible"] = "true"
    component_definition["riskPatternRefs"] = [risk_pattern_ref]

    risk_pattern = dict()
    risk_pattern["ref"] = risk_pattern_ref
    risk_pattern["name"] = component_name
    risk_pattern["desc"] = component_desc

    template["component"] = component_definition
    template["riskPattern"] = risk_pattern

    write_current_component(template)

    print(f"Component {component_ref} created")


@app.command()
def clean(force: Annotated[bool, typer.Option(help="Flag to clean all components automatically")] = False):
    """
    Removes all the generated files
    """

    clean_exported_components(force)


@app.command()
def restart(force: Annotated[bool, typer.Option(help="Flag to remove temporal component automatically")] = False):
    """
    Removes the current component
    """

    template_path = check_current_component()

    if force:
        remove_temporal_component = True
    else:
        remove_temporal_component = qconfirm("Are you sure you want to restart the component?")

    if remove_temporal_component:
        write_current_component(json.loads(EMPTY_TEMPLATE))
        os.remove(template_path)
        print(f"Temporal component removed")
    else:
        print("Operation aborted")


@app.command()
def load(file: Annotated[str, typer.Option(help="Path to file to import")] = None):
    """
    Loads an existing component from a file
    """
    # If you are using the load function I assume you want to restart the component

    load_init(file)


@app.command()
def save(format: Annotated[str, typer.Option(help="Indicate the file format of the source. 'xml' by default")] = "yaml",
         preview: Annotated[bool, typer.Option(help="Show a preview of the output without storing anything")] = False):
    """
    Saves the component in an IriusRisk XML
    """
    # This method is a mess, all because the IR data model

    if format == "xml":
        balance_mitigation_values()
        save_xml(preview)
    elif format == "yaml":
        save_yaml(preview)
    else:
        print(f"Invalid format: {format}")
        raise typer.Exit(-1)


def create_table(params, template):
    # Idea: if I create an index map I could put the right value in the right column
    headers = ["Element"] + params
    table = Table(*headers)

    for item, item_val in template["component"].items():
        param_map = dict()
        for param in params:
            if param == item:
                param_map[param] = item_val
        if len(param_map) != 0:
            table.add_row(template["component"]["ref"], *param_map.values())
    for item, item_val in template["riskPattern"].items():
        param_map = dict()
        for param in params:
            if param == item:
                param_map[param] = item_val
        if len(param_map) != 0:
            table.add_row(template["riskPattern"]["ref"], *param_map.values())

    for item in template["threats"].values():
        param_map = dict()
        for param in params:
            if param in item:
                if param in ["riskRating", "references"]:
                    param_map[param] = str(item[param])
                else:
                    param_map[param] = item[param]
            for cf, cfvalue in item["customFields"].items():
                if param == cf:
                    param_map[param] = cfvalue

        if len(param_map) != 0:
            table.add_row(item["ref"], *param_map.values())

    for item in template["controls"].values():
        param_map = dict()
        for param in params:
            if param in item:
                if param in ["standards", "references", "dataflow_tags"]:
                    param_map[param] = str(item[param])
                else:
                    param_map[param] = item[param]
            if param == "cwe":
                for rel in template["relations"]:
                    if rel["control"] == item["ref"]:
                        param_map[param] = rel["weakness"]
            for cf, cfvalue in item["customFields"].items():
                if param == cf:
                    param_map[param] = cfvalue
        if len(param_map) != 0:
            table.add_row(item["ref"], *param_map.values())
    return table


@app.command()
def info(full: Annotated[bool, typer.Option(help="Shows all properties")] = False,
         parameter: Annotated[bool, typer.Option(help="Shows parameter information")] = False,
         p: Annotated[str, typer.Option(help="Shows parameter information for a given parameter")] = ""):
    """
    Shows current component status
    """
    template = read_current_component()

    allowed_params = [
        "name",
        "desc",
        "cost",
        "question",
        "question_desc",
        "dataflow_tags",
        "attack_enterprise_mitigation",
        "attack_ics_mitigation",
        "attack_mobile_mitigation",
        "atlas_mitigation",
        "baseline_standard_ref",
        "baseline_standard_section",
        "scope",
        "cwe",
        "references",
        "standards",
        "riskRating",
        "attack_enterprise_technique",
        "attack_ics_technique",
        "attack_mobile_technique",
        "atlas_technique",
        "stride_lm",
        "categoryRef"
    ]

    if parameter:
        params = qmulti("Select parameter:", choices=allowed_params)
        table = create_table(params, template)
        print(table)
    elif p:
        if p not in allowed_params:
            print(f"Parameter {p} cannot be found")
        else:
            params = [p]
            table = create_table(params, template)
            print(table)

    else:
        if not full:
            # Here we remove everything we don't want to see
            for c in template["controls"].values():
                del c["desc"]
            for t in template["threats"].values():
                del t["desc"]
            for w in template["weaknesses"].values():
                del w["desc"]
            for uc in template["usecases"].values():
                del uc["desc"]

        print(f"[red]Use cases ({len(template['usecases'])}):")
        print(yaml.dump(template["usecases"]))
        print(f"[red]Threats ({len(template['threats'])}):")
        print(yaml.dump(template["threats"]))
        print(f"[red]Weaknesses ({len(template['weaknesses'])}):")
        print(yaml.dump(template["weaknesses"]))
        print(f"[red]Countermeasures ({len(template['controls'])}):")
        print(yaml.dump(template["controls"]))
        print("[red]Component:")
        print(yaml.dump(template["component"]))
        print("[red]Risk pattern:")
        print(yaml.dump(template["riskPattern"]))
        print(f"[red]Relations ({len(template['relations'])}):")
        table = Table("Risk Pattern", "Use case", "Threat", "Weakness", "Control", "Mitigation")
        for item in template["relations"]:
            table.add_row(item["riskPattern"], item["usecase"], item["threat"], item["weakness"], item["control"],
                          item.get("mitigation", "Not defined"))
        print(table)


@app.command()
def tm():
    """
    Creates a threat model with threats and countermeasures automatically with ChatGPT or from a file
    based on the current component name and description
    """

    template = read_current_component()

    properties_dir = get_app_dir()
    threat_model_path = os.path.join(properties_dir, THREAT_MODEL_FILE)

    component_ref = template["component"]["ref"]
    component_ref_nocd = component_ref.replace(PREFIX_COMPONENT_DEFINITION + get_company_name_prefix(), "")
    component_desc = template["component"]["desc"]

    reuse_threat_model = False
    if os.path.exists(threat_model_path):
        print(f"[blue]Existing threat model found in {threat_model_path}")
        reuse_threat_model = qconfirm("Do you want to reuse previous threat model?")

    template["threats"] = dict()
    template["weaknesses"] = dict()
    template["controls"] = dict()
    template["relations"] = list()
    if not reuse_threat_model:
        max_iterations = 10
        generated_threat_model = ""

        for attempt in range(1, max_iterations + 1):
            if attempt > 1:
                print(f"Round {attempt}")
            try:
                chatgpt_answer = generate_threat_model(component_ref + ": " + component_desc)
                generated_threat_model = extract_json(chatgpt_answer)
                break
            except JSONDecodeError:
                print(f"ChatGPT didn't answered with the right format. Trying again...")

                if attempt == max_iterations:
                    raise typer.Exit(-1)

        if generated_threat_model != "":
            with open(threat_model_path, "w") as threat_model_file:
                threat_model_file.write(json.dumps(generated_threat_model))
        else:
            raise typer.Exit(-1)

    with open(threat_model_path, "r") as threat_model_file:
        threat_model = json.loads(threat_model_file.read())

        try:
            jsonschema.validate(threat_model, TM_SCHEMA)
        except jsonschema.exceptions.ValidationError:
            print(f"The generated threat model is not valid. Please try to create the threat model again")
            raise typer.Exit(-1)

        for threat in threat_model["security_threats"]:
            new_threat = {
                "ref": f"{PREFIX_THREAT}{component_ref_nocd}-{threat['threat_id'].upper()}",
                "name": threat["threat_name"],
                "desc": threat["description"],
                "customFields": dict(),
                "references": list(),
                "riskRating": {
                    "C": "100",
                    "I": "100",
                    "A": "100",
                    "EE": "100"
                }
            }

            template["threats"][new_threat["ref"]] = new_threat

            for control in threat["countermeasures"]:
                new_control = {
                    "ref": f"{PREFIX_COUNTERMEASURE}{component_ref_nocd}-{control['countermeasure_id'].upper()}",
                    "name": control["countermeasure_name"],
                    "desc": control["description"],
                    "cost": "2",
                    "question": "",
                    "question_desc": "",
                    "dataflow_tags": [],
                    "customFields": dict(),
                    "references": [],
                    "standards": []
                }

                template["controls"][new_control["ref"]] = new_control

                new_relation = {
                    "riskPattern": template["riskPattern"]["ref"],
                    "usecase": "General",
                    "threat": new_threat["ref"],
                    "weakness": "",
                    "control": new_control["ref"]
                }

                template["relations"].append(new_relation)

        print(threat_model)
        print(f"Threats: {len(template['threats'])}")
        print(f"Countermeasures: {len(template['controls'])}")

        write_current_component(template)

        balance_mitigation_values()


@app.command()
def balance():
    """
    Balances the mitigation values of the countermeasures so that the values add up to 100 for each threat
    """
    balance_mitigation_values()


@app.command()
def upload():
    """
    Uploads a component into an IriusRisk instance
    """
    upload_component()


@app.command(hidden=True)
def batch():
    """
    Includes the component into a batch that will be uploaded to IriusRisk when the release command is executed
    """
    add_component_to_batch()


@app.command(hidden=True)
def release():
    """
    Uploads all batches found to IriusRisk
    """
    release_batch()


@app.command()
def pull():
    """
    Pulls the name, descriptions and metadata of threats and countermeasure of a component from IriusRisk
    """
    pull_component()
