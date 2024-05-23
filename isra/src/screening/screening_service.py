import warnings

import typer
from bs4 import MarkupResemblesLocatorWarning
from rich import print

from isra.src.component.component import read_current_component, write_current_component, balance_mitigation_values
from isra.src.config.config import get_sf_values
from isra.src.config.constants import CUSTOM_FIELD_STRIDE, CUSTOM_FIELD_SCOPE, \
    CUSTOM_FIELD_BASELINE_STANDARD_REF, CUSTOM_FIELD_BASELINE_STANDARD_SECTION, \
    STRIDE_LIST, CUSTOM_FIELD_ATTACK_ENTERPRISE_TECHNIQUE, \
    CUSTOM_FIELD_ATTACK_ENTERPRISE_MITIGATION, PREFIX_COMPONENT_DEFINITION, PREFIX_THREAT, PREFIX_COUNTERMEASURE, \
    IR_SF_C_STANDARD_BASELINES, IR_SF_T_STRIDE, IR_SF_C_SCOPE, IR_SF_C_MITRE, IR_SF_T_MITRE, IR_SF_C_STANDARD_SECTION, \
    CUSTOM_FIELD_ATTACK_ICS_TECHNIQUE, CUSTOM_FIELD_ATLAS_TECHNIQUE, CUSTOM_FIELD_ATTACK_MOBILE_TECHNIQUE, \
    CUSTOM_FIELD_ATTACK_ICS_MITIGATION, CUSTOM_FIELD_ATTACK_MOBILE_MITIGATION, CUSTOM_FIELD_ATLAS_MITIGATION
from isra.src.utils.cwe_functions import get_original_cwe_weaknesses, get_cwe_description, get_cwe_impact, set_weakness
from isra.src.utils.gpt_functions import query_chatgpt, get_prompt
from isra.src.utils.questionary_wrapper import qselect, qconfirm, qtext, qmulti
from isra.src.utils.structure_functions import build_new_threat, build_new_control
from isra.src.utils.text_functions import extract_json, closest_number, beautify, get_company_name_prefix, \
    check_valid_value, set_value

warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning)


# Get functions
def generate_threat():
    template = read_current_component()

    messages = [
        {"role": "system", "content": get_prompt("generate_threat.md")},
        {"role": "user", "content": template["component"]["name"] + ":" + template["component"]["desc"]}
    ]

    return query_chatgpt(messages)


def generate_threat_description(text, feedback):
    messages = [
        {"role": "system", "content": get_prompt("generate_threat_description.md")},
        {"role": "user", "content": text},
        {"role": "user", "content": feedback}
    ]

    return query_chatgpt(messages)


def generate_control(threat_base):
    messages = [
        {"role": "system", "content": get_prompt("generate_control.md")},
        {"role": "user", "content": threat_base["name"] + ":" + threat_base["desc"]}
    ]

    return query_chatgpt(messages)


def generate_control_description(text, feedback):
    messages = [
        {"role": "system", "content": get_prompt("generate_control_description.md")},
        {"role": "user", "content": text},
        {"role": "user", "content": feedback}
    ]

    return query_chatgpt(messages)


def create_description_for_question(text, feedback):
    messages = [
        {"role": "system", "content": get_prompt("create_description_for_question.md")},
        {"role": "user", "content": text},
        {"role": "user", "content": feedback}
    ]

    return query_chatgpt(messages)


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

    return result


def get_stride_category(item, feedback):
    text = item["name"] + ": " + beautify(item["desc"])
    messages = [
        {"role": "system", "content": get_prompt("get_stride_category.md")},
        {"role": "user", "content": text},
        {"role": "user", "content": feedback}
    ]

    result = query_chatgpt(messages)
    return check_valid_value(result, IR_SF_T_STRIDE)


def get_attack_technique(item, feedback):
    text = item["name"] + ": " + beautify(item["desc"])
    messages = [
        {"role": "system",
         "content": get_prompt("get_attack_technique.md")},
        {"role": "user", "content": text},
        {"role": "user", "content": feedback}
    ]

    result = query_chatgpt(messages)
    return check_valid_value(result, IR_SF_T_MITRE)


