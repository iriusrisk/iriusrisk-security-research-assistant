import json
import os
import uuid

import typer
from lxml import etree

from isra.src.config.config import get_property, get_app_dir
from isra.src.config.constants import OUTPUT_NAME, CATEGORIES_LIST, SF_C_MAP, SF_T_MAP, \
    CUSTOM_FIELD_SCOPE, \
    CUSTOM_FIELD_BASELINE_STANDARD_REF, CUSTOM_FIELD_BASELINE_STANDARD_SECTION, \
    CUSTOM_FIELD_STRIDE, EMPTY_TEMPLATE
from isra.src.utils.cwe_functions import get_original_cwe_weaknesses, get_cwe_description
from isra.src.utils.text_functions import merge_custom_fields, split_mitre_custom_field_threats, \
    split_mitre_custom_field_controls, generate_identifier_from_ref


def load_xml_file(component_path):
    file_name = os.path.basename(component_path)
    tree = etree.parse(component_path)
    root = tree.getroot()

    template = json.loads(EMPTY_TEMPLATE)
    template['component']['ref'] = os.path.splitext(file_name)[0]

    template = import_content_into_template(template, root=root)
    template = import_rules_into_template(template, root=root)

    return template


def save_xml_file(template):
    # Create new etree.Element with the information from the template
    root = etree.Element("library")
    root.attrib["ref"] = template['component']['ref']
    root.attrib["name"] = template['component']['ref']
    root.attrib["revision"] = "1"
    root.attrib["enabled"] = "true"
    root.attrib["tags"] = ""
    desc = etree.SubElement(root, "desc")
    desc.text = ""
    etree.SubElement(root, "categoryComponents")
    etree.SubElement(root, "componentDefinitions")
    etree.SubElement(root, "supportedStandards")
    etree.SubElement(root, "riskPatterns")
    etree.SubElement(root, "rules")
    etree.SubElement(root, "customFields")

    category = root.find(f'.//categoryComponent[@ref="{template["component"]["categoryRef"]}"]')
    if category is None:
        category = etree.Element("categoryComponent")
        root.find("categoryComponents").append(category)
    category.attrib["ref"] = template['component']['categoryRef']
    category.attrib["name"] = CATEGORIES_LIST[category.attrib["ref"]]["name"]

    component_definition = root.find(f'.//componentDefinition[@ref="{template["component"]["ref"]}"]')
    if component_definition is None:
        component_definition = etree.Element("componentDefinition")
        root.find("componentDefinitions").append(component_definition)
    component_definition.attrib["ref"] = template['component']['ref']
    component_definition.attrib["name"] = template['component']['name']
    component_definition.attrib["desc"] = template['component']['desc']
    component_definition.attrib["categoryRef"] = template['component']['categoryRef']
    component_definition.attrib["visible"] = "true"

    component_risk_patterns = component_definition.find("riskPatterns")
    if component_risk_patterns is None:
        component_risk_patterns = etree.Element("riskPatterns")
        component_definition.append(component_risk_patterns)
    for rp in component_risk_patterns.iter("riskPattern"):
        component_risk_patterns.remove(rp)
    component_risk_pattern = etree.SubElement(component_risk_patterns, "riskPattern")
    component_risk_pattern.attrib["ref"] = template['riskPattern']['ref']

    # This is different because we haven't added the content yet
    supported_standards = root.find("supportedStandards")
    supported_standards_to_add = set()
    for control, control_item in template["controls"].items():
        for standard_item in control_item["standards"]:
            supported_standards_to_add.add(standard_item["standard-ref"])
    for std in supported_standards_to_add:
        supported_standard = etree.SubElement(supported_standards, "supportedStandard")
        supported_standard.attrib["ref"] = OUTPUT_NAME[std]["ref"]
        supported_standard.attrib["name"] = OUTPUT_NAME[std]["name"]

    risk_pattern = create_risk_pattern_element()
    risk_pattern.attrib["ref"] = template['riskPattern']['ref']
    risk_pattern.attrib["name"] = template['riskPattern']['name']
    risk_pattern.attrib["desc"] = template['riskPattern']['desc']
    root.find("riskPatterns").append(risk_pattern)

    # First we create the nodes for countermeasures and weaknesses
    for control in template["controls"].values():
        if control["ref"] in [x["control"] for x in template["relations"]]:
            new_control = risk_pattern.find(f'./countermeasures/countermeasure[@ref="{control["ref"]}"]')
            if new_control is None:
                new_control = create_control_element()
                risk_pattern.find("countermeasures").append(new_control)
            new_control.attrib["ref"] = control["ref"]
            new_control.attrib["name"] = control["name"]
            new_control.attrib["cost"] = control["cost"]
            new_control.find("desc").text = control["desc"]

            for item in control["references"]:
                reference_element = etree.SubElement(new_control.find("references"), "reference")
                reference_element.attrib["name"] = item["name"]
                reference_element.attrib["url"] = item["url"]

            control_custom_fields = merge_custom_fields(control["customFields"], SF_C_MAP)
            for ref, value in control_custom_fields.items():
                cf_element = etree.SubElement(new_control.find("customFields"), "customField")
                cf_element.attrib["ref"] = ref
                cf_element.attrib["value"] = value

            for item in control["standards"]:
                reference_element = etree.SubElement(new_control.find("standards"), "standard")
                reference_element.attrib["supportedStandardRef"] = OUTPUT_NAME[item["standard-ref"]]["ref"]
                reference_element.attrib["ref"] = item["standard-section"]

    original_cwe_weaknesses = get_original_cwe_weaknesses()
    for weakness in template["weaknesses"].values():
        if weakness["ref"] in [item["weakness"] for item in template["relations"]]:
            new_weakness = risk_pattern.find(f'./weaknesses/weakness[@ref="{weakness["ref"]}"]')
            if new_weakness is None:
                new_weakness = create_weakness_element()
                risk_pattern.find("weaknesses").append(new_weakness)
            new_weakness.attrib["ref"] = weakness["ref"]
            new_weakness.attrib["name"] = weakness["name"]
            new_weakness.find("desc").text = get_cwe_description(original_cwe_weaknesses, weakness["ref"].split(" "))
            new_weakness.attrib["impact"] = weakness["impact"]

    # Then we add the use cases
    for relation in template["relations"]:
        new_use_case = risk_pattern.find(
            f'./usecases/usecase[@ref="{relation["usecase"]}"]')
        if new_use_case is None:
            new_use_case = create_usecase_element()
            etree.SubElement(new_use_case, "threats")
            risk_pattern.find("usecases").append(new_use_case)
        new_use_case.attrib["ref"] = relation["usecase"]
        new_use_case.attrib["name"] = template["usecases"][relation["usecase"]]["name"]
        new_use_case.attrib["desc"] = template["usecases"][relation["usecase"]]["desc"]

    # Then we add the threats
    for relation in template["relations"]:

        new_threat = risk_pattern.find(
            f'./usecases/usecase[@ref="{relation["usecase"]}"]/threats/threat[@ref="{relation["threat"]}"]')
        if new_threat is None:
            new_threat = create_threat_element()
            uc = risk_pattern.find(f"./usecases/usecase[@ref='{relation['usecase']}']")
            uc.find("threats").append(new_threat)

        new_threat.attrib["ref"] = relation["threat"]
        new_threat.attrib["name"] = template["threats"][relation["threat"]]["name"]
        new_threat.find("desc").text = template["threats"][relation["threat"]]["desc"]
        new_threat.find("riskRating").attrib["confidentiality"] = \
            template["threats"][relation["threat"]]["riskRating"]["C"]
        new_threat.find("riskRating").attrib["integrity"] = \
            template["threats"][relation["threat"]]["riskRating"]["I"]
        new_threat.find("riskRating").attrib["availability"] = \
            template["threats"][relation["threat"]]["riskRating"]["A"]
        new_threat.find("riskRating").attrib["easeOfExploitation"] = \
            template["threats"][relation["threat"]]["riskRating"]["EE"]

        existing_references = [item.attrib["name"] for item in new_threat.find("references").iter("reference")]
        for item in template["threats"][relation["threat"]]["references"]:
            if item["name"] not in existing_references:
                reference_element = etree.SubElement(new_threat.find("references"), "reference")
                reference_element.attrib["name"] = item["name"]
                reference_element.attrib["url"] = item["url"]

        threat_custom_fields = merge_custom_fields(template["threats"][relation["threat"]]["customFields"],
                                                   SF_T_MAP)
        for ref, value in threat_custom_fields.items():
            cf_element = etree.SubElement(new_threat.find("customFields"), "customField")
            cf_element.attrib["ref"] = ref
            cf_element.attrib["value"] = value

    # Finally we add weaknesses and countermeasures inside the threats
    for relation in template["relations"]:
        wrel = relation["weakness"]
        crel = relation["control"]

        new_threat = risk_pattern.find(
            "./usecases/usecase[@ref='%s']/threats/threat[@ref='%s']" % (relation["usecase"], relation["threat"]))

        if wrel == "" and crel == "":
            # Nothing to do, no weakness or control in this relation
            pass

        elif wrel != "" and crel == "":
            # Empty weakness
            witem = etree.Element("weakness")
            witem.attrib["ref"] = wrel
            new_threat.find("weaknesses").append(witem)

        elif wrel == "" and crel != "":
            # Orphaned control
            citem = etree.Element("countermeasure")
            citem.attrib["ref"] = crel
            citem.attrib["mitigation"] = relation["mitigation"]
            new_threat.find("countermeasures").append(citem)

        else:
            # Weakness and control found
            witem = etree.Element("weakness")
            witem.attrib["ref"] = wrel
            new_threat.find("weaknesses").append(witem)

            # It appears twice because it must be save in two different parent elements
            citem = etree.Element("countermeasure")
            citem.attrib["ref"] = crel
            citem.attrib["mitigation"] = relation["mitigation"]

            citem2 = etree.Element("countermeasure")
            citem2.attrib["ref"] = crel
            citem2.attrib["mitigation"] = relation["mitigation"]

            new_threat.find("countermeasures").append(citem)
            cbox = etree.SubElement(witem, "countermeasures")
            cbox.append(citem2)

    library_origin = template["component"]["ref"]
    create_rule_elements(template, root, library_origin)

    return root


