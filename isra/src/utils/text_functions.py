import difflib
import json
import re
from json import JSONDecodeError

import itertools
from bs4 import BeautifulSoup

from isra.src.config.config import get_property, get_sf_values
from isra.src.config.constants import NON_ASCII_CODES, CUSTOM_FIELD_ATTACK_ENTERPRISE_TECHNIQUE, \
    CUSTOM_FIELD_ATTACK_ICS_TECHNIQUE, CUSTOM_FIELD_ATTACK_MOBILE_TECHNIQUE, CUSTOM_FIELD_ATLAS_TECHNIQUE, \
    CUSTOM_FIELD_ATTACK_ENTERPRISE_MITIGATION, CUSTOM_FIELD_ATTACK_ICS_MITIGATION, \
    CUSTOM_FIELD_ATTACK_MOBILE_MITIGATION, CUSTOM_FIELD_ATLAS_MITIGATION, IR_SF_C_STANDARD_BASELINES, \
    IR_SF_C_STANDARD_SECTION, IR_SF_C_SCOPE, IR_SF_C_MITRE, IR_SF_T_MITRE, IR_SF_T_STRIDE
from isra.src.utils.questionary_wrapper import qselect


def extract_json(json_string):
    # Find the first occurrence of a valid JSON object
    start_index = json_string.find('{')
    end_index = json_string.rfind('}')

    # Extract the JSON object
    json_object = json_string[start_index:end_index + 1].replace("\'", "\"")

    # Parse the JSON object and return it

    try:
        result = json.loads(json_object)
    except JSONDecodeError as e:
        print(f"Couldn't convert JSON answer: {json_object}")
        raise e

    return result


def replace_non_ascii(text):
    replaced_text = ""
    for char in text:
        if ord(char) in NON_ASCII_CODES:
            replaced_text += NON_ASCII_CODES[ord(char)]
        else:
            replaced_text += char
    return replaced_text


def find_closest_match(input_word, word_list):
    # Find the closest matching word in the list using difflib
    lword = input_word.lower()
    lpos = {}
    for p in word_list:
        if p.lower() not in lpos:
            lpos[p.lower()] = [p]
        else:
            lpos[p.lower()].append(p)
    lmatches = difflib.get_close_matches(lword, lpos.keys(), n=6, cutoff=0.6)
    ret = [lpos[m] for m in lmatches]
    ret = itertools.chain.from_iterable(ret)
    return list(set(ret))


def check_valid_value(result, system_field):
    if result not in get_sf_values(system_field):
        possible_matches = find_closest_match(result, get_sf_values(system_field))
        print(f"ChatGPT answered this: {result}")
        result = qselect(
            "Apparently ChatGPT's answer is not valid, please choose the best match. "
            "If there are no valid matches select None and modify it manually",
            choices=["None"] + possible_matches)
        if result == "None":
            result = ""
    return result


def beautify(text):
    return BeautifulSoup(text, features='lxml').get_text()


def generate_identifier_from_ref(text, separator="."):
    return re.sub(r"[^a-zA-Z0-9]+", separator, text).lower()


def closest_number(num_str):
    num = int(num_str)
    if num <= 0:
        return "1"
    elif num > 100:
        return "100"
    else:
        return str(min([1, 25, 50, 75, 100], key=lambda x: abs(x - num)))


def convert_cost_value(value, to_number=False):
    cost_mapping = {"high": "2", "medium": "1", "low": "0"}

    if to_number:
        return cost_mapping.get(value, "2")
    else:
        reverse_mapping = {v: k for k, v in cost_mapping.items()}
        return reverse_mapping.get(value, "high")


def merge_custom_fields(input_dict, converter):
    """
    This function takes a dictionary and a converter.
    The converter is a dictionary that has the new keys and the keys from the input dictionary that will be merged
    :return: a new dictionary where the values of different keys from the input dict will be under a new key
    """
    output_dict = {}
    for key, values in converter.items():
        merged_value = '||'.join([input_dict[val] for val in values if val in input_dict and len(input_dict[val]) > 0])
        output_dict[key] = merged_value
    return output_dict


def split_mitre_custom_field_threats(mitre_value: str):
    customfields = dict()
    attack = []
    attack_ics = []
    attack_mobile = []
    atlas = []
    for val in mitre_value.split("||"):
        if "ATT&CK ICS" in val:
            attack_ics.append(val)
        elif "ATT&CK Enterprise" in val:
            attack.append(val)
        elif "ATT&CK Mobile" in val:
            attack_mobile.append(val)
        elif "ATLAS" in val:
            atlas.append(val)
        else:
            pass
    customfields[CUSTOM_FIELD_ATTACK_ENTERPRISE_TECHNIQUE] = "||".join(set(attack))
    customfields[CUSTOM_FIELD_ATTACK_ICS_TECHNIQUE] = "||".join(set(attack_ics))
    customfields[CUSTOM_FIELD_ATTACK_MOBILE_TECHNIQUE] = "||".join(set(attack_mobile))
    customfields[CUSTOM_FIELD_ATLAS_TECHNIQUE] = "||".join(set(atlas))
    return customfields


