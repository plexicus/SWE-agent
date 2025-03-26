#!/usr/bin/env python3
from typing import Any, Dict
import os
import re

class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass

def validate_path(path: str, must_exist: bool = True) -> bool:
    """Validate a file or directory path.
    
    Args:
        path: Path to validate
        must_exist: Whether the path must exist
        
    Returns:
        bool: True if validation passes
        
    Raises:
        ValidationError: If validation fails
    """
    if not isinstance(path, str):
        raise ValidationError(f"Path must be a string, got {type(path)}")
    
    if must_exist and not os.path.exists(path):
        raise ValidationError(f"Path does not exist: {path}")
    
    return True

def validate_command(command: str) -> bool:
    """Validate a shell command.
    
    Args:
        command: Command to validate
        
    Returns:
        bool: True if validation passes
        
    Raises:
        ValidationError: If validation fails
    """
    if not isinstance(command, str):
        raise ValidationError(f"Command must be a string, got {type(command)}")
    
    # List of dangerous commands/patterns
    dangerous_patterns = [
        r"rm\s+-rf\s+/",
        r"mkfs",
        r"dd\s+if=",
        r">\s*/dev/",
        r":\(\)\s*{\s*:\|\:&\s*}\s*;:",  # Fork bomb
    ]
    
    for pattern in dangerous_patterns:
        if re.search(pattern, command):
            raise ValidationError(f"Potentially dangerous command detected: {command}")
    
    return True

def validate_input(command_name: str, **kwargs) -> bool:
    """Validate command input based on command-specific rules.
    
    Args:
        command_name: Name of the command
        **kwargs: Command arguments
        
    Returns:
        bool: True if validation passes
        
    Raises:
        ValidationError: If validation fails
    """
    validators = {
        'grep_search': {
            'query': lambda x: isinstance(x, str) and len(x) > 0,
            'includes': lambda x: x is None or (isinstance(x, list) and all(isinstance(i, str) for i in x)),
            'case_insensitive': lambda x: isinstance(x, bool),
            'match_per_line': lambda x: isinstance(x, bool)
        },
        'view_file': {
            'absolute_path': lambda x: validate_path(x),
            'start_line': lambda x: isinstance(x, int) and x >= 0,
            'end_line': lambda x: x is None or (isinstance(x, int) and x >= 0),
            'include_summary': lambda x: isinstance(x, bool)
        },
        'run_command': {
            'command_line': lambda x: validate_command(x),
            'cwd': lambda x: x is None or validate_path(x),
            'blocking': lambda x: isinstance(x, bool),
            'safe_to_auto_run': lambda x: isinstance(x, bool)
        }
    }
    
    if command_name not in validators:
        return True  # No specific validation rules for this command
        
    for arg_name, validator in validators[command_name].items():
        if arg_name in kwargs:
            if not validator(kwargs[arg_name]):
                raise ValidationError(f"Invalid value for {arg_name} in {command_name}")
    
    return True
