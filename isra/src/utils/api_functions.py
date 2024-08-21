import os

import requests
import time
import typer
from requests import HTTPError
from rich import print
from rich.progress import Progress, SpinnerColumn, TextColumn
from urllib3.exceptions import NewConnectionError

from isra.src.config.config import get_property, get_app_dir
from isra.src.config.constants import IRIUSRISK_API_HEADERS
from isra.src.utils.text_functions import clean_and_capitalize, convert_cost_value, get_company_name_prefix, \
    set_category_suffix
from isra.src.utils.xml_functions import export_rules_into_rules_library, export_content_into_category_library, \
    import_content_into_template, import_rules_into_template, create_local_library, get_library_name_from_file
from isra.src.utils.yaml_functions import build_tree_hierarchy


# Categories
def get_category(template):
    answer = make_api_call("get",
                           f"/api/v2/components/categories"
                           f"/summary?filter='referenceId'='{template['component']['categoryRef']}'")
    return get_response_object([answer])


def post_category(template):
    category_ref = template["component"]["categoryRef"]
    data = {
        "referenceId": category_ref,
        "name": category_ref
    }

    return make_api_call("post", "/api/v2/components/categories", request_body=data)


# Component definitions
def get_component_definition(template):
    answer = make_api_call("get", f"/api/v2/components"
                                  f"?filter='referenceId'='{template['component']['ref']}'")
    answer2 = make_api_call("get", f"/api/v2/components"
                                   f"?filter='name'='{template['component']['name']}'")
    return get_response_object([answer, answer2])


def post_component_definition(template, category):
    data = {
        "referenceId": template["component"]["ref"],
        "name": template["component"]["name"],
        "category": {
            "id": category["id"]
        },
        "visible": bool(template["component"]["visible"])
    }

    return make_api_call("post", "/api/v2/components", request_body=data)


def put_component_definition(template, component, category):
    data = {
        "name": template["component"]["name"],
        "description": template["component"]["desc"],
        "category": {
            "id": category["id"]
        },
        "visible": bool(template["component"]["visible"])
    }

    return make_api_call("put", f"/api/v2/components/{component['id']}", request_body=data)


# Libraries
def get_library(template):
    category_ref = get_company_name_prefix() + template["component"]["categoryRef"]
    category_ref = set_category_suffix(category_ref)
    answer = make_api_call("get", f"/api/v2/libraries?filter='referenceId'='{category_ref}'")
    return get_response_object([answer])


def get_rules_library(template):
    category_ref = get_company_name_prefix() + template["component"]["categoryRef"] + "-rules"
    answer = make_api_call("get", f"/api/v2/libraries?filter='referenceId'='{category_ref}'")
    return get_response_object([answer])


def get_export_library_xml(library):
    answer = make_api_call("get", f"/api/v2/libraries/{library['id']}/export", api_version="v2xml",
                           response_format="xml")
    return answer


def post_library(template):
    prefix = get_company_name_prefix()
    name = prefix + " " if prefix != "" else ""
    category_ref = set_category_suffix(template["component"]["categoryRef"])
    data = {
        "referenceId": prefix + category_ref,
        "name": name + clean_and_capitalize(
            template["component"]["categoryRef"]) + " - Components"
    }

    return make_api_call("post", "/api/v2/libraries", request_body=data)


def post_rules_library(template):
    prefix = get_company_name_prefix()
    name = prefix + " " if prefix != "" else ""
    data = {
        "referenceId": prefix + template["component"]["categoryRef"] + "-rules",
        "name": name + clean_and_capitalize(
            template["component"]["categoryRef"]) + " - Rules"
    }

    return make_api_call("post", "/api/v2/libraries", request_body=data)


def post_library_xml(template, library, xml_library_path):
    with open(xml_library_path, 'rb') as f:
        filename = os.path.basename(f.name)
        filedata = f.read()
        mimetype = 'application/xml'
        files = {"file": (filename, filedata, mimetype)}

    return make_api_call("post", f"/api/v2/libraries/{library['id']}/update-with-file",
                         api_version="v2multipart",
                         files=files)


