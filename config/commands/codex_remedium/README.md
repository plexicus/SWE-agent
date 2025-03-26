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
│   ├── grep_search.py
│   ├── view_file.py
│   └── ...
└── logs/             # Log files (auto-generated)
```

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
