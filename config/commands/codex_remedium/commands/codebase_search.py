#!/usr/bin/env python3
from typing import Dict, Any, List, Optional
import subprocess
import os
from pathlib import Path
from ..core.base_command import BaseCommand
from ..validators.input_validator import ValidationError

class CodebaseSearchCommand(BaseCommand):
    """Command for searching code snippets in the codebase."""
    
    def execute(self, query: str, target_directories: Optional[List[str]] = None) -> Dict[str, Any]:
        """Execute codebase search command.
        
        This command uses ripgrep with additional context to find relevant code snippets.
        It also attempts to identify function and class definitions near the matches.
        
        Args:
            query: Search query
            target_directories: List of directories to search in, defaults to current directory
            
        Returns:
            Dict[str, Any]: Search results with code snippets and context
        """
        try:
            # Build ripgrep command with context
            cmd = [
                'rg',
                '--no-heading',
                '--with-filename',
                '--line-number',
                '--context=3',  # Show 3 lines before and after match
                '--type=python',  # Focus on Python files first
                '--smart-case'  # Case-insensitive if query is lowercase
            ]
            
            # Add pattern
            cmd.append(query)
            
            # Add target directories
            if target_directories:
                cmd.extend(target_directories)
            
            # Run command
            self.logger.debug(f"Running command: {' '.join(cmd)}")
            process = subprocess.run(cmd, capture_output=True, text=True)
            
            # Process output
            if process.returncode != 0 and process.returncode != 1:  # 1 means no matches
                raise Exception(f"Search failed: {process.stderr}")
            
            # Parse results and extract code snippets
            results = []
            current_file = None
            current_snippet = []
            
            if process.stdout:
                for line in process.stdout.splitlines():
                    if line.startswith('--'):  # Separator line
                        if current_snippet:
                            self._add_snippet_to_results(results, current_file, current_snippet)
                            current_snippet = []
                        continue
                        
                    if ':' in line:  # New match line
                        file_path, line_num, content = line.split(':', 2)
                        if file_path != current_file:
                            if current_snippet:
                                self._add_snippet_to_results(results, current_file, current_snippet)
                                current_snippet = []
                            current_file = file_path
                        current_snippet.append({
                            'line_number': int(line_num),
                            'content': content,
                            'is_match': True
                        })
                    else:  # Context line
                        current_snippet.append({
                            'content': line,
                            'is_match': False
                        })
                
                # Add last snippet if exists
                if current_snippet:
                    self._add_snippet_to_results(results, current_file, current_snippet)
            
            return {
                'status': 'success',
                'matches': results,
                'count': len(results)
            }
            
        except Exception as e:
            self.logger.error(f"Error in codebase search: {str(e)}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def _add_snippet_to_results(self, results: List[Dict], file_path: str, snippet: List[Dict]) -> None:
        """Add a code snippet to results with metadata.
        
        Args:
            results: List of results to append to
            file_path: Path to the file containing the snippet
            snippet: List of lines in the snippet with metadata
        """
        # Find the main match line
        match_lines = [line for line in snippet if line.get('is_match', False)]
        if not match_lines:
            return
            
        # Get relative path for better readability
        try:
            rel_path = str(Path(file_path).relative_to(os.getcwd()))
        except ValueError:
            rel_path = file_path
        
        results.append({
            'file': rel_path,
            'line': match_lines[0].get('line_number', 0),
            'snippet': snippet,
            'context': self._extract_context(snippet)
        })
    
    def _extract_context(self, snippet: List[Dict]) -> Dict[str, Any]:
        """Extract context information from snippet.
        
        Tries to identify function/class definitions and imports.
        
        Args:
            snippet: List of lines in the snippet
            
        Returns:
            Dict[str, Any]: Context information
        """
        context = {
            'type': None,  # 'function', 'class', or 'module'
            'name': None,
            'imports': []
        }
        
        for line in snippet:
            content = line.get('content', '').strip()
            
            # Check for function definition
            if content.startswith('def '):
                context['type'] = 'function'
                context['name'] = content[4:].split('(')[0].strip()
                break
                
            # Check for class definition
            elif content.startswith('class '):
                context['type'] = 'class'
                context['name'] = content[6:].split('(')[0].strip()
                break
                
            # Collect imports
            elif content.startswith('import ') or content.startswith('from '):
                context['imports'].append(content)
        
        return context

def codebase_search(query: str, target_directories: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Search for code snippets in the codebase.
    
    Args:
        query: Search query
        target_directories: List of directories to search in
    
    Returns:
        Dict[str, Any]: Search results containing relevant code snippets
    """
    command = CodebaseSearchCommand()
    return command.run(
        query=query,
        target_directories=target_directories
    )

if __name__ == "__main__":
    import sys
    import json
    
    args = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
    result = codebase_search(**args)
    print(json.dumps(result))
