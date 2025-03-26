#!/usr/bin/env python3
from typing import Dict, Any, List, Optional
import subprocess
import os
from ..core.base_command import BaseCommand
from ..validators.input_validator import ValidationError

class GrepSearchCommand(BaseCommand):
    """Command for performing text-based searches in files."""
    
    def execute(self, query: str, includes: Optional[List[str]] = None,
               case_insensitive: bool = False, match_per_line: bool = True) -> Dict[str, Any]:
        """Execute grep search command.
        
        Args:
            query: Search pattern
            includes: Files or directories to search within
            case_insensitive: Whether to ignore case
            match_per_line: Whether to return matching lines or just file names
            
        Returns:
            Dict[str, Any]: Search results
        """
        try:
            # Build ripgrep command
            cmd = ['rg', '--no-heading', '--with-filename', '--line-number']
            
            if case_insensitive:
                cmd.append('--ignore-case')
                
            if not match_per_line:
                cmd.append('--files-with-matches')
                
            # Add pattern
            cmd.append(query)
            
            # Add include patterns
            if includes:
                for include in includes:
                    cmd.extend(['--glob', include])
            
            # Run command
            self.logger.debug(f"Running command: {' '.join(cmd)}")
            process = subprocess.run(cmd, capture_output=True, text=True)
            
            # Process output
            if process.returncode != 0 and process.returncode != 1:  # 1 means no matches
                raise Exception(f"Search failed: {process.stderr}")
            
            # Parse results
            results = []
            if process.stdout:
                for line in process.stdout.splitlines():
                    if match_per_line:
                        file_path, line_num, content = line.split(':', 2)
                        results.append({
                            'file': file_path,
                            'line': int(line_num),
                            'content': content
                        })
                    else:
                        results.append({'file': line})
            
            return {
                'status': 'success',
                'matches': results,
                'count': len(results)
            }
            
        except Exception as e:
            self.logger.error(f"Error in grep search: {str(e)}")
            return {
                'status': 'error',
                'error': str(e)
            }

def grep_search(query: str, includes: Optional[List[str]] = None,
                case_insensitive: bool = False, match_per_line: bool = True) -> Dict[str, Any]:
    """
    Perform a text-based search in files.
    
    Args:
        query: Search pattern
        includes: Files or directories to search within
        case_insensitive: Whether to ignore case
        match_per_line: Whether to return matching lines or just file names
    
    Returns:
        Dict[str, Any]: Search results with matching files and lines
    """
    command = GrepSearchCommand()
    return command.run(
        query=query,
        includes=includes,
        case_insensitive=case_insensitive,
        match_per_line=match_per_line
    )

if __name__ == "__main__":
    import sys
    import json
    
    args = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
    result = grep_search(**args)
    print(json.dumps(result))
