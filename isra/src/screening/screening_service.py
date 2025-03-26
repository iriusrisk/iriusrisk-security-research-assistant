import warnings
from json import JSONDecodeError

from bs4 import MarkupResemblesLocatorWarning
from rich import print

from isra.src.component.component import read_current_component, write_current_component, balance_mitigation_values
from isra.src.config.config import get_sf_values, read_autoscreening_config, get_resource
from isra.src.config.constants import CUSTOM_FIELD_STRIDE, CUSTOM_FIELD_SCOPE, \
    CUSTOM_FIELD_STANDARD_BASELINE_REF, CUSTOM_FIELD_STANDARD_BASELINE_SECTION, \
    STRIDE_LIST, CUSTOM_FIELD_ATTACK_ENTERPRISE_TECHNIQUE, \
    CUSTOM_FIELD_ATTACK_ENTERPRISE_MITIGATION, \
    IR_SF_C_STANDARD_BASELINES, IR_SF_T_STRIDE, IR_SF_C_SCOPE, IR_SF_C_MITRE, IR_SF_T_MITRE, IR_SF_C_STANDARD_SECTION, \
    CUSTOM_FIELD_ATTACK_ICS_TECHNIQUE, CUSTOM_FIELD_ATLAS_TECHNIQUE, CUSTOM_FIELD_ATTACK_MOBILE_TECHNIQUE, \
    CUSTOM_FIELD_ATTACK_ICS_MITIGATION, CUSTOM_FIELD_ATTACK_MOBILE_MITIGATION, CUSTOM_FIELD_ATLAS_MITIGATION, \
    SYSTEM_FIELD_VALUES, CUSTOM_FIELD_EMB3D_TECHNIQUE, CUSTOM_FIELD_EMB3D_MITIGATION
from isra.src.utils.cwe_functions import get_original_cwe_weaknesses, get_cwe_description, get_cwe_impact, set_weakness
from isra.src.utils.gpt_functions import query_chatgpt, get_prompt
from isra.src.utils.questionary_wrapper import qselect, qconfirm, qtext, qauto
from isra.src.utils.text_functions import extract_json, closest_number, beautify, \
    check_valid_value, set_value, fix_value

warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning)


# Get functions


def fix_description(text, feedback):
    messages = [
        {"role": "system", "content": get_prompt("generate_control_description.md")},
        {"role": "user", "content": text},
        {"role": "user", "content": feedback}
    ]

    return query_chatgpt(messages), ""

def create_description_for_question(text, feedback):
    messages = [
        {"role": "system", "content": get_prompt("create_description_for_question.md")},
        {"role": "user", "content": text},
        {"role": "user", "content": feedback}
    ]

    return query_chatgpt(messages), ""


def generate_question(item, feedback):
    text = item["name"] + ": " + beautify(item["desc"])
    messages = [
        {"role": "system", "content": get_prompt("generate_question.md")},
        {"role": "user", "content": text},
        {"role": "user", "content": feedback}
    ]

    result = query_chatgpt(messages)
    if "\"" in result:
        print(f"Original question was: {result}")
        result = result.replace("\"", "'")
        print(f"Double quotes have been removed: {result}")

    return result, item["question"]


def get_stride_category(item, feedback):
    text = item["name"] + ": " + beautify(item["desc"])
    messages = [
        {"role": "system", "content": get_prompt("get_stride_category.md")},
        {"role": "user", "content": text},
        {"role": "user", "content": feedback}
    ]

    result = query_chatgpt(messages)
    return check_valid_value(result, IR_SF_T_STRIDE), item["customFields"].get(CUSTOM_FIELD_STRIDE, "")


def get_attack_technique(item, feedback):
    text = item["name"] + ": " + beautify(item["desc"])
    messages = [
        {"role": "system",
         "content": get_prompt("get_attack_technique.md")},
        {"role": "user", "content": text},
        {"role": "user", "content": feedback}
    ]

    result = query_chatgpt(messages)
    return (check_valid_value(result, IR_SF_T_MITRE),
            item["customFields"].get(CUSTOM_FIELD_ATTACK_ENTERPRISE_TECHNIQUE, ""))


