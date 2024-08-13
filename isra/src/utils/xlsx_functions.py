import ast
import json
from datetime import datetime

import pandas as pd

from isra.src.config.constants import EMPTY_TEMPLATE, CUSTOM_FIELD_STANDARD_BASELINE_SECTION, \
    CUSTOM_FIELD_STANDARD_BASELINE_REF, CUSTOM_FIELD_ATTACK_ENTERPRISE_MITIGATION, CUSTOM_FIELD_ATTACK_ICS_MITIGATION, \
    CUSTOM_FIELD_ATTACK_MOBILE_MITIGATION, CUSTOM_FIELD_ATLAS_MITIGATION, CUSTOM_FIELD_SCOPE, \
    CUSTOM_FIELD_ATTACK_ENTERPRISE_TECHNIQUE, CUSTOM_FIELD_ATTACK_ICS_TECHNIQUE, CUSTOM_FIELD_ATTACK_MOBILE_TECHNIQUE, \
    CUSTOM_FIELD_ATLAS_TECHNIQUE, CUSTOM_FIELD_STRIDE, STRIDE_LIST
from isra.src.utils.cwe_functions import get_cwe_description, get_original_cwe_weaknesses
from isra.src.utils.structure_functions import build_tree_hierarchy


def extract_from_sheet(df):
    return df[df.columns].astype(str).to_dict(orient='records')


def get_string(value):
    output = ""
    if value != "" and not pd.isna(value) and value.lower() != "nan":
        output = value
    return str(output)

def get_values(mylist, ref, name):
    list_of_values = []
    for element in mylist:
        if element["ref"] == ref and element["name"] == name:
            value = get_string(element["value"])
            if value != "":
                list_of_values.append(value)

    return list_of_values


