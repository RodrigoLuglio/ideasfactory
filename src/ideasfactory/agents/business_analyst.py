# In ideasfactory/agents/business_analyst.py
"""
Business Analyst agent for IdeasFactory.

This module implements the Business Analyst agent that conducts brainstorming
sessions and produces vision documents.
"""

import logging
from typing import List, Dict, Any, Optional
from enum import Enum
import asyncio

from pydantic import BaseModel, Field

from ideasfactory.utils.llm_utils import (
    Message, send_prompt, create_system_prompt, create_user_prompt,
    create_assistant_prompt, BA_SYSTEM_PROMPT, BA_DOCUMENT_CREATION_PROMPT
)

# Configure logging
logger = logging.getLogger(__name__)


class SessionState(Enum):
    """State of the brainstorming session."""
    STARTED = "started"
    BRAINSTORMING = "brainstorming"
    DOCUMENT_CREATION = "document_creation"
    DOCUMENT_REVIEW = "document_review"
    COMPLETED = "completed"


class Suggestion(BaseModel):
    """A suggestion made during the brainstorming session."""
    content: str = Field(..., description="Content of the suggestion")
    accepted: bool = Field(False, description="Whether the suggestion was accepted")

class Feature(BaseModel):
    """A feature discussed during the brainstorming session."""
    name: str = Field(..., description="Name of the feature")
    description: str = Field(..., description="Description of the feature")
    accepted: bool = Field(False, description="Whether the feature was accepted")

class BrainstormSession(BaseModel):
    """A brainstorming session with the Business Analyst."""
    id: str = Field(..., description="Unique identifier for the session")
    topic: str = Field(..., description="Topic of the brainstorming session")
    messages: List[Message] = Field(default_factory=list, description="Messages in the session")
    suggestions: List[Suggestion] = Field(default_factory=list, description="Suggestions made during the session")
    state: SessionState = Field(default=SessionState.STARTED, description="Current state of the session")
    document: Optional[str] = Field(None, description="Generated document content")
    
    class Config:
        """Pydantic model configuration."""
        arbitrary_types_allowed = True


class BusinessAnalyst:
    """
    Business Analyst agent that conducts brainstorming sessions and produces vision documents.
    
    Implemented as a singleton to ensure the same instance is shared across the application.
    """
    
    _instance = None
    
    def __new__(cls):
        """Ensure only one instance of BusinessAnalyst is created."""
        if cls._instance is None:
            cls._instance = super(BusinessAnalyst, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the Business Analyst agent."""
        if not hasattr(self, '_initialized') or not self._initialized:
            self.sessions: Dict[str, BrainstormSession] = {}
            self.system_prompt = create_system_prompt(BA_SYSTEM_PROMPT)
            self._initialized = True
    
    async def create_session(self, session_id: str, topic: str) -> BrainstormSession:
        """
        Create a new brainstorming session.
        
        Args:
            session_id: Unique identifier for the session
            topic: Topic of the brainstorming session
            
        Returns:
            The created brainstorming session
        """
        # Create a new session
        session = BrainstormSession(
            id=session_id,
            topic=topic,
            messages=[self.system_prompt],
            state=SessionState.STARTED
        )
        
        # Store the session
        self.sessions[session_id] = session
        
        return session
    
    async def start_brainstorming(self, session_id: str) -> Optional[str]:
        """
        Start the brainstorming session.
        
        Args:
            session_id: Identifier of the session to start
            
        Returns:
            The agent's initial response or None if session not found
        """
        # Get the session
        session = self.sessions.get(session_id)
        if not session:
            logger.error(f"Session not found: {session_id}")
            return None
        
        # Update the session state
        session.state = SessionState.BRAINSTORMING
        
        # Create the initial message
        initial_message = create_user_prompt(
            f"I want to brainstorm about this idea: {session.topic}. Help me refine this idea into a concrete project."
        )
        session.messages.append(initial_message)
        
        # Get the agent's response
        response = await send_prompt(session.messages)
        
        # Add the response to the session
        assistant_message = create_assistant_prompt(response.content)
        session.messages.append(assistant_message)
        
        return response.content
    
    async def send_message(self, session_id: str, content: str) -> Optional[str]:
        """
        Send a message to the agent during a brainstorming session.
        
        Args:
            session_id: Identifier of the session
            content: Content of the message
            
        Returns:
            The agent's response or None if session not found
        """
        # Get the session
        session = self.sessions.get(session_id)
        if not session:
            logger.error(f"Session not found: {session_id}")
            return None
        
        # Ensure the session is in the correct state
        if session.state != SessionState.BRAINSTORMING:
            logger.error(f"Session {session_id} not in brainstorming state: {session.state}")
            return None
        
        # Create and add the user message
        user_message = create_user_prompt(content)
        session.messages.append(user_message)
        
        # Get the agent's response
        response = await send_prompt(session.messages)
        
        # Add the response to the session
        assistant_message = create_assistant_prompt(response.content)
        session.messages.append(assistant_message)
        
        # TODO: Parse the response to identify suggestions
        # This would involve some NLP to identify suggestions in the response
        
        return response.content
    
    async def create_document(self, session_id: str) -> Optional[str]:
        """
        Create a document based on the brainstorming session.
        
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
        
        # Update the session state
        session.state = SessionState.DOCUMENT_CREATION
        
        # Create and add the document creation message
        document_request = create_user_prompt(BA_DOCUMENT_CREATION_PROMPT)
        document_messages = session.messages + [document_request]
        
        # Get the agent's response
        response = await send_prompt(document_messages)
        
        # Store the document in the session
        session.document = response.content
        
        # Update the session state
        session.state = SessionState.DOCUMENT_REVIEW
        
        return response.content
    
    async def revise_document(self, session_id: str, feedback: str) -> Optional[str]:
        """
        Revise the document based on feedback.
        
        Args:
            session_id: Identifier of the session
            feedback: Feedback on the document
            
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
        
        # Create the revision message
        revision_request = create_user_prompt(
            f"Please revise the document based on this feedback: {feedback}"
        )
        document_messages = session.messages + [revision_request]
        
        # Get the agent's response
        response = await send_prompt(document_messages)
        
        # Update the document in the session
        session.document = response.content
        
        return response.content
    
    async def complete_session(self, session_id: str) -> bool:
        """
        Complete the brainstorming session.
        
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