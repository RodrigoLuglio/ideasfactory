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

# Make enhanced tools available to the business analyst
from ideasfactory.tools.enhanced_web_search import (
    search_custom,
    fetch_full_page,
    search_and_fetch,
)
from ideasfactory.tools.enhanced_data_analysis import (
    extract_text_features,
)
from ideasfactory.tools.research_visualization import (
    create_ascii_table,
    create_timeline,
)

# Configure logging
logger = logging.getLogger(__name__)

# Business Analyst system prompt
BA_SYSTEM_PROMPT = """
You are a business analyst passionate about technology and innovation. Your role is to help transform initial ideas, no matter how vague, into a clear and detailed scope that captures the UNIQUE essence of each specific solution, project, or service.

You approach each idea as inherently novel and avoid applying generic templates or conventional thinking. Instead, you help uncover what makes THIS PARTICULAR idea special and different.

During the brainstorming session you:

- Help the user transform their unique idea into feasible, actionable, and structured features
- Listen attentively to recognize the distinctive aspects of the user's vision
- Suggest innovative features and improvements that align with the user's specific vision, one at a time in a conversational way
- Ask thoughtful questions, one at a time, at opportune moments to:
    - Discover the unique aspects that make this idea different from existing solutions
    - Clarify ambiguities while preserving the innovative spirit of the idea
    - Understand the essence of what the user wants to achieve
    - Help refine the idea without forcing it into conventional molds
- Maintain a record of the user's acceptance of both your suggestions and the features you're discussing
- DON'T directly ask the user to answer a list of questions, but rather engage in a natural conversation

By the end of the session, you must have captured a clear scope with all the necessary details to precisely describe 
the unique solution/project/service that emerged during your conversation. Your documentation should preserve both the 
practical implementation details AND the distinctive vision that makes this idea special.

Remember: Every idea is unique. Your job is to help the user articulate THEIR vision, not to fit their idea into existing patterns or templates.
"""

BA_DOCUMENT_CREATION_PROMPT = """
Based on our brainstorming session, please create a comprehensive project vision document in markdown format.

The document should:
- Contain all the necessary details to precisely describe the unique solution/product/service we discussed
- Include all features, improvements, and suggestions we agreed upon during the brainstorm session
- NOT contain any information, feature, suggestion or improvement that was not agreed upon
- NOT contain any invented information, feature, suggestion or improvement that was not discussed
- Be clear, detailed and precise, describing the solution with ALL and ONLY the information
  that was discussed and agreed upon during the brainstorm session
- Be written in markdown format
- Have a structure that is COMPLETELY TAILORED to this specific project's unique needs

VERY IMPORTANT:
- Do NOT follow a generic template structure
- Create a document structure that perfectly captures THIS SPECIFIC PROJECT'S unique nature
- Organize information in the way that best communicates this particular idea's essence
- Include ALL agreed features with detailed descriptions that specify precisely how they should work

The section headings and organization should reflect what makes this specific project unique. For example:
- A data-focused project might emphasize data flows and integration points
- A user-centric application might focus on user journeys and interaction patterns
- A technical tool might highlight capabilities and integration opportunities

Be particularly careful to:
1. FULLY describe each feature with its expected behavior
2. Capture any unique aspects, novel approaches, or differentiators discussed
3. Clearly articulate the project's scope boundaries (what it does and does not do)
4. Preserve the excitement and vision behind the original idea while making it actionable

Remember: This document will be the foundation for ALL future work on this project, so ensure nothing is missed or left ambiguous.
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
        
        # Extract suggestions and features from the response
        await self._extract_suggestions_and_features(session_id, content, response.content)
        
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
        
        # Create a summary of the structured data in the session
        accepted_suggestions = [s.content for s in session.suggestions if s.accepted]
        accepted_features = [f for f in session.features if f.accepted]
        
        # Format the structured data as a summary
        structured_data_summary = ""
        
        if accepted_suggestions:
            structured_data_summary += "## Accepted Suggestions\n"
            for suggestion in accepted_suggestions:
                structured_data_summary += f"- {suggestion}\n"
            structured_data_summary += "\n"
        
        if accepted_features:
            structured_data_summary += "## Accepted Features\n"
            for feature in accepted_features:
                structured_data_summary += f"### {feature.name}\n"
                structured_data_summary += f"{feature.description}\n\n"
        
        # Create an enhanced document creation prompt with the structured data
        enhanced_prompt = f"""
{BA_DOCUMENT_CREATION_PROMPT}

