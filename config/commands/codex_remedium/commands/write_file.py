#!/usr/bin/env python3
from typing import Dict, Any, Optional
import os
from pathlib import Path
from ..core.base_command import BaseCommand
from ..validators.input_validator import ValidationError

class WriteFileCommand(BaseCommand):
    """Command for safely writing content to files."""
    
    def execute(
        self,
        target_file: str,
        content: Optional[str] = None,
        empty_file: bool = False
    ) -> Dict[str, Any]:
        """Execute write file command.
        
        Args:
            target_file: Path to file to write
            content: Content to write to file
            empty_file: Whether to create an empty file
            
        Returns:
            Dict containing write operation results
        """
        try:
            # Input validation
            if not target_file:
                raise ValidationError("Target file path cannot be empty")
            
            if not empty_file and content is None:
                raise ValidationError("Must provide content or set empty_file=True")
            
            if empty_file and content is not None:
                raise ValidationError("Cannot provide content when empty_file=True")
            
            # Create parent directories if they don't exist
            path = Path(target_file)
            if not path.parent.exists():
                path.parent.mkdir(parents=True)
            
            # Check if file already exists
            if path.exists():
                raise ValidationError(f"File already exists: {target_file}")
            
            # Write file
            mode = 'w' if content is not None else 'x'
            with open(target_file, mode) as f:
                if content is not None:
                    f.write(content)
            
            return {
                'status': 'success',
                'file': target_file,
                'size': path.stat().st_size,
                'empty': empty_file
            }
            
        except Exception as e:
            self.logger.error(f"Error in write file: {str(e)}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def _validate_path(self, path: str) -> None:
        """Validate file path for potential security issues.
        
        Args:
            path: File path to validate
            
        Raises:
            ValidationError: If path is potentially unsafe
        """
        # Convert to absolute path
        abs_path = os.path.abspath(path)
        
        # Check for suspicious patterns
        suspicious_patterns = [
            '/etc/',
            '/bin/',
            '/sbin/',
            '/dev/',
            '/proc/',
            '/sys/',
            '/tmp/',
            '~/',
            '../'
        ]
        
        for pattern in suspicious_patterns:
            if pattern in abs_path:
                raise ValidationError(f"Path contains suspicious pattern: {pattern}")

def write_file(
    target_file: str,
    content: Optional[str] = None,
    empty_file: bool = False
) -> Dict[str, Any]:
    """
    Safely write content to a file.
    
    Args:
        target_file: Path to file to write
        content: Content to write to file
        empty_file: Whether to create an empty file
        
    Returns:
        Dict containing write operation results
    """
    command = WriteFileCommand()
    return command.run(
        target_file=target_file,
        content=content,
        empty_file=empty_file
    )

if __name__ == "__main__":
    import sys
    import json
    
    args = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
    result = write_file(**args)
    print(json.dumps(result))
