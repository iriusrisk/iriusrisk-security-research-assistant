import os
import re
import logging
import lxml.etree as etree
from pathlib import Path
from datetime import date
from collections import Counter
import xmlschema

# Creating a logger
logging.basicConfig(filename="logFile.log",
                    format='%(asctime)s  %(levelname)-10s %(message)s',
                    datefmt="%Y-%m-%d-%H-%M-%S",
                    filemode='w')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


# In this method, we compare the xml input with the input xsd validator to validate the input xml.
def xmlValidator(xml_path, xsd_path):
    errors = []

    xml_path = str(xml_path)
    xsd_path = str(xsd_path)
    try:
        # Check if the path exists
        if os.path.exists(xml_path):
            # parse the XSD Schema input file
            xmlschema2 = etree.XMLSchema(file=xsd_path)
            # parse the xml input file
            xml_doc = etree.parse(xml_path)
            # validate the xml with the XSD schema
            result = xmlschema2.validate(xml_doc)
            if not result:
                schema = xmlschema.XMLSchema(source=xsd_path)
                for error in schema.iter_errors(xml_doc):
                    print(
                        f'sourceline: {error.sourceline}; path: {error.path} | reason: {error.reason} | message: {error.message}')
                errors.append("Failed to validate the XSD schema: " + str(xml_path))
        else:
            errors.append("The following path was not found: " + str(xml_path))
            print("The following path was not found: " + str(xml_path))

    except etree.XMLSyntaxError:
        errors.append("Failed to validate the XSD schema due to exception: " + str(xml_path))

    return errors


def checkCopyrightInAllLibraries(path):
    errors = list()
    text1 = "<!--Copyright (c) 2012-%s IriusRisk SL. All rights reserved.The content of this library is the property of IriusRisk SL and may only be used in whole or in part with a valid license for IriusRisk.-->" % date.today().year

    found = False
    with open(str(path), 'r') as f:
        f.readline()
        second_line = f.readline()
        if second_line.find(text1) != -1:
            found = True
        if not found:
            p = Path(path)
            errors.append(f"The library {p.stem} has not got the Copyright in the xml file.")
        f.close()
    return errors


def checkIntegrityOfCategoryComponentsFromLibrary(root):
    errors = list()

    for categoryComponent in root.find("categoryComponents").iter("categoryComponent"):
        if categoryComponent.attrib['ref'] == "":
            errors.append(f"Empty Id for the Category Component with the name '{categoryComponent.attrib['name']}'.")
        if categoryComponent.attrib['name'] == "":
            errors.append(f"Empty Name for the Category Component with the ref '{categoryComponent.attrib['ref']}'.")

    return errors


def checkDuplicatedStandards(root):
    errors = []

    for component in root.find("riskPatterns").iter("riskPattern"):
        for control in component.find("countermeasures").iter("countermeasure"):
            items = list()
            for standard in control.find("standards").iter("standard"):
                items.append(standard.attrib['supportedStandardRef'] + "-" + standard.attrib['ref'])

            counter = Counter(items)
            for k, v in counter.items():
                if v > 1:
                    errors.append(
                        f"Component: {component.attrib['ref']} --> Control: {control.attrib['ref']} -> Standard: {k} appears {v} times")

    return errors


def checkDuplicatedReferences(root):
    errors = []

    for component in root.find("riskPatterns").iter("riskPattern"):
        for control in component.find("countermeasures").iter("countermeasure"):
            items = list()
            items2 = list()
            for reference in control.find("references").iter("reference"):
                items.append(reference.attrib['url'])
            for reference in control.find("references").iter("reference"):
                items2.append(reference.attrib['name'])

            counter = Counter(items)
            for k, v in counter.items():
                if v > 1:
                    errors.append(
                        f"Component: {component.attrib['ref']} --> Control: {control.attrib['ref']} -> References URL: {k} appears {v} times")
            counter = Counter(items2)
            for k, v in counter.items():
                if v > 1:
                    errors.append(
                        f"Component: {component.attrib['ref']} --> Control: {control.attrib['ref']} -> Reference Name: {k} appears {v} times")

    return errors


