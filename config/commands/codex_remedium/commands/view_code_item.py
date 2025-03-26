#!/usr/bin/env python3
from typing import Dict, Any, Optional, List
import os
import ast
from pathlib import Path
from ..core.base_command import BaseCommand
from ..validators.input_validator import ValidationError

class ViewCodeItemCommand(BaseCommand):
    """Command for viewing specific code items like functions or classes."""
    
    def execute(self, file_path: str, node_path: str) -> Dict[str, Any]:
        """Execute view code item command.
        
        Args:
            file_path: Path to the file containing the code item
            node_path: Dot-separated path to the node (e.g., 'Class.method')
            
        Returns:
            Dict containing the code item content and metadata
        """
        try:
            # Input validation
            if not os.path.isfile(file_path):
                raise ValidationError(f"File not found: {file_path}")
            
            if not node_path:
                raise ValidationError("Node path cannot be empty")
            
            # Read file content
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Parse file
            try:
                tree = ast.parse(content)
            except SyntaxError as e:
                raise ValidationError(f"Could not parse file: {e}")
            
            # Find node
            node_names = node_path.split('.')
            current_node = tree
            
            for name in node_names:
                found = False
                for node in ast.iter_child_nodes(current_node):
                    if isinstance(node, (ast.ClassDef, ast.FunctionDef)) and node.name == name:
                        current_node = node
                        found = True
                        break
                if not found:
                    raise ValidationError(f"Node not found: {name}")
            
            # Extract node content
            node_lines = content.splitlines()[
                current_node.lineno - 1:
                current_node.end_lineno
            ]
            
            # Get imports needed by the node
            imports = self._find_imports(tree, current_node)
            
            return {
                'status': 'success',
                'file': file_path,
                'node_path': node_path,
                'content': '\n'.join(node_lines),
                'start_line': current_node.lineno,
                'end_line': current_node.end_lineno,
                'type': type(current_node).__name__,
                'imports': imports
            }
            
        except Exception as e:
            self.logger.error(f"Error in view code item: {str(e)}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def _find_imports(self, tree: ast.AST, target_node: ast.AST) -> List[str]:
        """Find imports needed by the target node.
        
        Args:
            tree: AST of the entire file
            target_node: Node to find imports for
            
        Returns:
            List of import statements as strings
        """
        imports = []
        node_start = target_node.lineno
        
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                # Add imports before the node
                if node.lineno < node_start:
                    if isinstance(node, ast.Import):
                        for name in node.names:
                            imports.append(f"import {name.name}")
                    else:
                        names = ', '.join(name.name for name in node.names)
                        level = '.' * node.level
                        module = f" {node.module}" if node.module else ""
                        imports.append(f"from {level}{module} import {names}")
                        
        return imports

def view_code_item(file_path: str, node_path: str) -> Dict[str, Any]:
    """
    View specific code items like functions or classes.
    
    Args:
        file_path: Path to the file containing the code item
        node_path: Dot-separated path to the node (e.g., 'Class.method')
        
    Returns:
        Dict containing the code item content and metadata
    """
    command = ViewCodeItemCommand()
    return command.run(
        file_path=file_path,
        node_path=node_path
    )

if __name__ == "__main__":
    import sys
    import json
    
    args = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
    result = view_code_item(**args)
    print(json.dumps(result))
