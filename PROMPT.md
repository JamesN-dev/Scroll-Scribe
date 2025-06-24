Scroll-Scribe/PROMPT.md
```
# Agent Prompt and Project Comprehension Guidelines

## Purpose

This file provides instructions for all agents (AI assistants, code review bots, and automated tools) working on the Scroll-Scribe project. Its goal is to ensure that agents fully understand the project's purpose, features, workflows, and critical logic before performing any actions related to testing, code suggestions, or documentation.

---

## Agent Instructions

1. **Project Familiarization**
   - Before running tests, suggesting new tests, or making recommendations, agents must carefully read and understand the following:
     - The `README.md` file for a high-level overview and main features.
     - All documentation files in the `docs/` directory (including but not limited to `ARCHITECTURE.md`, `Phase2.md`, `LOGGING.md`) for detailed design, workflows, and requirements.
     - The source code, focusing on public functions, classes, and main modules, to understand implementation details and critical logic.

2. **Testing Workflow**
   - Agents should **not** generate new tests unless specifically requested.
   - Agents must recognize that a comprehensive suite of tests already exists in the `tests/` directory.
   - Agents are expected to run the full test suite (`pytest`) as part of their workflow.
   - If any tests fail or unexpected issues arise, agents must alert the developer in charge for review and **not** attempt to auto-fix unless explicitly instructed.

3. **Analysis and Suggestions**
   - If requirements appear unclear or test coverage seems insufficient, agents may suggest additional tests or clarifications, but should not implement them unless asked.
   - All suggestions or analysis should be based on a thorough understanding of the project's documentation and codebase.

4. **Best Practices**
   - Follow all code style and error handling conventions as outlined in `AGENTS.md` and other project documentation.
   - Use parameterized and integration tests where appropriate, and employ mocks for external dependencies if suggesting new tests.

---

## Summary

**Agents must always prioritize understanding the Scroll-Scribe project’s goals, architecture, and workflows before taking action.** This ensures that all testing, analysis, and recommendations are relevant, accurate, and aligned with the project's needs.

For further details on code style, error handling, and test execution, refer to `AGENTS.md`.
