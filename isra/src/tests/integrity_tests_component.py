from collections import Counter

import jsonschema
import yaml

from isra.src.config.config import get_resource
from isra.src.config.constants import YSC_SCHEMA


def read_yaml(file_path):
    """Reads a YAML file and returns its content."""
    try:
        with open(file_path, 'r') as file:
            return yaml.safe_load(file)
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None


def yaml_validator(yaml_component_path):
    errors = []
    yaml_component_data = read_yaml(yaml_component_path)
    schema = get_resource(YSC_SCHEMA, filetype="json")
    validator = jsonschema.Draft7Validator(schema)
    if not validator.is_valid(yaml_component_data):
        errors.append(f"Component {yaml_component_path} doesn't fit the JSON schema: ")
        for error in sorted(validator.iter_errors(yaml_component_data), key=str):
            errors.append(f"Field: {error.json_path}")
            errors.append(f"Reason: {error.message}")

    return errors


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


def check_duplicated_standards_sections(root):
    errors = []

    yaml_fields = ["standards"]
    standards = collect_field_values_from_yaml_data(root, yaml_fields)

    for index, standards_by_countermeasure in enumerate(standards):
        all_sections = []
        section_source = {}
        # Check if all sections across different standards are unique
        for standard, sections in standards_by_countermeasure.items():
            for section in sections:
                if section in section_source:
                    section_source[section].append(standard)
                else:
                    section_source[section] = [standard]
                all_sections.append(section)

        duplicate_sections = {section: sources for section, sources in section_source.items() if len(sources) > 1}
        if len(duplicate_sections):
            errors.append(f"Duplicate sections found across standards: {duplicate_sections}")

    return errors


def check_duplicated_references(root):
    errors = []

    component_ref = root['component']['ref']
    yaml_fields = ["references"]
    references_fields_found = collect_field_values_from_yaml_data(root, yaml_fields)

    for i, refs in enumerate(references_fields_found, start=1):
        names_counter = Counter(ref['name'] for ref in refs)
        urls_counter = Counter(ref['url'] for ref in refs)

        for name, count in names_counter.items():
            if count > 1:
                errors.append(f"Component: {component_ref} -> In 'references' field number: {i} "
                              f"-> Reference Name: {name} appears {count} times")

        for url, count in urls_counter.items():
            if count > 1:
                errors.append(f"Component: {component_ref} -> In 'references' field number: {i} "
                              f"-> Reference URL: {url} appears {count} times")

    return errors


def check_duplicated_taxonomies(root):
    errors = []

    risk_pattern = root['component']['risk_pattern']

    for threat in risk_pattern["threats"]:
        for key, inner_dict in threat["taxonomies"].items():
            values_counter = Counter(inner_dict)
            for value, count in values_counter.items():
                if count > 1:
                    errors.append(f"Threat: {threat['ref']} Key: {key} -> Value: {value} appears {count} times")

        for countermeasure in threat["countermeasures"]:
            for key, inner_dict in countermeasure["taxonomies"].items():
                values_counter = Counter(inner_dict)
                for value, count in values_counter.items():
                    if count > 1:
                        errors.append(
                            f"Countermeasure: {countermeasure['ref']} Key: {key} "
                            f"-> Value: {value} appears {count} times")

    return errors


def check_whitespaces_in_reference_urls(root):
    errors = []

    #   print(f"Component: {root['component']['ref']}")
    yaml_fields = ["references"]
    references_fields_found = collect_field_values_from_yaml_data(root, yaml_fields)
    #   print(f"Number of references defined for this component: {len(reference_fields_found)}")
    for i, refs in enumerate(references_fields_found):
        for j, ref in enumerate(refs):
            if " " in ref['url']:
                errors.append(
                    f"Component: {root['component']['ref']} "
                    f"-> In 'references' field number: {i + 1}/{len(references_fields_found)}"
                    f"-> URL with whitespaces: -> {ref['name']} -> {ref['url']}")

    return errors


