# IdeasFactory Active Context

## Core Philosophy

The foundational principle guiding all aspects of IdeasFactory is the preservation of each idea's inherent uniqueness:

**We treat each idea as inherently unique and preserve its innovation potential by avoiding templates, guides, or any predetermined patterns that could impose limitations.**

This means every aspect of our system is designed to:

- Adapt to the unique characteristics of each idea, rather than forcing ideas into conventional patterns
- Avoid biasing outputs with templates or hard-coded examples
- Preserve innovation potential through open-minded exploration
- Actively challenge assumptions that might limit innovation
- Explore the full spectrum of possibilities from established to experimental approaches
- Ensure no unique aspect of an idea is lost due to conventional implementation constraints

This philosophy influences every prompt, agent implementation, and document generation strategy throughout the system.

## Current Project Focus

IdeasFactory is currently in active development, with a focus on implementing the enhanced multi-phase research and architecture workflow. The system has successfully implemented the first research phase that explores foundation paths (architectural approaches) and is now working on the foundation decision phase with the Architect's second pass.

### Current Priority Areas

1. **Three-Phase Decision Approach**: Implementing the refined workflow that separates:

   - Foundation path research (completed)
   - Foundation decision and generic architecture (in progress)
   - Technology stack research and selection (planned)

2. **User Choice Enhancement**: Adding flexibility by giving users two options at decision points:

   - Select from research results with architect guidance
   - Explain their predetermined choices with architect assistance

3. **Interactive Decision Sessions**: Creating collaborative chat interfaces for foundation and technology decisions

4. **Document Chain Integrity**: Ensuring seamless information flow between different phases and documents

5. **Innovation Preservation**: Actively ensuring each idea's unique characteristics are preserved throughout the process

6. **Self-Contained Story Packages**: The ultimate goal of creating comprehensive developer packages

## Recent Changes

### Workflow Refinement

- Added PRD (Product Requirements Document) step to better capture implicit requirements
- Evolved the research approach into a multi-phase decision process:
  - Phase 1: Foundation Path Research (completed)
  - Phase 2: Foundation Decision & Generic Architecture (in development)
  - Phase 3: Technology Stack Research (planned)
  - Phase 4: Technology Stack Decision & Final Architecture (planned)
- Implemented weighted criteria for foundation path evaluation
- Added user choice at decision points to accommodate different user knowledge levels
- Redefined the Architect role into three passes:
  - First Pass: Technical research requirements (completed)
  - Second Pass: Foundation decision and generic architecture (in development)
  - Third Pass: Technology stack decision and final architecture (planned)
- Strengthened emphasis on preserving innovation potential throughout all phases

### Research Implementation

- Implemented dimensional research approach with foundation, branch, and integration teams
- Added cross-paradigm opportunity identification
- Created structured research reporting with implementation paths visualization
- Developed decision support framework with weighted criteria for path selection
- Terminology evolved from "foundations" and "technology options" to "foundation approaches" and "implementation paths"
- Designed research to avoid biasing toward mainstream solutions
- Implemented assumption-challenging questions to push beyond conventional thinking

### Technical Implementation

- Integrated LiteLLM for provider-agnostic LLM interactions
- Implemented document review screens supporting all document types
- Added session management with Git-based version tracking
- Created document models with frontmatter metadata
- Designed prompts to preserve uniqueness and avoid conventional constraints

## Active Decisions and Considerations

### Current Design Decisions

1. Two distinct decision points with user choice at each:

   - Foundation decision (Architect's second pass)
   - Technology stack decision (Architect's third pass)

2. Dual-path approach at decision points:

   - Option 1: User reviews research and selects with architect guidance
   - Option 2: User shares predetermined choices with architect assistance

3. Chat-based interactive sessions for both decision phases

4. Generic foundation architecture document as output from second pass

5. Technical research focused only on the selected foundation path

6. Final architecture document incorporating all previous decisions as output from third pass

7. No templates or predetermined patterns at any stage

### Open Considerations

1. Designing the user experience for the foundation decision chat interface
2. Implementing a specialized Technology Research Agent for Phase 3
3. Determining level of detail for the generic foundation architecture document
4. Balancing information density in decision sessions
5. Determining how to document user's reasoning when they bring predetermined choices
6. Ensuring prompts remain free of biasing language or examples
7. Creating effective assumption-challenging questions without introducing bias

## Important Patterns and Preferences

### Philosophical Commitments

- **Zero Templating**: No templates, guides, or hard-coded examples that could bias outputs
- **Open-Minded Exploration**: Every project aspect approached with a fresh perspective
- **Assumption Challenging**: Active questioning of conventional assumptions
- **Multi-Paradigm Thinking**: Exploration across the full spectrum from established to experimental
- **Idea-Centric Adaptation**: The system adapts to the idea, not vice versa

### Workflow Patterns

- User choice at critical decision points
- Interactive chat-based decision sessions
- Phased research with increasing specificity
- Document chain with clear dependencies

### Documentation Standards

- All documents use markdown with YAML frontmatter
- System prompts clearly define agent roles and responsibilities
- Document generation involves extraction-transformation phases
- Sessions track document relationships and metadata

### Project Preferences

- Focus on preserving innovation rather than defaulting to mainstream solutions
- Prefer explicit integration points over implicit assumptions
- Maintain clear boundaries between agent responsibilities
- Ensure complete context for AI implementation
- Provide flexibility for users with different knowledge levels
- Avoid any language that limits innovation potential

## Learnings and Project Insights

### Key Insights

- Research naturally evolved into a multi-phase approach that's more efficient than originally envisioned
- Separating architectural foundation decisions from technology stack decisions creates a more manageable decision process
- Users have different starting points - some already know their foundation or tech stack preferences
- The system needs to accommodate both exploratory and confirmatory decision paths
- Weighted criteria evaluation helps with objective foundation path selection
- Integration requires explicit standards and patterns documentation
- Preserving innovation potential requires vigilance against subtle biases in prompts and interfaces

### Technical Learnings

- LLM-based agents benefit from structured interactive sessions
- Document generation is more reliable with structured intermediate extraction
- Session management is critical for maintaining context across the workflow
- User experience benefits from choice and flexibility at decision points
- Prompts need careful crafting to avoid introducing biases or limitations
- Zero-templating philosophy produces more creative and tailored solutions

## Next Steps

### Immediate Priorities

1. Implement Architect's second pass with dual-path options:

   - Research review and selection path
   - User-driven foundation explanation path

2. Create the generic foundation architecture document template that adapts to each unique project

3. Design and implement Technology Research Agent for focused tech stack exploration

4. Develop collaborative session structure for both decision phases

5. Create decision documentation templates to capture reasoning

6. Review all prompts to eliminate any subtle biases or conventional constraints

### Medium-term Goals

1. Implement Architect's third pass with dual-path options for technology decisions
2. Enhance standards engineer to identify integration points across components
3. Implement story packaging with integration references
4. Improve session metadata tracking for cross-document relationships
5. Develop more sophisticated assumption-challenging questions to push innovation boundaries

### Long-term Vision

1. Create truly autonomous multi-agent research teams
2. Support complex software ecosystems with multiple integration points
3. Enable seamless handoff to AI developer agents
4. Support continuous project evolution with version tracking
5. Push the boundaries of what's possible in preserving innovation potential