def get_attack_mitigation(item, feedback):
    text = item["name"] + ": " + beautify(item["desc"])
    messages = [
        {"role": "system", "content": get_prompt("get_attack_mitigation.md")},
        {"role": "user", "content": text},
        {"role": "user", "content": feedback}
    ]

    result = query_chatgpt(messages)
    return check_valid_value(result, IR_SF_C_MITRE)


def get_intended_scope(item, feedback):
    text = item["name"] + ": " + beautify(item["desc"])
    messages = [
        {"role": "system", "content": get_prompt("get_intended_scope.md")},
        {"role": "user", "content": text},
        {"role": "user", "content": feedback}
    ]

    result = query_chatgpt(messages)
    return check_valid_value(result, IR_SF_C_SCOPE)


def get_baseline_standard_ref(item, feedback):
    text = item["name"] + ": " + beautify(item["desc"])
    messages = [
        {"role": "system", "content": get_prompt("get_baseline_standard_ref.md")},
        {"role": "user", "content": text},
        {"role": "user", "content": feedback}
    ]

    result = query_chatgpt(messages)
    return check_valid_value(result, IR_SF_C_STANDARD_BASELINES)


def get_baseline_standard_section(item, feedback):
    template = read_current_component()
    control_ref = item["ref"]
    standard_reference = template["controls"][control_ref]["customFields"][CUSTOM_FIELD_BASELINE_STANDARD_REF]
    print(f"Standard reference for countermeasure is: {standard_reference}")
    messages = [
        {"role": "system", "content": get_prompt("get_baseline_standard_section.md")},
        {"role": "user", "content": f"This is the countermeasure description: {item['desc']}"},
        {"role": "user", "content": f"This is the assigned security standard: {standard_reference}"},
        {"role": "user", "content": feedback}
    ]

    result = query_chatgpt(messages)
    return check_valid_value(result, IR_SF_C_STANDARD_SECTION)


def get_cia_triad(item, feedback):
    text = item["name"] + ": " + beautify(item["desc"])
    messages = [
        {"role": "system", "content": get_prompt("get_cia_triad.md")},
        {"role": "user", "content": text},
        {"role": "user", "content": feedback}
    ]

    return query_chatgpt(messages)


def get_proper_cost(item, feedback):
    text = item["name"] + ": " + beautify(item["desc"])
    messages = [
        {"role": "system", "content": get_prompt("get_proper_cost.md")},
        {"role": "user", "content": text},
        {"role": "user", "content": feedback}
    ]

    return query_chatgpt(messages)


def get_proper_cwe(item, feedback):
    text = item["name"] + ": " + beautify(item["desc"])
    messages = [
        {"role": "system", "content": get_prompt("get_proper_cwe.md")},
        {"role": "user", "content": text},
        {"role": "user", "content": feedback}
    ]

    return query_chatgpt(messages)


def get_complete_threat(item, feedback):
    text = item["name"] + ": " + beautify(item["desc"])
    messages = [
        {"role": "system", "content": get_prompt("get_complete_threat.md")},
        {"role": "user", "content": text},
        {"role": "user", "content": feedback}
    ]

    return query_chatgpt(messages)


def get_complete_control(item, feedback):
    text = item["name"] + ": " + beautify(item["desc"])
    messages = [
        {"role": "system", "content": get_prompt("get_complete_control.md")},
        {"role": "user", "content": text},
        {"role": "user", "content": feedback}
    ]

    return query_chatgpt(messages)


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


def save_intended_scope(template, to_update, action="init"):
    save_controls_custom_fields(template, CUSTOM_FIELD_SCOPE, to_update, action)


def save_baseline_standard_ref(template, to_update, action="init"):
    save_controls_custom_fields(template, CUSTOM_FIELD_BASELINE_STANDARD_REF, to_update, action)


def save_baseline_standard_section(template, to_update, action="init"):
    save_controls_custom_fields(template, CUSTOM_FIELD_BASELINE_STANDARD_SECTION, to_update, action)


def save_cia_triad(template, to_update, action="init"):
    for k, v in to_update.items():
        values = extract_json(to_update[k])

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
        cwe_id, cwe_name = val.split(":")
        set_weakness(template, k, cwe_id, action)
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