# Risk patterns
def get_risk_pattern(template, library):
    answer = make_api_call("get",
                           f"/api/v2/libraries/{library['id']}"
                           f"/risk-patterns?filter='referenceId'='{template['riskPattern']['ref']}'")
    return get_response_object([answer])


def post_risk_pattern(template, library):
    data = {
        "referenceId": template["riskPattern"]["ref"],
        "name": template["riskPattern"]["name"],
        "description": template["riskPattern"]["desc"],
        "library": {
            "id": library["id"]
        }
    }

    return make_api_call("post", "/api/v2/libraries/risk-patterns", request_body=data)


def put_risk_pattern(template, risk_pattern):
    data = {
        "referenceId": template["riskPattern"]["ref"],
        "name": template["riskPattern"]["name"],
        "description": template["riskPattern"]["desc"],
    }

    return make_api_call("put", f"/api/v2/libraries/risk-patterns/{risk_pattern['id']}",
                         request_body=data)


def associate_risk_pattern_to_component(component, risk_pattern):
    data = {
        "riskPattern": {
            "id": risk_pattern["id"]
        }
    }
    return make_api_call("post",
                         f"/api/v2/components/{component['id']}/risk-patterns",
                         request_body=data, no_response=True)


def get_associated_risk_patterns(component, risk_pattern):
    answer = make_api_call("get",
                           f"/api/v2/components/{component['id']}"
                           f"/risk-patterns?filter='name'='{risk_pattern['name']}'")
    return get_response_object([answer])


# Use cases
def get_use_case(usecase_ref, risk_pattern):
    answer = make_api_call("get",
                           f"/api/v2/libraries"
                           f"/risk-patterns/{risk_pattern['id']}"
                           f"/use-cases?filter='referenceId'='{usecase_ref}'",
                           color="blue")
    return get_response_object([answer])


def post_use_case(template, usecase_ref, risk_pattern):
    data = {
        "referenceId": template["usecases"][usecase_ref]["ref"],
        "name": template["usecases"][usecase_ref]["name"],
        "description": template["usecases"][usecase_ref]["desc"],
        "riskPattern": {
            "id": risk_pattern["id"]
        }
    }

    return make_api_call("post", "/api/v2/libraries/use-cases", request_body=data, color="blue")


def put_use_case(template, usecase_ref, usecase):
    data = {
        "name": template["usecases"][usecase_ref]["name"],
        "description": template["usecases"][usecase_ref]["desc"]
    }

    return make_api_call("put", f"/api/v2/libraries/use-cases/{usecase['id']}",
                         request_body=data, color="blue")


def get_all_use_cases(risk_pattern):
    answer = make_api_call("get",
                           f"/api/v2/libraries/risk-patterns/{risk_pattern['id']}/use-cases?size=1000",
                           color="blue")
    return get_response_array([answer])


def delete_use_case(uc):
    make_api_call("delete",
                  f"/api/v2/libraries/use-cases/{uc['id']}",
                  color="blue", no_response=True)


# Threats
def get_threat(th_key, uc):
    answer = make_api_call("get",
                           f"/api/v2/libraries"
                           f"/threats?filter='useCase.id'='{uc['id']}':AND:'referenceId'='{th_key}'",
                           color="red")
    return get_response_object([answer])


def post_threat(template, th_key, uc, customfields):
    custom_fields = list()
    for k, v in template["threats"][th_key]["customFields"].items():
        if k in customfields:
            cfid = customfields[k]
            custom_fields.append({"value": v, "customField": {"id": cfid}})
    data = {
        "availability": int(template["threats"][th_key]["riskRating"]["A"]),
        "confidentiality": int(template["threats"][th_key]["riskRating"]["C"]),
        "easeOfExploitation": int(template["threats"][th_key]["riskRating"]["EE"]),
        "integrity": int(template["threats"][th_key]["riskRating"]["I"]),
        "name": template["threats"][th_key]["name"],
        "referenceId": template["threats"][th_key]["ref"],
        "useCase": {
            "id": uc["id"]
        },
        "description": template["threats"][th_key]["desc"],
        "customFields": custom_fields
    }

    return make_api_call("post", "/api/v2/libraries/threats", request_body=data, color="red")


