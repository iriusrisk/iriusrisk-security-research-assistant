# Just believe that these are inmutable constants :)

APP_NAME = "ISRA"

CWE_SOURCE_FILE = "cwec_v4.13.xml"
PROMPTS_DIR = "prompts"
ILE_JAR_FILE = "editor-1.0.7-SNAPSHOT.jar"
TEMPLATE_FILE = "temp2.irius"
THREAT_MODEL_FILE = "threat_model.json"
TEST_ANSWERS_FILE = "test_answers.yaml"
OPENCRE_PLUS = "cre_mappings_plus.yaml"
YSC_SCHEMA = "ysc_schema.json"
SYSTEM_FIELD_VALUES = "output_system_fields_values.yaml"

CUSTOM_FIELD_STRIDE = "stride_lm"
CUSTOM_FIELD_SCOPE = "scope"
CUSTOM_FIELD_STANDARD_BASELINE_REF = "baseline_standard_ref"
CUSTOM_FIELD_STANDARD_BASELINE_SECTION = "baseline_standard_section"
CUSTOM_FIELD_ATTACK_ENTERPRISE_TECHNIQUE = "attack_enterprise_technique"
CUSTOM_FIELD_ATTACK_ICS_TECHNIQUE = "attack_ics_technique"
CUSTOM_FIELD_ATTACK_MOBILE_TECHNIQUE = "attack_mobile_technique"
CUSTOM_FIELD_ATTACK_ENTERPRISE_MITIGATION = "attack_enterprise_mitigation"
CUSTOM_FIELD_ATTACK_ICS_MITIGATION = "attack_ics_mitigation"
CUSTOM_FIELD_ATTACK_MOBILE_MITIGATION = "attack_mobile_mitigation"
CUSTOM_FIELD_ATLAS_TECHNIQUE = "atlas_technique"
CUSTOM_FIELD_ATLAS_MITIGATION = "atlas_mitigation"

PREFIX_COMPONENT_DEFINITION = "CD-V2-"
PREFIX_RISK_PATTERN = "RP-V2-"
PREFIX_USE_CASE = "UC-"
PREFIX_THREAT = "T-"
PREFIX_COUNTERMEASURE = "C-"

IR_SF_T_STRIDE = "SF-STRIDE-LM-TYPE"
IR_SF_T_MITRE = "SF-MITRE-T-TYPE"
IR_SF_C_MITRE = "SF-MITRE-C-TYPE"
IR_SF_C_SCOPE = "SF-SCOPE-TYPE"
IR_SF_C_STANDARD_BASELINES = "SF-STANDARD-BASELINE-TYPE"
IR_SF_C_STANDARD_SECTION = "SF-STANDARD-SECTION-TYPE"

NON_ASCII_CODES = {
    8220: "\"",
    8221: "\"",
    8216: "'",
    8217: "'",
    8211: "-",
    8212: "-",
    160: " ",
    228: "a",
    8239: " "
}

