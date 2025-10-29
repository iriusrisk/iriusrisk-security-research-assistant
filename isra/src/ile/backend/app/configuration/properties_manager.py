"""
Properties manager for handling configuration properties
"""

import os
import logging
import shutil
from pathlib import Path
from typing import Optional
from isra.src.ile.backend.app.configuration.constants import ILEConstants

# Configure logger
logger = logging.getLogger(__name__)


class PropertiesManager:
    """
    Manager for handling configuration properties
    """
    
    @staticmethod
    def get_property(property_name: str) -> Optional[str]:
        """
        Get a property value from the configuration file
        
        Args:
            property_name: The name of the property to retrieve
            
        Returns:
            Optional[str]: The property value if found, None otherwise
        """
        try:
            config_file_path = ILEConstants.CONFIG_PROPERTIES_FILE
            
            # Check if config file exists
            if not os.path.exists(config_file_path):
                logger.warning(f"Configuration file not found: {config_file_path}")
                return None
            
            # Read properties from file
            properties = {}
            with open(config_file_path, 'r', encoding='utf-8') as file:
                for line in file:
                    line = line.strip()
                    # Skip empty lines and comments
                    if not line or line.startswith('#'):
                        continue
                    
                    # Split on first '=' to handle values with '=' in them
                    if '=' in line:
                        key, value = line.split('=', 1)
                        properties[key.strip()] = value.strip()
            
            # Get the requested property
            property_value = properties.get(property_name)
            
            if property_value and property_value.strip():
                return property_value.strip()
            else:
                logger.debug(f"Property '{property_name}' not found or empty")
                return None
                
        except Exception as e:
            logger.error(f"Error loading configuration file or property not found: {e}")
            return None
    
    @staticmethod
    def set_property(property_name: str, property_value: str) -> bool:
        """
        Set a property value in the configuration file
        
        Args:
            property_name: The name of the property to set
            property_value: The value to set
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            config_file_path = ILEConstants.CONFIG_PROPERTIES_FILE
            
            # Ensure config directory exists
            config_dir = os.path.dirname(config_file_path)
            os.makedirs(config_dir, exist_ok=True)
            
            # Read existing properties
            properties = {}
            if os.path.exists(config_file_path):
                with open(config_file_path, 'r', encoding='utf-8') as file:
                    for line in file:
                        line = line.strip()
                        if not line or line.startswith('#'):
                            continue
                        if '=' in line:
                            key, value = line.split('=', 1)
                            properties[key.strip()] = value.strip()
            
            # Update the property
            properties[property_name] = property_value
            
            # Write back to file
            with open(config_file_path, 'w', encoding='utf-8') as file:
                for key, value in properties.items():
                    file.write(f"{key}={value}\n")
            
            logger.info(f"Property '{property_name}' set to '{property_value}'")
            return True
            
        except Exception as e:
            logger.error(f"Error setting property '{property_name}': {e}")
            return False
    
    @staticmethod
    def get_all_properties() -> dict:
        """
        Get all properties from the configuration file
        
        Returns:
            dict: Dictionary of all properties
        """
        try:
            config_file_path = ILEConstants.CONFIG_PROPERTIES_FILE
            
            if not os.path.exists(config_file_path):
                logger.warning(f"Configuration file not found: {config_file_path}")
                return {}
            
            properties = {}
            with open(config_file_path, 'r', encoding='utf-8') as file:
                for line in file:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    if '=' in line:
                        key, value = line.split('=', 1)
                        properties[key.strip()] = value.strip()
            
            return properties
            
        except Exception as e:
            logger.error(f"Error loading all properties: {e}")
            return {}
    
    @staticmethod
    def create_default_config() -> bool:
        """
        Create default configuration file if it doesn't exist
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            config_file_path = ILEConstants.CONFIG_PROPERTIES_FILE
            
            # Check if file already exists
            if os.path.exists(config_file_path):
                return True
            
            # Ensure config directory exists
            config_dir = os.path.dirname(config_file_path)
            os.makedirs(config_dir, exist_ok=True)
            
            # Create default properties
            default_properties = {
                "show-mitigation-values-on-changelog": "false",
                "load-project-on-startup": "",
                "main-library-folder": ""
            }
            
            # Write default properties to file
            with open(config_file_path, 'w', encoding='utf-8') as file:
                file.write("# IriusRisk Library Editor Configuration\n")
                file.write("# Default configuration file\n\n")
                for key, value in default_properties.items():
                    file.write(f"{key}={value}\n")
            
            logger.info(f"Default configuration file created: {config_file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating default configuration: {e}")
            return False
    
    @staticmethod
    def copy_resource_files() -> bool:
        """
        Copy resource files to config folder if they don't exist
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Get the resources directory path
            current_dir = Path(__file__).parent
            resources_dir = current_dir.parent.parent.parent.parent / "resources"
            
            if not resources_dir.exists():
                logger.warning(f"Resources directory not found: {resources_dir}")
                return False
            
            # Ensure config directory exists
            config_dir = Path(ILEConstants.CONFIG_FOLDER)
            config_dir.mkdir(parents=True, exist_ok=True)
            
            # List of resource files to copy
            resource_files = [
                "ysc_schema.json"
            ]
            
            # Copy each resource file if it doesn't exist in config
            for resource_file in resource_files:
                source_file = resources_dir / resource_file
                dest_file = config_dir / resource_file
                
                if source_file.exists() and not dest_file.exists():
                    shutil.copy2(source_file, dest_file)
                    logger.info(f"Copied resource file: {resource_file}")
                elif not source_file.exists():
                    logger.warning(f"Resource file not found: {source_file}")
                else:
                    logger.debug(f"Resource file already exists: {dest_file}")

            return True
            
        except Exception as e:
            logger.error(f"Error copying resource files: {e}")
            return False