def get_attack_mitigation(item, feedback):
    text = item["name"] + ": " + beautify(item["desc"])
    messages = [
        {"role": "system", "content": get_prompt("get_attack_mitigation.md")},
        {"role": "user", "content": text},
        {"role": "user", "content": feedback}
    ]

    result = query_chatgpt(messages)
    return (check_valid_value(result, IR_SF_C_MITRE),
            item["customFields"].get(CUSTOM_FIELD_ATTACK_ENTERPRISE_MITIGATION, ""))


def get_emb3d_technique(item, feedback):
    text = item["name"] + ": " + beautify(item["desc"])
    messages = [
        {"role": "system",
         "content": get_prompt("get_emb3d_technique.md")},
        {"role": "user", "content": text},
        {"role": "user", "content": feedback}
    ]

    result = query_chatgpt(messages)
    return (check_valid_value(result, IR_SF_T_MITRE),
            item["customFields"].get(CUSTOM_FIELD_EMB3D_TECHNIQUE, ""))


def get_emb3d_mitigation(item, feedback):
    text = item["name"] + ": " + beautify(item["desc"])
    messages = [
        {"role": "system", "content": get_prompt("get_emb3d_mitigation.md")},
        {"role": "user", "content": text},
        {"role": "user", "content": feedback}
    ]

    result = query_chatgpt(messages)
    return (check_valid_value(result, IR_SF_C_MITRE),
            item["customFields"].get(CUSTOM_FIELD_EMB3D_MITIGATION, ""))


def get_intended_scope(item, feedback):
    text = item["name"] + ": " + beautify(item["desc"])
    messages = [
        {"role": "system", "content": get_prompt("get_intended_scope.md")},
        {"role": "user", "content": text},
        {"role": "user", "content": feedback}
    ]

    result = query_chatgpt(messages)
    return check_valid_value(result, IR_SF_C_SCOPE), item["customFields"].get(CUSTOM_FIELD_SCOPE, "")


def get_baseline_standard_ref(item, feedback):
    text = item["name"] + ": " + beautify(item["desc"])
    messages = [
        {"role": "system", "content": get_prompt("get_baseline_standard_ref.md")},
        {"role": "user", "content": text},
        {"role": "user", "content": feedback}
    ]

    result = query_chatgpt(messages)
    return (check_valid_value(result, IR_SF_C_STANDARD_BASELINES),
            item["customFields"].get(CUSTOM_FIELD_STANDARD_BASELINE_REF, ""))


def get_baseline_standard_section(item, feedback):
    template = read_current_component()
    control_ref = item["ref"]
    standard_reference = template["controls"][control_ref]["customFields"][CUSTOM_FIELD_STANDARD_BASELINE_REF]
    print(f"Standard reference for countermeasure is: {standard_reference}")
    messages = [
        {"role": "system", "content": get_prompt("get_baseline_standard_section.md")},
        {"role": "user", "content": f"This is the countermeasure description: {item['desc']}"},
        {"role": "user", "content": f"This is the assigned security standard: {standard_reference}"},
        {"role": "user", "content": feedback}
    ]

    result = query_chatgpt(messages)
    return (check_valid_value(result, IR_SF_C_STANDARD_SECTION),
            item["customFields"].get(CUSTOM_FIELD_STANDARD_BASELINE_SECTION, ""))


def get_cia_triad(item, feedback):
    text = item["name"] + ": " + beautify(item["desc"])
    messages = [
        {"role": "system", "content": get_prompt("get_cia_triad.md")},
        {"role": "user", "content": text},
        {"role": "user", "content": feedback}
    ]

    return query_chatgpt(messages), str(item["riskRating"])


def get_proper_cost(item, feedback):
    text = item["name"] + ": " + beautify(item["desc"])
    messages = [
        {"role": "system", "content": get_prompt("get_proper_cost.md")},
        {"role": "user", "content": text},
        {"role": "user", "content": feedback}
    ]

    return query_chatgpt(messages), item["cost"]