def create_rule_elements(template, root, library_origin):
    comp_ref = generate_identifier_from_ref(template["component"]["ref"])

    for rule in root.findall('.//rules/rule'):
        if comp_ref in rule.attrib['name']:
            # print(f"Removed rule {rule.attrib['name']}")
            root.find('rules').remove(rule)

    for control_ref, control in template["controls"].items():
        cont = generate_identifier_from_ref(control["name"])
        qg_id = f"{comp_ref}.{cont}"

        # First we need to remove old rules
        if "question" in control and control["question"] != "":
            rule_element = create_rule_question_group(template['component']['ref'], qg_id, "Security Context",
                                                      control["question"], "7000", control["question_desc"])
            root.find("rules").append(rule_element)
            rule_element = create_rule_question_group_answers(qg_id)
            root.find("rules").append(rule_element)
            rule_element = create_rule_question_group_action_implemented(library_origin, qg_id, control_ref)
            root.find("rules").append(rule_element)
            rule_element = create_rule_question_group_action_unsure(library_origin, qg_id, control_ref)
            root.find("rules").append(rule_element)
            rule_element = create_rule_question_group_action_required(library_origin, qg_id, control_ref)
            root.find("rules").append(rule_element)
            rule_element = create_rule_question_group_action_na(library_origin, qg_id, control_ref)
            root.find("rules").append(rule_element)

        if "dataflow_tags" in control and len(control["dataflow_tags"]) > 0:
            for item in control["dataflow_tags"]:
                rule_element = create_rule_implement_by_tag(library_origin, qg_id, control_ref, item)
                root.find("rules").append(rule_element)

    return root


