"""
Paradigm Agents for specialized research teams.

This module defines specialized paradigm agents that focus on specific
technological paradigms, from established approaches to experimental ones.
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional
import re

from ideasfactory.utils.error_handler import handle_errors, handle_async_errors
from ideasfactory.utils.file_manager import load_document_content
from ideasfactory.agents.research_agents.base_agent import BaseResearchAgent, AgentMessage


# Configure logging
logger = logging.getLogger(__name__)


class ParadigmAgent(BaseResearchAgent):
    """
    Base class for paradigm-specific research agents.
    
    This abstract class provides common functionality for paradigm agents
    while allowing specialized behaviors for each paradigm type.
    """
    
    def __init__(self, agent_id: str, coordinator: Any = None, repository: Any = None):
        """Initialize the paradigm agent."""
        super().__init__(agent_id, coordinator, repository)
        
        # Register message handlers
        self.register_message_handler("request_paradigm_analysis", self._handle_paradigm_analysis_request)
        self.register_message_handler("debate_contribution_request", self._handle_debate_contribution_request)
        
        # Agent state
        self.analyzed_dimensions: Dict[str, Dict[str, Any]] = {}
        self.session_id: Optional[str] = None
        self.vision_document: Optional[str] = None
        self.prd_document: Optional[str] = None
        self.research_requirements: Optional[str] = None
    
    @property
    def paradigm_name(self) -> str:
        """Get the paradigm name (to be implemented by subclasses)."""
        raise NotImplementedError("Subclasses must implement paradigm_name")
    
    @handle_async_errors
    async def initialize(self, session_id: str) -> bool:
        """Initialize the agent with session context.
        
        Args:
            session_id: Session ID to initialize with
            
        Returns:
            True if initialization successful
        """
        self.session_id = session_id
        
        # Load relevant documents
        try:
            # Load project vision
            self.vision_document = await load_document_content(session_id, "project-vision")
            
            # Load PRD
            self.prd_document = await load_document_content(session_id, "prd")
            
            # Load research requirements
            self.research_requirements = await load_document_content(session_id, "research-requirements")
            
            return bool(self.research_requirements)
        except Exception as e:
            logger.error(f"Error initializing paradigm agent: {str(e)}")
            return False
    
    @handle_async_errors
    async def process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a research task.
        
        Args:
            task_data: Task data including type and parameters
            
        Returns:
            Task results
        """
        task_type = task_data.get("task_type", "")
        
        if task_type == "analyze_dimension":
            dimension_name = task_data.get("dimension_name")
            if dimension_name:
                return await self._analyze_dimension(dimension_name)
            else:
                return {"error": "Missing dimension name"}
        elif task_type == "foundation_debate_contribution":
            dimension_name = task_data.get("dimension_name")
            debate_index = task_data.get("debate_index")
            
            if dimension_name and debate_index is not None:
                return await self._contribute_to_foundation_debate(dimension_name, debate_index)
            else:
                return {"error": "Missing dimension name or debate index"}
        else:
            return {"error": f"Unknown task type: {task_type}"}
    
    @handle_async_errors
    async def _analyze_dimension(self, dimension_name: str) -> Dict[str, Any]:
        """Analyze a dimension from this agent's paradigm perspective.
        
        Args:
            dimension_name: Name of dimension to analyze
            
        Returns:
            Analysis results
        """
        logger.info(f"Agent {self.agent_id} analyzing dimension {dimension_name} from {self.paradigm_name} perspective")
        
        if not self.repository:
            return {"error": "No repository available"}
        
        # Get the dimension
        dimension = self.repository.get_dimension(dimension_name)
        if not dimension:
            return {"error": f"Dimension {dimension_name} not found"}
        
        # Prepare context for analysis
        context = {
            "Project Vision": self.vision_document or "Not available",
            "PRD": self.prd_document or "Not available",
            "Research Requirements": self.research_requirements,
            "Dimension": f"{dimension.name}: {dimension.description}",
            "Research Areas": "\n".join([f"- {area.get('name')}: {area.get('description')}" 
                                       for area in dimension.research_areas]),
            "Dependencies": ", ".join(dimension.dependencies) if dimension.dependencies else "None"
        }
        
        # Create prompt for paradigm-specific analysis
        prompt = f"""
        Analyze the dimension "{dimension.name}" from a {self.paradigm_name} perspective.

        Focus on:
        1. Identifying {self.paradigm_name} approaches that address this dimension
        2. Evaluating their applicability to this specific project
        3. Highlighting strengths and limitations of {self.paradigm_name} solutions
        4. Noting integration considerations with other dimensions
        5. Providing specific technology recommendations within this paradigm

        Be specific about actual technologies, frameworks, or methodologies within the {self.paradigm_name}
        paradigm that would be appropriate for this dimension.
        """
        
        # Generate analysis
        analysis_text = await self.generate_content(prompt, context)
        
        # Parse the analysis to extract technologies
        technologies = self._extract_technologies_from_analysis(analysis_text)
        
        # Store for later use
        if dimension_name not in self.analyzed_dimensions:
            self.analyzed_dimensions[dimension_name] = {}
        
        self.analyzed_dimensions[dimension_name]["technologies"] = technologies
        self.analyzed_dimensions[dimension_name]["analysis"] = analysis_text
        
        # Add findings to repository
        await self.repository.add_agent_finding(
            dimension_name, 
            self.agent_id, 
            {
                "paradigm": self.paradigm_name,
                "technologies": technologies,
                "analysis": analysis_text
            }
        )
        
        return {
            "dimension": dimension_name,
            "paradigm": self.paradigm_name,
            "technologies": technologies,
            "analysis": analysis_text
        }
    
    def _extract_technologies_from_analysis(self, analysis: str) -> List[Dict[str, Any]]:
        """Extract structured technology data from analysis text.
        
        Args:
            analysis: Analysis text
            
        Returns:
            List of technologies
        """
        technologies = []
        
        # Look for technology headers
        tech_matches = re.finditer(r'#+\s*(Technology|Framework|Approach|Solution)[:]*\s*(.*?)\n', analysis)
        
        for match in tech_matches:
            tech_name = match.group(2).strip()
            start_pos = match.end()
            
            # Find the next technology header or end of text
            next_match = re.search(r'#+\s*(Technology|Framework|Approach|Solution)[:]*\s*', analysis[start_pos:])
            if next_match:
                end_pos = start_pos + next_match.start()
                tech_text = analysis[start_pos:end_pos]
            else:
                tech_text = analysis[start_pos:]
            
            # Extract details
            description = self._extract_description(tech_text)
            strengths = self._extract_list_items(tech_text, r'Strengths[:]*\s*\n')
            limitations = self._extract_list_items(tech_text, r'Limitations[:]*\s*\n')
            integration = self._extract_list_items(tech_text, r'Integration[:]*\s*\n')
            
            technologies.append({
                "name": tech_name,
                "description": description,
                "strengths": strengths,
                "limitations": limitations,
                "integration_points": integration,
                "paradigm": self.paradigm_name
            })
        
        return technologies
    
    def _extract_description(self, text: str) -> str:
        """Extract technology description from text.
        
        Args:
            text: Technology text
            
        Returns:
            Description
        """
        # Look for first paragraph after header
        match = re.search(r'\n\n(.*?)\n\n', text)
        if match:
            return match.group(1).strip()
        else:
            # Take first 200 characters as fallback
            return text[:200].strip()
    
    def _extract_list_items(self, text: str, header_pattern: str) -> List[str]:
        """Extract list items following a header.
        
        Args:
            text: Text to search
            header_pattern: Regex pattern for the header
            
        Returns:
            List of items
        """
        items = []
        
        # Find the header
        header_match = re.search(header_pattern, text)
        if not header_match:
            return items
        
        start_pos = header_match.end()
        
        # Find the next header or end of text
        next_header = re.search(r'#+\s*\w+', text[start_pos:])
        if next_header:
            list_text = text[start_pos:start_pos + next_header.start()]
        else:
            list_text = text[start_pos:]
        
        # Extract list items
        item_matches = re.finditer(r'[-*]\s*(.*?)(?:\n|$)', list_text)
        for match in item_matches:
            items.append(match.group(1).strip())
        
        return items
    
    @handle_async_errors
    async def _contribute_to_foundation_debate(self, dimension_name: str, debate_index: int) -> Dict[str, Any]:
        """Contribute to a foundation debate from this paradigm's perspective.
        
        Args:
            dimension_name: Name of dimension being debated
            debate_index: Index of debate in repository
            
        Returns:
            Contribution results
        """
        logger.info(f"Agent {self.agent_id} contributing to debate on {dimension_name} from {self.paradigm_name} perspective")
        
        if not self.repository:
            return {"error": "No repository available"}
        
        # Get the dimension
        dimension = self.repository.get_dimension(dimension_name)
        if not dimension:
            return {"error": f"Dimension {dimension_name} not found"}
        
        # Get the debate
        if debate_index < 0 or debate_index >= len(self.repository.debates):
            return {"error": f"Debate index {debate_index} out of range"}
        
        debate = self.repository.debates[debate_index]
        
        # Prepare context for contribution
        dimension_context = {
            "Dimension": f"{dimension.name}: {dimension.description}",
            "Research Areas": "\n".join([f"- {area.get('name')}: {area.get('description')}" 
                                       for area in dimension.research_areas]),
            "Dependencies": ", ".join(dimension.dependencies) if dimension.dependencies else "None",
            "Foundation Impact": dimension.foundation_impact
        }
        
        # Add existing contributions for context
        contributions_context = ""
        for contrib in debate.contributions:
            contributions_context += f"{contrib.agent_id} ({contrib.agent_type}):\n{contrib.content}\n\n"
        
        if contributions_context:
            dimension_context["Existing Contributions"] = contributions_context
        
        # Create prompt for debate contribution
        prompt = f"""
        You are participating in a debate about foundation choices for the dimension: {dimension.name}

        As a specialist in {self.paradigm_name} approaches, your task is to advocate for consideration of
        {self.paradigm_name} solutions by:
        
        1. Proposing specific {self.paradigm_name} technologies or approaches that could serve as foundation choices
        2. Highlighting the unique strengths of these choices from a {self.paradigm_name} perspective
        3. Acknowledging limitations honestly and suggesting mitigations
        4. Explaining how these {self.paradigm_name} choices would impact dependent dimensions

        Provide a structured contribution that adds the {self.paradigm_name} perspective to this debate,
        ensuring decision-makers consider the full spectrum of options.
        """
        
        # Generate contribution
        contribution = await self.generate_content(prompt, dimension_context)
        
        # Add to debate
        await self.repository.add_debate_contribution(
            debate_index=debate_index,
            agent_id=self.agent_id,
            agent_type=self.agent_type,
            content=contribution
        )
        
        return {
            "dimension": dimension_name,
            "debate_index": debate_index,
            "paradigm": self.paradigm_name,
            "contribution": contribution
        }
    
    @handle_async_errors
    async def _handle_paradigm_analysis_request(self, message: AgentMessage) -> None:
        """Handle a request for paradigm-specific analysis.
        
        Args:
            message: Request message
        """
        logger.info(f"Agent {self.agent_id} handling paradigm analysis request")
        
        # Extract dimension name
        dimension_name = message.content.get("dimension_name")
        if not dimension_name:
            logger.error("Missing dimension name in request")
            return
        
        # Process the analysis
        analysis_results = await self._analyze_dimension(dimension_name)
        
        # Send response
        await self.send_message(
            recipient_id=message.sender_id,
            message_type="paradigm_analysis_response",
            content=analysis_results,
            reply_to=message.id
        )
    
    @handle_async_errors
    async def _handle_debate_contribution_request(self, message: AgentMessage) -> None:
        """Handle a request to contribute to a debate.
        
        Args:
            message: Request message
        """
        logger.info(f"Agent {self.agent_id} handling debate contribution request")
        
        # Extract parameters
        dimension_name = message.content.get("dimension_name")
        debate_index = message.content.get("debate_index")
        
        if not dimension_name or debate_index is None:
            logger.error("Missing dimension name or debate index in request")
            return
        
        # Contribute to debate
        contribution_results = await self._contribute_to_foundation_debate(
            dimension_name=dimension_name,
            debate_index=debate_index
        )
        
        # Send response
        await self.send_message(
            recipient_id=message.sender_id,
            message_type="debate_contribution_response",
            content=contribution_results,
            reply_to=message.id
        )