def put_threat(template, th_key, th, customfields):
    custom_fields = list()
    for k, v in template["threats"][th_key]["customFields"].items():
        if k in customfields:
            cfid = customfields[k]
            custom_fields.append({"value": v, "customField": {"id": cfid}})
    data = {
        "availability": int(template["threats"][th_key]["riskRating"]["A"]),
        "confidentiality": int(template["threats"][th_key]["riskRating"]["C"]),
        "easeOfExploitation": int(template["threats"][th_key]["riskRating"]["EE"]),
        "integrity": int(template["threats"][th_key]["riskRating"]["I"]),
        "name": template["threats"][th_key]["name"],
        "referenceId": template["threats"][th_key]["ref"],
        "description": template["threats"][th_key]["desc"],
        "customFields": custom_fields
    }

    return make_api_call("put", f"/api/v2/libraries/threats/{th['id']}",
                         request_body=data, color="red")


def delete_threat(th):
    make_api_call("delete",
                  f"/api/v2/libraries/threats/{th['id']}",
                  color="red", no_response=True)


def get_all_threats(uc):
    answer = make_api_call("get",
                           f"/api/v2/libraries/threats?filter='useCase.id'='{uc['id']}'",
                           color="red")
    return get_response_array([answer])


# Weaknesses
def get_weakness(w_key, risk_pattern):
    answer = make_api_call("get",
                           f"/api/v2/libraries/weaknesses"
                           f"/?filter='referenceId'='{w_key}':AND:'riskPattern.id'='{risk_pattern['id']}'",
                           color="green")

    return get_response_object([answer])


def post_weakness(template, w_key, risk_pattern):
    data = {
        "name": template["weaknesses"][w_key]["name"],
        "referenceId": template["weaknesses"][w_key]["ref"],
        "impact": int(template["weaknesses"][w_key]["impact"]),
        "description": template["weaknesses"][w_key]["desc"],
        "riskPattern": {
            "id": risk_pattern["id"]
        }
    }

    return make_api_call("post",
                         f"/api/v2/libraries/weaknesses",
                         request_body=data, color="green")


def put_weakness(template, w_key, ww):
    data = {
        "name": template["weaknesses"][w_key]["name"],
        "referenceId": template["weaknesses"][w_key]["ref"],
        "description": template["weaknesses"][w_key]["desc"],
        "impact": int(template["weaknesses"][w_key]["impact"])
    }

    return make_api_call("put", f"/api/v2/libraries/weaknesses/{ww['id']}",
                         request_body=data, color="green")


def delete_weakness(w):
    make_api_call("delete",
                  f"/api/v2/libraries/weaknesses/{w['id']}",
                  color="green", no_response=True)


def get_all_weaknesses(risk_pattern):
    answer = make_api_call("get",
                           f"/api/v2/libraries/weaknesses?filter='riskPattern.id'='{risk_pattern['id']}'",
                           color="green")
    return get_response_array([answer])


def associate_weakness_to_threat(w_key, library, risk_pattern, uc, th):
    data = {
        "ref": w_key
    }
    return make_api_call("put",
                         f"/api/v1/libraries/{library['referenceId']}"
                         f"/riskpatterns/{risk_pattern['referenceId']}"
                         f"/usecases/{uc['referenceId']}"
                         f"/threats/{th['referenceId']}"
                         f"/weaknesses",
                         request_body=data, api_version="v1", color="green", no_response=True)


# Countermeasures
def get_countermeasure(c_key, risk_pattern):
    answer = make_api_call("get",
                           f"/api/v2/libraries/countermeasures"
                           f"/?filter='referenceId'='{c_key}':AND:'riskPattern.id'='{risk_pattern['id']}'",
                           color="yellow")
    return get_response_object([answer])


def get_countermeasure_by_id(c_key):
    answer = make_api_call("get",
                           f"/api/v2/libraries/countermeasures/{c_key}",
                           color="yellow")
    return answer


