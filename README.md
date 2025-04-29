# IdeasFactory

IdeasFactory is an Agile AI-driven documentation tool for complex project development using specialized AI agents. It helps mature your ideas from brainstorming to complete implementation plans with detailed documentation.

## Overview

IdeasFactory transforms your abstract ideas into comprehensive implementation plans through a team of specialized AI agents. Each agent contributes to different phases of the project lifecycle:

1. **Business Analyst**: Conducts interactive brainstorming sessions to refine ideas
2. **Product Manager**: Creates comprehensive PRD based on vision document
3. **Architect (First Pass)**: Identifies technical aspects requiring research
4. **Research Team (First Pass)**: Conducts foundation-focused research on architectural approaches
5. **Architect (Second Pass)**: Selects foundation and creates generic architecture document
6. **Research Team (Second Pass)**: Explores technologies and tech stacks for the selected foundation
7. **Architect (Third Pass)**: Selects technologies and creates complete architecture document
8. **Standards Engineer**: Identifies integration points and shared patterns
9. **Product Owner**: Breaks down the project into granular tasks
10. **Scrum Master**: Creates detailed self-contained Stories and Epics
11. **Developer**: Implements the project based on the Stories (not included in this tool)

The end result is a complete set of documentation and implementation plans that can be handed off to developers.

## Current Status

The project is under active development. Currently implemented:

- Business Analyst agent with complete brainstorming workflow
- Document management system with Git version control
- Basic terminal UI using Textual
- Product Manager agent for PRD creation with innovation-preserving capabilities
- Architect agent with three-phase approach:
  - First pass: Technical Research Requirements generation
  - Second pass: Foundation selection and generic architecture document creation
  - Third pass: Technology selection and complete architecture document creation (coming soon)
- Research Team agent with two-phase dimensional research capabilities:
  - First pass: Multi-dimensional research on foundational architectural approaches
    - Parallel research teams with Foundation, Branch, and Integration teams
    - Cross-paradigm opportunity identification across research dimensions
    - Comprehensive visualizations of research paths and dimension relationships
  - Second pass: Technology-focused research building on selected foundation (coming soon)
- Foundation selection UI with interactive chat for exploring foundation options
- Session management for maintaining state across the workflow
- Document review screen that supports all document types in the workflow

## Installation

### Prerequisites