class EstablishedParadigmAgent(ParadigmAgent):
    """
    Established Paradigm Agent specializing in traditional, proven methodologies.
    
    This agent focuses on established approaches with long track records.
    """
    
    @property
    def agent_type(self) -> str:
        """Get the type of this agent."""
        return "established"
    
    @property
    def paradigm_name(self) -> str:
        """Get the paradigm name."""
        return "established approaches"
    
    @property
    def system_prompt(self) -> str:
        """Get the system prompt for this agent."""
        return """
        You are an Established Approaches Expert specializing in traditional, proven methodologies with
        long track records. Your role is to identify reliable solutions with strong industry adoption.

        Focus on:
        1. Mature technologies with proven stability and reliability
        2. Well-documented approaches with extensive community support
        3. Solutions with predictable performance characteristics
        4. Approaches with clear operational patterns and known limitations
        5. Technologies that have stood the test of time

        Avoid:
        1. Experimental or bleeding-edge technologies
        2. Solutions without significant production history
        3. Approaches with limited community support
        4. Overly complex methodologies with uncertain outcomes

        As you evaluate established options, be thorough and practical, emphasizing stability and reliability
        while acknowledging where newer approaches might offer advantages.
        """


class MainstreamParadigmAgent(ParadigmAgent):
    """
    Mainstream Paradigm Agent specializing in contemporary popular solutions.
    
    This agent focuses on current mainstream technologies with strong adoption.
    """
    
    @property
    def agent_type(self) -> str:
        """Get the type of this agent."""
        return "mainstream"
    
    @property
    def paradigm_name(self) -> str:
        """Get the paradigm name."""
        return "mainstream current"
    
    @property
    def system_prompt(self) -> str:
        """Get the system prompt for this agent."""
        return """
        You are a Mainstream Technologies Expert specializing in contemporary popular solutions with
        strong industry adoption. Your role is to identify current best practices and technologies.

        Focus on:
        1. Technologies with strong current industry adoption
        2. Approaches that represent current best practices
        3. Solutions with robust ecosystems and active development
        4. Technologies with good hiring pools and talent availability
        5. Approaches that balance innovation and stability

        Avoid:
        1. Legacy technologies in decline
        2. Extremely cutting-edge or unproven technologies
        3. Overemphasizing or dismissing innovation based on popularity alone
        4. Recommending approaches solely based on trends without substantive evaluation

        As you evaluate mainstream options, be balanced and practical, considering both technical merit
        and market adoption while providing specific technology recommendations.
        """


