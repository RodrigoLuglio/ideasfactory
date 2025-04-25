"""
Synthesis agent for specialized research teams.

This module defines the SynthesisAgent class that compiles findings 
from all research agents into a comprehensive research report.
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional
import re
import os
from pathlib import Path

from ideasfactory.utils.error_handler import handle_errors, handle_async_errors
from ideasfactory.utils.file_manager import save_document
from ideasfactory.utils.session_manager import SessionManager
from ideasfactory.agents.research_agents.base_agent import BaseResearchAgent, AgentMessage
from ideasfactory.agents.research_agents.repository import (
    ResearchDimension, 
    FoundationChoice,
    ResearchPath,
    CrossParadigmOpportunity,
    Debate,
    DebateStatus
)
from ideasfactory.tools.research_visualization import (
    generate_dimension_map,
    generate_research_paths_visualization,
    generate_cross_paradigm_opportunities_map,
    generate_dimensional_research_report
)


# Configure logging
logger = logging.getLogger(__name__)


class SynthesisAgent(BaseResearchAgent):
    """
    Agent responsible for synthesizing research findings.
    
    This agent compiles findings from all research agents into a
    comprehensive final research report, creates visualizations,
    and concludes foundation debates.
    """
    
    @property
    def system_prompt(self) -> str:
        """Get the system prompt for the synthesis agent."""
        return """You are a Synthesis Specialist in a multi-agent research team. Your role is to:

1. Compile findings from all research agents into a comprehensive, well-structured report
2. Create clear visualizations that effectively communicate complex relationships
3. Conclude debates by finding consensus or selecting optimal choices with clear rationale
4. Remain neutral and objective, giving equal consideration to all paradigms and approaches
5. Identify the most promising paths and cross-paradigm opportunities
6. Highlight implications of foundation choices across the technology stack
7. Present trade-offs clearly without bias toward any specific approach
8. Ensure all technical decisions have clear justification and context
9. Structure information hierarchically to aid understanding
10. Use clear, precise language suitable for both technical and business stakeholders

Your primary strength is your ability to synthesize complex information into clear, actionable recommendations while maintaining a balanced perspective. You excel at distilling complex technical concepts into clear explanations without oversimplification.

When creating the research report, you should:
- Maintain an unbiased perspective across all paradigms
- Clearly separate facts from opinions and recommendations
- Include supporting evidence for all conclusions
- Acknowledge limitations and trade-offs
- Present information in a logical, hierarchical structure
- Use visualization to clarify complex relationships

