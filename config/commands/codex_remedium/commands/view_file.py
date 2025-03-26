#!/usr/bin/env python3
from typing import Dict, Any, Optional, List
import os
from pathlib import Path
from ..core.base_command import BaseCommand
from ..validators.input_validator import ValidationError

class ViewFileCommand(BaseCommand):
    """Command for viewing file contents with line range support."""
    
    def execute(
        self,
        absolute_path: str,
        start_line: int = 0,
        end_line: Optional[int] = None,
        include_summary: bool = True
    ) -> Dict[str, Any]:
        """Execute view file command.
        
        Args:
            absolute_path: Path to file to view
            start_line: Starting line number (0-based)
            end_line: Ending line number (inclusive)
            include_summary: Whether to include summary of other lines
            
        Returns:
            Dict containing file contents and metadata
        """
        try:
            # Input validation
            if not os.path.isfile(absolute_path):
                raise ValidationError(f"File not found: {absolute_path}")
            
            if start_line < 0:
                raise ValidationError("Start line cannot be negative")
            
            if end_line is not None and end_line < start_line:
                raise ValidationError("End line cannot be before start line")
            
            # Read file
            with open(absolute_path, 'r') as f:
                lines = f.readlines()
            
            total_lines = len(lines)
            
            # Validate line range
            if start_line >= total_lines:
                raise ValidationError(f"Start line {start_line} exceeds file length {total_lines}")
            
            if end_line is None:
                end_line = total_lines - 1
            elif end_line >= total_lines:
                end_line = total_lines - 1
            
            # Extract requested lines
            selected_lines = lines[start_line:end_line + 1]
            
            # Generate summary if requested
            summary = None
            if include_summary and (start_line > 0 or end_line < total_lines - 1):
                summary = self._generate_summary(
                    lines,
                    start_line,
                    end_line,
                    total_lines
                )
            
            return {
                'status': 'success',
                'file': absolute_path,
                'content': ''.join(selected_lines),
                'start_line': start_line,
                'end_line': end_line,
                'total_lines': total_lines,
                'summary': summary,
                'metadata': self._get_file_metadata(absolute_path)
            }
            
        except Exception as e:
            self.logger.error(f"Error in view file: {str(e)}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def _generate_summary(
        self,
        lines: List[str],
        start_line: int,
        end_line: int,
        total_lines: int
    ) -> Dict[str, Any]:
        """Generate summary of lines outside the selected range.
        
        Args:
            lines: All lines in the file
            start_line: Selected start line
            end_line: Selected end line
            total_lines: Total number of lines
            
        Returns:
            Dict containing summary information
        """
        summary = {
            'before': None,
            'after': None
        }
        
        # Summarize lines before selection
        if start_line > 0:
            before_lines = lines[:start_line]
            summary['before'] = {
                'line_count': start_line,
                'preview': ''.join(before_lines[-3:]) if before_lines else ''
            }
        
        # Summarize lines after selection
        if end_line < total_lines - 1:
            after_lines = lines[end_line + 1:]
            summary['after'] = {
                'line_count': total_lines - end_line - 1,
                'preview': ''.join(after_lines[:3]) if after_lines else ''
            }
        
        return summary
    
    def _get_file_metadata(self, file_path: str) -> Dict[str, Any]:
        """Get file metadata.
        
        Args:
            file_path: Path to file
            
        Returns:
            Dict containing file metadata
        """
        path = Path(file_path)
        stat = path.stat()
        
        return {
            'size': stat.st_size,
            'modified': stat.st_mtime,
            'extension': path.suffix,
            'is_binary': not self._is_text_file(file_path)
        }
    
    def _is_text_file(self, file_path: str) -> bool:
        """Check if file is a text file.
        
        Args:
            file_path: Path to file
            
        Returns:
            True if file is text, False if binary
        """
        try:
            with open(file_path, 'tr') as f:
                f.read(1024)
            return True
        except UnicodeDecodeError:
            return False

def view_file(
    absolute_path: str,
    start_line: int = 0,
    end_line: Optional[int] = None,
    include_summary: bool = True
) -> Dict[str, Any]:
    """
    View file contents with line range support.
    
    Args:
        absolute_path: Path to file to view
        start_line: Starting line number (0-based)
        end_line: Ending line number (inclusive)
        include_summary: Whether to include summary of other lines
        
    Returns:
        Dict containing file contents and metadata
    """
    command = ViewFileCommand()
    return command.run(
        absolute_path=absolute_path,
        start_line=start_line,
        end_line=end_line,
        include_summary=include_summary
    )

if __name__ == "__main__":
    import sys
    import json
    
    args = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
    result = view_file(**args)
    print(json.dumps(result))