def checkDuplicatedImplementations(root):
    errors = []

    for component in root.find("riskPatterns").iter("riskPattern"):
        for control in component.find("countermeasures").iter("countermeasure"):
            items = list()
            for implementation in control.find("implementations").iter("implementation"):
                items.append(implementation.attrib['platform'])

            counter = Counter(items)
            for k, v in counter.items():
                if v > 1:
                    errors.append(
                        f"Component: {component.attrib['ref']} --> Control: {control.attrib['ref']} -> References: {k} appears {v} times")

    return errors


def checkDuplicatedControlsPerComponentFromLibrary(root):
    errors = []

    for component in root.find("riskPatterns").iter("riskPattern"):
        controls = list()
        for control in component.find("countermeasures").iter("countermeasure"):
            controls.append(control.attrib['ref'])

        counter = Counter(controls)
        for k, v in counter.items():
            if v > 1:
                errors.append(f"Component: {component.attrib['ref']} --> Countermeasure: {k} appears {v} times")

    return errors


def checkDuplicatedWeaknessesPerComponentFromLibrary(root):
    errors = []

    for component in root.find("riskPatterns").iter("riskPattern"):
        weaks = list()
        for weak in component.find("weaknesses").iter("weakness"):
            weaks.append(weak.attrib['ref'])

        counter = Counter(weaks)
        for k, v in counter.items():
            if v > 1:
                errors.append(f"Component: {component.attrib['ref']} --> Weakness: {k} appears {v} times")

    return errors


def checkDuplicatedThreatsPerUseCaseAndComponentFromLibrary(root):
    errors = []

    for component in root.find("riskPatterns").iter("riskPattern"):

        for usecase in component.find("usecases").iter("usecase"):
            threats = list()
            for threat in usecase.find("threats").iter("threat"):
                threats.append(threat.attrib['ref'])

            counter = Counter(threats)
            for k, v in counter.items():
                if v > 1:
                    errors.append(f"Component: {component.attrib['ref']} --> Weakness: {k} appears {v} times")

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


def checkIntegrityOfComponentDefinitionsFromLibrary(root):
    errors = list()
    componentRefs = list()
    for component in root.find("riskPatterns").iter("riskPattern"):
        componentRefs.append(component.attrib['ref'])
    for componentDefinition in root.find("componentDefinitions").iter("componentDefinition"):
        if componentDefinition.attrib['ref'] == "":
            errors.append(
                f'Empty Id for the Component Definition with the name {componentDefinition.attrib["name"]}.')
        if componentDefinition.attrib['name'] == "":
            errors.append(
                f'Empty Name for the Component Definition with the ref {componentDefinition.attrib["ref"]}.')
        if componentDefinition.attrib['categoryRef'] == "":
            errors.append(
                f'Empty CategoryRef for the Component Definition with the ref {componentDefinition.attrib["ref"]}.')
        for riskPattern in componentDefinition.find("riskPatterns").iter("riskPattern"):
            if not riskPattern.attrib['ref'] in componentRefs:
                errors.append(
                    f"Risk Pattern '{riskPattern.attrib['ref']}' for the Component Definition with the ref '{componentDefinition.attrib['ref']}' wasn't found.")
    return errors


def checkIfAllCountermeasuresAreWithRecommendedStatus(root):
    errors = list()
    for component in root.find("riskPatterns").iter("riskPattern"):
        for control in component.find("countermeasures").iter("countermeasure"):
            if control.attrib['state'] != "Recommended":
                errors.append(
                    f"Component: '{component.attrib['ref']}': Countermeasure with ref '{control.attrib['ref']}' hasn't got the state as Recommended.")

    return errors


