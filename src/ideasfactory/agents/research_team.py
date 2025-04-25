"""Foundational Research Team module for IdeasFactory.

This module implements the comprehensive Research Team that conducts foundation-based
research across multiple paradigms to inform architectural decisions
while preserving innovation and uniqueness throughout the exploration process.
"""

import logging
import asyncio
from typing import List, Dict, Any, Optional
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime

from ideasfactory.utils.error_handler import handle_errors, handle_async_errors
from ideasfactory.utils.session_manager import SessionManager
from ideasfactory.utils.llm_utils import (
    Message, send_prompt, create_system_prompt, create_user_prompt,
    create_assistant_prompt
)
from ideasfactory.documents.document_manager import DocumentManager
from ideasfactory.utils.file_manager import load_document_content

# Enhanced research tools - available but not prescriptively used
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

# Research paradigm categories
class ParadigmCategory(Enum):
    """Paradigm categories for research."""
    ESTABLISHED = "established_approaches"
    MAINSTREAM = "mainstream_current"
    CUTTING_EDGE = "cutting_edge"
    EXPERIMENTAL = "experimental"
    CROSS_PARADIGM = "cross_paradigm"
    FIRST_PRINCIPLES = "first_principles"

# Define research paradigms list
RESEARCH_PARADIGMS = [
    "established_approaches",
    "mainstream_current",
    "cutting_edge",
    "experimental",
    "cross_paradigm",
    "first_principles"
]

class ResearchAgentType(Enum):
    """Types of specialized research agents."""
    FOUNDATION = "foundation"
    PARADIGM = "paradigm"
    PATH = "path"
    INTEGRATION = "integration"
    SYNTHESIS = "synthesis"

@dataclass
class ProjectFoundation:
    """Class representing a potential project foundation approach."""
    name: str
    description: str
    paradigm_category: str
    research_areas: List[Dict[str, Any]] = field(default_factory=list)
    completed: bool = False
    research_content: Dict[str, str] = field(default_factory=dict)
    viability_score: float = 0.0  # How viable this foundation is for the project

@dataclass
class EmergentDimension:
    """Class representing an aspect of implementation that emerges from a foundation choice."""
    name: str
    description: str
    foundation_id: str  # Which foundation this dimension emerges from
    research_areas: List[Dict[str, Any]] = field(default_factory=list)
    completed: bool = False
    research_content: Dict[str, str] = field(default_factory=dict)

@dataclass
class ResearchPath:
    """Class representing a research path based on foundation choices."""
    name: str
    description: str
    foundation_id: str  # The foundation this path is based on
    emergent_dimensions: List[EmergentDimension] = field(default_factory=list)
    research_content: Optional[str] = None

@dataclass
class ResearchAgent:
    """Class representing a specialized research agent."""
    id: str
    type: ResearchAgentType
    name: str
    focus_area: str
    system_prompt: str
    messages: List[Message] = field(default_factory=list)
    findings: List[str] = field(default_factory=list)
    status: str = "initialized"

