"""
Integration Agent for specialized research teams.

This module defines the IntegrationAgent class responsible for
identifying cross-paradigm opportunities and integration patterns.
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional
import re
from itertools import combinations

from ideasfactory.utils.error_handler import handle_errors, handle_async_errors
from ideasfactory.utils.file_manager import load_document_content
from ideasfactory.agents.research_agents.base_agent import BaseResearchAgent, AgentMessage


# Configure logging
logger = logging.getLogger(__name__)


class IntegrationAgent(BaseResearchAgent):
    """
    Integration Agent specializing in cross-paradigm opportunities and integration patterns.
    
    This agent analyzes compatibility between technologies across dimensions and identifies
    novel combinations that create superior solutions.
    """
    
    @property
    def agent_type(self) -> str:
        """Get the type of this agent."""
        return "integration"
    
    @property
    def system_prompt(self) -> str:
        """Get the system prompt for this agent."""
        return """
        You are an Integration Agent specializing in cross-paradigm opportunities and integration patterns.
        Your role is to analyze how technologies from different dimensions and paradigms can work together
        to create a cohesive system.

        Focus on:
        1. Identifying compatibility between technologies across dimensions
        2. Discovering novel combinations that address limitations in single-paradigm solutions
        3. Creating integration patterns for connecting disparate technologies
        4. Analyzing system boundaries and interface requirements
        5. Highlighting cross-cutting concerns that affect multiple dimensions

        Avoid:
        1. Forcing integration between fundamentally incompatible technologies
        2. Creating unnecessarily complex integration patterns
        3. Ignoring practical implementation challenges
        4. Overlooking maintenance and operational concerns

        As you analyze integration opportunities, be creative yet practical, finding novel combinations
        that truly address project needs while providing clear, implementable integration approaches.
        """
    
    def __init__(self, agent_id: str, coordinator: Any = None, repository: Any = None):
        """Initialize the integration agent."""
        super().__init__(agent_id, coordinator, repository)
        
        # Register message handlers
        self.register_message_handler("request_integration_analysis", 
                                     self._handle_integration_analysis_request)
        
        # Agent state
        self.identified_opportunities: List[Dict[str, Any]] = []
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
            logger.error(f"Error initializing integration agent: {str(e)}")
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
        
        if task_type == "identify_integration_opportunities":
            return await self._identify_integration_opportunities()
        else:
            return {"error": f"Unknown task type: {task_type}"}
    
    @handle_async_errors
    async def _identify_integration_opportunities(self) -> Dict[str, Any]:
        """Identify cross-paradigm integration opportunities.
        
        Returns:
            Integration analysis results
        """
        logger.info(f"Agent {self.agent_id} identifying integration opportunities")
        
        if not self.repository:
            return {"error": "No repository available"}
        
        # Get all dimensions
        dimensions = list(self.repository.dimensions.values())
        
        # Get all research paths
        paths = self.repository.research_paths
        
        if not paths:
            return {"error": "No research paths available"}
        
        # Create a mapping of dimensions to technologies across paths
        dimension_technologies = {}
        for path in paths:
            for dimension in path.dimensions:
                dim_name = dimension.get("name")
                if dim_name not in dimension_technologies:
                    dimension_technologies[dim_name] = []
                
                dimension_technologies[dim_name].extend(dimension.get("technologies", []))
        
        # Prepare context for analysis
        context = {
            "Project Vision": self.vision_document or "Not available",
            "PRD": self.prd_document or "Not available",
            "Research Requirements": self.research_requirements
        }
        
        # Add path descriptions
        path_descriptions = []
        for i, path in enumerate(paths):
            path_descriptions.append(f"Path {i+1}: {path.name}")
            path_descriptions.append(f"Description: {path.description}")
            path_descriptions.append("Foundation Choices:")
            for dim, choice in path.foundation_choices.items():
                path_descriptions.append(f"- {dim}: {choice}")
            path_descriptions.append("")
        
        context["Research Paths"] = "\n".join(path_descriptions)
        
        # Add technologies by dimension
        tech_descriptions = []
        for dim_name, techs in dimension_technologies.items():
            tech_descriptions.append(f"Technologies for {dim_name}:")
            seen_tech_names = set()
            for tech in techs:
                tech_name = tech.get("name", "")
                if tech_name and tech_name not in seen_tech_names:
                    seen_tech_names.add(tech_name)
                    
                    paradigm = tech.get("paradigm", "")
                    limitations = tech.get("limitations", [])
                    
                    tech_descriptions.append(f"- {tech_name} ({paradigm})")
                    if limitations:
                        tech_descriptions.append(f"  Limitations: {', '.join(limitations[:3])}")
            tech_descriptions.append("")
        
        context["Technologies"] = "\n".join(tech_descriptions)
        
        # Create prompt for integration analysis
        prompt = """
        Analyze technologies across dimensions and paths to identify cross-paradigm integration opportunities.

        For each opportunity:
        1. Identify technologies from different paradigms that could be combined
        2. Analyze how they complement each other's strengths and limitations
        3. Describe the potential benefits of this integration
        4. Assess the integration complexity and challenges
        5. Outline a high-level integration approach

        Focus on novel combinations that address limitations in single-paradigm solutions while
        maintaining architectural coherence and practical implementability.
        """
        
        # Generate integration analysis
        analysis_text = await self.generate_content(prompt, context)
        
        # Parse the analysis to extract opportunities
        opportunities = self._extract_opportunities_from_analysis(analysis_text)
        
        # Store for later use
        self.identified_opportunities = opportunities
        
        # Add opportunities to repository
        for opp in opportunities:
            from ideasfactory.agents.research_agents.repository import CrossParadigmOpportunity
            
            # Convert to repository model
            repo_opp = CrossParadigmOpportunity(
                name=opp["name"],
                description=opp["description"],
                paradigm1=opp["paradigm1"],
                paradigm2=opp["paradigm2"],
                potential_score=opp["potential_score"],
                integration_complexity=opp["integration_complexity"],
                benefits=opp["benefits"],
                challenges=opp["challenges"],
                implementation_approach=opp["implementation_approach"],
                identified_by=self.agent_id
            )
            
            await self.repository.add_opportunity(repo_opp)
        
        return {
            "opportunities": opportunities,
            "analysis": analysis_text
        }
    
    def _extract_opportunities_from_analysis(self, analysis: str) -> List[Dict[str, Any]]:
        """Extract structured opportunity data from analysis text.
        
        Args:
            analysis: Analysis text
            
        Returns:
            List of opportunities
        """
        opportunities = []
        
        # Look for opportunity headers
        opp_matches = re.finditer(r'#+\s*(?:Opportunity|Integration)[:]*\s*(.*?)\n', analysis)
        
        for match in opp_matches:
            opp_name = match.group(1).strip()
            start_pos = match.end()
            
            # Find the next opportunity header or end of text
            next_match = re.search(r'#+\s*(?:Opportunity|Integration)[:]*\s*', analysis[start_pos:])
            if next_match:
                end_pos = start_pos + next_match.start()
                opp_text = analysis[start_pos:end_pos]
            else:
                opp_text = analysis[start_pos:]
            
            # Extract details
            description = self._extract_description(opp_text)
            
            # Extract technologies and paradigms
            paradigm1 = {}
            paradigm2 = {}
            tech_sections = re.finditer(r'(?:From|Technology from)\s+([^:]+)[:]\s*\n', opp_text)
            
            tech_count = 0
            for tech_match in tech_sections:
                paradigm_name = tech_match.group(1).strip()
                tech_start = tech_match.end()
                
                # Find end of technology section
                next_tech = re.search(r'(?:From|Technology from|Benefits|Challenges|Integration)', opp_text[tech_start:])
                if next_tech:
                    tech_end = tech_start + next_tech.start()
                    tech_text = opp_text[tech_start:tech_end]
                else:
                    tech_text = opp_text[tech_start:]
                
                # Extract technology names and details
                tech_items = re.finditer(r'[-*]\s*([^:]+)(?:[:]\s*(.*?))?(?:\n|$)', tech_text)
                technologies = []
                
                for item in tech_items:
                    tech_name = item.group(1).strip()
                    tech_detail = item.group(2).strip() if item.group(2) else ""
                    
                    technologies.append({
                        "name": tech_name,
                        "contribution": tech_detail
                    })
                
                # Assign to paradigm1 or paradigm2
                if tech_count == 0:
                    paradigm1 = {
                        "name": paradigm_name,
                        "technologies": technologies
                    }
                else:
                    paradigm2 = {
                        "name": paradigm_name,
                        "technologies": technologies
                    }
                
                tech_count += 1
            
            # Extract benefits
            benefits_match = re.search(r'(?:Benefits|Potential Benefits)[:]\s*\n(.*?)(?:(?:^#+\s*|^(?:Challenges|Integration))|\Z)', 
                                     opp_text, re.MULTILINE | re.DOTALL)
            benefits = []
            if benefits_match:
                benefits_text = benefits_match.group(1)
                benefit_items = re.finditer(r'[-*]\s*(.*?)(?:\n|$)', benefits_text)
                for item in benefit_items:
                    benefits.append(item.group(1).strip())
            
            # Extract challenges
            challenges_match = re.search(r'(?:Challenges|Integration Challenges)[:]\s*\n(.*?)(?:(?:^#+\s*|^(?:Integration|Implementation))|\Z)', 
                                       opp_text, re.MULTILINE | re.DOTALL)
            challenges = []
            if challenges_match:
                challenges_text = challenges_match.group(1)
                challenge_items = re.finditer(r'[-*]\s*(.*?)(?:\n|$)', challenges_text)
                for item in challenge_items:
                    challenges.append(item.group(1).strip())
            
            # Extract implementation approach
            impl_match = re.search(r'(?:Implementation|Integration Approach|Approach)[:]\s*\n(.*?)(?:^#+\s*|\Z)', 
                                 opp_text, re.MULTILINE | re.DOTALL)
            implementation_approach = ""
            if impl_match:
                implementation_approach = impl_match.group(1).strip()
            
            # Extract or estimate potential score
            potential_score = 0.75  # Default
            potential_match = re.search(r'(?:Potential|Integration Potential|Score)[:]\s*([0-9.]+)', opp_text)
            if potential_match:
                try:
                    potential_score = float(potential_match.group(1))
                    # Normalize to 0-1 scale if needed
                    if potential_score > 1.0:
                        potential_score /= 10.0
                except ValueError:
                    pass
            
            # Extract or estimate integration complexity
            integration_complexity = "Medium"  # Default
            complexity_match = re.search(r'(?:Complexity|Integration Complexity)[:]\s*([A-Za-z]+)', opp_text)
            if complexity_match:
                complexity = complexity_match.group(1).strip()
                if complexity.lower() in ["low", "medium", "high"]:
                    integration_complexity = complexity.title()
            
            # Create the opportunity
            opportunities.append({
                "name": opp_name,
                "description": description,
                "paradigm1": paradigm1,
                "paradigm2": paradigm2,
                "potential_score": potential_score,
                "integration_complexity": integration_complexity,
                "benefits": benefits,
                "challenges": challenges,
                "implementation_approach": implementation_approach
            })
        
        return opportunities
    
    def _extract_description(self, text: str) -> str:
        """Extract opportunity description from text.
        
        Args:
            text: Opportunity text
            
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
    
    @handle_async_errors
    async def _handle_integration_analysis_request(self, message: AgentMessage) -> None:
        """Handle a request for integration analysis.
        
        Args:
            message: Request message
        """
        logger.info(f"Agent {self.agent_id} handling integration analysis request")
        
        # Process the analysis
        analysis_results = await self._identify_integration_opportunities()
        
        # Send response
        await self.send_message(
            recipient_id=message.sender_id,
            message_type="integration_analysis_response",
            content=analysis_results,
            reply_to=message.id
        )