def create_control_element():
    new_control = etree.Element("countermeasure")
    new_control.attrib["ref"] = ""
    new_control.attrib["name"] = ""
    new_control.attrib["platform"] = ""
    new_control.attrib["cost"] = "2"
    new_control.attrib["risk"] = "0"
    new_control.attrib["state"] = "Recommended"
    new_control.attrib["owner"] = ""
    new_control.attrib["library"] = ""
    new_control.attrib["source"] = "MANUAL"
    control_desc = etree.SubElement(new_control, "desc")
    control_desc.text = ""
    etree.SubElement(new_control, "implementations")
    etree.SubElement(new_control, "references")
    etree.SubElement(new_control, "standards")
    etree.SubElement(new_control, "customFields")
    test = etree.SubElement(new_control, "test")
    test.attrib["expiryDate"] = ""
    test.attrib["expiryPeriod"] = "0"
    etree.SubElement(test, "steps")
    etree.SubElement(test, "notes")
    test_source = etree.SubElement(test, "source")
    test_source.attrib["filename"] = ""
    test_source.attrib["args"] = ""
    test_source.attrib["enabled"] = "true"
    etree.SubElement(test_source, "output")
    etree.SubElement(test, "references")
    etree.SubElement(test, "customFields")

    return new_control


def create_weakness_element():
    new_weakness = etree.Element("weakness")
    new_weakness.attrib["ref"] = ""
    new_weakness.attrib["name"] = ""
    new_weakness.attrib["state"] = "0"
    new_weakness.attrib["impact"] = "100"
    control_desc = etree.SubElement(new_weakness, "desc")
    control_desc.text = ""
    test = etree.SubElement(new_weakness, "test")
    test.attrib["expiryDate"] = ""
    test.attrib["expiryPeriod"] = "0"
    etree.SubElement(test, "steps")
    etree.SubElement(test, "notes")
    test_source = etree.SubElement(test, "source")
    test_source.attrib["filename"] = ""
    test_source.attrib["args"] = ""
    test_source.attrib["enabled"] = "true"
    etree.SubElement(test_source, "output")
    etree.SubElement(test, "references")
    etree.SubElement(test, "customFields")

    return new_weakness


def create_threat_element():
    new_threat = etree.Element("threat")
    new_threat.attrib["ref"] = ""
    new_threat.attrib["name"] = ""
    new_threat.attrib["state"] = "Expose"
    new_threat.attrib["source"] = "MANUAL"
    new_threat.attrib["owner"] = ""
    new_threat.attrib["library"] = ""
    etree.SubElement(new_threat, "desc")
    th_risk_rating = etree.SubElement(new_threat, "riskRating")
    th_risk_rating.attrib["confidentiality"] = "100"
    th_risk_rating.attrib["integrity"] = "100"
    th_risk_rating.attrib["availability"] = "100"
    th_risk_rating.attrib["easeOfExploitation"] = "100"
    etree.SubElement(new_threat, "references")
    etree.SubElement(new_threat, "weaknesses")
    etree.SubElement(new_threat, "countermeasures")
    etree.SubElement(new_threat, "customFields")

    return new_threat


def create_usecase_element():
    new_use_case = etree.Element("usecase")
    new_use_case.attrib["ref"] = ""
    new_use_case.attrib["name"] = ""
    new_use_case.attrib["desc"] = ""
    return new_use_case


def create_risk_pattern_element():
    new_risk_pattern = etree.Element("riskPattern")
    new_risk_pattern.attrib["ref"] = ""
    new_risk_pattern.attrib["name"] = ""
    new_risk_pattern.attrib["desc"] = ""
    etree.SubElement(new_risk_pattern, "tags")
    etree.SubElement(new_risk_pattern, "countermeasures")
    etree.SubElement(new_risk_pattern, "weaknesses")
    etree.SubElement(new_risk_pattern, "usecases")
    return new_risk_pattern


def create_rule_element():
    rule = etree.Element("rule")
    rule.attrib["module"] = "component"
    rule.attrib["generatedByGui"] = "true"
    etree.SubElement(rule, "conditions")
    etree.SubElement(rule, "actions")

    return rule


def create_rule_question_group(component_definition_ref, qg_id, qc_name, qc_question, qc_priority, qc_desc):
    rule = create_rule_element()
    rule.attrib["name"] = f"Q - {qg_id}"
    condition = etree.SubElement(rule.find("conditions"), "condition")
    condition.attrib["name"] = "CONDITION_COMPONENT_DEFINITION"
    condition.attrib["field"] = "id"
    condition.attrib["value"] = component_definition_ref

    action = etree.SubElement(rule.find("actions"), "action")
    action.attrib["name"] = "INSERT_COMPONENT_QUESTION_GROUP"
    action.attrib["project"] = ""
    action.attrib[
        "value"] = f"gc.qg.{qg_id}_::_{qc_name}_::_{qc_question}_::_{qc_priority}_::_true_::_false_::_{qc_desc}"

    return rule