def get_customfields():
    customfields = dict()
    answer = make_api_call("get", f"/api/v2/custom-fields")
    items = get_response_array([answer])
    for item in items:
        customfields[item["referenceId"]] = item["id"]

    return customfields


def post_countermeasure(template, c_key, risk_pattern, customfields):
    custom_fields = list()
    for k, v in template["controls"][c_key]["customFields"].items():
        if k in customfields:
            cfid = customfields[k]
            custom_fields.append({"value": v, "customField": {"id": cfid}})

    data = {
        "referenceId": template["controls"][c_key]["ref"],
        "name": template["controls"][c_key]["name"],
        "description": template["controls"][c_key]["desc"],
        "riskPattern": {
            "id": risk_pattern["id"]
        },
        "cost": convert_cost_value(template["controls"][c_key]["cost"]),
        "state": "recommended",
        "customFields": custom_fields
    }

    return make_api_call("post", "/api/v2/libraries/countermeasures", request_body=data, color="yellow")


def put_countermeasure(template, c_key, cc, customfields):
    custom_fields = list()
    for k, v in template["controls"][c_key]["customFields"].items():
        if k in customfields:
            cfid = customfields[k]
            custom_fields.append({"value": v, "customField": {"id": cfid}})

    data = {
        "referenceId": template["controls"][c_key]["ref"],
        "name": template["controls"][c_key]["name"],
        "description": template["controls"][c_key]["desc"],
        "cost": convert_cost_value(template["controls"][c_key]["cost"]),
        "state": "recommended",
        "customFields": custom_fields
    }

    return make_api_call("put", f"/api/v2/libraries/countermeasures/{cc['id']}", request_body=data, color="yellow")


def put_countermeasure_references(template, c_key, cc):
    # TODO: Endpoint not available yet
    pass


def post_countermeasure_standards(template, c_key, cc):
    data = [{
        "reference": st["standard-section"],
        "standardRef": st["standard-ref"]
    } for st in template["controls"][c_key]["standards"]]
    # TODO: V1 Endpoint. Standard ref must be present in the instance if we don't want this method to fail
    # Remove "data = []" when the method is enabled
    data = []

    if len(data) != 0:
        return make_api_call("post", f"/api/v1/security-content"
                                     f"/countermeasures/{cc['referenceId']}"
                                     f"/standards",
                             request_body=data, api_version="v1", no_response=True, color="yellow")


def delete_countermeasure(c):
    make_api_call("delete",
                  f"/api/v2/libraries/countermeasures/{c['id']}",
                  color="yellow", no_response=True)


def get_all_countermeasures(risk_pattern):
    answer = make_api_call("get",
                           f"/api/v2/libraries/countermeasures?filter='riskPattern.id'='{risk_pattern['id']}'",
                           color="yellow")
    return get_response_array([answer])


def associate_countermeasure_to_weakness(c_key, library, risk_pattern, uc, th, ww):
    data = {
        "ref": c_key
    }
    return make_api_call("put",
                         f"/api/v1/libraries/{library['referenceId']}"
                         f"/riskpatterns/{risk_pattern['referenceId']}"
                         f"/usecases/{uc['referenceId']}"
                         f"/threats/{th['referenceId']}"
                         f"/weaknesses/{ww['referenceId']}"
                         f"/countermeasures",
                         request_body=data, api_version="v1", color="yellow", no_response=True)


def associate_countermeasure_to_threat(template, c_key, library, risk_pattern, uc, th):
    mitigation = "99"
    for item in template["relations"]:
        if item["usecase"] == uc['referenceId'] and item["threat"] == th['referenceId'] and item["control"] == c_key:
            mitigation = item["mitigation"]

    # TODO: Check why the mitigation values are not updated correctly
    # Also, check why the countermeasures are moved under another threat in a put, and not removed
    data = {
        "ref": c_key,
        "mitigation": int(mitigation)
    }
    return make_api_call("put",
                         f"/api/v1/libraries/{library['referenceId']}"
                         f"/riskpatterns/{risk_pattern['referenceId']}"
                         f"/usecases/{uc['referenceId']}"
                         f"/threats/{th['referenceId']}"
                         f"/countermeasures",
                         request_body=data, api_version="v1", color="yellow", no_response=True)