# def save_complete_threat(template, to_update, action="init"):
#     for k, v in to_update.items():
#         try:
#             values = extract_json(to_update[k])
#         except:
#             print("A problem happened when extracting json")
#             continue
#
#         template["threats"][k]["riskRating"]["C"] = closest_number(values["C"])
#         template["threats"][k]["riskRating"]["I"] = closest_number(values["I"])
#         template["threats"][k]["riskRating"]["A"] = closest_number(values["A"])
#         template["threats"][k]["riskRating"]["EE"] = closest_number(values["EE"])
#         template["threats"][k]["customFields"][CUSTOM_FIELD_STRIDE] \
#             = check_valid_value(values["stride"], IR_SF_T_STRIDE)
#         template["threats"][k]["customFields"][CUSTOM_FIELD_ATTACK_ENTERPRISE_TECHNIQUE] \
#             = check_valid_value(values["attack"], IR_SF_T_MITRE)
#
#     save_threats_to_stride_usecase(template, [])


# def save_complete_control(template, to_update, action="init"):
#
#     for k, v in to_update.items():
#         try:
#             values = extract_json(to_update[k])
#         except:
#             print(f"A problem happened when extracting json for {k}")
#             continue
#
#         template["controls"][k]["question"] = values["question"]
#         template["controls"][k]["question_desc"] = ''  # values["question_desc"]
#         template["controls"][k]["cost"] = str(values["cost"])
#         template["controls"][k]["customFields"][CUSTOM_FIELD_BASELINE_STANDARD_REF] \
#             = check_valid_value(values["baseline"], IR_SF_C_STANDARD_BASELINES)
#         template["controls"][k]["customFields"][CUSTOM_FIELD_BASELINE_STANDARD_SECTION] \
#             = check_valid_value(values["section"], IR_SF_C_STANDARD_SECTION)
#         template["controls"][k]["customFields"][CUSTOM_FIELD_SCOPE] \
#             = check_valid_value(values["scope"], IR_SF_C_SCOPE)
#         template["controls"][k]["customFields"][CUSTOM_FIELD_ATTACK_ENTERPRISE_MITIGATION] \
#             = check_valid_value(values["attack-mit"], IR_SF_C_MITRE)
#
#         cwe_id, cwe_name = values["CWE"].split(":")
#         set_weakness(template, k, cwe_id)
#
#     # Cleaning unused weaknesses
#     available_weaknesses = set(rel["weakness"] for rel in template["relations"])
#     template["weaknesses"] = {w: template["weaknesses"][w] for w in template["weaknesses"] if
#                               w in available_weaknesses}


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
                stride_category = qselect("Choose STRIDE category to group threat:", choices=stride_categories)
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

def screening(items, ask_function, save_function, choices=None):
    template = read_current_component()
    if len(items) <= 0:
        print("No items found to do screening")
    else:
        screening_choices = {
            "I want to set values only where I haven't set them yet": "init",
            "I want to replace anything with new values": "replace",
            "I want to append new values to the existing ones": "append"
        }
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
        feedback = ""

        for index, item in enumerate(items):
            # First we check if the element is valid
            validation = validate_item(items[item])
            if validation != "":
                print(f"Item {item} is not valid: {validation}")
                continue

            # We enter in an infinite loop to keep asking if the user selects 'again'
            # Any other value will break the loop
            while True:
                print(f"Item {index + 1}/{len(items)}: {item}")
                print(f"Description: [bright_cyan]{items[item]['desc']}")
                chatgpt_answer = ask_function(items[item], feedback)
                print(f"ChatGPT says: [blue]{chatgpt_answer}")

                screening_item_result = qselect("Is it correct?", choices=[
                    "y",
                    "n",
                    "skip",
                    "again",
                    "manual",
                    "exit",
                    "save"
                ])

                if screening_item_result is None:
                    raise typer.Exit(-1)
                elif screening_item_result == "y":
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
                    manual_answer = qtext("Set manually (text input):")
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

        save_results = qconfirm("No more items. Do you want to save?")
        if save_results:
            print("Saving screening results")
            save_function(template, to_update, action=action)
            write_current_component(template)


