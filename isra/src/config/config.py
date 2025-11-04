import configparser
import json
import os
from typing import Annotated

import typer
import yaml
from importlib_resources import files
from openai import OpenAI, OpenAIError
from rich import print
from rich.table import Table

from isra.src.config.constants import APP_NAME, SYSTEM_FIELD_VALUES, PROPERTIES_FILE, CONFIG_FOLDER, BACKUP_FOLDER, \
    OLD_PROPERTIES_FILE, AUTOSCREENING_CONFIG_FILE
from isra.src.utils.questionary_wrapper import qselect, qtext, qpath

app = typer.Typer(no_args_is_help=True, add_help_option=False)

properties_s = None


def get_info():
    return {
        "components_dir": "Folder where the IriusRisk YAML components are stored",
        "libraries_dir": "Folder where the IriusRisk XML libraries are stored",
        "gpt_model": "GPT Model to use",
        "ile_root_folder": "Deprecated: Path where the ILE folders (config, projects, versions, output) will be "
                           "created or loaded if they already exist",
        "ile_port": "Deprecated: Port where ILE will listen",
        "component_input_path": "Path where components will be loaded. Leave empty to use appdata",
        "component_output_path": "Path where components will be saved. Leave empty to use appdata",
        "openai_assistant_id": "OpenAI Assistant ID that will be used to generate answers",
        "iriusrisk_url": "IriusRisk instance URL",
        "iriusrisk_api_token": "IriusRisk API Token",
        "company_name": "Fill only if the content will be released for a specific company",
        "openai_client": "Choose between OPENAI or AZURE",
    }


def load_config():
    with open(PROPERTIES_FILE, "r") as f:
        properties = yaml.safe_load(f)
    return properties


def save_config(new_properties):
    with open(PROPERTIES_FILE, "w") as f:
        yaml.safe_dump(new_properties, f, indent=4)


def get_property(key):
    global properties_s
    if properties_s is None:
        properties_s = load_config()

    if key in properties_s:
        return properties_s[key]
    else:
        print(f"No property '{key}' found")
        raise typer.Exit(-1)


def get_resource(resource, filetype="yaml"):
    """
    Return the parsed resource, ready to use. By default it parses YAML
    :param resource: the resource to get
    :param filetype: the file type of the resource: [json, yaml, path, text].
    :return:
    """
    resource_path = files('isra.src.resources').joinpath(resource)
    if filetype == "json":
        with open(str(resource_path)) as f:
            result = json.load(f)
    elif filetype == "path":
        result = resource_path
    elif filetype == "text":
        with open(str(resource_path), 'r', encoding="utf8") as f:
            result = str(f.read())
    else:
        with open(str(resource_path), 'r', encoding="utf8") as yml:
            result = yaml.safe_load(yml)

    return result


def get_sf_values(key=None):
    system_field_values = get_resource(SYSTEM_FIELD_VALUES)
    if key:
        return system_field_values[key]
    else:
        return system_field_values


def initialize_configuration():
    os.makedirs(CONFIG_FOLDER, exist_ok=True)
    os.makedirs(BACKUP_FOLDER, exist_ok=True)

    default_properties = {k: "" for k, v in get_info().items()}

    if os.path.exists(PROPERTIES_FILE):
        properties = load_config()
    else:
        print(f"No configuration file found in {PROPERTIES_FILE}. Creating new file...")
        properties = default_properties
        save_config(properties)
        print("Configuration initialized")

    # To update config with new config parameters
    merged_properties = {**default_properties, **properties}

    if merged_properties != properties:
        save_config(merged_properties)
        print("Configuration file updated with new parameters")

    # Migrate from old configuration file
    if os.path.exists(OLD_PROPERTIES_FILE):
        print(f"An old configuration file exists in {OLD_PROPERTIES_FILE}")
        print(f"Migrating to {PROPERTIES_FILE}")
        parser = configparser.ConfigParser()
        parser.read(OLD_PROPERTIES_FILE)
        for key, value in parser[APP_NAME].items():
            if key in merged_properties:
                merged_properties[key] = value
        save_config(merged_properties)
        os.remove(OLD_PROPERTIES_FILE)

    return merged_properties


def list_assistants():
    result = ["No assistant"]
    try:
        client = OpenAI()
        result = result + [str(x.id) + ":" + str(x.name) for x in client.beta.assistants.list().data if
                           str(x.name).startswith("ISRA")]
    except OpenAIError as e:
        print(f"Couldn't retrieve OpenAI Assistants: {e}")
    except Exception as e:
        print("Couldn't retrieve OpenAI Assistants. Ensure that you defined the OPENAI_API_KEY variable")
        print(f"Details: {e}")

    return result


