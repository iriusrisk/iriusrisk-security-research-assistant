"""
Safety utilities for input validation
"""

import re
from typing import Optional


class Safety:
    """
    Safety utilities for input validation
    """
    
    @staticmethod
    def is_safe_input(input_string: Optional[str]) -> bool:
        """
        Check if the input is alphanumeric + "-" and "."
        
        Args:
            input_string: A random string to validate
            
        Returns:
            bool: True if input is safe (alphanumeric + "-" and "."), False otherwise
        """
        if input_string is None:
            return False
        
        # Pattern matches alphanumeric characters, dots, and hyphens
        pattern = r'^[A-Za-z0-9.-]+$'
        return bool(re.match(pattern, input_string))
