# IdeasFactory Agent Roles

This document describes the specialized agent roles in the enhanced IdeasFactory workflow, detailing their responsibilities, inputs, outputs, and key characteristics.

## Core Agent Roles

### 1. Business Analyst (BA)
- **Primary Responsibility**: Transform initial ideas into a clear project vision
- **Key Capabilities**:
  - Facilitate brainstorming sessions to explore ideas
  - Identify core features and user needs
  - Maintain focus on the unique essence of each idea
  - Avoid biasing the solution toward conventional approaches
- **Inputs**: Initial project idea from user
- **Outputs**: Project Vision Document
- **Critical Skills**: Creative thinking, feature extraction, requirements gathering
- **Model Requirements**: High creativity, conversational skills

### 2. Product Manager (PM)
- **Primary Responsibility**: Expand vision into comprehensive requirements
- **Key Capabilities**:
  - Identify explicit and implicit requirements
  - Define non-functional requirements
  - Ensure completeness of requirements
  - Identify edge cases and potential challenges
- **Inputs**: Project Vision Document
- **Outputs**: Product Requirements Document (PRD)
- **Critical Skills**: Requirements analysis, product thinking, user empathy
- **Model Requirements**: Strong analytical thinking, domain understanding

### 3. Architect (First Pass)
- **Primary Responsibility**: Identify technical components needing research and direct multi-paradigm exploration
- **Key Capabilities**:
  - Analyze requirements to determine technical needs
  - Create targeted research questions across multiple technological paradigms
  - Direct exploration of established, mainstream, cutting-edge, experimental, cross-paradigm, and first-principles approaches
  - Formulate assumption-challenging questions that push beyond conventional thinking
  - Identify technical components with unique characteristics requiring tailored research
  - Recognize implicit technical requirements
  - Maintain innovation integrity by avoiding bias toward mainstream solutions
- **Inputs**: PRD and Vision Document
- **Outputs**: Technical Research Requirements with multi-paradigm directives
- **Critical Skills**: Technical breadth, systems thinking, multi-paradigm awareness, innovation mindset
- **Model Requirements**: Technical knowledge, analytical reasoning, creative thinking

### 4. Research Team
- **Primary Responsibility**: Conduct deep research on all aspects of implementation

#### 4a. Market Researcher
- **Key Capabilities**:
  - Analyze competitive landscape
  - Identify market trends and opportunities
  - Uncover user needs and preferences
- **Critical Skills**: Market analysis, trend spotting, competitive intelligence

#### 4b. Technical Researcher
- **Key Capabilities**:
  - Explore implementation options for each technical component
  - Research frameworks, libraries, platforms, and tools
  - Compare approaches across multiple dimensions
  - Identify unconventional technical solutions
- **Critical Skills**: Technical breadth, research depth, option analysis

#### 4c. Domain Expert
- **Key Capabilities**:
  - Provide field-specific insights
  - Identify domain best practices
  - Recognize domain-specific challenges
- **Critical Skills**: Domain knowledge, pattern recognition

- **Inputs**: PRD and Technical Research Requirements
- **Outputs**: Comprehensive Research Document
- **Model Requirements**: Research capabilities, knowledge synthesis, reasoning

### 5. Architect (Final Pass)
- **Primary Responsibility**: Create comprehensive technical architecture
- **Key Capabilities**:
  - Design system architecture based on requirements and research
  - Make informed technical decisions
  - Define component boundaries and interfaces
  - Create implementation guidance
- **Inputs**: PRD and Research Documents
- **Outputs**: Architecture Document
- **Critical Skills**: Technical design, decision-making, systems thinking
- **Model Requirements**: Technical expertise, design capability

### 6. Standards Engineer
- **Primary Responsibility**: Ensure seamless integration across implementation components
- **Key Capabilities**:
  - **Cross-reference tasks** to identify shared aspects across multiple implementation units
  - Identify potential integration gaps, loose ends, and duplication risks
  - Define precisely how components should interact and integrate
  - Create detailed integration patterns with concrete examples
  - Specify shared resources, interfaces, and communication mechanisms
  - Define standards for:
    - Code style and organization
    - Naming conventions
    - File structure and organization
    - Component interfaces
    - State management
    - Data flow
    - Error handling
    - Testing approaches
    - Logging and monitoring
    - CI/CD and deployment
- **Inputs**: 
  - Architecture Document
  - Task List (works closely with Product Owner)
- **Outputs**: 
  - Comprehensive Standards and Patterns Document
  - Integration guidelines for each shared component
  - Concrete examples of proper integration
- **Critical Skills**: 
  - System-level integration thinking
  - Pattern recognition across components
  - Interface design
  - Technical consistency enforcement
- **Model Requirements**: 
  - Exceptional technical precision
  - Systems thinking
  - Pattern recognition
  - Integration expertise

### 7. Product Owner
- **Primary Responsibility**: Create a detailed, granular task list for implementation
- **Key Capabilities**:
  - Break down architecture into sequential implementation tasks
  - Create highly granular task descriptions
  - Identify prerequisites and dependencies
  - Ensure complete coverage of all features
- **Inputs**: Architecture, Standards, and previous documents
- **Outputs**: Detailed Task List with implementation sequence
- **Critical Skills**: Task breakdown, sequence planning, technical understanding
- **Model Requirements**: Strong analytical thinking, implementation knowledge

### 8. Scrum Master
- **Primary Responsibility**: Organize tasks into self-contained user stories
- **Key Capabilities**:
  - Group related tasks into logical user stories
  - Organize stories into epics
  - Create self-contained story documents with all implementation details
  - Ensure each story has everything needed for implementation
  - Track story completion status
- **Inputs**: Task List and all previous documents
- **Outputs**: 
  - Epics/Stories index with completion tracking
  - Individual self-contained story documents 
- **Critical Skills**: Agile methodology, documentation packaging, context management
- **Model Requirements**: Organizational skills, documentation synthesis

## Model Selection Considerations

Different agent roles benefit from different types of large language models:

1. **Creative Roles** (Business Analyst):
   - Models with strong creative abilities
   - Excellence in conversation and ideation
   - Examples: Claude Opus, GPT-4

2. **Analytical Roles** (Product Manager, Architect):
   - Models with strong reasoning and analysis
   - Ability to identify implicit requirements
   - Examples: Claude Sonnet/Opus, GPT-4

3. **Research Roles** (Research Team):
   - Models with extensive knowledge
   - Strong information synthesis abilities
   - Examples: Claude Opus, DeepSeek, GPT-4

4. **Technical Roles** (Architect, Standards Engineer):
   - Models with deep technical knowledge
   - Strong reasoning about implementation
   - Examples: Claude Opus, DeepSeek Coder, GPT-4

For optimal results in production, the most capable models should be used for all roles, with a potential focus on technically specialized models for the architecture and standards roles.