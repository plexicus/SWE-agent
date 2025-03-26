#!/usr/bin/env python3
import unittest
import os
import tempfile
from pathlib import Path
from config.commands.codex_remedium.commands.write_file import WriteFileCommand, write_file

class TestWriteFile(unittest.TestCase):
    def setUp(self):
        """Set up test environment."""
        self.command = WriteFileCommand()
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test environment."""
        # Remove all test files
        for root, dirs, files in os.walk(self.temp_dir):
            for file in files:
                os.remove(os.path.join(root, file))
            for dir in dirs:
                os.rmdir(os.path.join(root, dir))
        if os.path.exists(self.temp_dir):
            os.rmdir(self.temp_dir)
    
    def test_basic_write(self):
        """Test basic file writing."""
        target_file = os.path.join(self.temp_dir, "test.txt")
        content = "Test content"
        
        result = self.command.execute(
            target_file=target_file,
            content=content
        )
        
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['file'], target_file)
        self.assertEqual(result['size'], len(content))
        self.assertFalse(result['empty'])
        
        # Verify file contents
        with open(target_file, 'r') as f:
            self.assertEqual(f.read(), content)
    
    def test_empty_file(self):
        """Test creating empty file."""
        target_file = os.path.join(self.temp_dir, "empty.txt")
        
        result = self.command.execute(
            target_file=target_file,
            empty_file=True
        )
        
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['size'], 0)
        self.assertTrue(result['empty'])
        self.assertTrue(os.path.exists(target_file))
    
    def test_create_directories(self):
        """Test creating parent directories."""
        target_file = os.path.join(self.temp_dir, "subdir1", "subdir2", "test.txt")
        content = "Test content"
        
        result = self.command.execute(
            target_file=target_file,
            content=content
        )
        
        self.assertEqual(result['status'], 'success')
        self.assertTrue(os.path.exists(target_file))
        self.assertTrue(os.path.isdir(os.path.dirname(target_file)))
    
    def test_file_exists(self):
        """Test error when file already exists."""
        target_file = os.path.join(self.temp_dir, "existing.txt")
        
        # Create file
        with open(target_file, 'w') as f:
            f.write("Existing content")
        
        # Try to write to it
        result = self.command.execute(
            target_file=target_file,
            content="New content"
        )
        
        self.assertEqual(result['status'], 'error')
        self.assertIn('error', result)
    
    def test_invalid_arguments(self):
        """Test error handling for invalid arguments."""
        # Test empty target path
        result = self.command.execute(
            target_file="",
            content="test"
        )
        self.assertEqual(result['status'], 'error')
        
        # Test no content and not empty_file
        result = self.command.execute(
            target_file=os.path.join(self.temp_dir, "test.txt")
        )
        self.assertEqual(result['status'], 'error')
        
        # Test both content and empty_file
        result = self.command.execute(
            target_file=os.path.join(self.temp_dir, "test.txt"),
            content="test",
            empty_file=True
        )
        self.assertEqual(result['status'], 'error')
    
    def test_suspicious_paths(self):
        """Test rejection of suspicious paths."""
        suspicious_paths = [
            "/etc/test.txt",
            "/bin/test.txt",
            "/sbin/test.txt",
            "/dev/test.txt",
            "/proc/test.txt",
            "/sys/test.txt",
            "/tmp/test.txt",
            "~/test.txt",
            "../test.txt"
        ]
        
        for path in suspicious_paths:
            result = self.command.execute(
                target_file=path,
                content="test"
            )
            self.assertEqual(
                result['status'],
                'error',
                f"Should reject path: {path}"
            )
    
    def test_unicode_content(self):
        """Test writing Unicode content."""
        target_file = os.path.join(self.temp_dir, "unicode.txt")
        content = "Hello, 世界! 🌍"
        
        result = self.command.execute(
            target_file=target_file,
            content=content
        )
        
        self.assertEqual(result['status'], 'success')
        
        # Verify file contents
        with open(target_file, 'r', encoding='utf-8') as f:
            self.assertEqual(f.read(), content)
    
    def test_module_function(self):
        """Test the module-level function."""
        target_file = os.path.join(self.temp_dir, "module_test.txt")
        content = "Test content"
        
        result = write_file(
            target_file=target_file,
            content=content
        )
        
        self.assertEqual(result['status'], 'success')
        self.assertTrue(os.path.exists(target_file))

if __name__ == '__main__':
    unittest.main()