def threat_generator():
    """
    This is a generator that will help the user to create a threat or a countermeasure
    :return:
    """

    new_threat_dict = build_new_threat()

    # Let's try to find a threat, we'll ask ChatGPT to generate a possible threat name
    while True:

        chatgpt_answer = generate_threat()
        print(f"ChatGPT says: [blue]{chatgpt_answer}")
        answer = qconfirm("What do you think?")

        if answer is None:
            raise typer.Exit(-1)
        elif answer:
            new_threat_dict["name"] = chatgpt_answer
            break
        elif not answer:
            print("Let's try again")

    # If the name sounds good, we'll ask ChatGPT to create a description and iterate until we are happy with it
    feedback = ""
    while True:
        feedback = "" if feedback is None else feedback

        chatgpt_answer = generate_threat_description(new_threat_dict["name"], feedback)
        print(f"ChatGPT says: [blue]{chatgpt_answer}")
        answer = qconfirm("What do you think?")

        if answer is None:
            raise typer.Exit(-1)
        elif answer:
            new_threat_dict["desc"] = chatgpt_answer
            break
        elif not answer:
            feedback = qtext("Add more information if needed for the next time: ", default=feedback)
            print("Let's try again")

    # Finally we add the new threat to our threat collection, but we need a threat ref
    template = read_current_component()
    component_ref = template["component"]["ref"]
    component_ref_nocd = component_ref.replace(PREFIX_COMPONENT_DEFINITION + get_company_name_prefix(), "")

    # Number of manual threats until now + 1
    i = sum(1 for t in template["threats"] if "-MANUAL-" in t) + 1

    new_threat_dict["ref"] = f"{PREFIX_THREAT}{component_ref_nocd}-MANUAL-T{i}"
    template["threats"][new_threat_dict["ref"]] = new_threat_dict

    save_results = qconfirm("Do you want to save?")
    if save_results:
        print("Saving generated results")
        write_current_component(template)


def control_generator():
    """
    This is a generator that will help the user to create a threat or a countermeasure
    :return:
    """

    template = read_current_component()
    component_ref = template["component"]["ref"]
    component_ref_nocd = component_ref.replace(PREFIX_COMPONENT_DEFINITION + get_company_name_prefix(), "")

    selected_threat = qselect("Choose a threat to find a countermeasure", choices=template["threats"].keys())
    threat_item = template["threats"][selected_threat]

    new_control_dict = build_new_control()

    # Let's try to find a threat, we'll ask ChatGPT to generate a possible control name
    while True:
        chatgpt_answer = generate_control(threat_item)
        print(f"ChatGPT says: [blue]{chatgpt_answer}")
        answer = qconfirm("What do you think?")

        if answer is None:
            raise typer.Exit(-1)
        elif answer:
            new_control_dict["name"] = chatgpt_answer
            break
        elif not answer:
            print("Let's try again")

    # If the name sounds good, we'll ask ChatGPT to create a description and iterate until we are happy with it
    extra = ""
    while True:
        extra = "" if extra is None else extra

        chatgpt_answer = generate_control_description(new_control_dict["name"], extra)
        print(f"ChatGPT says: [blue]{chatgpt_answer}")
        answer = qconfirm("What do you think?")

        if answer is None:
            raise typer.Exit(-1)
        elif answer:
            new_control_dict["desc"] = chatgpt_answer
            break
        elif not answer:
            extra = qtext("Add more information if needed for the next time: ", default=extra)
            print("Let's try again")

    # Finally we add the new threat to our control collection, but we need a control ref

    i = sum(1 for t in template["controls"] if "-MANUAL-" in t) + 1

    new_control_dict["ref"] = f"{PREFIX_COUNTERMEASURE}{component_ref_nocd}-MANUAL-C{i}"
    template["controls"][new_control_dict["ref"]] = new_control_dict

    new_relation = {
        "riskPattern": template["riskPattern"]["ref"],
        "usecase": "General",
        "threat": threat_item["ref"],
        "weakness": "",
        "control": new_control_dict["ref"]
    }
    template["relations"].append(new_relation)

    save_results = qconfirm("Do you want to save?")
    if save_results:
        print("Saving generated results")
        write_current_component(template)
        balance_mitigation_values()


