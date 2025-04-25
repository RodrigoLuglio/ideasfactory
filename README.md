# IdeasFactory

IdeasFactory is an Agile AI-driven documentation tool for complex project development using specialized AI agents. It helps mature your ideas from brainstorming to complete implementation plans with detailed documentation.

## Overview

IdeasFactory transforms your abstract ideas into comprehensive implementation plans through a team of specialized AI agents. Each agent contributes to different phases of the project lifecycle:

1. **Business Analyst**: Conducts interactive brainstorming sessions to refine ideas
2. **Product Manager**: Creates comprehensive PRD based on vision document
3. **Architect (First Pass)**: Identifies technical aspects requiring research
4. **Research Team**: Conducts deep, multi-faceted research on technical options
5. **Architect (Final Pass)**: Defines technical architecture based on PRD and research
6. **Standards Engineer**: Identifies integration points and shared patterns
7. **Product Owner**: Breaks down the project into granular tasks
8. **Scrum Master**: Creates detailed self-contained Stories and Epics
9. **Developer**: Implements the project based on the Stories (not included in this tool)

The end result is a complete set of documentation and implementation plans that can be handed off to developers.

## Current Status

The project is under active development. Currently implemented:

- Business Analyst agent with complete brainstorming workflow
- Document management system with Git version control
- Basic terminal UI using Textual
- Product Manager agent for PRD creation with innovation-preserving capabilities
- Architect agent with two-phase approach:
  - First pass: Technical Research Requirements generation
  - Final pass: Architecture design and decision making
- Research-focused technical requirements that explore multiple paradigms
- Research Team agent with dimensional research capabilities:
  - Multi-dimensional research approach that explores interconnected research areas
  - Parallel research teams with Foundation, Branch, and Integration teams
  - Cross-paradigm opportunity identification across research dimensions
  - Comprehensive visualizations of research paths and dimension relationships
  - *Coming soon*: Enhanced specialized multi-agent research system (see docs/specialized-research-teams.md)
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

4. **Research Phase**:

   - The Research Team conducts dimensional research with parallel teams:
     - Foundation Team explores foundational architectural decisions
     - Branch Teams investigate specific dimensions across multiple paradigms
     - Integration Team analyzes how technologies work together across dimensions
   - Explores multiple implementation paths based on foundation choices
   - Identifies cross-paradigm opportunities that combine technologies from different domains
   - Presents comprehensive dimensional research report with visualizations

5. **Architecture Phase**:

   - The Architect creates a detailed architecture document
   - Make decisions about technologies and implementation approaches
   - Define component boundaries and integration points

6. **Standards Definition Phase** (Coming Soon):

   - Define coding standards and patterns with the Standards Engineer
   - Identify cross-cutting concerns and shared components
   - Create integration guidelines for independently implemented features

7. **Task Breakdown Phase** (Coming Soon):

   - Break down the project into granular tasks with the Product Owner
   - Create a complete, sequential list of implementation steps

8. **Stories and Epics Phase** (Coming Soon):
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
4. **Integration Focus**: Maintain cross-component integrity through explicit standards
5. **Self-Contained Implementation**: Each story should have everything needed for implementation
6. **AI-Friendly Documentation**: Create documentation that enables AI to implement features effectively
7. **Innovation Integrity**: Actively resist defaulting to mainstream solutions; maintain what makes each project unique

These principles ensure that as projects grow in complexity, they maintain architectural integrity while preserving the vision's innovative elements. By encouraging exploration across multiple paradigms and challenging conventional assumptions, IdeasFactory helps discover truly innovative solutions tailored to each unique project.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