def get_proper_cwe(item, feedback):
    text = item["name"] + ": " + beautify(item["desc"])
    messages = [
        {"role": "system", "content": get_prompt("get_proper_cwe.md")},
        {"role": "user", "content": text},
        {"role": "user", "content": feedback}
    ]

    result = query_chatgpt(messages)
    original_cwe_weaknesses = get_original_cwe_weaknesses()
    if ":" in result:
        cwe_id, _ = result.split(":")

        if cwe_id not in original_cwe_weaknesses:
            print(f"{cwe_id} is not a valid CWE. Try to avoid using CWE categories and pillars")
        else:
            result = f"{cwe_id}:{original_cwe_weaknesses[cwe_id].attrib['Name']}"

    current = ""
    template = read_current_component()
    for rel in template["relations"]:
        if rel["control"] == item["ref"]:
            current = rel["weakness"]
            break

    if current != "":
        _, cwe_id = current.split("-")

        if cwe_id not in original_cwe_weaknesses:
            print(f"{cwe_id} is not a valid CWE. Try to avoid using CWE categories and pillars")
        else:
            current = f"{cwe_id}:{original_cwe_weaknesses[cwe_id].attrib['Name']}"

    return result, current


def get_complete_threat_auto(item):
    text = item["name"] + ": " + beautify(item["desc"])
    messages = [
        {"role": "system", "content": get_prompt("get_complete_threat_auto.md")},
        {"role": "user", "content": text}
    ]

    return query_chatgpt(messages)


def get_complete_control_auto(item):
    text = item["name"] + ": " + beautify(item["desc"])
    messages = [
        {"role": "system", "content": get_prompt("get_complete_control_auto.md")},
        {"role": "user", "content": text}
    ]

    return query_chatgpt(messages)


# Getters

def get_all_threats(field=""):
    """This function returns all threats.
    If a custom field is passed it will return those threats that don't have this custom field in place
    This is because we assume that those elements are still pending to be analyzed"""
    threats = dict()

    template = read_current_component()

    for ref, item in template["threats"].items():
        # If there is no custom field with the name indicated in the field parameter
        if not any(cf_ref == field for cf_ref in item["customFields"] if cf_ref != ""):
            # What the user will see when doing the screening
            threats[ref] = item
        # If there is a field but it's empty
        if any(cf_ref == field and cf_value == "" for cf_ref, cf_value in item["customFields"].items() if cf_ref != ""):
            threats[ref] = item

    return threats


def get_all_controls(field=""):
    """This function returns all controls.
    If a custom field is passed it will return those controls that don't have this custom field in place
    This is because we assume that those elements are still pending to be analyzed"""
    controls = dict()

    template = read_current_component()

    for ref, item in template["controls"].items():
        # If there is no custom field with the name indicated in the field parameter
        if not any(cf_ref == field for cf_ref in item["customFields"] if cf_ref != ""):
            # What the user will see when doing the screening
            controls[ref] = item
        # If there is a field but it's empty
        if any(cf_ref == field and cf_value == "" for cf_ref, cf_value in item["customFields"].items() if cf_ref != ""):
            controls[ref] = item

    return controls


# Save functions

def save_threats_custom_fields(template, field, to_update, action="init"):
    for k, v in to_update.items():
        if field not in template["threats"][k]["customFields"]:
            template["threats"][k]["customFields"][field] = ""
        template["threats"][k]["customFields"][field] \
            = set_value(field, template["threats"][k]["customFields"][field], v, action)


def save_controls_custom_fields(template, field, to_update, action="init"):
    for k, v in to_update.items():
        if field not in template["controls"][k]["customFields"]:
            template["controls"][k]["customFields"][field] = ""
        template["controls"][k]["customFields"][field] \
            = set_value(field, template["controls"][k]["customFields"][field], v, action)


def save_stride_category(template, to_update, action="init"):
    save_threats_custom_fields(template, CUSTOM_FIELD_STRIDE, to_update, action)
    save_threats_to_stride_usecase(template)