def create_rule_question_group_answers(qg_id):
    rule = create_rule_element()
    rule.attrib["name"] = f"Q - {qg_id} - *"
    condition = etree.SubElement(rule.find("conditions"), "condition")
    condition.attrib["name"] = "CONDITION_COMPONENT_QUESTION_GROUP_EXISTS"
    condition.attrib["field"] = "id"
    condition.attrib["value"] = f"gc.qg.{qg_id}_::_group"

    # fc.answer.audit.log.audit.operations.implemented
    q_id = f"gc.answer.{qg_id}"
    action1 = etree.SubElement(rule.find("actions"), "action")
    action1.attrib["name"] = "INSERT_COMPONENT_QUESTION"
    action1.attrib["project"] = ""
    action1.attrib[
        "value"] = (f"{q_id}.implemented_::_Yes, it is implemented_::_This functionality is already "
                    f"present in the system")

    action2 = etree.SubElement(rule.find("actions"), "action")
    action2.attrib["name"] = "INSERT_COMPONENT_QUESTION"
    action2.attrib["project"] = ""
    action2.attrib["value"] = f"{q_id}.required_::_No, but it is required_::_This requirement has to be implemented"

    action3 = etree.SubElement(rule.find("actions"), "action")
    action3.attrib["name"] = "INSERT_COMPONENT_QUESTION"
    action3.attrib["project"] = ""
    action3.attrib["value"] = f"{q_id}.unsure_::_Not sure_::_This requirement is under analysis"

    action4 = etree.SubElement(rule.find("actions"), "action")
    action4.attrib["name"] = "INSERT_COMPONENT_QUESTION"
    action4.attrib["project"] = ""
    action4.attrib[
        "value"] = (f"{q_id}.not.applicable_::_No, and this is not applicable_::_This requirement cannot be "
                    f"implemented in this system or is out of scope")

    return rule


def create_rule_question_group_action_implemented(category_ref, qg_id, control_ref):
    rule = create_rule_element()
    q_id = f"gc.answer.{qg_id}"

    rule.attrib["name"] = f"ControlImplemented: {qg_id} - Implemented"
    condition = etree.SubElement(rule.find("conditions"), "condition")
    condition.attrib["name"] = "CONDITION_COMPONENT_QUESTION"
    condition.attrib["field"] = "id"
    condition.attrib["value"] = f"{q_id}.implemented"

    action = etree.SubElement(rule.find("actions"), "action")
    action.attrib["name"] = "MARK_CONTROL_AS"
    action.attrib["project"] = category_ref
    action.attrib["value"] = f"{control_ref}_::_Implemented_::__::_false"

    notif_id = f"gc.notification.warning.{qg_id}.used"
    notif_message = f"This countermeasure has already been implemented as indicated in the questionnaire"
    notification = etree.SubElement(rule.find("actions"), "action")
    notification.attrib["name"] = "INSERT_COMPONENT_NOTIFICATION"
    notification.attrib["project"] = ""
    notification.attrib["value"] = f"NotificationType.WARNING_::_{notif_id}_::_{notif_message}"

    return rule


def create_rule_question_group_action_required(category_ref, qg_id, control_ref):
    rule = create_rule_element()
    q_id = f"gc.answer.{qg_id}"

    rule.attrib["name"] = f"ControlRequired: {qg_id} - Required"
    condition = etree.SubElement(rule.find("conditions"), "condition")
    condition.attrib["name"] = "CONDITION_COMPONENT_QUESTION"
    condition.attrib["field"] = "id"
    condition.attrib["value"] = f"{q_id}.required"

    action = etree.SubElement(rule.find("actions"), "action")
    action.attrib["name"] = "MARK_CONTROL_AS"
    action.attrib["project"] = category_ref
    action.attrib["value"] = f"{control_ref}_::_Required_::__::_false"

    return rule


def create_rule_question_group_action_na(category_ref, qg_id, control_ref):
    rule = create_rule_element()
    q_id = f"gc.answer.{qg_id}"

    rule.attrib["name"] = f"ControlNotApplicable: {qg_id} - N/A"
    condition = etree.SubElement(rule.find("conditions"), "condition")
    condition.attrib["name"] = "CONDITION_COMPONENT_QUESTION"
    condition.attrib["field"] = "id"
    condition.attrib["value"] = f"{q_id}.not.applicable"

    action = etree.SubElement(rule.find("actions"), "action")
    action.attrib["name"] = "MARK_CONTROL_AS"
    action.attrib["project"] = category_ref
    action.attrib["value"] = f"{control_ref}_::_N/A_::_This countermeasure has been marked as N/A_::_false"

    return rule


def create_rule_question_group_action_unsure(category_ref, qg_id, control_ref):
    rule = create_rule_element()
    q_id = f"gc.answer.{qg_id}"

    rule.attrib["name"] = f"ControlRecommended: {qg_id} - Recommended"
    condition = etree.SubElement(rule.find("conditions"), "condition")
    condition.attrib["name"] = "CONDITION_COMPONENT_QUESTION"
    condition.attrib["field"] = "id"
    condition.attrib["value"] = f"{q_id}.unsure"

    action = etree.SubElement(rule.find("actions"), "action")
    action.attrib["name"] = "MARK_CONTROL_AS"
    action.attrib["project"] = category_ref
    action.attrib["value"] = f"{control_ref}_::_Recommended_::__::_false"

    return rule