class CuttingEdgeParadigmAgent(ParadigmAgent):
    """
    Cutting-Edge Paradigm Agent specializing in emerging technologies gaining traction.
    
    This agent focuses on newer approaches that are showing promise and adoption.
    """
    
    @property
    def agent_type(self) -> str:
        """Get the type of this agent."""
        return "cutting_edge"
    
    @property
    def paradigm_name(self) -> str:
        """Get the paradigm name."""
        return "cutting-edge"
    
    @property
    def system_prompt(self) -> str:
        """Get the system prompt for this agent."""
        return """
        You are a Cutting-Edge Technologies Expert specializing in emerging technologies gaining traction
        in the industry. Your role is to identify promising new approaches that could provide significant advantages.

        Focus on:
        1. Technologies that have recently moved beyond experimental stage
        2. Approaches gaining momentum in industry adoption
        3. Solutions that offer step-change improvements over mainstream options
        4. Technologies with growing communities and support
        5. Emerging patterns that address known limitations of established approaches

        Avoid:
        1. Purely experimental technologies without proven implementation
        2. Overestimating maturity of emerging approaches
        3. Ignoring integration challenges with existing systems
        4. Recommending cutting-edge solutions when they don't align with project needs

        As you evaluate cutting-edge options, be forward-thinking but grounded, identifying opportunities
        where newer approaches offer genuine advantages while being pragmatic about implementation considerations.
        """


