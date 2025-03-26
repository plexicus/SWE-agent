#!/usr/bin/env python3
import unittest
from unittest.mock import patch, MagicMock
import os
import tempfile
from pathlib import Path
from config.commands.codex_remedium.commands.find import FindCommand, find

class TestFind(unittest.TestCase):
    def setUp(self):
        """Set up test environment."""
        self.command = FindCommand()
        
        # Create temporary test directory structure
        self.temp_dir = tempfile.mkdtemp()
        self.test_files = self._create_test_files()
    
    def tearDown(self):
        """Clean up test environment."""
        # Remove temporary files
        for file_path in self.test_files:
            if os.path.exists(file_path):
                os.remove(file_path)
        if os.path.exists(self.temp_dir):
            os.rmdir(self.temp_dir)
    
    def _create_test_files(self):
        """Create temporary test files with various extensions."""
        files = []
        
        # Create Python file
        py_file = os.path.join(self.temp_dir, "test.py")
        with open(py_file, "w") as f:
            f.write("print('test')")
        files.append(py_file)
        
        # Create text file
        txt_file = os.path.join(self.temp_dir, "test.txt")
        with open(txt_file, "w") as f:
            f.write("test content")
        files.append(txt_file)
        
        # Create subdirectory
        subdir = os.path.join(self.temp_dir, "subdir")
        os.makedirs(subdir)
        
        # Create file in subdirectory
        subfile = os.path.join(subdir, "subtest.py")
        with open(subfile, "w") as f:
            f.write("print('subtest')")
        files.append(subfile)
        
        return files
    
    def test_basic_find(self):
        """Test basic find functionality."""
        result = self.command.execute(self.temp_dir)
        
        self.assertEqual(result['status'], 'success')
        self.assertGreater(len(result['matches']), 0)
        self.assertEqual(result['count'], len(result['matches']))
        
        # Verify file metadata
        for match in result['matches']:
            self.assertIn('path', match)
            self.assertIn('type', match)
            self.assertIn('size', match)
            self.assertIn('modified', match)
    
    def test_extension_filter(self):
        """Test finding files by extension."""
        result = self.command.execute(
            search_directory=self.temp_dir,
            extensions=['py']
        )
        
        self.assertEqual(result['status'], 'success')
        self.assertTrue(all(
            match['path'].endswith('.py')
            for match in result['matches']
            if match['type'] == 'file'
        ))
    
    def test_type_filter(self):
        """Test filtering by type."""
        # Test directory filter
        result = self.command.execute(
            search_directory=self.temp_dir,
            type_filter='directory'
        )
        
        self.assertEqual(result['status'], 'success')
        self.assertTrue(all(
            match['type'] == 'directory'
            for match in result['matches']
        ))
        
        # Test file filter
        result = self.command.execute(
            search_directory=self.temp_dir,
            type_filter='file'
        )
        
        self.assertEqual(result['status'], 'success')
        self.assertTrue(all(
            match['type'] == 'file'
            for match in result['matches']
        ))
    
    def test_max_depth(self):
        """Test max depth limitation."""
        result = self.command.execute(
            search_directory=self.temp_dir,
            max_depth=0
        )
        
        self.assertEqual(result['status'], 'success')
        self.assertTrue(all(
            os.path.dirname(match['path']) == self.temp_dir
            for match in result['matches']
        ))
    
    def test_pattern_matching(self):
        """Test pattern matching."""
        result = self.command.execute(
            search_directory=self.temp_dir,
            pattern="*.py"
        )
        
        self.assertEqual(result['status'], 'success')
        self.assertTrue(all(
            match['path'].endswith('.py')
            for match in result['matches']
            if match['type'] == 'file'
        ))
    
    def test_excludes(self):
        """Test exclude patterns."""
        result = self.command.execute(
            search_directory=self.temp_dir,
            excludes=["*.txt"]
        )
        
        self.assertEqual(result['status'], 'success')
        self.assertTrue(all(
            not match['path'].endswith('.txt')
            for match in result['matches']
            if match['type'] == 'file'
        ))
    
    def test_invalid_directory(self):
        """Test error handling for invalid directory."""
        result = self.command.execute(
            search_directory="/nonexistent/directory"
        )
        
        self.assertEqual(result['status'], 'error')
        self.assertIn('error', result)
    
    def test_invalid_type(self):
        """Test error handling for invalid type filter."""
        result = self.command.execute(
            search_directory=self.temp_dir,
            type_filter="invalid"
        )
        
        self.assertEqual(result['status'], 'error')
        self.assertIn('error', result)
    
    def test_module_function(self):
        """Test the module-level function."""
        result = find(self.temp_dir)
        self.assertEqual(result['status'], 'success')
    
    @patch('subprocess.run')
    def test_command_error(self, mock_run):
        """Test error handling for command execution failure."""
        mock_run.side_effect = Exception("Command failed")
        
        result = self.command.execute(self.temp_dir)
        self.assertEqual(result['status'], 'error')
        self.assertIn('error', result)

if __name__ == '__main__':
    unittest.main()