def save_attack_technique(template, to_update, action="init"):
    save_threats_custom_fields(template, CUSTOM_FIELD_ATTACK_ENTERPRISE_TECHNIQUE, to_update, action)


def save_attack_mitigation(template, to_update, action="init"):
    save_controls_custom_fields(template, CUSTOM_FIELD_ATTACK_ENTERPRISE_MITIGATION, to_update, action)


def save_emb3d_technique(template, to_update, action="init"):
    save_threats_custom_fields(template, CUSTOM_FIELD_EMB3D_TECHNIQUE, to_update, action)


def save_emb3d_mitigation(template, to_update, action="init"):
    save_controls_custom_fields(template, CUSTOM_FIELD_EMB3D_MITIGATION, to_update, action)


def save_intended_scope(template, to_update, action="init"):
    save_controls_custom_fields(template, CUSTOM_FIELD_SCOPE, to_update, action)


def save_baseline_standard_ref(template, to_update, action="init"):
    save_controls_custom_fields(template, CUSTOM_FIELD_STANDARD_BASELINE_REF, to_update, action)


def save_baseline_standard_section(template, to_update, action="init"):
    save_controls_custom_fields(template, CUSTOM_FIELD_STANDARD_BASELINE_SECTION, to_update, action)


def save_cia_triad(template, to_update, action="init"):
    for k, v in to_update.items():
        try:
            values = extract_json(to_update[k])
        except JSONDecodeError:
            continue

        if action in ["init", "replace"]:
            risk_rating = ["C", "I", "A", "EE"]
            for r in risk_rating:
                template["threats"][k]["riskRating"][r] = set_value(r, template["threats"][k]["riskRating"][r],
                                                                    closest_number(values[r]), action)


def save_proper_cost(template, to_update, action="init"):
    for k, v in to_update.items():
        if action in ["init", "replace"]:
            template["controls"][k]["cost"] = set_value("cost", template["controls"][k]["cost"], str(v), action)


def save_proper_cwe(template, to_update, action="init"):
    # TODO: This could be improved by creating a script that generates a file with all the information
    # instead of querying the original document over and over

    for k, val in to_update.items():
        if ":" in val:
            cwe_id, cwe_name = val.split(":")
            set_weakness(template, k, cwe_id, action)
        else:
            print("Wrong format. Use ID:Name")
    # Cleaning unused weaknesses
    available_weaknesses = set(rel["weakness"] for rel in template["relations"])
    template["weaknesses"] = {w: template["weaknesses"][w] for w in template["weaknesses"] if w in available_weaknesses}


def save_question(template, to_update, action="init"):
    for control_ref, question_text in to_update.items():
        control_item = template["controls"][control_ref]
        question_desc = ""  # create_description_for_question(question_text)

        if action in ["init", "replace"]:
            control_item["question"] = set_value("question", control_item["question"], question_text, action)
            control_item["question_desc"] = set_value("question_desc", control_item["question_desc"], question_desc,
                                                      action)


# Custom behavior for saving functions

def save_threats_to_stride_usecase(template):
    for relation in template["relations"]:
        stride_cf = template["threats"][relation["threat"]]["customFields"].get(CUSTOM_FIELD_STRIDE, "")

        if len(stride_cf) == 0:
            pass
        else:
            stride_categories = stride_cf.split("||")
            stride_category_initial = stride_categories[0][0]
            if len(stride_categories) > 1:
                stride_category = qselect(f"Choose STRIDE category to group threat {relation['threat']}:",
                                          choices=stride_categories)
                stride_category_initial = stride_category[0]

            relation["usecase"] = STRIDE_LIST[stride_category_initial]["ref"]
            if relation["usecase"] not in template["usecases"]:
                template["usecases"][relation["usecase"]] = STRIDE_LIST[stride_category_initial]


# Utils


def validate_item(item):
    """
    A quick validation to check if the element (threat or countermeasure) has the minimum attributes in place
    """
    try:
        assert item["ref"] is not None, "Ref is None"
        assert item["ref"] != "", "Ref is empty"
        assert item["name"] is not None, "Name is None"
        assert item["name"] != "", "Name is empty"
        assert item["desc"] is not None, "Desc is None"
        assert item["desc"] != "", "Desc is empty"

        return ""
    except AssertionError as e:
        return str(e)