You are the final integrator of all research findings, ensuring a comprehensive and cohesive research report that will guide architectural decisions.
"""
    
    @property
    def agent_type(self) -> str:
        """Get the type of this agent."""
        return "synthesis"
    
    @handle_async_errors
    async def initialize(self, session_id: str) -> bool:
        """Initialize the agent with session context.
        
        Args:
            session_id: Session ID to initialize with
            
        Returns:
            True if initialization successful
        """
        self.session_manager.set_current_session(session_id)
        
        # Register message handlers
        self.register_message_handler("request_synthesis", self._handle_synthesis_request)
        
        logger.info(f"Synthesis agent {self.agent_id} initialized for session {session_id}")
        return True
    
    @handle_async_errors
    async def _handle_synthesis_request(self, message: AgentMessage) -> None:
        """Handle a request for synthesis.
        
        Args:
            message: Message containing the request
        """
        if "task" not in message.content:
            logger.error("Synthesis request missing task")
            return
        
        task = message.content["task"]
        
        if task == "conclude_debate":
            if "debate_index" in message.content:
                debate_index = message.content["debate_index"]
                await self._conclude_debate(debate_index)
        elif task == "create_report":
            await self._create_research_report()
    
    @handle_async_errors
    async def process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a research task.
        
        Args:
            task_data: Task data including type and parameters
            
        Returns:
            Task results
        """
        task_type = task_data.get("task_type")
        
        if task_type == "conclude_foundation_debate":
            return await self._conclude_foundation_debate(task_data)
        elif task_type == "create_research_report":
            return await self._create_research_report()
        else:
            logger.warning(f"Unknown task type: {task_type}")
            return {"error": f"Unknown task type: {task_type}"}
    
    @handle_async_errors
    async def _conclude_foundation_debate(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Conclude a foundation debate with a final decision.
        
        Args:
            task_data: Task data including debate index
            
        Returns:
            Task results
        """
        debate_index = task_data.get("debate_index")
        
        if debate_index is None:
            logger.error("No debate index provided")
            return {"error": "No debate index provided"}
        
        if debate_index < 0 or debate_index >= len(self.repository.debates):
            logger.error(f"Debate index {debate_index} out of range")
            return {"error": f"Debate index {debate_index} out of range"}
        
        debate = self.repository.debates[debate_index]
        
        if debate.status != DebateStatus.ACTIVE:
            logger.error("Cannot conclude already concluded debate")
            return {"error": "Cannot conclude already concluded debate"}
        
        if not debate.contributions:
            logger.error("Cannot conclude debate with no contributions")
            return {"error": "Cannot conclude debate with no contributions"}
        
        # Extract dimension name from topic
        dimension_name = None
        if debate.topic.startswith("Foundation choices for "):
            dimension_name = debate.topic[len("Foundation choices for "):]
        
        if not dimension_name:
            logger.error("Could not extract dimension name from debate topic")
            return {"error": "Could not extract dimension name from debate topic"}
        
        # Get the dimension
        dimension = self.repository.get_dimension(dimension_name)
        if not dimension:
            logger.error(f"Dimension {dimension_name} not found")
            return {"error": f"Dimension {dimension_name} not found"}
        
        # Analyze contributions and make a decision
        prompt = f"""Below are contributions to a debate about foundation choices for the dimension "{dimension_name}".

Dimension description: {dimension.description}

Foundation impact: {dimension.foundation_impact}

Research areas:
{self._format_research_areas(dimension.research_areas)}

Debate contributions:
{self._format_debate_contributions(debate.contributions)}

Your task is to conclude this debate by:
1. Analyzing all contributions from different agent perspectives
2. Identifying the most promising foundation choice(s) for this dimension
3. Providing a clear rationale for your conclusion
4. Considering implications for dependent dimensions
5. Acknowledging trade-offs

Provide your conclusion in this format:
- Selected foundation choice: [clear name of the choice]
- Rationale: [detailed explanation]
- Implications: [key impacts on other dimensions]
- Trade-offs: [what we gain and lose with this choice]
"""
        
        # Generate conclusion
        conclusion = await self.generate_content(prompt, with_system_prompt=True)
        
        # Extract the chosen foundation
        choice_match = re.search(r"Selected foundation choice:\s*(.+?)(?:-|$|\n)", conclusion, re.DOTALL)
        choice = choice_match.group(1).strip() if choice_match else "Unspecified choice"
        
        # Conclude the debate
        await self.repository.conclude_debate(debate_index, conclusion)
        
        # Add as foundation choice
        foundation_choice = FoundationChoice(
            dimension=dimension_name,
            choice=choice,
            rationale=conclusion,
            chosen_by=self.agent_id,
            paradigm="synthesis",  # Best choice across paradigms
            implications=[]  # Would parse these from conclusion in a real implementation
        )
        
        await self.repository.add_foundation_choice(foundation_choice)
        
        return {
            "status": "success",
            "dimension_name": dimension_name,
            "conclusion": conclusion
        }
    
    @handle_async_errors
    async def _create_research_report(self) -> Dict[str, Any]:
        """Create the final research report.
        
        Returns:
            Task results
        """
        # Generate visualizations
        dimension_map = generate_dimension_map(self.repository.dimensions)
        paths_visualization = generate_research_paths_visualization(self.repository.research_paths)
        opportunities_map = generate_cross_paradigm_opportunities_map(self.repository.opportunities)
        
        # Prepare content for research report
        foundation_choices_content = self._format_foundation_choices()
        research_paths_content = self._format_research_paths()
        opportunities_content = self._format_opportunities()
        
        # Generate the report
        prompt = f"""You are creating a comprehensive research report that synthesizes all findings from our multi-agent research team. The research covered multiple dimensions and paradigms, exploring different technological paths.

Your task is to create a well-structured research report with the following sections:

1. Executive Summary
2. Research Dimensions and Foundation Choices
3. Research Paths Analysis
4. Cross-Paradigm Opportunities
5. Recommendations
6. Conclusion

Use the following information to create the report:

## Foundation Choices:
{foundation_choices_content}

## Research Paths:
{research_paths_content}

## Cross-Paradigm Opportunities:
{opportunities_content}

## Visualizations:
- Dimension Map: {dimension_map}
- Research Paths Visualization: {paths_visualization}
- Cross-Paradigm Opportunities Map: {opportunities_map}

The report should provide a comprehensive overview of the research findings while remaining neutral and objective. It should present clear recommendations based on the research, including the most promising technology paths and integration opportunities.

Format the report in Markdown with appropriate headings, bullet points, and emphasis.
"""
        
        # Generate the report content
        report_content = await self.generate_content(prompt, with_system_prompt=True)
        
        # Add visualizations to the report
        report_with_viz = generate_dimensional_research_report(
            report_content,
            dimension_map,
            paths_visualization,
            opportunities_map
        )
        
        # Save the report
        try:
            session_id = self.session_manager.get_current_session()
            report_path = await save_document(
                session_id,
                "research-report/dimensional-research-report.md",
                report_with_viz
            )
            
            # Add to session
            self.session_manager.add_document(
                session_id,
                "research-report",
                report_path
            )
            
            logger.info(f"Research report saved to {report_path}")
            
            return {
                "status": "success",
                "report_path": report_path
            }
        except Exception as e:
            logger.error(f"Error saving research report: {str(e)}")
            return {
                "status": "error",
                "error": f"Error saving research report: {str(e)}"
            }
    
    def _format_research_areas(self, areas: List[Dict[str, str]]) -> str:
        """Format research areas for prompts.
        
        Args:
            areas: List of research areas
            
        Returns:
            Formatted string
        """
        if not areas:
            return "No specific research areas defined."
        
        result = ""
        for i, area in enumerate(areas):
            result += f"{i+1}. "
            for key, value in area.items():
                result += f"{key}: {value}, "
            result = result[:-2] + "\n"
        
        return result
    
    def _format_debate_contributions(self, contributions: List[Any]) -> str:
        """Format debate contributions for prompts.
        
        Args:
            contributions: List of debate contributions
            
        Returns:
            Formatted string
        """
        if not contributions:
            return "No contributions to the debate."
        
        result = ""
        for i, contribution in enumerate(contributions):
            result += f"### Contribution {i+1} (from {contribution.agent_type} agent)\n"
            result += f"{contribution.content}\n\n"
        
        return result
    
    def _format_foundation_choices(self) -> str:
        """Format foundation choices for the research report.
        
        Returns:
            Formatted string
        """
        if not self.repository.foundation_choices:
            return "No foundation choices have been established."
        
        result = "# Foundation Choices\n\n"
        
        # Group by dimension
        choices_by_dimension = {}
        for choice in self.repository.foundation_choices:
            if choice.dimension not in choices_by_dimension:
                choices_by_dimension[choice.dimension] = []
            choices_by_dimension[choice.dimension].append(choice)
        
        # Format by dimension
        for dimension, choices in choices_by_dimension.items():
            result += f"## {dimension}\n\n"
            
            for choice in choices:
                result += f"### {choice.choice} (from {choice.paradigm} paradigm)\n\n"
                result += f"Rationale: {choice.rationale}\n\n"
                
                if choice.implications:
                    result += "Implications:\n"
                    for imp in choice.implications:
                        result += f"- {imp.get('description', 'Unspecified implication')}\n"
                    result += "\n"
            
            result += "\n"
        
        return result
    
    def _format_research_paths(self) -> str:
        """Format research paths for the research report.
        
        Returns:
            Formatted string
        """
        if not self.repository.research_paths:
            return "No research paths have been explored."
        
        result = "# Research Paths\n\n"
        
        for path in self.repository.research_paths:
            result += f"## {path.name}\n\n"
            result += f"{path.description}\n\n"
            
            result += "Foundation choices:\n"
            for dim, choice in path.foundation_choices.items():
                result += f"- {dim}: {choice}\n"
            result += "\n"
            
            if path.technologies:
                result += "Technologies:\n"
                for tech in path.technologies:
                    result += f"- {tech.get('name', 'Unnamed technology')}: {tech.get('description', 'No description')}\n"
                result += "\n"
            
            if path.trade_offs:
                result += "Trade-offs:\n"
                for trade_off in path.trade_offs:
                    result += f"- {trade_off.get('description', 'Unspecified trade-off')}\n"
                result += "\n"
            
            if path.characteristics:
                result += "Characteristics:\n"
                for key, value in path.characteristics.items():
                    result += f"- {key}: {value}\n"
                result += "\n"
            
            result += f"Overall score: {path.overall_score}\n\n"
        
        return result
    
    def _format_opportunities(self) -> str:
        """Format cross-paradigm opportunities for the research report.
        
        Returns:
            Formatted string
        """
        if not self.repository.opportunities:
            return "No cross-paradigm opportunities have been identified."
        
        result = "# Cross-Paradigm Opportunities\n\n"
        
        for opp in self.repository.opportunities:
            result += f"## {opp.name}\n\n"
            result += f"{opp.description}\n\n"
            
            result += f"Combining paradigms:\n"
            result += f"- {opp.paradigm1.get('name', 'Unnamed paradigm')}: {opp.paradigm1.get('description', 'No description')}\n"
            result += f"- {opp.paradigm2.get('name', 'Unnamed paradigm')}: {opp.paradigm2.get('description', 'No description')}\n\n"
            
            result += f"Potential score: {opp.potential_score}\n"
            result += f"Integration complexity: {opp.integration_complexity}\n\n"
            
            if opp.benefits:
                result += "Benefits:\n"
                for benefit in opp.benefits:
                    result += f"- {benefit}\n"
                result += "\n"
            
            if opp.challenges:
                result += "Challenges:\n"
                for challenge in opp.challenges:
                    result += f"- {challenge}\n"
                result += "\n"
            
            if opp.implementation_approach:
                result += f"Implementation approach: {opp.implementation_approach}\n\n"
        
        return result