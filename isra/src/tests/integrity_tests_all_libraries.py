import os
import html
import logging
import lxml.etree as etree
from bs4 import BeautifulSoup
from collections import Counter


# Creating a logger
logging.basicConfig(filename="logFile.log",
                    format='%(asctime)s  %(levelname)-10s %(message)s',
                    datefmt="%Y-%m-%d-%H-%M-%S",
                    filemode='w')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def findNonASCIIWords(data):
    words = []
    if data is not None:
        decodedData = html.unescape(data)
    else:
        decodedData = ""

    soup = BeautifulSoup(decodedData, 'html.parser')
    text = soup.find_all(string=True)

    output = ''
    blacklist = [
        'style'
    ]

    for t in text:
        if t.parent.name not in blacklist:
            output += '{} '.format(t)

    datas = output.split()
    for t in datas:
        if not t.isascii():
            words.append(t)

    return words


def checkAscii(roots):
    errors = []

    for root in roots.values():
        for component in root.find("riskPatterns").iter("riskPattern"):

            for control in component.find("countermeasures").iter("countermeasure"):
                words = findNonASCIIWords(control.find("desc").text)
                for word in words:
                    errors.append(
                        f"Component: '{component.attrib['ref']}': Control: " + control.attrib[
                            "ref"] + " ->The following string is not ASCII: " + word)
            for weakness in component.find("weaknesses").iter("weakness"):
                words = findNonASCIIWords(weakness.find("desc").text)
                for word in words:
                    errors.append(
                        f"Component: '{component.attrib['ref']}': Weakness: " + weakness.attrib[
                            "ref"] + " ->The following string is not ASCII: " + word)
            for usecase in component.iter('usecase'):
                words = findNonASCIIWords(usecase.attrib['desc'])
                for word in words:
                    errors.append(
                        f"Component: '{component.attrib['ref']}': Use case: " + usecase.attrib[
                            "ref"] + " ->The following string is not ASCII: " + word)

                for threat in usecase.iter('threat'):
                    words = findNonASCIIWords(threat.find("desc").text)
                    for word in words:
                        errors.append(
                            f"Component: '{component.attrib['ref']}': Threat: " + threat.attrib[
                                "ref"] + " ->The following string is not ASCII: " + word)

    return errors


def checkDuplicatedComponentsFromLibrary(path_libraries):
    errors = []
    riskpatterns = list()

    for library in os.listdir(str(path_libraries)):
        if library.endswith(".xml"):
            root = etree.parse(str(path_libraries / library))

            for rp in root.find("riskPatterns").iter("riskPattern"):
                riskpatterns.append(rp.attrib['ref'])

    counter = Counter(riskpatterns)
    for k, v in counter.items():
        if v > 1:
            errors.append(f"Component {k} appears {v} times")

    return errors


def findErrors(itemList, tags):
    errors = []
    for itemRef, itemDuplicated in itemList.items_v1():
        if len(itemDuplicated) > 1:
            pivot = itemDuplicated[0]
            tagsFailed = []

            for duplicated in itemDuplicated[1:]:
                for i in range(2, len(tags)):
                    if duplicated[i] != pivot[i]:
                        if tags[i] not in tagsFailed:
                            tagsFailed.append(tags[i])

            if tagsFailed:
                errors.append(f"{itemRef} -> The following tags are not the same in all elements: {tagsFailed}")

    return errors


def checkDuplicatedThreatsWithDifferentData(roots):
    itemList = dict()
    tags = ["library", "ref", "name", "state", "source", "libraryAttribute", "desc", "confidentiality",
            "integrity", "availability", "easeOfExploitation",
            "references"]

    for root in roots.values():
        library = root.getroot().attrib['ref']
        for component in root.find("riskPatterns").iter("riskPattern"):
            for threat in component.iter("threat"):
                ref = threat.attrib['ref']
                if ref not in itemList.keys():
                    itemList[ref] = []
                itemList[ref].append([
                    library,
                    threat.attrib['ref'],
                    threat.attrib['name'],
                    threat.attrib['state'],
                    threat.attrib['source'],
                    threat.attrib['library'],
                    threat.find('desc').text,
                    threat.find('riskRating').attrib['confidentiality'],
                    threat.find('riskRating').attrib['integrity'],
                    threat.find('riskRating').attrib['availability'],
                    threat.find('riskRating').attrib['easeOfExploitation'],
                    str(sorted([[r.attrib['name'], r.attrib['url']] for r in
                                threat.find('references').iter('reference')]))
                ]
                )

    return findErrors(itemList, tags)