# Main processes

def screening(items, ask_function, save_function, choices=None, force=False):
    template = read_current_component()
    if len(items) <= 0:
        print("No items found to do screening")
    else:
        screening_choices = {
            "I want to replace existing values with new ones": "replace",
            "I want to set values only where they have not been set yet": "init",
            "I want to append new values to the existing ones": "append"
        }
        if force:
            action = "replace"
        else:
            action_choice = qselect("Define the purpose of the screening:", choices=screening_choices.keys())
            action = screening_choices[action_choice]

        print(f"[red]Starting screening process for {len(items)} items")
        print("Press 'y' or 'n' and then press Enter")
        print("Press 'again' to ask ChatGPT again and hope for a different answer")
        print("Press 'skip' to skip item")
        print("Press 'manual' to add a value manually")
        print("Press 'exit' to stop the screening process without saving any values")
        print("Press 'save' to stop the screening process and save values")

        to_update = dict()

        for index, item in enumerate(items):
            # First we check if the element is valid
            validation = validate_item(items[item])
            if validation != "":
                print(f"Item {item} is not valid: {validation}")
                continue

            feedback = ""
            # We enter in an infinite loop to keep asking if the user selects 'again'
            # Any other value will break the loop
            while True:
                print(f"Item {index + 1}/{len(items)}: {item}")
                print(f"Name: [bright_cyan]{items[item]['name']}")
                print(f"Description: [bright_cyan]{items[item]['desc']}")

                chatgpt_answer, current_value = ask_function(items[item], feedback)
                if current_value != "":
                    print(f"Current value is [green]{current_value}")
                if current_value != "" and action == "init":
                    print("Item already has a value, skipping...")
                    break

                print(f"ChatGPT says: [blue]{chatgpt_answer}")

                if force:
                    screening_item_result = "y"
                else:
                    screening_item_result = qselect("Is it correct?", choices=[
                        "y",
                        "n",
                        "skip",
                        "again",
                        "manual",
                        "exit",
                        "save"
                    ])

                if screening_item_result == "y":
                    to_update[item] = chatgpt_answer
                    break
                elif screening_item_result == "n":
                    if choices is not None:
                        manual_answer = qselect("Set manually:", choices=choices)
                        if manual_answer is None:
                            continue
                        to_update[item] = manual_answer
                    break
                elif screening_item_result == "again":
                    feedback = qtext("Add some feedback for ChatGPT:", default=feedback)
                    if feedback is None:
                        feedback = ""
                elif screening_item_result == "skip":
                    break
                elif screening_item_result == "manual":
                    manual_answer = qauto("Set manually (text input):", choices=choices)
                    if manual_answer is None:
                        continue
                    to_update[item] = manual_answer
                    break
                elif screening_item_result == "exit":
                    print("Stopping the screening process")
                    return
                elif screening_item_result == "save":
                    print("Saving screening results")
                    save_function(template, to_update, action=action)
                    write_current_component(template)
                    return

        if force:
            save_results = True
        else:
            save_results = qconfirm("No more items. Do you want to save?")
        if save_results:
            print("Saving screening results")
            save_function(template, to_update, action=action)
            write_current_component(template)


