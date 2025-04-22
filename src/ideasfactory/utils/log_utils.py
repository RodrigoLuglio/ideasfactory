"""
Logging utilities for IdeasFactory.

This module provides utilities for safely logging data, particularly
sanitizing sensitive information like API keys.
"""

import os
import re
from typing import Dict, Any

# List of environment variable name patterns that might contain sensitive data
SENSITIVE_ENV_PATTERNS = [
    re.compile(r'.*api[_]?key.*', re.IGNORECASE),
    re.compile(r'.*secret.*', re.IGNORECASE),
    re.compile(r'.*password.*', re.IGNORECASE),
    re.compile(r'.*token.*', re.IGNORECASE),
    re.compile(r'.*credential.*', re.IGNORECASE),
    re.compile(r'.*auth.*', re.IGNORECASE),
    # Specific to this application
    re.compile(r'openai.*', re.IGNORECASE),
    re.compile(r'.*search_api_key.*', re.IGNORECASE),
]

def is_sensitive_variable(var_name: str) -> bool:
    """
    Check if a variable name might contain sensitive information.
    
    Args:
        var_name: Name of the variable to check
        
    Returns:
        True if the variable might contain sensitive info, False otherwise
    """
    for pattern in SENSITIVE_ENV_PATTERNS:
        if pattern.match(var_name):
            return True
    return False

def sanitize_environment_variables(env_vars: Dict[str, str]) -> Dict[str, Any]:
    """
    Sanitize environment variables by replacing sensitive values with a placeholder.
    
    Args:
        env_vars: Dictionary of environment variables
        
    Returns:
        Sanitized dictionary with sensitive values replaced
    """
    sanitized = {}
    
    for key, value in env_vars.items():
        if is_sensitive_variable(key):
            # Replace the value with a placeholder indicating the type
            sanitized[key] = "[REDACTED]"
        else:
            sanitized[key] = value
            
    return sanitized

def get_safe_env_vars() -> Dict[str, Any]:
    """
    Get a sanitized version of the environment variables.
    
    Returns:
        Dictionary with environment variables where sensitive data is redacted
    """
    return sanitize_environment_variables(dict(os.environ))

