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

# Make enhanced tools available to the project manager
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

from ideasfactory.utils.error_handler import handle_async_errors
from ideasfactory.utils.session_manager import SessionManager

# Configure logging
logger = logging.getLogger(__name__)

# Product Manager system prompt
PM_SYSTEM_PROMPT = """
You are a visionary product manager with exceptional insight into transforming ideas into comprehensive requirements while AMPLIFYING their innovative essence.

Your primary responsibility is to bridge the gap between creative vision and technical implementation by producing a Product Requirements Document (PRD) that serves as the foundation for all subsequent workflow stages (Architecture Planning, Research, Standards Development, etc.).

You approach each project as FUNDAMENTALLY UNIQUE - recognizing that innovation often emerges from breaking conventional patterns. You have a rare ability to identify what makes THIS PARTICULAR project special and to ensure its distinctive character not only survives but THRIVES throughout the requirements definition process.

Your greatest strength is balancing comprehensiveness with innovation preservation:

1. You can extract the INNOVATION CORE from any vision - the elements that represent true departures from standard approaches
2. You can identify IMPLICIT REQUIREMENTS that aren't stated but are essential to realizing the vision's unique value
3. You can articulate TECHNICAL IMPLICATIONS of innovative approaches without constraining implementation creativity
4. You can define QUALITY ATTRIBUTES in the specific context of each unique project
5. You can document INTEGRATION TOUCHPOINTS without imposing conventional architectural patterns

Your PRD must serve as a COMPLETE BLUEPRINT that:

- Expands each identified feature into deeply detailed functional requirements
- Uncovers the full spectrum of implicit technical requirements essential to the vision
- Identifies non-functional requirements contextualized to THIS specific solution
- Defines edge cases and boundary conditions particularly relevant to the unique approach
- Establishes measurable success criteria that preserve innovative elements
- Documents constraints, dependencies, and assumptions without normalizing innovation
- Identifies integration points and data flows needed for implementation
- Articulates technical foundations required to enable distinctive capabilities

However, you have an unwavering commitment to these principles:

- NEVER introduce features or requirements not aligned with the original vision
- NEVER impose conventional product structures on innovative ideas
- ALWAYS maintain the unique character and approach of the original concept
- ACTIVELY RESIST the urge to standardize unique approaches into familiar patterns
- DELIBERATELY PRESERVE any unconventional or novel elements of the vision
- ADAPT document structure to highlight distinctive aspects rather than following templates

Above all, you understand that your PRD serves as the critical foundation for the entire implementation process. It must enable technical teams to build exactly what was envisioned, with all necessary details, while ENHANCING rather than diminishing the innovative and unique aspects that make this project special.

Your success is measured by creating requirements documents that are both COMPREHENSIVE enough for technical implementation AND FAITHFUL to the vision's innovative character.
"""

