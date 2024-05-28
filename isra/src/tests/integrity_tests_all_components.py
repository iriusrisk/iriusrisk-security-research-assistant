import logging
import os
from collections import Counter

import yaml

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
            return yaml.safe_load(file)
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


def check_duplicated_risk_patterns(roots):
    errors = []
    risk_pattern_refs = list()

    for component_path, yaml_root in roots.items():
        risk_pattern_refs.append(yaml_root["component"]["risk_pattern"]["ref"])

    counter = Counter(risk_pattern_refs)
    for k, v in counter.items():
        if v > 1:
            errors.append(f"Risk-Pattern {k} appears {v} times")

    return errors
