#!/usr/bin/env python3
from typing import Dict, Any, Optional
import re

class CodexRemediumParser:
    """Parser for Codex Remedium command outputs.
    
    This parser handles:
    1. Command output formatting
    2. Error detection and formatting
    3. Code block extraction
    4. File change summaries
    """
    
    def __init__(self):
        self.code_block_pattern = re.compile(r"```(\w+)?\n(.*?)```", re.DOTALL)
        self.file_change_pattern = re.compile(r"MODIFIED:\s+(\S+)")
    
    def parse_output(self, output: str) -> Dict[str, Any]:
        """Parse command output into structured format.
        
        Args:
            output: Raw command output
            
        Returns:
            Dict[str, Any]: Structured output
        """
        result = {
            'raw_output': output,
            'code_blocks': self._extract_code_blocks(output),
            'file_changes': self._extract_file_changes(output),
            'errors': self._extract_errors(output),
            'summary': self._generate_summary(output)
        }
        
        return result
    
    def _extract_code_blocks(self, text: str) -> list:
        """Extract code blocks with language information."""
        blocks = []
        for match in self.code_block_pattern.finditer(text):
            language = match.group(1) or 'text'
            code = match.group(2)
            blocks.append({
                'language': language,
                'code': code
            })
        return blocks
    
    def _extract_file_changes(self, text: str) -> list:
        """Extract information about file modifications."""
        changes = []
        for match in self.file_change_pattern.finditer(text):
            changes.append(match.group(1))
        return changes
    
    def _extract_errors(self, text: str) -> list:
        """Extract error messages from output."""
        errors = []
        error_patterns = [
            (r"Error:\s*(.*?)(?:\n|$)", "Error"),
            (r"Exception:\s*(.*?)(?:\n|$)", "Exception"),
            (r"ValidationError:\s*(.*?)(?:\n|$)", "Validation Error")
        ]
        
        for pattern, error_type in error_patterns:
            for match in re.finditer(pattern, text):
                errors.append({
                    'type': error_type,
                    'message': match.group(1)
                })
        
        return errors
    
    def _generate_summary(self, text: str) -> str:
        """Generate a brief summary of the output."""
        lines = text.split('\n')
        if len(lines) <= 3:
            return text
        
        return f"{lines[0]}\n...\n{lines[-1]}"