def create_rule_implement_by_tag(category_ref, qg_id, control_ref, tag):
    rule = create_rule_element()
    rule.attrib["module"] = "dataflow"

    rule.attrib["name"] = f"Implement countermeasure if tag {tag} in dataflow: {qg_id}"
    condition = etree.SubElement(rule.find("conditions"), "condition")
    condition.attrib["name"] = "CONDITION_DATAFLOW_CONTAINS_TAG"
    condition.attrib["field"] = "id"
    condition.attrib["value"] = f"{tag}"

    action = etree.SubElement(rule.find("actions"), "action")
    action.attrib["name"] = "IMPLEMENT_CONTROL_DESTINATION"
    action.attrib["project"] = category_ref
    action.attrib["value"] = f"{control_ref}_::_false"

    return rule


def import_content_into_template(template, xml_text=None, root=None):
    if xml_text is not None:
        root = etree.fromstring(xml_text)
    if xml_text is None and root is None:
        print("No XML to load")
        raise typer.Exit(-1)

    rps = []
    for cd in root.iter("componentDefinition"):
        if cd.attrib["ref"] == template["component"]["ref"]:
            for rp in cd.iter("riskPattern"):
                rps.append(rp.attrib["ref"])

            template["component"] = {
                "ref": cd.attrib["ref"],
                "name": cd.attrib["name"].rstrip(),
                "desc": cd.attrib["desc"],
                "categoryRef": cd.attrib["categoryRef"],
                "visible": cd.attrib["visible"],
                "riskPatternRefs": rps
            }

    # Loading risk pattern
    template["relations"] = []

    for rp in root.find("riskPatterns").iter("riskPattern"):
        if rp.attrib["ref"] in rps:
            template["riskPattern"] = {
                "ref": rp.attrib["ref"],
                "name": rp.attrib["name"].rstrip(),
                "desc": rp.attrib["desc"]
            }

            for weakness in rp.find("weaknesses").iter("weakness"):
                weaknessdesc = weakness.find("desc").text

                template["weaknesses"][weakness.attrib["ref"]] = {
                    "ref": weakness.attrib["ref"],
                    "name": weakness.attrib["name"].rstrip(),
                    "desc": weaknessdesc,
                    "impact": weakness.attrib["impact"]
                }

            for control in rp.find("countermeasures").iter("countermeasure"):

                controldesc = control.find("desc").text
                customfields = dict()
                for cf in control.iter("customField"):
                    if cf.attrib["value"] != "":
                        if cf.attrib["ref"] == "SF-C-MITRE":
                            customfields = split_mitre_custom_field_controls(cf.attrib["value"])
                        elif cf.attrib["ref"] == "SF-C-SCOPE":
                            customfields[CUSTOM_FIELD_SCOPE] = cf.attrib["value"]
                        elif cf.attrib["ref"] == "SF-C-STANDARD-BASELINE":
                            customfields[CUSTOM_FIELD_BASELINE_STANDARD_REF] = cf.attrib["value"]
                        elif cf.attrib["ref"] == "SF-C-STANDARD-SECTION":
                            customfields[CUSTOM_FIELD_BASELINE_STANDARD_SECTION] = cf.attrib["value"]
                        else:
                            print("Custom field not valid")

                references = list()
                for reference in control.iter("reference"):
                    if reference.attrib["url"] != "":
                        references.append({
                            "name": reference.attrib["name"],
                            "url": reference.attrib["url"]
                        })

                template["controls"][control.attrib["ref"]] = {
                    "ref": control.attrib["ref"],
                    "name": control.attrib["name"].rstrip(),
                    "desc": controldesc,
                    "cost": control.attrib["cost"],
                    "customFields": customfields,
                    "references": references,
                    "standards": [],
                    "dataflow_tags": []  # This will be filled in the import_rules_into_template function
                }

            for usecase in rp.find("usecases").iter("usecase"):

                template["usecases"][usecase.attrib["ref"]] = {
                    "ref": usecase.attrib["ref"],
                    "name": usecase.attrib["name"],
                    "desc": usecase.attrib["desc"]
                }

                for threat in usecase.iter("threat"):
                    desc = threat.find("desc").text
                    customfields = dict()
                    for cf in threat.iter("customField"):
                        if cf.attrib["value"] != "":
                            if cf.attrib["ref"] == "SF-T-MITRE":
                                customfields = split_mitre_custom_field_threats(cf.attrib["value"])
                            elif cf.attrib["ref"] == "SF-T-STRIDE-LM":
                                customfields[CUSTOM_FIELD_STRIDE] = cf.attrib["value"]
                            else:
                                print("Custom field not valid")

                    references_th = list()
                    for reference in threat.iter("reference"):
                        if reference.attrib["url"] != "":
                            references_th.append({
                                "name": reference.attrib["name"],
                                "url": reference.attrib["url"]
                            })

                    template["threats"][threat.attrib["ref"]] = {
                        "ref": threat.attrib["ref"],
                        "name": threat.attrib["name"].rstrip(),
                        "desc": desc,
                        "customFields": customfields,
                        "references": references_th,
                        "riskRating": {
                            "C": threat.find("riskRating").attrib["confidentiality"],
                            "I": threat.find("riskRating").attrib["integrity"],
                            "A": threat.find("riskRating").attrib["availability"],
                            "EE": threat.find("riskRating").attrib["easeOfExploitation"]
                        }
                    }

                    # Now we have to add relations
                    controls_added = set()
                    for weakness in threat.iter("weakness"):
                        for control in weakness.iter("countermeasure"):
                            template["relations"].append({
                                "riskPattern": rp.attrib["ref"],
                                "usecase": usecase.attrib["ref"],
                                "threat": threat.attrib["ref"],
                                "weakness": weakness.attrib["ref"],
                                "control": control.attrib["ref"],
                                "mitigation": control.attrib["mitigation"]
                            })
                            controls_added.add(control.attrib["ref"])

                    for control in threat.find("countermeasures").iter("countermeasure"):
                        if control.attrib["ref"] not in controls_added:
                            template["relations"].append({
                                "riskPattern": rp.attrib["ref"],
                                "usecase": usecase.attrib["ref"],
                                "threat": threat.attrib["ref"],
                                "weakness": "",
                                "control": control.attrib["ref"],
                                "mitigation": control.attrib["mitigation"]
                            })
    return template


