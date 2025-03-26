#!/usr/bin/env python3
from typing import Dict, Any, List, Optional
import os
import subprocess
from pathlib import Path
from ..core.base_command import BaseCommand
from ..validators.input_validator import ValidationError

class FindCommand(BaseCommand):
    """Command for finding files and directories based on various criteria."""
    
    def execute(
        self,
        search_directory: str,
        pattern: Optional[str] = None,
        extensions: Optional[List[str]] = None,
        excludes: Optional[List[str]] = None,
        max_depth: Optional[int] = None,
        type_filter: Optional[str] = None,
        full_path: bool = False
    ) -> Dict[str, Any]:
        """Execute find command.
        
        Args:
            search_directory: Directory to search in
            pattern: Pattern to match (glob format)
            extensions: File extensions to filter by
            excludes: Patterns to exclude
            max_depth: Maximum directory depth
            type_filter: Type filter (file/directory/any)
            full_path: Whether to match pattern against full path
            
        Returns:
            Dict containing found files/directories with metadata
        """
        try:
            # Input validation
            if not os.path.isdir(search_directory):
                raise ValidationError(f"Directory not found: {search_directory}")
            
            if type_filter and type_filter not in ('file', 'directory', 'any'):
                raise ValidationError("Type must be one of: file, directory, any")
            
            # Build fd command
            cmd = ['fd', '--hidden', '--no-ignore']
            
            if pattern:
                cmd.append(pattern)
                
            if extensions:
                for ext in extensions:
                    cmd.extend(['-e', ext])
                    
            if excludes:
                for excl in excludes:
                    cmd.extend(['--exclude', excl])
                    
            if max_depth is not None:
                cmd.extend(['--max-depth', str(max_depth)])
                
            if type_filter:
                if type_filter == 'file':
                    cmd.append('--type', 'f')
                elif type_filter == 'directory':
                    cmd.append('--type', 'd')
                    
            if full_path:
                cmd.append('--full-path')
                
            # Add search directory
            cmd.append('--search-path')
            cmd.append(search_directory)
            
            # Run command
            self.logger.debug(f"Running command: {' '.join(cmd)}")
            process = subprocess.run(cmd, capture_output=True, text=True)
            
            if process.returncode != 0:
                raise Exception(f"Find failed: {process.stderr}")
                
            # Process results
            results = []
            for line in process.stdout.splitlines():
                path = Path(line)
                try:
                    stat = path.stat()
                    results.append({
                        'path': str(path),
                        'type': 'directory' if path.is_dir() else 'file',
                        'size': stat.st_size if path.is_file() else None,
                        'modified': stat.st_mtime
                    })
                except OSError as e:
                    self.logger.warning(f"Could not stat {path}: {e}")
                    
            return {
                'status': 'success',
                'matches': results,
                'count': len(results)
            }
            
        except Exception as e:
            self.logger.error(f"Error in find command: {str(e)}")
            return {
                'status': 'error',
                'error': str(e)
            }

def find(
    search_directory: str,
    pattern: Optional[str] = None,
    extensions: Optional[List[str]] = None,
    excludes: Optional[List[str]] = None,
    max_depth: Optional[int] = None,
    type_filter: Optional[str] = None,
    full_path: bool = False
) -> Dict[str, Any]:
    """
    Find files and directories based on various criteria.
    
    Args:
        search_directory: Directory to search in
        pattern: Pattern to match (glob format)
        extensions: File extensions to filter by
        excludes: Patterns to exclude
        max_depth: Maximum directory depth
        type_filter: Type filter (file/directory/any)
        full_path: Whether to match pattern against full path
        
    Returns:
        Dict containing found files/directories with metadata
    """
    command = FindCommand()
    return command.run(
        search_directory=search_directory,
        pattern=pattern,
        extensions=extensions,
        excludes=excludes,
        max_depth=max_depth,
        type_filter=type_filter,
        full_path=full_path
    )

if __name__ == "__main__":
    import sys
    import json
    
    args = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
    result = find(**args)
    print(json.dumps(result))