OUTPUT_NAME = {
    "ISO 27001": {'ref': 'iso-27002-2022', 'name': 'ISO/IEC 27002:2022'},
    "NIST 800-53 v5": {'ref': 'NIST 800-53', 'name': 'NIST 800-53'},
    "ASVS": {'ref': 'owasp-asvs4-level-3', 'name': 'OWASP-ASVS4-Level-3'},
    "NIST 800-63": {'ref': 'nist-800-63', 'name': 'NIST 800-63'},
    "FedRAMP": {'ref': 'fedramp-high-baseline', 'name': 'FedRAMP High Baseline'},
    "OWASP Top 10 2021": {'ref': 'owasp-top-10-2021', 'name': 'OWASP Top 10 2021'},
    "PCI DSS v3.2.1": {'ref': 'PCI-DSS-v3.2.1', 'name': 'PCI-DSS-v3.2.1'},
    "Cloud Controls Matrix": {'ref': 'cloud-control-matrix', 'name': 'Cloud Controls Matrix'},
    "CWE": {'ref': 'cwe-standard', 'name': 'CWE'},
    "NIST SSDF": {'ref': 'nist-ssdf', 'name': 'NIST SSDF'},
    "OWASP Cheat Sheets": {'ref': 'owasp-cheat-sheets', 'name': 'OWASP Cheat Sheets'},
    "OWASP Proactive Controls": {'ref': 'owasp-proactive-controls', 'name': 'OWASP Proactive Controls'},
    "OWASP Web Security Testing Guide (WSTG)": {'ref': 'owasp-wstg', 'name': 'OWASP Web Security Testing Guide (WSTG)'},
    "SAMM": {'ref': 'SAMM', 'name': 'SAMM'},
    "CRE": {'ref': 'OpenCRE', 'name': 'OpenCRE'},
    "NIST CSF v1.1": {'ref': 'nist-csf', 'name': 'NIST Cybersecurity Framework'},
    "D3FEND": {'ref': 'D3FEND', 'name': 'Mitre D3FEND Framework'},
    "CCPA": {'ref': 'ccpa', 'name': 'California Consumer Privacy Act'},
    # {'ref': 'azure-security-benchmark', 'name': 'Azure Security Benchmark'},
    # {'ref': 'CIS AWS Standard', 'name': 'CIS Amazon Web Services Foundations Benchmark Level 1'},
    # {'ref': 'cis-amazon-web-services-three-tier-web-architecture-benchmark',
    #  'name': 'CIS Amazon Web Services Three-tier Web Architecture Benchmark Level 1'},
    # {'ref': 'cis-amazon-web-services-three-tier-web-architecture-benchmark-level-2',
    #  'name': 'CIS Amazon Web Services Three-tier Web Architecture Benchmark Level 2'},
    # {'ref': 'CIS-AWS-Standard-Level-2', 'name': 'CIS Amazon Web Services Foundations Benchmark Level 2'},
    # {'ref': 'cis-azure-standard', 'name': 'CIS Microsoft Azure Foundations Benchmark Level 1'},
    # {'ref': 'cis-azure-standard-level-2', 'name': 'CIS Microsoft Azure Foundations Benchmark Level 2'},
    # {'ref': 'cis-gcp-standard', 'name': 'CIS Google Cloud Platform Foundation Benchmark Level 1'},
    # {'ref': 'cis-gcp-standard-level-2', 'name': 'CIS Google Cloud Platform Foundation Benchmark Level 2'},
    # {'ref': 'cis-kubernetes-level-1', 'name': 'CIS Kubernetes - Level 1'},
    # {'ref': 'cis-kubernetes-level-2', 'name': 'CIS Kubernetes - Level 2'},
    # {'ref': 'cis-oracle-cloud-level-1', 'name': 'CIS Oracle Cloud Infrastructure Foundations Level 1'},
    # {'ref': 'cis-oracle-cloud-level-2', 'name': 'CIS Oracle Cloud Infrastructure Foundations Level 2'},
    # {'ref': 'csa-api-security-guidelines', 'name': 'CSA API Security Guidelines'},
    # {'ref': 'csa-container-architectures',
    #  'name': 'CSA Best Practices for Implementing a Secure Application Container Architecture'},
    # {'ref': 'cwe-top-25-dangerous-weaknesses', 'name': 'CWE Top 25 Most Dangerous Software Weaknesses'},
    # {'ref': 'EU-GDPR', 'name': 'EU-GDPR'},
    # {'ref': 'fedramp-low-baseline', 'name': 'FedRAMP Low Baseline'},
    # {'ref': 'fedramp-moderate-baseline', 'name': 'FedRAMP Moderate Baseline'},
    # {'ref': 'hipaa-addressable', 'name': 'HIPAA Addressable'},
    # {'ref': 'hipaa-required', 'name': 'HIPAA Required'},
    # {'ref': 'iotsf-class-0', 'name': 'IoTSF Class 0'},
    # {'ref': 'iotsf-class-1', 'name': 'IoTSF Class 1'},
    # {'ref': 'iotsf-class-2', 'name': 'IoTSF Class 2'},
    # {'ref': 'ISO/IEC 27002:2013', 'name': 'ISO/IEC 27002:2013'},
    # {'ref': 'iso-sae-21434', 'name': 'ISO/SAE 21434'},
    # {'ref': 'Level 1 - Docker', 'name': 'CIS Docker - Level 1'},
    # {'ref': 'Level 1 - Linux Host OS', 'name': 'CIS Docker Linux Host OS Level 1'},
    # {'ref': 'Level 2 - Docker', 'name': 'CIS Docker - Level 2'},
    # {'ref': 'nist-800-190', 'name': 'NIST 800-190'},
    # {'ref': 'NIST-Secure-Microservice-Strategies',
    #  'name': 'NIST Security Strategies for Microservices-based Application Systems'},
    # {'ref': 'owasp-api-security-top-10', 'name': 'OWASP API Security Top 10'},
    # {'ref': 'owasp-asvs4-level-1', 'name': 'OWASP-ASVS4-Level-1'},
    # {'ref': 'owasp-asvs4-level-2', 'name': 'OWASP-ASVS4-Level-2'},
    # {'ref': 'OWASP-CSVS-L1', 'name': 'OWASP-CSVS-L1'},
    # {'ref': 'OWASP-CSVS-L2', 'name': 'OWASP-CSVS-L2'},
    # {'ref': 'OWASP-CSVS-L3', 'name': 'OWASP-CSVS-L3'},
    # {'ref': 'owasp-docker-top-10-2018', 'name': 'OWASP Docker Top 10 2018'},
    # {'ref': 'owasp-kubernetes-top-10-2022', 'name': 'OWASP Kubernetes Top 10 2022'},
    # {'ref': 'owasp-masvs-testing-guide', 'name': 'OWASP MASVS'},
    # {'ref': 'owasp-mobile-top-10-2016', 'name': 'OWASP Mobile Top 10 2016'},
    # {'ref': 'owasp-top-10-2017', 'name': 'OWASP Top 10 2017'},
    # {'ref': 'PCI-DSS-v4.0', 'name': 'PCI-DSS-v4.0'},
    # {'ref': 'pci-sss', 'name': 'PCI Secure Software Standard'},
    # {'ref': 'swift-cscf', 'name': 'SWIFT CSCF'},
    # {'ref': 'unece-wp29-csms', 'name': 'UNECE WP.29 Cybersecurity Regulation (CSMS)'},

}

