#!/usr/bin/env python3
import unittest
from unittest.mock import patch, MagicMock
import os
import tempfile
from pathlib import Path
from config.commands.codex_remedium.commands.codebase_search import CodebaseSearchCommand, codebase_search

class TestCodebaseSearch(unittest.TestCase):
    def setUp(self):
        """Set up test environment."""
        self.command = CodebaseSearchCommand()
        
        # Create temporary test files
        self.temp_dir = tempfile.mkdtemp()
        self.test_files = self._create_test_files()
    
    def tearDown(self):
        """Clean up test environment."""
        # Remove temporary files
        for file_path in self.test_files:
            os.remove(file_path)
        os.rmdir(self.temp_dir)
    
    def _create_test_files(self):
        """Create temporary test files with sample content."""
        files = []
        
        # Test file 1: Python file with function
        file1_path = os.path.join(self.temp_dir, "test_func.py")
        with open(file1_path, "w") as f:
            f.write('''
def test_function():
    """Test function docstring."""
    print("Hello")
    
def another_function():
    return 42
''')
        files.append(file1_path)
        
        # Test file 2: Python file with class
        file2_path = os.path.join(self.temp_dir, "test_class.py")
        with open(file2_path, "w") as f:
            f.write('''
class TestClass:
    """Test class docstring."""
    def method(self):
        print("Method")
''')
        files.append(file2_path)
        
        return files
    
    def test_basic_search(self):
        """Test basic search functionality."""
        result = self.command.execute("print", [self.temp_dir])
        
        self.assertEqual(result['status'], 'success')
        self.assertGreater(len(result['matches']), 0)
        self.assertEqual(result['count'], len(result['matches']))
    
    def test_no_matches(self):
        """Test search with no matches."""
        result = self.command.execute("nonexistenttext", [self.temp_dir])
        
        self.assertEqual(result['status'], 'success')
        self.assertEqual(len(result['matches']), 0)
        self.assertEqual(result['count'], 0)
    
    def test_context_extraction(self):
        """Test context extraction from snippets."""
        snippet = [
            {'content': 'def test_function():', 'is_match': False},
            {'content': '    print("test")', 'is_match': True}
        ]
        
        context = self.command._extract_context(snippet)
        self.assertEqual(context['type'], 'function')
        self.assertEqual(context['name'], 'test_function')
    
    @patch('subprocess.run')
    def test_command_error(self, mock_run):
        """Test error handling."""
        # Mock subprocess.run to raise an exception
        mock_run.side_effect = Exception("Command failed")
        
        result = self.command.execute("test")
        self.assertEqual(result['status'], 'error')
        self.assertIn('error', result)
    
    def test_module_function(self):
        """Test the module-level function."""
        result = codebase_search("print", [self.temp_dir])
        self.assertEqual(result['status'], 'success')
    
    def test_relative_paths(self):
        """Test that file paths are properly relativized."""
        with patch('os.getcwd') as mock_getcwd:
            mock_getcwd.return_value = self.temp_dir
            result = self.command.execute("print", [self.temp_dir])
            
            for match in result['matches']:
                self.assertFalse(os.path.isabs(match['file']))

if __name__ == '__main__':
    unittest.main()
