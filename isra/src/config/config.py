import configparser
import json
import os
from pathlib import Path
from typing import Annotated

import typer
import yaml
from importlib_resources import files
from openai import OpenAI, OpenAIError
from rich import print
from rich.table import Table

from isra.src.config.constants import APP_NAME, SYSTEM_FIELD_VALUES
from isra.src.utils.questionary_wrapper import qselect, qtext, qpath

app = typer.Typer(no_args_is_help=True, add_help_option=False)


def get_info():
    return {
        "components_dir": "Folder where the IriusRisk YAML components are stored",
        "gpt_model": "GPT Model to use",
        "ile_root_folder": "Path where the ILE folders (config, projects, versions, output) will be created or loaded "
                           "if they already exist",
        "ile_port": "Port where ILE will listen",
        "component_input_path": "Path where components will be loaded. Leave empty to use appdata",
        "component_output_path": "Path where components will be saved. Leave empty to use appdata",
        "openai_assistant_id": "OpenAI Assistant ID that will be used to generate answers",
        "iriusrisk_url": "IriusRisk instance URL",
        "iriusrisk_api_token": "IriusRisk authentication token",
        "company_name": "Fill only if the content will be released for a specific company"
    }


def get_parser():
    properties_file = get_properties_file_path()
    parser = configparser.ConfigParser()
    parser.config_path = properties_file
    parser.read(properties_file)
    return parser


def save_properties(properties: dict):
    parser = get_parser()
    for key, value in properties.items():
        if key in parser[APP_NAME]:
            parser[APP_NAME][key] = value
        else:
            print(f"No '{key}' key found")
            return
    with open(parser.config_path, 'w') as configfile:
        parser.write(configfile)
        print("Parameters written to properties file")


def get_property(key):
    parser = get_parser()

    if key in parser[APP_NAME]:
        return parser[APP_NAME][key]
    else:
        print(f"No property '{key}' found")
        raise typer.Exit(-1)


def get_app_dir():
    return typer.get_app_dir(APP_NAME, roaming=False)


def get_properties_file_path():
    properties_file = Path(get_app_dir()) / 'isra.properties'
    if os.path.exists(properties_file):
        return properties_file
    else:
        properties_dir = get_app_dir()
        print(f"[bold blue]No config file found in {properties_dir}")
        print(f"[bold blue]Creating properties file in {properties_file}")
        if not os.path.exists(properties_dir):
            os.makedirs(properties_dir, exist_ok=True)

        # Create the properties file with default values
        parser = configparser.ConfigParser()
        parser.config_path = properties_file
        parser[APP_NAME] = {k: "" for k, v in get_info().items()}

        with open(properties_file, 'w') as f:
            parser.write(f)
            print("Parameters written to properties file")
        return properties_file


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


def initialize_properties_file():
    default_properties = {k: "" for k, v in get_info().items()}

    parser = get_parser()

    modified = False
    for key, value in default_properties.items():
        if key not in parser[APP_NAME]:
            parser[APP_NAME][key] = value
            modified = True
    if modified:
        with open(parser.config_path, 'w') as f:
            parser.write(f)
            print("Parameters written to properties file")


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
    parser = get_parser()

    table = Table("Property", "Value")
    for key, value in sorted(parser[APP_NAME].items()):
        table.add_row(key, value)
    print(table)


@app.command()
def update():
    """
    Updates a property with a specific value
    """
    parser = get_parser()

    choices = [key for key in parser[APP_NAME]]
    opt = qselect("Which property do you want to update?", choices=choices)

    try:
        if opt in ["components_dir", "ile_jar_location", "component_output_path",
                   "component_input_path", "ile_root_folder"]:
            value = qpath("Write the new value: ", default=parser[APP_NAME][opt])
        elif opt == "gpt_model":
            value = qselect("Select model (gpt-4 if not sure):", choices=[
                "gpt-3.5-turbo-0613",
                "gpt-3.5-turbo-1106",
                "gpt-3.5-turbo-16k",
                "gpt-4",
                "gpt-4-32k"
            ])
        elif opt == "openai_assistant_id":
            value = qselect("Select OpenAI Assistant ID:", choices=list_assistants())
            if value == "No assistant":
                value = ""
            else:
                value = value.split(":")[0]
        elif opt == "iriusrisk_url":
            value = qtext("Write the new value: ", default=parser[APP_NAME][opt])
            if value.endswith("/ui#!app"):
                value = value.replace("/ui#!app", "")
            if value.endswith("\\") or value.endswith("/"):
                print("Removing trailing slash...")
                value = value[:-1]
        else:
            value = qtext("Write the new value: ", default=parser[APP_NAME][opt])

    except Exception as e:
        print(e)
        print("Something wrong happened, try again")
        raise typer.Exit(-1)

    save_properties({opt: value})


@app.command()
def info():
    """
   Shows info about config parameters
    """

    parser = get_parser()
    print(f"[bold blue]Config file location: {parser.config_path}")
    print("None of these parameters are strictly mandatory, but having them enables some functionalities")
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
    parser = get_parser()
    os.remove(parser.config_path)
    initialize_properties_file()


@app.command()
def load():
    """
    Loads a configuration file
    """
    properties_dir = get_app_dir()

    choices = [file.name for file in os.scandir(properties_dir) if
               file.name.endswith(".properties") and file.name.startswith("backup")]

    if len(choices) == 0:
        print("No config backups to load")
        raise typer.Exit(-1)
    else:
        config_to_load = qselect("Which config do you want to load?", choices=choices)
        config_to_load_path = str(os.path.join(properties_dir, config_to_load))
        initialize_properties_file()
        parser = get_parser()
        parser_backup = configparser.ConfigParser()
        parser_backup.read(config_to_load_path)

        info_params = get_info()
        for key, value in parser_backup[APP_NAME].items():
            if key in info_params:
                parser[APP_NAME][key] = value
            else:
                print(f"Ignoring key {key} (deprecated)")
        with open(parser.config_path, 'w') as f:
            parser.write(f)


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
        new_properties_file = Path(get_app_dir()) / f'backup_{name}.properties'
        parser = get_parser()
        with open(new_properties_file, 'w') as configfile:
            parser.write(configfile)
            print(f"Parameters written to backup_{name}.properties file")
            print(f"To use it run 'isra config load' and select the configuration")


@app.command()
def allowed_values():
    """
    Prints all allowed values for IriusRisk's system fields
    """
    custom_field_values = get_sf_values()
    key = qselect("Which system field?", choices=custom_field_values.keys())
    print(custom_field_values[key])