# Main

def get_response_object(answers):
    for answer in answers:
        if len(answer["_embedded"]["items"]) != 0:
            return answer["_embedded"]["items"][0]
    return None


def get_response_array(answers):
    for answer in answers:
        if len(answer["_embedded"]["items"]) != 0:
            return answer["_embedded"]["items"]
    return []


def make_api_call(http_method, api_endpoint, request_body=None, api_version="v2", color=None, no_response=False,
                  files=None, response_format="json"):
    message = (f"[{color}]" if color else "") + f"Calling {http_method} {api_endpoint}"
    print(message)

    headers = IRIUSRISK_API_HEADERS[api_version]
    headers["api-token"] = get_property("iriusrisk_api_token")

    with Progress(
            SpinnerColumn(),
            TextColumn(f"Querying IriusRisk API, wait a moment..."),
            transient=True,
    ) as progress:
        progress.add_task(description="Processing...", total=None)
        url = get_property("iriusrisk_url")
        try:
            if http_method == 'get':
                response = requests.get(url + api_endpoint, headers=headers)
            elif http_method == 'post' and files is None:
                response = requests.post(url + api_endpoint, headers=headers, json=request_body)
            elif http_method == 'post' and files is not None:
                headers["X-Irius-Async"] = "true"
                response = requests.post(url + api_endpoint, headers=headers, files=files)
            elif http_method == 'put':
                response = requests.put(url + api_endpoint, headers=headers, json=request_body)
            elif http_method == 'delete':
                response = requests.delete(url + api_endpoint, headers=headers)
            else:
                raise Exception("HTTP method not allowed")

            response.raise_for_status()
        except HTTPError as e:
            print(e.response.text)
            raise typer.Exit(-1)
        except requests.exceptions.ConnectionError as e:
            print(e)
            raise typer.Exit(-1)
        except NewConnectionError as e:
            print(e)
            raise typer.Exit(-1)
        except Exception as e:
            print(e)
            raise typer.Exit(-1)

        if no_response:
            return {"message": response.status_code}
        else:
            if response_format == "xml":
                return response.content
            elif response_format == "json":
                return response.json()
            else:
                return response.text