class ExperimentalParadigmAgent(ParadigmAgent):
    """
    Experimental Paradigm Agent specializing in research-stage technologies.
    
    This agent focuses on emerging approaches that are still in early stages.
    """
    
    @property
    def agent_type(self) -> str:
        """Get the type of this agent."""
        return "experimental"
    
    @property
    def paradigm_name(self) -> str:
        """Get the paradigm name."""
        return "experimental"
    
    @property
    def system_prompt(self) -> str:
        """Get the system prompt for this agent."""
        return """
        You are an Experimental Technologies Expert specializing in research-stage approaches and
        emerging paradigms. Your role is to identify innovative ideas that could transform how problems are solved.

        Focus on:
        1. Technologies emerging from research that show transformative potential
        2. Novel approaches that challenge fundamental assumptions
        3. Ideas with early proof-of-concept demonstrations
        4. Approaches that may become mainstream in 2-5 years
        5. Solutions targeting unsolved problems or limitations in existing paradigms

        Avoid:
        1. Presenting experimental technologies as production-ready
        2. Ignoring the risks and limitations of unproven approaches
        3. Suggesting adoption without clear strategic advantage
        4. Overlooking the path from experimental to practical implementation

        As you evaluate experimental options, be visionary yet honest about maturity, identifying where
        bleeding-edge approaches might solve problems in fundamentally new ways while being clear about
        implementation challenges.
        """