IRIUSRISK_API_HEADERS = {
    "v1": {
        'accept': 'application/json',
        'Content-Type': 'application/json',
    },
    "v2": {
        'accept': 'application/hal+json',
        'Content-Type': 'application/json',
    },
    "v2xml": {
        'accept': 'application/xml',
        'Content-Type': 'application/json'
    },
    "v2multipart": {
        'accept': 'application/hal+json',
        # 'Content-Type': 'multipart/form-data'
    }
}

CRE_MAPPING_NAME = {
    "NIST SP 800-53 Rev5": "NIST 800-53 v5",
    "NIST 800-53 v5": "NIST 800-53 v5",
    "ASVS V4": "ASVS",
    "ASVS": "ASVS",
    "ISO 27001/2": "ISO 27001",
    "ISO 27001": "ISO 27001"
}

TM_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        "security_threats": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "threat_id": {
                        "type": "string"
                    },
                    "threat_name": {
                        "type": "string"
                    },
                    "description": {
                        "type": "string"
                    },
                    "countermeasures": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "countermeasure_id": {
                                    "type": "string"
                                },
                                "countermeasure_name": {
                                    "type": "string"
                                },
                                "description": {
                                    "type": "string"
                                }
                            },
                            "required": [
                                "countermeasure_id",
                                "countermeasure_name",
                                "description"
                            ]
                        }
                    }
                },
                "required": [
                    "threat_id",
                    "threat_name",
                    "description",
                    "countermeasures"
                ]
            }
        }
    },
    "required": [
        "security_threats"
    ]
}