def autoscreening_init():
    template = read_current_component()

    parameter_config = {
        "cost": "replace",
        "question": "init",
        "question_desc": "ignore",
        "dataflow_tags": "append",
        "attack_enterprise_mitigation": "append",
        "attack_ics_mitigation": "ignore",
        "attack_mobile_mitigation": "ignore",
        "atlas_mitigation": "ignore",
        "baseline_standard_ref": "init",
        "baseline_standard_section": "append",
        "scope": "append",
        "cwe": "init",
        "riskRating": "replace",
        "stride_lm": "append",
        "attack_enterprise_technique": "append",
        "attack_ics_technique": "ignore",
        "attack_mobile_technique": "ignore",
        "atlas_technique": "ignore"
    }

    component_ref = template["component"]["ref"]
    print(f"Starting autoscreening for {component_ref}")

    assert len(template["threats"]) > 0, "No threats found"
    assert len(template["controls"]) > 0, "No controls found"

    original_cwe_weaknesses = get_original_cwe_weaknesses()

    for th in template["threats"].values():
        k = th["ref"]
        print(f'[blue]Threat: {th["ref"]} - {th["name"]}')
        values = extract_json(get_complete_threat_auto(th))

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
                                CUSTOM_FIELD_ATLAS_TECHNIQUE]
        for custom_field in threat_custom_fields:
            template["threats"][k]["customFields"][custom_field] = \
                set_value(custom_field,
                          template["threats"][k]["customFields"][custom_field],
                          values.get(custom_field, None),
                          parameter_config[custom_field])

    for c in template["controls"].values():
        k = c["ref"]
        print(f'[blue]Countermeasure: {c["ref"]} - {c["name"]}')

        values = extract_json(get_complete_control_auto(c))
        for var in ["question", "question_desc", "cost"]:
            template["controls"][k][var] = set_value(var,
                                                     template["controls"][k][var],
                                                     values.get(var, None),
                                                     parameter_config[var])

        control_custom_fields = [CUSTOM_FIELD_BASELINE_STANDARD_REF,
                                 CUSTOM_FIELD_BASELINE_STANDARD_SECTION,
                                 CUSTOM_FIELD_SCOPE,
                                 CUSTOM_FIELD_ATTACK_ENTERPRISE_MITIGATION,
                                 CUSTOM_FIELD_ATTACK_ICS_MITIGATION,
                                 CUSTOM_FIELD_ATTACK_MOBILE_MITIGATION,
                                 CUSTOM_FIELD_ATLAS_MITIGATION]
        for custom_field in control_custom_fields:
            template["controls"][k]["customFields"][custom_field] = \
                set_value(custom_field,
                          template["controls"][k]["customFields"][custom_field],
                          values.get(custom_field, None),
                          parameter_config[custom_field])

        val = values["cwe"]

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

    # Cleaning unused weaknesses
    available_weaknesses = set(rel["weakness"] for rel in template["relations"])
    template["weaknesses"] = {w: template["weaknesses"][w] for w in template["weaknesses"] if
                              w in available_weaknesses}

    print("Autoscreening finished!")
    save_results = qconfirm("Do you want to save?")
    if save_results:
        print("Saving generated results")
        write_current_component(template)
        balance_mitigation_values()


def fix_component():
    template = read_current_component()
    print("Analyzing...")

    for th in template["threats"].values():
        k = th["ref"]
        print(f'[blue]Threat: {th["name"]}')

        risk_rating = ["C", "I", "A", "EE"]

        if th["customFields"][CUSTOM_FIELD_STRIDE] not in get_sf_values(IR_SF_T_STRIDE):
            print(f'Value {th["customFields"][CUSTOM_FIELD_STRIDE]} is not in the list')
            action = qselect("What do you want to do?",
                             choices=["Replace with allowed value from list",
                                      "Set new value manually",
                                      "Do nothing",
                                      "Find alternatives"])
            if "Replace" in action:
                options = qmulti("Select:", choices=get_sf_values(IR_SF_T_STRIDE))
                th["customFields"][CUSTOM_FIELD_STRIDE] = options.join("||")
                new_stride = qselect("Which one will be used to group the threat?:", choices=options)
                for relation in template["relations"]:
                    threat_custom_fields = template["threats"][relation["threat"]]["customFields"]
                    if CUSTOM_FIELD_STRIDE in threat_custom_fields:
                        stride_category_initial = new_stride[0]
                        relation["usecase"] = STRIDE_LIST[stride_category_initial]["ref"]
                        if relation["usecase"] not in template["usecases"]:
                            template["usecases"][relation["usecase"]] = STRIDE_LIST[stride_category_initial]

            elif "manually" in action:
                pass
            elif "alternatives":
                pass

    save_results = qconfirm("Do you want to save?")
    if save_results:
        write_current_component(template)
        print("Saved")
