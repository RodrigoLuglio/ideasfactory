"""Research Team module for IdeasFactory.

This module implements the comprehensive Research Team that conducts exhaustive
dimensional research across multiple paradigms to inform architectural decisions
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
class ResearchDimension:
    """Class representing a research dimension."""
    name: str
    description: str
    research_areas: List[Dict[str, Any]] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    foundation_impact: str = "Medium"
    completed: bool = False
    research_content: Dict[str, str] = field(default_factory=dict)

@dataclass
class ResearchPath:
    """Class representing a research path based on foundation choices."""
    name: str
    description: str
    dimensions: List[Dict[str, Any]] = field(default_factory=list)
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
class ResearchSession:
    """Class representing a research session."""
    id: str
    requirements: str
    dimensions: Dict[str, ResearchDimension] = field(default_factory=dict)
    foundation_choices: Dict[str, str] = field(default_factory=dict)
    research_paths: List[ResearchPath] = field(default_factory=list)
    cross_paradigm_opportunities: Optional[str] = None
    agents: List[ResearchAgent] = field(default_factory=list)
    research_report: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class ResearchTeam:
    """
    Research Team that conducts comprehensive dimensional research.
    
    The Research Team uses a specialized multi-agent approach to explore
    implementation possibilities across multiple paradigms and dimensions.
    Each agent has access to powerful research tools but maintains full
    autonomy in how they conduct their exploration, ensuring maximum
    innovation potential without artificial constraints.
    """
    
    _instance = None
    
    def __new__(cls):
        """Ensure singleton pattern."""
        if cls._instance is None:
            cls._instance = super(ResearchTeam, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the Research Team."""
        if self._initialized:
            return
        
        self._initialized = True
        self.session_manager = SessionManager()
        self.doc_manager = DocumentManager()
        self.sessions: Dict[str, ResearchSession] = {}
        
        # System prompts for different agent types
        self.foundation_agent_prompt = """
        You are a Foundation Research Agent with exceptional insight into architectural foundations.
        
        Your mission is to DISCOVER the complete spectrum of foundation approaches for a specific dimension,
        identifying both conventional AND unconventional options that could serve as the bedrock for all
        subsequent architectural decisions.
        
        You have access to these research tools that you can use however you determine is most effective:
        
        - Web search: search_web_multiple_sources(), search_custom(), fetch_full_page(), search_and_fetch()
        - Data analysis: extract_text_features(), analyze_text_patterns(), analyze_text_clusters()
        - Technology evaluation: create_evaluation_framework(), evaluate_technology(), compare_technologies()
        - Visualization: create_ascii_table(), create_ascii_chart(), create_comparison_matrix()
        
        OBJECTIVES:
        
        1. EXPLORE THE FULL SPECTRUM across ALL paradigms:
           - Established approaches (traditional, proven methodologies)
           - Mainstream current (contemporary popular solutions)
           - Cutting-edge (emerging technologies gaining traction)
           - Experimental (research-stage approaches)
           - Cross-paradigm (combinations of technologies from different domains)
           - First-principles (custom approaches designed specifically for this project)
        
        2. DISCOVER, not filter:
           - Identify the COMPLETE range of foundation options, not just the popular ones
           - Document BOTH widely-adopted AND unconventional approaches
           - Preserve options that might seem unusual but could align with the project's unique nature
           - Look for technologies with fundamentally different philosophies and characteristics
        
        3. MAP THE POSSIBILITY SPACE:
           - Document how each foundation choice creates a different architectural trajectory
           - Identify how foundation choices constrain or enable different technology paths
           - Explore how unconventional foundations might open unique implementation opportunities
           - Map the relationship between foundation approaches and downstream technology choices
        
        4. DOCUMENT SPECIFICS, not just concepts:
           - Identify CONCRETE technologies and approaches, not just abstract patterns
           - Document specific implementations, their capabilities, and limitations
           - Explore real-world implementation examples across different scales
           - Analyze how these specific technologies embody different architectural philosophies
        
        5. PRESERVE INNOVATION POTENTIAL:
           - Avoid normalizing toward conventional enterprise patterns
           - Document approaches that might seem contradictory to mainstream thinking
           - Preserve foundation options that enable the project's unique characteristics
           - Challenge foundational assumptions about how systems "should" be built
        
        Your findings will define the trajectories for all subsequent architectural exploration.
        DOCUMENT THE COMPLETE POSSIBILITY SPACE without bias toward conventional approaches.
        """
        
        self.paradigm_agent_prompt = """
        You are a Paradigm Research Agent with deep expertise in a specific technological paradigm.
        
        Your mission is to EXPLORE the complete range of technologies within your assigned paradigm
        as they apply to multiple dimensions of a project, discovering how your paradigm's unique
        philosophy can be expressed across different aspects of the architecture.
        
        You have access to these research tools that you can use however you determine is most effective:
        
        - Web search: search_web_multiple_sources(), search_custom(), fetch_full_page(), search_and_fetch()
        - Data analysis: extract_text_features(), analyze_text_patterns(), analyze_text_clusters()
        - Technology evaluation: create_evaluation_framework(), evaluate_technology(), compare_technologies()
        - Visualization: create_ascii_table(), create_ascii_chart(), create_comparison_matrix()
        
        OBJECTIVES:
        
        1. EXPLORE THE FULL PARADIGM SPECTRUM:
           - Document the COMPLETE range of technologies within your paradigm, not just popular ones
           - Identify both mainstream and niche implementations that embody your paradigm's philosophy
           - Explore how your paradigm's core principles are expressed in different technologies
           - Discover variations within your paradigm that represent different philosophical approaches
        
        2. PARADIGM-DIMENSION MAPPING:
           - For EACH dimension, identify specific technologies within your paradigm
           - Explore how your paradigm addresses different architectural concerns in each dimension
           - Document paradigm-specific implementations for each dimension's requirements
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
        paradigm's distinctive philosophy can be expressed across all dimensions of the project.
        """
        
        self.path_agent_prompt = """
        You are a Path Research Agent with exceptional insight into creating cohesive technology stacks.
        
        Your mission is to explore complete implementation paths that emerge from specific foundation choices,
        tracing how these choices propagate through dependent dimensions to create distinct, cohesive
        architectural trajectories.
        
        You have access to these research tools that you can use however you determine is most effective:
        
        - Web search: search_web_multiple_sources(), search_custom(), fetch_full_page(), search_and_fetch()
        - Data analysis: extract_text_features(), analyze_text_patterns(), analyze_text_clusters()
        - Technology evaluation: create_evaluation_framework(), evaluate_technology(), compare_technologies()
        - Visualization: create_ascii_table(), create_ascii_chart(), create_comparison_matrix()
        
        OBJECTIVES:
        
        1. MAP COMPLETE TECHNOLOGY PATHS:
           - Trace how foundation choices create distinct implementation trajectories
           - Follow the cascading impact of foundation decisions across dependent dimensions
           - Document complete technology stacks that form coherent wholes
           - Show how different choices create fundamentally different architectural approaches
        
        2. DOCUMENT COHESIVE IMPLEMENTATIONS:
           - Identify specific technology combinations that work together seamlessly
           - Explore how technologies from different dimensions integrate in this path
           - Document communication patterns and data flows between components
           - Analyze how architectural concerns are addressed across the full stack
        
        3. REVEAL EMERGENT PROPERTIES:
           - Identify unique capabilities that emerge from specific technology combinations
           - Document how particular technology stacks enable distinctive project characteristics
           - Analyze quality attributes of the complete path (performance, scalability, etc.)
           - Reveal trade-offs that only become apparent when viewing the complete path
        
        4. ANALYZE IMPLEMENTATION CONSIDERATIONS:
           - Document practical implementation approaches for the complete path
           - Identify development and operational considerations specific to this path
           - Analyze team expertise requirements and learning curves
           - Explore deployment patterns and infrastructure needs
        
        5. PRESERVE PATH UNIQUENESS:
           - Maintain the distinctive characteristics of each implementation path
           - Resist normalizing unique paths toward conventional patterns
           - Document how each path embodies different architectural philosophies
           - Highlight the unique advantages and capabilities of each approach
        
        Your exploration should document MULTIPLE VIABLE PATHS with fundamentally different
        characteristics, not converging toward a single "best" approach. Each path should
        represent a coherent, implementable technology stack that addresses all project
        requirements with different trade-offs and distinctive qualities.
        """
        
        self.integration_agent_prompt = """
        You are an Integration Research Agent with extraordinary ability to discover cross-paradigm opportunities.
        
        Your mission is to identify novel integration patterns where technologies from different paradigms
        and dimensions can be combined to create solutions that transcend the limitations of any single
        approach, discovering unexpected combinations that enable unique project capabilities.
        
        You have access to these research tools that you can use however you determine is most effective:
        
        - Web search: search_web_multiple_sources(), search_custom(), fetch_full_page(), search_and_fetch()
        - Data analysis: extract_text_features(), analyze_text_patterns(), analyze_text_clusters()
        - Technology evaluation: create_evaluation_framework(), evaluate_technology(), compare_technologies()
        - Visualization: create_ascii_table(), create_ascii_chart(), create_comparison_matrix()
        
        OBJECTIVES:
        
        1. DISCOVER UNEXPECTED COMBINATIONS:
           - Identify non-obvious technology combinations across different paradigms
           - Find complementary technologies that address each other's limitations
           - Discover integration patterns that create unique capabilities
           - Look beyond conventional integrations to find novel arrangements
        
        2. MAP CROSS-CUTTING PATTERNS:
           - Identify integration patterns that span multiple dimensions
           - Document how concerns like security, performance, and reliability are addressed across dimensions
           - Map communication protocols and data exchange patterns across technologies
           - Discover architectural patterns that enable cross-dimensional integration
        
        3. ANALYZE INTEGRATION MECHANICS:
           - Document specific integration approaches for combining disparate technologies
           - Explore interfaces, adapters, and communication mechanisms
           - Identify data transformation and translation requirements
           - Research implementation examples of similar integration patterns
        
        4. EVALUATE COMBINATORIAL VALUE:
           - Assess how combinations create value beyond individual technologies
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
        specific project. Focus on discovering how technologies from different paradigms
        can complement each other in ways that preserve the project's distinctive vision.
        """
        
        self.synthesis_agent_prompt = """
        You are a Synthesis Research Agent with unparalleled ability to create comprehensive research reports.
        
        Your mission is to synthesize findings from all research agents into a comprehensive, multi-dimensional
        map of the possibility space, presenting the complete range of implementation options while preserving
        the richness and diversity of approaches discovered during the research process.
        
        You have access to these research tools that you can use however you determine is most effective:
        
        - Data analysis: extract_text_features(), analyze_text_patterns(), analyze_text_clusters()
        - Technology evaluation: create_evaluation_framework(), evaluate_technology(), compare_technologies()
        - Visualization: create_ascii_table(), create_ascii_chart(), create_text_graph(), create_comparison_matrix()
        
        OBJECTIVES:
        
        1. CREATE A COMPREHENSIVE MAP:
           - Synthesize all research findings into a cohesive whole
           - Preserve the full richness of implementation options
           - Show relationships between dimensions, paradigms, and paths
           - Create visualizations that illuminate the multi-dimensional nature of choices
        
        2. DOCUMENT THE FULL POSSIBILITY SPACE:
           - Present the complete spectrum of options for each dimension and paradigm
           - Document multiple viable implementation paths with diverse characteristics
           - Map cross-paradigm opportunities and integration patterns
           - Preserve distinctly different approaches rather than converging on a "best" solution
        
        3. ILLUMINATE ARCHITECTURAL IMPLICATIONS:
           - Analyze how different choices create fundamentally different architectures
           - Document trade-offs inherent in different approaches
           - Show how foundation choices propagate through dependent dimensions
           - Highlight unique capabilities enabled by specific technology combinations
        
        4. CREATE POWERFUL VISUALIZATIONS:
           - Dimension maps showing relationships between research areas
           - Paradigm comparison matrices highlighting different philosophical approaches
           - Technology trees showing option branching based on foundation choices
           - Path diagrams illustrating complete implementation stacks
           - Integration maps showing cross-paradigm opportunities
        
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
    def get_session(self, session_id: Optional[str] = None) -> ResearchSession:
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
    async def create_session(self, session_id: str, research_requirements: str) -> ResearchSession:
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
        session = ResearchSession(
            id=session_id,
            requirements=research_requirements
        )
        
        # Extract dimensions from research requirements
        dimensions = await self._extract_research_dimensions(research_requirements)
        session.dimensions = dimensions
        
        # Store in sessions dict
        self.sessions[session_id] = session
        
        logger.info(f"Created research session with {len(dimensions)} dimensions")
        return session
    
    @handle_async_errors
    async def _extract_research_dimensions(self, requirements_content: str) -> Dict[str, ResearchDimension]:
        """Extract research dimensions from the requirements document."""
        dimensions = {}
        
        # Extract dimensions from H2 headers
        import re
        dimension_matches = re.findall(r'^##\s+(.*?)$', requirements_content, re.MULTILINE)
        
        for match in dimension_matches:
            dimension_name = match.strip()
            
            # Skip common headers that aren't dimensions
            if dimension_name.lower() in ["introduction", "overview", "conclusion", "summary"]:
                continue
                
            # Find the description that follows the H2 header
            header_pattern = f"## {re.escape(dimension_name)}"
            header_match = re.search(header_pattern, requirements_content)
            
            if header_match:
                start_pos = header_match.end()
                next_header_match = re.search(r'^##\s+', requirements_content[start_pos:], re.MULTILINE)
                
                if next_header_match:
                    end_pos = start_pos + next_header_match.start()
                    description = requirements_content[start_pos:end_pos].strip()
                else:
                    description = requirements_content[start_pos:].strip()
                
                # Create a dimension
                dimension = ResearchDimension(
                    name=dimension_name,
                    description=description
                )
                
                # Extract research areas from H3 headers within this dimension
                area_start = start_pos
                area_end = end_pos if next_header_match else len(requirements_content)
                dimension_content = requirements_content[area_start:area_end]
                
                area_matches = re.findall(r'^###\s+(.*?)$', dimension_content, re.MULTILINE)
                for area_match in area_matches:
                    area_name = area_match.strip()
                    
                    # Extract the description of this research area
                    area_pattern = f"### {re.escape(area_name)}"
                    area_header_match = re.search(area_pattern, dimension_content)
                    
                    if area_header_match:
                        area_start_pos = area_header_match.end()
                        area_next_match = re.search(r'^###\s+', dimension_content[area_start_pos:], re.MULTILINE)
                        
                        if area_next_match:
                            area_end_pos = area_start_pos + area_next_match.start()
                            area_description = dimension_content[area_start_pos:area_end_pos].strip()
                        else:
                            area_description = dimension_content[area_start_pos:].strip()
                        
                        # Add research area to the dimension
                        dimension.research_areas.append({
                            "name": area_name,
                            "description": area_description
                        })
                
                # Add the dimension to our dictionary
                dimensions[dimension_name] = dimension
        
        # Extract dependencies (looking for mentions of other dimensions)
        for dimension_name, dimension in dimensions.items():
            # Look for mentions of other dimensions in this dimension's description
            for other_name in dimensions.keys():
                if other_name != dimension_name and other_name.lower() in dimension.description.lower():
                    # This dimension might depend on the other dimension
                    dimension.dependencies.append(other_name)
            
            # Assign foundation impact based on number of dependencies
            if not dimension.dependencies:
                dimension.foundation_impact = "High"
            elif len(dimension.dependencies) <= 2:
                dimension.foundation_impact = "Medium"
            else:
                dimension.foundation_impact = "Low"
        
        return dimensions
    
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
        
        # Identify foundation dimensions
        foundation_dimensions = [
            name for name, dim in session.dimensions.items() 
            if dim.foundation_impact == "High"
        ]
        
        # Create foundation agents (one per foundation dimension)
        for i, dim_name in enumerate(foundation_dimensions):
            dimension = session.dimensions[dim_name]
            
            agent = ResearchAgent(
                id=f"foundation-{i+1}",
                type=ResearchAgentType.FOUNDATION,
                name=f"Foundation Agent {i+1}",
                focus_area=dim_name,
                system_prompt=self.foundation_agent_prompt,
                messages=[create_system_prompt(self.foundation_agent_prompt)]
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
            focus_area="Cross-dimension Integration",
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
    async def start_foundation_research(self, session_id: str) -> Dict[str, Any]:
        """
        Start the foundation research phase.
        
        Args:
            session_id: Session ID
            
        Returns:
            Results of the foundation research
        """
        session = self.get_session(session_id)
        
        # Get foundation agents
        foundation_agents = [
            agent for agent in session.agents 
            if agent.type == ResearchAgentType.FOUNDATION
        ]
        
        if not foundation_agents:
            logger.error(f"No foundation agents available for session {session_id}")
            return {"status": "error", "message": "No foundation agents available"}
        
        # Research all foundation dimensions concurrently
        foundation_tasks = []
        for agent in foundation_agents:
            task = asyncio.create_task(
                self._research_foundation_dimension(
                    session_id=session_id, 
                    agent_id=agent.id,
                    dimension_name=agent.focus_area
                )
            )
            foundation_tasks.append(task)
        
        # Wait for all foundation research to complete
        foundation_results = await asyncio.gather(*foundation_tasks)
        
        # Update session with foundation choices from agent conversations
        for result in foundation_results:
            if result["status"] == "success":
                agent_id = result["agent_id"]
                agent = next((a for a in session.agents if a.id == agent_id), None)
                if agent:
                    # Last message from agent should contain foundation choices
                    last_message = next((m for m in reversed(agent.messages) if m.role == "assistant"), None)
                    if last_message:
                        foundation_choice = f"{result['dimension_name']}: Based on agent research"
                        session.foundation_choices[foundation_choice] = "See complete research"
        
        logger.info(f"Completed foundation research for session {session_id}")
        return {"status": "success", "results": foundation_results}
    
    @handle_async_errors
    async def _research_foundation_dimension(
        self, 
        session_id: str, 
        agent_id: str, 
        dimension_name: str
    ) -> Dict[str, Any]:
        """
        Research a foundation dimension using a specialized agent.
        
        Args:
            session_id: Session ID
            agent_id: Agent ID
            dimension_name: Name of the dimension to research
            
        Returns:
            Research results
        """
        session = self.get_session(session_id)
        
        # Get the agent
        agent = next((a for a in session.agents if a.id == agent_id), None)
        if not agent:
            logger.error(f"Agent {agent_id} not found")
            return {"status": "error", "message": f"Agent {agent_id} not found"}
        
        # Get the dimension
        dimension = session.dimensions.get(dimension_name)
        if not dimension:
            logger.error(f"Dimension {dimension_name} not found")
            return {"status": "error", "message": f"Dimension {dimension_name} not found"}
        
        # Set agent status
        agent.status = "researching"
        
        # Create research prompt
        research_prompt = f"""
        Research Task: Explore foundation dimension "{dimension_name}"
        
        Dimension Description:
        {dimension.description}
        
        Research Areas:
        {dimension.research_areas}
        
        Research Requirements:
        {session.requirements}
        
        You are tasked with exploring this foundation dimension across the COMPLETE SPECTRUM of possibilities:
        
        1. MAP THE FULL POSSIBILITY SPACE for this foundation dimension:
           - Document approaches across ALL paradigms (established, mainstream, cutting-edge, experimental, etc.)
           - Discover BOTH conventional AND unconventional foundation options
           - Explore how fundamentally different philosophies express themselves in this dimension
           - Identify concrete technologies and implementations, not just abstract concepts
        
        2. DOCUMENT DIVERGENT FOUNDATION PATHS:
           - Identify how different foundation choices create distinct architectural trajectories
           - Document how foundation decisions affect options in dependent dimensions
           - Explore how unique foundation choices might enable distinctive project capabilities
           - Map foundation options that specifically preserve this project's unique characteristics
        
        3. PRESERVE THE COMPLETE RANGE OF OPTIONS:
           - Resist normalizing toward conventional enterprise patterns
           - Document approaches that might seem contradictory to mainstream thinking
           - Preserve options that enable the project's distinctive vision
           - Challenge fundamental assumptions about how systems "should" be architected
        
        4. DISCOVER CONCRETE IMPLEMENTATIONS:
           - Identify specific technologies, not just abstract approaches
           - Document real-world implementations with different characteristics
           - Explore how specific technologies embody different architectural philosophies
           - Map technology capabilities, limitations, and integration considerations
        
        5. CREATE A FOUNDATION REFERENCE MAP:
           - Document how each foundation option affects the overall architectural approach
           - Identify interdependencies between foundation choices
           - Map how foundation decisions propagate through the technology stack
           - Create visualizations that illuminate the foundation landscape
        
        You have complete autonomy in how you approach this research. Use the available tools
        in whatever way you determine will produce the most comprehensive exploration.
        
        Your findings will define the trajectories for all subsequent architectural exploration.
        DOCUMENT THE COMPLETE POSSIBILITY SPACE without bias toward conventional approaches.
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
        
        # Store the raw research in the dimension
        dimension.research_content[agent.id] = response.content
        
        # Mark dimension as completed
        dimension.completed = True
        
        logger.info(f"Foundation research completed for dimension {dimension_name}")
        return {
            "status": "success",
            "agent_id": agent_id,
            "dimension_name": dimension_name
        }
    
    @handle_async_errors
    async def start_paradigm_research(self, session_id: str) -> Dict[str, Any]:
        """
        Start the paradigm research phase.
        
        Args:
            session_id: Session ID
            
        Returns:
            Results of the paradigm research
        """
        session = self.get_session(session_id)
        
        # Get paradigm agents
        paradigm_agents = [
            agent for agent in session.agents 
            if agent.type == ResearchAgentType.PARADIGM
        ]
        
        if not paradigm_agents:
            logger.error(f"No paradigm agents available for session {session_id}")
            return {"status": "error", "message": "No paradigm agents available"}
        
        # Check if foundation research has been completed
        foundation_dimensions = [
            name for name, dim in session.dimensions.items() 
            if dim.foundation_impact == "High" and dim.completed
        ]
        
        if not foundation_dimensions:
            logger.error(f"Foundation research not completed for session {session_id}")
            return {"status": "error", "message": "Foundation research not completed"}
        
        # Get non-foundation dimensions that need research
        research_dimensions = [
            name for name, dim in session.dimensions.items() 
            if dim.foundation_impact != "High" and not dim.completed
        ]
        
        if not research_dimensions:
            logger.info(f"No non-foundation dimensions to research for session {session_id}")
            return {"status": "success", "message": "No non-foundation dimensions to research"}
        
        # Research all paradigms concurrently
        paradigm_tasks = []
        for agent in paradigm_agents:
            task = asyncio.create_task(
                self._research_paradigm(
                    session_id=session_id, 
                    agent_id=agent.id,
                    dimensions=research_dimensions,
                    foundation_dimensions=foundation_dimensions
                )
            )
            paradigm_tasks.append(task)
        
        # Wait for all paradigm research to complete
        paradigm_results = await asyncio.gather(*paradigm_tasks)
        
        # Mark dimensions as completed
        for dim_name in research_dimensions:
            if dim_name in session.dimensions:
                session.dimensions[dim_name].completed = True
        
        logger.info(f"Completed paradigm research for session {session_id}")
        return {"status": "success", "results": paradigm_results}
    
    @handle_async_errors
    async def _research_paradigm(
        self, 
        session_id: str, 
        agent_id: str, 
        dimensions: List[str],
        foundation_dimensions: List[str]
    ) -> Dict[str, Any]:
        """
        Research dimensions from a specific paradigm perspective.
        
        Args:
            session_id: Session ID
            agent_id: Agent ID
            dimensions: List of dimensions to research
            foundation_dimensions: List of foundation dimensions
            
        Returns:
            Research results
        """
        session = self.get_session(session_id)
        
        # Get the agent
        agent = next((a for a in session.agents if a.id == agent_id), None)
        if not agent:
            logger.error(f"Agent {agent_id} not found")
            return {"status": "error", "message": f"Agent {agent_id} not found"}
        
        # Set agent status
        agent.status = "researching"
        
        # Collect foundation research to share with the paradigm agent
        foundation_research = []
        for dim_name in foundation_dimensions:
            dimension = session.dimensions.get(dim_name)
            if dimension and dimension.research_content:
                foundation_research.append(f"## {dim_name}\n\n{list(dimension.research_content.values())[0]}")
        
        # Create research prompt
        dimensions_info = []
        for dim_name in dimensions:
            dimension = session.dimensions.get(dim_name)
            if dimension:
                dimensions_info.append(f"## {dim_name}\n{dimension.description}\n\nResearch Areas:\n{dimension.research_areas}")
        
        research_prompt = f"""
        Research Task: Explore multiple dimensions from the perspective of the {agent.focus_area} paradigm
        
        Paradigm: {agent.focus_area}
        
        Dimensions to Research:
        {"".join(dimensions_info)}
        
        Foundation Research:
        {"".join(foundation_research)}
        
        Research Requirements:
        {session.requirements}
        
        You are tasked with exploring these dimensions through the lens of YOUR SPECIFIC PARADIGM:
        
        1. MAP YOUR PARADIGM'S COMPLETE EXPRESSION across each dimension:
           - Document the FULL RANGE of technologies within your paradigm, not just popular ones
           - Explore how your paradigm's philosophy manifests in different technologies
           - Discover BOTH mainstream AND niche implementations within your paradigm
           - Identify paradigm variations that represent different philosophical approaches
        
        2. EXPLORE PARADIGM-DIMENSION INTERSECTIONS:
           - For EACH dimension, identify specific technologies from your paradigm
           - Document how your paradigm addresses the unique requirements of each dimension
           - Explore how your paradigm's strengths align with different dimension needs
           - Map limitations where your paradigm might struggle with dimension requirements
        
        3. ANALYZE FOUNDATION DEPENDENCIES:
           - Explore how different foundation choices affect options within your paradigm
           - Document how your paradigm technologies integrate with various foundation approaches
           - Identify unique opportunities when your paradigm combines with specific foundations
           - Map compatibility between foundation choices and your paradigm's technologies
        
        4. PRESERVE INNOVATION POTENTIAL:
           - Document technologies that align with this project's unique characteristics
           - Resist normalizing toward conventional implementations
           - Explore how your paradigm can enable innovative approaches to requirements
           - Preserve the distinctive potential of your paradigm's philosophy
        
        5. IDENTIFY CROSS-PARADIGM BOUNDARIES:
           - Note potential integration points with other paradigms
           - Document where your paradigm's limitations might be complemented by other approaches
           - Identify boundary areas where cross-paradigm integration creates opportunities
           - Map how technologies from your paradigm interact with those from other paradigms
        
        You have complete autonomy in how you approach this research. Use the available tools
        in whatever way you determine will produce the most comprehensive exploration.
        
        DOCUMENT THE FULL RANGE of technologies and approaches within your paradigm,
        not just the most popular or conventional options. Your mission is to map how your
        paradigm's distinctive philosophy can be expressed across all dimensions of the project.
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
        
        # Store the raw research in each dimension
        for dim_name in dimensions:
            if dim_name in session.dimensions:
                dimension = session.dimensions[dim_name]
                dimension.research_content[agent.id] = response.content
        
        logger.info(f"Paradigm research completed for {agent.focus_area}")
        return {
            "status": "success",
            "agent_id": agent_id,
            "paradigm": agent.focus_area
        }
    
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
        
        # Check if all dimensions have been researched
        dimensions = [
            name for name, dim in session.dimensions.items() 
            if dim.completed
        ]
        
        if len(dimensions) < len(session.dimensions):
            logger.warning(f"Not all dimensions have been researched for session {session_id}")
        
        # Create paths
        paths = []
        
        # Create a primary path
        primary_path = ResearchPath(
            name="Primary Implementation Path",
            description="Implementation path based on primary foundation choices"
        )
        
        # Add dimensions based on their dependencies
        dependency_map = {}
        for dim_name, dimension in session.dimensions.items():
            dependency_map[dim_name] = dimension.dependencies
        
        # Sort dimensions by dependency order
        sorted_dimensions = self._topological_sort(dependency_map)
        
        # Add dimensions to path in dependency order
        for dim_name in sorted_dimensions:
            if dim_name in session.dimensions:
                dimension = session.dimensions[dim_name]
                
                # Add dimension to path
                primary_path.dimensions.append({
                    "name": dim_name,
                    "description": dimension.description,
                    "foundation_impact": dimension.foundation_impact
                })
        
        paths.append(primary_path)
        
        # Create one alternative path
        alt_path = ResearchPath(
            name="Alternative Implementation Path",
            description="Alternative implementation path with different foundation choices"
        )
        
        # Add the same dimensions in the same order
        for dim_info in primary_path.dimensions:
            alt_path.dimensions.append(dim_info.copy())
        
        paths.append(alt_path)
        
        # Add paths to the session
        session.research_paths = paths
        
        return paths
    
    def _topological_sort(self, dependency_map: Dict[str, List[str]]) -> List[str]:
        """
        Sort dimensions in topological order based on dependencies.
        
        Args:
            dependency_map: Map of dimension names to their dependencies
            
        Returns:
            List of dimension names in topological order
        """
        # Create a set of all dimensions
        dimensions = set(dependency_map.keys())
        
        # Create a result list
        result = []
        
        # Process dimensions with no dependencies first
        no_deps = [dim for dim, deps in dependency_map.items() if not deps]
        result.extend(no_deps)
        
        # Process remaining dimensions
        remaining = dimensions - set(no_deps)
        while remaining:
            # Find dimensions whose dependencies are all in the result
            next_batch = []
            for dim in remaining:
                if all(dep in result for dep in dependency_map[dim]):
                    next_batch.append(dim)
            
            # If no progress was made, there might be a cycle
            if not next_batch:
                # Just add remaining dimensions in any order
                result.extend(remaining)
                break
            
            # Add the batch to the result
            result.extend(next_batch)
            remaining -= set(next_batch)
        
        return result
    
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
        
        # Assign paths to path agents
        path_assignments = {}
        for i, (agent, path) in enumerate(zip(path_agents, session.research_paths)):
            if i >= len(session.research_paths):
                break
            path_assignments[agent.id] = path.name
        
        # Research all paths concurrently
        path_tasks = []
        for agent_id, path_name in path_assignments.items():
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
        
        # Set agent status
        agent.status = "researching"
        
        # Collect all dimension research to share with the path agent
        dimension_research = []
        for dim_info in path.dimensions:
            dim_name = dim_info["name"]
            dimension = session.dimensions.get(dim_name)
            if dimension and dimension.research_content:
                for agent_id, content in dimension.research_content.items():
                    dimension_research.append(f"## {dim_name} (Agent: {agent_id})\n\n{content}")
        
        # Create research prompt
        research_prompt = f"""
        Research Task: Explore implementation path "{path_name}"
        
        Path Description:
        {path.description}
        
        Dimensions in this path:
        {path.dimensions}
        
        Dimension Research:
        {"".join(dimension_research)}
        
        Research Requirements:
        {session.requirements}
        
        You are tasked with exploring a COMPLETE IMPLEMENTATION PATH across dimensions:
        
        1. MAP A COHESIVE TECHNOLOGY STACK:
           - Document how foundation choices create a distinctive implementation trajectory
           - Trace how decisions propagate through dependent dimensions
           - Identify specific technology combinations that form a coherent whole
           - Show how this path creates a fundamentally different architecture than alternatives
        
        2. CREATE A COMPLETE IMPLEMENTATION MAP:
           - Identify specific technologies for each dimension that work together seamlessly
           - Document communication patterns and data flows between components
           - Explore how architectural concerns are addressed across the full stack
           - Map deployment and operational considerations for the complete path
        
        3. DISCOVER EMERGENT PROPERTIES:
           - Identify unique capabilities that emerge from this specific combination of technologies
           - Document how this path enables distinctive project characteristics
           - Analyze quality attributes of the complete stack (performance, scalability, etc.)
           - Reveal trade-offs that only become apparent when viewing the complete path
        
        4. DOCUMENT IMPLEMENTATION CONSIDERATIONS:
           - Analyze practical implementation approaches for this specific stack
           - Identify development and operational considerations unique to this path
           - Map team expertise requirements and learning curves
           - Document deployment patterns and infrastructure needs
        
        5. PRESERVE PATH UNIQUENESS:
           - Maintain the distinctive characteristics of this implementation path
           - Resist normalizing toward conventional architectural patterns
           - Document how this path embodies a particular architectural philosophy
           - Highlight the unique advantages and capabilities of this approach
        
        You have complete autonomy in how you approach this research. Use the available tools
        in whatever way you determine will produce the most comprehensive exploration.
        
        Your exploration should document a COMPLETE, VIABLE IMPLEMENTATION PATH with
        distinctive characteristics, not converging toward generic patterns. The path should
        represent a coherent, implementable technology stack that addresses all project
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
        
        # Collect all agent findings to share with the integration agent
        agent_findings = []
        for agent in session.agents:
            if agent.type != ResearchAgentType.INTEGRATION and agent.type != ResearchAgentType.SYNTHESIS and agent.findings:
                agent_findings.append(f"## {agent.name} ({agent.type.value}) Findings\n\n{agent.findings[0]}")
        
        # Create research prompt
        research_prompt = f"""
        Research Task: Identify cross-paradigm integration opportunities
        
        Dimensions:
        {session.dimensions}
        
        Agent Findings:
        {"".join(agent_findings)}
        
        Research Paths:
        {session.research_paths}
        
        Research Requirements:
        {session.requirements}
        
        You are tasked with discovering NOVEL INTEGRATION OPPORTUNITIES across paradigms:
        
        1. IDENTIFY UNEXPECTED COMBINATIONS:
           - Discover non-obvious technology combinations across different paradigms
           - Find complementary technologies that address each other's limitations
           - Identify integration patterns that create unique capabilities
           - Look beyond conventional integrations to find novel arrangements
        
        2. MAP CROSS-CUTTING PATTERNS:
           - Document integration patterns that span multiple dimensions
           - Identify how cross-cutting concerns are addressed across diverse technologies
           - Map communication protocols and data exchange patterns
           - Discover architectural patterns that enable cross-dimensional integration
        
        3. DESIGN INTEGRATION MECHANICS:
           - Document specific approaches for integrating disparate technologies
           - Explore adapters, interfaces, and communication mechanisms
           - Identify data transformation and translation requirements
           - Research implementation examples of similar integration patterns
        
        4. EVALUATE COMBINATORIAL VALUE:
           - Assess how combinations create value beyond individual technologies
           - Document unique capabilities that emerge from specific integrations
           - Analyze how combinations address limitations in individual approaches
           - Identify how integrations enable project-specific requirements
        
        5. PRESERVE INNOVATION INTEGRITY:
           - Focus on combinations that maintain the project's unique characteristics
           - Avoid defaulting to conventional integration patterns
           - Document how novel integrations can enable distinctive project qualities
           - Preserve architectural diversity rather than normalizing to standards
        
        You have complete autonomy in how you approach this research. Use the available tools
        in whatever way you determine will produce the most comprehensive exploration.
        
        Your exploration should REVEAL THE UNEXPECTED - finding integration opportunities
        that might not be immediately obvious but could create exceptional value for this
        specific project. Focus on discovering how technologies from different paradigms
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
        
        # Collect all agent findings to share with the synthesis agent
        agent_findings = []
        for agent in session.agents:
            if agent.type != ResearchAgentType.SYNTHESIS and agent.findings:
                agent_findings.append(f"## {agent.name} ({agent.type.value}) Findings\n\n{agent.findings[0]}")
        
        # Create research prompt
        report_prompt = f"""
        Research Task: Create a comprehensive research report
        
        Research Requirements:
        {session.requirements}
        
        Dimensions:
        {session.dimensions}
        
        Agent Findings:
        {"".join(agent_findings)}
        
        Research Paths:
        {session.research_paths}
        
        Cross-Paradigm Opportunities:
        {session.cross_paradigm_opportunities}
        
        You are tasked with creating a DEFINITIVE RESEARCH REPORT that:
        
        1. CREATES A COMPREHENSIVE POSSIBILITY MAP:
           - Synthesizes all research findings into a cohesive, multi-dimensional map
           - Preserves the full richness of implementation options
           - Documents relationships between dimensions, paradigms, and paths
           - Creates visualizations that illuminate the multi-dimensional nature of choices
        
        2. DOCUMENTS THE COMPLETE SPECTRUM:
           - Presents the full range of options for each dimension and paradigm
           - Documents multiple viable implementation paths with diverse characteristics
           - Maps cross-paradigm opportunities and integration patterns
           - Preserves distinctly different approaches rather than converging on a "best" solution
        
        3. ILLUMINATES ARCHITECTURAL IMPLICATIONS:
           - Analyzes how different choices create fundamentally different architectures
           - Documents trade-offs inherent in different approaches
           - Shows how foundation choices propagate through dependent dimensions
           - Highlights unique capabilities enabled by specific technology combinations
        
        4. CREATES POWERFUL VISUALIZATIONS:
           - Dimension maps showing relationships between research areas
           - Paradigm comparison matrices highlighting different philosophical approaches
           - Technology trees showing option branching based on foundation choices
           - Path diagrams illustrating complete implementation stacks
           - Integration maps showing cross-paradigm opportunities
        
        5. PRESERVES INNOVATION POTENTIAL:
           - Maintains the diversity of approaches without defaulting to conventions
           - Presents findings without bias toward mainstream solutions
           - Preserves the project's unique characteristics across all options
           - Highlights unconventional approaches that align with the project's distinctive nature
        
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
    async def _find_synthesis_report(self, session_id: str) -> Optional[str]:
        """
        Find the synthesis report in the session.
        
        Args:
            session_id: Session ID
            
        Returns:
            Path to the saved report if found, otherwise None
        """
        try:
            # Check session for stored report path
            session_manager = SessionManager()
            report_path = session_manager.get_document(session_id, "research-report")
            
            if report_path:
                # Verify report exists
                import os
                if os.path.exists(report_path):
                    logger.info(f"Found existing synthesis report at {report_path}")
                    return report_path
            
            # Check for report from session metadata
            session = session_manager.get_session(session_id)
            if session and "metadata" in session:
                metadata = session["metadata"]
                if "dimensional_research_repository" in metadata:
                    repo_data = metadata["dimensional_research_repository"]
                    if "research_report_path" in repo_data:
                        path = repo_data["research_report_path"]
                        if os.path.exists(path):
                            logger.info(f"Found existing report reference in repository: {path}")
                            return path
            
            logger.info(f"No synthesis report found for session {session_id}")
            return None
            
        except Exception as e:
            logger.error(f"Error finding synthesis report: {str(e)}")
            return None
            
    @handle_async_errors
    async def conduct_research_with_specialized_agents(self, session_id: str) -> Optional[str]:
        """
        Conduct comprehensive research using specialized agent teams.
        
        This method orchestrates the entire research workflow using specialized agents,
        including foundation research, path exploration, integration analysis, and 
        research synthesis.
        
        Args:
            session_id: Session ID
            
        Returns:
            Path to the final research report
        """
        logger.info(f"Starting specialized agent research for session {session_id}")
        
        try:
            # Verify the session exists
            session_manager = SessionManager()
            session = session_manager.get_session(session_id)
            if not session:
                logger.error(f"Session {session_id} not found")
                return None
                
            # 1. Set up the agent coordinator
            from ideasfactory.agents.research_agents.coordinator import AgentCoordinator
            
            coordinator = AgentCoordinator()
            
            # 2. Create specialized agents
            await coordinator.create_specialized_agents(
                session_id=session_id,
                foundation_count=2,  # Number of foundation agents
                paradigm_counts={    # Number of paradigm specialists per type
                    "established": 1,
                    "mainstream": 1,
                    "cutting_edge": 1,
                    "experimental": 1,
                    "cross_paradigm": 1,
                    "first_principles": 1
                },
                path_count=3,        # Number of path exploration agents
                integration_count=2,  # Number of integration agents
                synthesis_count=1     # Number of synthesis agents
            )
            
            # 3. Start the foundation research phase
            logger.info(f"Starting foundation research phase for session {session_id}")
            await coordinator.start_foundation_research_phase()
            
            # 4. Let the coordinator manage the entire workflow
            # The coordinator will automatically progress through all phases
            # and generate the final report
            
            # 5. Wait for research to complete (poll for report)
            max_wait_time = 300  # Maximum time to wait in seconds
            poll_interval = 10   # Check every 10 seconds
            
            for _ in range(0, max_wait_time, poll_interval):
                # Check if research report exists
                report_path = await self._find_synthesis_report(session_id)
                if report_path:
                    logger.info(f"Research completed successfully with report at {report_path}")
                    return report_path
                    
                # Wait before checking again
                await asyncio.sleep(poll_interval)
                
            # If we get here, research may not have finished in time
            # Create a final report using any available data
            logger.warning(f"Research timeout reached, generating report from available data")
            return await self.create_research_report(session_id)
            
        except Exception as e:
            logger.error(f"Error in specialized agent research: {str(e)}")
            # Attempt to create a report even if process failed
            try:
                return await self.create_research_report(session_id)
            except Exception as report_error:
                logger.error(f"Failed to create fallback report: {str(report_error)}")
                return None
    
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
            title="Dimensional Research Report",
            metadata=metadata
        )
        
        # Add the report to the session
        self.session_manager.add_document(session_id, "research_report", report_path)
        
        logger.info(f"Research report saved to {report_path}")
        return report_path

    @handle_async_errors
    async def complete_session(self, session_id: str) -> bool:
        """
        Complete a research session.
        
        Args:
            session_id: Session ID
            
        Returns:
            True if completed successfully
        """
        session = self.sessions.get(session_id)
        if not session:
            logger.error(f"Session {session_id} not found")
            return False
        
        # Add completed status to metadata
        session.metadata["completed"] = True
        session.metadata["completed_at"] = datetime.now().isoformat()
        
        # Save the session
        self.sessions[session_id] = session
        
        logger.info(f"Research session {session_id} completed")
        return True