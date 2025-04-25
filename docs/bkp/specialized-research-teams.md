# Specialized Research Teams Approach

*This document outlines the enhanced multi-agent research system for IdeasFactory, which uses specialized agent teams to conduct comprehensive dimensional research with greater depth and breadth.*

## Core Concept

The Specialized Research Teams approach transforms our dimensional research workflow by utilizing multiple specialized agents with distinct expertise, personalities, and responsibilities. Rather than a single agent simulating parallel teams, this approach employs actual parallel agents working in coordination through a shared knowledge repository and coordination framework.

## Advantages Over Current Approach

1. **Specialized Expertise**: Each agent type has prompts optimized for their specific role
2. **Truly Parallel Research**: Multiple agents can explore different dimensions simultaneously
3. **Diverse Thinking Patterns**: Different agent personalities yield more varied insights
4. **Emergent Discoveries**: Interactions between specialized agents reveal opportunities a single agent might miss
5. **Deeper Analysis**: Specialists can go deeper into their respective areas
6. **Better Debate & Evaluation**: Multiple viewpoints lead to more rigorous evaluation

## Agent Specializations

### Foundation Agents
- **Expertise**: Systems thinking, architectural fundamentals, dependency analysis
- **Personality**: Thoughtful, comprehensive, big-picture oriented
- **Responsibilities**: 
  - Identify foundation dimensions with highest impact
  - Explore options across paradigms for these dimensions
  - Map out downstream implications of different foundation choices
  - Collaborate to identify viable foundation choices worth exploring

### Paradigm Specialist Agents
- **Types**:
  - **Established Approaches Expert**: Deep knowledge of proven, traditional solutions
  - **Mainstream Technologies Expert**: Expertise in current popular technologies
  - **Cutting-Edge Technologies Expert**: Specializes in emerging technologies
  - **Experimental Approaches Expert**: Focuses on research-stage technologies
  - **Cross-Paradigm Specialist**: Identifies integration opportunities across paradigms
  - **First-Principles Thinker**: Designs custom solutions for unique problems

- **Personality**: Each has distinct personality matching their paradigm (conservative for established, innovative for cutting-edge, etc.)
- **Responsibilities**:
  - Provide deep expertise in their paradigm area
  - Contribute to foundation research from their paradigm perspective
  - Evaluate options within their paradigm for each dimension
  - Identify unique strengths and limitations of paradigm-specific approaches

### Path Exploration Agents
- **Expertise**: Technology stack coherence, integration patterns, implementation paths
- **Personality**: Practical, detail-oriented, consistency-focused
- **Responsibilities**:
  - Explore specific paths from foundation choices through dependent dimensions
  - Ensure technological coherence within a path
  - Identify trade-offs in each path
  - Document complete implementation approaches

### Integration Agents
- **Expertise**: Cross-path opportunities, technology compatibility, integration patterns
- **Personality**: Creative, connector, synergy-seeking
- **Responsibilities**:
  - Analyze compatibility between technologies across dimensions and paths
  - Identify novel combinations that address limitations in single-path approaches
  - Solve integration challenges between different paradigms
  - Create integration patterns and approaches

### Synthesis Agents
- **Expertise**: Research synthesis, visualization, communication
- **Personality**: Clear, unbiased, insight-focused
- **Responsibilities**:
  - Compile findings from all agents into cohesive research report
  - Generate visualizations of dimensions, paths, and opportunities
  - Summarize key insights and recommendations
  - Ensure the report maintains the project's innovative vision

## Multi-Agent Research Workflow

### 1. Foundation Phase
All agents participate in foundation research, bringing their specialized perspectives:

- **Process**:
  1. Foundation Agents identify key foundation dimensions
  2. Paradigm Specialists explore options within their expertise
  3. Foundation Agents map implications of different choices
  4. All agents participate in structured debate to identify viable paths
  5. Path Exploration Agents document initial path definitions

- **Outputs**:
  - Foundation dimension analysis
  - Multiple viable foundation choices
  - Initial path definitions for exploration
  - Dependency maps for dimensions

### 2. Path Exploration Phase
Teams of agents are assigned to explore specific research paths:

- **Process**:
  1. Form teams with balanced paradigm expertise for each path
  2. Each team explores their assigned path through all dimensions
  3. Teams document findings in structured format
  4. Paradigm Specialists provide deep expertise as needed

- **Outputs**:
  - Detailed exploration of each research path
  - Technology recommendations for each dimension
  - Trade-off analysis for each path
  - Implementation considerations

### 3. Integration Analysis Phase
Integration Agents analyze across paths to identify opportunities:

- **Process**:
  1. Integration Agents review all path exploration findings
  2. Identify compatibility between technologies across paths
  3. Discover novel combinations that address limitations
  4. Design integration patterns for promising combinations

- **Outputs**:
  - Cross-path opportunity catalog
  - Integration patterns and approaches
  - Compatibility analysis
  - Novel combination recommendations

### 4. Research Synthesis Phase
Synthesis Agents compile findings into comprehensive report:

- **Process**:
  1. Synthesis Agents gather all research findings
  2. Generate dimensional visualizations
  3. Create path comparison visualizations
  4. Produce cross-paradigm opportunity maps
  5. Compile executive summary and recommendations

- **Outputs**:
  - Comprehensive dimensional research report
  - Visual dimension maps
  - Path comparison visualizations
  - Cross-paradigm opportunity maps
  - Executive summary with balanced recommendations

## Implementation Architecture

### 1. Agent Framework
- **BaseResearchAgent**: Core capabilities shared by all agents
- **Specialized agent classes**: Foundation, Paradigm, Path, Integration, Synthesis
- **AgentCoordinator**: Orchestrates communication between agents

### 2. Knowledge Repository
- **DimensionalResearchRepository**: Shared knowledge store
- Structured storage for:
  - Foundation choices
  - Dimension findings
  - Path exploration results
  - Cross-paradigm opportunities
  - Integration patterns

### 3. Communication Framework
- **Message passing system** for inter-agent communication
- **Structured debate protocol** for foundation choices
- **Knowledge sharing mechanisms**
- **Conflict resolution procedures**

### 4. Research UI Enhancements
- **Team collaboration visualization**
- **Structured debate visualization**
- **Research progress tracking** for multiple agents
- **Path comparison tools**
- **Integration opportunity explorer**

## Technical Implementation Plan

### Phase 1: Agent Framework
1. Create `BaseResearchAgent` class with common capabilities
2. Implement specialized agent classes with unique prompts
3. Develop `AgentCoordinator` for orchestration
4. Create `DimensionalResearchRepository` for shared knowledge

### Phase 2: Communication Framework
1. Design message formats for inter-agent communication
2. Implement debate protocol for foundation choices
3. Create knowledge sharing mechanisms
4. Develop conflict resolution procedures

### Phase 3: Workflow Implementation
1. Implement Foundation Phase workflow
2. Develop Path Exploration Phase workflow
3. Create Integration Analysis Phase workflow
4. Implement Research Synthesis Phase workflow

### Phase 4: UI Enhancements
1. Update research screen for multi-agent visualization
2. Implement team collaboration visualization
3. Create path comparison tools
4. Develop integration opportunity explorer

## Prompt Engineering

Distinct prompts for each agent type will be critical to their specialized capabilities:

### Foundation Agent Prompt
```
You are a Foundation Research Agent specializing in systems thinking and architectural fundamentals. Your role is to identify foundation dimensions that impact all other aspects of the system and explore options across multiple paradigms.

Focus on:
1. Identifying dimensions with highest impact across the system
2. Mapping interdependencies between dimensions
3. Understanding how foundation choices create different paths
4. Evaluating options objectively across multiple paradigms
5. Considering long-term implications of foundation choices

Avoid:
1. Defaulting to conventional solutions without thorough analysis
2. Making assumptions about specific technologies
3. Limiting exploration to familiar paradigms
4. Ignoring the unique characteristics of this specific project

As you analyze foundation dimensions, be comprehensive, thoughtful, and aim to create a solid foundation that enables innovative implementation paths while maintaining architectural integrity.
```

### Paradigm Specialist Prompt (Example: Cutting-Edge Expert)
```
You are a Cutting-Edge Technologies Expert specializing in emerging technologies gaining traction in the industry. Your role is to identify promising new approaches that could provide significant advantages.

Focus on:
1. Technologies that have recently moved beyond experimental stage
2. Approaches gaining momentum in industry adoption
3. Solutions that offer step-change improvements over mainstream options
4. Technologies with growing communities and support
5. Emerging patterns that address known limitations of established approaches

Avoid:
1. Purely experimental technologies without proven implementation
2. Overestimating maturity of emerging approaches
3. Ignoring integration challenges with existing systems
4. Recommending cutting-edge solutions when they don't align with project needs

As you evaluate cutting-edge options, be forward-thinking but grounded, identifying opportunities where newer approaches offer genuine advantages while being pragmatic about implementation considerations.
```

### Path Exploration Agent Prompt
```
You are a Path Exploration Agent specializing in evaluating complete technology stacks across dimensions. Your role is to ensure technological coherence within implementation paths.

Focus on:
1. Following a specific foundation choice through all dependent dimensions
2. Ensuring compatibility between technologies across dimensions
3. Identifying trade-offs in each implementation path
4. Documenting coherent, complete implementation approaches
5. Evaluating the path against project requirements

Avoid:
1. Mixing incompatible technologies within a path
2. Ignoring dependencies between dimensions
3. Over-optimizing for one dimension at the expense of others
4. Losing sight of the project's unique vision

As you explore your assigned path, be thorough, detail-oriented, and practical, ensuring all recommendations work together as a coherent whole while preserving the project's innovative characteristics.
```

## Conclusion

The Specialized Research Teams approach represents a significant advancement in IdeasFactory's research capabilities. By leveraging multiple specialized agents working in coordination, this approach will produce more comprehensive, innovative, and balanced research findings that better serve the goal of creating self-contained implementation packages.