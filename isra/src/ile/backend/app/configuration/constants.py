"""
Constants for IriusRisk Library Editor
"""

import os
from typing import Dict


class ILEConstants:
    """
    Constants for IriusRisk Library Editor
    """
    
    # Get application directory (equivalent to Spring Boot's appdir)
    _app_dir = os.getenv('APPDIR', os.getcwd())
    
    # Folder paths
    CONFIG_FOLDER = os.path.join(_app_dir, "config")
    OUTPUT_FOLDER = os.path.join(_app_dir, "output")
    PROJECTS_FOLDER = os.path.join(_app_dir, "projects")
    VERSIONS_FOLDER = os.path.join(_app_dir, "versions")
    CONFIG_PROPERTIES_FILE = os.path.join(_app_dir, "config", "user_config.properties")
    
    # Configuration keys
    MAIN_LIBRARY_FOLDER = "main-library-folder"
    
    # Non-ASCII character mapping for text processing
    NON_ASCII_CODES: Dict[int, str] = {
        8220: '"',   # Left double quotation mark
        8221: '"',   # Right double quotation mark
        8216: "'",   # Left single quotation mark
        8217: "'",   # Right single quotation mark
        8211: "-",   # En dash
        8212: "-",   # Em dash
        8208: "-",   # Hyphen
        8804: "<=",  # Less than or equal to
        9658: ">",   # Black right-pointing triangle
        10060: "X",  # Cross mark
        9989: "V",   # Heavy check mark
        8203: "",    # Zero width space
        160: " ",    # Non-breaking space
        228: "a",    # Latin small letter a with diaeresis
        8239: " ",   # Narrow no-break space
        8594: "->",  # Rightwards arrow
        8209: "-",   # Non-breaking hyphen
        243: "o",    # Latin small letter o with acute
        10217: ">",  # Mathematical right angle bracket
        8230: "...", # Horizontal ellipsis
        8226: "*",   # Bullet
        215: "*",    # Multiplication sign
        173: "/",    # Soft hyphen
        8800: "!=",  # Not equal to
        8805: ">=",  # Greater than or equal to
        8776: "~",   # Almost equal to
        8364: "€",   # Euro sign
        8482: "(tm)", # Trade mark sign
        226: "a"     # Latin small letter a with circumflex
    }


class ExcelConstants:
    """
    Constants for Excel file processing
    """
    
    # Separators
    SEPARATOR = "##IRIUS##"
    CSV_SEPARATOR = ","
    
    # Library Property Colors
    LIBRARY_PROPERTY_HEADER = "2a6099"
    LIBRARY_PROPERTY_COLOR_1 = "dee6ef"
    LIBRARY_PROPERTY_COLOR_2 = "b4c7dc"
    
    # Library Component Colors
    LIBRARY_COMPONENT_HEADER = "ff9900"
    LIBRARY_COMPONENT_COLOR_1 = "ffdbb6"
    LIBRARY_COMPONENT_COLOR_2 = "ffb66c"
    
    # Library Standard Colors
    LIBRARY_STANDARD_HEADER = "800080"
    LIBRARY_STANDARD_COLOR_1 = "e0c2cd"
    LIBRARY_STANDARD_COLOR_2 = "bf819e"
    
    # Rule Colors
    RULE_HEADER = "2a6099"
    RULE_COLOR_1 = "dee6ef"
    RULE_COLOR_2 = "b4c7dc"
    
    # Rule Condition Colors
    RULE_CONDITION_HEADER = "ff9900"
    RULE_CONDITION_COLOR_1 = "ffdbb6"
    RULE_CONDITION_COLOR_2 = "ffb66c"
    
    # Rule Action Colors
    RULE_ACTION_HEADER = "800080"
    RULE_ACTION_COLOR_1 = "e0c2cd"
    RULE_ACTION_COLOR_2 = "bf819e"
    
    # Risk Pattern Colors
    RISK_PATTERN_HEADER = "2A6099"
    RISK_PATTERN_COLOR_1 = "DEE6EF"
    RISK_PATTERN_COLOR_2 = "B4C7DC"
    
    # Use Case Colors
    USE_CASE_HEADER = "800080"
    USE_CASE_COLOR_1 = "e0c2cd"
    USE_CASE_COLOR_2 = "bf819e"
    
    # Threat Colors
    THREAT_HEADER = "ff0000"
    THREAT_COLOR_1 = "ffd7d7"
    THREAT_COLOR_2 = "ffa6a6"
    
    # Weakness Colors
    WEAKNESS_HEADER = "38761d"
    WEAKNESS_COLOR_1 = "dde8cb"
    WEAKNESS_COLOR_2 = "afd095"
    
    # Countermeasure Colors
    COUNTERMEASURE_HEADER = "ff9900"
    COUNTERMEASURE_COLOR_1 = "ffdbb6"
    COUNTERMEASURE_COLOR_2 = "ffb66c"
    
    # Row numbers for Components sheet
    COMPONENTS_COMPONENT_NAME = 0
    COMPONENTS_COMPONENT_REF = 1
    COMPONENTS_COMPONENT_DESC = 2
    COMPONENTS_CATEGORY_NAME = 3
    COMPONENTS_CATEGORY_REF = 4
    COMPONENTS_CATEGORY_UUID = 5
    COMPONENTS_RISK_PATTERNS = 6
    COMPONENTS_VISIBLE = 7
    COMPONENTS_COMPONENT_UUID = 8
    
    # Row numbers for Supported Standards sheet
    SUPPORTED_STANDARD_NAME = 0
    SUPPORTED_STANDARD_REF = 1
    SUPPORTED_STANDARD_UUID = 2
    
    # Row numbers for Rules sheet
    RULES_NAME = 0
    RULES_MODULE = 1
    RULES_GUI = 2
    RULES_CONDITION_NAME = 3
    RULES_CONDITION_VALUE = 4
    RULES_CONDITION_FIELD = 5
    RULES_ACTION_NAME = 6
    RULES_ACTION_VALUE = 7
    RULES_ACTION_PROJECT = 8
    RULES_LAST_HEADER = 9
    
    # Row numbers for Risk Patterns sheet
    RISK_PATTERNS_LAST_HEADER = 34