def split_mitre_custom_field_controls(mitre_value: str):
    customfields = dict()
    attack = []
    attack_ics = []
    attack_mobile = []
    atlas = []
    for val in mitre_value.split("||"):
        if "ATT&CK ICS" in val:
            attack_ics.append(val)
        elif "ATT&CK Enterprise" in val:
            attack.append(val)
        elif "ATT&CK Mobile" in val:
            attack_mobile.append(val)
        elif "ATLAS" in val:
            atlas.append(val)
        else:
            pass
    customfields[CUSTOM_FIELD_ATTACK_ENTERPRISE_MITIGATION] = "||".join(set(attack))
    customfields[CUSTOM_FIELD_ATTACK_ICS_MITIGATION] = "||".join(set(attack_ics))
    customfields[CUSTOM_FIELD_ATTACK_MOBILE_MITIGATION] = "||".join(set(attack_mobile))
    customfields[CUSTOM_FIELD_ATLAS_MITIGATION] = "||".join(set(atlas))
    return customfields


def clean_and_capitalize(input_string):
    cleaned_string = ''.join(char if char.isalpha() else ' ' for char in input_string)
    cleaned_string = cleaned_string.capitalize()
    return cleaned_string


def remove_duplicates_from_dict_list(dict_list):
    # Convert each dictionary to a tuple representation
    tuple_list = [tuple(sorted(d.items())) for d in dict_list]

    # Convert the list of tuples to a set to remove duplicates
    unique_tuples = set(tuple_list)

    # Convert the unique tuples back to dictionaries
    unique_dict_list = [dict(t) for t in unique_tuples]

    return unique_dict_list


def get_company_name_prefix():
    return get_property("company_name") + "-" if get_property("company_name") else ""


def get_allowed_system_field_values():
    custom_field_values = (get_sf_values(IR_SF_C_STANDARD_BASELINES) +
                           get_sf_values(IR_SF_C_STANDARD_SECTION) +
                           get_sf_values(IR_SF_C_SCOPE) +
                           get_sf_values(IR_SF_C_MITRE) +
                           get_sf_values(IR_SF_T_MITRE) +
                           get_sf_values(IR_SF_T_STRIDE))

    return custom_field_values


def compare_elements(elem1, elem2, path=""):
    if type(elem1) is not type(elem2):
        print(f"Data type mismatch at path: {path}")
        return False

    if isinstance(elem1, list):
        if len(elem1) != len(elem2):
            print(f"List length mismatch at path: {path}")
            return False

        if all(isinstance(item, str) for item in elem1) and all(isinstance(item, str) for item in elem2):
            if set(elem1) != set(elem2):
                print(f"Set of string mismatch at path: {path}")
                return False
        else:
            for i, (e1, e2) in enumerate(zip(elem1, elem2)):
                if not compare_elements(e1, e2, path + f"[{i}]"):
                    return False
        return True

    elif isinstance(elem1, dict):
        for key in elem1:
            if key in elem2:
                if not compare_elements(elem1[key], elem2[key], path + f"['{key}']"):
                    return False
        return True

    else:

        if isinstance(elem1, str) and isinstance(elem2, str) and "||" in elem1:
            values1 = set(elem1.split("||"))
            values2 = set(elem2.split("||"))
            if values1 != values2:
                print(f"Data on list in string format mismatch at path: {path}")
                return False

        elif elem1 != elem2:
            print(f"Data value mismatch at path: {path}")
            return False
        return True


def set_value(variable_name, variable, value, action):
    message = ""
    log = True

    if action == "init":
        if variable == "":
            variable = value
            message = f"Setting '{value}' on {variable_name} for the first time"
    elif action == "replace":
        if str(variable) != str(value):
            message = f"Replacing '{variable}' with '{value}' on {variable_name}"
            variable = value
    elif action == "append":
        if isinstance(variable, list):
            if value.lower() not in [x.lower() for x in variable] and value != "":
                variable.append(value)
                message = f"Appending '{value}' to {variable_name} (list)"
        elif isinstance(variable, str):
            if value.lower() not in variable.lower():
                if variable != "" and value != "":
                    variable += "||" + value
                    message = f"Appending '{value}' to {variable_name} (string)"
                elif variable == "":
                    variable = value
                    message = f"Appending '{value}' to {variable_name} (string)"

        else:
            print("Type is not accepted to be appended")

    if message and log:
        print(message)

    return variable
