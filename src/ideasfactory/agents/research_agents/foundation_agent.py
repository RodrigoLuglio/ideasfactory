"""
Foundation Agent for specialized research teams.

This module defines the FoundationAgent class responsible for
analyzing foundation dimensions and their implications.
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


class FoundationAgent(BaseResearchAgent):
    """
    Foundation Research Agent specializing in foundational architectural decisions.
    
    This agent focuses on identifying high-impact foundation dimensions and exploring
    their implications for the entire system architecture.
    """
    
    @property
    def agent_type(self) -> str:
        """Get the type of this agent."""
        return "foundation"
    
    @property
    def system_prompt(self) -> str:
        """Get the system prompt for this agent."""
        return """
        You are a Foundation Research Agent specializing in systems thinking and architectural fundamentals. 
        Your role is to identify foundation dimensions that impact all other aspects of the system and 
        explore options across multiple paradigms.

        Focus on:
        1. Identifying dimensions with highest impact across the system
        2. Mapping interdependencies between dimensions
        3. Understanding how foundation choices create different paths
        4. Evaluating options objectively across multiple paradigms
        5. Considering long-term implications of foundation choices

        Avoid:
        1. Defaulting to conventional solutions without thorough analysis
        2. Making assumptions about specific technologies
        3. Limiting exploration to familiar paradigms
        4. Ignoring the unique characteristics of this specific project

        As you analyze foundation dimensions, be comprehensive, thoughtful, and aim to create a solid
        foundation that enables innovative implementation paths while maintaining architectural integrity.
        """
    
    def __init__(self, agent_id: str, coordinator: Any = None, repository: Any = None):
        """Initialize the foundation agent."""
        super().__init__(agent_id, coordinator, repository)
        
        # Register message handlers
        self.register_message_handler("request_foundation_analysis", self._handle_foundation_analysis_request)
        self.register_message_handler("debate_contribution_request", self._handle_debate_contribution_request)
        
        # Agent state
        self.analyzed_dimensions: Dict[str, Dict[str, Any]] = {}
        self.session_id: Optional[str] = None
        self.vision_document: Optional[str] = None
        self.prd_document: Optional[str] = None
        self.research_requirements: Optional[str] = None
    
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
            logger.error(f"Error initializing foundation agent: {str(e)}")
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
        
        if task_type == "analyze_foundation_dimensions":
            return await self._analyze_foundation_dimensions()
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
    async def _analyze_foundation_dimensions(self) -> Dict[str, Any]:
        """Analyze foundation dimensions and their implications.
        
        Returns:
            Analysis results
        """
        logger.info(f"Agent {self.agent_id} analyzing foundation dimensions")
        
        if not self.research_requirements:
            return {"error": "No research requirements available"}
        
        # Prepare context for analysis
        context = {
            "Project Vision": self.vision_document or "Not available",
            "PRD": self.prd_document or "Not available",
            "Research Requirements": self.research_requirements
        }
        
        # Create prompt for foundation dimension analysis
        prompt = """
        Analyze the research requirements document to identify foundation dimensions that impact all other aspects of the system.

        For each foundation dimension (those with no dependencies or with high system-wide impact):
        1. Identify its key characteristics and importance
        2. Map potential implications for dependent dimensions
        3. Explore at least 3 different approaches across paradigms
        4. Evaluate each approach objectively, noting strengths and limitations
        5. Identify which approaches open different implementation paths

        Provide your analysis in a structured format that clearly identifies each foundation dimension
        and presents a balanced exploration across paradigms.
        """
        
        # Generate analysis
        analysis_text = await self.generate_content(prompt, context)
        
        # Parse the analysis to extract foundation dimensions
        dimensions = self._extract_dimensions_from_analysis(analysis_text)
        
        # Store for later use
        self.analyzed_dimensions = dimensions
        
        # Add findings to repository
        for name, details in dimensions.items():
            if self.repository:
                dimension = self.repository.get_dimension(name)
                if dimension:
                    await self.repository.add_agent_finding(name, self.agent_id, details)
        
        return {
            "dimensions": dimensions,
            "analysis": analysis_text
        }
    
    def _extract_dimensions_from_analysis(self, analysis: str) -> Dict[str, Dict[str, Any]]:
        """Extract structured dimension data from analysis text.
        
        Args:
            analysis: Analysis text
            
        Returns:
            Dictionary mapping dimension names to details
        """
        dimensions = {}
        
        # Simple regex-based extraction (would be more sophisticated in production)
        # Look for headers that indicate dimensions
        dimension_matches = re.finditer(r'#+\s*(Foundation Dimension|Dimension)[:]*\s*(.*?)\n', analysis)
        
        for match in dimension_matches:
            dimension_name = match.group(2).strip()
            start_pos = match.end()
            
            # Find the next dimension header or end of text
            next_match = re.search(r'#+\s*(Foundation Dimension|Dimension)[:]*\s*', analysis[start_pos:])
            if next_match:
                end_pos = start_pos + next_match.start()
                dimension_text = analysis[start_pos:end_pos]
            else:
                dimension_text = analysis[start_pos:]
            
            # Extract details
            details = {
                "description": self._extract_description(dimension_text),
                "approaches": self._extract_approaches(dimension_text),
                "implications": self._extract_implications(dimension_text)
            }
            
            dimensions[dimension_name] = details
        
        return dimensions
    
    def _extract_description(self, text: str) -> str:
        """Extract dimension description from text.
        
        Args:
            text: Dimension text
            
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
    
    def _extract_approaches(self, text: str) -> List[Dict[str, Any]]:
        """Extract approaches from dimension text.
        
        Args:
            text: Dimension text
            
        Returns:
            List of approaches
        """
        approaches = []
        
        # Look for approaches across paradigms
        approach_matches = re.finditer(r'#+\s*(Approach|Option)[:]*\s*(.*?)\n', text)
        
        for match in approach_matches:
            approach_name = match.group(2).strip()
            start_pos = match.end()
            
            # Find the next approach header or end of section
            next_match = re.search(r'#+\s*(Approach|Option)[:]*\s*', text[start_pos:])
            if next_match:
                end_pos = start_pos + next_match.start()
                approach_text = text[start_pos:end_pos]
            else:
                # Find next major section
                next_section = re.search(r'#+\s*(Implications|Strengths|Limitations)', text[start_pos:])
                if next_section:
                    end_pos = start_pos + next_section.start()
                    approach_text = text[start_pos:end_pos]
                else:
                    approach_text = text[start_pos:]
            
            # Extract strengths and limitations
            strengths = self._extract_list_items(approach_text, r'Strengths[:]*\s*\n')
            limitations = self._extract_list_items(approach_text, r'Limitations[:]*\s*\n')
            
            # Extract paradigm if mentioned
            paradigm = "unknown"
            paradigm_match = re.search(r'(established|mainstream|cutting[ -]edge|experimental|cross[ -]paradigm|first[ -]principles)', 
                                     approach_text.lower())
            if paradigm_match:
                paradigm = paradigm_match.group(1).replace(" ", "_")
            
            approaches.append({
                "name": approach_name,
                "description": self._extract_description(approach_text),
                "strengths": strengths,
                "limitations": limitations,
                "paradigm": paradigm
            })
        
        return approaches
    
    def _extract_implications(self, text: str) -> List[str]:
        """Extract implications from dimension text.
        
        Args:
            text: Dimension text
            
        Returns:
            List of implications
        """
        return self._extract_list_items(text, r'Implications[:]*\s*\n')
    
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
        """Contribute to a foundation debate.
        
        Args:
            dimension_name: Name of dimension being debated
            debate_index: Index of debate in repository
            
        Returns:
            Contribution results
        """
        logger.info(f"Agent {self.agent_id} contributing to debate on {dimension_name}")
        
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

        Your task is to contribute meaningfully to this debate by:
        1. Proposing specific foundation choices that should be considered
        2. Evaluating the strengths and limitations of each choice
        3. Analyzing how each choice would impact dependent dimensions
        4. Considering the long-term implications of different choices

        Provide a structured, thoughtful contribution that helps move toward consensus on the best
        foundation choices for this dimension.
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
            "contribution": contribution
        }
    
    @handle_async_errors
    async def _handle_foundation_analysis_request(self, message: AgentMessage) -> None:
        """Handle a request for foundation dimension analysis.
        
        Args:
            message: Request message
        """
        logger.info(f"Agent {self.agent_id} handling foundation analysis request")
        
        # Process the analysis
        analysis_results = await self._analyze_foundation_dimensions()
        
        # Send response
        await self.send_message(
            recipient_id=message.sender_id,
            message_type="foundation_analysis_response",
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