def upload_component_to_iriusrisk(template):
    # Create component

    # Check if the category of the component exists
    category = get_category(template)
    if category is None:
        print("No category found in instance")
        # If no category has been found we need to create it in the instance
        category = post_category(template)
    else:
        # Otherwise we will have to update it if needed. Let's assume that we will always update it
        pass

    # Check if component already exists
    component = get_component_definition(template)
    if component is None:
        # If no component has been found we need to create it in the instance
        component = post_component_definition(template, category)
    else:
        # Otherwise we will have to update it if needed. Let's assume that we will always update it
        put_component_definition(template, component, category)
        # TODO: All risk patterns from this component definition should be updated

    # If we reach this point it's because we ensured that the component exists in the instance and it's empty (no rps)
    # Now we need to update the content. We need to find the library where the risk pattern for the component exists

    library = get_library(template)
    if library is None:
        # If no risk pattern has been found we need to create it in the instance
        library = post_library(template)
    else:
        pass

    # Create content tree
    tree = build_tree_hierarchy(template["relations"])
    customfields = get_customfields()

    for rp_key, rp_value in tree.items():
        risk_pattern = get_risk_pattern(template, library)
        if risk_pattern is None:
            # If no risk pattern has been found we need to create it in the instance
            risk_pattern = post_risk_pattern(template, library)
        else:
            # Otherwise we will have to update it if needed. Let's assume that we will always update it
            put_risk_pattern(template, risk_pattern)

        associated_rp = get_associated_risk_patterns(component, risk_pattern)
        if associated_rp is None:
            associate_risk_pattern_to_component(component, risk_pattern)
        else:
            pass

        for uc_key, uc_value in rp_value.items():
            uc = get_use_case(uc_key, risk_pattern)
            if uc is None:
                uc = post_use_case(template, uc_key, risk_pattern)
            else:
                put_use_case(template, uc_key, uc)

            for th_key, th_value in uc_value.items():
                th = get_threat(th_key, uc)
                if th is None:
                    th = post_threat(template, th_key, uc, customfields)
                else:
                    put_threat(template, th_key, th, customfields)
                # TODO: put_threat_references(template, th_key, library, risk_pattern, uc, th)

                for w_key, w_value in th_value.items():
                    ww = ""
                    if w_key != "":
                        ww = get_weakness(w_key, risk_pattern)
                        if ww is None:
                            ww = post_weakness(template, w_key, risk_pattern)
                        else:
                            put_weakness(template, w_key, ww)
                        associate_weakness_to_threat(w_key, library, risk_pattern, uc, th)
                        # TODO: put_weakness_references(template, w_key, library, risk_pattern, uc, th, ww)

                    for c_key, c_value in w_value.items():
                        cc = get_countermeasure(c_key, risk_pattern)
                        if cc is None:
                            cc = post_countermeasure(template, c_key, risk_pattern, customfields)
                        else:
                            put_countermeasure(template, c_key, cc, customfields)
                        post_countermeasure_standards(template, c_key, cc)
                        put_countermeasure_references(template, c_key, cc)

                        if w_key != "":
                            associate_countermeasure_to_weakness(c_key, library, risk_pattern, uc, th, ww)
                        else:
                            associate_countermeasure_to_threat(template, c_key, library, risk_pattern, uc, th)

    # Cleaning elements that are not present anymore
    # e.g. use cases that are not present in the template file
    #
    # TODO: Remove risk patterns not related anymore with the component from the component definition, if any
    risk_pattern = get_risk_pattern(template, library)
    usecases = get_all_use_cases(risk_pattern)
    for uc in usecases:
        if uc["referenceId"] not in template["usecases"]:
            delete_use_case(uc)

    usecases = get_all_use_cases(risk_pattern)
    for uc in usecases:
        threats = get_all_threats(uc)
        for th in threats:
            if th["referenceId"] not in template["threats"]:
                delete_threat(th)

    weaknesses = get_all_weaknesses(risk_pattern)
    for w in weaknesses:
        if w["referenceId"] not in template["weaknesses"]:
            delete_weakness(w)

    countermeasures = get_all_countermeasures(risk_pattern)
    for c in countermeasures:
        if c["referenceId"] not in template["controls"]:
            delete_countermeasure(c)

    # Rules: we need to import the rules through XML. This means that we need to push the rules to a different
    # library We also have to remove any other rule related with the component that might get deprecated,
    # but that could be done manually

    # Now we need to upload the rules into the corresponding rules library
    # We have no choice but donwload the library from the instance and try to update it with these rules

    rules_library = get_rules_library(template)
    if rules_library is None:
        rules_library = post_rules_library(template)

    xml = get_export_library_xml(rules_library)
    export_rules_into_rules_library(template, xml)
    output_folder = get_property("component_output_path") or get_app_dir()
    xml_rules_library_path = os.path.join(output_folder, f"{template['component']['categoryRef']}-rules.xml")
    post_library_xml(template, rules_library, xml_rules_library_path)


def upload_xml(template):
    output_folder = get_property("component_output_path") or get_app_dir()

    # Upload category library with updated component
    component_library = get_library(template)
    if component_library is None:
        component_library = post_library(template)
    xml = get_export_library_xml(component_library)
    export_content_into_category_library(template, xml_text=xml)

    category_ref = set_category_suffix(template["component"]["categoryRef"])
    xml_category_library_path = os.path.join(output_folder, f"{category_ref}.xml")
    post_library_xml(template, component_library, xml_category_library_path)
    # Upload rules in a different library
    rules_library = get_rules_library(template)
    if rules_library is None:
        rules_library = post_rules_library(template)
    xml = get_export_library_xml(rules_library)
    export_rules_into_rules_library(template, xml_text=xml)
    xml_rules_library_path = os.path.join(output_folder, f"{template['component']['categoryRef']}-rules.xml")
    post_library_xml(template, rules_library, xml_rules_library_path)