def read_autoscreening_config():
    default_parameter_config = {
        "cost": "replace",
        "question": "replace",
        "question_desc": "ignore",
        "dataflow_tags": "append",
        "attack_enterprise_mitigation": "append",
        "attack_ics_mitigation": "ignore",
        "attack_mobile_mitigation": "ignore",
        "atlas_mitigation": "ignore",
        "emb3d_mitigation": "ignore",
        "baseline_standard_ref": "init",
        "baseline_standard_section": "init",
        "scope": "append",
        "cwe": "init",
        "riskRating": "replace",
        "stride_lm": "append",
        "attack_enterprise_technique": "append",
        "attack_ics_technique": "ignore",
        "attack_mobile_technique": "ignore",
        "atlas_technique": "ignore",
        "emb3d_technique": "ignore"
    }

    if not os.path.exists(AUTOSCREENING_CONFIG_FILE):

        with open(AUTOSCREENING_CONFIG_FILE, 'w') as f:
            yaml.dump(default_parameter_config, f, default_flow_style=False, sort_keys=False)
            print(f"Autoscreening parameters generated in {AUTOSCREENING_CONFIG_FILE}")

        parameter_config = default_parameter_config
    else:
        with open(AUTOSCREENING_CONFIG_FILE, 'r') as f:
            parameter_config = yaml.safe_load(f)

    modify = False
    for k in default_parameter_config.keys():
        if k not in parameter_config.keys():
            parameter_config[k] = "ignore"
            modify = True

    if modify:
        with open(AUTOSCREENING_CONFIG_FILE, 'w') as f:
            yaml.dump(parameter_config, f, default_flow_style=False, sort_keys=False)
            print(f"Autoscreening parameters generated in {AUTOSCREENING_CONFIG_FILE}")

    return parameter_config


@app.callback()
def callback():
    """
    Configuration settings
    """


@app.command()
def list():
    """
    Shows all properties
    """
    properties = load_config()

    table = Table("Property", "Value")
    for key, value in sorted(properties.items()):
        table.add_row(key, value)
    print(table)


@app.command()
def update():
    """
    Updates a property with a specific value
    """
    properties = load_config()

    opt = qselect("Which property do you want to update?", choices=properties.keys())

    try:
        if opt in ["components_dir", "ile_jar_location", "component_output_path",
                   "component_input_path", "ile_root_folder"]:
            value = qpath("Write the new value: ", default=properties[opt])
        elif opt == "gpt_model":
            value = qtext("Write the new value: ", default=properties[opt])
        elif opt == "openai_assistant_id":
            if get_property("openai_client") == "OPENAI":
                value = qselect("Select OpenAI Assistant ID:", choices=list_assistants())
                if value == "No assistant":
                    value = ""
                else:
                    value = value.split(":")[0]
            else:
                print("Assistants couldn't be retrieved. Ensure that you defined OPENAI in the openai_client parameter")
                value = ""
        elif opt == "openai_client":
            value = qselect("Select OpenAI client", choices=["OPENAI", "AZURE"])
        elif opt == "iriusrisk_url":
            value = qtext("Write the new value: ", default=properties[opt])
            if value.endswith("/ui#!app"):
                value = value.replace("/ui#!app", "")
            if value.endswith("\\") or value.endswith("/"):
                print("Removing trailing slash...")
                value = value[:-1]
        else:
            value = qtext("Write the new value: ", default=properties[opt])

    except Exception as e:
        print(e)
        print("Something wrong happened, try again")
        raise typer.Exit(-1)

    properties[opt] = value
    save_config(properties)


@app.command()
def info():
    """
    Shows info about config parameters
    """

    print(f"[bold blue]Config file location: {PROPERTIES_FILE}")
    print("None of these parameters are strictly mandatory, but having them enables some functionality")
    info_items = get_info()
    table = Table("Property", "Value")
    for key, value in sorted(info_items.items()):
        table.add_row(key, value)
    print(table)


@app.command()
def reset():
    """
    Resets configuration (in case we need to force an update)
    """
    os.remove(PROPERTIES_FILE)
    initialize_configuration()


@app.command()
def load():
    """
    Loads a configuration file
    """

    choices = [file.name for file in os.scandir(BACKUP_FOLDER) if
               file.name.endswith(".yaml") and file.name.startswith("backup")]

    if len(choices) == 0:
        print("No config backups to load")
        raise typer.Exit(-1)
    else:
        backup_choice = qselect("Which config do you want to load?", choices=choices)
        backup_file_path = str(os.path.join(BACKUP_FOLDER, backup_choice))

        with open(backup_file_path, "r") as f:
            backup_properties = yaml.safe_load(f)

        properties = initialize_configuration()

        info_params = get_info()
        for key, value in backup_properties.items():
            if key in info_params:
                properties[key] = value
            else:
                print(f"Ignoring key {key} (deprecated)")
        save_config(properties)


@app.command()
def save(name: Annotated[str, typer.Option(help="Name of the new config file")] = None):
    """
    Saves a configuration file
    """
    if name is None or name == "":
        name = qtext("Indicate name for new file:")
    if name == "":
        raise typer.Exit(-1)
    if name == "isra":
        print("Name cannot be 'isra' since it's a reserved name")
    else:
        new_properties_file = BACKUP_FOLDER / f'backup_{name}.yaml'

        properties = load_config()
        with open(new_properties_file, 'w') as f:
            yaml.safe_dump(properties, f)
            print(f"Parameters written to backup_{name}.yaml file")
            print(f"To use it run 'isra config load' and select the configuration")


@app.command()
def allowed_values():
    """
    Prints all allowed values for IriusRisk's system fields
    """
    custom_field_values = get_sf_values()
    key = qselect("Which system field?", choices=custom_field_values.keys())
    print(custom_field_values[key])
