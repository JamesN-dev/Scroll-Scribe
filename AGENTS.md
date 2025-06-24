# Agent Guidelines for Python Projects

This document provides general instructions and best practices for AI agents, code review bots, or automated tools working on Python projects.

## Commands

- Run linting: `ruff check .`
- Run type checking: `basedpyright app/`
- Run tests: `pytest`
- Run a single test: `pytest path/to/test_file.py::test_name`
- Run tests with coverage: `pytest --cov=your_package tests/`

## Code Style

- Use Python type hints consistently.
- Follow PEP 8 naming conventions (snake_case for functions/variables, PascalCase for classes).
- Write clear docstrings for all public functions and classes.
- Prefer f-strings for string formatting.
- Use structured error handling with custom exceptions where appropriate.
- For I/O or long-running operations, use async/await.
- Keep imports clean and organized (group standard, third-party, and local).
- Use relative imports inside packages when appropriate.
- Maintain readable, maintainable code with clear function/class boundaries.

## Testing

- Ensure comprehensive unit and integration test coverage.
- Use mocks and fixtures for external dependencies.
- Follow consistent test naming and structure.
- Keep tests isolated and deterministic.

## Logging & Output

- Use consistent logging conventions with appropriate log levels.
- Prefer reusable logging utilities or libraries.
- Keep console output clean and user-friendly.

---

Agents should always run the full test suite and static analysis before making suggestions or changes.