def checkIfExistsUnassignedCountermeasures(root):
    errors = list()

    for component in root.find("riskPatterns").iter("riskPattern"):
        controlsRef1 = list()
        controlsRef2 = list()
        controlsAnyThreatTypeRef = list()
        controlsComponentTypeRef = [c.attrib['ref'] for c in component.find("countermeasures").iter("countermeasure")]
        for usecase in component.find("usecases").iter("usecase"):
            for threat in usecase.find("threats").iter("threat"):
                controlsThreatTypeRef = [c.attrib['ref'] for c in threat.find("countermeasures").iter("countermeasure")]
                controlsAnyThreatTypeRef += controlsThreatTypeRef
                for weakness in threat.find("weaknesses").iter("weakness"):
                    for control in weakness.find("countermeasures").iter("countermeasure"):
                        if control.attrib['ref'] not in controlsAnyThreatTypeRef:
                            controlsAnyThreatTypeRef.append(control.attrib['ref'])
                        # First we check that the control ref appears in the location component/controls/control
                        if (not control.attrib['ref'] in controlsComponentTypeRef) and (
                                not control.attrib['ref'] in controlsRef1):
                            controlsRef1.append(control.attrib['ref'])
                            errors.append(
                                f"Component: '{component.attrib['ref']}': Countermeasure with ref '{control.attrib['ref']}' not found in the control list for the component")
                        # Secondly we check that the control ref also appears in the location component/usecases/usecase/threats/threat/controls/control
                        if (not control.attrib['ref'] in controlsThreatTypeRef) and (
                                not control.attrib['ref'] in controlsRef2):
                            controlsRef2.append(control.attrib['ref'])
                            errors.append(
                                f"Component: '{component.attrib['ref']}': Countermeasure with ref '{control.attrib['ref']}' not found in the control list for the threat '{threat.attrib['ref']}'")

        # The controls at component-level should be the same that the controls at threat-level
        for controlRef in controlsComponentTypeRef:
            if controlRef not in controlsAnyThreatTypeRef:
                errors.append(
                    f"Component: '{component.attrib['ref']}': The control with ref '{controlRef}' is not assigned to any threat")
        for controlRef in controlsAnyThreatTypeRef:
            if controlRef not in controlsComponentTypeRef:
                errors.append(
                    f"Component: '{component.attrib['ref']}': The control with ref '{controlRef}' is not defined at component-level")

    return errors


def checkIfExistsUnassignedWeaknesses(root):
    errors = list()
    for component in root.find("riskPatterns").iter("riskPattern"):
        weaknessesThreatTypeRef = list()
        weaknessesComponentTypeRef = [w.attrib['ref'] for w in component.find("weaknesses").iter("weakness")]
        for usecase in component.find("usecases").iter("usecase"):
            for threat in usecase.find("threats").iter("threat"):
                for weakness in threat.find("weaknesses").iter("weakness"):
                    if weakness.attrib['ref'] not in weaknessesThreatTypeRef:
                        weaknessesThreatTypeRef.append(weakness.attrib['ref'])

        # The weaknesses at component-level should be the same that the weaknesses at threat-level
        for weaknessRef in weaknessesComponentTypeRef:
            if weaknessRef not in weaknessesThreatTypeRef:
                errors.append(
                    f"Component: '{component.attrib['ref']}': The weakness with ref '{weaknessRef}' is not assigned to any threat")
        for weaknessRef in weaknessesThreatTypeRef:
            if weaknessRef not in weaknessesComponentTypeRef:
                errors.append(
                    f"Component: '{component.attrib['ref']}': The weakness with ref '{weaknessRef}' is not defined at component-level")

    return errors


def checkIfStandardReferenceIsEmpty(root):
    errors = list()

    for component in root.find("riskPatterns").iter("riskPattern"):
        for control in component.find("countermeasures").iter("countermeasure"):
            for standard in control.find("standards").iter("standard"):
                if standard.attrib['supportedStandardRef'] == "":
                    errors.append(
                        f"Component: '{component.attrib['ref']}': the Supported standard Ref in the countermeasure '{control.attrib['ref']}' is empty.")
                if standard.attrib['ref'] == "":
                    errors.append(
                        f"Component: '{component.attrib['ref']}': the Reference in the countermeasure '{control.attrib['ref']}' is empty.")

    return errors


def checkIfThreatDescriptionIsEmpty(root):
    errors = list()

    for component in root.find('riskPatterns').iter('riskPattern'):
        for threat in component.iter('threat'):
            desc = threat.find("desc").text
            if desc == "" or desc is None:
                errors.append(
                    f"Component: '{component.attrib['ref']}': Threat {threat.attrib['ref']} doesn't have description: {desc}")

    return errors


def checkEmptyWeaknesses(root, exceptions):
    errors = []

    library = root.getroot().attrib['ref']

    for component in root.find("riskPatterns").iter("riskPattern"):
        for threat in component.iter("threat"):
            for weakness in threat.iter("weakness"):
                controls = list(weakness.iter('countermeasure'))
                if not controls:
                    if not component.attrib['ref'] in exceptions:
                        errors.append("Weakness without controls: " + library + " Component -> " + component.attrib[
                            'ref'] + " Weakness -> " +
                                      weakness.attrib['ref'])

    return errors


