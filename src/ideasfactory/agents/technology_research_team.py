"""Technology Research Team module for IdeasFactory.

This module implements the comprehensive Technology Research Team that conducts
technology-focused research for the selected foundation approach to inform
architectural decisions while preserving innovation and uniqueness.
"""

import logging
import asyncio
import json
import re
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

# Enhanced research tools
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
    """Paradigm categories for technology research."""
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
    TECHNOLOGY = "technology"
    PARADIGM = "paradigm"
    STACK = "stack"
    INTEGRATION = "integration"
    SYNTHESIS = "synthesis"

@dataclass
class TechnologyOption:
    """Class representing a potential technology for a component."""
    name: str
    description: str
    component_id: str  # Which component this technology is for
    paradigm_category: str
    research_areas: List[Dict[str, Any]] = field(default_factory=list)
    completed: bool = False
    research_content: Dict[str, str] = field(default_factory=dict)
    viability_score: float = 0.0

@dataclass
class ComponentTechnology:
    """Class representing a component and its technology options."""
    id: str
    name: str
    description: str
    technology_options: Dict[str, TechnologyOption] = field(default_factory=dict)

@dataclass
class TechnologyStack:
    """Class representing a complete technology stack."""
    name: str
    description: str
    foundation_id: str  # The foundation this stack is based on
    technologies: Dict[str, str] = field(default_factory=dict)  # Component ID to technology ID mapping
    research_content: Optional[str] = None
    report_path: Optional[str] = None  # Path to the saved report for this stack

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
class TechnologyResearchSession:
    """Class representing a technology research session."""
    id: str
    foundation_approach: Dict[str, Any]
    generic_architecture: str
    technology_requirements: str
    project_vision: Optional[str] = None
    prd_document: Optional[str] = None
    component_technologies: Dict[str, ComponentTechnology] = field(default_factory=dict)
    technology_stacks: List[TechnologyStack] = field(default_factory=list)
    integration_patterns: Optional[str] = None
    agents: List[ResearchAgent] = field(default_factory=list)
    technology_report: Optional[str] = None
    stack_path_reports: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    stack_evaluation: Optional[Dict[str, Any]] = None

