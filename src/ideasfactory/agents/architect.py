# In ideasfactory/agents/architect.py
"""
Architect agent for IdeasFactory.

This module implements the Architect agent that defines the technical architecture
based on the project vision document and research report.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum
import asyncio
import json

from pydantic import BaseModel, Field

from ideasfactory.utils.llm_utils import (
    Message, send_prompt, create_system_prompt, create_user_prompt,
    create_assistant_prompt
)

from ideasfactory.utils.error_handler import handle_async_errors
from ideasfactory.utils.session_manager import SessionManager

# Make enhanced tools available to the architect
from ideasfactory.tools.enhanced_web_search import (
    search_custom,
    fetch_full_page,
    search_and_fetch,
)
from ideasfactory.tools.enhanced_data_analysis import (
    extract_text_features,
)
from ideasfactory.tools.tech_evaluation import (
    create_evaluation_framework,
    evaluate_technology,
    compare_technologies,
    generate_evaluation_report
)
from ideasfactory.tools.research_visualization import (
    create_ascii_table,
    create_timeline,
)

# Configure logging
logger = logging.getLogger(__name__)

# Architect system prompt
ARCHITECT_SYSTEM_PROMPT = """
You are a visionary solution architect with endless creativity and analytical insight.

Your role is to discover and articulate ALL technical aspects of a project while preserving its unique essence. You approach each project as fundamentally distinctive, requiring its own emergent architectural thinking rather than following industry standards or conventional patterns.

In your first phase, you identify what aspects need deeper research. You create a comprehensive framework that guides exploration across the complete spectrum of possibilities without biasing toward any particular approach. You help uncover ALL requirements needed to fully implement the project, whether explicitly stated or implicitly needed.

The research framework you create should:
- Emerge organically from the project's unique nature rather than predetermined categories
- Enable exploration across ALL possible approaches from established to experimental
- Preserve what makes this specific idea innovative and distinctive
- Challenge fundamental assumptions about how features "should" be implemented
- Open pathways to discovering solutions uniquely suited to THIS specific project

You never make assumptions about "standard" components or implementation details, and you don't use prescriptive language that might limit creative exploration. Your guidance enables discovery rather than prescription.

In your second phase (after research), you help define a bespoke architecture that perfectly embodies the project's distinctive vision. You present comprehensive options across the full spectrum of possibilities for each architectural aspect, explaining implications without imposing biases.

Above all, you ensure that each document you produce fully captures the project's unique character, preserving what makes this idea special while making it technically feasible. You resist defaulting to mainstream solutions and instead facilitate the discovery of approaches that might best serve THIS specific project's distinctive nature.
"""

ARCHITECT_RESEARCH_REQUIREMENTS_PROMPT = """
Create a comprehensive multi-level research framework that identifies ALL aspects requiring exploration before architectural decisions can be made. This framework must guide the research team to identify and evaluate specific implementation options across the COMPLETE spectrum for each research area.

While YOU should avoid naming specific technologies in this document, you must EXPLICITLY DIRECT the research team to discover and evaluate specific technologies and approaches in their research. Their job is to identify concrete implementation options from established to experimental for each aspect of the project.

ESSENTIAL MULTI-LEVEL APPROACH:

1. IDENTIFY ALL TECHNICAL REQUIREMENTS for complete implementation:
   - Document EVERY technical need necessary to fully implement this project
   - Uncover both explicit requirements mentioned in the vision/PRD AND implicit requirements not directly stated
   - Consider the complete implementation journey from foundation to user-facing features
   - Focus on WHAT needs to be implemented, not HOW to implement it
   
2. ESTABLISH A CLEAR RESEARCH HIERARCHY that:
   - Identifies foundational technical requirements that must be researched FIRST
   - Shows how choices at the foundation level will create different paths for feature implementation
   - Establishes clear dependencies between research areas
   - Guides researchers to explore complete technological paths, not isolated components

3. MAP INTERDEPENDENCY RELATIONSHIPS between research areas:
   - Show how discoveries in foundational areas will shape exploration in dependent areas
   - Create a network of interconnected research pathways rather than isolated topics
   - Illustrate how decisions branch from foundational choices through implementation details
   - Identify where different paths may converge or create novel integration opportunities

4. DIRECT FULL-SPECTRUM EXPLORATION across all research areas:
   - Guide researchers to explore foundation options across the COMPLETE spectrum for EACH area:
     * From established approaches to experimental innovations
     * From mainstream solutions to first-principles thinking
     * From conventional patterns to revolutionary concepts
   - Show how different spectrum positions might create unique advantages for THIS project

5. CRAFT ILLUMINATING QUESTIONS that:
   - Challenge fundamental assumptions about how this project "should" be implemented
   - Reveal possibilities that conventional thinking would overlook
   - Connect directly to what makes this project distinctive and valuable
   - Push exploration beyond the boundaries of established practice
   - Encourage researchers to discover approaches uniquely suited to THIS SPECIFIC project

