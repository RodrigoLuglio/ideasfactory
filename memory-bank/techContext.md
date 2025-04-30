# IdeasFactory Technical Context

## Technology Stack

### Backend Framework

- **Language**: Python 3.8+
- **Package Management**: UV (fast alternative to pip)
- **Dependency Format**: pyproject.toml
- **Environment Management**: Native Python virtual environments

### LLM Integration

- **LLM Abstraction**: LiteLLM for provider-agnostic interactions
- **Supported Providers**:
  - OpenAI (GPT-4, GPT-3.5 Turbo)
  - Anthropic (Claude Opus, Claude Sonnet)
  - Potentially other providers through LiteLLM

### User Interface

- **UI Framework**: Textual (TUI - Terminal User Interface)
- **Design Approach**: Screen-based navigation with consistent layout
- **Components**: Custom widgets for document display and interaction
- **Interaction Model**: Keyboard-driven with shortcut support
- **Decision Interfaces**: Specialized screens for collaborative decision-making with dual-path options

### Document Management

- **Format**: Markdown with YAML frontmatter
- **Metadata Handling**: python-frontmatter library
- **Version Control**: Git-based tracking
- **Storage**: File-system based organization by session and document type
- **Multi-Phase Organization**: Documents organized by research and decision phases

### Decision Support

- **Criteria Framework**: Weighted evaluation criteria for objective decision-making
- **Path Selection**: Support for both research-driven and user-defined foundation paths
- **Decision Documentation**: Structured templates for capturing reasoning and considerations
- **Visualization**: Comparative displays for option evaluation

### Data Validation

- **Validation Framework**: Pydantic models
- **Schema Definition**: Strong typing with field validation
- **Data Extraction**: Structured parser for document content
- **Decision Capture**: Structured models for recording decision points and rationales

## Development Environment

### Requirements

- Python 3.8+
- Git
- UV package manager
- LLM API access (OpenAI, Anthropic, etc.)

### Setup Process

1. Clone repository: `git clone https://github.com/rodrigoluglio/ideasfactory.git`
2. Navigate to directory: `cd ideasfactory`
3. Install dependencies: `uv sync`
4. Configure environment: Create `.env` file with API keys
5. Run application: `uv run python -m ideasfactory`

### API Configurations

- API keys stored in `.env` file (not committed to version control)
- Google Custom Search configuration for research capabilities
- LLM provider API keys and configuration parameters

## Project Structure

### Directory Organization

```
ideasfactory/
├── docs/                # Documentation
├── output/              # Generated documents
│   ├── session-{id}/    # Session-specific outputs
│   ├── project-vision/  # Vision documents
│   ├── prd/             # Product Requirements Documents
│   ├── research-requirements/ # Technical research requirements
│   ├── research-report/ # Foundation research reports
│   │   └── foundation-path-reports/ # Individual implementation path reports
│   ├── architecture/    # Architecture documents (generic and final)
│   ├── tech-research/   # Technology stack research (planned)
│   ├── standards-patterns/ # Standards and patterns documents
│   ├── task-list/       # Task breakdown lists
│   └── epics-stories/   # Epics and stories organization
├── src/
│   └── ideasfactory/
│       ├── agents/      # Agent implementations
│       │   ├── business_analyst.py
│       │   ├── product_manager.py
│       │   ├── architect.py
│       │   ├── research_team.py
│       │   ├── standards_engineer.py
│       │   ├── product_owner.py
│       │   └── scrum_master.py
│       ├── decision/    # Decision support framework (new)
│       │   ├── criteria.py
│       │   ├── foundation_decision.py
│       │   └── tech_decision.py
│       ├── documents/   # Document models and generators
│       ├── tools/       # Utilities like web search
│       ├── ui/          # Textual UI components
│       │   ├── screens/ # UI screens for each workflow stage
│       │   └── widgets/ # Reusable UI components
│       └── utils/       # Shared utility functions
└── tests/               # Test suite
```

### Key Files

- `src/ideasfactory/__init__.py`: Main application entry point
- `src/ideasfactory/utils/session_manager.py`: Session management
- `src/ideasfactory/agents/architect.py`: Multi-pass architect implementation
- `src/ideasfactory/decision/criteria.py`: Weighted criteria framework
- `.env.example`: Template for environment variables
- `pyproject.toml`: Project dependencies and configuration

## Integration Points

### Decision Framework Integration

- Weighted criteria evaluation for foundation path selection
- Dual-path workflow supporting research-driven or user-defined choices
- Decision documentation with structured reasoning capture
- Session metadata storage for decision context

### LLM Integration

- LiteLLM for abstracting LLM provider differences
- Custom prompt engineering for each agent role
- Specialized prompts for collaborative decision sessions
- Structured response parsing tailored to document types

### Web Search Integration

- Google Custom Search for research capabilities
- Structured search strategies for different research phases
- Result parsing and integration into documents
- Specialized search patterns for foundation vs. technology research

### File System Integration

- Document persistence using structured organization
- Session tracking with UUID-based directories
- Git-based version tracking of output documents
- Phase-specific document organization

## Technical Constraints

### Performance Considerations

- LLM requests have latency implications
- Multi-phase research increases total token usage
- Decision interfaces need responsive user experience
- Batch processing for multi-agent simulations
- Research phases can be time and token-intensive

### Scalability Aspects

- Session isolation enables multi-project support
- Document versioning for tracking changes
- Modular design allows for agent substitution or enhancement
- Decision path flexibility accommodates different user needs

### Security Considerations

- API keys stored in local environment variables
- No remote data storage (all files local)
- Clear data flow with no unexpected external connections
- User decisions stored only in local session data

## Development Practices

### Testing Approach

- Unit tests for core functionality
- Integration tests for agent interactions
- Decision path testing for dual-path options
- Document validation testing

### Error Handling

- Custom error classes extended from base AppError
- Decorators for consistent error handling
- Graceful degradation for non-critical failures
- Decision validation to prevent inconsistent states

### Logging Strategy

- Hierarchical logging with appropriate levels
- Session-specific log contexts
- Decision event logging for troubleshooting
- Diagnostic information for debugging

## Tool Usage Patterns

### LLM Interaction Patterns

- System prompt defines agent role and capabilities
- Creation prompts focus on specific document generation
- Decision prompts enable collaborative interaction
- Extraction prompts pull structured data from documents
- Multi-step generation for complex documents
- Explicit boundary enforcement to maintain scope

### Document Generation Patterns

- Template-based generation for consistent structure
- Hierarchical assembly of complex documents
- Extraction-transformation for maintaining cross-document references
- Phase-specific document formats for foundation vs. technology architecture

### Decision Support Patterns

- Criteria-based evaluation for objective decision-making
- Dual-path interfaces supporting different user knowledge levels
- Structured reasoning capture for decision documentation
- Path convergence ensuring consistent outputs regardless of chosen path

### Web Research Patterns

- Phase-specific research approaches (foundation vs. technology)
- Multi-query strategies for comprehensive coverage
- Dimension-specific search approaches
- Result synthesis across multiple sources

## Deployment Considerations

### Distribution

- Currently local installation only
- Potential for pip/conda packaging
- Docker containerization possible for consistent environments

### Environment Requirements

- Python runtime (3.8+)
- Access to LLM APIs (API keys required)
- Terminal with Unicode support for TUI
- Git for version control features

### Configuration Management

- Environment variables for sensitive settings
- Configuration files for user preferences
- Session-specific settings stored in metadata
- Decision framework configuration options