STRIDE_LIST = {
    "S": {
        "ref": "UC-STRIDE-SPOOFING",
        "name": "Spoofing",
        "desc": "Spoofing involves an attacker pretending to be someone else by falsifying data or identity. This can "
                "include spoofing email addresses, IP addresses, or user identities to gain unauthorized access to "
                "systems or information."
    },
    "T": {
        "ref": "UC-STRIDE-TAMPERING",
        "name": "Tampering",
        "desc": "Tampering refers to unauthorized modification of data or systems. Attackers may alter data in "
                "transit or modify software components to introduce vulnerabilities or compromise the integrity of "
                "the system."
    },
    "R": {
        "ref": "UC-STRIDE-REPUDIATION",
        "name": "Repudiation",
        "desc": "Repudiation involves denying an action or event that has taken place. In a security context, "
                "repudiation threats can occur when a user denies performing a specific action, such as denying "
                "sending a message or making a transaction."
    },
    "I": {
        "ref": "UC-STRIDE-INFORMATION-DISCLOSURE",
        "name": "Information Disclosure",
        "desc": "Information disclosure occurs when sensitive data is exposed to unauthorized parties. This can "
                "include unauthorized access to confidential information, such as personal data, financial records, "
                "or intellectual property."
    },
    "D": {
        "ref": "UC-STRIDE-DENIAL-OF-SERVICE",
        "name": "Denial of Service",
        "desc": "Denial of Service attacks aim to disrupt the availability of services or resources to legitimate "
                "users. Attackers overwhelm systems with excessive traffic or requests, causing them to become "
                "unresponsive or unavailable to users."
    },
    "E": {
        "ref": "UC-STRIDE-ELEVATION-OF-PRIVILEGE",
        "name": "Elevation of Privilege",
        "desc": "Elevation of privilege involves an attacker gaining higher levels of access or permissions than "
                "intended. By exploiting vulnerabilities, attackers can escalate their privileges within a system to "
                "perform unauthorized actions or access sensitive data."
    },
    "L": {
        "ref": "UC-STRIDE-LATERAL-MOVEMENT",
        "name": "Lateral Movement",
        "desc": "Lateral Movement refers to the technique used by attackers to move horizontally across a network "
                "after gaining initial access. Once inside a network, attackers seek to explore and compromise "
                "additional systems to escalate their attack and access valuable resources."
    }
}

CATEGORIES_LIST = {
    "google-cloud-platform": {
        "ref": "google-cloud-platform",
        "name": "Google Cloud Platform",
        "desc": ""
    },
    "kubernetes": {
        "ref": "kubernetes",
        "name": "Kubernetes",
        "desc": ""
    },
    "functional": {
        "ref": "functional",
        "name": "Functional",
        "desc": ""
    },
    "network-components": {
        "ref": "network-components",
        "name": "Network Components",
        "desc": ""
    },
    "data-store": {
        "ref": "data-store",
        "name": "Data store",
        "desc": ""
    },
    "regulatory": {
        "ref": "regulatory",
        "name": "Regulatory",
        "desc": ""
    },
    "oracle-cloud-infrastructure": {
        "ref": "oracle-cloud-infrastructure",
        "name": "Oracle Cloud Infrastructure",
        "desc": ""
    },
    "amazon-web-services": {
        "ref": "amazon-web-services",
        "name": "Amazon Web Services",
        "desc": ""
    },
    "docker-category": {
        "ref": "docker-category",
        "name": "Docker",
        "desc": ""
    },
    "general": {
        "ref": "general",
        "name": "General",
        "desc": ""
    },
    "salesforce-components": {
        "ref": "salesforce-components",
        "name": "Salesforce components",
        "desc": ""
    },
    "microsoft-azure": {
        "ref": "microsoft-azure",
        "name": "Microsoft Azure",
        "desc": ""
    },
    "message-broker": {
        "ref": "message-broker",
        "name": "Message Broker",
        "desc": ""
    },
    "service-side": {
        "ref": "service-side",
        "name": "Server-side",
        "desc": ""
    },
    "on-premises-architecture": {
        "ref": "on-premises-architecture",
        "name": "On Premises Architecture",
        "desc": ""
    },
    "microservice-architecture": {
        "ref": "microservice-architecture",
        "name": "Microservice architecture",
        "desc": ""
    },
    "hardware": {
        "ref": "hardware",
        "name": "Hardware",
        "desc": ""
    },
    "virtual-components": {
        "ref": "virtual-components",
        "name": "Virtual Components",
        "desc": ""
    },
    "sap-components": {
        "ref": "sap-components",
        "name": "SAP Components",
        "desc": ""
    },
    "vmware": {
        "ref": "vmware",
        "name": "VMware",
        "desc": ""
    },
    "boundary-devices": {
        "ref": "boundary-devices",
        "name": "Boundary Devices",
        "desc": ""
    },
    "financial-services": {
        "ref": "financial-services",
        "name": "Financial Services",
        "desc": ""
    },
    "blockchain": {
        "ref": "blockchain",
        "name": "Blockchain",
        "desc": ""
    },
    "machine-learning-artificial-intelligence": {
        "ref": "machine-learning-artificial-intelligence",
        "name": "ML/AI",
        "desc": ""
    },
    "iot-components": {
        "ref": "iot-components",
        "name": "IoT components",
        "desc": ""
    },
    "automotive": {
        "ref": "automotive",
        "name": "Automotive",
        "desc": ""
    },
    "client-side": {
        "ref": "client-side",
        "name": "Client-side",
        "desc": ""
    },
    "generic-components": {
        "ref": "generic-components",
        "name": "Generic Components",
        "desc": ""
    },
    "alibaba-cloud": {
        "ref": "alibaba-cloud",
        "name": "Alibaba Cloud",
        "desc": ""
    }
}

