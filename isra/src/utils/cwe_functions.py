"""
This script holds all the function that are related with data extraction from CWE
"""
from lxml import etree

from isra.src.config.config import get_resource
from isra.src.config.constants import CWE_SOURCE_FILE


def ns(element):
    return "{http://cwe.mitre.org/cwe-7}" + element


def get_cwe_impact(original_cwe_weaknesses, cwe_id):
    impact = "100"
    likelihood = original_cwe_weaknesses[cwe_id].find(ns("Likelihood_Of_Exploit"))
    if likelihood is not None:
        likelihood_value = likelihood.text
        calculated_impact = {
            "High": "75",
            "Medium": "50",
            "Low": "25"
        }

        impact = calculated_impact[likelihood_value]

    return impact


def get_cwe_description(weaknesses, ids):
    final_desc = "CWE:"

    for cwe_id in ids:
        id_number = cwe_id.split("-")[1]
        if id_number in weaknesses:
            weakness = weaknesses[id_number]
            description, extended_desc = "", ""
            if weakness.find(ns("Description")) is not None:
                description = weakness.find(ns("Description")).text
            if weakness.find(ns("Extended_Description")) is not None:
                extended_desc = weakness.find(ns("Extended_Description")).text
            final_desc = f"{final_desc}\n{cwe_id}: {weakness.attrib['Name']}\n{description}\n{extended_desc}"
        else:
            print(f"{cwe_id} is not a valid CWE. Try to avoid using CWE categories and pillars")

    return final_desc


def get_original_cwe_weaknesses():
    cwe_xml_path = get_resource(CWE_SOURCE_FILE, filetype="path")
    tree = etree.parse(cwe_xml_path)
    root = tree.getroot()

    class_base_weaknesses = dict()
    for weakness in root.find(ns("Weaknesses")).iter(ns("Weakness")):
        if weakness.attrib["Status"] != "Obsolete":
            class_base_weaknesses[weakness.attrib["ID"]] = weakness

    return class_base_weaknesses


def set_weakness(template, control_ref, cwe_id, action="init"):
    original_cwe_weaknesses = get_original_cwe_weaknesses()
    if cwe_id not in original_cwe_weaknesses:
        print(f"Weakness {cwe_id} has not been found in the internal CWE list")
    else:
        for rel in template["relations"]:
            if action == "init":
                if rel["control"] == control_ref and rel["weakness"] == "" and cwe_id in original_cwe_weaknesses:
                    rel["weakness"] = f"CWE-{cwe_id}"

                    final_desc = get_cwe_description(original_cwe_weaknesses, [rel["weakness"]])
                    final_impact = get_cwe_impact(original_cwe_weaknesses, cwe_id)

                    template["weaknesses"][rel["weakness"]] = {
                        "ref": rel["weakness"],
                        "name": rel["weakness"],  # Before: class_base_weaknesses[cwe_id].attrib["Name"],
                        "desc": final_desc,
                        "impact": final_impact
                    }
            elif action == "replace":
                if rel["control"] == control_ref and cwe_id in original_cwe_weaknesses:
                    rel["weakness"] = f"CWE-{cwe_id}"

                    final_desc = get_cwe_description(original_cwe_weaknesses, [rel["weakness"]])
                    final_impact = get_cwe_impact(original_cwe_weaknesses, cwe_id)

                    template["weaknesses"][rel["weakness"]] = {
                        "ref": rel["weakness"],
                        "name": rel["weakness"],  # Before: class_base_weaknesses[cwe_id].attrib["Name"],
                        "desc": final_desc,
                        "impact": final_impact
                    }
            else:
                pass


def generate_cwe_jsonl():
    cwe_xml_path = get_resource(CWE_SOURCE_FILE, filetype="path")
    tree = etree.parse(cwe_xml_path)
    root = tree.getroot()

    with open("cwe.jsonl", "w") as f:
        for weakness in root.find(ns("Weaknesses")).iter(ns("Weakness")):
            if weakness.attrib["Abstraction"] in ["Class", "Base"]:
                description, extended_desc = "", ""

                if weakness.find(ns("Description")) is not None:
                    description = weakness.find(ns("Description")).text
                if weakness.find(ns("Extended_Description")) is not None:
                    extended_desc = weakness.find(ns("Extended_Description")).text
                final_desc = description + "\n" + extended_desc

                f.write(
                    '{"id":"' + weakness.attrib["ID"] + '", "name":"' + weakness.attrib["Name"] + '", "description":"' +
                    final_desc
                    .replace("\n", "")
                    .replace("\t", "")
                    .replace("\"", "\'")
                    .replace("\\", "\\\\") + '"}')
                f.write("\n")


def get_allowed_cwe_ids():
    original_cwe_weaknesses = get_original_cwe_weaknesses()

    allowed_values = list()
    for k, v in original_cwe_weaknesses.items():
        if v.attrib["Status"] != "Obsolete":
            allowed_values.append(k)

    print(len(allowed_values))
    print(str(allowed_values))