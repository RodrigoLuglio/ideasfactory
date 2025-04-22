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

## Core Project Objective
The fundamental purpose of IdeasFactory is to produce truly self-contained packages for each project that include:
- Comprehensive stories and requirements that capture the project's unique essence
- Standards and patterns documents that apply specifically to that project
- Architecture documentation that addresses ALL features and requirements

This approach solves the biggest challenge of AI-driven development: maintaining organization and integration as implementation complexity grows. By creating complete, tailored documentation that preserves each project's distinctive character, we enable AI developers to implement functionality that remains fully integrated with the rest of the codebase even as the project scales.

## Project Vision
IdeasFactory aims to democratize software development by enabling anyone with a good idea to see their vision become reality with the help of AI. As an open source tool, it addresses the critical gap in current AI-driven development: maintaining coherence and integration in complex systems.

The transformative goal is to create self-contained, comprehensive story packages that can be implemented fully integrated with the rest of the codebase using only the information provided in each package. This will:

- Allow non-technical visionaries to bring their ideas to life without learning to code
- Enable small teams to build complex, integrated systems that would typically require much larger teams
- Free developers to focus on innovation rather than integration challenges
- Support open source communities with consistent, comprehensive documentation

By bridging the gap between creative conception and technical implementation, IdeasFactory can fundamentally change the current AI-driven development landscape, making software creation more accessible while maintaining the architectural integrity essential for successful projects.

## Session Management
- The `SessionManager` class in `utils/session_manager.py` is the single source of truth for all session-related operations
- Sessions are identified by a UUID and store project metadata and document paths
- Use `get_current_session()` and `set_current_session()` methods to manipulate the active session
- All UI screens and agents should retrieve session information only through the SessionManager
- Document paths should be added to sessions using `add_document()`
- Session-specific files are stored in `output/session-{session_id}/` directories
- Implementation follows incremental stages: first one agent, then the next, using shared document review