@dataclass
class FoundationalResearchSession:
    """Class representing a research session focused on emergent foundations."""
    id: str
    requirements: str
    project_foundations: Dict[str, ProjectFoundation] = field(default_factory=dict)
    emergent_dimensions: Dict[str, EmergentDimension] = field(default_factory=dict)
    research_paths: List[ResearchPath] = field(default_factory=list)
    cross_paradigm_opportunities: Optional[str] = None
    agents: List[ResearchAgent] = field(default_factory=list)
    research_report: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class FoundationalResearchTeam:
    """
    Research Team that conducts comprehensive foundation-based research.
    
    The Research Team uses a specialized multi-agent approach to discover
    potential project foundations and explore implementation possibilities
    across multiple paradigms. Each agent has access to powerful research
    tools but maintains full autonomy in how they conduct their exploration,
    ensuring maximum innovation potential without artificial constraints.
    """
    
    _instance = None
    
    def __new__(cls):
        """Ensure singleton pattern."""
        if cls._instance is None:
            cls._instance = super(FoundationalResearchTeam, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the Research Team."""
        if self._initialized:
            return
        
        self._initialized = True
        self.session_manager = SessionManager()
        self.doc_manager = DocumentManager()
        self.sessions: Dict[str, FoundationalResearchSession] = {}
        
        # System prompts for different agent types
        self.foundation_discovery_agent_prompt = """
        You are a Foundation Discovery Agent with exceptional insight into discovering viable project foundations.
        
        Your mission is to DISCOVER the complete spectrum of FUNDAMENTAL APPROACHES for implementing this project,
        identifying both conventional AND unconventional foundation options that could serve as the
        basis for all subsequent architectural decisions.
        
        You have access to these research tools that you can use however you determine is most effective:
        
        - Web search: search_custom(), fetch_full_page(), search_and_fetch()
        - Data analysis: extract_text_features()
        - Technology evaluation: create_evaluation_framework(), evaluate_technology(), compare_technologies(), generate_evaluation_report()
        - Visualization: create_ascii_table(), create_timeline()
        
        OBJECTIVES:
        
        1. DISCOVER PROJECT FOUNDATIONS, not predefined components:
           - Identify the complete spectrum of FUNDAMENTAL APPROACHES to building this project
           - Avoid assuming any predetermined architecture or components
           - Consider completely different ways the project could be approached
           - Look beyond conventional software patterns to identify unique foundation options
           
        2. EXPLORE EACH FOUNDATION across the FULL SPECTRUM of paradigms:
           - Established approaches (traditional, proven methodologies)
           - Mainstream current (contemporary popular solutions)
           - Cutting-edge (emerging technologies gaining traction)
           - Experimental (research-stage approaches)
           - Cross-paradigm (combinations from different domains)
           - First-principles (custom approaches designed specifically for this project)
        
        3. REMAIN COMPLETELY OPEN TO POSSIBILITIES:
           - Consider traditional software platforms
           - Explore hardware-software combinations
           - Examine novel interaction paradigms
           - Investigate pure algorithmic solutions
           - Consider edge computing approaches
           - Look for entirely new foundation types specific to this project
           - Explore hybrid combinations that don't fit existing categories
           
        4. MAP THE POSSIBILITY SPACE:
           - Document how each foundation approach creates a different implementation trajectory
           - Identify how foundation choices enable or constrain different capabilities
           - Explore how unconventional foundations might open unique implementation opportunities
           - Map the relationship between foundation approaches and potential project success
        
        5. PRESERVE INNOVATION POTENTIAL:
           - Avoid normalizing toward conventional enterprise patterns
           - Document approaches that might seem contradictory to mainstream thinking
           - Preserve foundation options that enable the project's unique characteristics
           - Challenge foundational assumptions about how systems "should" be built
        
        Your discoveries will define the trajectories for all subsequent architectural exploration.
        DOCUMENT THE COMPLETE POSSIBILITY SPACE without bias toward conventional approaches.
        """
        
        self.foundation_exploration_agent_prompt = """
        You are a Foundation Exploration Agent with deep expertise in exploring a specific foundation approach.
        
        Your mission is to thoroughly explore a particular project foundation approach across the paradigm spectrum,
        documenting how this foundation can be implemented in different ways and what emergent dimensions would
        arise from choosing this foundation.
        
        You have access to these research tools that you can use however you determine is most effective:
        
        - Web search: search_custom(), fetch_full_page(), search_and_fetch()
        - Data analysis: extract_text_features()
        - Technology evaluation: create_evaluation_framework(), evaluate_technology(), compare_technologies(), generate_evaluation_report()
        - Visualization: create_ascii_table()
        
        OBJECTIVES:
        
        1. EXPLORE THIS FOUNDATION ACROSS THE PARADIGM SPECTRUM:
           - Document how this foundation can be implemented using approaches from different paradigms
           - Identify established, mainstream, cutting-edge, experimental, and first-principles implementations
           - Explore variations within this foundation that represent different philosophical approaches
           - Document specific technologies and approaches for each paradigm within this foundation
        
        2. DISCOVER EMERGENT DIMENSIONS:
           - Identify what aspects of implementation would emerge from choosing this foundation
           - Document the unique dimensions that would need to be addressed in this foundation approach
           - Explore how these dimensions differ from those that would emerge from other foundations
           - Map relationships between emergent dimensions specific to this foundation
        
        3. EVALUATE FOUNDATION VIABILITY:
           - Analyze how well this foundation aligns with the project's unique requirements
           - Document strengths and limitations of this foundation approach
           - Identify scenarios where this foundation would be particularly advantageous
           - Assess implementation complexity, scalability, and other relevant factors
        
        4. PRESERVE INNOVATION POTENTIAL:
           - Resist normalizing toward conventional implementations of this foundation
           - Document unconventional approaches that might be particularly well-suited
           - Explore how this foundation could enable unique project characteristics
           - Challenge assumptions about how this foundation "should" be implemented
        
        5. IDENTIFY CROSS-FOUNDATION OPPORTUNITIES:
           - Note potential integration points with other foundation approaches
           - Identify where hybrid approaches might combine the strengths of multiple foundations
           - Document how this foundation could complement or be complemented by others
           - Explore potential novel combinations with other foundation approaches
        
        You have complete autonomy in how you approach this exploration. Your mission is to
        thoroughly understand this foundation, its emergent dimensions, its viability for this
        specific project, and how it could be implemented across the paradigm spectrum.
        """
        
        self.paradigm_agent_prompt = """
        You are a Paradigm Research Agent with deep expertise in a specific technological paradigm.
        
        Your mission is to EXPLORE how your paradigm can be applied to different project foundations and their
        emergent dimensions, discovering how your paradigm's unique philosophy can be expressed across
        different aspects of the architecture.
        
        You have access to these research tools that you can use however you determine is most effective:
        
        - Web search: search_custom(), fetch_full_page(), search_and_fetch()
        - Data analysis: extract_text_features()
        - Technology evaluation: create_evaluation_framework(), evaluate_technology(), compare_technologies(), generate_evaluation_report()
        - Visualization: create_ascii_table()
        
        OBJECTIVES:
        
        1. EXPLORE YOUR PARADIGM ACROSS FOUNDATIONS:
           - Document how your paradigm can be applied to different foundation approaches
           - Identify where your paradigm is particularly well-suited and where it faces challenges
           - Explore how your paradigm's philosophy would manifest within each foundation
           - Document specific technologies and approaches within your paradigm for each foundation
        
        2. PARADIGM-DIMENSION MAPPING:
           - For EACH emergent dimension, identify specific technologies within your paradigm
           - Explore how your paradigm addresses different concerns in each dimension
           - Document paradigm-specific implementations for each dimension within different foundations
           - Analyze how your paradigm's strengths align with different dimension requirements
        
        3. FOUNDATION RESPONSE:
           - Analyze how different foundation choices affect options within your paradigm
           - Document how your paradigm technologies integrate with various foundation approaches
           - Identify unique opportunities that emerge when your paradigm is combined with specific foundations
           - Map compatibility between foundation choices and your paradigm's technologies
        
        4. INNOVATION PRESERVATION:
           - Seek technologies that align with the project's unique characteristics
           - Document unconventional implementations that might be overlooked in standard analyses
           - Preserve the distinctive potential of your paradigm rather than normalizing to conventions
           - Identify how your paradigm can enable innovative approaches to the project's requirements
        
        5. CROSS-PARADIGM AWARENESS:
           - Note potential integration points with other paradigms
           - Identify where your paradigm's limitations might be complemented by other approaches
           - Document how technologies from your paradigm interact with those from other paradigms
           - Recognize boundary areas where cross-paradigm integration creates unique opportunities
        
        DOCUMENT THE FULL RANGE of technologies and approaches within your paradigm,
        not just the most popular or conventional options. Your mission is to map how your
        paradigm's distinctive philosophy can be expressed across all foundations and dimensions
        of the project.
        """
        
        self.path_agent_prompt = """
        You are a Path Research Agent with exceptional insight into creating cohesive implementation paths.
        
        Your mission is to explore complete implementation paths that emerge from specific foundation choices,
        tracing how these choices propagate through emergent dimensions to create distinct, cohesive
        architectural trajectories.
        
        You have access to these research tools that you can use however you determine is most effective:
        
        - Web search: search_custom(), fetch_full_page(), search_and_fetch()
        - Data analysis: extract_text_features()
        - Technology evaluation: create_evaluation_framework(), evaluate_technology(), compare_technologies(), generate_evaluation_report()
        - Visualization: create_ascii_table()
        
        OBJECTIVES:
        
        1. MAP COMPLETE IMPLEMENTATION PATHS:
           - Trace how a specific foundation choice creates a distinct implementation trajectory
           - Follow how this foundation gives rise to emergent dimensions with unique characteristics
           - Document a complete approach to implementing the project based on this foundation
           - Show how this path differs fundamentally from paths based on other foundations
        
        2. DOCUMENT COHESIVE IMPLEMENTATIONS:
           - Identify specific implementation approaches for each dimension in this path
           - Explore how different dimensions integrate cohesively within this path
           - Document communication patterns and data flows between components
           - Analyze how architectural concerns are addressed across the full implementation
        
        3. REVEAL EMERGENT PROPERTIES:
           - Identify unique capabilities that emerge from this specific implementation path
           - Document how this path enables distinctive project characteristics
           - Analyze quality attributes of the complete path (performance, scalability, etc.)
           - Reveal trade-offs that only become apparent when viewing the complete path
        
        4. ANALYZE IMPLEMENTATION CONSIDERATIONS:
           - Document practical implementation approaches for the complete path
           - Identify development and operational considerations specific to this path
           - Analyze team expertise requirements and learning curves
           - Explore deployment patterns and infrastructure needs
        
        5. PRESERVE PATH UNIQUENESS:
           - Maintain the distinctive characteristics of this implementation path
           - Resist normalizing unique paths toward conventional patterns
           - Document how this path embodies a particular philosophical approach
           - Highlight the unique advantages and capabilities of this approach
        
        Your exploration should document a COMPLETE, VIABLE IMPLEMENTATION PATH with
        distinctive characteristics, not converging toward generic patterns. The path should
        represent a coherent, implementable approach that addresses all project
        requirements with unique trade-offs and qualities.
        """
        
        self.integration_agent_prompt = """
        You are an Integration Research Agent with extraordinary ability to discover cross-foundation opportunities.
        
        Your mission is to identify novel integration patterns where different foundation approaches
        can be combined to create solutions that transcend the limitations of any single
        approach, discovering unexpected combinations that enable unique project capabilities.
        
        You have access to these research tools that you can use however you determine is most effective:
        
        - Web search: search_custom(), fetch_full_page(), search_and_fetch()
        - Data analysis: extract_text_features()
        - Technology evaluation: create_evaluation_framework(), evaluate_technology(), compare_technologies(), generate_evaluation_report()
        - Visualization: create_ascii_table()
        
        OBJECTIVES:
        
        1. DISCOVER UNEXPECTED COMBINATIONS:
           - Identify non-obvious ways to combine different foundation approaches
           - Find complementary foundations that address each other's limitations
           - Discover integration patterns that create unique capabilities
           - Look beyond conventional integrations to find novel arrangements
        
        2. MAP HYBRID FOUNDATION APPROACHES:
           - Document how different foundation approaches can be combined
           - Explore what new dimensions might emerge from hybrid foundations
           - Map communication protocols and data exchange patterns across foundation boundaries
           - Discover architectural patterns that enable cross-foundation integration
        
        3. ANALYZE INTEGRATION MECHANICS:
           - Document specific approaches for integrating disparate foundations
           - Explore interfaces, adapters, and communication mechanisms
           - Identify data transformation and translation requirements
           - Research implementation examples of similar integration patterns
        
        4. EVALUATE COMBINATORIAL VALUE:
           - Assess how combinations create value beyond individual foundations
           - Document unique capabilities that emerge from specific integrations
           - Analyze how combinations address limitations in individual approaches
           - Identify how integrations enable project-specific requirements
        
        5. PRESERVE INNOVATION INTEGRITY:
           - Focus on combinations that maintain the project's unique characteristics
           - Avoid defaulting to conventional integration patterns
           - Document how novel integrations can enable distinctive project qualities
           - Preserve architectural diversity rather than normalizing to standards
        
        Your exploration should REVEAL THE UNEXPECTED - finding integration opportunities
        that might not be immediately obvious but could create exceptional value for this
        specific project. Focus on discovering how different foundation approaches
        can complement each other in ways that preserve the project's distinctive vision.
        """
        
        self.synthesis_agent_prompt = """
        You are a Synthesis Research Agent with unparalleled ability to create comprehensive research reports.
        
        Your mission is to synthesize findings from all research agents into a comprehensive, multi-dimensional
        map of the possibility space, presenting the complete range of implementation options while preserving
        the richness and diversity of approaches discovered during the research process.
        
        You have access to these research tools that you can use however you determine is most effective:
        
        - Data analysis: extract_text_features()
        - Technology evaluation: create_evaluation_framework(), evaluate_technology(), compare_technologies(), generate_evaluation_report()
        - Visualization: create_ascii_table()
        
        OBJECTIVES:
        
        1. CREATE A COMPREHENSIVE MAP:
           - Synthesize all research findings into a cohesive whole
           - Preserve the full richness of foundation approaches and their emergent dimensions
           - Show relationships between foundations, paradigms, and implementation paths
           - Create visualizations that illuminate the multi-dimensional nature of choices
        
        2. DOCUMENT THE FULL POSSIBILITY SPACE:
           - Present the complete spectrum of foundation options discovered during research
           - Document multiple viable implementation paths with diverse characteristics
           - Map cross-foundation opportunities and integration patterns
           - Preserve distinctly different approaches rather than converging on a "best" solution
        
        3. ILLUMINATE ARCHITECTURAL IMPLICATIONS:
           - Analyze how different foundation choices create fundamentally different architectures
           - Document trade-offs inherent in different approaches
           - Show how foundation choices give rise to different emergent dimensions
           - Highlight unique capabilities enabled by specific foundation approaches
        
        4. CREATE POWERFUL VISUALIZATIONS:
           - Foundation maps showing the spectrum of options
           - Path diagrams illustrating complete implementation approaches
           - Integration maps showing hybrid foundation opportunities
           - Trade-off matrices comparing different approaches
        
        5. PRESERVE INNOVATION POTENTIAL:
           - Maintain the diversity of approaches without defaulting to conventions
           - Present findings without bias toward mainstream solutions
           - Preserve the project's unique characteristics across all options
           - Highlight unconventional approaches that align with the project's distinctive nature
        
        Your report should be the DEFINITIVE RESOURCE for architectural decision-making -
        a comprehensive map of the possibility space that enables informed choices
        without normalizing toward conventions. It should present the full spectrum
        of viable approaches with their implications, trade-offs, and unique characteristics.
        """
    
    @handle_errors
    def get_session(self, session_id: Optional[str] = None) -> FoundationalResearchSession:
        """Get a session by ID or the current session."""
        if session_id:
            session = self.sessions.get(session_id)
            if not session:
                raise ValueError(f"Session {session_id} not found")
            return session
        
        # Get current session from session manager
        current_session = self.session_manager.get_current_session()
        if not current_session:
            raise ValueError("No active session found")
        
        session_id = current_session.id
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        return session
    
    @handle_async_errors
    async def create_session(self, session_id: str, research_requirements: str) -> FoundationalResearchSession:
        """
        Create a new research session.
        
        Args:
            session_id: Session ID
            research_requirements: Research requirements document content
            
        Returns:
            Created research session
        """
        logger.info(f"Creating research session {session_id}")
        
        # Create a new session
        session = FoundationalResearchSession(
            id=session_id,
            requirements=research_requirements
        )
        
        # Store in sessions dict
        self.sessions[session_id] = session
        
        logger.info(f"Created foundational research session")
        return session
    
    @handle_async_errors
    async def initialize_research_agents(self, session_id: str) -> List[ResearchAgent]:
        """
        Initialize specialized research agents for the session.
        
        Args:
            session_id: Session ID
            
        Returns:
            List of created research agents
        """
        session = self.get_session(session_id)
        
        # Create specialized agents for different research aspects
        agents = []
        
        # Create foundation discovery agents (to identify potential foundations)
        for i in range(2):  # Start with 2 discovery agents
            agent = ResearchAgent(
                id=f"foundation-discovery-{i+1}",
                type=ResearchAgentType.FOUNDATION,
                name=f"Foundation Discovery Agent {i+1}",
                focus_area="Project Foundation Discovery",
                system_prompt=self.foundation_discovery_agent_prompt,
                messages=[create_system_prompt(self.foundation_discovery_agent_prompt)]
            )
            agents.append(agent)
        
        # Create paradigm agents (one per paradigm category)
        for i, paradigm in enumerate(ParadigmCategory):
            agent = ResearchAgent(
                id=f"paradigm-{paradigm.value}",
                type=ResearchAgentType.PARADIGM,
                name=f"{paradigm.value.replace('_', ' ').title()} Paradigm Agent",
                focus_area=paradigm.value,
                system_prompt=self.paradigm_agent_prompt,
                messages=[create_system_prompt(self.paradigm_agent_prompt)]
            )
            agents.append(agent)
        
        # Create path agents (for exploring implementation paths)
        # We'll start with 2 but can add more as needed
        for i in range(2):
            agent = ResearchAgent(
                id=f"path-{i+1}",
                type=ResearchAgentType.PATH,
                name=f"Path Research Agent {i+1}",
                focus_area=f"Implementation Path {i+1}",
                system_prompt=self.path_agent_prompt,
                messages=[create_system_prompt(self.path_agent_prompt)]
            )
            agents.append(agent)
        
        # Create integration agent
        integration_agent = ResearchAgent(
            id="integration-1",
            type=ResearchAgentType.INTEGRATION,
            name="Integration Research Agent",
            focus_area="Cross-foundation Integration",
            system_prompt=self.integration_agent_prompt,
            messages=[create_system_prompt(self.integration_agent_prompt)]
        )
        agents.append(integration_agent)
        
        # Create synthesis agent
        synthesis_agent = ResearchAgent(
            id="synthesis-1",
            type=ResearchAgentType.SYNTHESIS,
            name="Synthesis Research Agent",
            focus_area="Research Synthesis",
            system_prompt=self.synthesis_agent_prompt,
            messages=[create_system_prompt(self.synthesis_agent_prompt)]
        )
        agents.append(synthesis_agent)
        
        # Add agents to the session
        session.agents = agents
        
        logger.info(f"Initialized {len(agents)} research agents for session {session_id}")
        return agents
    
    @handle_async_errors
    async def discover_project_foundations(self, session_id: str) -> Dict[str, Any]:
        """
        Start the foundation discovery phase to identify potential project foundations.
        
        Args:
            session_id: Session ID
            
        Returns:
            Results of the foundation discovery
        """
        session = self.get_session(session_id)
        
        # Get foundation discovery agents
        discovery_agents = [
            agent for agent in session.agents 
            if agent.type == ResearchAgentType.FOUNDATION and "discovery" in agent.id
        ]
        
        if not discovery_agents:
            logger.error(f"No foundation discovery agents available for session {session_id}")
            return {"status": "error", "message": "No foundation discovery agents available"}
        
        # Research potential foundations concurrently
        discovery_tasks = []
        for agent in discovery_agents:
            task = asyncio.create_task(
                self._discover_potential_foundations(
                    session_id=session_id, 
                    agent_id=agent.id
                )
            )
            discovery_tasks.append(task)
        
        # Wait for all foundation discovery to complete
        discovery_results = await asyncio.gather(*discovery_tasks)
        
        # Process discovery results to extract foundation approaches
        foundations = await self._extract_foundation_approaches(session_id, discovery_results)
        
        # Store foundations in session
        for foundation_id, foundation in foundations.items():
            session.project_foundations[foundation_id] = foundation
        
        logger.info(f"Discovered {len(foundations)} potential foundation approaches for session {session_id}")
        return {"status": "success", "foundations": foundations}
    
    @handle_async_errors
    async def _discover_potential_foundations(
        self, 
        session_id: str, 
        agent_id: str
    ) -> Dict[str, Any]:
        """
        Use a specialized agent to discover potential project foundations.
        
        Args:
            session_id: Session ID
            agent_id: Agent ID
            
        Returns:
            Discovery results
        """
        session = self.get_session(session_id)
        
        # Get the agent
        agent = next((a for a in session.agents if a.id == agent_id), None)
        if not agent:
            logger.error(f"Agent {agent_id} not found")
            return {"status": "error", "message": f"Agent {agent_id} not found"}
        
        # Set agent status
        agent.status = "discovering"
        
        # Create discovery prompt
        discovery_prompt = f"""
        Research Task: Discover Potential Project Foundations
        
        Research Requirements:
        {session.requirements}
        
        You are tasked with discovering the COMPLETE SPECTRUM of FOUNDATION APPROACHES
        for implementing this project:
        
        1. DISCOVER FUNDAMENTALLY DIFFERENT APPROACHES:
           - What are the completely different ways this project could be implemented?
           - Identify a diverse range of foundation approaches, NOT just variations on the same theme
           - Consider both conventional AND unconventional foundation options
           - Look beyond standard software patterns to consider novel foundation approaches
           
        2. REMAIN COMPLETELY OPEN TO POSSIBILITIES:
           - Consider traditional software platforms
           - Explore hardware-software combinations
           - Examine novel interaction paradigms
           - Investigate pure algorithmic solutions
           - Consider edge computing approaches
           - Look for entirely new foundation types specific to this project
           - Explore hybrid combinations that don't fit existing categories
        
        3. FOR EACH POTENTIAL FOUNDATION:
           - Provide a clear name and description
           - Identify which paradigm category it primarily belongs to
           - Describe key characteristics and implications
           - Note what makes this foundation approach distinctive
           - Identify what kinds of dimensions would emerge from this foundation
        
        4. AVOID PREMATURE FILTERING:
           - Do not eliminate options based on perceived difficulty
           - Include approaches that seem unconventional or challenging
           - Document the complete possibility space, not just "reasonable" options
           - Include options from across the paradigm spectrum
        
        5. PRESERVE THE PROJECT'S UNIQUENESS:
           - Consider how each foundation approach enables the unique aspects of this project
           - Avoid forcing the project into conventional implementation patterns
           - Identify approaches that preserve what makes this project distinctive
           - Challenge assumptions about how systems "should" be built
        
        You have complete autonomy in how you approach this discovery. Use the available tools
        in whatever way you determine will produce the most comprehensive exploration.
        
        Your discoveries will define the starting points for all subsequent research.
        DOCUMENT THE COMPLETE POSSIBILITY SPACE without bias toward conventional approaches.
        """
        
        # Add the discovery prompt to agent messages
        agent.messages.append(create_user_prompt(discovery_prompt))
        
        # Get the agent's response
        response = await send_prompt(agent.messages)
        
        # Add the response to the agent messages
        agent.messages.append(create_assistant_prompt(response.content))
        
        # Store findings directly - no extraction, preserve all information
        agent.findings.append(response.content)
        agent.status = "completed"
        
        logger.info(f"Foundation discovery completed by agent {agent_id}")
        return {
            "status": "success",
            "agent_id": agent_id,
            "content": response.content
        }
    
    @handle_async_errors
    async def _extract_foundation_approaches(
        self,
        session_id: str,
        discovery_results: List[Dict[str, Any]]
    ) -> Dict[str, ProjectFoundation]:
        """
        Extract foundation approaches from discovery results.
        
        Args:
            session_id: Session ID
            discovery_results: Results from foundation discovery agents
            
        Returns:
            Dictionary of foundation approaches
        """
        session = self.get_session(session_id)
        
        # Create an agent to analyze and extract foundation approaches
        analysis_prompt = """
        You are a Foundation Analysis Agent. Your task is to analyze the discovery results from multiple agents
        and extract a comprehensive list of distinct project foundation approaches.
        
        For each identified foundation approach, extract:
        1. A clear name
        2. A concise description
        3. The paradigm category it belongs to (established, mainstream, cutting-edge, experimental, cross-paradigm, or first-principles)
        4. Any research areas mentioned for this foundation
        
        Combine similar foundation approaches, but preserve truly distinct approaches even if they seem unusual.
        
        Return your analysis in a structured JSON format:
        {
          "foundations": [
            {
              "id": "foundation-1",
              "name": "Foundation Name",
              "description": "Description of the foundation approach",
              "paradigm_category": "one of the paradigm categories",
              "research_areas": [
                {"name": "Research Area 1", "description": "Description of the research area"}
              ]
            }
          ]
        }
        """
        
        # Combine all discovery results
        all_content = "\n\n".join([result["content"] for result in discovery_results if result["status"] == "success"])
        
        # Create the complete prompt
        complete_prompt = f"{analysis_prompt}\n\nDiscovery Results:\n{all_content}"
        
        # Create messages for the analysis
        messages = [
            create_system_prompt(analysis_prompt),
            create_user_prompt(f"Discovery Results:\n{all_content}")
        ]
        
        # Get analysis response
        response = await send_prompt(messages)
        
        # Extract JSON from response
        import json
        import re
        
        # Look for JSON pattern in the response
        json_match = re.search(r'```json\n(.*?)\n```', response.content, re.DOTALL)
        if not json_match:
            json_match = re.search(r'{.*}', response.content, re.DOTALL)
        
        if not json_match:
            logger.error("Could not extract JSON from analysis response")
            return {}
        
        json_str = json_match.group(1) if json_match.group(0).startswith('```') else json_match.group(0)
        
        try:
            data = json.loads(json_str)
            # Convert to dictionary of ProjectFoundation objects
            foundations = {}
            for foundation_data in data["foundations"]:
                foundation = ProjectFoundation(
                    name=foundation_data["name"],
                    description=foundation_data["description"],
                    paradigm_category=foundation_data["paradigm_category"],
                    research_areas=foundation_data.get("research_areas", [])
                )
                foundations[foundation_data["id"]] = foundation
            
            return foundations
        except Exception as e:
            logger.error(f"Error parsing foundation approaches: {str(e)}")
            return {}
    
    @handle_async_errors
    async def explore_foundation_approaches(self, session_id: str) -> Dict[str, Any]:
        """
        Explore each viable foundation approach across paradigms.
        
        Args:
            session_id: Session ID
            
        Returns:
            Results of the foundation exploration
        """
        session = self.get_session(session_id)
        
        # Check if foundations have been discovered
        if not session.project_foundations:
            logger.error(f"No project foundations discovered for session {session_id}")
            return {"status": "error", "message": "No project foundations discovered"}
        
        # Create foundation exploration agents for each foundation
        exploration_agents = []
        for i, (foundation_id, foundation) in enumerate(session.project_foundations.items()):
            agent = ResearchAgent(
                id=f"foundation-exploration-{foundation_id}",
                type=ResearchAgentType.FOUNDATION,
                name=f"Foundation Exploration Agent for {foundation.name}",
                focus_area=foundation_id,
                system_prompt=self.foundation_exploration_agent_prompt,
                messages=[create_system_prompt(self.foundation_exploration_agent_prompt)]
            )
            exploration_agents.append(agent)
            session.agents.append(agent)
        
        # Explore all foundations concurrently
        exploration_tasks = []
        for agent in exploration_agents:
            foundation_id = agent.focus_area
            task = asyncio.create_task(
                self._explore_foundation_approach(
                    session_id=session_id, 
                    agent_id=agent.id,
                    foundation_id=foundation_id
                )
            )
            exploration_tasks.append(task)
        
        # Wait for all foundation exploration to complete
        exploration_results = await asyncio.gather(*exploration_tasks)
        
        # Process exploration results to extract emergent dimensions
        for result in exploration_results:
            if result["status"] == "success":
                foundation_id = result["foundation_id"]
                
                # Extract emergent dimensions from exploration results
                dimensions = await self._extract_emergent_dimensions(
                    session_id=session_id,
                    foundation_id=foundation_id,
                    exploration_content=result["content"]
                )
                
                # Store emergent dimensions in session
                for dimension_id, dimension in dimensions.items():
                    session.emergent_dimensions[dimension_id] = dimension
        
        logger.info(f"Explored {len(exploration_results)} foundation approaches for session {session_id}")
        return {"status": "success", "results": exploration_results}
    
    @handle_async_errors
    async def _explore_foundation_approach(
        self, 
        session_id: str, 
        agent_id: str,
        foundation_id: str
    ) -> Dict[str, Any]:
        """
        Explore a specific foundation approach using a specialized agent.
        
        Args:
            session_id: Session ID
            agent_id: Agent ID
            foundation_id: Foundation ID to explore
            
        Returns:
            Exploration results
        """
        session = self.get_session(session_id)
        
        # Get the agent
        agent = next((a for a in session.agents if a.id == agent_id), None)
        if not agent:
            logger.error(f"Agent {agent_id} not found")
            return {"status": "error", "message": f"Agent {agent_id} not found"}
        
        # Get the foundation
        foundation = session.project_foundations.get(foundation_id)
        if not foundation:
            logger.error(f"Foundation {foundation_id} not found")
            return {"status": "error", "message": f"Foundation {foundation_id} not found"}
        
        # Set agent status
        agent.status = "exploring"
        
        # Create exploration prompt
        exploration_prompt = f"""
        Research Task: Explore Foundation Approach "{foundation.name}"
        
        Foundation Description:
        {foundation.description}
        
        Paradigm Category:
        {foundation.paradigm_category}
        
        Research Areas:
        {foundation.research_areas}
        
        Research Requirements:
        {session.requirements}
        
        You are tasked with exploring this foundation approach in depth:
        
        1. EXPLORE THIS FOUNDATION ACROSS THE PARADIGM SPECTRUM:
           - How can this foundation be implemented using approaches from different paradigms?
           - What established, mainstream, cutting-edge, experimental, and first-principles implementations exist?
           - What variations exist within this foundation that represent different philosophical approaches?
           - What specific technologies and approaches could be used for each paradigm within this foundation?
        
        2. DISCOVER EMERGENT DIMENSIONS:
           - What aspects of implementation would emerge from choosing this foundation?
           - What unique dimensions would need to be addressed in this foundation approach?
           - How do these dimensions differ from those that would emerge from other foundations?
           - What relationships exist between emergent dimensions specific to this foundation?
        
        3. EVALUATE FOUNDATION VIABILITY:
           - How well does this foundation align with the project's unique requirements?
           - What are the strengths and limitations of this foundation approach?
           - In what scenarios would this foundation be particularly advantageous?
           - What is the implementation complexity, scalability, and other relevant factors?
        
        4. PRESERVE INNOVATION POTENTIAL:
           - Avoid normalizing toward conventional implementations of this foundation
           - What unconventional approaches might be particularly well-suited?
           - How could this foundation enable unique project characteristics?
           - What assumptions about how this foundation "should" be implemented need challenging?
        
        5. IDENTIFY CROSS-FOUNDATION OPPORTUNITIES:
           - What potential integration points exist with other foundation approaches?
           - Where might hybrid approaches combine the strengths of multiple foundations?
           - How could this foundation complement or be complemented by others?
           - What novel combinations with other foundation approaches might be valuable?
        
        You have complete autonomy in how you approach this exploration. Use the available tools
        in whatever way you determine will produce the most comprehensive exploration.
        
        Your mission is to thoroughly understand this foundation, its emergent dimensions,
        its viability for this specific project, and how it could be implemented across
        the paradigm spectrum.
        """
        
        # Add the exploration prompt to agent messages
        agent.messages.append(create_user_prompt(exploration_prompt))
        
        # Get the agent's response
        response = await send_prompt(agent.messages)
        
        # Add the response to the agent messages
        agent.messages.append(create_assistant_prompt(response.content))
        
        # Store findings directly - no extraction, preserve all information
        agent.findings.append(response.content)
        agent.status = "completed"
        
        # Store the raw research in the foundation
        foundation.research_content[agent.id] = response.content
        
        # Mark foundation as completed
        foundation.completed = True
        
        logger.info(f"Foundation exploration completed for {foundation.name}")
        return {
            "status": "success",
            "agent_id": agent_id,
            "foundation_id": foundation_id,
            "content": response.content
        }
    
    @handle_async_errors
    async def _extract_emergent_dimensions(
        self,
        session_id: str,
        foundation_id: str,
        exploration_content: str
    ) -> Dict[str, EmergentDimension]:
        """
        Extract emergent dimensions from foundation exploration results.
        
        Args:
            session_id: Session ID
            foundation_id: Foundation ID
            exploration_content: Content from foundation exploration
            
        Returns:
            Dictionary of emergent dimensions
        """
        session = self.get_session(session_id)
        
        # Create an agent to analyze and extract emergent dimensions
        analysis_prompt = """
        You are a Dimension Analysis Agent. Your task is to analyze the foundation exploration results
        and extract all emergent dimensions that would arise from this foundation approach.
        
        For each identified emergent dimension, extract:
        1. A clear name
        2. A concise description
        3. Any research areas mentioned for this dimension
        
        Return your analysis in a structured JSON format:
        {
          "dimensions": [
            {
              "id": "dimension-1",
              "name": "Dimension Name",
              "description": "Description of the dimension",
              "research_areas": [
                {"name": "Research Area 1", "description": "Description of the research area"}
              ]
            }
          ]
        }
        """
        
        # Create the complete prompt
        complete_prompt = f"{analysis_prompt}\n\nFoundation Exploration Results:\n{exploration_content}"
        
        # Create messages for the analysis
        messages = [
            create_system_prompt(analysis_prompt),
            create_user_prompt(f"Foundation Exploration Results:\n{exploration_content}")
        ]
        
        # Get analysis response
        response = await send_prompt(messages)
        
        # Extract JSON from response
        import json
        import re
        
        # Look for JSON pattern in the response
        json_match = re.search(r'```json\n(.*?)\n```', response.content, re.DOTALL)
        if not json_match:
            json_match = re.search(r'{.*}', response.content, re.DOTALL)
        
        if not json_match:
            logger.error("Could not extract JSON from analysis response")
            return {}
        
        json_str = json_match.group(1) if json_match.group(0).startswith('```') else json_match.group(0)
        
        try:
            data = json.loads(json_str)
            # Convert to dictionary of EmergentDimension objects
            dimensions = {}
            for dimension_data in data["dimensions"]:
                dimension = EmergentDimension(
                    name=dimension_data["name"],
                    description=dimension_data["description"],
                    foundation_id=foundation_id,
                    research_areas=dimension_data.get("research_areas", [])
                )
                # Create unique ID for dimension that includes foundation ID
                dimension_id = f"{foundation_id}-{dimension_data['id']}"
                dimensions[dimension_id] = dimension
            
            return dimensions
        except Exception as e:
            logger.error(f"Error parsing emergent dimensions: {str(e)}")
            return {}
    
    @handle_async_errors
    async def generate_research_paths(self, session_id: str) -> List[ResearchPath]:
        """
        Generate research paths based on foundation choices.
        
        Args:
            session_id: Session ID
            
        Returns:
            List of research paths
        """
        session = self.get_session(session_id)
        
        # Check if foundations have been explored
        completed_foundations = [
            foundation_id for foundation_id, foundation in session.project_foundations.items() 
            if foundation.completed
        ]
        
        if not completed_foundations:
            logger.warning(f"No completed foundations found for session {session_id}")
            return []
        
        # Create paths for each foundation
        paths = []
        
        for foundation_id in completed_foundations:
            foundation = session.project_foundations[foundation_id]
            
            # Create a path for this foundation
            path = ResearchPath(
                name=f"{foundation.name} Implementation Path",
                description=f"Implementation path based on the {foundation.name} foundation approach",
                foundation_id=foundation_id
            )
            
            # Add relevant emergent dimensions to the path
            path_dimensions = []
            for dimension_id, dimension in session.emergent_dimensions.items():
                if dimension.foundation_id == foundation_id:
                    path_dimensions.append(dimension)
            
            path.emergent_dimensions = path_dimensions
            paths.append(path)
        
        # Add paths to the session
        session.research_paths = paths
        
        return paths
    
    @handle_async_errors
    async def start_path_research(self, session_id: str) -> Dict[str, Any]:
        """
        Start the path research phase.
        
        Args:
            session_id: Session ID
            
        Returns:
            Results of the path research
        """
        session = self.get_session(session_id)
        
        # Get path agents
        path_agents = [
            agent for agent in session.agents 
            if agent.type == ResearchAgentType.PATH
        ]
        
        if not path_agents:
            logger.error(f"No path agents available for session {session_id}")
            return {"status": "error", "message": "No path agents available"}
        
        # Generate paths if not already created
        if not session.research_paths:
            session.research_paths = await self.generate_research_paths(session_id)
        
        # Assign paths to path agents (round-robin if more paths than agents)
        path_assignments = {}
        for i, path in enumerate(session.research_paths):
            agent_index = i % len(path_agents)
            path_agent = path_agents[agent_index]
            
            if path_agent.id not in path_assignments:
                path_assignments[path_agent.id] = []
            
            path_assignments[path_agent.id].append(path.name)
        
        # Research all paths concurrently
        path_tasks = []
        for agent_id, path_names in path_assignments.items():
            for path_name in path_names:
                task = asyncio.create_task(
                    self._research_path(
                        session_id=session_id, 
                        agent_id=agent_id,
                        path_name=path_name
                    )
                )
                path_tasks.append(task)
        
        # Wait for all path research to complete
        path_results = await asyncio.gather(*path_tasks)
        
        logger.info(f"Completed path research for session {session_id}")
        return {"status": "success", "results": path_results}
    
    @handle_async_errors
    async def _research_path(
        self, 
        session_id: str, 
        agent_id: str, 
        path_name: str
    ) -> Dict[str, Any]:
        """
        Research a specific implementation path.
        
        Args:
            session_id: Session ID
            agent_id: Agent ID
            path_name: Name of the path to research
            
        Returns:
            Research results
        """
        session = self.get_session(session_id)
        
        # Get the agent
        agent = next((a for a in session.agents if a.id == agent_id), None)
        if not agent:
            logger.error(f"Agent {agent_id} not found")
            return {"status": "error", "message": f"Agent {agent_id} not found"}
        
        # Get the path
        path = next((p for p in session.research_paths if p.name == path_name), None)
        if not path:
            logger.error(f"Path {path_name} not found")
            return {"status": "error", "message": f"Path {path_name} not found"}
        
        # Get the foundation
        foundation = session.project_foundations.get(path.foundation_id)
        if not foundation:
            logger.error(f"Foundation {path.foundation_id} not found")
            return {"status": "error", "message": f"Foundation {path.foundation_id} not found"}
        
        # Set agent status
        agent.status = "researching"
        
        # Collect foundation research to share with the path agent
        foundation_research = ""
        for agent_id, content in foundation.research_content.items():
            foundation_research += f"## Foundation Research (Agent: {agent_id})\n\n{content}\n\n"
        
        # Create research prompt
        research_prompt = f"""
        Research Task: Explore implementation path "{path_name}"
        
        Foundation:
        {foundation.name}: {foundation.description}
        
        Foundation Research:
        {foundation_research}
        
        Emergent Dimensions:
        {[f"{d.name}: {d.description}" for d in path.emergent_dimensions]}
        
        Research Requirements:
        {session.requirements}
        
        You are tasked with exploring a COMPLETE IMPLEMENTATION PATH based on this foundation:
        
        1. MAP A COHESIVE IMPLEMENTATION APPROACH:
           - How would this foundation choice be implemented in practice?
           - How would each emergent dimension be addressed within this approach?
           - What specific implementation strategies would work well together?
           - How does this implementation path differ from paths based on other foundations?
        
        2. CREATE A COMPLETE IMPLEMENTATION MAP:
           - What specific implementation approach would be used for each dimension?
           - How would different dimensions integrate cohesively?
           - What communication patterns and data flows would exist?
           - How would architectural concerns be addressed across the implementation?
        
        3. DISCOVER EMERGENT PROPERTIES:
           - What unique capabilities would emerge from this implementation path?
           - How would this path enable distinctive project characteristics?
           - What quality attributes would this path provide (performance, scalability, etc.)?
           - What trade-offs would this path involve?
        
        4. DOCUMENT IMPLEMENTATION CONSIDERATIONS:
           - What practical implementation approaches would be most suitable?
           - What development and operational considerations would be important?
           - What team expertise would be required?
           - What deployment patterns and infrastructure would be needed?
        
        5. PRESERVE PATH UNIQUENESS:
           - Maintain the distinctive characteristics of this implementation path
           - Resist normalizing toward conventional architectural patterns
           - How does this path embody a particular philosophical approach?
           - What are the unique advantages and capabilities of this approach?
        
        You have complete autonomy in how you approach this research. Use the available tools
        in whatever way you determine will produce the most comprehensive exploration.
        
        Your exploration should document a COMPLETE, VIABLE IMPLEMENTATION PATH with
        distinctive characteristics, not converging toward generic patterns. The path should
        represent a coherent, implementable approach that addresses all project
        requirements with unique trade-offs and qualities.
        """
        
        # Add the research prompt to agent messages
        agent.messages.append(create_user_prompt(research_prompt))
        
        # Get the agent's response
        response = await send_prompt(agent.messages)
        
        # Add the response to the agent messages
        agent.messages.append(create_assistant_prompt(response.content))
        
        # Store findings directly - no extraction, preserve all information
        agent.findings.append(response.content)
        agent.status = "completed"
        
        # Store the raw research in the path
        path.research_content = response.content
        
        logger.info(f"Path research completed for {path_name}")
        return {
            "status": "success",
            "agent_id": agent_id,
            "path_name": path_name
        }
    
    @handle_async_errors
    async def start_integration_research(self, session_id: str) -> Dict[str, Any]:
        """
        Start the integration research phase.
        
        Args:
            session_id: Session ID
            
        Returns:
            Results of the integration research
        """
        session = self.get_session(session_id)
        
        # Get integration agent
        integration_agent = next(
            (a for a in session.agents if a.type == ResearchAgentType.INTEGRATION),
            None
        )
        
        if not integration_agent:
            logger.error(f"No integration agent available for session {session_id}")
            return {"status": "error", "message": "No integration agent available"}
        
        # Set agent status
        integration_agent.status = "researching"
        
        # Collect information about foundations and paths
        foundations_info = []
        for foundation_id, foundation in session.project_foundations.items():
            if foundation.completed:
                foundations_info.append(f"## {foundation.name}\n{foundation.description}")
        
        paths_info = []
        for path in session.research_paths:
            if path.research_content:
                paths_info.append(f"## {path.name}\n{path.description}\n\nResearch Content:\n{path.research_content}")
        
        # Create research prompt
        research_prompt = f"""
        Research Task: Identify cross-foundation integration opportunities
        
        Project Foundations:
        {"".join(foundations_info)}
        
        Research Paths:
        {"".join(paths_info)}
        
        Research Requirements:
        {session.requirements}
        
        You are tasked with discovering NOVEL INTEGRATION OPPORTUNITIES across foundation approaches:
        
        1. DISCOVER UNEXPECTED COMBINATIONS:
           - What non-obvious ways could different foundation approaches be combined?
           - How might complementary foundations address each other's limitations?
           - What integration patterns could create unique capabilities?
           - What novel arrangements might exist beyond conventional integrations?
        
        2. MAP HYBRID FOUNDATION APPROACHES:
           - How could different foundation approaches be combined?
           - What new dimensions might emerge from hybrid foundations?
           - What communication protocols could enable cross-foundation integration?
           - What architectural patterns could enable combinations of foundations?
        
        3. ANALYZE INTEGRATION MECHANICS:
           - What specific approaches could integrate disparate foundations?
           - What interfaces, adapters, or communication mechanisms would be needed?
           - What data transformation requirements would exist?
           - Are there existing implementation examples of similar integration patterns?
        
        4. EVALUATE COMBINATORIAL VALUE:
           - How would combinations create value beyond individual foundations?
           - What unique capabilities would emerge from specific integrations?
           - How would combinations address limitations in individual approaches?
           - How would integrations enable project-specific requirements?
        
        5. PRESERVE INNOVATION INTEGRITY:
           - Focus on combinations that maintain the project's unique characteristics
           - Avoid defaulting to conventional integration patterns
           - How could novel integrations enable distinctive project qualities?
           - How could we preserve architectural diversity rather than normalizing to standards?
        
        You have complete autonomy in how you approach this research. Use the available tools
        in whatever way you determine will produce the most comprehensive exploration.
        
        Your exploration should REVEAL THE UNEXPECTED - finding integration opportunities
        that might not be immediately obvious but could create exceptional value for this
        specific project. Focus on discovering how different foundation approaches
        can complement each other in ways that preserve the project's distinctive vision.
        """
        
        # Add the research prompt to agent messages
        integration_agent.messages.append(create_user_prompt(research_prompt))
        
        # Get the agent's response
        response = await send_prompt(integration_agent.messages)
        
        # Add the response to the agent messages
        integration_agent.messages.append(create_assistant_prompt(response.content))
        
        # Store findings directly - no extraction, preserve all information
        integration_agent.findings.append(response.content)
        integration_agent.status = "completed"
        
        # Store the raw integration opportunities in the session
        session.cross_paradigm_opportunities = response.content
        
        logger.info(f"Integration research completed for session {session_id}")
        return {
            "status": "success",
            "agent_id": integration_agent.id
        }
    
    @handle_async_errors
    async def create_research_report(self, session_id: str) -> Optional[str]:
        """
        Create a comprehensive research report.
        
        Args:
            session_id: Session ID
            
        Returns:
            Path to the saved research report
        """
        session = self.get_session(session_id)
        
        # Get synthesis agent
        synthesis_agent = next(
            (a for a in session.agents if a.type == ResearchAgentType.SYNTHESIS),
            None
        )
        
        if not synthesis_agent:
            logger.error(f"No synthesis agent available for session {session_id}")
            return None
        
        # Set agent status
        synthesis_agent.status = "synthesizing"
        
        # Collect all foundation information
        foundations_info = []
        for foundation_id, foundation in session.project_foundations.items():
            if foundation.completed:
                foundation_content = f"## {foundation.name}\n{foundation.description}\n\n"
                if foundation.research_content:
                    # Include first 1000 characters of research content for each foundation
                    for agent_id, content in foundation.research_content.items():
                        content_preview = content[:1000] + "..." if len(content) > 1000 else content
                        foundation_content += f"### Research by {agent_id}:\n{content_preview}\n\n"
                foundations_info.append(foundation_content)
        
        # Collect all path information
        paths_info = []
        for path in session.research_paths:
            if path.research_content:
                path_content = f"## {path.name}\n{path.description}\n\n"
                # Include first 1000 characters of research content
                content_preview = path.research_content[:1000] + "..." if len(path.research_content) > 1000 else path.research_content
                path_content += f"### Research Content:\n{content_preview}\n\n"
                paths_info.append(path_content)
        
        # Create research prompt
        report_prompt = f"""
        Research Task: Create a comprehensive foundational research report
        
        Research Requirements:
        {session.requirements}
        
        Project Foundations:
        {"".join(foundations_info)}
        
        Research Paths:
        {"".join(paths_info)}
        
        Cross-Foundation Opportunities:
        {session.cross_paradigm_opportunities}
        
        You are tasked with creating a DEFINITIVE RESEARCH REPORT that:
        
        1. CREATES A COMPREHENSIVE FOUNDATION MAP:
           - Synthesize all research findings into a cohesive whole
           - Present the full spectrum of foundation approaches discovered
           - Document relationships between foundations, their emergent dimensions, and implementation paths
           - Create visualizations that illuminate the multi-dimensional nature of choices
        
        2. DOCUMENT THE COMPLETE POSSIBILITY SPACE:
           - Present all viable foundation approaches with their characteristics
           - Document multiple implementation paths with their distinctive qualities
           - Map cross-foundation opportunities and integration patterns
           - Preserve distinctly different approaches rather than converging on a "best" solution
        
        3. ILLUMINATE ARCHITECTURAL IMPLICATIONS:
           - Analyze how different foundation choices create fundamentally different architectures
           - Document trade-offs inherent in different approaches
           - Show how foundation choices give rise to different emergent dimensions
           - Highlight unique capabilities enabled by specific foundation approaches
        
        4. CREATE POWERFUL VISUALIZATIONS:
           - Foundation maps showing the spectrum of options
           - Path diagrams illustrating complete implementation approaches
           - Integration maps showing hybrid foundation opportunities
           - Trade-off matrices comparing different approaches
        
        5. PRESERVE INNOVATION POTENTIAL:
           - Maintain the diversity of approaches without defaulting to conventions
           - Present findings without bias toward mainstream solutions
           - Preserve the project's unique characteristics across all options
           - Highlight unconventional approaches that align with the project's distinctive nature
        
        You have complete autonomy in how you approach this task. Use the available visualization
        tools in whatever way you determine will create the most illuminating representations.
        
        Your report should be the ULTIMATE ARCHITECTURAL RESOURCE - a comprehensive map
        of the possibility space that enables informed choices without normalizing toward
        conventions. It should present the full spectrum of viable approaches with their
        implications, trade-offs, and unique characteristics.
        """
        
        # Add the research prompt to agent messages
        synthesis_agent.messages.append(create_user_prompt(report_prompt))
        
        # Get the agent's response
        response = await send_prompt(synthesis_agent.messages)
        
        # Add the response to the agent messages
        synthesis_agent.messages.append(create_assistant_prompt(response.content))
        
        # Update agent status
        synthesis_agent.status = "completed"
        
        # Update session with research report
        session.research_report = response.content
        
        # Save the report to file
        report_path = await self._save_research_report(session_id, response.content)
        
        logger.info(f"Research report created for session {session_id}")
        return report_path
    
    @handle_async_errors
    async def _save_research_report(self, session_id: str, content: str) -> str:
        """
        Save the research report to file.
        
        Args:
            session_id: Session ID
            content: Report content
            
        Returns:
            Path to the saved report
        """
        # Create metadata
        metadata = {
            "session_id": session_id,
            "created_at": datetime.now().isoformat()
        }
        
        # Save the report using document manager
        report_path = self.doc_manager.create_document(
            content=content,
            document_type="research-report",
            title="Foundational Research Report",
            metadata=metadata
        )
        
        # Add the report to the session
        self.session_manager.add_document(session_id, "research_report", report_path)
        
        logger.info(f"Research report saved to {report_path}")
        return report_path
    
    @handle_async_errors
    async def conduct_research(self, session_id: str) -> Optional[str]:
        """
        Conduct full research workflow.
        
        Args:
            session_id: Session ID
            
        Returns:
            Path to the final research report
        """
        logger.info(f"Starting complete research workflow for session {session_id}")
        
        # Step 1: Create session if it doesn't exist
        session = self.sessions.get(session_id)
        if not session:
            # Get research requirements from architecture research requirements document
            session_manager = SessionManager()
            requirements_path = session_manager.get_document(session_id, "architecture_research_requirements")
            if not requirements_path:
                logger.error(f"No architecture research requirements found for session {session_id}")
                return None
            
            requirements_content = await load_document_content(requirements_path)
            session = await self.create_session(session_id, requirements_content)
        
        # Step 2: Initialize research agents
        if not session.agents:
            await self.initialize_research_agents(session_id)
        
        # Step 3: Discover project foundations
        if not session.project_foundations:
            await self.discover_project_foundations(session_id)
        
        # Step 4: Explore foundation approaches
        if all(not foundation.completed for foundation in session.project_foundations.values()):
            await self.explore_foundation_approaches(session_id)
        
        # Step 5: Generate research paths
        if not session.research_paths:
            await self.generate_research_paths(session_id)
        
        # Step 6: Conduct path research
        if all(not path.research_content for path in session.research_paths):
            await self.start_path_research(session_id)
        
        # Step 7: Conduct integration research
        if not session.cross_paradigm_opportunities:
            await self.start_integration_research(session_id)
        
        # Step 8: Create comprehensive research report
        report_path = await self.create_research_report(session_id)
        
        logger.info(f"Completed research workflow for session {session_id}")
        return report_path