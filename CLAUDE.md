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
- Workflow: Session-based progression through agent stages (see Improved Workflow below)
- Each agent produces markdown documents stored in their respective output folders
- Agent implementations follow singleton pattern with session management

## Improved Workflow
The project follows a refined workflow to create truly self-contained story packages:

1. **Vision Creation** (Business Analyst): Captures core concept and unique value proposition
2. **Detailed Requirements** (Product Manager): Expands vision into comprehensive PRD
3. **Technical Research Requirements** (Architect - First Pass): Analysis of what needs investigation
4. **Foundation Research** (Research Team - First Pass): Explores implementation possibilities through foundational paradigm-based approach
5. **Foundation Selection** (Architect - Second Pass): Selection of foundational architectural approach and creation of generic architecture document
6. **Technology Research** (Research Team - Second Pass): Explores specific technologies and tech stacks for implementing the selected foundation
7. **Technology Selection & Architecture Design** (Architect - Third Pass): Selection of specific technologies and creation of complete architecture document
8. **Standards and Patterns** (Standards Engineer): Defines integration points and shared components
9. **Task List Creation** (Product Owner): Breaks down implementation into granular tasks
10. **Story Creation** (Scrum Master): Packages tasks into self-contained stories with integration

This workflow ensures all implicit requirements are captured, avoids imposing conventional patterns on innovative ideas, and maintains integration integrity across components. The three-phase approach to architecture (research requirements → foundation selection → technology selection) ensures that architectural decisions are made with progressively deeper levels of information while maintaining flexibility until the appropriate decision point.

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

## Agent Roles and Responsibilities
Each agent has a specific role in the workflow:

1. **Business Analyst**: Conducts brainstorming to create vision document
2. **Product Manager**: Creates PRD focusing on comprehensive requirements while preserving uniqueness
3. **Architect**: Three-phase approach:
   - First Pass: Identifying research needs and creating research requirements
   - Second Pass: Foundation selection and creation of generic architecture document
   - Third Pass: Technology selection and creation of complete architecture document
4. **Research Team**: Two-phase research approach:
   - First Pass: Foundation Research - exploring foundational architectural approaches
   - Second Pass: Technology Research - exploring specific technologies based on selected foundation
   - Both passes use dimensional research with parallel teams (Foundation, Branch, Integration)
5. **Standards Engineer**: Identifies integration points and creates cross-cutting standards
6. **Product Owner**: Creates task list with granular implementation steps
7. **Scrum Master**: Creates self-contained stories that maintain integration

## Important Notes for Future Development
1. Remember that session models need to be properly used for tracking decisions and document creation
2. Always extract structured data from documents (features, requirements, decisions) for later use
3. Ensure each agent preserves project uniqueness rather than imposing conventional patterns
4. Focus on integration points between components to ensure system-level cohesion
5. Keep stories self-contained while maintaining cross-component integration
6. For the Research Team, implement the specialized multi-agent approach described in docs/specialized-research-teams.md

## Key Implementation Details To Remember
1. **Session Model Structure**: Each agent has a dedicated session model in their respective file (PRDSession, ArchitectureSession, etc.)
   - Use the `metadata` field to store important context and decisions
   - Define model classes with clear Pydantic field descriptions

2. **Document Flow**:
   - Vision Document → PRD → Architecture Research Requirements → Foundation Research Report → 
     Generic Architecture Document → Technology Research Report → Complete Architecture Document
   - Each document builds on the previous one and contributes to the next
   - Extract and preserve structured data when passing between stages

3. **UI Integration**:
   - Each agent has a corresponding screen in `src/ideasfactory/ui/screens/`
   - Screen names should match their purpose (e.g., `prd_creation_screen.py`)
   - Use `set_session()` on all screens to maintain session context
   
4. **Document Generation Patterns**:
   - Complex documents use multi-step generation with intermediate extraction
   - For example: analyze vision → extract features → create PRD → extract requirements
   - Store extracted data in session models for reference by later steps

5. **Prompting Strategy**:
   - Start with a clear system prompt that defines agent role and personality
   - Use specific creation prompts focused on current document/task
   - Include extracted data from previous steps in prompts
   - Emphasize preserving project uniqueness in all prompts
   
   - For the Architect's first pass (research requirements):
     * Establish a multi-level research framework with foundations first
     * Identify interdependency relationships between research areas
     * Direct exploration across the full spectrum of options for each research area:
       - Established approaches (traditional, proven methodologies)
       - Mainstream current (contemporary popular solutions) 
       - Cutting-edge (emerging technologies gaining traction)
       - Experimental (research-stage approaches)
       - Cross-paradigm (combinations of technologies from different domains)
       - First-principles (custom approaches designed specifically for the project)
     * Make it clear that while the Architect avoids naming specific technologies, the Research Team MUST identify specific implementation options
     * Create a framework that shows how foundational choices create different paths for feature implementation
   
   - For the Research Team's first pass (foundation research):
     * Use parallel teams approach with Foundation, Branch, and Integration teams
     * Foundation team explores foundational architectural decisions
     * Branch teams investigate specific dimensions across multiple paradigms
     * Integration team analyzes cross-dimensional compatibility and integration
     * Identify dependencies between dimensions to map implementation paths
     * Discover cross-paradigm opportunities that combine technologies from different domains
     * Create visualizations showing dimension relationships and research paths
     * Produce comprehensive foundation options for the Architect's consideration
   
   - For the Architect's second pass (foundation selection):
     * Extract foundation options from research results
     * Present options in a user-friendly format for selection
     * Support interactive exploration of foundation details
     * Guide user-defined foundation creation when preferred
     * Create a technology-neutral generic architecture document based on selected foundation
     * Ensure the generic architecture preserves the project's unique vision
     * Provide clear structure for the second research phase
   
   - For the Research Team's second pass (technology research):
     * Apply the same dimensional research methodology to technology exploration
     * Use the generic architecture document as the primary research framework
     * Explore the full spectrum of technologies for implementing the selected foundation
     * Maintain parallel teams approach focused on technology dimensions
     * Identify viable implementation paths using different technology combinations
     * Evaluate technologies based on project-specific criteria, not industry popularity
     * Document technology options comprehensively for the Architect's consideration
   
   - For the Architect's third pass (technology selection):
     * Analyze technology research without preconceptions
     * Make technology selections based on project-specific needs, not conventional patterns
     * Create a complete architecture document that is uniquely tailored to the project
     * Structure the document in whatever way best serves this particular project
     * Avoid imposing industry-standard patterns or approaches that don't fit the project
     * Preserve the project's unique vision throughout the architecture
   
   - Throughout all phases:
     * Include assumption-challenging questions that push beyond conventional thinking
     * Avoid biasing toward mainstream solutions; maintain innovation integrity
     * Clearly separate responsibilities between agents
     * Ensure each document preserves and enhances the project's unique character
     * Resist defaulting to standard patterns or approaches

6. **Implementation Organization**:
   - `src/ideasfactory/agents/` - Agent implementations
   - `src/ideasfactory/ui/screens/` - TUI screens for each agent
   - `src/ideasfactory/utils/` - Shared utilities including session management
   - `src/ideasfactory/tools/` - Tools for web search, data analysis, etc.
   - `docs/` - Documentation including workflow and implementation guides