def autoscreening_init(force=False):
    template = read_current_component()

    parameter_config = read_autoscreening_config()

    component_ref = template["component"]["ref"]
    print(f"Starting autoscreening for {component_ref}")

    assert len(template["threats"]) > 0, "No threats found"
    assert len(template["controls"]) > 0, "No controls found"

    original_cwe_weaknesses = get_original_cwe_weaknesses()

    for th in template["threats"].values():
        k = th["ref"]
        print(f'[blue]Threat: {th["ref"]} - {th["name"]}')

        tries = 5
        valid = False
        while tries > 0 and not valid:
            try:
                values = extract_json(get_complete_threat_auto(th))
                valid = True
            except JSONDecodeError:
                tries -= 1
                print(f"Failed when decoding JSON, trying again...({tries})")

        if not valid:
            print("Couldn't extract JSON after 5 tries, skipping...")
            continue

        risk_rating = ["C", "I", "A", "EE"]
        for category in risk_rating:
            template["threats"][k]["riskRating"][category] = set_value(category,
                                                                       template["threats"][k]["riskRating"][category],
                                                                       closest_number(values.get(category, "100")),
                                                                       parameter_config["riskRating"])

        threat_custom_fields = [CUSTOM_FIELD_STRIDE,
                                CUSTOM_FIELD_ATTACK_ENTERPRISE_TECHNIQUE,
                                CUSTOM_FIELD_ATTACK_ICS_TECHNIQUE,
                                CUSTOM_FIELD_ATTACK_MOBILE_TECHNIQUE,
                                CUSTOM_FIELD_ATLAS_TECHNIQUE,
                                CUSTOM_FIELD_EMB3D_TECHNIQUE]
        for custom_field in threat_custom_fields:
            if custom_field not in template["threats"][k]["customFields"]:
                template["threats"][k]["customFields"][custom_field] = ""
            template["threats"][k]["customFields"][custom_field] = \
                set_value(custom_field,
                          template["threats"][k]["customFields"][custom_field],
                          values.get(custom_field, None),
                          parameter_config[custom_field])

    save_threats_to_stride_usecase(template)

    for c in template["controls"].values():
        k = c["ref"]
        print(f'[blue]Countermeasure: {c["ref"]} - {c["name"]}')
        try:
            values = extract_json(get_complete_control_auto(c))
        except JSONDecodeError:
            continue

        for var in ["question", "question_desc", "cost"]:
            template["controls"][k][var] = set_value(var,
                                                     template["controls"][k][var],
                                                     values.get(var, None),
                                                     parameter_config[var])

        control_custom_fields = [CUSTOM_FIELD_STANDARD_BASELINE_REF,
                                 CUSTOM_FIELD_STANDARD_BASELINE_SECTION,
                                 CUSTOM_FIELD_SCOPE,
                                 CUSTOM_FIELD_ATTACK_ENTERPRISE_MITIGATION,
                                 CUSTOM_FIELD_ATTACK_ICS_MITIGATION,
                                 CUSTOM_FIELD_ATTACK_MOBILE_MITIGATION,
                                 CUSTOM_FIELD_ATLAS_MITIGATION,
                                 CUSTOM_FIELD_EMB3D_MITIGATION]
        for custom_field in control_custom_fields:
            if custom_field not in template["controls"][k]["customFields"]:
                template["controls"][k]["customFields"][custom_field] = ""
            template["controls"][k]["customFields"][custom_field] = \
                set_value(custom_field,
                          template["controls"][k]["customFields"][custom_field],
                          values.get(custom_field, None),
                          parameter_config[custom_field])

        val = values["cwe"]

        if ":" in val:
            cwe_id, cwe_name = val.split(":")

            for rel in template["relations"]:
                if rel["control"] == k and cwe_id in original_cwe_weaknesses:
                    rel["weakness"] = f"CWE-{cwe_id}"

                    final_desc = get_cwe_description(original_cwe_weaknesses, [rel["weakness"]])
                    final_impact = get_cwe_impact(original_cwe_weaknesses, cwe_id)

                    template["weaknesses"][rel["weakness"]] = {
                        "ref": rel["weakness"],
                        "name": rel["weakness"],  # Before: class_base_weaknesses[cwe_id].attrib["Name"],
                        "desc": final_desc,
                        "impact": final_impact
                    }
                    print(f"{rel['weakness']} set")
                elif rel["control"] == k and cwe_id not in original_cwe_weaknesses:
                    print(f"Weakness {cwe_id} has not been found in the internal CWE list")
        else:
            print(f"Couldn't extract CWE from '{val}'")
    # Cleaning unused weaknesses
    available_weaknesses = set(rel["weakness"] for rel in template["relations"])
    template["weaknesses"] = {w: template["weaknesses"][w] for w in template["weaknesses"] if
                              w in available_weaknesses}

    print("Autoscreening finished!")
    if force:
        save_results = True
    else:
        save_results = qconfirm("Do you want to save?")
    if save_results:
        print("Saving generated results")
        write_current_component(template)
        balance_mitigation_values()