def import_rules_into_template(template, xml_text=None, root=None):
    if xml_text is not None:
        root = etree.fromstring(xml_text)
    if xml_text is None and root is None:
        print("No XML to load")
        raise typer.Exit(-1)

    comp_ref = generate_identifier_from_ref(template["component"]["ref"])
    for rule in root.iter("rule"):
        if comp_ref in rule.attrib["name"]:
            if (rule.attrib["name"].startswith("Implement countermeasure if tag")
                    and rule.attrib["module"] == "dataflow"):
                # Extract question and question desc from rule
                condition = rule.xpath(".//conditions/condition")[0]
                tag = condition.attrib["value"]

                action = rule.xpath(".//actions/action")[0]
                countermeasure = action.attrib["value"].split("_::_")[0]

                if tag not in template["controls"][countermeasure]["dataflow_tags"]:
                    template["controls"][countermeasure]["dataflow_tags"].append(tag)

            if rule.attrib["name"].startswith(f"Q - ") and " - *" not in rule.attrib["name"]:
                # Extract question and question desc from rule
                action = rule.xpath(".//actions/action")[0]
                question = action.attrib["value"].split("_::_")[2]
                question_desc = action.attrib["value"].split("_::_")[6]

                # Find control to store question
                for control_ref, control in template["controls"].items():
                    cont = generate_identifier_from_ref(control["name"])

                    if cont in rule.attrib["name"]:
                        control["question"] = question
                        control["question_desc"] = question_desc
    return template


