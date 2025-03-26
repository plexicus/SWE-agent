#!/usr/bin/env python3
import unittest
import os
import tempfile
import time
from pathlib import Path
from config.commands.codex_remedium.commands.view_file import ViewFileCommand, view_file

class TestViewFile(unittest.TestCase):
    def setUp(self):
        """Set up test environment."""
        self.command = ViewFileCommand()
        
        # Create temporary test files
        self.temp_dir = tempfile.mkdtemp()
        self.test_files = self._create_test_files()
    
    def tearDown(self):
        """Clean up test environment."""
        for file_path in self.test_files:
            if os.path.exists(file_path):
                os.remove(file_path)
        if os.path.exists(self.temp_dir):
            os.rmdir(self.temp_dir)
    
    def _create_test_files(self):
        """Create temporary test files."""
        files = []
        
        # Create text file
        text_file = os.path.join(self.temp_dir, "test.txt")
        with open(text_file, "w") as f:
            f.write("Line 1\nLine 2\nLine 3\nLine 4\nLine 5\n")
        files.append(text_file)
        
        # Create binary file
        binary_file = os.path.join(self.temp_dir, "test.bin")
        with open(binary_file, "wb") as f:
            f.write(bytes(range(256)))
        files.append(binary_file)
        
        return files
    
    def test_basic_view(self):
        """Test basic file viewing."""
        result = self.command.execute(self.test_files[0])
        
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['file'], self.test_files[0])
        self.assertIn('Line 1', result['content'])
        self.assertEqual(result['start_line'], 0)
        self.assertEqual(result['total_lines'], 5)
    
    def test_line_range(self):
        """Test viewing specific line range."""
        result = self.command.execute(
            absolute_path=self.test_files[0],
            start_line=1,
            end_line=3
        )
        
        self.assertEqual(result['status'], 'success')
        self.assertIn('Line 2', result['content'])
        self.assertIn('Line 3', result['content'])
        self.assertIn('Line 4', result['content'])
        self.assertNotIn('Line 1', result['content'])
        self.assertNotIn('Line 5', result['content'])
    
    def test_summary(self):
        """Test summary generation."""
        result = self.command.execute(
            absolute_path=self.test_files[0],
            start_line=2,
            end_line=3,
            include_summary=True
        )
        
        self.assertEqual(result['status'], 'success')
        self.assertIsNotNone(result['summary'])
        self.assertIsNotNone(result['summary']['before'])
        self.assertIsNotNone(result['summary']['after'])
        self.assertEqual(result['summary']['before']['line_count'], 2)
        self.assertEqual(result['summary']['after']['line_count'], 1)
    
    def test_no_summary(self):
        """Test viewing without summary."""
        result = self.command.execute(
            absolute_path=self.test_files[0],
            include_summary=False
        )
        
        self.assertEqual(result['status'], 'success')
        self.assertIsNone(result['summary'])
    
    def test_metadata(self):
        """Test file metadata."""
        result = self.command.execute(self.test_files[0])
        
        self.assertEqual(result['status'], 'success')
        self.assertIn('metadata', result)
        self.assertIn('size', result['metadata'])
        self.assertIn('modified', result['metadata'])
        self.assertIn('extension', result['metadata'])
        self.assertIn('is_binary', result['metadata'])
    
    def test_binary_detection(self):
        """Test binary file detection."""
        # Test text file
        result = self.command.execute(self.test_files[0])
        self.assertFalse(result['metadata']['is_binary'])
        
        # Test binary file
        result = self.command.execute(self.test_files[1])
        self.assertTrue(result['metadata']['is_binary'])
    
    def test_invalid_file(self):
        """Test error handling for invalid file."""
        result = self.command.execute("/nonexistent/file.txt")
        
        self.assertEqual(result['status'], 'error')
        self.assertIn('error', result)
    
    def test_invalid_line_range(self):
        """Test error handling for invalid line range."""
        # Test negative start line
        result = self.command.execute(
            absolute_path=self.test_files[0],
            start_line=-1
        )
        self.assertEqual(result['status'], 'error')
        
        # Test end line before start line
        result = self.command.execute(
            absolute_path=self.test_files[0],
            start_line=3,
            end_line=2
        )
        self.assertEqual(result['status'], 'error')
        
        # Test start line beyond file length
        result = self.command.execute(
            absolute_path=self.test_files[0],
            start_line=10
        )
        self.assertEqual(result['status'], 'error')
    
    def test_module_function(self):
        """Test the module-level function."""
        result = view_file(self.test_files[0])
        self.assertEqual(result['status'], 'success')

if __name__ == '__main__':
    unittest.main()
