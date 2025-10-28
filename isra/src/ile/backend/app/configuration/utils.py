"""
Configuration utilities and helpers
"""

import os
import logging
from typing import Dict, Any, Optional, List
from .constants import ILEConstants
from .properties_manager import PropertiesManager


class ConfigUtils:
    """
    Configuration utilities
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def normalize_path(self, path: str) -> str:
        """
        Normalize a file path
        
        Args:
            path: Path to normalize
            
        Returns:
            str: Normalized path
        """
        return os.path.normpath(os.path.expanduser(path))
    
    def get_relative_path(self, path: str, base_path: str = None) -> str:
        """
        Get relative path from base path
        
        Args:
            path: Target path
            base_path: Base path (defaults to app directory)
            
        Returns:
            str: Relative path
        """
        if base_path is None:
            base_path = ILEConstants._app_dir
        
        try:
            return os.path.relpath(path, base_path)
        except ValueError:
            return path
    
    def ensure_file_exists(self, file_path: str, create_dirs: bool = True) -> bool:
        """
        Ensure a file exists, optionally creating directories
        
        Args:
            file_path: Path to the file
            create_dirs: Whether to create parent directories
            
        Returns:
            bool: True if file exists or was created
        """
        try:
            if os.path.exists(file_path):
                return True
            
            if create_dirs:
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Create empty file
            with open(file_path, 'w') as f:
                pass
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to ensure file exists {file_path}: {e}")
            return False
    
    def get_file_size(self, file_path: str) -> Optional[int]:
        """
        Get file size in bytes
        
        Args:
            file_path: Path to the file
            
        Returns:
            Optional[int]: File size in bytes, None if file doesn't exist
        """
        try:
            if os.path.exists(file_path):
                return os.path.getsize(file_path)
            return None
        except Exception as e:
            self.logger.error(f"Failed to get file size {file_path}: {e}")
            return None
    
    def list_files_in_directory(self, directory: str, pattern: str = "*") -> List[str]:
        """
        List files in a directory matching a pattern
        
        Args:
            directory: Directory to search
            pattern: File pattern to match (default: "*")
            
        Returns:
            List[str]: List of matching file paths
        """
        try:
            if not os.path.exists(directory):
                return []
            
            import glob
            search_pattern = os.path.join(directory, pattern)
            return glob.glob(search_pattern)
        except Exception as e:
            self.logger.error(f"Failed to list files in {directory}: {e}")
            return []
    
    def clean_directory(self, directory: str, keep_files: List[str] = None) -> bool:
        """
        Clean a directory, optionally keeping specific files
        
        Args:
            directory: Directory to clean
            keep_files: List of files to keep (default: None)
            
        Returns:
            bool: True if successful
        """
        try:
            if not os.path.exists(directory):
                return True
            
            if keep_files is None:
                keep_files = []
            
            for filename in os.listdir(directory):
                file_path = os.path.join(directory, filename)
                
                if os.path.isfile(file_path):
                    if filename not in keep_files:
                        os.remove(file_path)
                        self.logger.debug(f"Removed file: {file_path}")
                elif os.path.isdir(file_path):
                    import shutil
                    shutil.rmtree(file_path)
                    self.logger.debug(f"Removed directory: {file_path}")
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to clean directory {directory}: {e}")
            return False
    
    def get_config_summary(self) -> Dict[str, Any]:
        """
        Get configuration summary
        
        Returns:
            Dict[str, Any]: Configuration summary
        """
        try:
            properties = PropertiesManager.get_all_properties()
            
            return {
                'app_directory': ILEConstants._app_dir,
                'config_folder': ILEConstants.CONFIG_FOLDER,
                'output_folder': ILEConstants.OUTPUT_FOLDER,
                'projects_folder': ILEConstants.PROJECTS_FOLDER,
                'versions_folder': ILEConstants.VERSIONS_FOLDER,
                'config_file_exists': os.path.exists(ILEConstants.CONFIG_PROPERTIES_FILE),
                'user_properties': properties,
                'directory_status': {
                    'config': os.path.exists(ILEConstants.CONFIG_FOLDER),
                    'output': os.path.exists(ILEConstants.OUTPUT_FOLDER),
                    'projects': os.path.exists(ILEConstants.PROJECTS_FOLDER),
                    'versions': os.path.exists(ILEConstants.VERSIONS_FOLDER)
                }
            }
        except Exception as e:
            self.logger.error(f"Failed to get configuration summary: {e}")
            return {}
    
    def validate_configuration(self) -> Dict[str, Any]:
        """
        Validate configuration
        
        Returns:
            Dict[str, Any]: Validation results
        """
        results = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        try:
            # Check directories
            required_dirs = [
                ('config', ILEConstants.CONFIG_FOLDER),
                ('output', ILEConstants.OUTPUT_FOLDER),
                ('projects', ILEConstants.PROJECTS_FOLDER),
                ('versions', ILEConstants.VERSIONS_FOLDER)
            ]
            
            for name, path in required_dirs:
                if not os.path.exists(path):
                    results['errors'].append(f"Required directory missing: {name} ({path})")
                    results['valid'] = False
                elif not os.access(path, os.W_OK):
                    results['warnings'].append(f"Directory not writable: {name} ({path})")
            
            # Check config file
            if not os.path.exists(ILEConstants.CONFIG_PROPERTIES_FILE):
                results['warnings'].append("Configuration file not found, will use defaults")
            
            # Check properties
            properties = PropertiesManager.get_all_properties()
            if not properties:
                results['warnings'].append("No user properties found")
            
        except Exception as e:
            results['valid'] = False
            results['errors'].append(f"Configuration validation failed: {e}")
        
        return results


# Global configuration utils instance
config_utils = ConfigUtils()
