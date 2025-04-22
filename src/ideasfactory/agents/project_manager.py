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

from ideasfactory.utils.error_handler import handle_async_errors
from ideasfactory.utils.session_manager import SessionManager

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
Based on this project vision document, I need you to conduct thorough, comprehensive research tailored specifically to this unique project's needs.

You have the following tools at your disposal:
1. Web search - You can search the internet for information using the search_web() function
2. Web scraping - You can extract detailed content from web pages using the scrape_webpage() function
3. Data analysis - You can analyze text data using extract_key_phrases(), summarize_content(), and categorize_information() functions
4. Market data extraction - You can extract market data from text using extract_market_data() function

First, identify the core technical domains relevant to THIS SPECIFIC PROJECT - these will vary completely based on the project's nature.

For EACH identified technical domain, research:
- A comprehensive spectrum of implementation approaches, from established to experimental
- Diverse technological foundations with fundamentally different characteristics
- Solutions across multiple paradigms, not just the most mainstream options
- Combinations of technologies that might offer unique advantages
- Unconventional approaches that might suit the project's specific needs

Your technology research must:
- Be completely tailored to the project's unique requirements
- Avoid assumptions about traditional technology categories
- Present a truly diverse range of options for each project aspect
- Include both proven and innovative approaches
- Explore the full landscape of possibilities without omitting options
- Uncover approaches the user might not be aware of

In addition, please consider these general research areas, adapting them to fit the project's specific context:
1. Market Analysis: Target market, competitors, market trends, potential challenges
2. Legal/Compliance: Any legal requirements, regulations, compliance needs
3. Resource Requirements: Team composition, skills needed, estimated timelines
4. Risk Assessment: Potential risks and mitigation strategies

