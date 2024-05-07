import json
from collections import defaultdict
from datetime import datetime

import jsonschema
import typer
import yaml
from rich import print
from yaml.scanner import ScannerError

from isra.src.config.config import get_resource
from isra.src.config.constants import (CUSTOM_FIELD_SCOPE, CUSTOM_FIELD_STRIDE, CUSTOM_FIELD_BASELINE_STANDARD_REF,
                                       CUSTOM_FIELD_BASELINE_STANDARD_SECTION,
                                       STRIDE_LIST, YSC_SCHEMA, CUSTOM_FIELD_ATTACK_ENTERPRISE_MITIGATION,
                                       CUSTOM_FIELD_ATTACK_ICS_MITIGATION, CUSTOM_FIELD_ATTACK_MOBILE_MITIGATION,
                                       CUSTOM_FIELD_ATLAS_MITIGATION, CUSTOM_FIELD_ATTACK_ENTERPRISE_TECHNIQUE,
                                       CUSTOM_FIELD_ATTACK_ICS_TECHNIQUE, CUSTOM_FIELD_ATTACK_MOBILE_TECHNIQUE,
                                       CUSTOM_FIELD_ATLAS_TECHNIQUE, EMPTY_TEMPLATE)
from isra.src.utils.structure_functions import build_tree_hierarchy
from isra.src.utils.xml_functions import get_cwe_description, get_original_cwe_weaknesses


def load_yaml_file(component):
    template = json.loads(EMPTY_TEMPLATE)
    with open(component, "r") as f:
        validate_yaml(f)
    with open(component, "r") as f:
        yml = yaml.safe_load(f)

        original_cwe_weaknesses = get_original_cwe_weaknesses()

        component = yml["component"]

        risk_pattern = component["risk_pattern"]
        template["component"] = {
            "ref": component["ref"],
            "name": component["name"],
            "desc": component["description"],
            "categoryRef": component["category"],
            "visible": "true",
            "riskPatternRefs": [risk_pattern["ref"]]
        }
        template["riskPattern"] = {
            "ref": risk_pattern["ref"],
            "name": risk_pattern["name"],
            "desc": risk_pattern["description"]
        }

        for th in risk_pattern["threats"]:

            if th["group"][0] in STRIDE_LIST.keys():
                use_case = STRIDE_LIST[th["group"][0]]
            else:
                use_case = template["usecases"]["General"]
            template["usecases"][use_case["ref"]] = use_case

            references_th = []
            for item in th.get("references", []):
                if item["name"] not in [None, "null", ""]:
                    references_th.append({
                        "name": item["name"],
                        "url": item["url"]
                    })

            attack_tech = "||".join(th["taxonomies"].get("attack_enterprise_technique", []))
            attack_ics_tech = "||".join(th["taxonomies"].get("attack_ics_technique", []))
            attack_mobile_tech = "||".join(th["taxonomies"].get("attack_mobile_technique", []))
            atlas_tech = "||".join(th["taxonomies"].get("atlas_technique", []))
            stride = "||".join(th["taxonomies"].get("stride", []))

            new_threat = {
                "ref": th["ref"],
                "name": th["name"],
                "desc": th["description"],
                "riskRating": {
                    "C": th["risk_score"]["confidentiality"],
                    "I": th["risk_score"]["integrity"],
                    "A": th["risk_score"]["availability"],
                    "EE": th["risk_score"]["ease_of_exploitation"]
                },
                "references": references_th,
                "customFields": {
                    CUSTOM_FIELD_ATTACK_ENTERPRISE_TECHNIQUE: attack_tech,
                    CUSTOM_FIELD_ATTACK_ICS_TECHNIQUE: attack_ics_tech,
                    CUSTOM_FIELD_ATTACK_MOBILE_TECHNIQUE: attack_mobile_tech,
                    CUSTOM_FIELD_ATLAS_TECHNIQUE: atlas_tech,
                    CUSTOM_FIELD_STRIDE: stride
                }
            }

            for c in th["countermeasures"]:
                standards = []
                for stref, stref_values in c.get("standards", {}).items():
                    for stsection in stref_values:
                        standards.append({
                            "standard-ref": stref,
                            "standard-section": stsection
                        })

                references_c = []
                for item in c.get("references", []):
                    if item["name"] not in [None, "null", ""]:
                        references_c.append({
                            "name": item["name"],
                            "url": item["url"]
                        })

                attack_mit = "||".join(c["taxonomies"].get("attack_enterprise_mitigation", []))
                attack_ics_mit = "||".join(c["taxonomies"].get("attack_ics_mitigation", []))
                attack_mobile_mit = "||".join(c["taxonomies"].get("attack_mobile_mitigation", []))
                atlas_mit = "||".join(c["taxonomies"].get("atlas_mitigation", []))
                scope = "||".join(c["taxonomies"].get("scope", []))

                new_control = {
                    "ref": c["ref"],
                    "name": c["name"],
                    "desc": c["description"],
                    "cost": c.get("cost", "2"),
                    "customFields": {
                        CUSTOM_FIELD_ATTACK_ENTERPRISE_MITIGATION: attack_mit,
                        CUSTOM_FIELD_ATTACK_ICS_MITIGATION: attack_ics_mit,
                        CUSTOM_FIELD_ATTACK_MOBILE_MITIGATION: attack_mobile_mit,
                        CUSTOM_FIELD_ATLAS_MITIGATION: atlas_mit,
                        CUSTOM_FIELD_BASELINE_STANDARD_REF: c.get("base_standard", ""),
                        CUSTOM_FIELD_BASELINE_STANDARD_SECTION: "||".join(c.get("base_standard_section", [])),
                        CUSTOM_FIELD_SCOPE: scope
                    },
                    "references": references_c,
                    "question": c.get("question", ""),
                    "question_desc": c.get("question_desc", ""),
                    "dataflow_tags": c.get("dataflow_tags", []),
                    "standards": standards
                }

                if "cwe" in c and c["cwe"] != "":
                    if c["cwe"] not in template["weaknesses"]:
                        new_weakness = {
                            "ref": c["cwe"],
                            "name": c["cwe"],
                            "desc": get_cwe_description(original_cwe_weaknesses, c["cwe"].split(" ")),
                            "impact": c.get("cwe_impact", "100")
                        }

                        template["weaknesses"][new_weakness["ref"]] = new_weakness

                new_relation = {
                    "riskPattern": risk_pattern["ref"],
                    "usecase": use_case["ref"],
                    "threat": th["ref"],
                    "weakness": c["cwe"],
                    "control": c["ref"]
                }

                template["relations"].append(new_relation)

                template["controls"][new_control["ref"]] = new_control

            template["threats"][new_threat["ref"]] = new_threat

    return template