Based on our brainstorming session, I've identified these key elements that we agreed upon:

{structured_data_summary}

Please use these specific agreed upon suggestions and features as the foundation for the document, 
in addition to any other valuable insights from our conversation.
"""
        
        # Create and add the document creation message
        document_request = create_user_prompt(enhanced_prompt)
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
    async def _extract_suggestions_and_features(self, session_id: str, user_message: str, assistant_response: str) -> None:
        """
        Extract suggestions and features from the assistant's response.
        
        Args:
            session_id: Identifier of the session
            user_message: User's message
            assistant_response: Assistant's response to analyze
            
        Returns:
            None
        """
        # Get the session
        session = self.sessions.get(session_id)
        if not session:
            logger.error(f"Session not found: {session_id}")
            return
        
        # Create a prompt to identify suggestions and features
        analysis_prompt = f"""
        Please analyze this conversation fragment from a brainstorming session to identify:
        
        1. Suggestions: Ideas or improvements proposed by the assistant
        2. Features: Product/service features mentioned or discussed by either party
        
        User message: {user_message}
        
        Assistant response: {assistant_response}
        
        For each suggestion:
        - Extract the specific suggestion text
        - Determine if it was accepted or not based on the conversation
        
        For each feature:
        - Extract the feature name
        - Extract a brief description
        - Determine if it was accepted or not based on the conversation
        
        Format your response as JSON with two arrays:
        
        ```json
        {{
          "suggestions": [
            {{
              "content": "specific suggestion text",
              "accepted": true/false
            }}
          ],
          "features": [
            {{
              "name": "feature name",
              "description": "feature description",
              "accepted": true/false
            }}
          ]
        }}
        ```
        
        Only return the JSON object without any additional text.
        """
        
        # Create a temporary list of messages to avoid affecting the session
        temp_messages = [
            self.system_prompt,
            create_user_prompt(analysis_prompt)
        ]
        
        # Get the agent's response
        try:
            response = await send_prompt(temp_messages)
            
            # Extract the JSON object from the response
            import re
            import json
            
            json_match = re.search(r'```json\s*(.*?)\s*```', response.content, re.DOTALL)
            
            if json_match:
                json_text = json_match.group(1)
            else:
                # Try to find json without the code block markers
                json_match = re.search(r'\{\s*"suggestions"', response.content)
                if json_match:
                    json_text = response.content[json_match.start():]
                else:
                    logger.error("No JSON found in the response")
                    return
            
            # Parse the JSON
            extracted_data = json.loads(json_text)
            
            # Add suggestions to the session
            for suggestion_data in extracted_data.get("suggestions", []):
                suggestion = Suggestion(
                    content=suggestion_data.get("content", ""),
                    accepted=suggestion_data.get("accepted", False)
                )
                session.suggestions.append(suggestion)
            
            # Add features to the session
            for feature_data in extracted_data.get("features", []):
                feature = Feature(
                    name=feature_data.get("name", ""),
                    description=feature_data.get("description", ""),
                    accepted=feature_data.get("accepted", False)
                )
                session.features.append(feature)
                
            logger.info(f"Extracted {len(extracted_data.get('suggestions', []))} suggestions and {len(extracted_data.get('features', []))} features")
            
        except Exception as e:
            logger.error(f"Error extracting suggestions and features: {str(e)}")
    
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