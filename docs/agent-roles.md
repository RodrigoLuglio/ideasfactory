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

### 3. Architect

#### 3a. Architect (First Pass)
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

#### 3b. Architect (Second Pass)
- **Primary Responsibility**: Select foundation approach and create generic architecture document
- **Key Capabilities**:
  - Extract foundation options from research results
  - Present options for user selection
  - Guide users through foundation exploration via interactive chat
  - Support user-defined custom foundations
  - Create technology-neutral generic architecture document
  - Preserve project uniqueness in architectural decisions
  - Define architectural structure for second research phase
- **Inputs**: Foundation Research Report, PRD, Vision Document
- **Outputs**: Selected Foundation Approach, Generic Architecture Document
- **Critical Skills**: Option analysis, architectural design, technology-neutral thinking
- **Model Requirements**: Technical design capabilities, explanation skills, decision-making

#### 3c. Architect (Third Pass)
- **Primary Responsibility**: Select technologies and create complete architecture document
- **Key Capabilities**:
  - Analyze technology research without biasing toward conventional choices
  - Select technologies based on project-specific needs
  - Create tailored architecture document structure unique to the project
  - Define complete implementation architecture
  - Preserve project uniqueness in technology decisions
  - Avoid imposing industry-standard patterns where not appropriate
- **Inputs**: Technology Research Report, Generic Architecture, Previous Documents
- **Outputs**: Complete Architecture Document
- **Critical Skills**: Technology evaluation, architectural design, innovation preservation
- **Model Requirements**: Technical expertise, design capabilities, unbiased decision-making

### 4. Research Team

#### 4a. Research Team (First Pass - Foundation Research)
- **Primary Responsibility**: Explore foundational architectural approaches
- **Key Capabilities**:
  - Use dimensional research methodology to explore foundation options
  - Research across full spectrum from established to experimental approaches
  - Identify viable foundation approaches for the project
  - Map interdependencies between foundations and feature implementation
  - Discover cross-paradigm opportunities that combine different approaches
  - Create comprehensive foundation options with pros and cons
- **Team Structure**:
  - **Foundation Team**: Explores core architectural foundations
  - **Branch Teams**: Investigate specific dimensions across paradigms
  - **Integration Team**: Analyzes cross-dimensional compatibility
- **Inputs**: Technical Research Requirements, PRD, Vision Document
- **Outputs**: Foundation Research Report with implementation path options
- **Critical Skills**: Research depth, multi-paradigm thinking, architectural analysis
- **Model Requirements**: Research capabilities, knowledge synthesis, reasoning

#### 4b. Research Team (Second Pass - Technology Research)
- **Primary Responsibility**: Explore specific technologies for implementing the selected foundation
- **Key Capabilities**:
  - Apply dimensional research methodology to technology exploration
  - Use generic architecture as framework for technology research
  - Explore full spectrum of technologies for each component
  - Identify viable technology combinations and stacks
  - Map interdependencies between technology choices
  - Discover cross-domain technology opportunities
  - Create comprehensive technology options with evaluation criteria
- **Team Structure**:
  - Same parallel team approach applied to technology exploration
  - Focus on specific technologies rather than architectural approaches
- **Inputs**: Generic Architecture Document, Foundation Selection, Previous Documents
- **Outputs**: Technology Research Report with implementation options
- **Critical Skills**: Technology evaluation, integration analysis, stack design
- **Model Requirements**: Technical knowledge, research capabilities, evaluation skills

### 5. Standards Engineer
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

### 6. Product Owner
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

### 7. Scrum Master
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
   - Examples: Claude Opus, GPT-4o, Llama 3 70B

2. **Analytical Roles** (Product Manager, Architect First Pass):
   - Models with strong reasoning and analysis
   - Ability to identify implicit requirements
   - Examples: Claude Sonnet/Opus, GPT-4o, Llama 3 70B

3. **Interactive Roles** (Architect Second Pass):
   - Models with strong conversation and explanation abilities
   - Capable of interactive chat about complex topics
   - Examples: Claude Opus, GPT-4o, Llama 3 70B

4. **Research Roles** (Research Team):
   - Models with extensive knowledge
   - Strong information synthesis abilities
   - Web search capabilities for up-to-date information
   - Examples: Claude Opus, Claude Sonnet+Web, GPT-4o

5. **Decision-Making Roles** (Architect Third Pass):
   - Models with strong reasoning and decision-making
   - Ability to evaluate options without bias toward conventional choices
   - Examples: Claude Opus, GPT-4o, Llama 3 70B

6. **Technical Roles** (Standards Engineer):
   - Models with deep technical knowledge
   - Strong reasoning about implementation
   - Examples: Claude Opus, GPT-4o, DeepSeek Coder

7. **Organizational Roles** (Product Owner, Scrum Master):
   - Models with strong planning and organizational abilities
   - Examples: Claude Sonnet/Opus, GPT-4o, Llama 3 70B

For optimal results in production, the most capable models should be used for all roles, with a potential focus on technically specialized models for the architecture and standards roles. The research roles benefit significantly from web search capabilities.