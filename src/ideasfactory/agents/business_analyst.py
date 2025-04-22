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
    create_assistant_prompt
)

from ideasfactory.utils.error_handler import handle_errors, handle_async_errors

# Configure logging
logger = logging.getLogger(__name__)

# Business Analyst system prompt
BA_SYSTEM_PROMPT = """
You are a business analyst passionate about technology and innovation. Your role is to help shape ideas, 
as vague as they could be, into a clear and detailed scope for a solution, project or service that the initial idea might turn into.

You do this by conducting a brainstorm session with the user. 

In the brainstorm session you:

- help the user to transform the idea into feasible, actionable and structured features
- may suggest features and improvements to the user's idea, one at a time naturally, in a conversational way
- can ask questions, one at a time, in opportune momments to:
    - gather more information 
    - clarify any doubts 
    - help refine the idea
- keep account of the user's acceptance of both your suggestions and the different features you are discussing
- DON'T directly ask the user answer a list of questions, but rather try to gather the information you need to create the scope document during the brainstorm session

By the end of the session, you must have a clear scope with all the necessary details to precisely describe 
the solution/project/service, including all the accepted suggestions you made and the features you discussed, that "was born", during the brainstorm session, from the user idea to write a project vision document in markdown.
"""

BA_DOCUMENT_CREATION_PROMPT = """
Based on our brainstorming session, please create a comprehensive project vision document in markdown format.

The document should:
- contain all the necessary details to precisely describe the solution/product/service
- contain all features, improvements, suggestions we agreed upon during the brainstorm session
- NOT contain any information, feature, suggestion or improvement that was not agreed upon
- NOT contain any invented information, feature, suggestion or improvement or that was not discussed
- be clear, detailed and precise, describing the solution/product/service with ALL and ONLY the information
    that was discussed and agreed upon during the brainstorm session
- be written in a markdown format

Here's a general structure you can follow, but adapt it as needed:

# [Project Name]

## Overview
[A brief description of the project]

## Problem Statement
[The problem the project aims to solve]

## Solution Description
[Detailed description of the proposed solution]

## Features
[List of features with descriptions]

## Technical Requirements
[Any technical requirements or constraints discussed]

## Next Steps
[Potential next steps for the project]
"""


class SessionState(Enum):
    """State of the brainstorming session."""
    STARTED = "started"
    BRAINSTORMING = "brainstorming"
    DOCUMENT_CREATION = "document_creation"
    DOCUMENT_REVIEW = "document_review"
    COMPLETED = "completed"


class Suggestion(BaseModel):
    """A suggestion made by the agent during the brainstorming session."""
    content: str = Field(..., description="Content of the suggestion")
    accepted: bool = Field(False, description="Whether the suggestion was accepted")

class Feature(BaseModel):
    """A feature discussed by both the agent and the user during the brainstorming session."""
    name: str = Field(..., description="Name of the feature")
    description: str = Field(..., description="Description of the feature")
    accepted: bool = Field(False, description="Whether the feature was accepted")

class BrainstormSession(BaseModel):
    """A brainstorming session with the Business Analyst."""
    id: str = Field(..., description="Unique identifier for the session")
    topic: str = Field(..., description="Topic of the brainstorming session")
    messages: List[Message] = Field(default_factory=list, description="Messages in the session")
    suggestions: List[Suggestion] = Field(default_factory=list, description="Suggestions made during the session")
    features: List[Feature] = Field(default_factory=list, description="Features discussed during the session")
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
    
    @handle_async_errors
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
    
    @handle_async_errors
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
    
    @handle_async_errors
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
    
    @handle_async_errors
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
    
    @handle_async_errors
    async def revise_document(self, session_id: str, feedback: str) -> Optional[str]:
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
            f"""I need you to revise the document that was created based on our brainstorming session.

    Here is the feedback: 
    {feedback}

    Please provide ONLY the complete revised document in markdown format. Do not include any other explanations or conversation outside of the document content. Just the revised document text."""
        )
        
        # We need to include the original document creation context
        # First find the original document in the messages
        document_messages = []
        document_found = False
        
        for msg in session.messages:
            document_messages.append(msg)
            # If we reach the document creation request, we'll include it
            if msg.role == "user" and "create a comprehensive project vision document" in msg.content:
                document_found = True
        
        # If we didn't find the document creation message, use a different approach
        if not document_found:
            # Create a temporary message that includes the current document
            document_content_msg = create_assistant_prompt(session.document)
            document_messages.append(document_content_msg)
        
        # Add the revision request
        document_messages.append(revision_request)
        
        # Get the agent's response
        response = await send_prompt(document_messages)
        
        # Update the document in the session
        session.document = response.content
        
        return response.content
    
    @handle_async_errors
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