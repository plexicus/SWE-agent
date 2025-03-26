#!/usr/bin/env python3
import unittest
import os
import tempfile
import time
from pathlib import Path
from config.commands.codex_remedium.commands.run_command import RunCommandCommand, run_command

class TestRunCommand(unittest.TestCase):
    def setUp(self):
        """Set up test environment."""
        self.command = RunCommandCommand()
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.temp_dir):
            os.rmdir(self.temp_dir)
    
    def test_basic_command(self):
        """Test basic command execution."""
        result = self.command.execute("echo 'test'")
        
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['exit_code'], 0)
        self.assertIn('test', result['stdout'])
        self.assertEqual(result['stderr'], '')
    
    def test_working_directory(self):
        """Test command execution in specific working directory."""
        result = self.command.execute("pwd", cwd=self.temp_dir)
        
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['exit_code'], 0)
        self.assertIn(self.temp_dir, result['stdout'])
    
    def test_command_failure(self):
        """Test handling of failed commands."""
        result = self.command.execute("nonexistentcommand")
        
        self.assertEqual(result['status'], 'error')
        self.assertIn('error', result)
    
    def test_invalid_working_directory(self):
        """Test error handling for invalid working directory."""
        result = self.command.execute(
            "echo 'test'",
            cwd="/nonexistent/directory"
        )
        
        self.assertEqual(result['status'], 'error')
        self.assertIn('error', result)
    
    def test_empty_command(self):
        """Test error handling for empty command."""
        result = self.command.execute("")
        
        self.assertEqual(result['status'], 'error')
        self.assertIn('error', result)
    
    def test_unsafe_command(self):
        """Test rejection of unsafe commands."""
        unsafe_commands = [
            "echo 'test' && ls",
            "echo 'test' || ls",
            "echo 'test' | grep test",
            "echo 'test' > file.txt",
            "echo $PATH",
            "echo `ls`",
            "echo \\test"
        ]
        
        for cmd in unsafe_commands:
            result = self.command.execute(cmd)
            self.assertEqual(
                result['status'],
                'error',
                f"Command should be rejected: {cmd}"
            )
    
    def test_command_timeout(self):
        """Test command timeout."""
        result = self.command.execute(
            "sleep 2",
            timeout=1
        )
        
        self.assertEqual(result['status'], 'error')
        self.assertIn('timeout', result['error'].lower())
    
    def test_non_blocking(self):
        """Test non-blocking command execution."""
        result = self.command.execute(
            "sleep 1",
            blocking=False
        )
        
        self.assertEqual(result['status'], 'running')
        self.assertIn('pid', result)
        
        # Wait for process to finish
        time.sleep(1.5)
    
    def test_environment_variables(self):
        """Test environment variable handling."""
        result = self.command.execute("echo $PAGER")
        
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['exit_code'], 0)
        self.assertIn('cat', result['stdout'])
    
    def test_command_output_capture(self):
        """Test capturing command output."""
        # Test stdout
        result = self.command.execute("echo 'stdout test'")
        self.assertIn('stdout test', result['stdout'])
        
        # Test stderr
        result = self.command.execute("ls nonexistentfile")
        self.assertNotEqual(result['stderr'], '')
    
    def test_module_function(self):
        """Test the module-level function."""
        result = run_command("echo 'test'")
        self.assertEqual(result['status'], 'success')
        self.assertIn('test', result['stdout'])

if __name__ == '__main__':
    unittest.main()
