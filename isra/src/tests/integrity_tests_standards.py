import os

import pandas as pd
from lxml import etree


def findStandardReference(supportedStandardRef, standardReferences, standards):
    foundButNecessary = list()
    errorsFoundButNotNecessary = list()
    filtered_standard = standards.loc[standards['Supported Standard Id'] == supportedStandardRef]
    filtered_standard = filtered_standard.sort_values(by=['Standard Reference'])
    filtered_standard = filtered_standard.drop_duplicates()
    for item in standardReferences:
        if len(filtered_standard[filtered_standard['Standard Reference'] == item]) == 0:
            foundButNecessary.append(item)
    for index, row in filtered_standard.iterrows():
        if not row['Standard Reference'] in standardReferences:
            errorsFoundButNotNecessary.append(row['Standard Reference'])
    text = ""
    if len(foundButNecessary) != 0:
        text += f"The following standard references are not found but they are necessary: {str(foundButNecessary)}\n"
    if len(errorsFoundButNotNecessary) != 0:
        text += f"The following standard references are found but they are NOT necessary: {str(errorsFoundButNotNecessary)}\n"

    return text


def getStandardsFromCountermeasures(path_libraries):
    control_standard = list()
    for library in os.listdir(str(path_libraries)):
        if library.endswith(".xml"):
            root = etree.parse(str(path_libraries / library))
            for component in root.find("riskPatterns").iter("riskPattern"):
                for control in component.find("countermeasures").iter("countermeasure"):
                    for standard in control.find("standards").iter("standard"):
                        control_standard.append([standard.attrib['supportedStandardRef'], standard.attrib['ref']])

    dfm = pd.DataFrame(control_standard, columns=['Supported Standard Id', 'Standard Reference'])
    dfm.sort_values(by=['Supported Standard Id', 'Standard Reference'])
    dfm.drop_duplicates()
    return dfm