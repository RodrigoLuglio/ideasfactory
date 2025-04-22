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

# Configure logging
logger = logging.getLogger(__name__)

# Architect system prompt
ARCHITECT_SYSTEM_PROMPT = """
You are a senior solution architect with strong background in technology and innovation. 

Your role is to define the architecture of a project based on the information provided by the Business Analyst and Project Manager. You will identify all the requirements and define the architecture of the project, including, but not limited to:

- Tech stack definition
- Project structure
- Types of applications needed (web, mobile, desktop, etc.)
- Database definition and schemas
- Data models
- Security requirements
- Infrastructure
- Deployment strategy
- Any other relevant information needed for the implementation

As each project is unique, you won't follow a fixed structure. Instead, you will define the best structure, topics, and requirements that each different project might need. 

You will help the user make informed decisions by:
1. Presenting options with clear pros and cons
2. Explaining the implications of each decision
3. Providing recommendations based on the project requirements
4. Guiding the user through each architectural decision in a conversational manner

Once the user makes the decisions, you will document all the architectural decisions in a comprehensive markdown document containing all the necessary details to precisely describe the project from start to end, including all information needed for implementation.

You always make sure that everything is decided and the documents have everything in place so that when handled to the development agents, they have every detail needed to implement the project.
"""

ARCHITECT_ANALYSIS_PROMPT = """
Please analyze the project vision document and research report provided, then identify the key architectural decisions that need to be made.

For each decision point, provide:
1. The decision that needs to be made
2. 2-4 viable options with pros and cons
3. Your recommendation with rationale

Format your response as a structured list of decision points that we'll discuss one by one. Include high-level categories such as:

- Overall architecture approach
- Frontend technology
- Backend technology
- Database selection
- Authentication & security approach
- Deployment & infrastructure

Focus on the most important decisions first. We'll go through each decision point in our conversation.
"""

ARCHITECT_DOCUMENT_CREATION_PROMPT = """
Based on our architectural discussion, please create a comprehensive architecture document in markdown format.

The document should:
- Contain all the architectural decisions we've made
- Include detailed technical specifications
- Cover all aspects of the solution architecture
- Provide clear guidance for implementation
- Include diagrams and models as textual descriptions (these will be converted to visual diagrams later)
- Be written in a markdown format
- Be structured in a way that makes sense for this specific project

Include all these sections (and others if relevant to this project):

# [Project Name] - Architecture Document

## Overview
[Brief description of the architectural approach]

## System Architecture
[High-level architecture description]

## Technology Stack
[Detailed list of technologies for each component]

## Component Breakdown
[Description of each system component]

## Data Model
[Database schema and data structures]

## Security Architecture
[Security measures and implementations]

## Integration Points
[APIs, third-party services, etc.]

## Deployment Architecture
[Infrastructure and deployment strategy]

## Development Guidelines
[Coding standards, patterns, and practices]

## Non-Functional Requirements
[Performance, scalability, etc.]
"""


class SessionState(Enum):
    """State of the architecture definition session."""
    STARTED = "started"
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
    research_report: str = Field(..., description="Research report content")
    messages: List[Message] = Field(default_factory=list, description="Messages in the session")
    decisions: List[ArchitecturalDecision] = Field(default_factory=list, description="Architectural decisions to be made")
    current_decision_index: Optional[int] = Field(None, description="Index of the current decision being discussed")
    state: SessionState = Field(default=SessionState.STARTED, description="Current state of the session")
    architecture_document: Optional[str] = Field(None, description="Generated architecture document content")
    
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
        research_report: str
    ) -> ArchitectureSession:
        """
        Create a new architecture definition session.
        
        Args:
            session_id: Unique identifier for the session
            project_vision: Project vision document content
            research_report: Research report content
            
        Returns:
            The created architecture session
        """
        # Create a new session
        session = ArchitectureSession(
            id=session_id,
            project_vision=project_vision,
            research_report=research_report,
            messages=[self.system_prompt],
            state=SessionState.STARTED
        )
        
        # Store the session
        self.sessions[session_id] = session
        
        return session

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
    
    @handle_async_errorss
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
        
        # Create a prompt to extract decisions
        extraction_prompt = f"""
        Based on the analysis below, extract a structured list of architectural decisions that need to be made.
        
        Analysis:
        {analysis_text}
        
        For each decision, extract:
        1. A unique identifier (e.g., "frontend-framework")
        2. The category (e.g., "Frontend", "Backend", "Database")
        3. The title of the decision
        4. A description of the decision
        5. The options with pros and cons
        6. The recommended option (if any)
        
        Format your response as a JSON array of objects. Here's an example structure:
        
        ```json
        [
          {{
            "id": "frontend-framework",
            "category": "Frontend",
            "title": "Frontend Framework Selection",
            "description": "Choose the main frontend framework for the application",
            "options": [
              {{
                "name": "React",
                "pros": ["Large ecosystem", "Flexible", "Well-established"],
                "cons": ["Requires additional libraries for routing, state management"]
              }},
              {{
                "name": "Angular",
                "pros": ["Comprehensive solution", "Strong typing with TypeScript"],
                "cons": ["Steeper learning curve", "More opinionated"]
              }}
            ],
            "recommendation": "React"
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
        
        # Create a summary of the decisions made
        decisions_summary = "\n\n".join([
            f"## {decision.title}\n" +
            f"**Decision**: {decision.decision}\n" +
            (f"**Rationale**: {decision.rationale}\n" if decision.rationale else "")
            for decision in session.decisions
            if decision.completed
        ])
        
        # Create and add the document creation message
        document_request = create_user_prompt(
            f"""We've completed our architectural discussion and made the following decisions:

{decisions_summary}

{ARCHITECT_DOCUMENT_CREATION_PROMPT}"""
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