def checkDuplicatedWeaknessesWithDifferentData(roots):
    itemList = dict()
    tags = ["library", "ref", "name", "state", "impact", "desc", "expiryDate", "expiryPeriod", "steps", "notes",
            "references"]

    for root in roots.values():
        library = root.getroot().attrib['ref']
        for component in root.find("riskPatterns").iter("riskPattern"):
            for weakness in component.find("weaknesses").iter("weakness"):
                ref = weakness.attrib['ref']
                if ref not in itemList.keys():
                    itemList[ref] = []
                itemList[ref].append([
                    library,
                    weakness.attrib['ref'],
                    weakness.attrib['name'],
                    weakness.attrib['state'],
                    weakness.attrib['impact'],
                    weakness.find('desc').text,
                    weakness.find('test').attrib['expiryDate'],
                    weakness.find('test').attrib['expiryPeriod'],
                    weakness.find('test').find('steps').text,
                    weakness.find('test').find('notes').text,
                    str(sorted([[r.attrib['name'], r.attrib['url']] for r in
                                weakness.find('test').find('references').iter('reference')]))
                ]
                )

    return findErrors(itemList, tags)


def checkDuplicatedControlsWithDifferentData(roots):
    itemList = dict()
    tags = ["library", "ref", "name", "platform", "cost", "risk", "state", "libraryAttribute",
            "sourceAttribute",
            "desc", "expiryDate", "expiryPeriod", "steps", "notes", 
            "testReferences", "standards", "references", "implementations"]

    for root in roots.values():
        library = root.getroot().attrib['ref']
        for component in root.find("riskPatterns").iter("riskPattern"):
            for control in component.find("countermeasures").iter("countermeasure"):
                ref = control.attrib['ref']
                if ref not in itemList.keys():
                    itemList[ref] = []
                itemList[ref].append([
                    library,
                    control.attrib['ref'],
                    control.attrib['name'],
                    control.attrib['platform'],
                    control.attrib['cost'],
                    control.attrib['risk'],
                    control.attrib['state'],
                    control.attrib['library'],
                    control.attrib['source'],
                    control.find('desc').text,
                    control.find('test').attrib['expiryDate'],
                    control.find('test').attrib['expiryPeriod'],
                    control.find('test').find('steps').text,
                    control.find('test').find('notes').text,
                    str(sorted([[r.attrib['name'], r.attrib['url']] for r in
                                control.find('test').find('references').iter('reference')])),
                    str(sorted([[r.attrib['ref'], r.attrib['supportedStandardRef']] for r in
                                control.find('standards').iter('standard')])),
                    str(sorted([[r.attrib['name'], r.attrib['url']] for r in
                                control.find('references').iter('reference')])),
                    str(sorted([r.attrib['platform'] for r in
                                control.find('implementations').iter('implementation')])),
                ]
                )

    return findErrors(itemList, tags)


def checkInconsistentControlNames(roots):
    errors = []

    controls = dict()
    for root in roots.values():
        for component in root.find("riskPatterns").iter("riskPattern"):
            for control in component.find("countermeasures").iter("countermeasure"):
                ref = control.attrib['ref']
                name = control.attrib['name']

                if ref not in controls.keys():
                    controls[ref] = [name]
                else:
                    if name not in controls[ref]:
                        controls[ref].append(name)

    for control, l in controls.items():
        if len(l) > 1:
            for e in l:
                errors.append(f"Control {control} has different names: {e}")

    return errors


def checkDuplicatedRiskPatternRefs(roots):
    errors = []

    riskPatternFound = dict()
    for root in roots.values():
        library = root.getroot().attrib['ref']
        for component in root.find("riskPatterns").iter("riskPattern"):
            ref = component.attrib['ref']
            if ref not in riskPatternFound.keys():
                riskPatternFound[ref] = library
            else:
                errors.append(
                    f"Risk pattern {ref} in {library} appears to be duplicated in {riskPatternFound[ref]}")

    return errors

def checkIncorrectLibraryRefOnRule(roots):
    errors = []

    libraryRPMap = dict()

    for root in roots.values():
        libRef = root.getroot().attrib['ref']
        rpList = list()
        for component in root.find('riskPatterns').iter('riskPattern'):
            rpList.append(component.attrib['ref'])

        libraryRPMap[libRef] = rpList

    for root in roots.values():
        for rule in root.iter('rule'):
            for condition in rule.iter('condition'):
                if condition.attrib['name'] == "CONDITION_RISK_PATTERN_EXISTS":
                    value = condition.attrib['value'].split("_::_")
                    if value[1] not in libraryRPMap[value[0]]:
                        errors.append(
                            f"Rule [{rule.attrib['name']}] has a risk pattern that doesn't exists: {value}")

            for action in rule.iter('action'):
                if action.attrib['name'] in ["IMPORT_RISK_PATTERN", "EXTEND_RISK_PATTERN"]:
                    value = action.attrib['value'].split("_::_")
                    if value[1] not in libraryRPMap[value[0]]:
                        errors.append(
                            f"Rule [{rule.attrib['name']}] has a risk pattern that doesn't exists: {value}")
                    if action.attrib['project'] not in ["", value[0]] and action.attrib[
                        'project'] not in libraryRPMap.keys():
                        errors.append(
                            f"Rule [{rule.attrib['name']}] references a library that doesn't match with the action: {value[0]} != {action.attrib['project']}")
                if action.attrib['name'] in ["APPLY_CONTROL"]:
                    if action.attrib['project'] not in libraryRPMap.keys():
                        errors.append(
                            f"Rule [{rule.attrib['name']}] references a library that doesn't match any existing library: {action.attrib['project']} not in {libraryRPMap.keys()}")

    return errors


