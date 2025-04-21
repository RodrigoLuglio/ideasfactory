# IdeasFactory

IdeasFactory is an Agile AI-driven documentation tool for complex project development using specialized AI agents. It helps mature your ideas from brainstorming to complete implementation plans with detailed documentation.

## Overview

IdeasFactory transforms your abstract ideas into comprehensive implementation plans through a team of specialized AI agents. Each agent contributes to different phases of the project lifecycle:

1. **Business Analyst**: Conducts interactive brainstorming sessions to refine ideas
2. **Project Manager**: Performs deep research on the project vision
3. **Architect**: Defines the technical architecture and structure
4. **Product Owner**: Breaks down the project into granular tasks
5. **Standards Engineer**: Defines coding standards and patterns
6. **Scrum Master**: Creates detailed Stories and Epics
7. **Developer**: Implements the project based on the Stories (not included in this tool)

The end result is a complete set of documentation and implementation plans that can be handed off to developers.

## Current Status

The project is under active development. Currently implemented:

- Business Analyst agent with complete brainstorming workflow
- Document management system with Git version control
- Basic terminal UI using Textual
- Project Manager agent for research (in progress)

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

### Setting up Google Custom Search for the Project Manager

The Project Manager agent relies on web search capabilities. To enable this feature:

1. Create a Google Cloud project at [Google Cloud Console](https://console.cloud.google.com/)
2. Enable the Custom Search API
3. Create API credentials
4. Set up a Custom Search Engine at [Google Programmable Search Engine](https://programmablesearchengine.google.com/)
5. Add your API key and Search Engine ID to the `.env` file

## Usage

Start the application with:

```bash
uv run python -m ideasfactory
```

### Workflow

1. **Brainstorming Phase**:

   - Enter your initial idea and start a brainstorming session
   - Interact with the Business Analyst agent to refine your idea
   - Review and revise the generated vision document

2. **Research Phase**:

   - The Project Manager agent conducts research on your project vision
   - Review and revise the research report

3. **Architecture Phase** (Coming Soon):

   - Define the technical architecture with the Architect agent
   - Make decisions about technologies and implementation approaches

4. **Task Breakdown Phase** (Coming Soon):

   - Break down the project into granular tasks with the Product Owner
   - Review the task list

5. **Standards Definition Phase** (Coming Soon):

   - Define coding standards and patterns with the Standards Engineer
   - Ensure consistency across implementation

6. **Stories and Epics Phase** (Coming Soon):
   - Create detailed user stories grouped by epics
   - Ensure each story is self-contained and implementable

## Tech Stack

- **Language**: Python
- **UI Framework**: Textual (terminal-based UI)
- **LLM Integration**: LiteLLM (abstraction for multiple LLM providers)
- **Document Management**: python-frontmatter with Git version control
- **Project Management**: uv (dependency management)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