The structure of your findings should be completely adapted to this specific project's nature. There is no one-size-fits-all template - organize the information in whatever way best serves THIS project.

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
    
    @handle_async_errors
    async def create_session(self, session_id: str, project_vision: str) -> ResearchSession:
        """
        Create a new research session.
        
        Args:
            session_id: Unique identifier for the session
            project_vision: Project vision document content
            
        Returns:
            The created research session
        """
        # Log session creation
        logger.info(f"Creating project manager session {session_id} with vision document of length {len(project_vision)}")
        
        # Create a new session
        session = ResearchSession(
            id=session_id,
            project_vision=project_vision,
            messages=[self.system_prompt]
        )
        
        # Store the session
        self.sessions[session_id] = session
        logger.info(f"Project manager session {session_id} created successfully")
        
        return session
    
    @handle_async_errors
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
    
    @handle_async_errors
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
    
    @handle_async_errors
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
    
    @handle_async_errors
    async def conduct_research(self, session_id: str) -> Optional[str]:
        """
        Conduct research on the project.
        
        Args:
            session_id: Identifier of the session
            
        Returns:
            The research report or None if session not found
        """
        logger.info(f"Starting comprehensive research for session {session_id}")
        
        # Get the session
        session = self.sessions.get(session_id)
        if not session:
            logger.error(f"Session not found: {session_id}")
            return None
            
        # Validate the project vision is available
        if not session.project_vision:
            logger.error(f"Project vision not found in session {session_id}")
            return None
            
        logger.info(f"Session retrieved for {session_id} with vision of length: {len(session.project_vision)}")
        
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
        
        # Step 5: Extract structured research findings
        # Process the research data to create structured findings
        await self._extract_research_findings(session_id, all_search_results, detailed_content, categorized_snippets)

        # Get the updated session with findings
        session = self.sessions.get(session_id)
        
        # Format the structured findings for inclusion in the document
        structured_findings = self._format_research_findings(session.findings)
        
        # Create a research data package with both raw data and structured findings
        research_data = {
            "vision": session.project_vision,
            "search_results": all_search_results,
            "detailed_content": detailed_content,
            "categorized_information": categorized_snippets
        }
        
        # Extract features from the vision document for explicit tracking
        import re
        feature_pattern = r'### \d+\.\s+([^\n]+)\n- \*\*Description:\*\*\s+([^\n]+)'
        features = re.findall(feature_pattern, session.project_vision)
        feature_list = "\n".join([f"- {name}: {desc}" for name, desc in features])
        
        # Create a prompt for the research report that includes the structured findings
        research_prompt = f"""
        Based on the project vision document and research data, create a comprehensive research report that is both THOROUGH and INSIGHTFUL.
        
        Project Vision:
        {session.project_vision}
        
        KEY FEATURES EXTRACTED FROM VISION DOCUMENT:
        {feature_list}
        
        Research Data:
        {json.dumps(research_data, indent=2)}
        
        I've also extracted and categorized the following key research findings:
        
        {structured_findings}
        
        {PM_RESEARCH_PROMPT}
        
        CRITICAL REQUIREMENTS FOR YOUR REPORT:
        
        1. SCOPE CLARITY: 
           - The "Core Features and Requirements" section must include ALL features explicitly mentioned in the Project Vision document
           - Use a clearly separate "Potential Extensions" section for valuable features discovered in research that weren't in the original vision
        
        2. TECHNOLOGY OPTIONS:
           - For EACH feature, research and document AT LEAST 5-7 different implementation approaches
           - Each approach must specify THE ACTUAL TECHNOLOGIES that would be used (frameworks, libraries, platforms, tools)
           - Include the FULL SPECTRUM: established/traditional, mainstream current, and cutting-edge/experimental options
           - For example, don't just say "Text-Based Search" - specify "Elasticsearch with React hooks" or "PostgreSQL full-text search with Django ORM"
           - Present all options neutrally with detailed technical pros/cons
        
        3. COMPREHENSIVE MARKET INSIGHTS:
           - Conduct deep competitive analysis of similar solutions (not just surface-level trends)
           - Identify specific competitor products and their unique approaches to similar problems
           - Uncover unexpected market opportunities or challenges that might not be immediately obvious
           - Present genuinely surprising insights that someone couldn't easily find in a basic search
        
        4. INTELLECTUAL CURIOSITY:
           - Don't just answer the obvious questions - anticipate the questions no one thought to ask
           - Connect unexpected domains that might influence this project in surprising ways
           - Identify patterns and insights across different fields that could be relevant
           - Include at least 2-3 truly surprising insights that would make someone say "I never would have thought of that"
        
        5. TECHNICAL DEPTH & BREADTH:
           - For each technology option, explore specific implementation details, not just high-level approaches
           - Consider how different features might interact technically
           - Explore unconventional technology combinations that might offer unique advantages
           - Identify specific libraries, tools, and frameworks for each approach
        
        Approach this research as if you have unlimited access to the world's knowledge and a genuinely curious mind. The report should reflect both comprehensive thoroughness AND surprising insight - the kind that comes from making unexpected connections across different fields of knowledge.
        
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
    
    @handle_async_errors
    async def _extract_research_findings(self, session_id: str, search_results: list, detailed_content: list, categorized_info: dict) -> None:
        """
        Extract structured research findings from the research data.
        
        Args:
            session_id: Identifier of the session
            search_results: Web search results
            detailed_content: Detailed content from scraped pages
            categorized_info: Information categorized by research category
            
        Returns:
            None - updates the session with findings
        """
        # Get the session
        session = self.sessions.get(session_id)
        if not session:
            logger.error(f"Session not found: {session_id}")
            return
        
        # Create a prompt to extract findings
        analysis_prompt = f"""
        Please analyze this research data and extract comprehensive, detailed findings for each category.
        
        Research Categories:
        - Market Analysis (market trends, competitors, target audience)
        - Technical Feasibility (technical approach, technology stack, challenges)
        - Legal/Compliance (regulations, legal requirements, compliance needs)
        - Resource Requirements (team composition, skills needed, timeline)
        - Risk Assessment (potential risks, mitigation strategies)
        
        Search Results:
        {json.dumps(search_results[:5], indent=2)}
        
        Detailed Content:
        {json.dumps(detailed_content, indent=2)}
        
        Categorized Information:
        {json.dumps(categorized_info, indent=2)}
        
        IMPORTANT FOR TECHNICAL FEASIBILITY FINDINGS:
        
        1. Identify the COMPLETE SPECTRUM of technology options for EACH technical aspect of the project
        2. Include findings covering diverse technology approaches:
           - Established/traditional approaches
           - Current mainstream solutions
           - Emerging/cutting-edge options
           - Cross-paradigm or unconventional approaches
        3. For each major feature or component, find at least 5-7 different possible implementation approaches
        4. Do not limit findings to only the most popular technologies
        5. Include findings about interesting technology combinations that could benefit this specific project
        
        For each category, extract at least 5-8 key findings supported by the research data.
        
        Format your response as a JSON array of objects with the following structure:
        
        ```json
        [
          {{
            "category": "market_analysis", 
            "content": "Specific finding about the market",
            "source": "URL or source of the information"
          }},
          {{
            "category": "technical_feasibility",
            "content": "Specific finding about technical feasibility",
            "source": "URL or source of the information"
          }}
        ]
        ```
        
        Only return the JSON array without any additional text.
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
                    return
            
            # Parse the JSON
            findings_data = json.loads(json_text)
            
            # Convert to ResearchFinding objects and add to session
            for finding_data in findings_data:
                try:
                    # Convert string category to enum
                    category = ResearchCategory(finding_data.get("category", "market_analysis"))
                    
                    finding = ResearchFinding(
                        category=category,
                        content=finding_data.get("content", ""),
                        source=finding_data.get("source", "")
                    )
                    session.findings.append(finding)
                except ValueError as e:
                    logger.error(f"Invalid category: {finding_data.get('category')}")
                    continue
                
            logger.info(f"Extracted {len(findings_data)} research findings")
            
        except Exception as e:
            logger.error(f"Error extracting research findings: {str(e)}")
    
    def _format_research_findings(self, findings: List[ResearchFinding]) -> str:
        """
        Format research findings for inclusion in the document.
        
        Args:
            findings: List of research findings
            
        Returns:
            Formatted findings as markdown text
        """
        if not findings:
            return "No structured findings available."
        
        # Group findings by category
        findings_by_category = {}
        for finding in findings:
            category = finding.category
            if category not in findings_by_category:
                findings_by_category[category] = []
            findings_by_category[category].append(finding)
        
        # Format the findings
        formatted_findings = ""
        
        for category, category_findings in findings_by_category.items():
            # Convert enum to display name
            display_name = category.value.replace("_", " ").title()
            
            formatted_findings += f"## {display_name}\n\n"
            
            for finding in category_findings:
                formatted_findings += f"- {finding.content}"
                if finding.source:
                    formatted_findings += f" (Source: {finding.source})"
                formatted_findings += "\n"
            
            formatted_findings += "\n"
        
        return formatted_findings
            
    @handle_async_errors
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
        
        # Format the structured findings for inclusion in the revision
        structured_findings = self._format_research_findings(session.findings)
        
        # Create the revision message with structured findings
        revision_prompt = f"""
        Please revise the research report based on this feedback: "{feedback}"
        
        Remember to incorporate these key research findings that were identified during our research:
        
        {structured_findings}
        
        IMPORTANT: 
        - ONLY provide the updated report in markdown format
        - Do NOT add commentary, questions, or explanations before or after the report
        - Simply apply the requested changes to the existing report and return the complete updated document
        - Make sure to include the relevant research findings in the appropriate sections
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