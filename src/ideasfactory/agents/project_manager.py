# project_manager.py - Project Manager agent for IdeasFactory

"""
Project Manager agent for IdeasFactory.

This module implements the Project Manager agent that conducts deep research
and produces PRD or research report documents.
"""

import logging
from typing import List, Dict, Any, Optional
from enum import Enum
import json

from pydantic import BaseModel, Field

from ideasfactory.utils.llm_utils import (
    Message, send_prompt, create_system_prompt, create_user_prompt,
    create_assistant_prompt
)

# Configure logging
logger = logging.getLogger(__name__)

# Project Manager system prompt
PM_SYSTEM_PROMPT = """
You are an experienced senior project manager with strong background in technology and innovation.

Your role is to analyze the project vision document provided by the Business Analyst and make a research to gather all possible information about the solution/product/service it describes, including, but not limited to, market research, technology research, and legal research.

Use your knowledge, skills and if required, conduct online search to make a deep research and provide a detailed report with all the information you can find about the project.

This report can follow the structure of a Product Requirements Document (PRD) if you think it is the best way to present the information. Otherwise, you can define the best structure to present the information according to the kind of project as each idea might require a different way to be presented.

The report must:
- Be clear, detailed and precise, describing the project with ALL and ONLY the information that you found in your research or your insights if they are based on existing sources
- NOT contain any invented information or that is not related to the project
- Include proper citations for any external information or research findings
- Be written in a markdown format
"""

PM_RESEARCH_PROMPT = """
Based on the project vision document, I need you to conduct thorough research on all aspects of this project.

Please consider the following areas:
1. Market Analysis: Target market, competitors, market trends, potential challenges
2. Technical Feasibility: Technologies involved, potential technical challenges, best practices
3. Legal/Compliance: Any legal requirements, regulations, compliance needs
4. Resource Requirements: Team composition, skills needed, estimated timelines
5. Risk Assessment: Potential risks and mitigation strategies

Structure your findings in a way that best serves this specific project. If a PRD format is suitable, use it. Otherwise, create a structure that best presents the information for this type of project.

Remember to cite your sources and provide evidence for your findings where possible.
"""


class ResearchArea(BaseModel):
    """Research area in the project analysis."""
    name: str = Field(..., description="Name of the research area")
    findings: List[str] = Field(default_factory=list, description="Research findings")
    sources: List[str] = Field(default_factory=list, description="Sources for the findings")


class ResearchSession(BaseModel):
    """A research session with the Project Manager."""
    id: str = Field(..., description="Unique identifier for the session")
    project_vision: str = Field(..., description="Project vision document content")
    research_areas: List[ResearchArea] = Field(default_factory=list, description="Research areas analyzed")
    messages: List[Message] = Field(default_factory=list, description="Messages in the session")
    research_report: Optional[str] = Field(None, description="Generated research report content")
    
    class Config:
        """Pydantic model configuration."""
        arbitrary_types_allowed = True


class ProjectManager:
    """
    Project Manager agent that conducts research and produces PRD or research reports.
    
    Implemented as a singleton to ensure the same instance is shared across the application.
    """
    
    _instance = None
    
    def __new__(cls):
        """Ensure only one instance of ProjectManager is created."""
        if cls._instance is None:
            cls._instance = super(ProjectManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the Project Manager agent."""
        if not hasattr(self, '_initialized') or not self._initialized:
            self.sessions: Dict[str, ResearchSession] = {}
            self.system_prompt = create_system_prompt(PM_SYSTEM_PROMPT)
            self._initialized = True
    
    async def create_session(self, session_id: str, project_vision: str) -> ResearchSession:
        """
        Create a new research session.
        
        Args:
            session_id: Unique identifier for the session
            project_vision: Project vision document content
            
        Returns:
            The created research session
        """
        # Create a new session
        session = ResearchSession(
            id=session_id,
            project_vision=project_vision,
            messages=[self.system_prompt]
        )
        
        # Store the session
        self.sessions[session_id] = session
        
        return session
    
    async def conduct_research(self, session_id: str) -> Optional[str]:
        """
        Conduct research on the project.
        
        Args:
            session_id: Identifier of the session
            
        Returns:
            The research report or None if session not found
        """
        # Get the session
        session = self.sessions.get(session_id)
        if not session:
            logger.error(f"Session not found: {session_id}")
            return None
        
        # Create the research prompt
        research_prompt = f"""
        Please analyze this project vision document and conduct thorough research:
        
        {session.project_vision}
        
        {PM_RESEARCH_PROMPT}
        """
        
        research_request = create_user_prompt(research_prompt)
        session.messages.append(research_request)
        
        # Get the agent's response
        response = await send_prompt(session.messages)
        
        # Add the response to the session
        assistant_message = create_assistant_prompt(response.content)
        session.messages.append(assistant_message)
        
        # Store the research report
        session.research_report = response.content
        
        return response.content
    
    async def revise_report(self, session_id: str, feedback: str) -> Optional[str]:
        """
        Revise the research report based on feedback.
        
        Args:
            session_id: Identifier of the session
            feedback: Feedback on the research report
            
        Returns:
            The revised report content or None if session not found
        """
        # Get the session
        session = self.sessions.get(session_id)
        if not session:
            logger.error(f"Session not found: {session_id}")
            return None
        
        # Create the revision message
        revision_prompt = f"""
        Please revise the research report based on this feedback: "{feedback}"
        
        IMPORTANT: 
        - ONLY provide the updated report in markdown format
        - Do NOT add commentary, questions, or explanations before or after the report
        - Simply apply the requested changes to the existing report and return the complete updated document
        """
        
        revision_request = create_user_prompt(revision_prompt)
        session.messages.append(revision_request)
        
        # Get the agent's response
        response = await send_prompt(session.messages)
        
        # Add the response to the session
        assistant_message = create_assistant_prompt(response.content)
        session.messages.append(assistant_message)
        
        # Update the research report
        session.research_report = response.content
        
        return response.content