import logging
import os
from collections import Counter

import yaml


# The C loader is much faster than the pure Python one (seconds instead of minutes for all the components)
YAML_LOADER = getattr(yaml, "CSafeLoader", yaml.SafeLoader)

# Creating a logger
logging.basicConfig(filename="logFile.log",
                    format='%(asctime)s  %(levelname)-10s %(message)s',
                    datefmt="%Y-%m-%d-%H-%M-%S",
                    filemode='w')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def read_yaml(file_path):
    """Reads a YAML file and returns its content."""
    try:
        with open(file_path, 'r') as file:
            return yaml.load(file, Loader=YAML_LOADER)
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None


def collect_field_values_from_yaml_data(yaml_data, fields_to_collect):
    """
    Recursively collect values from specified fields in a YAML file.
    """

    def recurse_collect(data, collected):
        if isinstance(data, dict):
            for key, value in data.items():
                if key in fields_to_collect:
                    collected.append(value)
                recurse_collect(value, collected)
        elif isinstance(data, list):
            for item in data:
                recurse_collect(item, collected)

    collected_values = []
    recurse_collect(yaml_data, collected_values)

    return collected_values


def check_duplicated_components(roots):
    errors = []
    component_refs = list()

    for component_path, yaml_root in roots.items():
        component_refs.append(yaml_root["component"]["ref"])

    counter = Counter(component_refs)
    for k, v in counter.items():
        if v > 1:
            errors.append(f"Component {k} appears {v} times")

    return errors


def check_duplicated_risk_pattern_refs(roots):
    errors = []
    risk_pattern_refs = list()

    for component_path, yaml_root in roots.items():
        risk_pattern_refs.append(yaml_root["component"]["risk_pattern"]["ref"])

    counter = Counter(risk_pattern_refs)
    for k, v in counter.items():
        if v > 1:
            errors.append(f"Risk-Pattern ref {k} appears {v} times")

    return errors


def check_duplicated_risk_pattern_names(roots):
    errors = []
    risk_pattern_refs = list()

    for component_path, yaml_root in roots.items():
        risk_pattern_refs.append(yaml_root["component"]["risk_pattern"]["name"])

    counter = Counter(risk_pattern_refs)
    for k, v in counter.items():
        if v > 1:
            errors.append(f"Risk-Pattern name {k} appears {v} times")

    return errors


def check_component_category_matches_folder(roots, components_dir):
    """Check that every YAML component's category matches the top-level folder that contains it.
    ISRA adds a component to the library of the category in its YAML, not of its folder."""
    errors = []

    for component_path, yaml_root in sorted(roots.items()):
        rel_path = os.path.relpath(component_path, components_dir)
        parts = rel_path.split(os.sep)
        if len(parts) < 2:
            # Files in the root of the components directory don't belong to a category folder
            continue
        folder = parts[0]
        component = yaml_root.get("component") if isinstance(yaml_root, dict) else None
        if not isinstance(component, dict):
            errors.append(f"{rel_path}: could not be parsed or has no component section")
            continue
        category = component.get("category")
        if category != folder:
            errors.append(f"{rel_path}: category is '{category}' but the component is in folder '{folder}'")

    return errors