def fix_component(force_save=False):
    template = read_current_component()
    print("Analyzing...")

    allowed_standard_baselines = get_sf_values(IR_SF_C_STANDARD_BASELINES)
    allowed_standard_sections = get_sf_values(IR_SF_C_STANDARD_SECTION)
    allowed_scopes = get_sf_values(IR_SF_C_SCOPE)
    allowed_mitre_mitigations = get_sf_values(IR_SF_C_MITRE)
    allowed_mitre_techniques = get_sf_values(IR_SF_T_MITRE)
    allowed_stride_categories = get_sf_values(IR_SF_T_STRIDE)

    for th in template["threats"].values():
        print(f'[blue]Threat: {th["ref"]} - {th["name"]}')

        risk_rating = ["C", "I", "A", "EE"]
        for r in risk_rating:
            th["riskRating"][r] = fix_value(th["riskRating"][r], ["1", "25", "50", "75", "100"])

        th["customFields"].setdefault(CUSTOM_FIELD_ATTACK_ENTERPRISE_TECHNIQUE, "")
        th["customFields"].setdefault(CUSTOM_FIELD_STRIDE, "")

        th["customFields"][CUSTOM_FIELD_ATTACK_ENTERPRISE_TECHNIQUE] \
            = fix_value(th["customFields"][CUSTOM_FIELD_ATTACK_ENTERPRISE_TECHNIQUE],
                        allowed_mitre_techniques)
        th["customFields"][CUSTOM_FIELD_STRIDE] \
            = fix_value(th["customFields"][CUSTOM_FIELD_STRIDE],
                        allowed_stride_categories)

    save_threats_to_stride_usecase(template)

    for c in template["controls"].values():
        print(f'[blue]Countermeasure: {c["ref"]} - {c["name"]}')

        c["customFields"].setdefault(CUSTOM_FIELD_STANDARD_BASELINE_REF, "")
        c["customFields"].setdefault(CUSTOM_FIELD_STANDARD_BASELINE_SECTION, "")
        c["customFields"].setdefault(CUSTOM_FIELD_SCOPE, "")
        c["customFields"].setdefault(CUSTOM_FIELD_ATTACK_ENTERPRISE_MITIGATION, "")

        c["customFields"][CUSTOM_FIELD_STANDARD_BASELINE_REF] \
            = fix_value(c["customFields"][CUSTOM_FIELD_STANDARD_BASELINE_REF],
                        allowed_standard_baselines)
        c["customFields"][CUSTOM_FIELD_STANDARD_BASELINE_SECTION] \
            = fix_value(c["customFields"][CUSTOM_FIELD_STANDARD_BASELINE_SECTION],
                        allowed_standard_sections)
        c["customFields"][CUSTOM_FIELD_SCOPE] \
            = fix_value(c["customFields"][CUSTOM_FIELD_SCOPE],
                        allowed_scopes)
        c["customFields"][CUSTOM_FIELD_ATTACK_ENTERPRISE_MITIGATION] \
            = fix_value(c["customFields"][CUSTOM_FIELD_ATTACK_ENTERPRISE_MITIGATION],
                        allowed_mitre_mitigations)
        c["cost"] = fix_value(c["cost"], ["0", "1", "2"])

        if "\"" in c["question"]:
            c["question"] = c["question"].replace("\"", "'")

    original_cwe_weaknesses = get_original_cwe_weaknesses()
    for relation in template["relations"]:
        cwe_id = relation["weakness"].replace("CWE-", "")
        if cwe_id not in original_cwe_weaknesses:
            # TODO: This should return a list of related CWEs but we don't have that list :(
            # related_weaknesses = get_cwe_related_weaknesses(original_cwe_weaknesses, cwe_id)
            relation["weakness"] = fix_value(relation["weakness"], [])

    save_results = qconfirm("Do you want to save?")
    if save_results:
        write_current_component(template)
        print("Saved")


