"""
Environment configuration and setup utilities
"""

import os
import logging
from typing import Dict, Any
from isra.src.ile.backend.app.configuration.constants import ILEConstants
from isra.src.ile.backend.app.configuration.properties_manager import PropertiesManager


class EnvironmentConfig:
    """
    Environment configuration manager
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._ensure_directories()
        self._setup_logging()
    
    def _ensure_directories(self) -> None:
        """
        Ensure all required directories exist
        """
        directories = [
            ILEConstants.CONFIG_FOLDER,
            ILEConstants.OUTPUT_FOLDER,
            ILEConstants.PROJECTS_FOLDER,
            ILEConstants.VERSIONS_FOLDER
        ]
        
        for directory in directories:
            try:
                os.makedirs(directory, exist_ok=True)
                self.logger.debug(f"Directory ensured: {directory}")
            except Exception as e:
                self.logger.error(f"Failed to create directory {directory}: {e}")
                raise
    
    def _setup_logging(self) -> None:
        """
        Setup logging configuration
        """
        log_file = os.path.join(ILEConstants.OUTPUT_FOLDER, "library-editor.log")
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
        self.logger.info("Logging configured")
    
    def get_app_config(self) -> Dict[str, Any]:
        """
        Get application configuration
        
        Returns:
            Dict[str, Any]: Application configuration
        """
        return {
            "app_dir": ILEConstants._app_dir,
            "config_folder": ILEConstants.CONFIG_FOLDER,
            "output_folder": ILEConstants.OUTPUT_FOLDER,
            "projects_folder": ILEConstants.PROJECTS_FOLDER,
            "versions_folder": ILEConstants.VERSIONS_FOLDER,
            "config_file": ILEConstants.CONFIG_PROPERTIES_FILE
        }
    
    def initialize_default_config(self) -> bool:
        """
        Initialize default configuration if not exists
        
        Returns:
            bool: True if successful
        """
        # Create default config file
        config_created = PropertiesManager.create_default_config()
        
        # Copy resource files to config folder
        resources_copied = PropertiesManager.copy_resource_files()
        
        return config_created and resources_copied
    
    def get_user_config(self) -> Dict[str, str]:
        """
        Get user configuration properties
        
        Returns:
            Dict[str, str]: User configuration properties
        """
        return PropertiesManager.get_all_properties()
    
    def is_development_mode(self) -> bool:
        """
        Check if running in development mode
        
        Returns:
            bool: True if in development mode
        """
        return os.getenv('ENVIRONMENT', 'production').lower() == 'development'
    
    def get_server_config(self) -> Dict[str, Any]:
        """
        Get server configuration
        
        Returns:
            Dict[str, Any]: Server configuration
        """
        return {
            "host": os.getenv('SERVER_HOST', '127.0.0.1'),
            "port": int(os.getenv('SERVER_PORT', '8080')),
            "debug": self.is_development_mode(),
            "reload": self.is_development_mode()
        }
