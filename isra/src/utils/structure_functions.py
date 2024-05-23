"""
This script holds some functions that can be used to generate alternative data structures when needed
"""


def build_new_threat():
    return {
        "ref": "",
        "name": "",
        "desc": "",
        "customFields": {},
        "references": [],
        "riskRating": {
            "C": "100",
            "I": "100",
            "A": "100",
            "EE": "100"
        }
    }


def build_new_control():
    return {
        "ref": "",
        "name": "",
        "desc": "",
        "cost": "2",
        "question": "",
        "question_desc": "",
        "dataflow_tags": [],
        "customFields": dict(),
        "references": [],
        "standards": []
    }


def build_tree_hierarchy(objects):
    tree = {}

    for obj in objects:
        current_level = tree
        for key, value in obj.items():
            if value not in current_level:
                current_level[value] = {}
            current_level = current_level[value]

    return tree
