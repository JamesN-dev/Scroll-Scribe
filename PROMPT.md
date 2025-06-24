# AI Agent Usage Guidelines for Python Projects

## Purpose

This document provides generic instructions for AI assistants, code review bots, or automated tools interacting with Python projects.

## Workflow

1. **Project Familiarization**

    - Before suggesting code, tests, or documentation updates, thoroughly read:
        - The main README or equivalent overview document.
        - All project documentation files (e.g., design docs, architecture).
        - Existing tests and test coverage.
        - Source code focusing on public APIs and critical logic.

2. **Testing and Validation**

    - Run the full test suite (`pytest`) to verify no regressions.
    - Do not add or modify tests unless explicitly requested.
    - Report any test failures or anomalies clearly.

3. **Code Suggestions**

    - Propose improvements or fixes that align with project style and conventions.
    - Avoid unnecessary changes; focus on clarity, correctness, and maintainability.
    - Use mocks for external dependencies when recommending tests.

4. **Documentation**

    - Recommend documentation updates where functionality changes or new features are added.
    - Maintain clear, concise, and accurate descriptions.

5. **Best Practices**
    - Follow language and framework best practices.
    - Use type hints and clear naming.
    - Write modular and reusable code.

---

Agents must prioritize understanding the project context before acting to ensure all suggestions are relevant and aligned with the project goals.