def save_yaml_file(template):
    relation_tree = build_tree_hierarchy(template["relations"])

    threats = list()
    for rp_key, rp_value in relation_tree.items():
        for uc_key, uc_value in rp_value.items():
            for th_key, th_value in uc_value.items():
                countermeasures = list()
                for w_key, w_value in th_value.items():
                    for c_key, c_value in w_value.items():
                        standards = defaultdict(list)
                        for st in template["controls"][c_key].get("standards", []):
                            standards[st["standard-ref"]].append(st["standard-section"])
                        for k, v in standards.items():
                            standards[k] = sorted(list(dict.fromkeys(v)))
                        standards = dict(standards)

                        cwe = ""
                        cwe_impact = ""
                        if w_key != "":
                            cwe = w_key
                            cwe_impact = template["weaknesses"][w_key]["impact"]

                        base_standard_section = template["controls"][c_key]["customFields"].get(
                            CUSTOM_FIELD_BASELINE_STANDARD_SECTION, "")
                        if len(base_standard_section) == 0:
                            base_standard_section = []
                        else:
                            base_standard_section = base_standard_section.split("||")

                        scope_val = template["controls"][c_key]["customFields"].get(CUSTOM_FIELD_SCOPE, "")
                        scope = sorted(scope_val.split("||")) if scope_val else []

                        attack_enterprise_mitigation_val = template["controls"][c_key]["customFields"].get(
                            CUSTOM_FIELD_ATTACK_ENTERPRISE_MITIGATION, "")
                        attack_enterprise_mitigation = sorted(
                            attack_enterprise_mitigation_val.split("||")) if attack_enterprise_mitigation_val else []

                        attack_ics_mitigation_val = template["controls"][c_key]["customFields"].get(
                            CUSTOM_FIELD_ATTACK_ICS_MITIGATION, "")
                        attack_ics_mitigation = sorted(
                            attack_ics_mitigation_val.split("||")) if attack_ics_mitigation_val else []

                        attack_mobile_mitigation_val = template["controls"][c_key]["customFields"].get(
                            CUSTOM_FIELD_ATTACK_MOBILE_MITIGATION, "")
                        attack_mobile_mitigation = sorted(
                            attack_mobile_mitigation_val.split("||")) if attack_mobile_mitigation_val else []

                        atlas_mitigation_val = template["controls"][c_key]["customFields"].get(
                            CUSTOM_FIELD_ATLAS_MITIGATION, "")
                        atlas_mitigation = sorted(atlas_mitigation_val.split("||")) if atlas_mitigation_val else []

                        countermeasure = {
                            "ref": template["controls"][c_key]["ref"],
                            "name": template["controls"][c_key]["name"],
                            "description": template["controls"][c_key]["desc"],
                            "cost": template["controls"][c_key]["cost"],
                            "question": template["controls"][c_key].get("question", ""),
                            "question_desc": template["controls"][c_key].get("question_desc", ""),
                            "dataflow_tags": template["controls"][c_key].get("dataflow_tags", []),
                            "cwe": cwe,
                            "cwe_impact": cwe_impact,
                            "references": sorted(template["controls"][c_key].get("references", []),
                                                 key=lambda x: x['name']),
                            "taxonomies": {
                                "scope": scope,
                                "attack_enterprise_mitigation": attack_enterprise_mitigation,
                                "attack_ics_mitigation": attack_ics_mitigation,
                                "attack_mobile_mitigation": attack_mobile_mitigation,
                                "atlas_mitigation": atlas_mitigation
                            },
                            "base_standard": template["controls"][c_key]["customFields"].get(
                                CUSTOM_FIELD_BASELINE_STANDARD_REF, ""),
                            "base_standard_section": base_standard_section,
                            "standards": standards
                        }

                        countermeasures.append(countermeasure)

                stride_val = template["threats"][th_key]["customFields"].get(
                    CUSTOM_FIELD_STRIDE, "")
                stride = sorted(
                    stride_val.split("||")) if stride_val else []

                attack_enterprise_technique_val = template["threats"][th_key]["customFields"].get(
                    CUSTOM_FIELD_ATTACK_ENTERPRISE_TECHNIQUE, "")
                attack_enterprise_technique = sorted(
                    attack_enterprise_technique_val.split("||")) if attack_enterprise_technique_val else []

                attack_ics_technique_val = template["threats"][th_key]["customFields"].get(
                    CUSTOM_FIELD_ATTACK_ICS_TECHNIQUE, "")
                attack_ics_technique = sorted(
                    attack_ics_technique_val.split("||")) if attack_ics_technique_val else []

                attack_mobile_technique_val = template["threats"][th_key]["customFields"].get(
                    CUSTOM_FIELD_ATTACK_MOBILE_TECHNIQUE, "")
                attack_mobile_technique = sorted(
                    attack_mobile_technique_val.split("||")) if attack_mobile_technique_val else []

                atlas_technique_val = template["threats"][th_key]["customFields"].get(
                    CUSTOM_FIELD_ATLAS_TECHNIQUE, "")
                atlas_technique = sorted(atlas_technique_val.split("||")) if atlas_technique_val else []

                threat = {
                    "ref": template["threats"][th_key]["ref"],
                    "name": template["threats"][th_key]["name"],
                    "description": template["threats"][th_key]["desc"],
                    "group": template["usecases"][uc_key]["name"],
                    "risk_score": {
                        "confidentiality": template["threats"][th_key]["riskRating"]["C"],
                        "integrity": template["threats"][th_key]["riskRating"]["I"],
                        "availability": template["threats"][th_key]["riskRating"]["A"],
                        "ease_of_exploitation": template["threats"][th_key]["riskRating"]["EE"]
                    },
                    "references": sorted(template["threats"][th_key].get("references", []), key=lambda x: x['name']),
                    "taxonomies": {
                        "stride": stride,
                        "attack_enterprise_technique": attack_enterprise_technique,
                        "attack_ics_technique": attack_ics_technique,
                        "attack_mobile_technique": attack_mobile_technique,
                        "atlas_technique": atlas_technique
                    },
                    "question": template["threats"][th_key].get("question", ""),
                    "question_desc": template["threats"][th_key].get("question_desc", ""),
                    "countermeasures": countermeasures
                }

                threats.append(threat)

    root = {
        "component": {
            "ref": template['component']['ref'],
            "name": template['component']['name'],
            "description": template['component']['desc'],
            "category": template['component']['categoryRef'],
            "last_review": datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
            "risk_pattern": {
                "ref": template['riskPattern']['ref'],
                "name": template['riskPattern']['name'],
                "description": template['riskPattern']['desc'],
                "type": "static",
                "threats": threats
            }
        }
    }
    return root


def validate_yaml(file):
    try:
        output = yaml.safe_load(file)
    except ScannerError as e:
        print("[red]An error happened when parsing the YAML file. Reason:")
        print(e)
        raise typer.Exit(-1)

    schema = get_resource(YSC_SCHEMA, filetype="json")

    validator = jsonschema.Draft7Validator(schema)
    if not validator.is_valid(output):
        print(f"[red]YSC doesn't fit schema: ")
        for error in sorted(validator.iter_errors(output), key=str):
            print(f"Field: {error.json_path}")
            error_message = error.message
            if error.schema.get("message") is not None:
                error_message = error.schema.get("message").get("pattern") + " -> " + error.instance
            print(f'Reason: {error_message}')
        raise typer.Exit(-1)
