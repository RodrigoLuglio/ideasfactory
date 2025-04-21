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
import asyncio

from pydantic import BaseModel, Field

from ideasfactory.utils.llm_utils import (
    Message, send_prompt, create_system_prompt, create_user_prompt,
    create_assistant_prompt
)
from ideasfactory.tools import (
    search_web, scrape_webpage, extract_key_phrases, summarize_content,
    categorize_information, extract_market_data
)

# Configure logging
logger = logging.getLogger(__name__)

# Project Manager system prompt
PM_SYSTEM_PROMPT = """
You are an experienced senior project manager with strong background in technology and innovation.

Your role is to analyze the project vision document provided by the Business Analyst and make a research to gather all possible information about the solution/product/service it describes, including, but not limited to, market research, technology research, and legal research.

You have access to the following tools to assist with your research:
1. Web search - search the internet for information
2. Web scraping - extract detailed content from web pages
3. Data analysis - analyze and categorize information
4. Market data extraction - identify market size, growth rates, competitors from text

Use these tools to conduct a deep research and provide a detailed report with all the information you can find about the project.

This report can follow the structure of a Product Requirements Document (PRD) if you think it is the best way to present the information. Otherwise, you can define the best structure to present the information according to the kind of project as each idea might require a different way to be presented.

The report must:
- Be clear, detailed and precise, describing the project with ALL and ONLY the information that you found in your research or your insights if they are based on existing sources
- NOT contain any invented information or information that is not related to the project
- Include proper citations for any external information or research findings
- Be written in a markdown format
"""

PM_RESEARCH_PROMPT = """
Based on this project vision document, I need you to conduct thorough research on all aspects of this project.

You have the following tools at your disposal:
1. Web search - You can search the internet for information using the search_web() function
2. Web scraping - You can extract detailed content from web pages using the scrape_webpage() function
3. Data analysis - You can analyze text data using extract_key_phrases(), summarize_content(), and categorize_information() functions
4. Market data extraction - You can extract market data from text using extract_market_data() function

Please consider the following areas in your research:
1. Market Analysis: Target market, competitors, market trends, potential challenges
2. Technical Feasibility: Technologies involved, potential technical challenges, best practices
3. Legal/Compliance: Any legal requirements, regulations, compliance needs
4. Resource Requirements: Team composition, skills needed, estimated timelines
5. Risk Assessment: Potential risks and mitigation strategies

Structure your findings in a way that best serves this specific project. If a PRD format is suitable, use it. Otherwise, create a structure that best presents the information for this type of project.

Remember to:
- Cite your sources and provide evidence for your findings where possible
- Focus on factual information rather than speculation
- Consider both positive and negative aspects (benefits and challenges)
- Take into account the specific requirements and constraints mentioned in the vision document
"""


class ResearchCategory(str, Enum):
    """Research categories for the project analysis."""
    MARKET = "market_analysis"
    TECHNICAL = "technical_feasibility"
    LEGAL = "legal_compliance"
    RESOURCES = "resource_requirements"
    RISKS = "risk_assessment"


class ResearchFinding(BaseModel):
    """A research finding for a specific category."""
    category: ResearchCategory
    content: str
    source: str