# Experimental functions

def get_baseline_standard_section_nist(item, feedback):
    template = read_current_component()
    control_ref = item["ref"]
    standard_reference = template["controls"][control_ref]["customFields"][CUSTOM_FIELD_STANDARD_BASELINE_REF]
    print(f"Standard reference for countermeasure is: {standard_reference}")
    messages = [
        {"role": "system", "content": get_prompt("get_baseline_standard_section_nist.md")},
        {"role": "user", "content": f"This is the countermeasure description: {item['desc']}"},
        {"role": "user", "content": f"This is the assigned security standard: {standard_reference}"},
        {"role": "user", "content": feedback}
    ]

    result = query_chatgpt(messages)
    print(result)
    return result, ""


def set_default_baseline_standard(standard):
    template = read_current_component()
    to_update = dict()
    items = get_all_controls()
    for c in items:
        to_update[c] = standard

    save_controls_custom_fields(template, CUSTOM_FIELD_STANDARD_BASELINE_REF, to_update, "replace")
    write_current_component(template)

    items = get_all_controls()
    screening(items, get_baseline_standard_section_nist, save_baseline_standard_section,
              choices=get_sf_values(IR_SF_C_STANDARD_SECTION), force=True)


def fix_mitre_values():
    # A hack to fix MITRE values automatically
    template = read_current_component()

    cfs = get_resource(SYSTEM_FIELD_VALUES, filetype="yaml")

    for threat in template["threats"].values():
        for cf_key, cf_value in threat["customFields"].items():
            if cf_key in [CUSTOM_FIELD_ATLAS_TECHNIQUE, CUSTOM_FIELD_ATTACK_ENTERPRISE_TECHNIQUE,
                          CUSTOM_FIELD_ATTACK_MOBILE_TECHNIQUE, CUSTOM_FIELD_ATTACK_ICS_TECHNIQUE]:

                if cf_value != "":
                    new_value = ""
                    for value in cf_value.split("||"):

                        if value in cfs[IR_SF_T_MITRE]:
                            new_value += value + "||"
                        else:
                            m = value.split(" - ")
                            k = m[0] + " - " + m[1] + " - "
                            for cfv in cfs[IR_SF_T_MITRE]:
                                if k in cfv:
                                    new_value += cfv + "||"

                    new_value = new_value[:-2]
                    threat["customFields"][cf_key] = new_value

    for control in template["controls"].values():
        for cf_key, cf_value in control["customFields"].items():
            if cf_key in [CUSTOM_FIELD_ATLAS_MITIGATION, CUSTOM_FIELD_ATTACK_ENTERPRISE_MITIGATION,
                          CUSTOM_FIELD_ATTACK_MOBILE_MITIGATION, CUSTOM_FIELD_ATTACK_ICS_MITIGATION]:

                if cf_value != "":
                    new_value = ""
                    for value in cf_value.split("||"):
                        if value in cfs[IR_SF_C_MITRE]:
                            new_value += value + "||"
                        else:
                            m = value.split(" - ")
                            k = m[0] + " - " + m[1] + " - "
                            for cfv in cfs[IR_SF_C_MITRE]:
                                if k in cfv:
                                    new_value += cfv + "||"

                    new_value = new_value[:-2]
                    control["customFields"][cf_key] = new_value

    write_current_component(template)


def custom_fix_component():
    # A hack to fix MITRE values automatically
    template = read_current_component()


    # for threat in template["threats"].values():
    #     print(threat["desc"])
    #
    #     answer, current_value = fix_description(threat["desc"], "")
    #     ss = extract_json(answer)
    #     print(answer)
    #
    #     threat["desc"] = ss["description"]

    for control in template["controls"].values():
        print(control["desc"])

        answer, current_value = fix_description(control["name"], "")
        print(answer)

        control["desc"] = answer


    write_current_component(template)