class TechnologyResearchTeam:
    """
    Research Team that conducts comprehensive technology research based on the selected foundation.
    
    The Technology Research Team uses a specialized multi-agent approach to discover
    potential technologies for each component in the generic architecture and explore
    technology stacks across multiple paradigms.
    """
    
    _instance = None
    
    def __new__(cls):
        """Ensure singleton pattern."""
        if cls._instance is None:
            cls._instance = super(TechnologyResearchTeam, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the Technology Research Team."""
        if not hasattr(self, '_initialized') or not self._initialized:
            self.sessions: Dict[str, TechnologyResearchSession] = {}
            self.session_manager = SessionManager()
            self.doc_manager = DocumentManager()
            self._initialized = True
            
            # System prompts for different agent types
            self.technology_discovery_agent_prompt = """
            You are a Technology Discovery Agent with exceptional insight into discovering viable implementation technologies.

            Your mission is to DISCOVER the COMPLETE SPECTRUM of TECHNOLOGY OPTIONS for implementing components within the selected foundation approach. You identify both conventional AND unconventional technologies that could serve as the implementation building blocks for the generic architecture.

            You have access to these research tools that you can use however you determine is most effective:

            - Web search: search_custom(), fetch_full_page(), search_and_fetch()
            - Data analysis: extract_text_features()
            - Technology evaluation: create_evaluation_framework(), evaluate_technology(), compare_technologies(), generate_evaluation_report()
            - Visualization: create_ascii_table(), create_timeline()

            OBJECTIVES:

            1. DISCOVER TECHNOLOGIES FOR EACH ARCHITECTURAL COMPONENT:
               - Identify the complete spectrum of technologies for implementing each component in the generic architecture
               - Avoid assuming any predetermined technology stack or implementation approach
               - Consider completely different ways each component could be implemented
               - Look beyond standard technology choices to identify unique options
               
            2. EXPLORE EACH TECHNOLOGY across the FULL SPECTRUM of paradigms:
               - Established approaches (traditional, proven technologies with long history)
               - Mainstream current (contemporary popular technologies widely adopted)
               - Cutting-edge (emerging technologies gaining traction in industry)
               - Experimental (research-stage technologies with promising potential)
               - Cross-paradigm (novel combinations across different domains)
               - First-principles (custom approaches designed specifically for this project)

            3. REMAIN COMPLETELY OPEN TO POSSIBILITIES:
               - Consider traditional technology platforms
               - Explore hardware-software combinations
               - Examine novel technology paradigms
               - Investigate pure algorithmic solutions
               - Consider edge computing technologies
               - Look for entirely new technology types specific to this project
               - Explore hybrid combinations that don't fit existing categories
               
            4. MAP THE POSSIBILITY SPACE:
               - Document how each technology choice creates different implementation characteristics
               - Identify how technology choices enable or constrain different capabilities
               - Explore how unconventional technologies might open unique implementation opportunities
               - Map relationships between technology choices and potential project success
               
            5. PRESERVE INNOVATION POTENTIAL:
               - Avoid normalizing toward conventional technology stacks
               - Document technologies that might seem contradictory to mainstream thinking
               - Preserve technology options that enable the project's unique characteristics
               - Challenge assumptions about how components "should" be implemented

            Your discoveries will define the options for all subsequent technology exploration.
            DOCUMENT THE COMPLETE POSSIBILITY SPACE without bias toward conventional approaches.
            """
            
            self.technology_exploration_agent_prompt = """
            You are a Technology Exploration Agent with deep expertise in exploring a specific technology.

            Your mission is to thoroughly explore a particular technology option across the paradigm spectrum,
            documenting how this technology can be implemented in different ways and what emergent characteristics would
            arise from choosing this technology for a specific component in the generic architecture.

            You have access to these research tools that you can use however you determine is most effective:

            - Web search: search_custom(), fetch_full_page(), search_and_fetch()
            - Data analysis: extract_text_features()
            - Technology evaluation: create_evaluation_framework(), evaluate_technology(), compare_technologies(), generate_evaluation_report()
            - Visualization: create_ascii_table()

            OBJECTIVES:

            1. EXPLORE THIS TECHNOLOGY ACROSS THE PARADIGM SPECTRUM:
               - Document how this technology can be implemented using approaches from different paradigms
               - Identify established, mainstream, cutting-edge, experimental, and first-principles implementations
               - Explore variations within this technology that represent different philosophical approaches
               - Document specific implementation patterns for each paradigm using this technology
               
            2. DISCOVER EMERGENT CHARACTERISTICS:
               - Identify what implementation characteristics would emerge from choosing this technology
               - Document the unique aspects that would need to be addressed with this technology
               - Explore how these characteristics differ from those that would emerge from other technologies
               - Map relationships between emergent characteristics specific to this technology
               
            3. EVALUATE TECHNOLOGY VIABILITY:
               - Analyze how well this technology aligns with the project's unique requirements
               - Document strengths and limitations of this technology for the specific component
               - Identify scenarios where this technology would be particularly advantageous
               - Assess implementation complexity, scalability, performance, and other relevant factors
               
            4. PRESERVE INNOVATION POTENTIAL:
               - Resist normalizing toward conventional implementations of this technology
               - Document unconventional uses that might be particularly well-suited
               - Explore how this technology could enable unique project characteristics
               - Challenge assumptions about how this technology "should" be implemented
               
            5. IDENTIFY CROSS-TECHNOLOGY OPPORTUNITIES:
               - Note potential integration points with other technologies
               - Identify where hybrid approaches might combine the strengths of multiple technologies
               - Document how this technology could complement or be complemented by others
               - Explore potential novel combinations with other technology options

            You have complete autonomy in how you approach this exploration. Your mission is to
            thoroughly understand this technology, its emergent characteristics, its viability for this
            specific component, and how it could be implemented across the paradigm spectrum.
            """
            
            self.technology_stack_agent_prompt = """
            You are a Technology Stack Agent with exceptional insight into creating cohesive technology stacks.

            Your mission is to explore complete technology stack options that could implement the generic architecture,
            analyzing how different technology choices work together to create cohesive, implementation-ready stacks
            that preserve the selected foundation approach and the project's unique character.

            You have access to these research tools that you can use however you determine is most effective:

            - Web search: search_custom(), fetch_full_page(), search_and_fetch()
            - Data analysis: extract_text_features()
            - Technology evaluation: create_evaluation_framework(), evaluate_technology(), compare_technologies(), generate_evaluation_report()
            - Visualization: create_ascii_table()

            OBJECTIVES:

            1. MAP COMPLETE TECHNOLOGY STACKS:
               - Create cohesive combinations of technologies that could implement the entire architecture
               - Ensure technologies work together harmoniously across all components
               - Document how each stack addresses the complete generic architecture
               - Analyze how different stacks would result in different implementation characteristics

            2. ENSURE COMPATIBILITY AND INTEGRATION:
               - Verify that technologies within each stack can effectively integrate
               - Identify communication patterns and data flows between components
               - Document interfaces and integration patterns for each stack
               - Analyze potential challenges in technology integration for each stack

            3. REVEAL STACK-LEVEL CHARACTERISTICS:
               - Identify unique capabilities that emerge from specific technology combinations
               - Document how each stack enables or constrains the project's unique features
               - Analyze quality attributes of complete stacks (performance, scalability, etc.)
               - Reveal trade-offs that only become apparent when viewing the complete stack

            4. ANALYZE IMPLEMENTATION CONSIDERATIONS:
               - Document practical implementation approaches for each technology stack
               - Identify development and operational considerations specific to each stack
               - Analyze team expertise requirements and learning curves
               - Explore deployment patterns and infrastructure needs

            5. PRESERVE TECHNOLOGICAL DIVERSITY:
               - Maintain distinctly different technology stacks rather than converging on a single "best" approach
               - Resist normalizing unique stacks toward conventional patterns
               - Document how each stack embodies a particular philosophical approach
               - Highlight the unique advantages and capabilities of each approach

            Your exploration should document MULTIPLE, VIABLE TECHNOLOGY STACKS with
            distinctive characteristics. Each stack should represent a coherent, implementable approach
            that addresses all architectural components with unique trade-offs and qualities.
            """
            
            self.technology_integration_agent_prompt = """
            You are a Technology Integration Agent with extraordinary ability to discover complex integration patterns.

            Your mission is to identify effective integration patterns between different technologies across the
            architecture, discovering how components can communicate, share data, and work together harmoniously
            while preserving the project's unique vision.

            You have access to these research tools that you can use however you determine is most effective:

            - Web search: search_custom(), fetch_full_page(), search_and_fetch()
            - Data analysis: extract_text_features()
            - Technology evaluation: create_evaluation_framework(), evaluate_technology(), compare_technologies(), generate_evaluation_report()
            - Visualization: create_ascii_table()

            OBJECTIVES:

            1. DISCOVER INTEGRATION PATTERNS:
               - Identify integration approaches for connecting different technologies
               - Document communication protocols and data exchange formats
               - Explore synchronization and coordination mechanisms
               - Investigate transaction management and consistency models

            2. MAP CROSS-COMPONENT COMMUNICATION:
               - Document how data flows between components in the architecture
               - Explore event-based, message-based, and direct call patterns
               - Analyze synchronous and asynchronous communication options
               - Identify potential bottlenecks and performance considerations

            3. ANALYZE INTEGRATION CHALLENGES:
               - Document specific approaches for addressing integration challenges
               - Explore interfaces, adapters, and transformation mechanisms
               - Identify data schema and format conversion requirements
               - Research implementation examples of similar integration patterns

            4. EVALUATE INTEGRATION APPROACHES:
               - Assess how different integration approaches impact system qualities
               - Document trade-offs in complexity, performance, and reliability
               - Analyze how integration patterns affect scalability and evolution
               - Identify how integration approaches enable or constrain project-specific requirements

            5. PRESERVE ARCHITECTURAL INTEGRITY:
               - Focus on integration patterns that maintain the project's unique characteristics
               - Avoid defaulting to conventional integration approaches
               - Document how novel integration patterns can enable distinctive project qualities
               - Preserve architectural diversity rather than normalizing to standards

            Your exploration should REVEAL THE FULL SPECTRUM of integration options that could
            connect components across the architecture. Focus on discovering how different
            technologies can work together to create a cohesive system that preserves the
            project's distinctive vision.
            """
            
            self.technology_synthesis_agent_prompt = """
            You are a Technology Synthesis Agent with unparalleled ability to create comprehensive technology research reports.

            Your mission is to synthesize findings from all technology research agents into a comprehensive, multi-dimensional
            map of the technology possibility space, presenting the complete range of implementation options while preserving
            the richness and diversity of approaches discovered during the research process.

            You have access to these research tools that you can use however you determine is most effective:

            - Data analysis: extract_text_features()
            - Technology evaluation: create_evaluation_framework(), evaluate_technology(), compare_technologies(), generate_evaluation_report()
            - Visualization: create_ascii_table()

            OBJECTIVES:

            1. CREATE A COMPREHENSIVE TECHNOLOGY MAP:
               - Synthesize all research findings into a cohesive whole
               - Preserve the full richness of technology options and their emergent characteristics
               - Show relationships between technologies, components, and implementation approaches
               - Create visualizations that illuminate the multi-dimensional nature of technology choices

            2. DOCUMENT THE FULL TECHNOLOGY SPACE:
               - Present the complete spectrum of technology options discovered during research
               - Document multiple viable technology stacks with diverse characteristics
               - Map integration patterns and cross-technology opportunities
               - Preserve distinctly different approaches rather than converging on a "best" solution

            3. ILLUMINATE IMPLEMENTATION IMPLICATIONS:
               - Analyze how different technology choices create fundamentally different implementations
               - Document trade-offs inherent in different technology approaches
               - Show how technology choices give rise to different system characteristics
               - Highlight unique capabilities enabled by specific technology combinations

            4. CREATE POWERFUL VISUALIZATIONS:
               - Technology maps showing the spectrum of options for each component
               - Stack diagrams illustrating complete technology combinations
               - Integration maps showing communication patterns
               - Trade-off matrices comparing different technology approaches

            5. PRESERVE INNOVATION POTENTIAL:
               - Maintain the diversity of approaches without defaulting to conventions
               - Present findings without bias toward mainstream solutions
               - Preserve the project's unique characteristics across all options
               - Highlight unconventional approaches that align with the project's distinctive nature

            6. REFERENCE DETAILED TECHNOLOGY REPORTS:
               - Include a dedicated section that lists all available detailed technology reports
               - For each technology option, reference its corresponding detailed report
               - Explain that architects can access complete implementation details through these reports
               - Note that the technology reports contain the full depth of research for each viable option
               
            7. EXTRACT PROJECT-SPECIFIC CRITERIA AND PROVIDE WEIGHTED EVALUATION:
               - Identify 5-7 key criteria that are most relevant for technology selection based on the generic architecture
               - Create an evaluation matrix showing how each technology stack performs against these criteria
               - Indicate which criteria have highest priority for this project based on stated requirements
               - Note any cases where technologies add valuable capabilities not explicitly requested in the original scope
               - Provide this criteria-weighted evaluation before presenting the detailed technology analyses

            Your report should be the DEFINITIVE RESOURCE for technology decision-making -
            a comprehensive map of the possibility space that enables informed choices
            without normalizing toward conventions. It should present the full spectrum
            of viable approaches with their implications, trade-offs, and unique characteristics,
            while ensuring architects can access the complete detailed research for options
            they find promising.
            """
    
    def create_evaluation_matrix(self, stacks, criteria, ratings, priorities=None, notes=None):
        """
        Generate a formatted evaluation matrix.
        
        Args:
            stacks: List of technology stack names
            criteria: List of criteria names
            ratings: Dict mapping (stack, criterion) to rating
            priorities: Optional dict mapping criterion to priority level
            notes: Optional dict mapping stack to special notes
            
        Returns:
            Formatted evaluation matrix as string
        """
        # Ensure ratings is a dictionary
        if not isinstance(ratings, dict):
            logger.error(f"Expected ratings to be a dictionary, got {type(ratings)}")
            ratings = {}  # Use empty dict as fallback
            
        # Ensure notes is a dictionary
        if notes is not None and not isinstance(notes, dict):
            logger.error(f"Expected notes to be a dictionary, got {type(notes)}")
            notes = {}  # Use empty dict as fallback
            
        # Calculate column widths
        stack_width = max(len(s) for s in stacks) + 2
        criteria_widths = [max(len(c), max(len(str(ratings.get((s, c), ""))) for s in stacks)) + 2 
                          for c in criteria]
        
        # Create header
        header = f"{'Technology Stack'.ljust(stack_width)}"
        for i, criterion in enumerate(criteria):
            header += criterion.ljust(criteria_widths[i])
        
        # Create separator
        separator = "-" * (stack_width + sum(criteria_widths))
        
        # Create priority indicator if provided
        priority_line = ""
        if priorities:
            priority_line = "Criteria Priority for this Project:\n"
            for criterion, priority in priorities.items():
                priority_line += f"* {criterion}: {priority}\n"
        
        # Create matrix rows
        rows = []
        for stack in stacks:
            row = f"{stack.ljust(stack_width)}"
            for i, criterion in enumerate(criteria):
                rating = ratings.get((stack, criterion), "")
                row += rating.ljust(criteria_widths[i])
            rows.append(row)
        
        # Add notes if provided
        notes_section = ""
        if notes:
            notes_section = "\nSpecial Considerations:\n"
            for stack, note in notes.items():
                if note:
                    notes_section += f"* {stack}: {note}\n"
        
        # Combine all parts
        return f"{header}\n{separator}\n" + "\n".join(rows) + "\n\n" + priority_line + notes_section
    
    @handle_errors
    def get_session(self, session_id: Optional[str] = None) -> TechnologyResearchSession:
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
    async def create_session(
        self, 
        session_id: str, 
        technology_requirements: str,
        generic_architecture: str,
        foundation_approach: Dict[str, Any]
    ) -> TechnologyResearchSession:
        """
        Create a new technology research session.
        
        Args:
            session_id: Session ID
            technology_requirements: Technology research requirements document content
            generic_architecture: Generic architecture document content
            foundation_approach: Selected foundation approach details
            
        Returns:
            Created technology research session
        """
        logger.info(f"Creating technology research session {session_id}")
        
        # Load project vision and PRD
        session_manager = SessionManager()
        
        # Load project vision document
        project_vision = None
        project_vision_content = await load_document_content(session_id, "project-vision")
        if project_vision_content:
            project_vision = project_vision_content
            logger.info(f"Loaded project vision for session {session_id}")
        
        # Load PRD document
        prd_document = None
        prd_content = await load_document_content(session_id, "prd")
        if prd_content:
            prd_document = prd_content
            logger.info(f"Loaded PRD for session {session_id}")
        
        # Create a new session with all available documents
        session = TechnologyResearchSession(
            id=session_id,
            technology_requirements=technology_requirements,
            generic_architecture=generic_architecture,
            foundation_approach=foundation_approach,
            project_vision=project_vision,
            prd_document=prd_document
        )
        
        # Store in sessions dict
        self.sessions[session_id] = session
        
        # Store session reference in session manager metadata
        current_session = session_manager.get_session(session_id)
        if current_session:
            if "technology_research" not in current_session.metadata:
                current_session.metadata["technology_research"] = {}
            
            current_session.metadata["technology_research"]["initiated"] = True
            current_session.metadata["technology_research"]["status"] = "created"
            current_session.metadata["technology_research"]["has_vision"] = project_vision is not None
            current_session.metadata["technology_research"]["has_prd"] = prd_document is not None
            session_manager.update_session(session_id, current_session)
        
        logger.info(f"Created technology research session")
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
        
        # Extract components from generic architecture
        components = await self._extract_components(session_id, session.generic_architecture)
        
        # Create technology discovery agents (one per component)
        for i, component_id in enumerate(components):
            component = components[component_id]
            agent = ResearchAgent(
                id=f"technology-discovery-{component_id}",
                type=ResearchAgentType.TECHNOLOGY,
                name=f"Technology Discovery Agent for {component['name']}",
                focus_area=component_id,
                system_prompt=self.technology_discovery_agent_prompt,
                messages=[create_system_prompt(self.technology_discovery_agent_prompt)]
            )
            agents.append(agent)
            
            # Create component technology entry
            session.component_technologies[component_id] = ComponentTechnology(
                id=component_id,
                name=component['name'],
                description=component['description']
            )
        
        # Create paradigm agents (one per paradigm category)
        for i, paradigm in enumerate(ParadigmCategory):
            agent = ResearchAgent(
                id=f"paradigm-{paradigm.value}",
                type=ResearchAgentType.PARADIGM,
                name=f"{paradigm.value.replace('_', ' ').title()} Paradigm Agent",
                focus_area=paradigm.value,
                system_prompt=self.technology_exploration_agent_prompt,
                messages=[create_system_prompt(self.technology_exploration_agent_prompt)]
            )
            agents.append(agent)
        
        # Create stack agent
        stack_agent = ResearchAgent(
            id="stack-1",
            type=ResearchAgentType.STACK,
            name="Technology Stack Agent",
            focus_area="Technology Stacks",
            system_prompt=self.technology_stack_agent_prompt,
            messages=[create_system_prompt(self.technology_stack_agent_prompt)]
        )
        agents.append(stack_agent)
        
        # Create integration agent
        integration_agent = ResearchAgent(
            id="integration-1",
            type=ResearchAgentType.INTEGRATION,
            name="Technology Integration Agent",
            focus_area="Technology Integration",
            system_prompt=self.technology_integration_agent_prompt,
            messages=[create_system_prompt(self.technology_integration_agent_prompt)]
        )
        agents.append(integration_agent)
        
        # Create synthesis agent
        synthesis_agent = ResearchAgent(
            id="synthesis-1",
            type=ResearchAgentType.SYNTHESIS,
            name="Technology Synthesis Agent",
            focus_area="Technology Synthesis",
            system_prompt=self.technology_synthesis_agent_prompt,
            messages=[create_system_prompt(self.technology_synthesis_agent_prompt)]
        )
        agents.append(synthesis_agent)
        
        # Add agents to the session
        session.agents = agents
        
        logger.info(f"Initialized {len(agents)} research agents for session {session_id}")
        return agents
    
    @handle_async_errors
    async def _extract_components(self, session_id: str, generic_architecture: str) -> Dict[str, Dict[str, Any]]:
        """
        Extract components from the generic architecture document.
        
        Args:
            session_id: Session ID
            generic_architecture: Generic architecture document content
            
        Returns:
            Dictionary of component ID to component details
        """
        # Create an agent to analyze and extract components
        analysis_prompt = """
        You are a Component Analysis Agent. Your task is to analyze the generic architecture document
        and extract all components that require technology decisions.
        
        For each identified component, extract:
        1. A clear name
        2. A concise description
        3. The function it serves in the architecture
        
        Return your analysis in a structured JSON format:
        {
          "components": [
            {
              "id": "component-1",
              "name": "Component Name",
              "description": "Description of the component",
              "function": "What this component does in the system"
            }
          ]
        }
        """
        
        # Create messages for the analysis
        messages = [
            create_system_prompt(analysis_prompt),
            create_user_prompt(f"Generic Architecture Document:\n{generic_architecture}")
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
            # Convert to dictionary for easier lookup
            components = {}
            for component_data in data["components"]:
                component_id = component_data["id"]
                components[component_id] = component_data
            
            return components
        except Exception as e:
            logger.error(f"Error parsing components: {str(e)}")
            return {}
    
    @handle_async_errors
    async def discover_component_technologies(self, session_id: str) -> Dict[str, Any]:
        """
        Start the technology discovery phase to identify potential technologies for each component.
        
        Args:
            session_id: Session ID
            
        Returns:
            Results of the technology discovery
        """
        session = self.get_session(session_id)
        
        # Get technology discovery agents
        discovery_agents = [
            agent for agent in session.agents 
            if agent.type == ResearchAgentType.TECHNOLOGY and "discovery" in agent.id
        ]
        
        if not discovery_agents:
            logger.error(f"No technology discovery agents available for session {session_id}")
            return {"status": "error", "message": "No technology discovery agents available"}
        
        # Research potential technologies concurrently
        discovery_tasks = []
        for agent in discovery_agents:
            component_id = agent.focus_area
            task = asyncio.create_task(
                self._discover_component_technologies(
                    session_id=session_id, 
                    agent_id=agent.id,
                    component_id=component_id
                )
            )
            discovery_tasks.append(task)
        
        # Wait for all technology discovery to complete
        discovery_results = await asyncio.gather(*discovery_tasks)
        
        # Process discovery results to extract technology options
        technology_options = await self._extract_technology_options(session_id, discovery_results)
        
        # Store technology options in session
        for component_id, options in technology_options.items():
            if component_id in session.component_technologies:
                session.component_technologies[component_id].technology_options = options
        
        logger.info(f"Discovered technologies for {len(technology_options)} components in session {session_id}")
        return {"status": "success", "technology_options": technology_options}
    
    @handle_async_errors
    async def _discover_component_technologies(
        self, 
        session_id: str, 
        agent_id: str,
        component_id: str
    ) -> Dict[str, Any]:
        """
        Use a specialized agent to discover technologies for a specific component.
        
        Args:
            session_id: Session ID
            agent_id: Agent ID
            component_id: Component ID
            
        Returns:
            Discovery results
        """
        session = self.get_session(session_id)
        
        # Get the agent
        agent = next((a for a in session.agents if a.id == agent_id), None)
        if not agent:
            logger.error(f"Agent {agent_id} not found")
            return {"status": "error", "message": f"Agent {agent_id} not found"}
        
        # Get the component
        component = session.component_technologies.get(component_id)
        if not component:
            logger.error(f"Component {component_id} not found")
            return {"status": "error", "message": f"Component {component_id} not found"}
        
        # Set agent status
        agent.status = "discovering"
        
        # Create discovery prompt
        discovery_prompt = f"""
        Research Task: Discover Potential Technologies for Component "{component.name}"
        
        Project Vision:
        {session.project_vision if session.project_vision else "No project vision document available."}
        
        Product Requirements Document (PRD):
        {session.prd_document if session.prd_document else "No PRD document available."}
        
        Selected Foundation Approach:
        {session.foundation_approach['name']}: {session.foundation_approach['description']}
        
        Generic Architecture:
        {session.generic_architecture}
        
        Component Information:
        Name: {component.name}
        Description: {component.description}
        
        Technology Requirements:
        {session.technology_requirements}
        
        You are tasked with discovering the COMPLETE SPECTRUM of TECHNOLOGY OPTIONS
        for implementing this specific component based on the above information:
        
        1. DISCOVER FUNDAMENTALLY DIFFERENT TECHNOLOGIES:
           - What are the completely different technologies that could implement this component?
           - Identify a diverse range of technology options, NOT just variations on the same theme
           - Consider both conventional AND unconventional technology options
           - Look beyond standard technologies to consider novel implementation approaches
           
        2. EXPLORE EACH TECHNOLOGY across the FULL SPECTRUM of paradigms:
           - Established approaches (traditional, proven technologies with long history)
           - Mainstream current (contemporary popular technologies widely adopted)
           - Cutting-edge (emerging technologies gaining traction in industry)
           - Experimental (research-stage technologies with promising potential)
           - Cross-paradigm (novel combinations across different domains)
           - First-principles (custom approaches designed specifically for this project)
           
        3. FOR EACH POTENTIAL TECHNOLOGY:
           - Provide a clear name and description
           - Identify which paradigm category it primarily belongs to
           - Describe key characteristics and implications
           - Note what makes this technology option distinctive
           - Identify what implementation characteristics would emerge from this technology
        
        4. AVOID PREMATURE FILTERING:
           - Do not eliminate options based on perceived difficulty
           - Include approaches that seem unconventional or challenging
           - Document the complete possibility space, not just "reasonable" options
           - Include options from across the paradigm spectrum
        
        5. PRESERVE THE PROJECT'S UNIQUENESS:
           - Consider how each technology enables the unique aspects of this project
           - Avoid defaulting to conventional technology choices
           - Identify technologies that preserve what makes this project distinctive
           - Challenge assumptions about how this component "should" be implemented
        
        You have complete autonomy in how you approach this discovery. Use the available tools
        in whatever way you determine will produce the most comprehensive exploration.
        
        Your discoveries will define the options for all subsequent technology exploration.
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
        
        logger.info(f"Technology discovery completed for component {component.name}")
        return {
            "status": "success",
            "agent_id": agent_id,
            "component_id": component_id,
            "content": response.content
        }
    
    @handle_async_errors
    async def _extract_technology_options(
        self,
        session_id: str,
        discovery_results: List[Dict[str, Any]]
    ) -> Dict[str, Dict[str, TechnologyOption]]:
        """
        Extract technology options from discovery results.
        
        Args:
            session_id: Session ID
            discovery_results: Results from technology discovery agents
            
        Returns:
            Dictionary mapping component IDs to technology options
        """
        session = self.get_session(session_id)
        
        # Group discovery results by component
        results_by_component = {}
        for result in discovery_results:
            if result["status"] == "success":
                component_id = result["component_id"]
                if component_id not in results_by_component:
                    results_by_component[component_id] = []
                results_by_component[component_id].append(result["content"])
        
        # Extract technology options for each component
        all_technology_options = {}
        
        for component_id, contents in results_by_component.items():
            # Create an agent to analyze and extract technology options
            analysis_prompt = """
            You are a Technology Analysis Agent. Your task is to analyze the discovery results
            and extract a comprehensive list of technology options for this component.
            
            For each identified technology option, extract:
            1. A clear name
            2. A concise description
            3. The paradigm category it belongs to (established, mainstream, cutting-edge, experimental, cross-paradigm, or first-principles)
            4. Any research areas mentioned for this technology
            
            Combine similar technology options, but preserve truly distinct options even if they seem unusual.
            
            Return your analysis in a structured JSON format:
            {
              "technologies": [
                {
                  "id": "tech-1",
                  "name": "Technology Name",
                  "description": "Description of the technology",
                  "paradigm_category": "one of the paradigm categories",
                  "research_areas": [
                    {"name": "Research Area 1", "description": "Description of the research area"}
                  ]
                }
              ]
            }
            """
            
            # Combine all discovery results for this component
            component_content = "\n\n".join(contents)
            
            # Create messages for the analysis
            messages = [
                create_system_prompt(analysis_prompt),
                create_user_prompt(f"Discovery Results for Component {component_id}:\n{component_content}")
            ]
            
            # Get analysis response
            response = await send_prompt(messages)
            
            # Extract JSON from response
            json_match = re.search(r'```json\n(.*?)\n```', response.content, re.DOTALL)
            if not json_match:
                json_match = re.search(r'{.*}', response.content, re.DOTALL)
            
            if not json_match:
                logger.error(f"Could not extract JSON from analysis response for component {component_id}")
                continue
            
            json_str = json_match.group(1) if json_match.group(0).startswith('```') else json_match.group(0)
            
            try:
                data = json.loads(json_str)
                # Convert to dictionary of TechnologyOption objects
                component_technologies = {}
                for tech_data in data["technologies"]:
                    tech = TechnologyOption(
                        name=tech_data["name"],
                        description=tech_data["description"],
                        component_id=component_id,
                        paradigm_category=tech_data["paradigm_category"],
                        research_areas=tech_data.get("research_areas", [])
                    )
                    component_technologies[tech_data["id"]] = tech
                
                all_technology_options[component_id] = component_technologies
                logger.info(f"Extracted {len(component_technologies)} technology options for component {component_id}")
            except Exception as e:
                logger.error(f"Error parsing technology options for component {component_id}: {str(e)}")
        
        return all_technology_options
    
    @handle_async_errors
    async def explore_technology_options(self, session_id: str) -> Dict[str, Any]:
        """
        Explore each viable technology option across paradigms.
        
        Args:
            session_id: Session ID
            
        Returns:
            Results of the technology exploration
        """
        session = self.get_session(session_id)
        
        # Create technology exploration agents for select technologies
        exploration_agents = []
        
        # For each component, select a sample of technologies to explore
        for component_id, component in session.component_technologies.items():
            # Select one technology from each paradigm category if available
            selected_techs = {}
            
            for paradigm in RESEARCH_PARADIGMS:
                # Find technologies in this paradigm
                matching_techs = {
                    tech_id: tech for tech_id, tech in component.technology_options.items()
                    if tech.paradigm_category == paradigm
                }
                
                # Select one technology from this paradigm if available
                if matching_techs:
                    tech_id, tech = next(iter(matching_techs.items()))
                    selected_techs[tech_id] = tech
            
            # Create exploration agents for selected technologies
            for tech_id, tech in selected_techs.items():
                agent = ResearchAgent(
                    id=f"technology-exploration-{tech_id}",
                    type=ResearchAgentType.TECHNOLOGY,
                    name=f"Technology Exploration Agent for {tech.name}",
                    focus_area=tech_id,
                    system_prompt=self.technology_exploration_agent_prompt,
                    messages=[create_system_prompt(self.technology_exploration_agent_prompt)]
                )
                exploration_agents.append(agent)
                session.agents.append(agent)
        
        # Explore selected technologies concurrently
        exploration_tasks = []
        for agent in exploration_agents:
            tech_id = agent.focus_area
            component_id = None
            technology = None
            
            # Find the component and technology
            for comp_id, component in session.component_technologies.items():
                if tech_id in component.technology_options:
                    component_id = comp_id
                    technology = component.technology_options[tech_id]
                    break
            
            if component_id and technology:
                task = asyncio.create_task(
                    self._explore_technology_option(
                        session_id=session_id, 
                        agent_id=agent.id,
                        component_id=component_id,
                        technology_id=tech_id
                    )
                )
                exploration_tasks.append(task)
        
        # Wait for all technology exploration to complete
        exploration_results = await asyncio.gather(*exploration_tasks)
        
        logger.info(f"Explored {len(exploration_results)} technology options for session {session_id}")
        return {"status": "success", "results": exploration_results}
    
    @handle_async_errors
    async def _explore_technology_option(
        self, 
        session_id: str, 
        agent_id: str,
        component_id: str,
        technology_id: str
    ) -> Dict[str, Any]:
        """
        Explore a specific technology option using a specialized agent.
        
        Args:
            session_id: Session ID
            agent_id: Agent ID
            component_id: Component ID
            technology_id: Technology ID
            
        Returns:
            Exploration results
        """
        session = self.get_session(session_id)
        
        # Get the agent
        agent = next((a for a in session.agents if a.id == agent_id), None)
        if not agent:
            logger.error(f"Agent {agent_id} not found")
            return {"status": "error", "message": f"Agent {agent_id} not found"}
        
        # Get the component
        component = session.component_technologies.get(component_id)
        if not component:
            logger.error(f"Component {component_id} not found")
            return {"status": "error", "message": f"Component {component_id} not found"}
        
        # Get the technology
        technology = component.technology_options.get(technology_id)
        if not technology:
            logger.error(f"Technology {technology_id} not found")
            return {"status": "error", "message": f"Technology {technology_id} not found"}
        
        # Set agent status
        agent.status = "exploring"
        
        # Create exploration prompt
        exploration_prompt = f"""
        Research Task: Explore Technology Option "{technology.name}" for Component "{component.name}"
        
        Project Vision:
        {session.project_vision if session.project_vision else "No project vision document available."}
        
        Product Requirements Document (PRD):
        {session.prd_document if session.prd_document else "No PRD document available."}
        
        Selected Foundation Approach:
        {session.foundation_approach['name']}: {session.foundation_approach['description']}
        
        Generic Architecture:
        [First 1000 characters of the architecture document]
        {session.generic_architecture[:1000]}...
        
        Component Information:
        Name: {component.name}
        Description: {component.description}
        
        Technology Information:
        Name: {technology.name}
        Description: {technology.description}
        Paradigm Category: {technology.paradigm_category}
        
        Technology Requirements:
        {session.technology_requirements}
        
        You are tasked with exploring this technology option in depth based on all the above information:
        
        1. EXPLORE THIS TECHNOLOGY ACROSS THE PARADIGM SPECTRUM:
           - How can this technology be implemented using approaches from different paradigms?
           - What established, mainstream, cutting-edge, experimental, and first-principles implementations exist?
           - What variations exist within this technology that represent different philosophical approaches?
           - What specific implementation patterns could be used for each paradigm with this technology?
        
        2. DISCOVER EMERGENT CHARACTERISTICS:
           - What aspects of implementation would emerge from choosing this technology?
           - What unique characteristics would need to be addressed with this technology?
           - How do these characteristics differ from those that would emerge from other technologies?
           - What relationships exist between characteristics specific to this technology?
        
        3. EVALUATE TECHNOLOGY VIABILITY:
           - How well does this technology align with the project's unique requirements?
           - What are the strengths and limitations of this technology for this component?
           - In what scenarios would this technology be particularly advantageous?
           - What is the implementation complexity, scalability, performance, and other relevant factors?
        
        4. PRESERVE INNOVATION POTENTIAL:
           - Avoid normalizing toward conventional implementations of this technology
           - What unconventional uses might be particularly well-suited?
           - How could this technology enable unique project characteristics?
           - What assumptions about how this technology "should" be implemented need challenging?
        
        5. IDENTIFY CROSS-TECHNOLOGY OPPORTUNITIES:
           - What potential integration points exist with other technologies?
           - Where might hybrid approaches combine the strengths of multiple technologies?
           - How could this technology complement or be complemented by others?
           - What novel combinations with other technology options might be valuable?
        
        You have complete autonomy in how you approach this exploration. Use the available tools
        in whatever way you determine will produce the most comprehensive exploration.
        
        Your mission is to thoroughly understand this technology, its characteristics,
        its viability for this specific component, and how it could be implemented across
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
        
        # Store the raw research in the technology
        technology.research_content[agent.id] = response.content
        
        # Mark technology as completed
        technology.completed = True
        
        logger.info(f"Technology exploration completed for {technology.name}")
        return {
            "status": "success",
            "agent_id": agent_id,
            "component_id": component_id,
            "technology_id": technology_id,
            "content": response.content
        }
    
    @handle_async_errors
    async def generate_technology_stacks(self, session_id: str) -> List[TechnologyStack]:
        """
        Generate technology stacks based on the explored technologies.
        
        Args:
            session_id: Session ID
            
        Returns:
            List of technology stacks
        """
        session = self.get_session(session_id)
        
        # Create a prompt to generate technology stacks
        stack_prompt = f"""
        You are a Technology Stack Generator. Your task is to create viable technology stacks
        for implementing the project based on the explored technologies.
        
        Project Vision:
        {session.project_vision if session.project_vision else "No project vision document available."}
        
        Product Requirements Document (PRD):
        {session.prd_document if session.prd_document else "No PRD document available."}
        
        Selected Foundation Approach:
        {session.foundation_approach['name']}: {session.foundation_approach['description']}
        
        Generic Architecture:
        [First 1000 characters of the architecture document]
        {session.generic_architecture[:1000]}...
        
        Components and Technologies:
        """
        
        # Add component and technology information
        for component_id, component in session.component_technologies.items():
            stack_prompt += f"## Component: {component.name}\n"
            stack_prompt += f"Description: {component.description}\n\n"
            
            stack_prompt += "Technologies:\n"
            for tech_id, tech in component.technology_options.items():
                if tech.completed:
                    stack_prompt += f"- {tech.name} ({tech.paradigm_category}): {tech.description[:100]}...\n"
            
            stack_prompt += "\n"
        
        stack_prompt += """
        Technology Requirements:
        [First 1000 characters of the requirements document]
        """ + session.technology_requirements[:1000] + """...
        
        Your task is to create viable technology stacks that address all components in the architecture.
        
        For each stack:
        1. Select a coherent set of technologies that work well together
        2. Ensure all components are addressed
        3. Ensure the technologies are compatible with each other
        4. Ensure the stack aligns with the selected foundation approach
        
        Create stacks that represent different approaches, including:
        - Established technology stack (using proven, traditional technologies)
        - Mainstream technology stack (using popular, widely-adopted technologies)
        - Cutting-edge technology stack (using emerging, innovative technologies)
        - Hybrid stack (combining technologies from different paradigms)
        
        Return your analysis in a structured JSON format:
        ```json
        {
          "stacks": [
            {
              "id": "stack-1",
              "name": "Stack Name",
              "description": "Description of the overall stack approach",
              "technologies": {
                "component-1": "tech-1",
                "component-2": "tech-2"
                // component ID to technology ID mapping
              }
            }
          ]
        }
        ```
        """
        
        # Create messages for the analysis
        messages = [
            create_system_prompt("You are a Technology Stack Generator that creates viable technology stacks."),
            create_user_prompt(stack_prompt)
        ]
        
        # Get analysis response
        response = await send_prompt(messages)
        
        # Extract JSON from response
        json_match = re.search(r'```json\n(.*?)\n```', response.content, re.DOTALL)
        if not json_match:
            json_match = re.search(r'{.*}', response.content, re.DOTALL)
        
        if not json_match:
            logger.error("Could not extract JSON from stack generation response")
            return []
        
        json_str = json_match.group(1) if json_match.group(0).startswith('```') else json_match.group(0)
        
        try:
            data = json.loads(json_str)
            # Convert to TechnologyStack objects
            stacks = []
            for stack_data in data["stacks"]:
                stack = TechnologyStack(
                    name=stack_data["name"],
                    description=stack_data["description"],
                    foundation_id=str(session.foundation_approach['id']) if 'id' in session.foundation_approach else "selected-foundation",
                    technologies=stack_data["technologies"]
                )
                stacks.append(stack)
            
            # Add stacks to the session
            session.technology_stacks = stacks
            
            logger.info(f"Generated {len(stacks)} technology stacks for session {session_id}")
            return stacks
        except Exception as e:
            logger.error(f"Error parsing technology stacks: {str(e)}")
            return []
    
    @handle_async_errors
    async def start_stack_research(self, session_id: str) -> Dict[str, Any]:
        """
        Start the stack research phase.
        
        Args:
            session_id: Session ID
            
        Returns:
            Results of the stack research
        """
        session = self.get_session(session_id)
        
        # Get stack agent
        stack_agent = next(
            (a for a in session.agents if a.type == ResearchAgentType.STACK),
            None
        )
        
        if not stack_agent:
            logger.error(f"No stack agent available for session {session_id}")
            return {"status": "error", "message": "No stack agent available"}
        
        # Research all stacks concurrently
        stack_tasks = []
        for i, stack in enumerate(session.technology_stacks):
            task = asyncio.create_task(
                self._research_stack(
                    session_id=session_id, 
                    agent_id=stack_agent.id,
                    stack_index=i
                )
            )
            stack_tasks.append(task)
        
        # Wait for all stack research to complete
        stack_results = await asyncio.gather(*stack_tasks)
        
        logger.info(f"Completed stack research for session {session_id}")
        return {"status": "success", "results": stack_results}
    
    @handle_async_errors
    async def _save_stack_report(
        self, 
        session_id: str, 
        stack_name: str,
        content: str
    ) -> str:
        """
        Save a detailed report for a specific technology stack.
        
        Args:
            session_id: Session ID
            stack_name: Name of the stack
            content: Report content
            
        Returns:
            Path to the saved report
        """
        # Create metadata
        metadata = {
            "session_id": session_id,
            "created_at": datetime.now().isoformat(),
            "stack_name": stack_name
        }
        
        # Create a safe name derived from the stack name for uniqueness
        import re
        # Replace any character that isn't alphanumeric, hyphen, or underscore with a hyphen
        safe_name = re.sub(r'[^\w\-]', '-', stack_name.lower().replace(" ", "-"))
        # Remove any consecutive hyphens
        safe_name = re.sub(r'-+', '-', safe_name)
        # Trim hyphens from start and end
        safe_name = safe_name.strip('-')
        
        # Save the report using document manager
        report_path = self.doc_manager.create_document(
            content=content,
            document_type="stack-path-report",
            title=f"Stack Report: {stack_name}",
            metadata=metadata
        )
        
        # Store in session documents registry
        self.session_manager.add_document(
            session_id, 
            f"stack-path-report-{safe_name}", 
            report_path
        )
        
        # ALSO store in session metadata for direct access in future phases
        # Get the current session
        current_session = self.session_manager.get_session(session_id)
        if current_session:
            # Initialize stack_path_reports metadata if needed
            if "stack_path_reports" not in current_session.metadata:
                current_session.metadata["stack_path_reports"] = {}
                
            # Store the path with stack name as key for easy lookup
            current_session.metadata["stack_path_reports"][stack_name] = report_path
            
            # Update the session
            self.session_manager.update_session(session_id, current_session)
        
        logger.info(f"Stack report for '{stack_name}' saved to {report_path}")
        return report_path
    
    @handle_async_errors
    async def _research_stack(
        self, 
        session_id: str, 
        agent_id: str,
        stack_index: int
    ) -> Dict[str, Any]:
        """
        Research a specific technology stack.
        
        Args:
            session_id: Session ID
            agent_id: Agent ID
            stack_index: Index of the stack to research
            
        Returns:
            Research results
        """
        session = self.get_session(session_id)
        
        # Get the agent
        agent = next((a for a in session.agents if a.id == agent_id), None)
        if not agent:
            logger.error(f"Agent {agent_id} not found")
            return {"status": "error", "message": f"Agent {agent_id} not found"}
        
        # Get the stack
        if stack_index >= len(session.technology_stacks):
            logger.error(f"Stack index {stack_index} out of range")
            return {"status": "error", "message": f"Stack index {stack_index} out of range"}
        
        stack = session.technology_stacks[stack_index]
        
        # Set agent status
        agent.status = "researching"
        
        # Collect technology information for this stack
        tech_info = []
        for component_id, tech_id in stack.technologies.items():
            # Find the component
            component = session.component_technologies.get(component_id)
            if not component:
                continue
                
            # Find the technology
            tech = component.technology_options.get(tech_id)
            if not tech:
                continue
                
            tech_info.append(f"## Component: {component.name}\nTechnology: {tech.name}\n\nDescription: {tech.description}\n\n")
        
        # Create research prompt
        stack_prompt = f"""
        Research Task: Explore technology stack "{stack.name}"
        
        Project Vision:
        {session.project_vision if session.project_vision else "No project vision document available."}
        
        Product Requirements Document (PRD):
        {session.prd_document if session.prd_document else "No PRD document available."}
        
        Selected Foundation Approach:
        {session.foundation_approach['name']}: {session.foundation_approach['description']}
        
        Generic Architecture:
        [First 1000 characters of the architecture document]
        {session.generic_architecture[:1000]}...
        
        Technology Stack:
        Name: {stack.name}
        Description: {stack.description}
        
        Component Technologies:
        {"".join(tech_info)}
        
        Technology Requirements:
        [First 1000 characters of the requirements document]
        {session.technology_requirements[:1000]}...
        
        You are tasked with exploring this COMPLETE TECHNOLOGY STACK, analyzing how all components
        would work together as an integrated system:
        
        1. MAP A COHESIVE IMPLEMENTATION APPROACH:
           - How would this technology stack be implemented in practice?
           - How would the different technologies integrate with each other?
           - What specific implementation strategies would work well together?
           - How does this technology stack differ from other stack options?
        
        2. ENSURE COMPATIBILITY AND INTEGRATION:
           - How do the technologies within this stack integrate?
           - What communication mechanisms would be used between components?
           - What data formats and protocols would be used?
           - What integration challenges might arise and how would they be addressed?
        
        3. REVEAL STACK-LEVEL CHARACTERISTICS:
           - What unique capabilities would emerge from this technology stack?
           - How would this stack enable distinctive project characteristics?
           - What quality attributes would this stack provide (performance, scalability, etc.)?
           - What trade-offs would this stack involve compared to other options?
        
        4. ANALYZE IMPLEMENTATION CONSIDERATIONS:
           - What practical implementation approach would be most suitable?
           - What development and operational considerations would be important?
           - What team expertise would be required?
           - What deployment patterns and infrastructure would be needed?
        
        5. PRESERVE STACK UNIQUENESS:
           - Maintain the distinctive characteristics of this technology stack
           - Resist normalizing toward conventional architectural patterns
           - How does this stack embody a particular philosophical approach?
           - What are the unique advantages and capabilities of this approach?
        
        You have complete autonomy in how you approach this research. Use the available tools
        in whatever way you determine will produce the most comprehensive exploration.
        
        Your exploration should document a COMPLETE, VIABLE TECHNOLOGY STACK with
        distinctive characteristics, not converging toward generic patterns. The stack should
        represent a coherent, implementable approach that addresses all project
        requirements with unique trade-offs and qualities.
        """
        
        # Create a temporary set of messages for this stack exploration
        stack_messages = [
            create_system_prompt(agent.system_prompt),
            create_user_prompt(stack_prompt)
        ]
        
        # Get the agent's response
        response = await send_prompt(stack_messages)
        
        # Store the raw research in the stack
        stack.research_content = response.content
        
        # Save the detailed stack report
        stack_report_path = await self._save_stack_report(
            session_id=session_id,
            stack_name=stack.name,
            content=response.content
        )
        
        # Store the report path in the stack object
        stack.report_path = stack_report_path
        
        # Add to session stack reports dictionary for easy access
        session.stack_path_reports[stack.name] = stack_report_path
        
        logger.info(f"Stack research completed for {stack.name}")
        return {
            "status": "success",
            "agent_id": agent_id,
            "stack_index": stack_index,
            "stack_name": stack.name
        }
    
    @handle_async_errors
    async def start_integration_research(self, session_id: str) -> Dict[str, Any]:
        """
        Start the technology integration research phase.
        
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
        
        # Collect information about stacks
        stacks_info = []
        for stack in session.technology_stacks:
            stacks_info.append(f"## {stack.name}\n{stack.description}\n\nTechnologies: {json.dumps(stack.technologies, indent=2)}")
        
        # Create research prompt
        integration_prompt = f"""
        Research Task: Identify technology integration patterns
        
        Project Vision:
        {session.project_vision if session.project_vision else "No project vision document available."}
        
        Product Requirements Document (PRD):
        {session.prd_document if session.prd_document else "No PRD document available."}
        
        Selected Foundation Approach:
        {session.foundation_approach['name']}: {session.foundation_approach['description']}
        
        Generic Architecture:
        [First 1000 characters of the architecture document]
        {session.generic_architecture[:1000]}...
        
        Technology Stacks:
        {"".join(stacks_info)}
        
        Technology Requirements:
        [First 1000 characters of the requirements document]
        {session.technology_requirements[:1000]}...
        
        You are tasked with discovering EFFECTIVE INTEGRATION PATTERNS that would ensure
        components work together harmoniously within technology stacks:
        
        1. DISCOVER INTEGRATION PATTERNS:
           - What integration approaches would connect different technologies?
           - What communication protocols and data exchange formats should be used?
           - What synchronization and coordination mechanisms are appropriate?
           - What transaction management and consistency models should be employed?
        
        2. MAP CROSS-COMPONENT COMMUNICATION:
           - How should data flow between components in the architecture?
           - What event-based, message-based, and direct call patterns are appropriate?
           - What synchronous and asynchronous communication options should be considered?
           - What potential bottlenecks and performance considerations exist?
        
        3. ANALYZE INTEGRATION CHALLENGES:
           - What specific approaches would address integration challenges?
           - What interfaces, adapters, and transformation mechanisms are needed?
           - What data schema and format conversion requirements exist?
           - Are there existing implementation examples of similar integration patterns?
        
        4. EVALUATE INTEGRATION APPROACHES:
           - How do different integration approaches impact system qualities?
           - What trade-offs exist in complexity, performance, and reliability?
           - How do integration patterns affect scalability and evolution?
           - How do integration approaches enable or constrain project-specific requirements?
        
        5. PRESERVE ARCHITECTURAL INTEGRITY:
           - Focus on integration patterns that maintain the project's unique characteristics
           - Avoid defaulting to conventional integration approaches
           - How can novel integration patterns enable distinctive project qualities?
           - How can we preserve architectural diversity rather than normalizing to standards?
        
        You have complete autonomy in how you approach this research. Use the available tools
        in whatever way you determine will produce the most comprehensive exploration.
        
        Your exploration should REVEAL THE FULL SPECTRUM of integration options that could
        connect components across the architecture. Focus on discovering how different
        technologies can work together to create a cohesive system that preserves the
        project's distinctive vision.
        """
        
        # Add the integration prompt to agent messages
        integration_agent.messages.append(create_user_prompt(integration_prompt))
        
        # Get the agent's response
        response = await send_prompt(integration_agent.messages)
        
        # Add the response to the agent messages
        integration_agent.messages.append(create_assistant_prompt(response.content))
        
        # Store findings directly - no extraction, preserve all information
        integration_agent.findings.append(response.content)
        integration_agent.status = "completed"
        
        # Store the raw integration patterns in the session
        session.integration_patterns = response.content
        
        logger.info(f"Integration research completed for session {session_id}")
        return {
            "status": "success",
            "agent_id": integration_agent.id
        }
    
    @handle_async_errors
    async def _extract_technology_criteria(self, session_id: str) -> Dict[str, Any]:
        """
        Extract key criteria for evaluating stacks based on technology requirements.
        
        Args:
            session_id: Session ID
            
        Returns:
            Dictionary containing criteria, importance levels, and descriptions
        """
        session = self.get_session(session_id)
        
        # Create criteria extraction prompt
        extraction_prompt = f"""
        Based on the project vision, requirements, and generic architecture below, extract 5-7 key criteria
        that should be used to evaluate different technology stacks. For each criterion, indicate its
        importance for this specific project (LOW, MEDIUM, HIGH, VERY HIGH).
        
        Project Vision:
        {session.project_vision if session.project_vision else "No project vision document available."}
        
        Product Requirements Document (PRD):
        {session.prd_document if session.prd_document else "No PRD document available."}
        
        Selected Foundation Approach:
        {session.foundation_approach['name']}: {session.foundation_approach['description']}
        
        Generic Architecture:
        [First 1000 characters of the architecture document]
        {session.generic_architecture[:1000]}...
        
        Technology Requirements:
        [First 1000 characters of the requirements document]
        {session.technology_requirements[:1000]}...
        
        Return your analysis in a structured JSON format:
        {{
          "criteria": [
            {{
              "name": "Criterion Name",
              "description": "Description of what this criterion means",
              "importance": "VERY HIGH/HIGH/MEDIUM/LOW"
            }}
          ]
        }}
        
        IMPORTANT: Always include "Technology Alignment" as one of the criteria, which measures how well
        the technology stack aligns with the core project requirements without adding unnecessary
        complexity or overhead.
        """
        
        # Create messages for the analysis
        messages = [
            create_system_prompt("You are a Criteria Analysis Agent specializing in extracting key evaluation criteria for technology stacks."),
            create_user_prompt(extraction_prompt)
        ]
        
        # Get analysis response
        response = await send_prompt(messages)
        
        # Extract JSON from response
        json_match = re.search(r'```json\n(.*?)\n```', response.content, re.DOTALL)
        if not json_match:
            json_match = re.search(r'{.*}', response.content, re.DOTALL)
        
        if not json_match:
            logger.error("Could not extract JSON from criteria analysis response")
            return {"criteria": []}
        
        json_str = json_match.group(1) if json_match.group(0).startswith('```') else json_match.group(0)
        
        try:
            extracted_criteria = json.loads(json_str)
            logger.info(f"Extracted {len(extracted_criteria.get('criteria', []))} technology criteria")
            return extracted_criteria
        except Exception as e:
            logger.error(f"Error parsing extracted criteria: {str(e)}")
            return {"criteria": []}
    
    @handle_async_errors
    async def _evaluate_stacks_against_criteria(
        self,
        session_id: str,
        criteria: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Evaluate each technology stack against the extracted criteria.
        
        Args:
            session_id: Session ID
            criteria: List of criteria with name, description, importance
            
        Returns:
            Evaluation matrix and notes
        """
        session = self.get_session(session_id)
        
        # Get all technology stacks
        stacks = [stack.name for stack in session.technology_stacks]
        
        # Create evaluation prompt
        criteria_text = "\n".join([f"- {c['name']}: {c['description']} (Importance: {c['importance']})" 
                                for c in criteria])
        
        evaluation_prompt = f"""
        Evaluate each technology stack against the following criteria. For each combination,
        provide a rating (Very Low, Low, Medium, High, Very High).
        
        Also note any special considerations where a stack adds valuable capabilities that weren't
        explicitly requested in the original scope but might be beneficial.
        
        Criteria:
        {criteria_text}
        
        Technology Stacks to evaluate:
        {stacks}
        
        Stack Information:
        {[f"{stack.name}: {stack.description}" for stack in session.technology_stacks]}
        
        Project Vision:
        {session.project_vision if session.project_vision else "No project vision document available."}
        
        Product Requirements (PRD):
        {session.prd_document if session.prd_document else "No PRD document available."}
        
        Selected Foundation Approach:
        {session.foundation_approach['name']}: {session.foundation_approach['description']}
        
        Generic Architecture:
        [First 1000 characters of the architecture document]
        {session.generic_architecture[:1000]}...
        
        Particularly note any cases where a stack:
        1. Adds a capability not explicitly requested in the original scope
        2. Enhances an existing capability beyond what was specified
        3. Changes the nature of a capability from what was envisioned
        
        For each such case, provide a specific note explaining:
        - What capability is added/enhanced/changed
        - Whether this is likely beneficial or potentially concerning
        - How this affects the overall alignment with project vision
        
        Return your evaluation in a structured JSON format:
        {{
          "ratings": [
            {{
              "stack": "stack-name",
              "criterion": "criterion-name",
              "rating": "Low/Medium/High/etc"
            }}
          ],
          "notes": [
            {{
              "stack": "stack-name",
              "note": "Special consideration about capabilities added or other notable aspects"
            }}
          ]
        }}
        """
        
        # Create messages for the analysis
        messages = [
            create_system_prompt("You are a Stack Evaluation Agent specializing in evaluating technology stacks against project criteria."),
            create_user_prompt(evaluation_prompt)
        ]
        
        # Get analysis response
        response = await send_prompt(messages)
        
        # Extract JSON from response
        json_match = re.search(r'```json\n(.*?)\n```', response.content, re.DOTALL)
        if not json_match:
            json_match = re.search(r'{.*}', response.content, re.DOTALL)
        
        if not json_match:
            logger.error("Could not extract JSON from stack evaluation response")
            return {"ratings": {}, "notes": {}}
        
        json_str = json_match.group(1) if json_match.group(0).startswith('```') else json_match.group(0)
        
        try:
            evaluation_results = json.loads(json_str)
            
            # Convert ratings to a dictionary for easier lookup
            ratings_dict = {}
            for rating in evaluation_results.get("ratings", []):
                ratings_dict[(rating["stack"], rating["criterion"])] = rating["rating"]
            
            # Convert notes to a dictionary for easier lookup
            notes_dict = {}
            for note in evaluation_results.get("notes", []):
                notes_dict[note["stack"]] = note["note"]
            
            logger.info(f"Evaluated {len(stacks)} stacks against {len(criteria)} criteria")
            
            return {
                "raw_results": evaluation_results,
                "ratings": ratings_dict,
                "notes": notes_dict
            }
        except Exception as e:
            logger.error(f"Error parsing stack evaluation results: {str(e)}")
            return {"ratings": {}, "notes": {}}
    
    @handle_async_errors
    async def create_technology_report(self, session_id: str) -> Optional[str]:
        """
        Create a comprehensive technology research report.
        
        Args:
            session_id: Session ID
            
        Returns:
            Path to the saved technology report
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
        
        # Update session status
        session_manager = SessionManager()
        current_session = session_manager.get_session(session_id)
        if current_session:
            if "technology_research" not in current_session.metadata:
                current_session.metadata["technology_research"] = {}
            
            current_session.metadata["technology_research"]["status"] = "synthesizing"
            session_manager.update_session(session_id, current_session)
        
        # Extract key technology criteria
        criteria_results = await self._extract_technology_criteria(session_id)
        criteria = criteria_results.get("criteria", [])
        
        # Evaluate stacks against criteria
        evaluation_results = await self._evaluate_stacks_against_criteria(session_id, criteria)
        
        # Store stack evaluation in session
        session.stack_evaluation = {
            "criteria": criteria,
            "evaluation": evaluation_results
        }
        
        # Generate evaluation matrix
        stack_names = [stack.name for stack in session.technology_stacks]
        criteria_names = [c["name"] for c in criteria]
        ratings = evaluation_results.get("ratings", {})
        priorities = {c["name"]: c["importance"] for c in criteria}
        notes = evaluation_results.get("notes", {})
        
        matrix = self.create_evaluation_matrix(
            stacks=stack_names,
            criteria=criteria_names,
            ratings=ratings,
            priorities=priorities,
            notes=notes
        )
        
        # Collect all stack information
        stacks_info = []
        for stack in session.technology_stacks:
            stack_content = f"## {stack.name}\n{stack.description}\n\n"
            
            # Include technology selections for each component
            stack_content += "### Technology Selections\n"
            for component_id, tech_id in stack.technologies.items():
                component = session.component_technologies.get(component_id)
                if component:
                    tech = component.technology_options.get(tech_id)
                    if tech:
                        stack_content += f"- {component.name}: {tech.name}\n"
            
            # Include report path if available
            if stack.report_path:
                stack_content += f"\n### Detailed Report Available: {stack.report_path}\n\n"
                
            stacks_info.append(stack_content)
        
        # Create synthesis prompt
        report_prompt = f"""
        Research Task: Create a comprehensive technology research report
        
        Project Vision:
        {session.project_vision if session.project_vision else "No project vision document available."}
        
        Product Requirements Document (PRD):
        {session.prd_document if session.prd_document else "No PRD document available."}
        
        Selected Foundation Approach:
        {session.foundation_approach['name']}: {session.foundation_approach['description']}
        
        Generic Architecture:
        [First 1000 characters of the architecture document]
        {session.generic_architecture[:1000]}...
        
        Technology Requirements:
        [First 1000 characters of the requirements document]
        {session.technology_requirements[:1000]}...
        
        Technology Stack Evaluation Matrix:
        {matrix}
        
        Technology Stacks:
        {"".join(stacks_info)}
        
        Integration Patterns:
        {session.integration_patterns}
        
        Available Stack Reports:
        {", ".join([f"'{stack_name}'" for stack_name in session.stack_path_reports.keys()])}
        
        You are tasked with creating a DEFINITIVE TECHNOLOGY RESEARCH REPORT that aligns with the project vision and requirements:
        
        1. CREATE A COMPREHENSIVE TECHNOLOGY MAP:
           - Synthesize all research findings into a cohesive whole
           - Preserve the full richness of technology options and their emergent characteristics
           - Show relationships between technologies, components, and implementation approaches
           - Create visualizations that illuminate the multi-dimensional nature of technology choices
        
        2. DOCUMENT THE FULL TECHNOLOGY SPACE:
           - Present the complete spectrum of technology options discovered during research
           - Document multiple viable technology stacks with diverse characteristics
           - Map integration patterns and cross-technology opportunities
           - Preserve distinctly different approaches rather than converging on a "best" solution
        
        3. ILLUMINATE IMPLEMENTATION IMPLICATIONS:
           - Analyze how different technology choices create fundamentally different implementations
           - Document trade-offs inherent in different technology approaches
           - Show how technology choices give rise to different system characteristics
           - Highlight unique capabilities enabled by specific technology combinations
        
        4. CREATE POWERFUL VISUALIZATIONS:
           - Technology maps showing the spectrum of options for each component
           - Stack diagrams illustrating complete technology combinations
           - Integration maps showing communication patterns
           - Trade-off matrices comparing different technology approaches
        
        5. PRESERVE INNOVATION POTENTIAL:
           - Maintain the diversity of approaches without defaulting to conventions
           - Present findings without bias toward mainstream solutions
           - Preserve the project's unique characteristics across all options
           - Highlight unconventional approaches that align with the project's distinctive nature
        
        6. REFERENCE DETAILED STACK REPORTS:
           - Include a dedicated section that lists all available detailed stack reports
           - For each technology stack, reference its corresponding detailed report in the technology-research/stack-reports directory
           - Explain that architects can access complete implementation details through these reports
           - Note that the stack reports contain the full depth of research for each viable approach
           - Provide clear location information to help architects find the reports (session-id/technology-research/stack-reports/)
        
        7. INCLUDE TECHNOLOGY STACK EVALUATION:
           - BEGIN the report with the stack evaluation matrix you've been provided
           - Explain how stacks were evaluated against key project criteria
           - Highlight which stacks best align with the project's priorities
           - Note any stacks that add capabilities not explicitly requested in the original scope
        
        You have complete autonomy in how you approach this task. Use the available visualization
        tools in whatever way you determine will create the most illuminating representations.
        
        Your report should be the ULTIMATE TECHNOLOGY RESOURCE - a comprehensive map
        of the technology possibility space that enables informed choices without normalizing toward
        conventions. It should present the full spectrum of viable approaches with their
        implications, trade-offs, and unique characteristics, while ensuring architects can
        access the complete detailed research for options they find promising.
        """
        
        # Add the synthesis prompt to agent messages
        synthesis_agent.messages.append(create_user_prompt(report_prompt))
        
        # Get the agent's response
        response = await send_prompt(synthesis_agent.messages)
        
        # Add the response to the agent messages
        synthesis_agent.messages.append(create_assistant_prompt(response.content))
        
        # Update agent status
        synthesis_agent.status = "completed"
        
        # Update session with technology report
        session.technology_report = response.content
        
        # Save the report to file
        report_path = await self._save_technology_report(session_id, response.content)
        
        # Update session status
        if current_session and "technology_research" in current_session.metadata:
            current_session.metadata["technology_research"]["status"] = "completed"
            session_manager.update_session(session_id, current_session)
        
        logger.info(f"Technology report created for session {session_id}")
        return report_path
    
    @handle_async_errors
    async def _save_technology_report(self, session_id: str, content: str) -> str:
        """
        Save the technology report to file.
        
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
            document_type="technology-research-report",
            title="Technology Research Report",
            metadata=metadata
        )
        
        # Add the report to the session - use consistent kebab-case document type naming
        self.session_manager.add_document(session_id, "technology-research-report", report_path)
        
        logger.info(f"Technology report saved to {report_path}")
        return report_path
    
    @handle_async_errors
    async def conduct_technology_research(self, session_id: str) -> Optional[str]:
        """
        Conduct full technology research workflow.
        
        Args:
            session_id: Session ID
            
        Returns:
            Path to the final technology report
        """
        logger.info(f"Starting complete technology research workflow for session {session_id}")
        
        # Track workflow progress in session manager
        session_manager = SessionManager()
        current_session = session_manager.get_session(session_id)
        if current_session:
            if "technology_research" not in current_session.metadata:
                current_session.metadata["technology_research"] = {}
            
            current_session.metadata["technology_research"]["workflow_started"] = True
            current_session.metadata["technology_research"]["status"] = "in_progress"
            session_manager.update_session(session_id, current_session)
        
        # Step 1: Get all required documents
        # - Technology requirements (required)
        # - Generic architecture (required)
        # - Foundation approach (required)
        technology_requirements = await load_document_content(session_id, "technology-requirements")
        generic_architecture = await load_document_content(session_id, "architecture")
        
        # Get foundation selection from session metadata
        foundation_approach = None
        session_data = session_manager.get_session(session_id)
        if session_data and "architecture" in session_data.metadata and "selected_foundation" in session_data.metadata["architecture"]:
            foundation_approach = session_data.metadata["architecture"]["selected_foundation"]
        
        # Check if we have all required documents
        if not technology_requirements or not generic_architecture or not foundation_approach:
            logger.error(f"Missing required documents for technology research: " + 
                          f"Requirements: {bool(technology_requirements)}, " +
                          f"Architecture: {bool(generic_architecture)}, " +
                          f"Foundation: {bool(foundation_approach)}")
            
            # Update status in session manager
            if current_session and "technology_research" in current_session.metadata:
                current_session.metadata["technology_research"]["status"] = "failed"
                current_session.metadata["technology_research"]["error"] = "Missing required documents"
                session_manager.update_session(session_id, current_session)
            
            return None
        
        # Step 2: Create session
        session = await self.create_session(
            session_id, 
            technology_requirements, 
            generic_architecture, 
            foundation_approach
        )
        
        # Step 3: Initialize research agents
        if not session.agents:
            await self.initialize_research_agents(session_id)
            
            # Update phase status
            if current_session and "technology_research" in current_session.metadata:
                if "phases" not in current_session.metadata["technology_research"]:
                    current_session.metadata["technology_research"]["phases"] = {}
                
                current_session.metadata["technology_research"]["phases"]["agent_initialization"] = "completed"
                session_manager.update_session(session_id, current_session)
        
        # Step 4: Discover component technologies
        if not any(component.technology_options for component in session.component_technologies.values()):
            # Update phase status - starting
            if current_session and "technology_research" in current_session.metadata:
                current_session.metadata["technology_research"]["phases"]["technology_discovery"] = "in_progress"
                session_manager.update_session(session_id, current_session)
            
            await self.discover_component_technologies(session_id)
            
            # Update phase status - completed
            if current_session and "technology_research" in current_session.metadata:
                current_session.metadata["technology_research"]["phases"]["technology_discovery"] = "completed"
                session_manager.update_session(session_id, current_session)
        
        # Step 5: Explore technology options
        # This is selective exploration of key technologies
        if all(not tech.completed for component in session.component_technologies.values() for tech in component.technology_options.values()):
            # Update phase status - starting
            if current_session and "technology_research" in current_session.metadata:
                current_session.metadata["technology_research"]["phases"]["technology_exploration"] = "in_progress"
                session_manager.update_session(session_id, current_session)
            
            await self.explore_technology_options(session_id)
            
            # Update phase status - completed
            if current_session and "technology_research" in current_session.metadata:
                current_session.metadata["technology_research"]["phases"]["technology_exploration"] = "completed"
                session_manager.update_session(session_id, current_session)
        
        # Step 6: Generate technology stacks
        if not session.technology_stacks:
            await self.generate_technology_stacks(session_id)
        
        # Step 7: Conduct stack research
        if all(not stack.research_content for stack in session.technology_stacks):
            # Update phase status - starting
            if current_session and "technology_research" in current_session.metadata:
                current_session.metadata["technology_research"]["phases"]["stack_research"] = "in_progress"
                session_manager.update_session(session_id, current_session)
            
            await self.start_stack_research(session_id)
            
            # Update phase status - completed
            if current_session and "technology_research" in current_session.metadata:
                current_session.metadata["technology_research"]["phases"]["stack_research"] = "completed"
                session_manager.update_session(session_id, current_session)
        
        # Step 8: Conduct integration research
        if not session.integration_patterns:
            # Update phase status - starting
            if current_session and "technology_research" in current_session.metadata:
                current_session.metadata["technology_research"]["phases"]["integration_research"] = "in_progress"
                session_manager.update_session(session_id, current_session)
            
            await self.start_integration_research(session_id)
            
            # Update phase status - completed
            if current_session and "technology_research" in current_session.metadata:
                current_session.metadata["technology_research"]["phases"]["integration_research"] = "completed"
                session_manager.update_session(session_id, current_session)
        
        # Step 9: Create comprehensive technology report
        # Update phase status - starting
        if current_session and "technology_research" in current_session.metadata:
            current_session.metadata["technology_research"]["phases"]["research_synthesis"] = "in_progress"
            session_manager.update_session(session_id, current_session)
        
        report_path = await self.create_technology_report(session_id)
        
        # Update phase status - completed
        if current_session and "technology_research" in current_session.metadata:
            current_session.metadata["technology_research"]["phases"]["research_synthesis"] = "completed"
            current_session.metadata["technology_research"]["status"] = "completed"
            session_manager.update_session(session_id, current_session)
        
        logger.info(f"Completed technology research workflow for session {session_id}")
        return report_path
        
    @handle_async_errors
    async def revise_report(self, session_id: str, feedback: str) -> str:
        """
        Revise the technology report based on feedback.
        
        Args:
            session_id: Session ID
            feedback: Feedback to incorporate
            
        Returns:
            Revised report content
        """
        session = self.sessions.get(session_id)
        if not session or not session.technology_report:
            logger.error(f"No technology report to revise for session {session_id}")
            return "No technology report to revise"
        
        # Get a synthesis agent
        synthesis_agent = next(
            (a for a in session.agents if a.type == ResearchAgentType.SYNTHESIS),
            None
        )
        
        if not synthesis_agent:
            logger.error(f"No synthesis agent available for session {session_id}")
            return "No synthesis agent available"
        
        # Create revision prompt
        revision_prompt = f"""
        You are tasked with revising the technology research report based on the following feedback:
        
        Feedback:
        {feedback}
        
        Original Report:
        {session.technology_report}
        
        Revise the report to incorporate this feedback while maintaining the comprehensive nature
        of the report and continuing to present the full spectrum of technology options.
        Be particularly careful to preserve the innovation potential and not bias toward
        conventional approaches.
        
        Return the complete revised report.
        """
        
        # Create messages for the revision
        synthesis_agent.messages.append(create_user_prompt(revision_prompt))
        
        # Get the agent's response
        response = await send_prompt(synthesis_agent.messages)
        
        # Add the response to the agent messages
        synthesis_agent.messages.append(create_assistant_prompt(response.content))
        
        # Update the report
        session.technology_report = response.content
        
        # Save the revised report
        await self._save_technology_report(session_id, response.content)
        
        return response.content
        
    @handle_async_errors
    async def complete_session(self, session_id: str) -> None:
        """
        Complete a technology research session.
        
        Args:
            session_id: Session ID to complete
        """
        # Mark session as completed in session manager
        session_manager = SessionManager()
        current_session = session_manager.get_session(session_id)
        if current_session:
            if "technology_research" not in current_session.metadata:
                current_session.metadata["technology_research"] = {}
            
            current_session.metadata["technology_research"]["completed"] = True
            current_session.metadata["technology_research"]["status"] = "completed"
            session_manager.update_session(session_id, current_session)
        
        logger.info(f"Technology research session {session_id} marked as completed")