class ResearchSession(BaseModel):
    """A research session with the Project Manager."""
    id: str = Field(..., description="Unique identifier for the session")
    project_vision: str = Field(..., description="Project vision document content")
    findings: List[ResearchFinding] = Field(default_factory=list, description="Research findings")
    messages: List[Message] = Field(default_factory=list, description="Messages in the session")
    research_report: Optional[str] = Field(None, description="Generated research report content")
    search_queries: List[str] = Field(default_factory=list, description="Search queries used")
    
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
    
    async def _perform_web_search(self, session_id: str, query: str, num_results: int = 5) -> List[Dict[str, Any]]:
        """
        Perform a web search for the given query.
        
        Args:
            session_id: Identifier of the session
            query: Search query
            num_results: Number of results to return
            
        Returns:
            List of search results
        """
        # Get the session
        session = self.sessions.get(session_id)
        if not session:
            logger.error(f"Session not found: {session_id}")
            return []
        
        # Add the query to the session
        session.search_queries.append(query)
        
        # Perform the search
        results = await search_web(query, num_results)
        
        return results
    
    async def _scrape_web_page(self, session_id: str, url: str) -> Optional[Dict[str, Any]]:
        """
        Scrape content from a web page.
        
        Args:
            session_id: Identifier of the session
            url: URL to scrape
            
        Returns:
            Scraped content or None if session not found
        """
        # Get the session
        session = self.sessions.get(session_id)
        if not session:
            logger.error(f"Session not found: {session_id}")
            return None
        
        # Scrape the web page
        content = await scrape_webpage(url)
        
        return content
    
    async def _analyze_research_needs(self, session_id: str) -> List[str]:
        """
        Analyze the project vision to determine research needs.
        
        Args:
            session_id: Identifier of the session
            
        Returns:
            List of suggested search queries
        """
        # Get the session
        session = self.sessions.get(session_id)
        if not session:
            logger.error(f"Session not found: {session_id}")
            return []
        
        # Create a prompt to analyze research needs
        research_analysis_prompt = f"""
        I need to conduct research on this project. Based on the project vision document below, 
        suggest 5-10 specific search queries that would help gather comprehensive information.
        
        Project Vision:
        {session.project_vision}
        
        For each suggested query, briefly explain what information it aims to gather.
        Format your response as a JSON array of objects, each with 'query' and 'purpose' fields.
        """
        
        # Create the message
        analysis_request = create_user_prompt(research_analysis_prompt)
        
        # Use a temporary list of messages to avoid affecting the session
        temp_messages = [self.system_prompt, analysis_request]
        
        # Get the agent's response
        response = await send_prompt(temp_messages)
        
        # Parse the response to extract queries
        try:
            # Find JSON content in the response
            import re
            json_match = re.search(r'```json\s*(.*?)\s*```', response.content, re.DOTALL)
            
            if json_match:
                json_content = json_match.group(1)
            else:
                # Try to find JSON without the markdown code block
                json_match = re.search(r'\[\s*{', response.content)
                if json_match:
                    json_content = response.content[json_match.start():]
                else:
                    logger.error("JSON content not found in response")
                    return []
            
            # Parse the JSON content
            queries_data = json.loads(json_content)
            
            # Extract the queries
            queries = [item["query"] for item in queries_data]
            
            return queries
            
        except Exception as e:
            logger.error(f"Error parsing research queries: {str(e)}")
            # If parsing fails, extract basic keywords from the vision document
            key_phrases = extract_key_phrases(session.project_vision, min_count=3)
            
            # Create simple search queries from key phrases
            return [f"{phrase} market analysis" for phrase in key_phrases[:5]]
    
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
        
        # Step 1: Analyze the project vision to determine research needs
        search_queries = await self._analyze_research_needs(session_id)
        
        # Step 2: Perform web searches
        all_search_results = []
        
        for query in search_queries:
            results = await self._perform_web_search(session_id, query)
            all_search_results.extend(results)
        
        # Step 3: Scrape detailed content from the most relevant results
        detailed_content = []
        
        # Sort results by relevance (simple implementation)
        top_results = sorted(all_search_results, key=lambda x: len(x["snippet"]), reverse=True)[:5]
        
        for result in top_results:
            content = await self._scrape_web_page(session_id, result["link"])
            if content:
                # Summarize the content to make it more manageable
                summary = summarize_content(content["content"])
                
                detailed_content.append({
                    "title": content["title"],
                    "summary": summary,
                    "url": content["url"]
                })
        
        # Step 4: Categorize the information
        categories = [cat.value for cat in ResearchCategory]
        
        # Extract text snippets for categorization
        snippets = [result["snippet"] for result in all_search_results]
        categorized_snippets = categorize_information(snippets, categories)
        
        # Step 5: Generate the research report
        research_data = {
            "vision": session.project_vision,
            "search_results": all_search_results,
            "detailed_content": detailed_content,
            "categorized_information": categorized_snippets
        }
        
        # Create a prompt for the research report
        research_prompt = f"""
        Based on the project vision document and research data, create a comprehensive research report.
        
        Project Vision:
        {session.project_vision}
        
        Research Data:
        {json.dumps(research_data, indent=2)}
        
        {PM_RESEARCH_PROMPT}
        
        Please provide the research report in markdown format.
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