def add_to_batch(template):
    output_folder = get_property("component_output_path") or get_app_dir()

    category_ref = set_category_suffix(template["component"]["categoryRef"])
    library_path = os.path.join(output_folder, f'{category_ref}.xml')
    if not os.path.exists(library_path):
        component_library = get_library(template)
        if component_library is None:
            component_library = post_library(template)
        xml = get_export_library_xml(component_library)
        create_local_library(xml, library_path)

    export_content_into_category_library(template, source_path=library_path)

    rules_library_path = os.path.join(output_folder, f'{template["component"]["categoryRef"]}-rules.xml')
    if not os.path.exists(rules_library_path):
        rules_library = get_rules_library(template)
        if rules_library is None:
            rules_library = post_rules_library(template)
        xml = get_export_library_xml(rules_library)
        create_local_library(xml, rules_library_path)

    export_rules_into_rules_library(template, source_path=rules_library_path)


def release_component_batch():
    output_folder = get_property("component_output_path") or get_app_dir()

    for root, dirs, files in os.walk(output_folder):
        for file in files:
            if file.endswith(".xml") and "-components" in file:
                # Assuming that there will be a components library and a rules library
                library_name = get_library_name_from_file(file)
                print(library_name)
                tt = {
                    "component": {
                        "categoryRef": library_name
                    }
                }
                component_library = get_library(tt)
                category_ref = set_category_suffix(library_name)
                xml_library_path = os.path.join(output_folder, category_ref + ".xml")
                post_library_xml(tt, component_library, xml_library_path)

                rules_library = get_rules_library(tt)
                xml_rules_library_path = os.path.join(output_folder, library_name + "-rules.xml")
                post_library_xml(tt, rules_library, xml_rules_library_path)

                time.sleep(20)


