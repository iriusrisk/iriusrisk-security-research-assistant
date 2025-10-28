"""
Configuration factory for creating and managing configuration instances
"""

import os
import logging
from typing import Optional, Dict, Any
from isra.src.ile.backend.app.configuration.constants import ILEConstants, ExcelConstants
from isra.src.ile.backend.app.configuration.safety import Safety
from isra.src.ile.backend.app.configuration.properties_manager import PropertiesManager
from isra.src.ile.backend.app.configuration.environment import EnvironmentConfig


class ConfigFactory:
    """
    Factory for creating and managing configuration instances
    """
    
    _instance: Optional['ConfigFactory'] = None
    _environment_config: Optional[EnvironmentConfig] = None
    
    def __new__(cls) -> 'ConfigFactory':
        """
        Singleton pattern implementation
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, '_initialized'):
            self.logger = logging.getLogger(__name__)
            self._initialized = True
            self._environment_config = None
    
    def get_environment_config(self) -> EnvironmentConfig:
        """
        Get environment configuration instance
        
        Returns:
            EnvironmentConfig: Environment configuration instance
        """
        if self._environment_config is None:
            self._environment_config = EnvironmentConfig()
        return self._environment_config
    
    def get_constants(self) -> Dict[str, Any]:
        """
        Get all constants
        
        Returns:
            Dict[str, Any]: Dictionary of all constants
        """
        return {
            'ile_constants': {
                'config_folder': ILEConstants.CONFIG_FOLDER,
                'output_folder': ILEConstants.OUTPUT_FOLDER,
                'projects_folder': ILEConstants.PROJECTS_FOLDER,
                'versions_folder': ILEConstants.VERSIONS_FOLDER,
                'config_properties_file': ILEConstants.CONFIG_PROPERTIES_FILE,
                'main_library_folder': ILEConstants.MAIN_LIBRARY_FOLDER,
                'non_ascii_codes': ILEConstants.NON_ASCII_CODES
            },
            'excel_constants': {
                'separator': ExcelConstants.SEPARATOR,
                'csv_separator': ExcelConstants.CSV_SEPARATOR,
                'library_property_header': ExcelConstants.LIBRARY_PROPERTY_HEADER,
                'library_property_color_1': ExcelConstants.LIBRARY_PROPERTY_COLOR_1,
                'library_property_color_2': ExcelConstants.LIBRARY_PROPERTY_COLOR_2,
                'library_component_header': ExcelConstants.LIBRARY_COMPONENT_HEADER,
                'library_component_color_1': ExcelConstants.LIBRARY_COMPONENT_COLOR_1,
                'library_component_color_2': ExcelConstants.LIBRARY_COMPONENT_COLOR_2,
                'library_standard_header': ExcelConstants.LIBRARY_STANDARD_HEADER,
                'library_standard_color_1': ExcelConstants.LIBRARY_STANDARD_COLOR_1,
                'library_standard_color_2': ExcelConstants.LIBRARY_STANDARD_COLOR_2,
                'rule_header': ExcelConstants.RULE_HEADER,
                'rule_color_1': ExcelConstants.RULE_COLOR_1,
                'rule_color_2': ExcelConstants.RULE_COLOR_2,
                'rule_condition_header': ExcelConstants.RULE_CONDITION_HEADER,
                'rule_condition_color_1': ExcelConstants.RULE_CONDITION_COLOR_1,
                'rule_condition_color_2': ExcelConstants.RULE_CONDITION_COLOR_2,
                'rule_action_header': ExcelConstants.RULE_ACTION_HEADER,
                'rule_action_color_1': ExcelConstants.RULE_ACTION_COLOR_1,
                'rule_action_color_2': ExcelConstants.RULE_ACTION_COLOR_2,
                'risk_pattern_header': ExcelConstants.RISK_PATTERN_HEADER,
                'risk_pattern_color_1': ExcelConstants.RISK_PATTERN_COLOR_1,
                'risk_pattern_color_2': ExcelConstants.RISK_PATTERN_COLOR_2,
                'use_case_header': ExcelConstants.USE_CASE_HEADER,
                'use_case_color_1': ExcelConstants.USE_CASE_COLOR_1,
                'use_case_color_2': ExcelConstants.USE_CASE_COLOR_2,
                'threat_header': ExcelConstants.THREAT_HEADER,
                'threat_color_1': ExcelConstants.THREAT_COLOR_1,
                'threat_color_2': ExcelConstants.THREAT_COLOR_2,
                'weakness_header': ExcelConstants.WEAKNESS_HEADER,
                'weakness_color_1': ExcelConstants.WEAKNESS_COLOR_1,
                'weakness_color_2': ExcelConstants.WEAKNESS_COLOR_2,
                'countermeasure_header': ExcelConstants.COUNTERMEASURE_HEADER,
                'countermeasure_color_1': ExcelConstants.COUNTERMEASURE_COLOR_1,
                'countermeasure_color_2': ExcelConstants.COUNTERMEASURE_COLOR_2,
                'components_component_name': ExcelConstants.COMPONENTS_COMPONENT_NAME,
                'components_component_ref': ExcelConstants.COMPONENTS_COMPONENT_REF,
                'components_component_desc': ExcelConstants.COMPONENTS_COMPONENT_DESC,
                'components_category_name': ExcelConstants.COMPONENTS_CATEGORY_NAME,
                'components_category_ref': ExcelConstants.COMPONENTS_CATEGORY_REF,
                'components_category_uuid': ExcelConstants.COMPONENTS_CATEGORY_UUID,
                'components_risk_patterns': ExcelConstants.COMPONENTS_RISK_PATTERNS,
                'components_visible': ExcelConstants.COMPONENTS_VISIBLE,
                'components_component_uuid': ExcelConstants.COMPONENTS_COMPONENT_UUID,
                'supported_standard_name': ExcelConstants.SUPPORTED_STANDARD_NAME,
                'supported_standard_ref': ExcelConstants.SUPPORTED_STANDARD_REF,
                'supported_standard_uuid': ExcelConstants.SUPPORTED_STANDARD_UUID,
                'rules_name': ExcelConstants.RULES_NAME,
                'rules_module': ExcelConstants.RULES_MODULE,
                'rules_gui': ExcelConstants.RULES_GUI,
                'rules_condition_name': ExcelConstants.RULES_CONDITION_NAME,
                'rules_condition_value': ExcelConstants.RULES_CONDITION_VALUE,
                'rules_condition_field': ExcelConstants.RULES_CONDITION_FIELD,
                'rules_action_name': ExcelConstants.RULES_ACTION_NAME,
                'rules_action_value': ExcelConstants.RULES_ACTION_VALUE,
                'rules_action_project': ExcelConstants.RULES_ACTION_PROJECT,
                'rules_last_header': ExcelConstants.RULES_LAST_HEADER,
                'risk_patterns_last_header': ExcelConstants.RISK_PATTERNS_LAST_HEADER
            }
        }
    
    def get_safety_validator(self) -> Safety:
        """
        Get safety validator instance
        
        Returns:
            Safety: Safety validator instance
        """
        return Safety
    
    def get_properties_manager(self) -> PropertiesManager:
        """
        Get properties manager instance
        
        Returns:
            PropertiesManager: Properties manager instance
        """
        return PropertiesManager
    
    def validate_environment(self) -> bool:
        """
        Validate that the environment is properly configured
        
        Returns:
            bool: True if environment is valid
        """
        try:
            env_config = self.get_environment_config()
            
            # Check if all required directories exist
            required_dirs = [
                ILEConstants.CONFIG_FOLDER,
                ILEConstants.OUTPUT_FOLDER,
                ILEConstants.PROJECTS_FOLDER,
                ILEConstants.VERSIONS_FOLDER
            ]
            
            for directory in required_dirs:
                if not os.path.exists(directory):
                    self.logger.error(f"Required directory does not exist: {directory}")
                    return False
            
            # Check if config file exists or can be created
            if not os.path.exists(ILEConstants.CONFIG_PROPERTIES_FILE):
                if not env_config.initialize_default_config():
                    self.logger.error("Failed to create default configuration file")
                    return False
            
            self.logger.info("Environment validation successful")
            return True
            
        except Exception as e:
            self.logger.error(f"Environment validation failed: {e}")
            return False
    
    def get_app_info(self) -> Dict[str, Any]:
        """
        Get application information
        
        Returns:
            Dict[str, Any]: Application information
        """
        return {
            'name': 'IriusRisk Library Editor',
            'version': '2.0.0',
            'environment': os.getenv('ENVIRONMENT', 'production'),
            'app_dir': ILEConstants._app_dir,
            'python_version': os.sys.version,
            'platform': os.name
        }


# Global configuration factory instance
config_factory = ConfigFactory()
