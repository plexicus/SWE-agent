#!/usr/bin/env python3
import unittest
import os
import tempfile
from pathlib import Path
from config.commands.codex_remedium.commands.view_code_item import ViewCodeItemCommand, view_code_item

class TestViewCodeItem(unittest.TestCase):
    def setUp(self):
        """Set up test environment."""
        self.command = ViewCodeItemCommand()
        
        # Create temporary test file
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = self._create_test_file()
    
    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
        if os.path.exists(self.temp_dir):
            os.rmdir(self.temp_dir)
    
    def _create_test_file(self):
        """Create temporary test file with sample code."""
        file_path = os.path.join(self.temp_dir, "test_code.py")
        with open(file_path, "w") as f:
            f.write('''
import os
from pathlib import Path
import json

class TestClass:
    """Test class docstring."""
    
    def __init__(self):
        self.value = 42
    
    def test_method(self, arg):
        """Test method docstring."""
        return self.value + arg

def standalone_function(x, y):
    """Standalone function docstring."""
    return x + y

class NestedClass:
    class InnerClass:
        def inner_method(self):
            return "inner"
''')
        return file_path
    
    def test_view_class(self):
        """Test viewing a class definition."""
        result = self.command.execute(
            file_path=self.test_file,
            node_path="TestClass"
        )
        
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['type'], 'ClassDef')
        self.assertIn('TestClass', result['content'])
        self.assertIn('test_method', result['content'])
    
    def test_view_method(self):
        """Test viewing a method definition."""
        result = self.command.execute(
            file_path=self.test_file,
            node_path="TestClass.test_method"
        )
        
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['type'], 'FunctionDef')
        self.assertIn('test_method', result['content'])
        self.assertIn('docstring', result['content'])
    
    def test_view_function(self):
        """Test viewing a standalone function."""
        result = self.command.execute(
            file_path=self.test_file,
            node_path="standalone_function"
        )
        
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['type'], 'FunctionDef')
        self.assertIn('standalone_function', result['content'])
        self.assertIn('x + y', result['content'])
    
    def test_nested_class(self):
        """Test viewing a nested class."""
        result = self.command.execute(
            file_path=self.test_file,
            node_path="NestedClass.InnerClass"
        )
        
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['type'], 'ClassDef')
        self.assertIn('InnerClass', result['content'])
    
    def test_nested_method(self):
        """Test viewing a method in a nested class."""
        result = self.command.execute(
            file_path=self.test_file,
            node_path="NestedClass.InnerClass.inner_method"
        )
        
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['type'], 'FunctionDef')
        self.assertIn('inner_method', result['content'])
    
    def test_nonexistent_file(self):
        """Test error handling for nonexistent file."""
        result = self.command.execute(
            file_path="/nonexistent/file.py",
            node_path="TestClass"
        )
        
        self.assertEqual(result['status'], 'error')
        self.assertIn('error', result)
    
    def test_nonexistent_node(self):
        """Test error handling for nonexistent node."""
        result = self.command.execute(
            file_path=self.test_file,
            node_path="NonexistentClass"
        )
        
        self.assertEqual(result['status'], 'error')
        self.assertIn('error', result)
    
    def test_invalid_python(self):
        """Test error handling for invalid Python code."""
        invalid_file = os.path.join(self.temp_dir, "invalid.py")
        with open(invalid_file, "w") as f:
            f.write("this is not valid python code")
        
        try:
            result = self.command.execute(
                file_path=invalid_file,
                node_path="SomeClass"
            )
            
            self.assertEqual(result['status'], 'error')
            self.assertIn('error', result)
        finally:
            os.remove(invalid_file)
    
    def test_imports_tracking(self):
        """Test that required imports are tracked."""
        result = self.command.execute(
            file_path=self.test_file,
            node_path="TestClass"
        )
        
        self.assertEqual(result['status'], 'success')
        self.assertIsInstance(result['imports'], list)
        self.assertTrue(any('import os' in imp for imp in result['imports']))
        self.assertTrue(any('pathlib' in imp for imp in result['imports']))
    
    def test_module_function(self):
        """Test the module-level function."""
        result = view_code_item(
            file_path=self.test_file,
            node_path="TestClass"
        )
        self.assertEqual(result['status'], 'success')

if __name__ == '__main__':
    unittest.main()