def export_content_into_category_library(template, source_path=None, xml_text=None, root=None):
    if xml_text is not None:
        root = etree.fromstring(xml_text)
    if source_path is not None:
        tree = etree.parse(source_path)
        root = tree.getroot()
    if xml_text is None and root is None and source_path is None:
        print("No XML to load")
        raise typer.Exit(-1)

    root.attrib["revision"] = str(int(root.attrib["revision"]) + 1)
    root.find("desc").text = (f"This library contains a collection of threats and countermeasures for"
                              f" {root.attrib['name']}")
    category = root.find(f'.//categoryComponent[@ref="{template["component"]["categoryRef"]}"]')
    if category is None:
        category = etree.Element("categoryComponent")
        root.find("categoryComponents").append(category)
    category.attrib["ref"] = template['component']['categoryRef']
    category.attrib["name"] = CATEGORIES_LIST[category.attrib["ref"]]["name"]

    component_definition = root.find(f'.//componentDefinition[@ref="{template["component"]["ref"]}"]')
    if component_definition is None:
        component_definition = etree.Element("componentDefinition")
        root.find("componentDefinitions").append(component_definition)
    component_definition.attrib["ref"] = template['component']['ref']
    component_definition.attrib["name"] = template['component']['name']
    component_definition.attrib["desc"] = template['component']['desc']
    component_definition.attrib["categoryRef"] = template['component']['categoryRef']
    component_definition.attrib["visible"] = "true"

    component_risk_patterns = component_definition.find("riskPatterns")
    if component_risk_patterns is None:
        component_risk_patterns = etree.Element("riskPatterns")
        component_definition.append(component_risk_patterns)
    for rp in component_risk_patterns.iter("riskPattern"):
        component_risk_patterns.remove(rp)
    component_risk_pattern = etree.SubElement(component_risk_patterns, "riskPattern")
    component_risk_pattern.attrib["ref"] = template['riskPattern']['ref']

    # Supported standards
    for node in root.iter("supportedStandard"):
        root.find("supportedStandards").remove(node)

    supported_standards_to_add = set()
    supported_standards_to_add_ref = set()

    for control, control in template["controls"].items():
        for standard_item in control["standards"]:
            supported_standards_to_add.add(standard_item["standard-ref"])
    for std in root.iter("standard"):
        supported_standards_to_add_ref.add(std.attrib["supportedStandardRef"])

    supported_standards_node = root.find("supportedStandards")
    for std in supported_standards_to_add:
        supported_standard = etree.SubElement(supported_standards_node, "supportedStandard")
        supported_standard.attrib["ref"] = OUTPUT_NAME[std]["ref"]
        supported_standard.attrib["name"] = OUTPUT_NAME[std]["name"]

    for std in supported_standards_to_add_ref:
        output_name = [x for x in OUTPUT_NAME.values() if x["ref"] == std]
        if len(output_name) > 0:
            out = output_name[0]

            if out["ref"] not in [node.attrib["ref"] for node in root.iter("supportedStandard")]:
                supported_standard = etree.SubElement(supported_standards_node, "supportedStandard")
                supported_standard.attrib["ref"] = out["ref"]
                supported_standard.attrib["name"] = out["name"]
            else:
                pass
        else:
            print(f"[red]No name found for {std}")

    risk_pattern = root.find(f'./riskPatterns/riskPattern[@ref="{template["riskPattern"]["ref"]}"]')
    if risk_pattern is None:
        risk_pattern = create_risk_pattern_element()
        root.find("riskPatterns").append(risk_pattern)
    risk_pattern.attrib["ref"] = template['riskPattern']['ref']
    risk_pattern.attrib["name"] = template['riskPattern']['name']
    risk_pattern.attrib["desc"] = template['riskPattern']['desc']

    # First we create the nodes for countermeasures and weaknesses
    for control in template["controls"].values():
        if control["ref"] in [x["control"] for x in template["relations"]]:
            new_control = risk_pattern.find(f'./countermeasures/countermeasure[@ref="{control["ref"]}"]')
            if new_control is None:
                new_control = create_control_element()
                risk_pattern.find("countermeasures").append(new_control)
            new_control.attrib["ref"] = control["ref"]
            new_control.attrib["name"] = control["name"]
            new_control.attrib["cost"] = control["cost"]
            new_control.find("desc").text = control["desc"]

            # This removes those references from the library that are not in the template
            for ref in new_control.find("references").iter("reference"):
                if ref.attrib["name"] not in [x["name"] for x in
                                              template["controls"][control["ref"]]["references"]]:
                    new_control.find("references").remove(ref)
            for item in template["controls"][control["ref"]]["references"]:
                reference_element = new_control.find(f'./references/reference[@name="{item["name"]}"]')
                if reference_element is None:
                    reference_element = etree.SubElement(new_control.find("references"), "reference")
                    reference_element.attrib["uuid"] = str(uuid.uuid4())
                    reference_element.attrib["name"] = item["name"]
                    reference_element.attrib["url"] = item["url"]
                else:
                    reference_element.attrib["name"] = item["name"]
                    reference_element.attrib["url"] = item["url"]

            control_custom_fields = merge_custom_fields(control["customFields"], SF_C_MAP)
            for ref in new_control.find("customFields").iter("customField"):
                if ref.attrib["ref"] not in control_custom_fields:
                    new_control.find("customFields").remove(ref)
            for ref, value in control_custom_fields.items():
                cf_element = new_control.find(f'./customFields/customField[@ref="{ref}"]')
                if cf_element is None:
                    cf_element = etree.SubElement(new_control.find("customFields"), "customField")
                    cf_element.attrib["ref"] = ref
                    cf_element.attrib["value"] = value
                else:
                    cf_element.attrib["ref"] = ref
                    cf_element.attrib["value"] = value

            for ref in new_control.find("standards").iter("standard"):
                if (ref.attrib["supportedStandardRef"] + ref.attrib["ref"] not in
                        [x["standard-ref"] + x["standard-section"]
                         for x in template["controls"][control["ref"]]["standards"]]):
                    new_control.find("standards").remove(ref)
            for item in template["controls"][control["ref"]]["standards"]:
                std_element = new_control.find(f'./standards/standard[@supportedStandardRef="{item["standard-ref"]}"]')
                if std_element is None:
                    std_element = etree.SubElement(new_control.find("standards"), "standard")
                    std_element.attrib["supportedStandardRef"] = OUTPUT_NAME[item["standard-ref"]]["ref"]
                    std_element.attrib["ref"] = item["standard-section"]
                else:
                    std_element.attrib["ref"] = item["standard-section"]

    # Now we have to remove those controls that are not in the template but are present in the XML
    # This is only valid for upload operation
    for control in risk_pattern.find("countermeasures").iter("countermeasure"):
        if control.attrib["ref"] not in template["controls"]:
            risk_pattern.find("countermeasures").remove(control)

    original_cwe_weaknesses = get_original_cwe_weaknesses()
    for weakness in template["weaknesses"].values():
        if weakness["ref"] in [item["weakness"] for item in template["relations"]]:
            new_weakness = risk_pattern.find(f'./weaknesses/weakness[@ref="{weakness["ref"]}"]')
            if new_weakness is None:
                new_weakness = create_weakness_element()
                risk_pattern.find("weaknesses").append(new_weakness)
            new_weakness.attrib["ref"] = weakness["ref"]
            new_weakness.attrib["name"] = weakness["name"]
            new_weakness.find("desc").text = get_cwe_description(original_cwe_weaknesses, weakness["ref"].split(" "))
            new_weakness.attrib["impact"] = weakness["impact"]

    # We remove weaknesses not present in the template
    for weakness in risk_pattern.find("weaknesses").iter("weakness"):
        if weakness.attrib["ref"] not in template["weaknesses"]:
            risk_pattern.find("weaknesses").remove(weakness)

    # Then we add the use cases
    for relation in template["relations"]:
        new_use_case = risk_pattern.find(
            f'./usecases/usecase[@ref="{relation["usecase"]}"]')
        if new_use_case is None:
            new_use_case = create_usecase_element()
            etree.SubElement(new_use_case, "threats")
            risk_pattern.find("usecases").append(new_use_case)
        new_use_case.attrib["ref"] = relation["usecase"]
        new_use_case.attrib["name"] = template["usecases"][relation["usecase"]]["name"]
        new_use_case.attrib["desc"] = template["usecases"][relation["usecase"]]["desc"]

    # Then we add the threats
    for relation in template["relations"]:

        new_threat = risk_pattern.find(
            f'./usecases/usecase[@ref="{relation["usecase"]}"]/threats/threat[@ref="{relation["threat"]}"]')
        if new_threat is None:
            new_threat = create_threat_element()
            uc = risk_pattern.find(f"./usecases/usecase[@ref='{relation['usecase']}']")
            uc.find("threats").append(new_threat)

        new_threat.attrib["ref"] = relation["threat"]
        new_threat.attrib["name"] = template["threats"][relation["threat"]]["name"]
        new_threat.find("desc").text = template["threats"][relation["threat"]]["desc"]
        new_threat.find("riskRating").attrib["confidentiality"] = \
            template["threats"][relation["threat"]]["riskRating"]["C"]
        new_threat.find("riskRating").attrib["integrity"] = \
            template["threats"][relation["threat"]]["riskRating"]["I"]
        new_threat.find("riskRating").attrib["availability"] = \
            template["threats"][relation["threat"]]["riskRating"]["A"]
        new_threat.find("riskRating").attrib["easeOfExploitation"] = \
            template["threats"][relation["threat"]]["riskRating"]["EE"]

        # This removes those references from the library that are not in the template
        for ref in new_threat.find("references").iter("reference"):
            if ref.attrib["name"] not in [x["name"] for x in template["threats"][relation["threat"]]["references"]]:
                new_threat.find("references").remove(ref)
        for item in template["threats"][relation["threat"]]["references"]:
            reference_element = new_threat.find(f'./references/reference[@name="{item["name"]}"]')
            if reference_element is None:
                reference_element = etree.SubElement(new_threat.find("references"), "reference")
                reference_element.attrib["uuid"] = str(uuid.uuid4())
                reference_element.attrib["name"] = item["name"]
                reference_element.attrib["url"] = item["url"]
            else:
                reference_element.attrib["name"] = item["name"]
                reference_element.attrib["url"] = item["url"]

        threat_custom_fields = merge_custom_fields(template["threats"][relation["threat"]]["customFields"],
                                                   SF_T_MAP)
        for ref in new_threat.find("customFields").iter("customField"):
            if ref.attrib["ref"] not in threat_custom_fields:
                new_threat.find("customFields").remove(ref)
        for ref, value in threat_custom_fields.items():
            cf_element = new_threat.find(f'./customFields/customField[@ref="{ref}"]')
            if cf_element is None:
                cf_element = etree.SubElement(new_threat.find("customFields"), "customField")
                cf_element.attrib["ref"] = ref
                cf_element.attrib["value"] = value
            else:
                cf_element.attrib["ref"] = ref
                cf_element.attrib["value"] = value

    # We remove use cases not present in the template
    for usecase in risk_pattern.find("usecases").iter("usecase"):
        if usecase.attrib["ref"] not in template["usecases"]:
            risk_pattern.find("usecases").remove(usecase)
        else:
            for threat in usecase.find("threats").iter("threat"):
                if threat.attrib["ref"] not in template["threats"]:
                    usecase.find("threats").remove(threat)

    # Finally we add weaknesses and countermeasures inside the threats

    # We first remove any existing relations between threats and w/c
    for relation in template["relations"]:
        th = risk_pattern.find(
            f"./usecases/usecase[@ref='{relation['usecase']}']/threats/threat[@ref='{relation['threat']}']")

        th.remove(th.find("./weaknesses"))
        th.remove(th.find("./countermeasures"))
        th.append(etree.Element("weaknesses"))
        th.append(etree.Element("countermeasures"))

    for relation in template["relations"]:
        wrel = relation["weakness"]
        crel = relation["control"]

        th = risk_pattern.find(
            "./usecases/usecase[@ref='%s']/threats/threat[@ref='%s']" % (relation["usecase"], relation["threat"]))
        if wrel == "" and crel == "":
            # Nothing to do, no weakness or control in this relation
            pass

        elif wrel != "" and crel == "":
            # Empty weakness
            witem = etree.Element("weakness")
            witem.attrib["ref"] = wrel
            th.find("weaknesses").append(witem)

        elif wrel == "" and crel != "":
            # Orphaned control
            citem = etree.Element("countermeasure")
            citem.attrib["ref"] = crel
            citem.attrib["mitigation"] = relation["mitigation"]
            th.find("countermeasures").append(citem)

        else:
            # Weakness and control found
            witem = etree.Element("weakness")
            witem.attrib["ref"] = wrel
            th.find("weaknesses").append(witem)

            # It appears twice because it must be save in two different parent elements

            citem = etree.Element("countermeasure")
            citem.attrib["ref"] = crel
            citem.attrib["mitigation"] = relation["mitigation"]

            citem2 = etree.Element("countermeasure")
            citem2.attrib["ref"] = crel
            citem2.attrib["mitigation"] = relation["mitigation"]

            th.find("countermeasures").append(citem)
            cbox = etree.SubElement(witem, "countermeasures")
            cbox.append(citem2)

    output_folder = get_property("component_output_path") or get_app_dir()
    xml_library_path = os.path.join(output_folder, f"{template['component']['categoryRef']}-components.xml")
    tree = etree.ElementTree(root)
    tree.write(xml_library_path, pretty_print=True, encoding='utf-8', xml_declaration=True)


