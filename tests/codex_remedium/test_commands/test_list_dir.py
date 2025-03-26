#!/usr/bin/env python3
import unittest
import os
import tempfile
import time
from pathlib import Path
from config.commands.codex_remedium.commands.list_dir import ListDirCommand, list_dir

class TestListDir(unittest.TestCase):
    def setUp(self):
        """Set up test environment."""
        self.command = ListDirCommand()
        
        # Create temporary test directory structure
        self.temp_dir = tempfile.mkdtemp()
        self.test_files = self._create_test_files()
    
    def tearDown(self):
        """Clean up test environment."""
        # Remove temporary files
        for file_path in self.test_files:
            if os.path.exists(file_path):
                os.remove(file_path)
        
        # Remove directories in reverse order (deepest first)
        for dir_path in sorted(self.test_dirs, reverse=True):
            if os.path.exists(dir_path):
                os.rmdir(dir_path)
    
    def _create_test_files(self):
        """Create temporary test directory structure."""
        files = []
        self.test_dirs = []
        
        # Create files in root
        file1 = os.path.join(self.temp_dir, "test1.txt")
        with open(file1, "w") as f:
            f.write("test1")
        files.append(file1)
        
        file2 = os.path.join(self.temp_dir, "test2.txt")
        with open(file2, "w") as f:
            f.write("test2")
        files.append(file2)
        
        # Create subdirectory
        subdir1 = os.path.join(self.temp_dir, "subdir1")
        os.makedirs(subdir1)
        self.test_dirs.append(subdir1)
        
        # Create files in subdirectory
        subfile1 = os.path.join(subdir1, "subtest1.txt")
        with open(subfile1, "w") as f:
            f.write("subtest1")
        files.append(subfile1)
        
        # Create nested subdirectory
        subdir2 = os.path.join(subdir1, "subdir2")
        os.makedirs(subdir2)
        self.test_dirs.append(subdir2)
        
        # Create file in nested subdirectory
        subfile2 = os.path.join(subdir2, "subtest2.txt")
        with open(subfile2, "w") as f:
            f.write("subtest2")
        files.append(subfile2)
        
        return files
    
    def test_basic_list(self):
        """Test basic directory listing."""
        result = self.command.execute(self.temp_dir)
        
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['path'], self.temp_dir)
        self.assertGreater(len(result['contents']), 0)
        self.assertEqual(result['count'], len(result['contents']))
    
    def test_content_metadata(self):
        """Test content metadata is correct."""
        result = self.command.execute(self.temp_dir)
        
        for content in result['contents']:
            self.assertIn('name', content)
            self.assertIn('path', content)
            self.assertIn('type', content)
            self.assertIn('size', content)
            self.assertIn('modified', content)
            self.assertIn('children_count', content)
            
            if content['type'] == 'file':
                self.assertIsNotNone(content['size'])
                self.assertIsNone(content['children_count'])
            else:
                self.assertIsNone(content['size'])
                self.assertIsNotNone(content['children_count'])
    
    def test_sorting(self):
        """Test contents are properly sorted."""
        result = self.command.execute(self.temp_dir)
        
        # Directories should come first
        dirs_done = False
        for content in result['contents']:
            if content['type'] == 'file':
                dirs_done = True
            if content['type'] == 'directory':
                self.assertFalse(dirs_done, "Found directory after files")
    
    def test_children_count(self):
        """Test children count is correct."""
        result = self.command.execute(self.temp_dir)
        
        for content in result['contents']:
            if content['type'] == 'directory':
                path = Path(os.path.join(self.temp_dir, content['path']))
                actual_count = sum(1 for _ in path.rglob('*'))
                self.assertEqual(content['children_count'], actual_count)
    
    def test_invalid_directory(self):
        """Test error handling for invalid directory."""
        result = self.command.execute("/nonexistent/directory")
        
        self.assertEqual(result['status'], 'error')
        self.assertIn('error', result)
    
    def test_permission_denied(self):
        """Test error handling for permission denied."""
        if os.name != 'nt':  # Skip on Windows
            restricted_dir = os.path.join(self.temp_dir, "restricted")
            os.makedirs(restricted_dir)
            os.chmod(restricted_dir, 0o000)
            
            try:
                result = self.command.execute(restricted_dir)
                self.assertEqual(result['status'], 'error')
            finally:
                os.chmod(restricted_dir, 0o755)
                os.rmdir(restricted_dir)
    
    def test_module_function(self):
        """Test the module-level function."""
        result = list_dir(self.temp_dir)
        self.assertEqual(result['status'], 'success')
    
    def test_relative_paths(self):
        """Test relative paths are correct."""
        result = self.command.execute(self.temp_dir)
        
        for content in result['contents']:
            # Path should be relative to the listed directory
            self.assertFalse(os.path.isabs(content['path']))
            # Full path should exist
            self.assertTrue(os.path.exists(os.path.join(self.temp_dir, content['path'])))

if __name__ == '__main__':
    unittest.main()