PM_PRD_CREATION_PROMPT = """
Based on the project vision document, create a comprehensive Product Requirements Document (PRD) that expands the vision into detailed requirements while PRESERVING and ENHANCING its unique, innovative character.

Your approach should be to:

1. DEEPLY ANALYZE the vision document to extract:
   - Explicitly stated features and capabilities
   - Implied needs and functionalities
   - The UNIQUE ESSENCE that makes this idea special and different from conventional solutions

2. IDENTIFY THE INNOVATION CORE:
   - What aspects of this vision represent a true departure from standard approaches?
   - What makes this solution fundamentally different from existing alternatives?
   - What novel value does this unique approach create for users?
   - How must this uniqueness be preserved throughout implementation?

3. EXPAND each feature into:
   - Detailed functional requirements with specific behaviors
   - Edge cases and boundary conditions that are particularly relevant to this unique approach
   - Technical implications that arise SPECIFICALLY BECAUSE of this vision's innovative aspects
   - Dependencies between features that create the vision's distinctive experience

4. SURFACE IMPLICIT REQUIREMENTS:
   - For each explicit feature, identify at least 3-5 implicit requirements necessary for full implementation
   - Consider what "hidden" capabilities would be needed to deliver the complete user experience
   - Analyze what technical foundations must exist to enable the distinctive aspects of the vision
   - Identify interaction patterns unique to this specific solution

5. CONTEXTUALIZE QUALITY ATTRIBUTES:
   - Performance requirements that are particularly relevant to this vision's unique approach
   - Security considerations specific to this solution's distinctive characteristics
   - Scalability needs that preserve the vision's innovative qualities as usage grows
   - Usability requirements that maintain the vision's unique interaction model
   - Accessibility considerations tailored to this specific solution's distinctive interface
   - Any other quality attributes especially critical to THIS specific project's success

6. DEFINE INTEGRATION TOUCHPOINTS:
   - Identify boundaries and integration points with other systems
   - Specify data flows necessary for the solution to function in its environment
   - Articulate API requirements without prescribing specific implementation approaches

7. DOCUMENT ASSUMPTIONS AND CONSTRAINTS:
   - Articulate assumptions that underpin the vision's approach
   - Identify constraints that must be respected while maintaining innovation
   - Note potential tensions between conventional approaches and this vision's unique needs

8. ADAPT the document structure to highlight what makes this project unique:
   - Don't force into conventional templates
   - Create sections that emphasize the distinctive aspects
   - Organize requirements in a way that reflects the project's natural structure

The final document should provide a COMPLETE BLUEPRINT for implementation while AMPLIFYING the vision's innovative elements. It must enable subsequent workflow stages (Architecture Research Requirements, Research Phase, etc.) with sufficient detail while preserving the original concept's distinctiveness.

CRITICAL BALANCE: Your PRD must be comprehensive enough to support technical implementation without standardizing away what makes this vision innovative. Document WHAT needs to be built while remaining flexible on HOW it should be built.

IMPORTANT: The PRD must NOT introduce new features beyond the vision's scope, yet must include ALL implicit requirements needed to successfully implement the envisioned features in a way that maintains their distinctive character.

Please create this document in markdown format, with a structure that best serves THIS specific project's unique nature.
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


class RequirementCategory(str, Enum):
    """Requirement categories for the PRD."""
    FUNCTIONAL = "functional_requirements"
    NON_FUNCTIONAL = "non_functional_requirements"
    CONSTRAINTS = "constraints"
    ASSUMPTIONS = "assumptions"
    DEPENDENCIES = "dependencies"
    SUCCESS_CRITERIA = "success_criteria"
    # Additional categories used in practice
    IMPLICIT_REQUIREMENTS = "implicit_requirements"
    CONSTRAINT = "constraint"
    ASSUMPTION = "assumption"
    QUALITY_ATTRIBUTES = "quality_attributes"
    INTEGRATION_TOUCHPOINTS = "integration_touchpoints"


class Requirement(BaseModel):
    """A requirement for the PRD."""
    category: RequirementCategory
    title: str
    description: str
    priority: str = "Medium"
    notes: Optional[str] = None


class PRDSession(BaseModel):
    """A PRD creation session with the Project Manager."""
    id: str = Field(..., description="Unique identifier for the session")
    project_vision: str = Field(..., description="Project vision document content")
    requirements: List[Requirement] = Field(default_factory=list, description="Requirements list")
    messages: List[Message] = Field(default_factory=list, description="Messages in the session")
    prd_document: Optional[str] = Field(None, description="Generated PRD content")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata for the session")
    
    class Config:
        """Pydantic model configuration."""
        arbitrary_types_allowed = True


class ProjectManager:
    """
    Project Manager agent that creates Product Requirements Documents (PRDs) from project vision documents.
    
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
            self.sessions: Dict[str, PRDSession] = {}
            self.system_prompt = create_system_prompt(PM_SYSTEM_PROMPT)
            self._initialized = True
    
    @handle_async_errors
    async def create_session(self, session_id: str, project_vision: str) -> PRDSession:
        """
        Create a new PRD creation session.
        
        Args:
            session_id: Unique identifier for the session
            project_vision: Project vision document content
            
        Returns:
            The created PRD session
        """
        # Log session creation
        logger.info(f"Creating project manager session {session_id} with vision document of length {len(project_vision)}")
        
        # Create a new session
        session = PRDSession(
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
    async def create_prd(self, session_id: str) -> Optional[str]:
        """
        Create a Product Requirements Document (PRD) based on the project vision.
        
        Args:
            session_id: Identifier of the session
            
        Returns:
            The PRD content or None if session not found
        """
        logger.info(f"Starting PRD creation for session {session_id}")
        
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
        
        # Extract features from the vision document for explicit tracking
        import re
        feature_pattern = r'### \d+\.\s+([^\n]+)\n- \*\*Description:\*\*\s+([^\n]+)'
        features = re.findall(feature_pattern, session.project_vision)
        feature_list = "\n".join([f"- {name}: {desc}" for name, desc in features])
        
        # Create a prompt for the PRD that preserves the vision's unique character
        prd_prompt = f"""
        Based on the project vision document, create a comprehensive Product Requirements Document (PRD).
        
        Project Vision:
        {session.project_vision}
        
        KEY FEATURES EXTRACTED FROM VISION DOCUMENT:
        {feature_list}
        
        {PM_PRD_CREATION_PROMPT}
        
        IMPORTANT GUIDANCE:
        
        1. PRESERVE UNIQUENESS:
           - The structure of the PRD should adapt to what makes THIS project unique
           - Don't force this project into a conventional template or structure
           - Let the document organization reflect the project's natural structure
        
        2. COMPLETENESS WITHOUT STANDARDIZATION:
           - Cover all necessary requirement aspects (functional, non-functional, etc.)
           - But avoid imposing conventional product structures on this innovative idea
           - Find the natural organization this specific project demands
        
        3. DETAILED FUNCTIONAL REQUIREMENTS:
           - For EACH feature explicitly mentioned in the vision document:
             * Document detailed behaviors
             * Explain user interactions
             * Define success criteria
             * Identify edge cases
        
        4. IMPLICIT REQUIREMENTS:
           - Identify and document requirements that weren't explicitly stated but are necessary
           - For example: performance needs, security considerations, usability requirements
           - Ensure these are presented as enabling the vision, not changing it
        
        5. TECHNICAL BOUNDARIES:
           - Define clear boundaries between components/features
           - Specify integration points and interfaces
           - Document constraints and dependencies
        
        Please provide the PRD in markdown format. The structure should be tailored to highlight what makes this specific project unique while ensuring it contains all the information needed for implementation.
        """
        
        prd_request = create_user_prompt(prd_prompt)
        session.messages.append(prd_request)
        
        # Get the agent's response
        response = await send_prompt(session.messages)
        
        # Extract requirements from the PRD
        await self._extract_requirements(session_id, response.content)
        
        # Add the response to the session
        assistant_message = create_assistant_prompt(response.content)
        session.messages.append(assistant_message)
        
        # Store the PRD
        session.prd_document = response.content
        
        return response.content
        
    @handle_async_errors
    async def _extract_requirements(self, session_id: str, prd_content: str) -> None:
        """
        Extract structured requirements from the PRD.
        
        Args:
            session_id: Identifier of the session
            prd_content: Content of the PRD
            
        Returns:
            None - updates the session with requirements
        """
        # Get the session
        session = self.sessions.get(session_id)
        if not session:
            logger.error(f"Session not found: {session_id}")
            return
        
        # Create a prompt to extract requirements
        analysis_prompt = f"""
        Please analyze this Product Requirements Document (PRD) and extract structured requirements.
        
        PRD Content:
        {prd_content}
        
        For each requirement you identify, extract:
        1. Category (functional, non-functional, constraint, assumption, dependency, success_criteria)
        2. Title (short descriptive name)
        3. Description (detailed explanation)
        4. Priority (High, Medium, Low)
        5. Notes (any additional information)
        
        Format your response as a JSON array of objects with the following structure:
        
        ```json
        [
          {{
            "category": "functional_requirements", 
            "title": "Requirement title",
            "description": "Detailed description",
            "priority": "High",
            "notes": "Additional notes or null if none"
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
            requirements_data = json.loads(json_text)
            
            # Convert to Requirement objects and add to session
            for req_data in requirements_data:
                try:
                    # Convert string category to enum
                    category = RequirementCategory(req_data.get("category", "functional_requirements"))
                    
                    requirement = Requirement(
                        category=category,
                        title=req_data.get("title", ""),
                        description=req_data.get("description", ""),
                        priority=req_data.get("priority", "Medium"),
                        notes=req_data.get("notes")
                    )
                    session.requirements.append(requirement)
                except ValueError as e:
                    logger.error(f"Invalid category: {req_data.get('category')}")
                    continue
                
            logger.info(f"Extracted {len(requirements_data)} requirements")
            
        except Exception as e:
            logger.error(f"Error extracting requirements: {str(e)}")
    
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
    
    def _format_requirements(self, requirements: List[Requirement]) -> str:
        """
        Format requirements for inclusion in the document.
        
        Args:
            requirements: List of requirements
            
        Returns:
            Formatted requirements as markdown text
        """
        if not requirements:
            return "No structured requirements available."
        
        # Group requirements by category
        requirements_by_category = {}
        for requirement in requirements:
            category = requirement.category
            if category not in requirements_by_category:
                requirements_by_category[category] = []
            requirements_by_category[category].append(requirement)
        
        # Format the requirements
        formatted_requirements = ""
        
        for category, category_requirements in requirements_by_category.items():
            # Convert enum to display name
            display_name = category.value.replace("_", " ").title()
            
            formatted_requirements += f"## {display_name}\n\n"
            
            for requirement in category_requirements:
                formatted_requirements += f"### {requirement.title} (Priority: {requirement.priority})\n\n"
                formatted_requirements += f"{requirement.description}\n\n"
                if requirement.notes:
                    formatted_requirements += f"**Notes:** {requirement.notes}\n\n"
        
        return formatted_requirements
            
    @handle_async_errors
    async def revise_prd(self, session_id: str, feedback: str) -> Optional[str]:
        """
        Revise the PRD based on feedback.
        
        Args:
            session_id: Identifier of the session
            feedback: Feedback on the PRD
            
        Returns:
            The revised PRD content or None if session not found
        """
        # Get the session
        session = self.sessions.get(session_id)
        if not session:
            logger.error(f"Session not found: {session_id}")
            return None
        
        # Format the structured requirements for inclusion in the revision
        structured_requirements = self._format_requirements(session.requirements)
        
        # Create the revision message with structured requirements
        revision_prompt = f"""
        Please revise the Product Requirements Document based on this feedback: "{feedback}"
        
        Remember to preserve these key structured requirements that were previously identified:
        
        {structured_requirements}
        
        CRITICAL REVISION GUIDELINES:
        
        1. ENHANCE INNOVATIVE ELEMENTS:
           - Your revisions should AMPLIFY what makes THIS project unique, not diminish it
           - Pay special attention to preserving the innovation core while addressing feedback
           - Ensure any additions further illuminate the vision's distinctive qualities
        
        2. PRESERVE & DEEPEN UNIQUENESS:
           - The structure of the PRD should continue to adapt to what makes THIS project unique
           - Never force this project into a conventional template or structure
           - Look for opportunities to make unique aspects even more distinct in your revisions
        
        3. COMPLETENESS WITHOUT STANDARDIZATION:
           - Address all feedback completely while maintaining the project's distinctive nature
           - Cover necessary requirement aspects while avoiding conventional product structures
           - Expand on implicit requirements that enable the vision's unique approach
        
        4. TECHNICAL FOUNDATIONS WITHOUT IMPLEMENTATION BIAS:
           - Clarify technical implications of the vision's unique approach without prescribing solutions
           - Specify what technical capabilities are needed without dictating how to implement them
           - Address integration points and boundaries while preserving implementation flexibility
        
        5. MAINTAIN VISION INTEGRITY:
           - Ensure all revisions align with and enhance the original project vision
           - Never introduce requirements that would normalize or standardize the innovative concept
           - Strengthen requirements that preserve the unique user experience envisioned
        
        6. IMPORTANT FORMAT INSTRUCTIONS: 
           - ONLY provide the updated PRD in markdown format
           - Do NOT add commentary, questions, or explanations before or after the document
           - Simply apply the requested changes and return the complete updated document
           - Make sure to include the relevant requirements in the appropriate sections
           - Ensure the document structure continues to highlight the project's unique qualities
        """
        
        revision_request = create_user_prompt(revision_prompt)
        session.messages.append(revision_request)
        
        # Get the agent's response
        response = await send_prompt(session.messages)
        
        # Add the response to the session
        assistant_message = create_assistant_prompt(response.content)
        session.messages.append(assistant_message)
        
        # Update the PRD document
        session.prd_document = response.content
        
        return response.content