def export_rules_into_rules_library(template, source_path=None, xml_text=None, root=None):
    if xml_text is not None:
        root = etree.fromstring(xml_text)
    if source_path is not None:
        tree = etree.parse(source_path)
        root = tree.getroot()
    if xml_text is None and root is None and source_path is None:
        print("No XML to load")
        raise typer.Exit(-1)

    if "- Rules" not in root.attrib["name"]:
        root.attrib["name"] = root.attrib["name"] + " - Rules"
    root.attrib["revision"] = str(int(root.attrib["revision"]) + 1)
    root.find("desc").text = f"This library holds the rules for the components in the {root.attrib['name']} library"

    library_origin = template["component"]["categoryRef"] + "-components"
    create_rule_elements(template, root, library_origin)

    output_folder = get_property("component_output_path") or get_app_dir()
    xml_rules_library_path = os.path.join(output_folder, f"{template['component']['categoryRef']}-rules.xml")
    tree = etree.ElementTree(root)
    tree.write(xml_rules_library_path, pretty_print=True, encoding='utf-8', xml_declaration=True)


def create_local_library(xml, library_path):
    rules_library_root = etree.fromstring(xml)
    tree = etree.ElementTree(rules_library_root)
    tree.write(library_path, pretty_print=True, encoding='utf-8', xml_declaration=True)
