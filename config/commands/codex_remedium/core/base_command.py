#!/usr/bin/env python3
from abc import ABC, abstractmethod
import logging
from typing import Any, Dict, Optional
from ..utils.logging_utils import setup_logger
from ..validators.input_validator import validate_input

class BaseCommand(ABC):
    """Base class for all Codex Remedium commands."""
    
    def __init__(self):
        self.logger = setup_logger(self.__class__.__name__)

    @abstractmethod
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute the command with the given arguments.
        
        Args:
            **kwargs: Command-specific arguments
            
        Returns:
            Dict[str, Any]: Command execution results
        """
        raise NotImplementedError

    def validate(self, **kwargs) -> bool:
        """Validate command arguments.
        
        Args:
            **kwargs: Arguments to validate
            
        Returns:
            bool: True if validation passes, raises ValidationError otherwise
        """
        return validate_input(self.__class__.__name__, **kwargs)

    def run(self, **kwargs) -> Dict[str, Any]:
        """Run the command with validation and error handling.
        
        Args:
            **kwargs: Command arguments
            
        Returns:
            Dict[str, Any]: Command execution results
        """
        try:
            self.logger.info(f"Running {self.__class__.__name__} with args: {kwargs}")
            self.validate(**kwargs)
            result = self.execute(**kwargs)
            self.logger.info(f"Command completed successfully")
            return result
        except Exception as e:
            self.logger.error(f"Error executing command: {str(e)}")
            raise