# TODO: This function is incomplete due to missing parameters. For example, some references are not updated
# Use pull_remote_component_xml instead
#
# def pull_remote_component(template):
#     library = get_library(template)
#     if library is None:
#         # If no risk pattern has been found we need to create it in the instance
#         print("No library found")
#         raise typer.Exit(-1)
#
#     risk_pattern = get_risk_pattern(template, library)
#     if risk_pattern is None:
#         print("No risk pattern found")
#         raise typer.Exit(-1)
#
#     usecases = get_all_use_cases(risk_pattern)
#     for uc in usecases:
#         threats = get_all_threats(uc)
#         for th in threats:
#             if th["referenceId"] in template["threats"]:
#                 template["threats"][th["referenceId"]]["name"] = th["name"]
#                 template["threats"][th["referenceId"]]["desc"] = th["description"]
#                 template["threats"][th["referenceId"]]["riskRating"]["C"] = str(th["confidentiality"])
#                 template["threats"][th["referenceId"]]["riskRating"]["I"] = str(th["integrity"])
#                 template["threats"][th["referenceId"]]["riskRating"]["A"] = str(th["availability"])
#                 template["threats"][th["referenceId"]]["riskRating"]["EE"] = str(th["easeOfExploitation"])
#                 # Hardcode to remove automatic CWE references included in IR
#                 references_to_add = list()
#                 for reference in th["references"]:
#                     if not reference["url"].startswith("http://cwe.mitre.org"):
#                         references_to_add.append(reference)
#                 template["threats"][th["referenceId"]]["references"] \
#                     = remove_duplicates_from_dict_list(references_to_add)
#                 for cf in th["customFields"]:
#                     if cf["customField"]["name"] == "STRIDE-LM":
#                         template["threats"][th["referenceId"]]["customFields"][CUSTOM_FIELD_STRIDE] = cf["value"]
#                     elif cf["customField"]["name"] == "MITRE reference":
#                         customfields = split_mitre_custom_field_threats(cf["value"])
#
#                         template["threats"][th["referenceId"]]["customFields"][
#                             CUSTOM_FIELD_ATTACK_ENTERPRISE_TECHNIQUE] = customfields[
#                             CUSTOM_FIELD_ATTACK_ENTERPRISE_TECHNIQUE]
#                         template["threats"][th["referenceId"]]["customFields"][CUSTOM_FIELD_ATTACK_ICS_TECHNIQUE] = \
#                             customfields[CUSTOM_FIELD_ATTACK_ICS_TECHNIQUE]
#                         template["threats"][th["referenceId"]]["customFields"][CUSTOM_FIELD_ATTACK_MOBILE_TECHNIQUE] = \
#                             customfields[CUSTOM_FIELD_ATTACK_MOBILE_TECHNIQUE]
#                         template["threats"][th["referenceId"]]["customFields"][CUSTOM_FIELD_ATLAS_TECHNIQUE] = \
#                             customfields[CUSTOM_FIELD_ATLAS_TECHNIQUE]
#
#     countermeasures = get_all_countermeasures(risk_pattern)
#     for ccc in countermeasures:
#         c = get_countermeasure_by_id(ccc["id"])
#
#         if c["referenceId"] in template["controls"]:
#             template["controls"][c["referenceId"]]["name"] = c["name"]
#             template["controls"][c["referenceId"]]["desc"] = c["description"]
#             template["controls"][c["referenceId"]]["cost"] = convert_cost_value(str(c["cost"]), to_number=True)
#             print("[red] Countermeasure references are not pulled!")
#             # TODO: References are not present in the response
#             # references_to_add = set()
#             # for reference in c["references"]:
#             #     if not reference["url"].startswith("http://cwe.mitre.org"):
#             #         references_to_add.add(reference)
#             # template["controls"][c["referenceId"]]["references"] = references_to_add
#             for cf in c["customFields"]:
#                 # TODO: Setting custom fields based on names is a bit hardcoded but it works
#                 if cf["customField"]["name"] == "Standard baseline":
#                     template["controls"][c["referenceId"]]["customFields"][CUSTOM_FIELD_BASELINE_STANDARD_REF] = \
#                         cf["value"]
#                 elif cf["customField"]["name"] == "Standard baseline section":
#                     template["controls"][c["referenceId"]]["customFields"][CUSTOM_FIELD_BASELINE_STANDARD_SECTION] = \
#                         cf["value"]
#                 elif cf["customField"]["name"] == "Scope":
#                     template["controls"][c["referenceId"]]["customFields"][CUSTOM_FIELD_SCOPE] = cf["value"]
#                 elif cf["customField"]["name"] == "MITRE reference":
#                     customfields = split_mitre_custom_field_controls(cf["value"])
#
#                     template["controls"][c["referenceId"]]["customFields"][
#                         CUSTOM_FIELD_ATTACK_ENTERPRISE_MITIGATION] = customfields[
#                         CUSTOM_FIELD_ATTACK_ENTERPRISE_MITIGATION]
#                     template["controls"][c["referenceId"]]["customFields"][CUSTOM_FIELD_ATTACK_ICS_MITIGATION] = \
#                         customfields[CUSTOM_FIELD_ATTACK_ICS_MITIGATION]
#                     template["controls"][c["referenceId"]]["customFields"][CUSTOM_FIELD_ATTACK_MOBILE_MITIGATION] = \
#                         customfields[CUSTOM_FIELD_ATTACK_MOBILE_MITIGATION]
#                     template["controls"][c["referenceId"]]["customFields"][CUSTOM_FIELD_ATLAS_MITIGATION] = \
#                         customfields[CUSTOM_FIELD_ATLAS_MITIGATION]
#
#     return template


def pull_remote_component_xml(template):
    library = get_library(template)
    if library is None:
        # If no risk pattern has been found we need to create it in the instance
        print("No library found")
        raise typer.Exit(-1)

    rules_library = get_rules_library(template)
    if rules_library is None:
        print("No rules library found")
        raise typer.Exit(-1)

    xml = get_export_library_xml(library)
    template = import_content_into_template(template, xml_text=xml)

    xml2 = get_export_library_xml(rules_library)
    template = import_rules_into_template(template, xml_text=xml2)

    return template
