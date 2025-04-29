# IdeasFactory System Patterns

## System Architecture

### Overall Architecture

IdeasFactory follows a modular, agent-based architecture with clear separation of concerns:

1. **Core System Layer**:

   - Session Management: Handles project state across the entire workflow
   - Document Management: Stores and retrieves all project documents with version control
   - Agent Orchestration: Controls the workflow progression and agent interactions
   - UI Framework: Provides terminal-based user interface with dedicated screens

2. **Agent Layer**:

   - Specialized agent modules for each role in the workflow
   - Each agent has defined inputs, processing capabilities, and outputs
   - Agents maintain state within their specific session context

3. **Decision Layer** (New):

   - Collaborative decision interfaces with dual-path options
   - Decision support frameworks with weighted criteria
   - Decision documentation and reasoning capture
   - User choice facilitation at key decision points

4. **Tools and Resources Layer**:

   - Web search capabilities for research
   - File system interactions
   - Document parsing and generation
   - Visualization components

5. **Output Layer**:
   - Session-specific document organization
   - Developer package creation
   - Document versioning and tracking

### Data Flow

1. **Document Chain**: Each document builds on and references previous documents
2. **Multi-phase Research Flow**: Foundation research → Foundation decision → Technology research → Technology decision
3. **Dual-path Decisions**: User can choose research-driven or user-defined paths at decision points
4. **Session State**: Central session tracking ensures continuity across the workflow
5. **Extraction-Transformation-Loading**: Structured data extracted from documents feeds into subsequent stages
6. **Bi-directional User Interaction**: Each agent can engage in dialog with users for refinement

## Key Technical Decisions

### Agent Framework

- **Agent Implementation Pattern**: Each agent is implemented as a service class with stateless interactions but session-based state tracking
- **Agent Communication**: Agents communicate through structured document formats and session metadata
- **Agent Autonomy**: Each agent operates independently within its domain with clear boundaries
- **Three-Pass Architect**: Architect role split into three distinct passes with increasing specificity:
  - First Pass: Technical research requirements definition
  - Second Pass: Foundation decision and generic architecture
  - Third Pass: Technology stack decision and final architecture

### Research Framework

- **Two-Phase Research Approach**: Separate foundation path research from technology stack research
- **Foundation Path Research**: Explores architectural implementation paths at a high level
- **Technology Stack Research**: Focused exploration of specific technologies within the selected foundation
- **Decision Support Framework**: Weighted criteria evaluation for objective path selection
- **Dual-Path Options**: Support for both research-driven and user-defined decision paths

### Document Management

- **Markdown with Frontmatter**: All documents use markdown with YAML frontmatter for metadata
- **Git-based Versioning**: Document changes tracked using Git for version control
- **Structured Data Extraction**: Key information is extracted into structured formats for cross-referencing
- **Multi-Phase Documentation**: Clear separation between generic foundation architecture and final technology architecture

### Session Management

- **UUID-based Sessions**: Each project has a unique session identifier
- **Hierarchical Session Storage**: Files organized by session ID and document type
- **Session Metadata Tracking**: Key decisions and state stored in session metadata
- **Decision Context Persistence**: Reasoning and considerations captured for later reference

### UI Architecture

- **Textual Framework**: Terminal-based UI using the Textual library
- **Screen-based Navigation**: Each workflow step has a dedicated screen
- **Document Preview/Edit Cycle**: All screens follow a consistent preview/edit/approve pattern
- **Decision Interfaces**: Specialized interfaces for collaborative decision-making

## Design Patterns

### Singleton Pattern

- **SessionManager**: Single source of truth for all session-related operations
- **AgentManager**: Controls agent instantiation and access

### Strategy Pattern

- **LLM Provider Strategy**: Abstraction over multiple possible LLM providers
- **Document Generation Strategy**: Different strategies for different document types
- **Decision Path Strategy**: Different approaches for research-driven vs. user-defined paths

### Factory Pattern

- **Agent Factory**: Creates appropriate agent instances based on workflow stage
- **Document Factory**: Creates structured document instances of various types
- **Decision Interface Factory**: Creates appropriate decision interfaces based on context