- Python 3.8+
- Git
- UV package manager (install from https://github.com/astral-sh/uv)
- LLM API access (OpenAI, Anthropic, etc.)

### Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/rodrigoluglio/ideasfactory.git
   cd ideasfactory
   ```

2. Install dependencies using UV:

   ```bash
   uv sync
   ```

3. Create a `.env` file based on the provided `.env.example`:

   ```bash
   cp .env.example .env
   ```

4. Edit the `.env` file with your API keys and configuration

### Setting up Google Custom Search for Web Research

The Research Team agent relies on web search capabilities. To enable this feature:

1. Create a Google Cloud project at [Google Cloud Console](https://console.cloud.google.com/)
2. Enable the Custom Search API
3. Create API credentials
4. Set up a Custom Search Engine at [Google Programmable Search Engine](https://programmablesearchengine.google.com/)
5. Add your API key and Search Engine ID to the `.env` file

See [docs/google-search-setup.md](docs/google-search-setup.md) for detailed instructions.

## Usage

Start the application with:

```bash
uv run python -m ideasfactory
```

### Workflow

1. **Vision Creation Phase**:

   - Enter your initial idea and start a brainstorming session
   - Interact with the Business Analyst agent to refine your idea
   - Review and revise the generated vision document

2. **Requirements Phase**:

   - The Product Manager agent creates a comprehensive PRD based on the vision
   - Review and revise the PRD to ensure it captures all requirements
   - Focus on preserving the unique character of your project vision

3. **Technical Research Requirements Phase**:

   - The Architect performs a first pass to create a multi-level research framework
   - Identifies ALL technical requirements needed for complete implementation
   - Establishes a clear research hierarchy with foundational elements first
   - Maps interdependencies showing how choices in one area affect options in others
   - Shows how foundational choices create different paths for feature implementation
   - Directs exploration across the full spectrum for each research area
   - Creates challenging questions that push beyond conventional thinking
   - Makes clear that while the Architect avoids naming specific technologies, the Research Team must identify and evaluate specific options

4. **Foundation Research Phase**:

   - The Research Team conducts first-pass dimensional research with parallel teams:
     - Foundation Team explores foundational architectural decisions
     - Branch Teams investigate specific dimensions across multiple paradigms
     - Integration Team analyzes how technologies work together across dimensions
   - Explores multiple implementation paths based on foundation choices
   - Identifies cross-paradigm opportunities that combine technologies from different domains
   - Presents comprehensive research report with foundation options and visualizations

5. **Foundation Selection Phase**:

   - Review foundation options identified in the research phase
   - Select a foundation approach or define a custom foundation
   - Engage with the Architect agent through interactive chat to refine foundation details
   - Generate a generic architecture document based on the selected foundation

6. **Technology Research Phase**:

   - The Research Team conducts second-pass dimensional research based on the selected foundation
   - Explores specific technologies and tech stacks for implementing each component
   - Evaluates technology options against project requirements and constraints
   - Presents comprehensive technology research report with implementation options

7. **Technology Selection & Architecture Phase**:

   - Review technology options identified in the second research phase
   - Select specific technologies for each component
   - Generate the complete architecture document with full implementation details

8. **Standards Definition Phase** (Coming Soon):

   - Define coding standards and patterns with the Standards Engineer
   - Identify cross-cutting concerns and shared components
   - Create integration guidelines for independently implemented features

9. **Task Breakdown Phase** (Coming Soon):

   - Break down the project into granular tasks with the Product Owner
   - Create a complete, sequential list of implementation steps

10. **Stories and Epics Phase** (Coming Soon):
    - Package tasks into detailed user stories grouped by epics
    - Ensure each story is self-contained yet maintains integration
    - Include all information needed for independent implementation

## Tech Stack

- **Language**: Python
- **UI Framework**: Textual (terminal-based UI)
- **LLM Integration**: LiteLLM (abstraction for multiple LLM providers)
- **Document Management**: python-frontmatter with Git version control
- **Project Management**: uv (dependency management)
- **Data Validation**: Pydantic for model validation and serialization
- **Session Management**: Custom UUID-based session tracking with metadata

## Project Philosophy

IdeasFactory is guided by these core principles:

1. **Preserve Uniqueness**: Never force innovative ideas into conventional patterns
2. **Comprehensive Requirements**: Capture both explicit and implicit needs
3. **Multi-Paradigm Exploration**: Direct research across the full spectrum of approaches from established to experimental
4. **Progressive Decision Making**: Make architectural decisions in layers, with increasing specificity as knowledge grows
5. **Integration Focus**: Maintain cross-component integrity through explicit standards
6. **Self-Contained Implementation**: Each story should have everything needed for implementation
7. **AI-Friendly Documentation**: Create documentation that enables AI to implement features effectively
8. **Innovation Integrity**: Actively resist defaulting to mainstream solutions; maintain what makes each project unique
9. **Project-Specific Documentation**: Structure all documentation in whatever way best serves the particular project
10. **Three-Phase Research and Architecture**: Use research-selection-research cycles to ensure fully informed decisions

These principles ensure that as projects grow in complexity, they maintain architectural integrity while preserving the vision's innovative elements. By encouraging exploration across multiple paradigms, challenging conventional assumptions, and making decisions progressively, IdeasFactory helps discover truly innovative solutions tailored to each unique project.

The three-phase approach to architecture (research requirements → foundation selection → technology selection) ensures that architectural decisions are made with progressively deeper levels of information while maintaining flexibility until the appropriate decision point.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