SF_C_MAP = {
    "SF-C-MITRE": [CUSTOM_FIELD_ATTACK_ENTERPRISE_MITIGATION,
                   CUSTOM_FIELD_ATTACK_ICS_MITIGATION,
                   CUSTOM_FIELD_ATTACK_MOBILE_MITIGATION,
                   CUSTOM_FIELD_ATLAS_MITIGATION],
    "SF-C-STANDARD-BASELINE": [CUSTOM_FIELD_STANDARD_BASELINE_REF],
    "SF-C-STANDARD-SECTION": [CUSTOM_FIELD_STANDARD_BASELINE_SECTION],
    "SF-C-SCOPE": [CUSTOM_FIELD_SCOPE]
}

SF_T_MAP = {
    "SF-T-MITRE": [CUSTOM_FIELD_ATTACK_ENTERPRISE_TECHNIQUE,
                   CUSTOM_FIELD_ATTACK_ICS_TECHNIQUE,
                   CUSTOM_FIELD_ATTACK_MOBILE_TECHNIQUE,
                   CUSTOM_FIELD_ATLAS_TECHNIQUE],
    "SF-T-STRIDE-LM": [CUSTOM_FIELD_STRIDE]
}

HINTS = [
    "ChatGPT is thinking, wait a moment...",
    "Did you know that you can add metadata? Try to use 'isra screening' to see what you can do",
    "You can check the current status of a component by using 'isra component info'",
    "Use 'isra screening baseline' to set the baseline standard on every countermeasure in your threat model",
    "Sometimes ChatGPT may take its time to answer, just wait a bit",
    "If you get a weird error don't forget to share the temp.irius file or the XML/YAML source file",
    "Use 'isra screening sections' to find the best section from a base standard (if you added it)",
    "Use 'isra screening scope' to find the scope of a countermeasure",
    "The 'isra screening cwe' will find the best CWE for a countermeasure and will create a weakness in IR",
    "Components can be saved in XML or YAML using 'isra component save --format <xml/yaml>'",
    "If something went wrong when loading a YAML file I'll help you by telling the errors that have to be fixed",
    "Save your current configuration using 'isra config save'",
    "Use --help on any command to see available options for the command",
    "Set a company name to append a prefix to the library that will be uploaded to IriusRisk if you need it",
    "Use 'isra config info' to learn about the configurable parameters in ISRA",
    "Use 'isra screening autoscreening' to perform an automatic screening, but don't forget to fix values later!",
    "Use 'isra screening fix' to fix every value that might be wrong, especially after the autoscreening",
    "The command 'isra standards show' will show you the whole list of supported standards",
    "If the autoscreening doesn't do what you want you can modify its behavior by editing the config file"
]
