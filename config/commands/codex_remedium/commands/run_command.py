#!/usr/bin/env python3
from typing import Dict, Any, Optional
import os
import subprocess
import shlex
from pathlib import Path
from ..core.base_command import BaseCommand
from ..validators.input_validator import ValidationError

class RunCommandCommand(BaseCommand):
    """Command for safely executing shell commands."""
    
    def execute(
        self,
        command_line: str,
        cwd: Optional[str] = None,
        blocking: bool = True,
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """Execute a shell command.
        
        Args:
            command_line: Command to execute
            cwd: Working directory for command
            blocking: Whether to wait for command completion
            timeout: Timeout in seconds (only for blocking commands)
            
        Returns:
            Dict containing command execution results
        """
        try:
            # Input validation
            if not command_line:
                raise ValidationError("Command line cannot be empty")
            
            if cwd and not os.path.isdir(cwd):
                raise ValidationError(f"Working directory not found: {cwd}")
            
            # Parse command
            try:
                cmd = shlex.split(command_line)
            except ValueError as e:
                raise ValidationError(f"Invalid command line: {e}")
            
            # Security check: no shell metacharacters
            dangerous_chars = set(';&|><$`\\')
            if any(c in command_line for c in dangerous_chars):
                raise ValidationError("Command contains unsafe characters")
            
            # Prepare environment
            env = os.environ.copy()
            env['PAGER'] = 'cat'  # Disable paging
            
            # Execute command
            self.logger.debug(f"Running command: {command_line}")
            self.logger.debug(f"Working directory: {cwd or os.getcwd()}")
            
            if blocking:
                process = subprocess.run(
                    cmd,
                    cwd=cwd,
                    env=env,
                    capture_output=True,
                    text=True,
                    timeout=timeout
                )
                
                return {
                    'status': 'success',
                    'exit_code': process.returncode,
                    'stdout': process.stdout,
                    'stderr': process.stderr,
                    'command': command_line,
                    'cwd': cwd or os.getcwd()
                }
            else:
                # For non-blocking commands, start process and return immediately
                process = subprocess.Popen(
                    cmd,
                    cwd=cwd,
                    env=env,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                return {
                    'status': 'running',
                    'pid': process.pid,
                    'command': command_line,
                    'cwd': cwd or os.getcwd()
                }
                
        except subprocess.TimeoutExpired as e:
            self.logger.error(f"Command timed out after {timeout} seconds: {command_line}")
            return {
                'status': 'error',
                'error': f"Command timed out after {timeout} seconds",
                'command': command_line
            }
            
        except Exception as e:
            self.logger.error(f"Error in run command: {str(e)}")
            return {
                'status': 'error',
                'error': str(e),
                'command': command_line
            }

def run_command(
    command_line: str,
    cwd: Optional[str] = None,
    blocking: bool = True,
    timeout: Optional[int] = None
) -> Dict[str, Any]:
    """
    Safely execute a shell command.
    
    Args:
        command_line: Command to execute
        cwd: Working directory for command
        blocking: Whether to wait for command completion
        timeout: Timeout in seconds (only for blocking commands)
        
    Returns:
        Dict containing command execution results
    """
    command = RunCommandCommand()
    return command.run(
        command_line=command_line,
        cwd=cwd,
        blocking=blocking,
        timeout=timeout
    )

if __name__ == "__main__":
    import sys
    import json
    
    args = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
    result = run_command(**args)
    print(json.dumps(result))