def checkOrphanedControls(root):
    errors = []

    library = root.getroot().attrib['ref']

    for threat in root.find("riskPatterns").iter("threat"):
        controlRefs = [control.attrib['ref'] for control in
                       list(threat.find("countermeasures").iter("countermeasure"))]
        wControlRefs = [wControl.attrib['ref'] for wControl in
                        list(threat.find("weaknesses").iter("countermeasure"))]
        for controlRef in controlRefs:
            if controlRef not in wControlRefs:
                errors.append("Orphaned controls: " + library + " -> " + controlRef)

    return errors


def checkCRLF(path):
    errors = []

    f = open(str(path))
    f.readline()
    # Check if the line separator is CRLF or CR
    if repr('\r\n') == repr(f.newlines) or repr('\r') == repr(f.newlines):
        p = Path(path)
        errors.append(f"Library with CRLF or CR: {p.name}")

    return errors


def checkWhitespacesInReferenceUrls(root):
    errors = []

    library = root.getroot().attrib['ref']

    for component in root.find("riskPatterns").iter("riskPattern"):
        for control in component.find("countermeasures").iter("countermeasure"):
            references = list(control.iter("reference"))
            for reference in references:
                if " " in reference.attrib['url']:
                    errors.append(
                        f"URL with whitespaces: {library} -> {control.attrib['ref']} -> {reference.attrib['url']}")

    return errors


def checkMissingSupportedStandards(root):
    errors = []

    library = root.getroot().attrib['ref']

    supportedStandardsSet = set()
    for supportedStandard in root.iter("supportedStandard"):
        supportedStandardsSet.add(supportedStandard.attrib['ref'])

    missingStandardsFound = set()

    for component in root.find("riskPatterns").iter("riskPattern"):
        ref = component.attrib['ref']
        for standard in component.iter("standard"):
            std = standard.attrib['supportedStandardRef']
            if std not in supportedStandardsSet and std not in missingStandardsFound:
                errors.append(f"Missing supported standard '{std}' in component '{ref}' in {library}")
                missingStandardsFound.add(std)

    return errors


def checkMissingCategoryRefs(root):
    errors = []

    library = root.getroot().attrib['ref']

    categoryRefSet = set()
    for categoryRef in root.iter("categoryComponent"):
        categoryRefSet.add(categoryRef.attrib['ref'])

    missingCategoryRefFound = set()

    for componentDefinition in root.iter("componentDefinition"):
        categoryRef = componentDefinition.attrib['categoryRef']
        if categoryRef not in categoryRefSet and categoryRef not in missingCategoryRefFound:
            errors.append(
                f"Missing category ref '{categoryRef}' in component definition '{componentDefinition.attrib['ref']}' in {library}")
            missingCategoryRefFound.add(categoryRef)

    return errors


def checkWhitespacesInRefs(root):
    errors = []

    library = root.getroot().attrib['ref']

    for component in root.find("riskPatterns").iter("riskPattern"):
        if " " in component.attrib['ref']:
            errors.append(f"{library} -> Component {component.attrib['ref']}")

        for weakness in component.find("weaknesses").iter("weakness"):
            if " " in weakness.attrib['ref']:
                errors.append(f"{library} -> {component.attrib['ref']} -> Weakness {weakness.attrib['ref']}")
        for control in component.find("countermeasures").iter("countermeasure"):
            if " " in control.attrib['ref']:
                errors.append(f"{library} -> {component.attrib['ref']} -> Control {control.attrib['ref']}")
        for usecase in component.find("usecases").iter("usecase"):
            if " " in usecase.attrib['ref']:
                errors.append(f"{library} -> {component.attrib['ref']} -> Use Case {usecase.attrib['ref']}")
            for threat in usecase.iter("threat"):
                if " " in threat.attrib['ref']:
                    errors.append(f"{library} -> {component.attrib['ref']} -> Threat {threat.attrib['ref']}")

    return errors


def checkCorrectMitigationSum(root):
    errors = []

    for component in root.find('riskPatterns').iter('riskPattern'):
        for threat in component.iter('threat'):
            nControls = len(list(threat.find("countermeasures").iter("countermeasure")))
            mitigationSum = 0
            for control in threat.find("countermeasures").iter("countermeasure"):
                controlMitigation = int(control.attrib["mitigation"])
                mitigationSum += controlMitigation

            if nControls > 0 and mitigationSum != 100:
                errors.append(
                    component.attrib["ref"] + ": Threat " + threat.attrib["ref"] + " mitigation sum is not 100: " + str(
                        mitigationSum))

    return errors


