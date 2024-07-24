import difflib
import logging
import os

import itertools
from lxml import etree

# Settings

libFolder = "C:\\CS\\Workspace\\ir-sc-tests\\libraries\\v1"
v2_components_xml = "C:\\CS\\Workspace\\ir-sc-tests\\libraries\\v2"
modify_original_folder = False

logger = logging.getLogger('logger')
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
logger.addHandler(ch)


# Aux functions

def find_closest_match(input_word, word_list, cutoff=0.6):
    # Find the closest matching word in the list using difflib
    lword = input_word.lower()
    lpos = {}
    for p in word_list:
        if p.lower() not in lpos:
            lpos[p.lower()] = [p]
        else:
            lpos[p.lower()].append(p)
    lmatches = difflib.get_close_matches(lword, lpos.keys(), n=6, cutoff=cutoff)
    ret = [lpos[m] for m in lmatches]
    ret = itertools.chain.from_iterable(ret)
    return list(set(ret))


if __name__ == "__main__":

    to_replace = set()
    with open("to_replace.txt", "r") as f:
        for line in f.read().splitlines():
            to_replace.add(line)

    v2_components = []
    for library in os.listdir(str(v2_components_xml)):
        if library.endswith(".xml"):
            tree = etree.parse(os.path.join(v2_components_xml, library))
            root = tree.getroot()
            for cd in root.find("componentDefinitions").iter("componentDefinition"):
                v2_components.append((cd.attrib["ref"], cd.attrib["name"]))

    for library in os.listdir(str(libFolder)):
        if library.endswith(".xml"):
            tree = etree.parse(os.path.join(libFolder, library))
            root = tree.getroot()
            logger.debug(root.attrib["ref"])

            modified = False

            for cd in root.find("componentDefinitions").iter("componentDefinition"):
                if cd.attrib["categoryRef"] == "system-deprecated":
                    logger.debug(f"Already deprecated: {cd.attrib['ref']}")
                    continue
                # If the name is exactly the same of one in the v2 component library
                mark_as_deprecated = False
                if cd.attrib["name"] in [x[1] for x in v2_components]:
                    mark_as_deprecated = True

                closest_match = find_closest_match(cd.attrib["name"], [x[1] for x in v2_components], cutoff=0.8)
                # logger.debug(cd.attrib["name"])

                if len(closest_match) > 0:
                    logger.info(f"This component {cd.attrib['name']} may be this one")
                    logger.info(closest_match)

                if cd.attrib["ref"] in to_replace:
                    mark_as_deprecated = True

                if mark_as_deprecated:
                    cd.attrib["categoryRef"] = "system-deprecated"
                    cd.attrib["name"] = "Deprecated - " + cd.attrib["name"]
                    logger.info(cd.attrib['name'])
                    cd.attrib["desc"] = ("This component has been marked as deprecated. This component is not "
                                         "maintained and will be removed in the future.")
                    modified = True

            if modified:
                if "system-deprecated" not in [x.attrib["ref"] for x in root.iter("categoryComponent")]:
                    new_cat = etree.SubElement(root.find("categoryComponents"), "categoryComponent")
                    new_cat.attrib["uuid"] = "1217c6b1-10f6-44ba-81f5-7524d3b3ca35"
                    new_cat.attrib["ref"] = "system-deprecated"
                    new_cat.attrib["name"] = "Deprecated"

                if "Legacy" not in root.attrib["name"]:
                    root.attrib["name"] = "Legacy - " + root.attrib["name"]
                root.attrib["revision"] = str(int(root.attrib["revision"]) + 1)
                root.find(
                    "desc").text = ("This library will be labeled Legacy as we make updates. It will still be "
                                    "available but won't be regularly updated.")

                if modify_original_folder:
                    tree.write(os.path.join(libFolder, library))
                else:
                    tree.write("updated/" + library)
            else:
                logger.debug("Library not modified")