def check_duplicated_controls_per_threat(root):
    errors = []

    #    print(f"Component: {root['component']['ref']}")
    yaml_fields = ["countermeasures"]
    countermeasures_fields_found = collect_field_values_from_yaml_data(root, yaml_fields)
    for i, countermeasures in enumerate(countermeasures_fields_found):
        countermeasure_refs = []
        for j, countermeasure in enumerate(countermeasures):
            countermeasure_refs.append(countermeasure['ref'])

        counter = Counter(countermeasure_refs)
        for k, v in counter.items():
            if v > 1:
                errors.append(f"Component: {root['component']['ref']} --> Countermeasure: {k} appears {v} times")

    return errors


def check_duplicated_threats_per_risk_pattern(root):
    errors = []

    #    print(f"Component: {root['component']['ref']}")
    yaml_fields = ["threats"]
    threats_fields_found = collect_field_values_from_yaml_data(root, yaml_fields)
    for i, threats in enumerate(threats_fields_found):
        threat_refs = []
        for j, threat in enumerate(threats):
            threat_refs.append(threat['ref'])

        counter = Counter(threat_refs)
        for k, v in counter.items():
            if v > 1:
                errors.append(f"Component: {root['component']['ref']} --> Threat: {k} appears {v} times")

    return errors


def check_empty_threat_descriptions(root):
    errors = []

    #    print(f"Component: {root['component']['ref']}")
    yaml_fields = ["threats"]
    threats_fields_found = collect_field_values_from_yaml_data(root, yaml_fields)
    for i, threats in enumerate(threats_fields_found):
        for j, threat in enumerate(threats):
            if not threat['description']:
                errors.append(f"Component: {root['component']['ref']} --> Threat ref: {threat['ref']} "
                              f"has an empty description")

    return errors


def check_empty_countermeasure_descriptions(root):
    errors = []

    #    print(f"Component: {root['component']['ref']}")
    yaml_fields = ["countermeasures"]
    countermeasures_fields_found = collect_field_values_from_yaml_data(root, yaml_fields)
    for i, countermeasures in enumerate(countermeasures_fields_found):
        for j, countermeasure in enumerate(countermeasures):
            if not countermeasure['description']:
                errors.append(f"Component: {root['component']['ref']} --> Countermeasure ref: {countermeasure['ref']} "
                              f"has an empty description")

    return errors


def check_problematic_characters_in_questions(root):
    errors = []

    yaml_fields = ["question", "question_desc"]
    question_fields_found = collect_field_values_from_yaml_data(root, yaml_fields)
    for i, question in enumerate(question_fields_found):
        if '"' in question:
            errors.append(f"Component: {root['component']['ref']} --> Countermeasure 'question' or 'question_desc' "
                          f"field: '{question}' contains at least one double quote character")

    return errors


def check_countermeasure_without_question(root):
    errors = []

    yaml_fields = ["countermeasures"]
    countermeasures_fields_found = collect_field_values_from_yaml_data(root, yaml_fields)
    for i, countermeasures in enumerate(countermeasures_fields_found):
        for j, countermeasure in enumerate(countermeasures):
            if not countermeasure['question']:
                errors.append(f"Component: {root['component']['ref']} --> Countermeasure ref: {countermeasure['ref']} "
                              f"has an empty question")

    return errors


def check_inconsistent_stride_values(root):
    errors = []

    yaml_fields = ["threats"]
    threats_fields_found = collect_field_values_from_yaml_data(root, yaml_fields)
    for i, threats in enumerate(threats_fields_found):
        for j, threat in enumerate(threats):
            if threat["group"] not in threat["taxonomies"]["stride"]:
                errors.append(f"Component: {root['component']['ref']} --> Threat ref: {threat['ref']} -> "
                              "STRIDE category doesn't appear in the custom field")

    return errors


def check_trailing_whitespaces(root):
    errors = []

    yaml_fields = ["name"]
    items_found = collect_field_values_from_yaml_data(root, yaml_fields)
    for i, item in enumerate(items_found):
        if item[-1] == " " or item[0] == " ":
            errors.append(f"Component: {root['component']['ref']} --> Name: '{item}' -> "
                          "Trailing whitespaces")

    return errors


def check_name_does_not_contain_category(root):
    errors = []
    component_ref: str = root['component']['ref']
    component_name: str = root['component']['name']
    category: str = root['component']['category']

    if category in component_name:
        errors.append(f"Component {component_ref} has an invalid name: {component_name}")

    return errors
