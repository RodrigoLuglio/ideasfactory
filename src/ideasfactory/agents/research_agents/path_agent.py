"""
Path Exploration Agent for specialized research teams.

This module defines the PathExplorationAgent class responsible for
exploring specific research paths based on foundation choices.
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


class PathExplorationAgent(BaseResearchAgent):
    """
    Path Exploration Agent specializing in evaluating complete technology stacks.
    
    This agent explores comprehensive paths across dimensions based on foundation choices.
    """
    
    @property
    def agent_type(self) -> str:
        """Get the type of this agent."""
        return "path"
    
    @property
    def system_prompt(self) -> str:
        """Get the system prompt for this agent."""
        return """
        You are a Path Exploration Agent specializing in evaluating complete technology stacks across dimensions.
        Your role is to ensure technological coherence within implementation paths.

        Focus on:
        1. Following a specific foundation choice through all dependent dimensions
        2. Ensuring compatibility between technologies across dimensions
        3. Identifying trade-offs in each implementation path
        4. Documenting coherent, complete implementation approaches
        5. Evaluating the path against project requirements

        Avoid:
        1. Mixing incompatible technologies within a path
        2. Ignoring dependencies between dimensions
        3. Over-optimizing for one dimension at the expense of others
        4. Losing sight of the project's unique vision

        As you explore your assigned path, be thorough, detail-oriented, and practical, ensuring all
        recommendations work together as a coherent whole while preserving the project's innovative characteristics.
        """
    
    def __init__(self, agent_id: str, coordinator: Any = None, repository: Any = None):
        """Initialize the path exploration agent."""
        super().__init__(agent_id, coordinator, repository)
        
        # Register message handlers
        self.register_message_handler("request_path_exploration", self._handle_path_exploration_request)
        
        # Agent state
        self.assigned_paths: List[int] = []  # Indices of assigned paths
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
            logger.error(f"Error initializing path exploration agent: {str(e)}")
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
        
        if task_type == "explore_research_path":
            path_index = task_data.get("path_index")
            if path_index is not None:
                return await self._explore_research_path(path_index)
            else:
                return {"error": "Missing path index"}
        else:
            return {"error": f"Unknown task type: {task_type}"}
    
    @handle_async_errors
    async def _explore_research_path(self, path_index: int) -> Dict[str, Any]:
        """Explore a research path across all dimensions.
        
        Args:
            path_index: Index of path to explore
            
        Returns:
            Exploration results
        """
        logger.info(f"Agent {self.agent_id} exploring research path {path_index}")
        
        if not self.repository:
            return {"error": "No repository available"}
        
        # Get the path
        if path_index < 0 or path_index >= len(self.repository.research_paths):
            return {"error": f"Path index {path_index} out of range"}
        
        path = self.repository.research_paths[path_index]
        
        # Add to assigned paths
        if path_index not in self.assigned_paths:
            self.assigned_paths.append(path_index)
        
        # Get all dimensions
        dimensions = list(self.repository.dimensions.values())
        
        # Sort dimensions by dependencies (foundation dimensions first)
        dimensions.sort(key=lambda d: len(d.dependencies))
        
        # Prepare context for exploration
        context = {
            "Project Vision": self.vision_document or "Not available",
            "PRD": self.prd_document or "Not available",
            "Research Requirements": self.research_requirements,
            "Path Name": path.name,
            "Path Description": path.description,
            "Foundation Choices": "\n".join([f"- {dim}: {choice}" 
                                            for dim, choice in path.foundation_choices.items()])
        }
        
        # Add dimension descriptions
        dimension_descriptions = []
        for dimension in dimensions:
            deps = ", ".join(dimension.dependencies) if dimension.dependencies else "None"
            dimension_descriptions.append(f"{dimension.name}: {dimension.description} (Dependencies: {deps})")
        
        context["Dimensions"] = "\n\n".join(dimension_descriptions)
        
        # Create prompt for path exploration
        prompt = f"""
        Explore the research path named "{path.name}" across all dimensions based on the foundation choices:
        {", ".join([f"{dim}: {choice}" for dim, choice in path.foundation_choices.items()])}

        For each dimension in dependency order:
        1. Determine technology choices compatible with the foundation choices
        2. Ensure coherent integration across the path
        3. Identify trade-offs inherent in this path
        4. Evaluate how each choice affects downstream dimensions

        Analyze how this path addresses the project's unique requirements and provide a comprehensive
        overview of the complete technology stack with a focus on coherence and integration.
        """
        
        # Generate exploration analysis
        exploration_text = await self.generate_content(prompt, context)
        
        # Parse the exploration to extract technologies and trade-offs
        path_technologies = []
        path_dimensions = []
        path_trade_offs = []
        
        # Extract technologies for each dimension
        for dimension in dimensions:
            # Extract technologies for this dimension within the path
            dimension_techs = self._extract_dimension_technologies(exploration_text, dimension.name)
            
            # Add to path dimensions
            if dimension_techs:
                path_dimensions.append({
                    "name": dimension.name,
                    "description": dimension.description,
                    "technologies": dimension_techs
                })
                
                # Add all technologies to the main list
                path_technologies.extend(dimension_techs)
        
        # Extract trade-offs
        path_trade_offs = self._extract_trade_offs(exploration_text)
        
        # Extract characteristics
        path_characteristics = self._extract_characteristics(exploration_text)
        
        # Update the path in the repository
        path_updates = {
            "dimensions": path_dimensions,
            "technologies": path_technologies,
            "trade_offs": path_trade_offs,
            "characteristics": path_characteristics,
            "explored_by": self.agent_id
        }
        
        await self.repository.update_research_path(path_index, path_updates)
        
        return {
            "path_index": path_index,
            "path_name": path.name,
            "dimensions": path_dimensions,
            "technologies": path_technologies,
            "trade_offs": path_trade_offs,
            "characteristics": path_characteristics,
            "exploration": exploration_text
        }
    
    def _extract_dimension_technologies(self, exploration: str, dimension_name: str) -> List[Dict[str, Any]]:
        """Extract technologies for a dimension from exploration text.
        
        Args:
            exploration: Exploration text
            dimension_name: Name of dimension
            
        Returns:
            List of technologies
        """
        technologies = []
        
        # Find the dimension section
        dimension_pattern = rf'#+\s*{re.escape(dimension_name)}(?:\s*Dimension)?[:]*\s*\n'
        dimension_match = re.search(dimension_pattern, exploration)
        
        if not dimension_match:
            return technologies
        
        start_pos = dimension_match.end()
        
        # Find the next dimension section or end of text
        next_dimension = re.search(r'#+\s*([A-Za-z0-9_ ]+?)(?:\s*Dimension)?[:]*\s*\n', exploration[start_pos:])
        if next_dimension:
            end_pos = start_pos + next_dimension.start()
            dimension_text = exploration[start_pos:end_pos]
        else:
            dimension_text = exploration[start_pos:]
        
        # Look for technology mentions
        tech_matches = re.finditer(r'(?:Technology|Framework|Tool|Approach)[:]*\s*([A-Za-z0-9_. -]+)', dimension_text)
        
        for match in tech_matches:
            tech_name = match.group(1).strip()
            
            # Extract surrounding paragraph for description
            context_start = max(0, match.start() - 200)
            context_end = min(len(dimension_text), match.end() + 200)
            context_text = dimension_text[context_start:context_end]
            
            # Extract description
            description = self._extract_paragraph_containing(context_text, tech_name)
            
            # Extract strengths and limitations if mentioned
            strengths = []
            strengths_match = re.search(r'Strengths?[:\s]+(.*?)(?:\n\n|\n#|\n\*\*)', context_text, re.DOTALL)
            if strengths_match:
                strengths_text = strengths_match.group(1)
                strengths = [s.strip() for s in re.findall(r'[-*]\s*(.*?)(?:\n|$)', strengths_text)]
            
            limitations = []
            limitations_match = re.search(r'Limitations?[:\s]+(.*?)(?:\n\n|\n#|\n\*\*)', context_text, re.DOTALL)
            if limitations_match:
                limitations_text = limitations_match.group(1)
                limitations = [l.strip() for l in re.findall(r'[-*]\s*(.*?)(?:\n|$)', limitations_text)]
            
            technologies.append({
                "name": tech_name,
                "description": description,
                "strengths": strengths,
                "limitations": limitations,
                "dimension": dimension_name
            })
        
        return technologies
    
    def _extract_paragraph_containing(self, text: str, keyword: str) -> str:
        """Extract a paragraph containing a keyword.
        
        Args:
            text: Text to search
            keyword: Keyword to find
            
        Returns:
            Paragraph containing the keyword
        """
        # Find the position of the keyword
        keyword_match = re.search(re.escape(keyword), text)
        if not keyword_match:
            return ""
        
        # Find paragraph boundaries
        para_start = text.rfind("\n\n", 0, keyword_match.start())
        if para_start == -1:
            para_start = 0
        else:
            para_start += 2  # Skip the newlines
        
        para_end = text.find("\n\n", keyword_match.end())
        if para_end == -1:
            para_end = len(text)
        
        return text[para_start:para_end].strip()
    
    def _extract_trade_offs(self, exploration: str) -> List[Dict[str, Any]]:
        """Extract trade-offs from exploration text.
        
        Args:
            exploration: Exploration text
            
        Returns:
            List of trade-offs
        """
        trade_offs = []
        
        # Find the trade-offs section
        section_match = re.search(r'#+\s*Trade-?offs[:]*\s*\n', exploration)
        if not section_match:
            return trade_offs
        
        start_pos = section_match.end()
        
        # Find the next section or end of text
        next_section = re.search(r'#+\s*', exploration[start_pos:])
        if next_section:
            end_pos = start_pos + next_section.start()
            section_text = exploration[start_pos:end_pos]
        else:
            section_text = exploration[start_pos:]
        
        # Extract trade-off items
        item_matches = re.finditer(r'[-*]\s*(.*?)(?:\n|$)', section_text)
        
        for match in item_matches:
            trade_off_text = match.group(1).strip()
            
            # Try to extract benefit and cost
            parts = trade_off_text.split(" vs. ")
            if len(parts) == 2:
                benefit, cost = parts
                description = f"{benefit} versus {cost}"
            else:
                description = trade_off_text
                benefit = ""
                cost = ""
                
                # Try to extract from other formats
                benefit_match = re.search(r'benefit[:]*\s*(.*?)(?:\.|;|$)', trade_off_text, re.IGNORECASE)
                if benefit_match:
                    benefit = benefit_match.group(1).strip()
                
                cost_match = re.search(r'cost[:]*\s*(.*?)(?:\.|;|$)', trade_off_text, re.IGNORECASE)
                if cost_match:
                    cost = cost_match.group(1).strip()
            
            trade_offs.append({
                "description": description,
                "benefit": benefit,
                "cost": cost
            })
        
        return trade_offs
    
    def _extract_characteristics(self, exploration: str) -> Dict[str, Any]:
        """Extract path characteristics from exploration text.
        
        Args:
            exploration: Exploration text
            
        Returns:
            Dictionary of characteristics
        """
        characteristics = {}
        
        # Look for common characteristics
        for char in ["implementation_complexity", "team_expertise_required", 
                    "maintainability", "scalability", "innovation_level"]:
            # Convert from snake_case to readable format for regex
            readable = char.replace("_", " ").title()
            
            # Look for mentions of this characteristic
            pattern = rf'{readable}[:]*\s*([A-Za-z0-9 .-]+)'
            match = re.search(pattern, exploration, re.IGNORECASE)
            
            if match:
                characteristics[char] = match.group(1).strip()
        
        # If not found, look in a characteristics section
        if not characteristics:
            section_match = re.search(r'#+\s*(?:Path )?Characteristics[:]*\s*\n', exploration)
            if section_match:
                start_pos = section_match.end()
                
                # Find the next section or end of text
                next_section = re.search(r'#+\s*', exploration[start_pos:])
                if next_section:
                    end_pos = start_pos + next_section.start()
                    section_text = exploration[start_pos:end_pos]
                else:
                    section_text = exploration[start_pos:]
                
                # Extract characteristic items
                item_matches = re.finditer(r'[-*]\s*([^:]+)[:]\s*(.*?)(?:\n|$)', section_text)
                
                for match in item_matches:
                    key = match.group(1).strip().lower().replace(" ", "_")
                    value = match.group(2).strip()
                    characteristics[key] = value
        
        # Set defaults if not found
        if "implementation_complexity" not in characteristics:
            characteristics["implementation_complexity"] = "Medium"
        if "maintainability" not in characteristics:
            characteristics["maintainability"] = "Good"
        if "scalability" not in characteristics:
            characteristics["scalability"] = "Medium"
        
        return characteristics
    
    @handle_async_errors
    async def _handle_path_exploration_request(self, message: AgentMessage) -> None:
        """Handle a request to explore a research path.
        
        Args:
            message: Request message
        """
        logger.info(f"Agent {self.agent_id} handling path exploration request")
        
        # Extract path index
        path_index = message.content.get("path_index")
        if path_index is None:
            logger.error("Missing path index in request")
            return
        
        # Explore the path
        exploration_results = await self._explore_research_path(path_index)
        
        # Send response
        await self.send_message(
            recipient_id=message.sender_id,
            message_type="path_exploration_response",
            content=exploration_results,
            reply_to=message.id
        )