def load_xlsx_file(component):
    template = json.loads(EMPTY_TEMPLATE)

    df1 = pd.read_excel(component, sheet_name="Component")
    df2 = pd.read_excel(component, sheet_name="RiskPattern")
    df3 = pd.read_excel(component, sheet_name="Threat")
    df4 = pd.read_excel(component, sheet_name="Countermeasure")
    df5 = pd.read_excel(component, sheet_name="Reference")
    df6 = pd.read_excel(component, sheet_name="Taxonomy")

    original_cwe_weaknesses = get_original_cwe_weaknesses()

    component = extract_from_sheet(df1)[0]
    risk_pattern = extract_from_sheet(df2)[0]
    template["component"] = {
        "ref": component["ref"],
        "name": component["name"].rstrip(),
        "desc": component["description"],
        "categoryRef": component["category"],
        "visible": "true",
        "riskPatternRefs": [risk_pattern["ref"]]
    }
    template["riskPattern"] = {
        "ref": risk_pattern["ref"],
        "name": risk_pattern["name"].rstrip(),
        "desc": risk_pattern["description"]
    }

    references_sheet = extract_from_sheet(df5)
    taxonomies_sheet = extract_from_sheet(df6)

    for th in extract_from_sheet(df3):

        if th["group"][0] in STRIDE_LIST.keys():
            use_case = STRIDE_LIST[th["group"][0]]
        else:
            use_case = template["usecases"]["General"]
        template["usecases"][use_case["ref"]] = use_case

        references_th = []

        for reference in references_sheet:
            if reference["ref"] == th["ref"]:
                references_th.append({
                    "name": reference["name"],
                    "url": reference["url"]
                })

        attack_tech = "||".join(get_values(taxonomies_sheet, th["ref"], CUSTOM_FIELD_ATTACK_ENTERPRISE_TECHNIQUE))
        attack_ics_tech = "||".join(get_values(taxonomies_sheet, th["ref"], CUSTOM_FIELD_ATTACK_ICS_TECHNIQUE))
        attack_mobile_tech = "||".join(get_values(taxonomies_sheet, th["ref"], CUSTOM_FIELD_ATTACK_MOBILE_TECHNIQUE))
        atlas_tech = "||".join(get_values(taxonomies_sheet, th["ref"], CUSTOM_FIELD_ATLAS_TECHNIQUE))
        stride = "||".join(get_values(taxonomies_sheet, th["ref"], CUSTOM_FIELD_STRIDE))

        new_threat = {
            "ref": th["ref"],
            "name": th["name"].rstrip(),
            "desc": th["description"],
            "riskRating": {
                "C": th["confidentiality"],
                "I": th["integrity"],
                "A": th["availability"],
                "EE": th["ease_of_exploitation"]
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

        for c in extract_from_sheet(df4):
            if c["threat"] != th["ref"]:
                continue
            standards = []
            # for stref, stref_values in c.get("standards", {}).items():
            #     for stsection in stref_values:
            #         standards.append({
            #             "standard-ref": stref,
            #             "standard-section": stsection
            #         })
            #
            references_c = []

            for reference in references_sheet:
                if reference["ref"] == c["ref"]:
                    references_c.append({
                        "name": reference["name"],
                        "url": reference["url"]
                    })

            attack_mit = "||".join(get_values(taxonomies_sheet, c["ref"], CUSTOM_FIELD_ATTACK_ENTERPRISE_MITIGATION))
            attack_ics_mit = "||".join(get_values(taxonomies_sheet, c["ref"], CUSTOM_FIELD_ATTACK_ICS_MITIGATION))
            attack_mobile_mit = "||".join(get_values(taxonomies_sheet, c["ref"], CUSTOM_FIELD_ATTACK_MOBILE_MITIGATION))
            atlas_mit = "||".join(get_values(taxonomies_sheet, c["ref"], CUSTOM_FIELD_ATLAS_MITIGATION))
            scope = "||".join(get_values(taxonomies_sheet, c["ref"], CUSTOM_FIELD_SCOPE))

            base_standard_sections_string = c.get("base_standard_section", "")
            base_standard_sections = []
            if base_standard_sections_string != "" and not pd.isna(
                    base_standard_sections_string) and base_standard_sections_string != "nan":
                base_standard_sections = ast.literal_eval(base_standard_sections_string)
            dataflow_tags_string = c.get("dataflow_tags", "")
            dataflow_tags = []
            if dataflow_tags_string != "" and not pd.isna(dataflow_tags_string) and dataflow_tags_string != "nan":
                dataflow_tags = ast.literal_eval(dataflow_tags_string)

            new_control = {
                "ref": c["ref"],
                "name": c["name"].rstrip(),
                "desc": c["description"],
                "cost": get_string(c.get("cost", "2")),
                "customFields": {
                    CUSTOM_FIELD_ATTACK_ENTERPRISE_MITIGATION: attack_mit,
                    CUSTOM_FIELD_ATTACK_ICS_MITIGATION: attack_ics_mit,
                    CUSTOM_FIELD_ATTACK_MOBILE_MITIGATION: attack_mobile_mit,
                    CUSTOM_FIELD_ATLAS_MITIGATION: atlas_mit,
                    CUSTOM_FIELD_STANDARD_BASELINE_REF: c.get("base_standard", ""),
                    CUSTOM_FIELD_STANDARD_BASELINE_SECTION: "||".join(base_standard_sections),
                    CUSTOM_FIELD_SCOPE: scope
                },
                "references": references_c,
                "question": get_string(c.get("question", "")).rstrip(),
                "question_desc": get_string(c.get("question_desc", "")),
                "dataflow_tags": dataflow_tags,
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


def save_xlsx_file(xlsx_template_path, template):
    with pd.ExcelWriter(xlsx_template_path, engine='xlsxwriter') as writer:
        # Create three empty DataFrames
        df1 = pd.DataFrame(columns=["ref", "name", "description", "category", "last_review"])
        df2 = pd.DataFrame(columns=["component", "ref", "name", "description", "type"])
        df3 = pd.DataFrame(
            columns=["risk_pattern", "ref", "name", "description", "group", "confidentiality", "integrity",
                     "availability", "ease_of_exploitation", "question", "question_desc"])
        df4 = pd.DataFrame(
            columns=["threat", "ref", "name", "description", "cost", "question", "question_desc", "cwe", "cwe_impact",
                     "base_standard", "base_standard_section", "dataflow_tags"])
        df5 = pd.DataFrame(columns=["ref", "name", "url"])
        df6 = pd.DataFrame(columns=["ref", "name", "value"])

        relation_tree = build_tree_hierarchy(template["relations"])

        risk_patterns = list()
        threats = list()
        countermeasures = list()
        references = list()
        taxonomies = list()

        data1 = {
            "ref": template["component"]["ref"],
            "name": template["component"]["name"],
            "description": template["component"]["desc"],
            "category": template["component"]["categoryRef"],
            "last_review": datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
        }
        df1 = pd.concat([df1, pd.DataFrame([data1], columns=df1.columns)], ignore_index=True)

        for rp_key, rp_value in relation_tree.items():

            risk_patterns.append({
                "component": template["component"]["ref"],
                "ref": template["riskPattern"]["ref"],
                "name": template["riskPattern"]["name"],
                "description": template["riskPattern"]["desc"],
                "type": "static"
            })

            for uc_key, uc_value in rp_value.items():
                for th_key, th_value in uc_value.items():

                    threats.append({
                        "risk_pattern": template["riskPattern"]["ref"],
                        "ref": template["threats"][th_key]["ref"],
                        "name": template["threats"][th_key]["name"],
                        "description": template["threats"][th_key]["desc"],
                        "group": template["usecases"][uc_key]["name"],
                        "confidentiality": template["threats"][th_key]["riskRating"]["C"],
                        "integrity": template["threats"][th_key]["riskRating"]["I"],
                        "availability": template["threats"][th_key]["riskRating"]["A"],
                        "ease_of_exploitation": template["threats"][th_key]["riskRating"]["EE"],
                        "question": template["threats"][th_key].get("question", ""),
                        "question_desc": template["threats"][th_key].get("question_desc", "")
                    })

                    for reference in template["threats"][th_key]["references"]:
                        references.append({"ref": template["threats"][th_key]["ref"],
                                           "name": reference["name"],
                                           "url": reference["url"]})

                    for customField, customFieldValues in template["threats"][th_key]["customFields"].items():
                        for value in customFieldValues.split("||"):
                            taxonomies.append({"ref": template["threats"][th_key]["ref"],
                                               "name": customField,
                                               "value": value})

                    for w_key, w_value in th_value.items():
                        for c_key, c_value in w_value.items():

                            cwe = ""
                            cwe_impact = ""
                            if w_key != "":
                                cwe = w_key
                                cwe_impact = template["weaknesses"][w_key]["impact"]

                            base_standard_section = template["controls"][c_key]["customFields"].get(
                                CUSTOM_FIELD_STANDARD_BASELINE_SECTION, "")
                            if len(base_standard_section) == 0:
                                base_standard_section = []
                            else:
                                base_standard_section = base_standard_section.split("||")

                            countermeasures.append({
                                "threat": template["threats"][th_key]["ref"],
                                "ref": template["controls"][c_key]["ref"],
                                "name": template["controls"][c_key]["name"],
                                "description": template["controls"][c_key]["desc"],
                                "cost": template["controls"][c_key].get("cost", ""),
                                "question": template["controls"][c_key].get("question", ""),
                                "question_desc": template["controls"][c_key].get("question_desc", ""),
                                "cwe": cwe,
                                "cwe_impact": cwe_impact,
                                "base_standard": template["controls"][c_key]["customFields"].get(
                                    CUSTOM_FIELD_STANDARD_BASELINE_REF, ""),
                                "base_standard_section": base_standard_section
                            })

                            for reference in template["controls"][c_key]["references"]:
                                references.append({"ref": template["controls"][c_key]["ref"],
                                                   "name": reference["name"],
                                                   "url": reference["url"]})

                            for customField, customFieldValues in template["controls"][c_key]["customFields"].items():
                                for value in customFieldValues.split("||"):
                                    taxonomies.append({"ref": template["controls"][c_key]["ref"],
                                                       "name": customField,
                                                       "value": value})

        df2 = pd.concat([df2, pd.DataFrame(risk_patterns, columns=df2.columns)], ignore_index=True)
        df3 = pd.concat([df3, pd.DataFrame(threats, columns=df3.columns)], ignore_index=True)
        df4 = pd.concat([df4, pd.DataFrame(countermeasures, columns=df4.columns)], ignore_index=True)
        df5 = pd.concat([df5, pd.DataFrame(references, columns=df5.columns)], ignore_index=True)
        df6 = pd.concat([df6, pd.DataFrame(taxonomies, columns=df6.columns)], ignore_index=True)

        # Write each DataFrame to a different worksheet.
        df1.to_excel(writer, sheet_name='Component')
        df2.to_excel(writer, sheet_name='RiskPattern')
        df3.to_excel(writer, sheet_name='Threat')
        df4.to_excel(writer, sheet_name='Countermeasure')
        df5.to_excel(writer, sheet_name='Reference')
        df6.to_excel(writer, sheet_name='Taxonomy')