6. MAINTAIN ABSOLUTE INNOVATION INTEGRITY by:
   - NEVER naming specific technologies, frameworks, or implementation approaches in YOUR document (that is the research team's job)
   - CLEARLY STATING that the research team MUST identify and evaluate specific technologies and frameworks across the entire spectrum
   - ACTIVELY RESISTING conventional patterns and mainstream defaults in your requirements
   - EMPHASIZING the project's unique essence throughout the framework
   - ENABLING the research team to discover ALL possible implementation options, not merely validate conventional approaches
   - PRESERVING what makes this project distinctive through the entire research process

Your document should provide:
- A comprehensive list of ALL technical requirements needed for complete implementation
- A clear hierarchy showing which areas must be researched first (foundations) and how other areas depend on those choices
- A map of interdependencies between different research areas
- Guidance for exploring the full spectrum of possibilities in each area without biasing toward any particular approach
- Questions that challenge assumptions and connect to the project's distinctive aspects

CRITICALLY IMPORTANT: 
1. YOU should avoid prescribing specific technologies, frameworks, or implementation approaches in your document.
2. EXPLICITLY DIRECT the research team to identify and evaluate specific technologies, frameworks, and implementation approaches across the FULL spectrum for each research area.
3. Make it clear that the research team's PRIMARY RESPONSIBILITY is to discover ALL viable implementation options (from established to experimental) for each research area.

Your document should give the research team both clear structure (what to research and in what order) and clear direction to identify specific implementation options across the entire spectrum.
"""

ARCHITECT_ANALYSIS_PROMPT = """
First, conduct a STRICT BOUNDARY ANALYSIS between the project vision document and research report:

1. Extract ONLY the explicitly stated features and requirements from the vision document
2. For each identified feature, locate all implementation approaches described in the research report

This strict boundary preservation is critical - the architecture must implement EXACTLY what was envisioned, no more and no less.

For each core feature from the vision document:
- Document the precise feature description
- Map all technology options explored in the research report
- Identify any additional viable approaches not mentioned in the research

Then determine the comprehensive set of architectural decisions needed, with these critical requirements:
- Each decision must directly implement a specific feature from the vision document
- Every feature from the vision document must have corresponding architectural decisions
- The scope must remain absolutely faithful to the vision document

For each decision point, provide:
1. The exact decision that needs to be made
2. At least 5-7 different implementation options with detailed pros/cons for each
3. Present all options neutrally, without recommendations

Structure your response as follows:

## Core Feature Analysis
[List each feature precisely as described in the vision document]

## Architectural Decisions
[Only decisions that directly implement the identified features]

For the architectural decisions:
- Create categories based solely on this project's specific needs
- For each feature, explore the complete spectrum of implementation approaches
- Include traditional, current mainstream, and emerging implementation options
- Present each option objectively with detailed analysis

CRITICAL: The architecture must remain precisely within the boundaries of what was explicitly described in the vision document - no assumptions about additional functionality or standard features unless explicitly mentioned.
"""

ARCHITECT_DOCUMENT_CREATION_PROMPT = """
Create an architecture document that PRECISELY implements the vision document's features - nothing more, nothing less. This document must maintain absolute scope discipline.

ESSENTIAL REQUIREMENTS:

1. SCOPE INTEGRITY:
   - The functional requirements section must EXACTLY match the features in the vision document
   - Include ONLY architectural elements that directly implement these explicit features
   - NEVER add "standard" or "assumed" features not specified in the vision document

2. IMPLEMENTATION CLARITY:
   - For each feature from the vision document, document the implementation approach we selected
   - Ensure the chosen implementation approach matches the option we actually selected during our discussion
   - Provide detailed specifications for how each feature will be technically realized

3. DOCUMENT STRUCTURE:
   - Create a document organization that perfectly reflects THIS project's specific nature
   - The structure should emphasize the unique aspects of this particular solution
   - Avoid generic template structures that could apply to any similar project

4. TECHNICAL FOCUS:
   - Emphasize how the specific technical decisions support the project's unique needs
   - Explain integration points between features to show how they work as a cohesive system
   - Document any technical considerations specific to this project's distinctive approach

Before finalizing:
- Verify that EVERY feature from the vision document is implemented in the architecture
- Confirm that NO additional features have been introduced
- Ensure the document maintains the essential character and vision of the original idea
- Verify that the technical decisions match exactly what we agreed upon in our discussion

The final document should read as a precise blueprint for implementing exactly what was envisioned - a perfect translation from concept to technical specification, without scope creep or omissions.
"""


class SessionState(Enum):
    """State of the architecture definition session."""
    STARTED = "started"
    RESEARCH_REQUIREMENTS = "research_requirements"
    ANALYZING = "analyzing"
    DECISION_MAKING = "decision_making"
    DOCUMENT_CREATION = "document_creation"
    DOCUMENT_REVIEW = "document_review"
    COMPLETED = "completed"


class ArchitecturalDecision(BaseModel):
    """An architectural decision to be made."""
    id: str = Field(..., description="Unique identifier for the decision")
    category: str = Field(..., description="Category of the decision (e.g., 'frontend', 'database')")
    title: str = Field(..., description="Title of the decision")
    description: str = Field(..., description="Description of the decision to be made")
    options: List[Dict[str, Any]] = Field(..., description="List of options with pros and cons")
    recommendation: Optional[str] = Field(None, description="Recommended option")
    decision: Optional[str] = Field(None, description="Final decision made")
    rationale: Optional[str] = Field(None, description="Rationale for the decision")
    completed: bool = Field(False, description="Whether the decision has been made")


class ArchitectureSession(BaseModel):
    """An architecture definition session with the Architect."""
    id: str = Field(..., description="Unique identifier for the session")
    project_vision: str = Field(..., description="Project vision document content")
    prd_document: Optional[str] = Field(None, description="Product Requirements Document content")
    research_report: Optional[str] = Field(None, description="Research report content")
    research_requirements: Optional[str] = Field(None, description="Technical research requirements document content")
    messages: List[Message] = Field(default_factory=list, description="Messages in the session")
    decisions: List[ArchitecturalDecision] = Field(default_factory=list, description="Architectural decisions to be made")
    current_decision_index: Optional[int] = Field(None, description="Index of the current decision being discussed")
    state: SessionState = Field(default=SessionState.STARTED, description="Current state of the session")
    architecture_document: Optional[str] = Field(None, description="Generated architecture document content")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata for the session")
    
    class Config:
        """Pydantic model configuration."""
        arbitrary_types_allowed = True
        

class Architect:
    """
    Architect agent that defines the technical architecture for the project.
    
    Implemented as a singleton to ensure the same instance is shared across the application.
    """
    
    _instance = None
    
    def __new__(cls):
        """Ensure only one instance of Architect is created."""
        if cls._instance is None:
            cls._instance = super(Architect, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the Architect agent."""
        if not hasattr(self, '_initialized') or not self._initialized:
            self.sessions: Dict[str, ArchitectureSession] = {}
            self.system_prompt = create_system_prompt(ARCHITECT_SYSTEM_PROMPT)
            self._initialized = True
    
    @handle_async_errors
    async def create_session(
        self, 
        session_id: str, 
        project_vision: str, 
        prd_document: Optional[str] = None,
        research_report: Optional[str] = None
    ) -> ArchitectureSession:
        """
        Create a new architecture definition session.
        
        Args:
            session_id: Unique identifier for the session
            project_vision: Project vision document content
            prd_document: Product Requirements Document content (optional)
            research_report: Research report content (optional)
            
        Returns:
            The created architecture session
        """
        # Create a new session
        session = ArchitectureSession(
            id=session_id,
            project_vision=project_vision,
            prd_document=prd_document,
            research_report=research_report,
            messages=[self.system_prompt],
            state=SessionState.STARTED
        )
        
        # Store the session
        self.sessions[session_id] = session
        
        return session
        
    @handle_async_errors
    async def create_research_requirements(self, session_id: str) -> Optional[str]:
        """
        Create technical research requirements document based on the PRD.
        
        Args:
            session_id: Identifier of the session
            
        Returns:
            The research requirements document content or None if session not found
        """
        # Get the session
        session = self.sessions.get(session_id)
        if not session:
            logger.error(f"Session not found: {session_id}")
            return None
            
        # Ensure we have a PRD document
        if not session.prd_document:
            logger.error(f"No PRD document available for session {session_id}")
            return None
            
        # Update session state
        session.state = SessionState.RESEARCH_REQUIREMENTS
        
        # Create the research requirements prompt
        requirements_prompt = f"""
        Analyze the Project Vision and Product Requirements Document (PRD) to create a comprehensive research framework that enables exploration of ALL aspects needed to bring this unique idea to life. 

        # Project Vision
        {session.project_vision}

        # Product Requirements Document (PRD)
        {session.prd_document}

        {ARCHITECT_RESEARCH_REQUIREMENTS_PROMPT}
        """
        
        # Create the message
        requirements_request = create_user_prompt(requirements_prompt)
        session.messages.append(requirements_request)
        
        # Get the agent's response
        response = await send_prompt(session.messages)
        
        # Add the response to the session
        assistant_message = create_assistant_prompt(response.content)
        session.messages.append(assistant_message)
        
        # Store the research requirements
        session.research_requirements = response.content
        
        return response.content
    
    @handle_async_errors
    async def revise_research_requirements(self, session_id: str, feedback: str) -> Optional[str]:
        """
        Revise the technical research requirements document based on feedback.
        
        Args:
            session_id: Identifier of the session
            feedback: Feedback for the research requirements document
            
        Returns:
            The revised research requirements content or None if session not found
        """
        # Get the session
        session = self.sessions.get(session_id)
        if not session:
            logger.error(f"Session not found: {session_id}")
            return None
        
        # Ensure we have a research requirements document
        if not session.research_requirements:
            logger.error(f"No research requirements document available for session {session_id}")
            return None
        
        # Create the revision prompt
        revision_prompt = f"""
        Please revise the Technical Research Requirements document based on this feedback:
        
        {feedback}
        
        When revising, maintain the focus on identifying all technical components that need research before architectural decisions can be made. Ensure your revised document:
        
        1. Preserves the unique aspects of the project vision
        2. Provides clear, focused research questions for each technical component
        3. Offers guidance on what technical approaches to explore
        4. Ensures comprehensive coverage of all technical aspects
        
        Please provide the complete revised document in markdown format.
        """
        
        # Create the message
        revision_request = create_user_prompt(revision_prompt)
        session.messages.append(revision_request)
        
        # Get the agent's response
        response = await send_prompt(session.messages)
        
        # Add the response to the session
        assistant_message = create_assistant_prompt(response.content)
        session.messages.append(assistant_message)
        
        # Update the research requirements
        session.research_requirements = response.content
        
        return response.content
    
    @handle_async_errors
    async def complete_session(self, session_id: str) -> bool:
        """
        Complete the architecture definition session.
        
        Args:
            session_id: Identifier of the session
            
        Returns:
            True if the session was completed, False otherwise
        """
        # Get the session
        session = self.sessions.get(session_id)
        if not session:
            logger.error(f"Session not found: {session_id}")
            return False
        
        # Update the session state
        session.state = SessionState.COMPLETED
        
        return True

    # TODO Think on how should we improve/adapt/replace the methods from here until the end of the file to properly implement our new 3-step architecture workflow. 
    # TODO The first step is the generation of the research requirements that is already implemented above
    # TODO The second step is the decision making with the user on which of the foundational paths from the 1st step of research results to use or gather the foundation inforamtion from the user in case he already knows with what foundation he wants to implement his project on, and generate a complete generic architecture document to identify and inform the research team everything that needs to be researched to gather the technology options for the next step.
    # TODO The third step is after the research team provides the technology research result with all technologies and technology stack options make the decisions on which to use with the user, again, unless the user already know what technologies and stack he wants, in that case we should gather the information from him. And generate the final complete project architecture document with each and every information needed to bring the project to life from beggining to end. The document must be completely tailored to the unique project that emerged from the original idea following all oour project's philosophy and principles.

    @handle_async_errors    
    async def start_analysis(self, session_id: str) -> Optional[List[ArchitecturalDecision]]:
        """
        Start the architecture analysis process.
        
        Args:
            session_id: Identifier of the session to analyze
            
        Returns:
            List of architectural decisions to be made or None if session not found
        """
        # Get the session
        session = self.sessions.get(session_id)
        if not session:
            logger.error(f"Session not found: {session_id}")
            return None
        
        # Update the session state
        session.state = SessionState.ANALYZING
        
        # Create the analysis message
        analysis_message = create_user_prompt(
            f"""I need you to analyze these documents and identify the key architectural decisions we need to make:

Project Vision Document:
{session.project_vision}

Research Report:
{session.research_report}

{ARCHITECT_ANALYSIS_PROMPT}"""
        )
        session.messages.append(analysis_message)
        
        # Get the agent's response
        response = await send_prompt(session.messages)
        
        # Add the response to the session
        assistant_message = create_assistant_prompt(response.content)
        session.messages.append(assistant_message)
        
        # Parse the decisions from the response
        # This would involve NLP in a production system, but for now we'll
        # use a separate API call to extract structured decisions
        decisions = await self._extract_decisions(session_id, response.content)
        
        # Update the session with the decisions
        session.decisions = decisions
        
        # Set the current decision index to the first decision
        if decisions:
            session.current_decision_index = 0
        
        # Update the session state
        session.state = SessionState.DECISION_MAKING
        
        return decisions
    
    @handle_async_errors
    async def _extract_decisions(self, session_id: str, analysis_text: str) -> List[ArchitecturalDecision]:
        """
        Extract architectural decisions from the analysis text.
        
        Args:
            session_id: Identifier of the session
            analysis_text: Text containing the analysis
            
        Returns:
            List of extracted architectural decisions
        """
        # Get the session
        session = self.sessions.get(session_id)
        if not session:
            logger.error(f"Session not found: {session_id}")
            return []
        
        # Extract the requirements section for later use in document creation
        import re
        requirements_match = re.search(r'## Requirements Analysis\s*(.*?)(?=##|\Z)', analysis_text, re.DOTALL)
        if requirements_match:
            requirements_text = requirements_match.group(1).strip()
            # Store the requirements in the session metadata for later use
            if not hasattr(session, 'metadata'):
                session.metadata = {}
            session.metadata['requirements_analysis'] = requirements_text
            logger.info(f"Extracted requirements analysis of length {len(requirements_text)}")
        else:
            logger.warning("Requirements Analysis section not found in architect's analysis")
        
        # Create a prompt to extract decisions
        extraction_prompt = f"""
        Based on the analysis below, extract a structured list of architectural decisions that need to be made.
        
        Analysis:
        {analysis_text}
        
        For each decision, extract:
        1. A unique identifier (e.g., "data-storage-approach")
        2. A category that is specific to this project's domains
        3. The title of the decision
        4. A description of the decision
        5. A COMPREHENSIVE set of options with detailed pros and cons
        6. The recommended option (if any)
        
        CRITICAL REQUIREMENTS:
        
        1. COMPREHENSIVENESS: For each decision, include ALL viable options identified in the research, not just mainstream ones:
           - Include established/traditional approaches
           - Include current mainstream solutions
           - Include cutting-edge/emerging approaches
           - Include unconventional or cross-paradigm options
        
        2. COMPLETENESS: Ensure that every feature and requirement mentioned in the Requirements Analysis 
           section is addressed by at least one decision. Add additional decisions if needed to cover ALL features.
        
        3. PROJECT-SPECIFIC: The decisions and categories must be specifically tailored to THIS project,
           not based on generic web/mobile/software templates.
        
        Format your response as a JSON array of objects. Here's an example structure:
        
        ```json
        [
          {{
            "id": "unique-decision-id",
            "category": "Project-Specific Category",
            "title": "Clear Decision Title",
            "description": "Detailed description of the decision to be made",
            "options": [
              {{
                "name": "Option Name",
                "pros": ["Advantage 1", "Advantage 2", "Advantage 3"],
                "cons": ["Limitation 1", "Limitation 2"]
              }},
              {{
                "name": "Another Option",
                "pros": ["Advantage 1", "Advantage 2"],
                "cons": ["Limitation 1", "Limitation 2", "Limitation 3"]
              }}
            ],
            "recommendation": "Recommended option if there is one"
          }}
        ]
        ```
        
        Only return the JSON array without any additional text or explanation.
        """
        
        # Create a temporary list of messages to avoid affecting the session
        temp_messages = [
            self.system_prompt,
            create_user_prompt(extraction_prompt)
        ]
        
        # Get the agent's response
        response = await send_prompt(temp_messages)
        
        # Parse the JSON response
        try:
            # Extract the JSON object from the response
            import re
            json_match = re.search(r'```json\s*(.*?)\s*```', response.content, re.DOTALL)
            
            if json_match:
                json_text = json_match.group(1)
            else:
                # Try to find json without the code block markers
                json_match = re.search(r'\[\s*\{', response.content)
                if json_match:
                    json_text = response.content[json_match.start():]
                else:
                    logger.error("No JSON found in the response")
                    return []
            
            # Parse the JSON
            decisions_data = json.loads(json_text)
            
            # Convert to ArchitecturalDecision objects
            decisions = []
            for i, decision_data in enumerate(decisions_data):
                decision = ArchitecturalDecision(
                    id=decision_data.get("id", f"decision-{i+1}"),
                    category=decision_data.get("category", "Uncategorized"),
                    title=decision_data.get("title", f"Decision {i+1}"),
                    description=decision_data.get("description", ""),
                    options=decision_data.get("options", []),
                    recommendation=decision_data.get("recommendation"),
                    completed=False
                )
                decisions.append(decision)
            
            return decisions
            
        except Exception as e:
            logger.error(f"Error extracting decisions: {str(e)}")
            return []
    
    @handle_async_errors
    async def get_current_decision(self, session_id: str) -> Optional[ArchitecturalDecision]:
        """
        Get the current architectural decision being discussed.
        
        Args:
            session_id: Identifier of the session
            
        Returns:
            The current architectural decision or None if not available
        """
        # Get the session
        session = self.sessions.get(session_id)
        if not session or session.current_decision_index is None:
            logger.error(f"Session not found or no current decision: {session_id}")
            return None
        
        # Get the current decision
        if 0 <= session.current_decision_index < len(session.decisions):
            return session.decisions[session.current_decision_index]
        else:
            logger.error(f"Current decision index out of bounds: {session.current_decision_index}")
            return None
    
    @handle_async_errors
    async def make_decision(
        self, 
        session_id: str, 
        decision_id: str, 
        selected_option: str, 
        rationale: Optional[str] = None
    ) -> bool:
        """
        Record a decision made by the user.
        
        Args:
            session_id: Identifier of the session
            decision_id: Identifier of the decision
            selected_option: Option selected by the user
            rationale: Rationale for the decision (optional)
            
        Returns:
            True if the decision was recorded, False otherwise
        """
        # Get the session
        session = self.sessions.get(session_id)
        if not session:
            logger.error(f"Session not found: {session_id}")
            return False
        
        # Find the decision
        for i, decision in enumerate(session.decisions):
            if decision.id == decision_id:
                # Record the decision
                decision.decision = selected_option
                decision.rationale = rationale
                decision.completed = True
                
                # Record the decision in the conversation
                decision_message = create_user_prompt(
                    f"For the {decision.title} decision, I choose the '{selected_option}' option." +
                    (f" My rationale is: {rationale}" if rationale else "")
                )
                session.messages.append(decision_message)
                
                # Store this decision in metadata for document creation
                if not hasattr(session, 'metadata') or session.metadata is None:
                    session.metadata = {}
                
                if 'selected_decisions' not in session.metadata:
                    session.metadata['selected_decisions'] = []
                
                # Store full decision details including the selected option
                session.metadata['selected_decisions'].append({
                    'id': decision_id,
                    'title': decision.title,
                    'option': selected_option,
                    'rationale': rationale,
                    'category': decision.category
                })
                
                # Log the selection for verification
                logger.info(f"Decision recorded - ID: {decision_id}, Title: {decision.title}, Selected Option: {selected_option}")
                
                # Get the agent's acknowledgment
                response = await send_prompt(session.messages)
                
                # Add the response to the session
                assistant_message = create_assistant_prompt(response.content)
                session.messages.append(assistant_message)
                
                # If this was the current decision, move to the next one
                if session.current_decision_index == i:
                    # Find the next uncompleted decision
                    next_index = self._find_next_uncompleted_decision(session)
                    session.current_decision_index = next_index
                
                return True
        
        logger.error(f"Decision not found: {decision_id}")
        return False
    
    def _find_next_uncompleted_decision(self, session: ArchitectureSession) -> Optional[int]:
        """
        Find the index of the next uncompleted decision.
        
        Args:
            session: The architecture session
            
        Returns:
            Index of the next uncompleted decision or None if all completed
        """
        for i, decision in enumerate(session.decisions):
            if not decision.completed:
                return i
        
        # All decisions completed
        return None
    
    @handle_async_errors
    async def ask_question(self, session_id: str, question: str) -> Optional[str]:
        """
        Ask a question during the architecture definition process.
        
        Args:
            session_id: Identifier of the session
            question: Question to ask
            
        Returns:
            The agent's response or None if session not found
        """
        # Get the session
        session = self.sessions.get(session_id)
        if not session:
            logger.error(f"Session not found: {session_id}")
            return None
        
        # Create and add the user message
        user_message = create_user_prompt(question)
        session.messages.append(user_message)
        
        # Get the agent's response
        response = await send_prompt(session.messages)
        
        # Add the response to the session
        assistant_message = create_assistant_prompt(response.content)
        session.messages.append(assistant_message)
        
        return response.content
    
    @handle_async_errors
    async def create_document(self, session_id: str) -> Optional[str]:
        """
        Create an architecture document based on the decisions made.
        
        Args:
            session_id: Identifier of the session
            
        Returns:
            The generated document content or None if session not found
        """
        # Get the session
        session = self.sessions.get(session_id)
        if not session:
            logger.error(f"Session not found: {session_id}")
            return None
        
        # Check if all decisions have been made
        all_completed = all(decision.completed for decision in session.decisions)
        if not all_completed:
            logger.warning(f"Not all decisions completed for session: {session_id}")
            # We'll proceed anyway but log a warning
        
        # Update the session state
        session.state = SessionState.DOCUMENT_CREATION
        
        # Get stored user-selected decisions from metadata
        selected_decisions = []
        if hasattr(session, 'metadata') and session.metadata and 'selected_decisions' in session.metadata:
            selected_decisions = session.metadata['selected_decisions']
            logger.info(f"Found {len(selected_decisions)} stored decisions in metadata")
        
        # As a fallback, use the decision objects if metadata isn't available
        if not selected_decisions:
            logger.warning("No stored decisions found in metadata, using fallback")
            completed_decisions = [d for d in session.decisions if d.completed]
            
            for decision in completed_decisions:
                selected_decisions.append({
                    'id': decision.id,
                    'title': decision.title,
                    'category': decision.category,
                    'option': decision.decision,
                    'rationale': decision.rationale or ""
                })
        
        # Get detailed information about each decision and selected option
        decision_details = []
        for selected in selected_decisions:
            # Find the original decision object to get the description and option details
            decision_obj = next((d for d in session.decisions if d.id == selected['id']), None)
            
            if not decision_obj:
                logger.warning(f"Decision object not found for ID: {selected['id']}")
                continue
                
            # Find the details of the chosen option
            option_details = next(
                (opt for opt in decision_obj.options if opt.get("name") == selected['option']), 
                {}
            )
            
            decision_detail = {
                "id": selected['id'],
                "category": selected['category'],
                "title": selected['title'],
                "description": decision_obj.description if decision_obj else "",
                "chosen_option": selected['option'],
                "rationale": selected['rationale'],
                "option_details": option_details
            }
            
            decision_details.append(decision_detail)
            
        # Log the selected options for verification
        for detail in decision_details:
            logger.info(f"Documenting decision: {detail['title']} = {detail['chosen_option']}")
        
        # Group decisions by category for better organization
        decisions_by_category = {}
        for decision in decision_details:
            category = decision["category"]
            if category not in decisions_by_category:
                decisions_by_category[category] = []
            decisions_by_category[category].append(decision)
        
        # Format the structured decisions data
        structured_decisions = "# Selected Architectural Decisions\n\n"
        structured_decisions += "These are the specific implementation approaches we have chosen for each feature:\n\n"
        
        for category, decisions in decisions_by_category.items():
            structured_decisions += f"## {category}\n\n"
            
            for decision in decisions:
                structured_decisions += f"### {decision['title']}\n"
                structured_decisions += f"{decision['description']}\n\n"
                structured_decisions += f"**SELECTED OPTION: {decision['chosen_option']}**\n\n"
                
                if decision['rationale']:
                    structured_decisions += f"**Implementation Rationale**: {decision['rationale']}\n\n"
                
                # Add details about the chosen option
                option = decision['option_details']
                if option:
                    structured_decisions += "**Implementation Characteristics**:\n"
                    
                    if 'pros' in option and option['pros']:
                        structured_decisions += "**Advantages**:\n"
                        for pro in option['pros']:
                            structured_decisions += f"- {pro}\n"
                    
                    if 'cons' in option and option['cons']:
                        structured_decisions += "**Considerations**:\n"
                        for con in option['cons']:
                            structured_decisions += f"- {con}\n"
                
                structured_decisions += "\n"
        
        # Retrieve the requirements analysis if available
        requirements_analysis = ""
        if hasattr(session, 'metadata') and 'requirements_analysis' in session.metadata:
            requirements_analysis = session.metadata['requirements_analysis']
            
        # Create and add the document creation message with rich structured data and requirements
        document_request = create_user_prompt(
            f"""We've completed our architectural discussion and made the following decisions.
I'm providing you with a detailed breakdown of each decision including the category, chosen option,
rationale, and the advantages/considerations of each choice:

{structured_decisions}

At the beginning of our process, we identified these requirements and features that must be fully 
addressed in the architecture:

{requirements_analysis}

Using this detailed information about our architectural decisions and requirements, please create 
a comprehensive architecture document following these guidelines:

{ARCHITECT_DOCUMENT_CREATION_PROMPT}

When creating this document, please:
1. Begin with a complete Functional Requirements section that lists ALL identified features and requirements
2. Incorporate the specific details from our decisions to ensure the architecture is precisely defined
3. Ensure EVERY feature and requirement is addressed somewhere in the architecture
4. Verify that all technical elements (data models, APIs, etc.) properly support the functional requirements

The document must be comprehensive and leave no requirements or features unaddressed.
"""
        )
        document_messages = session.messages + [document_request]
        
        # Get the agent's response
        response = await send_prompt(document_messages)
        
        # Store the document in the session
        session.architecture_document = response.content
        
        # Update the session state
        session.state = SessionState.DOCUMENT_REVIEW
        
        return response.content
    
    @handle_async_errors
    async def revise_document(self, session_id: str, feedback: str) -> Optional[str]:
        """
        Revise the architecture document based on feedback.
        
        Args:
            session_id: Identifier of the session
            feedback: Feedback for the document
            
        Returns:
            The revised document content or None if session not found
        """
        # Get the session
        session = self.sessions.get(session_id)
        if not session:
            logger.error(f"Session not found: {session_id}")
            return None
        
        # Ensure the session is in the correct state
        if session.state != SessionState.DOCUMENT_REVIEW:
            logger.error(f"Session {session_id} not in document review state: {session.state}")
            return None
        
        # Create a specific document revision request
        revision_request = create_user_prompt(
            f"""I need you to revise the architecture document based on this feedback:

{feedback}

Please provide the complete revised document in markdown format. Do not include any other explanations outside of the document content."""
        )
        
        # We need to include the original document creation context
        # Find the original document request and response
        document_creation_index = -1
        for i, msg in enumerate(session.messages):
            if msg.role == "user" and "We've completed our architectural discussion" in msg.content:
                document_creation_index = i
                break
        
        if document_creation_index >= 0:
            # Use the messages up to and including the document creation
            revision_messages = session.messages[:document_creation_index+2] + [revision_request]
        else:
            # If we can't find the original document request, use all messages
            revision_messages = session.messages + [revision_request]
        
        # Get the agent's response
        response = await send_prompt(revision_messages)
        
        # Update the document in the session
        session.architecture_document = response.content
        
        # Add the revision request and response to the session messages
        session.messages.append(revision_request)
        session.messages.append(create_assistant_prompt(response.content))
        
        return response.content
    
    # Methods for the Architect's 2nd pass (foundation selection)
    
    @handle_async_errors
    async def create_generic_architecture_document(self, session_id: str, foundation_approach: Dict[str, Any]) -> Optional[str]:
        """
        Create a generic architecture document based on the selected foundation approach,
        without mentioning any specific technologies.
        
        Args:
            session_id: Session ID
            foundation_approach: Selected foundation approach details
            
        Returns:
            The generated architecture document content
        """
        session = self.sessions.get(session_id)
        if not session:
            logger.error(f"Session {session_id} not found")
            return None
        
        # Get the project vision, PRD, and research report
        project_vision = session.project_vision
        prd_document = session.prd_document
        
        # Load the specific path report for this foundation if available
        path_report = foundation_approach.get("path_report", "")
        foundation_name = foundation_approach.get("name", "Selected Foundation")
        specific_path_report = None
        
        if path_report:
            from ideasfactory.utils.file_manager import load_document_content
            try:
                # Extract the path from the full path including "output/" prefix
                if "path-reports" in path_report:
                    parts = path_report.split("/")
                    path_report_file = parts[-1]
                    specific_path_report = await load_document_content(session_id, "research-report/path-reports/" + path_report_file)
            except Exception as e:
                logger.error(f"Error loading path report: {str(e)}")
                # Continue without the specific path report
                pass
        
        # Get conversation history if this was a user-defined foundation
        conversation_history = []
        is_user_defined = foundation_approach.get("id", "").startswith("user-")
        
        if is_user_defined and "foundation_conversation" in session.metadata:
            conversation_history = session.metadata["foundation_conversation"]
        
        # Create a comprehensive prompt for generating the generic architecture document
        prompt = f"""
        You are creating a comprehensive GENERIC architecture document for a project based on the selected foundation approach.
        This document must detail ALL aspects of the implementation without naming any specific technologies or tech stacks.
        Your focus is on creating an architecture that preserves the unique essence of the project while providing complete
        guidance for the next research phase.

        # Project Vision
        {project_vision}

        # Product Requirements Document (PRD)
        {prd_document}

        # Selected Foundation Approach
        {json.dumps(foundation_approach, indent=2)}

        # Specific Path Report (if available):
        {specific_path_report if specific_path_report else ""}

        # User Foundation Conversation (if available):
        {json.dumps(conversation_history, indent=2) if is_user_defined and conversation_history else ""}

        Your task is to create a COMPREHENSIVE architecture document that:

        1. COMPLETELY captures all aspects needed to implement the project from foundation to user-facing features
        2. Maintains ABSOLUTE TECHNOLOGY NEUTRALITY (no specific technologies, frameworks, libraries, or tech stacks)
        3. Preserves the PROJECT'S UNIQUE CHARACTER throughout the architecture
        4. Addresses ALL functional requirements from the PRD
        5. Provides complete guidance for the next phase of technology research

        The document should include:

        1. Introduction and Background
           - Overview of the project and its core purpose
           - Summary of the selected foundation approach and why it fits the project

        2. Architecture Principles and Goals
           - Core architectural principles driving the design
           - Quality attributes prioritized in this architecture

        3. System Overview
           - High-level architecture diagram (described in text)
           - Key components and their responsibilities
           - System boundaries and external interfaces

        4. Component Architecture
           - Detailed description of each component/module
           - Interfaces and communication patterns
           - Data management approach
           - State management and persistence strategy

        5. Functional Capabilities
           - How each project requirement is addressed by the architecture
           - User interaction flows and behaviors
           - Cross-cutting concerns (security, performance, etc.)

        6. Technical Requirements
           - Clear generic specifications that will drive technology selection
           - Performance requirements
           - Security requirements
           - Scalability and flexibility considerations

        7. Implementation Considerations
           - Development approach
           - Testing strategy
           - Deployment considerations

        8. Areas for Technology Research (CRITICAL SECTION)
           - Specific aspects of the architecture that require technology decisions
           - Categories of technologies to explore for each component
           - Criteria for evaluating technology options

        CRITICAL REQUIREMENT: ABSOLUTELY NO MENTIONS OF SPECIFIC TECHNOLOGIES, FRAMEWORKS, LIBRARIES OR TECH STACKS!
        Instead, describe the TYPES and CHARACTERISTICS of technologies needed. For example:
        - Use a reactive data management system instead of naming specific state management libraries
        - Implement a document-oriented storage system instead of naming specific databases
        - Apply a component-based UI architecture instead of naming specific UI frameworks

        Format the document in Markdown and ensure it provides complete, technology-neutral guidance that enables the next phase of detailed technology research.
        """
        
        # Initialize the session if needed
        if not session.messages:
            session.messages = [self.system_prompt]
        
        # Create the document prompt message
        document_request = create_user_prompt(prompt)
        session.messages.append(document_request)
        
        # Get the agent's response
        response = await send_prompt(session.messages)
        
        # Add the response to the session
        assistant_message = create_assistant_prompt(response.content)
        session.messages.append(assistant_message)
        
        # Store the document in the session
        session.architecture_document = response.content
        
        # Update session state to reflect document creation
        session.state = SessionState.DOCUMENT_REVIEW
        
        # Store the selected foundation in session metadata
        if not hasattr(session, 'metadata') or session.metadata is None:
            session.metadata = {}
            
        session.metadata["selected_foundation"] = foundation_approach
        
        return response.content

    @handle_async_errors
    async def extract_foundation_options(self, session_id: str, research_report: str) -> List[Dict[str, Any]]:
        """
        Extract foundation options from the research report.
        
        Args:
            session_id: Session ID
            research_report: Content of the research report
            
        Returns:
            List of foundation options
        """
        session = self.sessions.get(session_id)
        if not session:
            logger.error(f"Session {session_id} not found")
            return []
        
        # Create a prompt to extract foundation options that preserves the project's unique essence
        prompt = f"""
        Analyze the provided research report for the project and extract all foundation implementation paths. 
        Your task is to identify and extract structured information about each foundation approach described 
        in the research report, maintaining absolute respect for the project's unique character.

        # Research Report
        {research_report}

        For each foundation approach, extract the following information:
        1. Name (unique identifier for the foundation)
        2. Description (concise explanation of the foundation approach)
        3. Key characteristics (what makes this foundation distinctive)
        4. Score or compatibility rating with the project vision (if available)
        5. Primary advantages (key benefits of this approach)
        6. Primary considerations (potential challenges or trade-offs)
        7. Path report reference (path to the detailed report file if available)

        ESSENTIAL REQUIREMENTS:
        - Preserve the EXACT terminology used in the research report
        - Maintain the full diversity of foundation approaches without bias toward conventional solutions
        - Include ALL viable foundation approaches, not just mainstream ones
        - Extract ALL information needed to make an informed decision
        - Preserve what makes each approach unique and distinctive

        Format your response as a JSON array following this structure:
        ```json
        [
          {{
            "id": "foundation-1",
            "name": "Foundation Approach Name",
            "description": "Concise description of the foundation approach",
            "characteristics": ["Key characteristic 1", "Key characteristic 2", "Key characteristic 3"],
            "compatibility_score": 85,  // 0-100 score if available or calculated from report data
            "advantages": ["Primary advantage 1", "Primary advantage 2"],
            "considerations": ["Consideration 1", "Consideration 2"],
            "path_report": "path/to/report-file.md" // If available
          }},
          // Additional foundation approaches...
        ]
        ```

        Only return the JSON array without any additional text or explanation.
        """
        
        # Create messages for extraction
        extraction_messages = [
            self.system_prompt,
            create_user_prompt(prompt)
        ]
        
        # Get extraction response
        response = await send_prompt(extraction_messages)
        
        # Parse the JSON response
        try:
            import re
            import json
            
            # Look for JSON in the response
            json_match = re.search(r'```json\s*(.*?)\s*```', response.content, re.DOTALL)
            if not json_match:
                json_match = re.search(r'(\[\s*\{.*\}\s*\])', response.content, re.DOTALL)
            
            if json_match:
                json_str = json_match.group(1)
                foundations = json.loads(json_str)
                
                # Store in session for future use
                if not hasattr(session, 'metadata') or session.metadata is None:
                    session.metadata = {}
                    
                session.metadata["foundation_options"] = foundations
                
                # Log the number of extracted options
                logger.info(f"Extracted {len(foundations)} foundation options from research report")
                
                return foundations
            else:
                logger.error("Failed to extract JSON from response")
                return []
        
        except Exception as e:
            logger.error(f"Error parsing foundation options: {str(e)}")
            return []

    @handle_async_errors
    async def get_foundation_details(self, session_id: str, foundation_name: str, question: str) -> str:
        """
        Get more details about a specific foundation based on a user question.
        
        Args:
            session_id: Session ID
            foundation_name: Name of the foundation to get details for
            question: User's question about the foundation
            
        Returns:
            Detailed response about the foundation
        """
        session = self.sessions.get(session_id)
        if not session:
            logger.error(f"Session {session_id} not found")
            return "I'm sorry, but I couldn't find your session information. Please try again later."
        
        # First check if foundation exists in session metadata
        foundation_options = session.metadata.get("foundation_options", [])
        selected_foundation = next(
            (f for f in foundation_options if f.get("name") == foundation_name), 
            None
        )
        
        if not selected_foundation:
            logger.warning(f"Foundation '{foundation_name}' not found in session metadata")
            # Try to load the research report to answer anyway
            research_report = None
            if hasattr(session, 'research_report') and session.research_report:
                research_report = session.research_report
        else:
            # Try to load the specific path report if available
            path_report = selected_foundation.get("path_report", "")
            from ideasfactory.utils.file_manager import load_document_content
            
            try:
                # Use DocumentManager to find path reports related to the foundation
                from ideasfactory.documents.document_manager import DocumentManager
                doc_manager = DocumentManager()
                
                try:
                    # First, try to find path reports that match the foundation name
                    path_reports_dir = "research-report/path-reports"
                    path_report_docs = doc_manager.list_documents(
                        document_type=path_reports_dir,
                        session_id=session_id
                    )
                    
                    # Find a report that matches this foundation (case insensitive)
                    foundation_key = foundation_name.lower()
                    matching_docs = []
                    
                    for doc in path_report_docs:
                        # Try to match based on the document title or filename
                        doc_title = doc.get("title", "").lower()
                        doc_filename = doc.get("filename", "").lower()
                        
                        # Check for matches in title or filename
                        if (foundation_key in doc_title or 
                            foundation_key in doc_filename or
                            any(term in doc_title for term in foundation_key.split()) or
                            any(term in doc_filename for term in foundation_key.split())):
                            matching_docs.append(doc)
                    
                    if matching_docs:
                        # Use the first matching document
                        logger.info(f"Found matching path report: {matching_docs[0].get('filepath')}")
                        
                        # Load the document content
                        if "content" in matching_docs[0]:
                            research_report = matching_docs[0]["content"]
                        elif "filepath" in matching_docs[0]:
                            doc_content = doc_manager.get_document(matching_docs[0]["filepath"])
                            if doc_content and "content" in doc_content:
                                research_report = doc_content["content"]
                            else:
                                logger.warning(f"Could not extract content from matching document")
                                research_report = session.research_report
                    else:
                        logger.warning(f"No matching path report found for '{foundation_name}'")
                        research_report = session.research_report
                except Exception as e:
                    logger.error(f"Error finding path report: {str(e)}")
                    research_report = session.research_report
            except Exception as e:
                logger.error(f"Error loading path report: {str(e)}")
                research_report = session.research_report
        
        # Create the prompt to answer the user's question
        prompt = f"""
        You are having a conversation with a user about the foundation approach named "{foundation_name}" for their project.
        The user is asking: "{question}"
        
        Based on the project details and research information, provide a thorough, accurate response that helps the user 
        understand this foundation approach and make an informed decision.
        
        # Project Vision
        {session.project_vision}
        
        # Product Requirements Document
        {session.prd_document}
        
        # Research Report
        {research_report}
        
        # Foundation Details
        {json.dumps(selected_foundation, indent=2) if selected_foundation else "Foundation details not available"}
        
        Your response should:
        1. Directly answer the user's question with specific details
        2. Provide relevant context from the research
        3. Highlight how this foundation approach aligns with the project's unique vision
        4. Present balanced information without bias toward this approach
        5. Include advantages, considerations, and other factors relevant to the question
        
        Answer in a conversational yet informative tone, focusing on what's most relevant to the user's question.
        """
        
        # Create temporary messages for this interaction
        interaction_messages = [
            self.system_prompt,
            create_user_prompt(prompt)
        ]
        
        # Get the response
        response = await send_prompt(interaction_messages)
        
        return response.content
    
    @handle_async_errors
    async def refine_user_foundation(self, session_id: str, foundation_id: str, user_response: str) -> str:
        """
        Refine the user-defined foundation based on their responses to questions.
        
        Args:
            session_id: Session ID
            foundation_id: ID of the foundation being refined
            user_response: User's response to questions
            
        Returns:
            Next response in the conversation to further refine the foundation
        """
        session = self.sessions.get(session_id)
        if not session:
            logger.error(f"Session {session_id} not found")
            return "I'm sorry, but I couldn't find your session information. Please try again later."
        
        # Get the current user foundation from metadata
        user_foundation = session.metadata.get("user_foundation", {})
        conversation_history = session.metadata.get("foundation_conversation", [])
        
        # Add this exchange to the conversation history
        if not "foundation_conversation" in session.metadata:
            session.metadata["foundation_conversation"] = []
            
        session.metadata["foundation_conversation"].append({
            "user": user_response
        })
        
        # Create the prompt to continue the conversation
        prompt = f"""
        You are having a conversation with a user to refine their custom foundation approach for their project.
        The user has provided more details in response to your previous questions.
        
        # Project Vision
        {session.project_vision}
        
        # Product Requirements Document
        {session.prd_document}
        
        # Current Understanding of User's Foundation Approach
        {json.dumps(user_foundation, indent=2)}
        
        # User's Latest Response
        {user_response}
        
        Your task is to:
        1. Analyze the user's response and extract any new information about their foundation approach
        2. Update your understanding of their approach based on this new information
        3. Identify what aspects of the foundation are still unclear or need elaboration
        4. Continue the conversation with follow-up questions or a summary
        
        When generating your response:
        - Acknowledge the information the user has provided
        - Update your mental model of their foundation approach
        - Either ask focused follow-up questions about remaining unclear aspects
        - OR if you have a complete picture, provide a summary of your understanding
        
        If you believe you have a complete understanding of the user's foundation approach, include a JSON object with the updated foundation details in a code block that won't be shown to the user:
        
        <foundation_update>
        {{
          "complete": true,
          "foundation": {{
            // Updated foundation details
          }}
        }}
        </foundation_update>
        
        If you still need more information, include what aspects are still missing:
        
        <foundation_update>
        {{
          "complete": false,
          "foundation": {{
            // Updated foundation details with what you know so far
          }},
          "missing_aspects": [
            "Aspect 1 that still needs clarification",
            "Aspect 2 that still needs clarification"
          ]
        }}
        </foundation_update>
        """
        
        # Create temporary messages for this interaction
        interaction_messages = [
            self.system_prompt,
            create_user_prompt(prompt)
        ]
        
        # Get the response
        response = await send_prompt(interaction_messages)
        response_content = response.content
        
        # Process the foundation update if included
        import re
        foundation_update_match = re.search(r'<foundation_update>(.*?)</foundation_update>', response_content, re.DOTALL)
        
        if foundation_update_match:
            try:
                update_json = foundation_update_match.group(1).strip()
                update_data = json.loads(update_json)
                
                # Update the foundation in session metadata
                if "foundation" in update_data:
                    session.metadata["user_foundation"] = update_data["foundation"]
                
                # Check if the foundation definition is complete
                if update_data.get("complete", False):
                    session.metadata["foundation_complete"] = True
                else:
                    session.metadata["foundation_complete"] = False
                    
                # Store missing aspects if any
                if "missing_aspects" in update_data:
                    session.metadata["foundation_missing_aspects"] = update_data["missing_aspects"]
                
                # Remove the hidden update from the user-visible response
                response_content = re.sub(r'<foundation_update>.*?</foundation_update>', '', response_content, flags=re.DOTALL).strip()
            except Exception as e:
                logger.error(f"Error processing foundation update: {str(e)}")
        
        # Add the assistant's response to conversation history
        session.metadata["foundation_conversation"].append({
            "assistant": response_content
        })
        
        return response_content

    @handle_async_errors
    async def process_user_foundation(self, session_id: str, foundation_description: str) -> Dict[str, Any]:
        """
        Process a user-specified foundation approach.
        
        Args:
            session_id: Session ID
            foundation_description: User's description of their foundation approach
            
        Returns:
            Processed foundation data with questions for refinement
        """
        session = self.sessions.get(session_id)
        if not session:
            logger.error(f"Session {session_id} not found")
            return {"status": "error", "message": "Session not found"}
        
        # Get the project vision and PRD from the session
        project_vision = session.project_vision
        prd_document = session.prd_document
        
        # Create a prompt to process the user's foundation while preserving uniqueness
        prompt = f"""
        You are helping structure a user-defined foundation approach for a project.
        Analyze this foundation description and extract structured information while 
        identifying areas that need further clarification to ensure comprehensive architecture design.

        # Project Vision
        {project_vision}

        # Product Requirements Document
        {prd_document}

        # User-Defined Foundation Approach
        {foundation_description}

        Your task is to:
        1. Extract and structure the information about this foundation approach
        2. Identify specific areas that need further clarification or elaboration
        3. Generate targeted questions to help refine the foundation approach

        Create a JSON response that:
        - Preserves the unique character and specific terminology of the user's description
        - Does not impose conventional patterns or assumptions
        - Identifies the actual information provided and what's missing
        - Generates questions that help define implementation aspects without biasing toward particular technologies

        CRITICAL: Your questions should EXPLORE the foundation further, not DIRECT it toward any specific implementation.

        Structure your response as a JSON object following this format:
        ```json
        {{
          "foundation": {{
            "id": "user-defined",
            "name": "User-Defined Foundation Name", // Extract from description or provide suitable name
            "description": "Structured description based on user input",
            "characteristics": ["Identified characteristic 1", "Identified characteristic 2"],
            "challenges": ["Potential challenge 1", "Potential challenge 2"],
            "components": ["Component 1", "Component 2"] // Components mentioned explicitly in the description
          }},
          "questions": [
            "Question about aspect 1 that needs clarification?",
            "Question about aspect 2 that needs clarification?"
          ],
          "missing_elements": [
            "Element 1 that needs to be defined for a complete foundation",
            "Element 2 that needs to be defined for a complete foundation"
          ]
        }}
        ```

        Only return the JSON object without any additional text or explanation.
        """
        
        # Create messages for processing
        processing_messages = [
            self.system_prompt,
            create_user_prompt(prompt)
        ]
        
        # Get processing response
        response = await send_prompt(processing_messages)
        
        # Parse the JSON response
        try:
            import re
            import json
            
            # Look for JSON in the response
            json_match = re.search(r'```json\s*(.*?)\s*```', response.content, re.DOTALL)
            if not json_match:
                json_match = re.search(r'(\{.*\})', response.content, re.DOTALL)
            
            if json_match:
                json_str = json_match.group(1)
                result = json.loads(json_str)
                
                # Format the questions as a single string including both questions and missing elements
                questions_list = result.get("questions", [])
                missing_elements = result.get("missing_elements", [])
                
                # Create a comprehensive list of questions
                all_questions = questions_list[:]
                for element in missing_elements:
                    all_questions.append(f"Could you elaborate on {element}?")
                
                questions = "\n".join([f"{i+1}. {q}" for i, q in enumerate(all_questions)])
                
                # Store in session for future use
                if not hasattr(session, 'metadata') or session.metadata is None:
                    session.metadata = {}
                    
                if "user_foundation" not in session.metadata:
                    session.metadata["user_foundation"] = result.get("foundation", {})
                
                # Return the processed data
                return {
                    "status": "success",
                    "foundation": result.get("foundation", {}),
                    "questions": questions
                }
            else:
                logger.error("Failed to extract JSON from response")
                return {"status": "error", "message": "Failed to process foundation"}
        
        except Exception as e:
            logger.error(f"Error processing user foundation: {str(e)}")
            return {"status": "error", "message": f"Error: {str(e)}"}