def checkInconsistentThreatNames(roots):
    errors = []

    threats = dict()
    for root in roots.values():
        for component in root.find("riskPatterns").iter("riskPattern"):
            for threat in component.iter("threat"):
                ref = threat.attrib['ref']
                name = threat.attrib['name']

                if ref not in threats.keys():
                    threats[ref] = [name]
                else:
                    if name not in threats[ref]:
                        threats[ref].append(name)

    for threat, l in threats.items():
        if len(l) > 1:
            for e in l:
                errors.append(f"Threat {threat} has different names: {e}")

    return errors


def checkInconsistentWeaknessNames(roots):
    errors = []

    weaknesses = dict()
    for root in roots.values():
        for component in root.find("riskPatterns").iter("riskPattern"):
            for weakness in component.find("weaknesses").iter("weakness"):
                ref = weakness.attrib['ref']
                name = weakness.attrib['name']

                if ref not in weaknesses.keys():
                    weaknesses[ref] = [name]
                else:
                    if name not in weaknesses[ref]:
                        weaknesses[ref].append(name)

    for weakness, l in weaknesses.items():
        if len(l) > 1:
            for e in l:
                errors.append(f"Weakness {weakness} has different names: {e}")

    return errors


def checkDisabledLibrariesAreDisabled(roots, disabled):
    errors = []

    for root in roots.values():
        r = root.getroot()
        if "enabled" in r.attrib:
            if r.attrib["enabled"] == "true":
                if r.attrib["ref"] in disabled:
                    errors.append(f"Library {r.attrib['ref']} is marked as enabled but it should be disabled")
            else:
                if r.attrib["ref"] not in disabled:
                    errors.append(
                        f"Library {r.attrib['ref']} is marked as disabled but is not in the list of disabled libraries")
        else:
            if r.attrib["ref"] in disabled:
                errors.append(f"Library {r.attrib['ref']} is marked as enabled but it should be disabled")

    return errors


def checkDuplicatedRules(roots, disabled):
    errors = []

    rules = dict()

    for root in roots.values():
        r = root.getroot()

        for rule in r.find("rules").iter("rule"):
            if rule.attrib["name"] not in rules:
                rules[rule.attrib["name"]] = 0
            rules[rule.attrib["name"]] +=1

    for k,v in rules.items():
        if v>1:
            errors.append(f"Rule '{k}' is duplicated")


    return errors


def checkPlaceholderComponentsAreDisabled(roots, disabled):
    errors = []

    rules = dict()

    for root in roots.values():
        for componentDefinition in root.find("componentDefinitions").iter("componentDefinition"):
            cd_name = componentDefinition.attrib['name']
            cd_ref = componentDefinition.attrib["ref"]
            if "placeholder" in cd_name.lower() and componentDefinition.attrib["visible"] != "false":
                errors.append(f"Component definition '{cd_ref}' is a placeholder component but is visible")


    return errors

def checkRuleReferencesAreNotBroken(roots, disabled):
    errors = []

    countermeasures_in_libs = dict()

    for root in roots.values():
        r = root.getroot()
        rootref = r.attrib["ref"]
        if rootref not in countermeasures_in_libs:
            countermeasures_in_libs[rootref] = set()

        for component in r.find("riskPatterns").iter("riskPattern"):
            for control in component.find("countermeasures").iter("countermeasure"):
                ref = control.attrib['ref']
                countermeasures_in_libs[rootref].add(ref)

    for root in roots.values():
        r = root.getroot()
        for rule in r.iter('rule'):
            for action in rule.iter('action'):

                action_project = action.attrib['project']

                if action.attrib['name'] in ["IMPORT_SPECIFIC_RISK"]:
                    value = action.attrib['value'].split("_::_")
                    if action_project != value[0]:
                        errors.append(f"Rule <{rule.attrib['name']}> has a wrong library reference (IMPORT_SPECIFIC_RISK): {action_project} != {value[0]}")

                if action.attrib['name'] in ["MARK_CONTROL_AS"]:
                    value = action.attrib['value'].split("_::_")
                    if value[0] not in countermeasures_in_libs[action_project]:
                        errors.append(f"Rule <{rule.attrib['name']}> has a wrong library reference (MARK_CONTROL_AS): {value[0]} not in countermeasures of {action_project}")


    return errors
