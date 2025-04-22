# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build and Test Commands
- Install dependencies: `uv sync`
- Run the application: `uv run python -m ideasfactory`
- Run tests: `pytest`
- Run a single test: `pytest tests/test_file.py::test_function`
- Type checking: `mypy src/`
- Formatting: `black src/`
- Sort imports: `isort src/`

## Code Style Guidelines
- Imports: Group standard library, third-party, and local imports
- Types: Use Python type hints from the typing module
- Naming: snake_case for functions/variables, PascalCase for classes
- Error handling: Use `@handle_errors` or `@handle_async_errors` decorators
- Async: Prefer async/await for async operations
- Docstrings: Triple-quote docstrings with Args/Returns sections
- Use pydantic models for data validation and serialization
- Logging: Use the logging module with appropriate log levels
- Exception class: Extend from AppError for custom exceptions

## Project Architecture
- Agents: Business Analyst, Project Manager, Architect, etc. in `src/ideasfactory/agents/`
- Document Management: Session-specific document storage in `output/` directory
- UI: Textual-based TUI in `src/ideasfactory/ui/`
- Workflow: Session-based progression through agent stages
- Each agent produces markdown documents stored in their respective output folders
- Agent implementations follow singleton pattern with session management

## Session Management
- The `SessionManager` class in `utils/session_manager.py` is the single source of truth for all session-related operations
- Sessions are identified by a UUID and store project metadata and document paths
- Use `get_current_session()` and `set_current_session()` methods to manipulate the active session
- All UI screens and agents should retrieve session information only through the SessionManager
- Document paths should be added to sessions using `add_document()`
- Session-specific files are stored in `output/session-{session_id}/` directories
- Implementation follows incremental stages: first one agent, then the next, using shared document review