### Observer Pattern

- **Document Change Notifications**: UI updates when documents change
- **Session State Updates**: Components react to session state changes
- **Decision Event Propagation**: System responds to user decisions across components

### Facade Pattern

- **API Facade**: Simplified interface to external services (search, LLM)
- **Document Facade**: Unified interface for document operations
- **Decision Framework Facade**: Simplified access to decision support capabilities

### Template Method Pattern

- **Base Agent Class**: Defines the template for agent operations with hooks for specialization
- **Document Generation Pipeline**: Standard steps with customizable processing
- **Decision Process Template**: Structured approach to collaborative decision-making

## Component Relationships

### Multi-phase Workflow Structure

```
                     ┌─────────────────┐
                     │ Business Analyst │
                     └────────┬────────┘
                              │
                              ▼
                     ┌─────────────────┐
                     │ Product Manager  │
                     └────────┬────────┘
                              │
                              ▼
                ┌─────────────────────────┐
                │  Architect (First Pass) │
                └────────────┬────────────┘
                             │
                             ▼
                 ┌───────────────────────┐
                 │ Foundation Research   │
                 └───────────┬───────────┘
                             │
                             ▼
          ┌──────────────────────────────────┐
          │  Architect (Second Pass)         │
          │                                  │
┌─────────┴─────────┐              ┌─────────┴─────────┐
│ Research-Based    │              │ User-Defined      │
│ Foundation Choice │              │ Foundation        │
└─────────┬─────────┘              └─────────┬─────────┘
          │                                  │
          └──────────────┬───────────────────┘
                         │
                         ▼
                ┌────────────────────┐
                │ Technology Research │
                └──────────┬─────────┘
                           │
                           ▼
         ┌─────────────────────────────────┐
         │  Architect (Third Pass)         │
         │                                 │
┌────────┴────────┐              ┌─────────┴─────────┐
│ Research-Based  │              │ User-Defined      │
│ Tech Choice     │              │ Tech Stack        │
└────────┬────────┘              └─────────┬─────────┘
         │                                 │
         └─────────────┬───────────────────┘
                       │
                       ▼
              ┌──────────────────┐
              │ Standards Engineer│
              └─────────┬────────┘
                        │
                        ▼
               ┌────────────────┐
               │ Product Owner  │
               └────────┬───────┘
                        │
                        ▼
               ┌────────────────┐
               │  Scrum Master  │
               └────────────────┘
```

### Agent-Document Relationships

- Each agent is responsible for specific document types
- Agents consume documents from previous stages
- Agents produce documents for subsequent stages
- Foundation decisions influence entire downstream document chain
- Technology decisions build upon foundation decisions

### Decision-Architecture Relationships

- First decision point produces generic foundation architecture
- Second decision point produces final technology architecture
- Both research-driven and user-defined paths must produce compatible documents
- Decision documentation captures reasoning for future reference

### UI-Agent Relationships

- Each agent has corresponding UI screens
- Decision interfaces support collaborative interactions
- UI screens delegate processing to agent instances
- Agents provide progress updates to UI components

## Critical Implementation Paths

### Document Chain Integrity

The system's most critical path is the document chain that connects:

1. Vision Document →
2. PRD →
3. Technical Research Requirements →
4. Foundation Research Report →
5. Generic Foundation Architecture →
6. Technology Research Report →
7. Final Architecture Document →
8. Standards Document →
9. Task List →
10. Stories

Each document must maintain referential integrity to previous documents.

### Multi-Phase Decision Flow

The decision flow must maintain continuity across phases:

1. Foundation Research →
2. Foundation Decision (dual-path) →
3. Generic Foundation Architecture →
4. Technology Research →
5. Technology Decision (dual-path) →
6. Final Architecture

### Agent Session Continuity

Maintaining consistent session state across agents:

1. Session creation →
2. Document registration →
3. Metadata updates →
4. Decision capturing →
5. Agent handoffs →
6. Document chain validation
