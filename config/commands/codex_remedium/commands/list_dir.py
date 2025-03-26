#!/usr/bin/env python3
from typing import Dict, Any
import os
from pathlib import Path
from ..core.base_command import BaseCommand
from ..validators.input_validator import ValidationError

class ListDirCommand(BaseCommand):
    """Command for listing directory contents with metadata."""
    
    def execute(self, directory_path: str) -> Dict[str, Any]:
        """Execute list directory command.
        
        Args:
            directory_path: Absolute path to directory to list
            
        Returns:
            Dict containing directory contents with metadata
        """
        try:
            # Input validation
            if not os.path.isdir(directory_path):
                raise ValidationError(f"Directory not found: {directory_path}")
            
            # Get directory contents
            path = Path(directory_path)
            contents = []
            
            for item in path.iterdir():
                try:
                    stat = item.stat()
                    content = {
                        'name': item.name,
                        'path': str(item.relative_to(path)),
                        'type': 'directory' if item.is_dir() else 'file',
                        'size': stat.st_size if item.is_file() else None,
                        'modified': stat.st_mtime,
                        'children_count': self._count_children(item) if item.is_dir() else None
                    }
                    contents.append(content)
                except OSError as e:
                    self.logger.warning(f"Could not stat {item}: {e}")
            
            # Sort contents: directories first, then files, both alphabetically
            contents.sort(key=lambda x: (x['type'] != 'directory', x['name'].lower()))
            
            return {
                'status': 'success',
                'path': str(path),
                'contents': contents,
                'count': len(contents)
            }
            
        except Exception as e:
            self.logger.error(f"Error in list directory command: {str(e)}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def _count_children(self, path: Path) -> int:
        """Recursively count children in directory.
        
        Args:
            path: Path to directory
            
        Returns:
            Total number of children (files and directories)
        """
        try:
            count = 0
            for item in path.iterdir():
                count += 1
                if item.is_dir():
                    count += self._count_children(item)
            return count
        except OSError as e:
            self.logger.warning(f"Could not count children in {path}: {e}")
            return 0

def list_dir(directory_path: str) -> Dict[str, Any]:
    """
    List directory contents with metadata.
    
    Args:
        directory_path: Absolute path to directory to list
        
    Returns:
        Dict containing directory contents with metadata
    """
    command = ListDirCommand()
    return command.run(directory_path=directory_path)

if __name__ == "__main__":
    import sys
    import json
    
    args = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
    result = list_dir(**args)
    print(json.dumps(result))