class CrossParadigmAgent(ParadigmAgent):
    """
    Cross-Paradigm Agent specializing in combinations of technologies from different domains.
    
    This agent focuses on hybrid approaches that combine different paradigms.
    """
    
    @property
    def agent_type(self) -> str:
        """Get the type of this agent."""
        return "cross_paradigm"
    
    @property
    def paradigm_name(self) -> str:
        """Get the paradigm name."""
        return "cross-paradigm"
    
    @property
    def system_prompt(self) -> str:
        """Get the system prompt for this agent."""
        return """
        You are a Cross-Paradigm Integration Expert specializing in combining technologies from different
        domains into hybrid solutions. Your role is to identify opportunities where integration across
        paradigms creates superior results.

        Focus on:
        1. Identifying complementary strengths across different paradigms
        2. Finding solutions where technologies from different domains address each other's limitations
        3. Creating integration patterns that preserve the advantages of each technology
        4. Exploring hybrid approaches that overcome traditional trade-offs
        5. Designing system boundaries and interfaces between paradigms

        Avoid:
        1. Forcing incompatible technologies together
        2. Creating unnecessarily complex solutions when simpler approaches suffice
        3. Ignoring integration challenges and compatibility issues
        4. Overlooking maintenance complexity in hybrid solutions

        As you evaluate cross-paradigm opportunities, be creative yet practical, identifying novel
        combinations that solve problems in ways single-paradigm approaches cannot, while providing
        clear integration strategies.
        """


class FirstPrinciplesAgent(ParadigmAgent):
    """
    First-Principles Agent specializing in custom approaches designed for specific projects.
    
    This agent focuses on ground-up solutions tailored to unique requirements.
    """
    
    @property
    def agent_type(self) -> str:
        """Get the type of this agent."""
        return "first_principles"
    
    @property
    def paradigm_name(self) -> str:
        """Get the paradigm name."""
        return "first-principles"
    
    @property
    def system_prompt(self) -> str:
        """Get the system prompt for this agent."""
        return """
        You are a First-Principles Design Expert specializing in custom approaches designed specifically
        for unique project requirements. Your role is to rethink problems from fundamental needs rather
        than applying existing patterns.

        Focus on:
        1. Breaking down problems to their essential requirements
        2. Designing solutions specifically tailored to project uniqueness
        3. Questioning assumed constraints and conventional approaches
        4. Creating purpose-built approaches that prioritize project-specific goals
        5. Exploring novel combinations and custom designs

        Avoid:
        1. Reinventing solutions that existing technologies already solve well
        2. Creating unnecessary complexity through over-customization
        3. Ignoring lessons and patterns from established approaches
        4. Designing systems that are difficult to maintain or evolve

        As you develop first-principles solutions, be innovative yet pragmatic, designing approaches that
        truly align with the project's unique characteristics while considering practical implementation concerns.
        """