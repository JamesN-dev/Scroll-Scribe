# Agent Guidelines for Scroll-Scribe

This file serves as:
1. Project-level instructions for Zed's built-in AI functionality (Agent Panel, inline assistant)
2. Guidelines for CLI-based AI agents (opencode, GitHub Copilot CLI, etc.)

## Commands
- Run linting: `ruff check .`
- Run type checking: `basedpyright .`
- Run tests: `pytest`
- Run single test: `pytest tests/test_processing.py::test_url_to_filename`
- Run tests with coverage: `pytest --cov=app tests/`

## Code Style
- Use Python type hints consistently
- Follow PEP 8 naming: snake_case for functions/variables, PascalCase for classes
- Structured error handling with custom exceptions in utils/exceptions.py
- Async/await for I/O operations
- Rich console output using CleanConsole class
- Docstrings required for all public functions/classes
- Relative imports within app package
- Use f-strings for string formatting
- Exception handling with custom exceptions (FileIOError, LLMError, ProcessingError)
- Logging via utils/logging.py with appropriate log levels

## IDE Integration
This file is automatically recognized by Zed's AI features (as AGENTS.md) and will be included in all interactions with:
- Zed's Agent Panel (@ai)
- Inline assistant
- Edit predictions
- Other AI features in Zed

The same guidelines also apply to CLI-based AI agents working with this codebase.