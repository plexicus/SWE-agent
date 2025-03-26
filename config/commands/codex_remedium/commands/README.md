# Codex Remedium Commands

This directory contains the implementation of individual Codex Remedium commands. Each command follows a standardized structure and provides specific functionality for code analysis and manipulation.

## Available Commands

### Codebase Search
Advanced code search functionality with context awareness and code structure detection.
```python
result = codebase_search(
    query="search_term",
    target_directories=["/path"]
)
```

### Find
File and directory search with advanced filtering options.
```python
result = find(
    search_directory="/path",
    pattern="*.py",
    extensions=["py"],
    excludes=["venv"],
    max_depth=3,
    type_filter="file",
    full_path=False
)
```

### Grep Search
Text-based search within files.
```python
result = grep_search(
    query="pattern",
    includes=["*.txt"],
    case_insensitive=True,
    match_per_line=True
)
```

### List Directory
Directory content listing with metadata.
```python
result = list_dir(
    directory_path="/path"
)
```

### Run Command
Safe command execution with validation.
```python
result = run_command(
    command_line="ls",
    cwd="/path",
    blocking=True,
    timeout=30
)
```

### View Code Item
View specific code items like functions or classes.
```python
result = view_code_item(
    file_path="/path/file.py",
    node_path="Class.method"
)
```

### View File
File content viewer with line range support.
```python
result = view_file(
    absolute_path="/path/file.txt",
    start_line=0,
    end_line=10,
    include_summary=True
)
```

### Write File
Safe file writing functionality.
```python
result = write_file(
    target_file="/path/file.txt",
    content="data",
    empty_file=False
)
```

## Command Structure

Each command follows this standard structure:

1. **Class-based Implementation**
   - Inherits from `BaseCommand`
   - Implements `execute` method
   - Provides command-specific helper methods

2. **Input Validation**
   - Parameter type checking
   - Value range validation
   - Security checks

3. **Error Handling**
   - Comprehensive exception handling
   - Detailed error messages
   - Logging of errors

4. **Return Format**
```python
{
    'status': 'success' | 'error',
    'error': str,  # Only present if status is 'error'
    ... # Command-specific data
}
```

## Security Features

All commands implement security measures:

1. **Path Validation**
   - Absolute path verification
   - Directory traversal prevention
   - Suspicious path detection

2. **Input Sanitization**
   - Command injection prevention
   - Shell metacharacter filtering
   - Unicode handling

3. **Resource Protection**
   - File access controls
   - Resource limit checks
   - Timeout mechanisms

## Testing

Each command includes comprehensive tests:

```bash
# Run all command tests
pytest tests/codex_remedium/test_commands/

# Run specific command test
pytest tests/codex_remedium/test_commands/test_[command].py
```

Test coverage includes:
- Basic functionality
- Edge cases
- Error conditions
- Security checks

## Error Handling

Commands use a standardized error handling approach:

1. **Validation Errors**
   - Invalid parameters
   - Missing dependencies
   - Security violations

2. **Runtime Errors**
   - File system errors
   - Permission issues
   - Resource constraints

3. **Security Errors**
   - Access violations
   - Injection attempts
   - Resource exhaustion

## Performance Considerations

Commands are optimized for:
- Memory efficiency
- CPU utilization
- I/O operations
- Large file handling

## Contributing

When adding new commands:

1. Create command class inheriting from `BaseCommand`
2. Implement required validation
3. Add comprehensive tests
4. Update documentation
5. Ensure CI/CD passes

## Dependencies

- Python 3.8+
- pathlib
- subprocess
- Command-specific tools (e.g., ripgrep, fd)
