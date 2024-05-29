from datetime import datetime

import jsonschema
import typer
import yaml
from rich import print
from yaml.scanner import ScannerError

from isra.src.config.config import get_resource
from isra.src.v2.constants2 import (YSC_SCHEMA)
from isra.src.v2.Component import Component
from isra.src.v2.Control import Control
from isra.src.v2.RiskPattern import RiskPattern
from isra.src.v2.Template import Template
from isra.src.v2.Threat import Threat
from isra.src.utils.cwe_functions import get_cwe_impact
from isra.src.utils.xml_functions import get_original_cwe_weaknesses


def load_yaml_file(component):
    template = Template()
    with open(component, "r") as f:
        validate_yaml(f)
    with open(component, "r") as f:
        yml = yaml.safe_load(f)

        original_cwe_weaknesses = get_original_cwe_weaknesses()

        component = yml["component"]

        risk_pattern = component["risk_pattern"]

        t_component = Component(
            ref=component["ref"],
            name=component["name"].rstrip(),
            description=component["description"],
            category=component["category"],
        )
        template.set_component(t_component)

        t_risk_pattern = RiskPattern(
            ref=risk_pattern["ref"],
            name=risk_pattern["name"].rstrip(),
            description=risk_pattern["description"],
        )
        template.set_risk_pattern(t_risk_pattern)

        for th in risk_pattern["threats"]:

            new_threat = Threat(
                ref=th["ref"],
                name=th["name"].rstrip(),
                description=th["description"],
            )

            for c in th["countermeasures"]:

                new_control = Control(
                    ref=c["ref"],
                    name=c["name"].rstrip(),
                    description=c["description"],
                )

                template.get_controls().append(new_control)

            template.get_threats().append(new_threat)

    return template


def save_yaml_file(template: Template):
    original_cwe_weaknesses = get_original_cwe_weaknesses()

    component = template.get_component()
    risk_pattern = template.get_risk_pattern()

    relation_tree = template.build_tree()

    threats = list()
    for rp_key, rp_value in relation_tree.items():
        for uc_key, uc_value in rp_value.items():
            for th_key, th_value in uc_value.items():
                countermeasures = list()
                for w_key, w_value in th_value.items():
                    for c_key, c_value in w_value.items():
                        control = template.get_control(c_key)

                        cwe_impact = get_cwe_impact(original_cwe_weaknesses, w_key.replace("CWE-", ""))
                        countermeasure = {
                            "ref": control.get_ref(),
                            "name": control.get_name(),
                            "description": control.get_description(),
                            "cost": control.get_cost(),
                            "question": control.get_question(),
                            "question_desc": control.get_question_desc(),
                            "dataflow_tags": control.get_dataflow_tags(),
                            "cwe": w_key,
                            "cwe_impact": cwe_impact if w_key != "" else "",
                            "references": [x.to_dict() for x in sorted(control.get_references())],
                            "taxonomies": {tx.get_ref(): tx.get_values() for tx in control.get_taxonomies()},
                            "base_standard": control.get_base_standard().get_ref(),
                            "base_standard_section": list(control.get_base_standard().get_sections()),
                            "standards": {st.get_ref(): st.get_sections() for st in control.get_standards()}
                        }

                        countermeasures.append(countermeasure)

                threat = template.get_threat(th_key)

                threat = {
                    "ref": threat.get_ref(),
                    "name": threat.get_name(),
                    "description": threat.get_description(),
                    "group": uc_key,  # threat.get_group(),
                    "risk_score": {
                        "confidentiality": threat.get_risk_score().get_confidentiality(),
                        "integrity": threat.get_risk_score().get_integrity(),
                        "availability": threat.get_risk_score().get_availability(),
                        "ease_of_exploitation": threat.get_risk_score().get_ease_of_exploitation()
                    },
                    "references": [x.to_dict() for x in sorted(threat.get_references())],
                    "taxonomies": {tx.get_ref(): tx.get_values() for tx in threat.get_taxonomies()},
                    "question": threat.get_question(),
                    "question_desc": threat.get_question_desc(),
                    "countermeasures": countermeasures
                }

                threats.append(threat)

    root = {
        "component": {
            "ref": component.get_ref(),
            "name": component.get_name(),
            "description": component.get_description(),
            "category": component.get_category(),
            "last_review": datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
            "risk_pattern": {
                "ref": risk_pattern.get_ref(),
                "name": risk_pattern.get_name(),
                "description": risk_pattern.get_description(),
                "type": risk_pattern.get_type(),
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