def checkIncorrectNameSuffix(root):
    errors = []

    regex = r'(\*|\"|\'|\)|\w|\d+)$'

    for component in root.find("riskPatterns").iter('riskPattern'):

        for control in component.find("countermeasures").iter("countermeasure"):
            name = control.attrib['name']
            if re.search(regex, name) is None:
                errors.append(
                    f"Component: '{component.attrib['ref']}': Incorrect name suffix: Control " + control.attrib[
                        'ref'] + ": ###" + name + "###")
        for weakness in component.find("weaknesses").iter("weakness"):
            name = weakness.attrib['name']
            if re.search(regex, name) is None:
                errors.append(
                    f"Component: '{component.attrib['ref']}': Incorrect name suffix: Weakness " + weakness.attrib[
                        'ref'] + ": ###" + name + "###")
        for usecase in component.iter('usecase'):
            name = usecase.attrib['name']
            if re.search(regex, name) is None:
                errors.append(
                    f"Component: '{component.attrib['ref']}': Incorrect name suffix: Usecase " + usecase.attrib[
                        'ref'] + ": ###" + name + "###")
            for threat in usecase.iter('threat'):
                name = threat.attrib['name']
                if re.search(regex, name) is None:
                    errors.append(
                        f"Component: '{component.attrib['ref']}': Incorrect name suffix: Threat " + threat.attrib[
                            'ref'] + ": ###" + name + "###")

    return errors


def checkIfControlDescriptionIsEmpty(root):
    errors = list()

    for component in root.find('riskPatterns').iter('riskPattern'):
        for c in component.find("countermeasures").iter('countermeasure'):
            desc = c.find("desc").text
            if desc == "" or desc is None:
                errors.append(
                    f"Component: '{component.attrib['ref']}': Countermeasure {c.attrib['ref']} doesn't have description: {desc}")

    return errors


def checkRiskRatingValuesStride(root):
    errors = list()

    for component in root.find('riskPatterns').iter('riskPattern'):
        for t in component.iter('threat'):
            confidentiality_threshold = 0
            integrity_threshold = 0
            availability_threshold = 0
            ee_threshold = 0


            stride = ""
            for customField in t.iter("customField"):
                if customField.attrib["ref"] == "SF-T-STRIDE-LM":
                    stride = customField.attrib["value"]
                    if customField.attrib["value"].startswith("S"):
                        confidentiality_threshold = 75
                        integrity_threshold = 75
                    elif customField.attrib["value"].startswith("T"):
                        integrity_threshold = 75
                    elif customField.attrib["value"].startswith("R"):
                        integrity_threshold = 75
                        ee_threshold = 50
                    elif customField.attrib["value"].startswith("I"):
                        confidentiality_threshold = 75
                    elif customField.attrib["value"].startswith("D"):
                        availability_threshold = 75
                    elif customField.attrib["value"].startswith("E"):
                        confidentiality_threshold = 75
                        integrity_threshold = 75
                    elif customField.attrib["value"].startswith("L"):
                        confidentiality_threshold = 75

            risk_rating_errors = ""

            if int(t.find("riskRating").attrib["confidentiality"]) < confidentiality_threshold:
                risk_rating_errors += f' C={t.find("riskRating").attrib["confidentiality"]} '
            if int(t.find("riskRating").attrib["integrity"]) < integrity_threshold:
                risk_rating_errors += f' I={t.find("riskRating").attrib["integrity"]} '
            if int(t.find("riskRating").attrib["availability"]) < availability_threshold:
                risk_rating_errors += f' A={t.find("riskRating").attrib["availability"]} '
            if int(t.find("riskRating").attrib["easeOfExploitation"]) < ee_threshold:
                risk_rating_errors += f' EE={t.find("riskRating").attrib["easeOfExploitation"]} '

            if risk_rating_errors != "":
                errors.append(
                    f"Component: '{component.attrib['ref']}': Threat {t.attrib['ref']} has wrong {stride} risk rating {risk_rating_errors}")

    return errors
