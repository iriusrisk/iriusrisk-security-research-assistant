"""
This script holds some functions that can be used to generate alternative data structures when needed
"""


def build_tree_hierarchy(objects):
    tree = {}

    for obj in objects:
        current_level = tree
        for key, value in obj.items():
            if value not in current_level:
                current_level[value] = {}
            current_level = current_level[value]

    return tree
