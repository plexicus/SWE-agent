# Codex Remedium Commands

This directory contains the implementation of Codex Remedium commands and their supporting infrastructure.

## Directory Structure

```
codex_remedium/
├── core/              # Core functionality
│   └── base_command.py    # Base command class
├── utils/             # Common utilities
│   └── logging_utils.py   # Logging setup
├── validators/        # Input validation
│   └── input_validator.py # Validation functions
├── processors/        # Data processors
│   ├── history_processor.py  # Command history processing
│   └── output_parser.py      # Command output parsing
├── commands/          # Individual commands
│   ├── codebase_search.py  # Code search functionality
│   ├── find.py            # File finding utility
│   ├── grep_search.py     # Text search functionality
│   ├── list_dir.py        # Directory listing
│   ├── run_command.py     # Command execution
│   ├── view_code_item.py  # Code item viewer
│   ├── view_file.py       # File viewer
│   └── write_file.py      # File writer
└── logs/             # Log files (auto-generated)
```

## Commands

### Codebase Search
Advanced code search functionality with context awareness and code structure detection.
```python
result = codebase_search(query="search_term", target_directories=["/path"])
```

### Find
File and directory search with advanced filtering options.
```python
result = find(search_directory="/path", pattern="*.py", type="file")
```

### Grep Search
Text-based search within files.
```python
result = grep_search(query="pattern", includes=["*.txt"])
```

### List Directory
Directory content listing with metadata.
```python
result = list_dir(directory_path="/path")
```

### Run Command
Safe command execution with validation.
```python
result = run_command(command_line="ls", cwd="/path")
```

### View Code Item
View specific code items like functions or classes.
```python
result = view_code_item(file_path="/path/file.py", node_path="Class.method")
```

### View File
File content viewer with line range support.
```python
result = view_file(absolute_path="/path/file.txt", start_line=0, end_line=10)
```

### Write File
Safe file writing functionality.
```python
result = write_file(target_file="/path/file.txt", content="data")
```

## Testing

All commands include comprehensive unit tests located in `tests/codex_remedium/`.
Run tests with:
```bash
pytest tests/codex_remedium
```

## CI/CD

Continuous integration is configured in `.github/workflows/codex_remedium.yml` and includes:
- Unit testing
- Type checking
- Code linting
- Coverage reporting

## Error Handling

All commands follow a standardized error handling approach:
1. Input validation through validators
2. Exception handling with logging
3. Structured error responses

## Logging

Centralized logging system:
- Each command has its own log file
- Configurable log levels
- Comprehensive error tracking

## Contributing

When adding new commands:
1. Create command class inheriting from BaseCommand
2. Implement required validation
3. Add comprehensive tests
4. Update documentation
5. Ensure CI/CD passes

## Components

### Core

The `core` directory contains fundamental functionality used by all commands:
- `base_command.py`: Abstract base class for all commands, providing common functionality

### Utils

The `utils` directory contains shared utilities:
- `logging_utils.py`: Centralized logging configuration

### Validators

The `validators` directory contains input validation logic:
- `input_validator.py`: Input validation for all commands

### Processors

The `processors` directory contains data processing components:
- `history_processor.py`: Processes command history for context preservation
- `output_parser.py`: Parses and structures command outputs

### Commands

The `commands` directory contains individual command implementations:
- Each command follows the base command structure
- Commands include proper error handling and logging
- All commands are documented with docstrings

## Usage

Each command can be used either:
1. As a standalone script:
   ```bash
   python commands/grep_search.py '{"query": "example"}'
   ```

2. As a module:
   ```python
   from commands.grep_search import grep_search
   result = grep_search(query="example")
   ```

## Testing

Tests for each component are located in the corresponding test directory:
```
tests/
└── codex_remedium/
    ├── test_commands/
    ├── test_validators/
    └── test_processors/
```

## Logging

Logs are automatically generated in the `logs` directory:
- Each command has its own log file
- Log level can be configured in `logging_utils.py`
- Logs include timestamps and severity levels

## Error Handling

All commands use a standardized error handling approach:
1. Input validation through validators
2. Proper exception handling and logging
3. Structured error responses

## Contributing

When adding new commands:
1. Create a new file in the `commands` directory
2. Inherit from `BaseCommand`
3. Implement required validation in `input_validator.py`
4. Add appropriate tests
5. Update this documentation
