"""
Agent coordinator for specialized research teams.

This module defines the AgentCoordinator class that orchestrates
communication between specialized research agents.
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional, Set, Type
import uuid

from ideasfactory.utils.error_handler import handle_errors, handle_async_errors
from ideasfactory.utils.session_manager import SessionManager
from ideasfactory.agents.research_agents.base_agent import BaseResearchAgent, AgentMessage
from ideasfactory.agents.research_agents.repository import DimensionalResearchRepository


# Configure logging
logger = logging.getLogger(__name__)


class AgentCoordinator:
    """
    Coordinator for specialized research agents.
    
    This class orchestrates communication between agents and manages
    the overall research workflow.
    """
    
    _instance = None
    
    def __new__(cls):
        """Ensure singleton pattern for the coordinator."""
        if cls._instance is None:
            cls._instance = super(AgentCoordinator, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the coordinator."""
        if self._initialized:
            return
        
        self._initialized = True
        self.session_manager = SessionManager()
        self.repository = DimensionalResearchRepository()
        
        # Agent management
        self.agents: Dict[str, BaseResearchAgent] = {}
        self.agent_types: Dict[str, List[str]] = {}  # type -> list of agent IDs
        
        # Workflow management
        self.session_id: Optional[str] = None
        self.current_phase: Optional[str] = None
        self.phase_status: Dict[str, str] = {}
        
        # Communication management
        self.message_history: List[AgentMessage] = []
        
        # Locks for thread safety
        self._agent_lock = asyncio.Lock()
        self._message_lock = asyncio.Lock()
    
    @handle_errors
    def register_agent(self, agent: BaseResearchAgent) -> None:
        """Register an agent with the coordinator.
        
        Args:
            agent: Agent to register
        """
        # Set coordinator and repository for the agent
        agent.coordinator = self
        agent.repository = self.repository
        
        # Register agent
        self.agents[agent.agent_id] = agent
        
        # Register by type
        agent_type = agent.agent_type
        if agent_type not in self.agent_types:
            self.agent_types[agent_type] = []
        
        self.agent_types[agent_type].append(agent.agent_id)
        
        logger.info(f"Registered agent {agent.agent_id} of type {agent_type}")
    
    @handle_errors
    def unregister_agent(self, agent_id: str) -> None:
        """Unregister an agent from the coordinator.
        
        Args:
            agent_id: ID of agent to unregister
        """
        if agent_id not in self.agents:
            logger.warning(f"Agent {agent_id} not registered")
            return
        
        agent = self.agents[agent_id]
        agent_type = agent.agent_type
        
        # Unregister from type mapping
        if agent_type in self.agent_types and agent_id in self.agent_types[agent_type]:
            self.agent_types[agent_type].remove(agent_id)
            
        # Unregister agent
        del self.agents[agent_id]
        
        logger.info(f"Unregistered agent {agent_id}")
    
    @handle_errors
    def get_agent(self, agent_id: str) -> Optional[BaseResearchAgent]:
        """Get an agent by ID.
        
        Args:
            agent_id: ID of agent to get
            
        Returns:
            Agent or None if not found
        """
        return self.agents.get(agent_id)
    
    @handle_errors
    def get_agents_by_type(self, agent_type: str) -> List[BaseResearchAgent]:
        """Get all agents of a specific type.
        
        Args:
            agent_type: Type of agents to get
            
        Returns:
            List of agents of the specified type
        """
        if agent_type not in self.agent_types:
            return []
        
        return [self.agents[agent_id] for agent_id in self.agent_types[agent_type]]
    
    @handle_async_errors
    async def deliver_message(self, message: AgentMessage) -> None:
        """Deliver a message to its recipient(s).
        
        Args:
            message: Message to deliver
        """
        async with self._message_lock:
            # Add to message history
            self.message_history.append(message)
            
            if message.recipient_id is None:
                # Broadcast to all agents except sender
                for agent_id, agent in self.agents.items():
                    if agent_id != message.sender_id:
                        await agent.receive_message(message)
            else:
                # Deliver to specific recipient
                recipient = self.agents.get(message.recipient_id)
                if recipient:
                    await recipient.receive_message(message)
                else:
                    logger.warning(f"Recipient {message.recipient_id} not found for message")
    
    @handle_async_errors
    async def initialize_agents(self, session_id: str) -> bool:
        """Initialize all registered agents with session context.
        
        Args:
            session_id: Session ID to initialize with
            
        Returns:
            True if initialization successful
        """
        self.session_id = session_id
        
        # Initialize repository
        self.repository.load_from_session(session_id)
        
        # Initialize all agents
        tasks = []
        for agent_id, agent in self.agents.items():
            tasks.append(agent.initialize(session_id))
        
        # Wait for all agents to initialize
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Check for failures
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Agent initialization failed: {str(result)}")
                return False
            elif not result:
                logger.error(f"Agent initialization failed")
                return False
        
        logger.info(f"Initialized {len(self.agents)} agents for session {session_id}")
        return True
    
    @handle_async_errors
    async def create_specialized_agents(self, 
                                      session_id: str,
                                      foundation_count: int = 2,
                                      paradigm_counts: Dict[str, int] = None,
                                      path_count: int = 3,
                                      integration_count: int = 2,
                                      synthesis_count: int = 1) -> None:
        """Create and register specialized agents for a research session.
        
        Args:
            session_id: Session ID
            foundation_count: Number of foundation agents
            paradigm_counts: Dict mapping paradigm types to counts
            path_count: Number of path exploration agents
            integration_count: Number of integration agents
            synthesis_count: Number of synthesis agents
        """
        from ideasfactory.agents.research_agents.foundation_agent import FoundationAgent
        from ideasfactory.agents.research_agents.paradigm_agent import (
            EstablishedParadigmAgent,
            MainstreamParadigmAgent,
            CuttingEdgeParadigmAgent,
            ExperimentalParadigmAgent,
            CrossParadigmAgent,
            FirstPrinciplesAgent,
        )
        from ideasfactory.agents.research_agents.path_agent import PathExplorationAgent
        from ideasfactory.agents.research_agents.integration_agent import IntegrationAgent
        from ideasfactory.agents.research_agents.synthesis_agent import SynthesisAgent
        
        # Default paradigm counts if not provided
        if paradigm_counts is None:
            paradigm_counts = {
                "established": 1,
                "mainstream": 1,
                "cutting_edge": 1,
                "experimental": 1,
                "cross_paradigm": 1,
                "first_principles": 1
            }
        
        # Create and register foundation agents
        for i in range(foundation_count):
            agent_id = f"foundation_{i+1}"
            agent = FoundationAgent(agent_id=agent_id)
            self.register_agent(agent)
        
        # Create and register paradigm agents
        for paradigm, count in paradigm_counts.items():
            for i in range(count):
                agent_id = f"{paradigm}_{i+1}"
                
                # Create the appropriate agent type
                if paradigm == "established":
                    agent = EstablishedParadigmAgent(agent_id=agent_id)
                elif paradigm == "mainstream":
                    agent = MainstreamParadigmAgent(agent_id=agent_id)
                elif paradigm == "cutting_edge":
                    agent = CuttingEdgeParadigmAgent(agent_id=agent_id)
                elif paradigm == "experimental":
                    agent = ExperimentalParadigmAgent(agent_id=agent_id)
                elif paradigm == "cross_paradigm":
                    agent = CrossParadigmAgent(agent_id=agent_id)
                elif paradigm == "first_principles":
                    agent = FirstPrinciplesAgent(agent_id=agent_id)
                else:
                    logger.warning(f"Unknown paradigm type: {paradigm}")
                    continue
                
                self.register_agent(agent)
        
        # Create and register path exploration agents
        for i in range(path_count):
            agent_id = f"path_{i+1}"
            agent = PathExplorationAgent(agent_id=agent_id)
            self.register_agent(agent)
        
        # Create and register integration agents
        for i in range(integration_count):
            agent_id = f"integration_{i+1}"
            agent = IntegrationAgent(agent_id=agent_id)
            self.register_agent(agent)
        
        # Create and register synthesis agents
        for i in range(synthesis_count):
            agent_id = f"synthesis_{i+1}"
            agent = SynthesisAgent(agent_id=agent_id)
            self.register_agent(agent)
        
        # Initialize all agents
        await self.initialize_agents(session_id)
        
        logger.info(f"Created specialized agents for session {session_id}")
    
    @handle_async_errors
    async def start_foundation_research_phase(self) -> None:
        """Start the foundation research phase of the workflow."""
        if not self.session_id:
            logger.error("No active session to start foundation research")
            return
        
        self.current_phase = "foundation_research"
        self.phase_status[self.current_phase] = "in_progress"
        
        logger.info("Starting foundation research phase")
        
        # Get research requirements from session
        session = self.session_manager.get_session(self.session_id)
        if not session:
            logger.error(f"Session {self.session_id} not found")
            return
        
        requirements_path = self.session_manager.get_document(
            self.session_id, "research-requirements"
        )
        
        if not requirements_path:
            logger.error("No research requirements document found in session")
            return
        
        # Load research requirements
        from ideasfactory.utils.file_manager import load_document_content
        
        requirements_content = await load_document_content(
            self.session_id, "research-requirements"
        )
        
        if not requirements_content:
            logger.error("Failed to load research requirements content")
            return
        
        # Extract dimensions
        from ideasfactory.agents.research_team import ResearchTeam
        
        research_team = ResearchTeam()
        dimensions = await research_team._extract_research_dimensions(requirements_content)
        
        # Add dimensions to repository
        for name, dimension in dimensions.items():
            from ideasfactory.agents.research_agents.repository import ResearchDimension
            
            # Convert to repository model
            repo_dimension = ResearchDimension(
                name=dimension.name,
                description=dimension.description,
                research_areas=dimension.research_areas,
                dependencies=dimension.dependencies,
                foundation_impact=dimension.foundation_impact
            )
            
            await self.repository.add_dimension(repo_dimension)
        
        # Start foundation debate
        await self._start_foundation_debate()
    
    @handle_async_errors
    async def _start_foundation_debate(self) -> None:
        """Start the foundation debate among agents."""
        # Get foundation dimensions
        foundation_dimensions = self.repository.get_foundation_dimensions()
        
        if not foundation_dimensions:
            logger.error("No foundation dimensions found to debate")
            return
        
        # Start a debate for each foundation dimension
        for dimension in foundation_dimensions:
            # Create debate
            debate_topic = f"Foundation choices for {dimension.name}"
            debate_description = (
                f"This debate aims to identify the best foundation choices for {dimension.name}. "
                f"Agents should propose and evaluate options across paradigms, considering "
                f"implications for dependent dimensions."
            )
            
            debate = await self.repository.start_debate(
                topic=debate_topic,
                description=debate_description
            )
            
            # Get debate index
            debate_index = self.repository.debates.index(debate)
            
            # Notify foundation agents to contribute
            foundation_agents = self.get_agents_by_type("foundation")
            
            for agent in foundation_agents:
                # Create task for agent to contribute
                task_data = {
                    "task_type": "foundation_debate_contribution",
                    "dimension_name": dimension.name,
                    "debate_index": debate_index
                }
                
                # Process asynchronously
                asyncio.create_task(agent.process_task(task_data))
            
            # Notify paradigm agents to contribute
            for paradigm in ["established", "mainstream", "cutting_edge", 
                            "experimental", "cross_paradigm", "first_principles"]:
                paradigm_agents = self.get_agents_by_type(paradigm)
                
                for agent in paradigm_agents:
                    # Create task for agent to contribute
                    task_data = {
                        "task_type": "foundation_debate_contribution",
                        "dimension_name": dimension.name,
                        "debate_index": debate_index,
                        "from_paradigm_perspective": True
                    }
                    
                    # Process asynchronously
                    asyncio.create_task(agent.process_task(task_data))
        
        # Schedule debate conclusion
        asyncio.create_task(self._schedule_foundation_debate_conclusion())
    
    @handle_async_errors
    async def _schedule_foundation_debate_conclusion(self) -> None:
        """Schedule the conclusion of foundation debates after a delay."""
        # Wait for agents to contribute (simulated time for debate)
        await asyncio.sleep(10)  # Adjust as needed
        
        # Conclude all active debates
        for i, debate in enumerate(self.repository.debates):
            if debate.status == "active":
                # Get a synthesis agent to conclude
                synthesis_agents = self.get_agents_by_type("synthesis")
                
                if synthesis_agents:
                    agent = synthesis_agents[0]
                    
                    # Create task for agent to conclude debate
                    task_data = {
                        "task_type": "conclude_foundation_debate",
                        "debate_index": i
                    }
                    
                    await agent.process_task(task_data)
        
        # Proceed to path definition phase
        await self._start_path_definition_phase()
    
    @handle_async_errors
    async def _start_path_definition_phase(self) -> None:
        """Start the path definition phase based on foundation choices."""
        self.current_phase = "path_definition"
        self.phase_status[self.current_phase] = "in_progress"
        
        logger.info("Starting path definition phase")
        
        # Get foundation choices from debates
        foundation_choices = {}
        
        for debate in self.repository.debates:
            if debate.status == "concluded" and debate.conclusion:
                # Extract dimension name from topic
                if debate.topic.startswith("Foundation choices for "):
                    dimension_name = debate.topic[len("Foundation choices for "):]
                    
                    # Extract choice from conclusion
                    foundation_choices[dimension_name] = debate.conclusion
        
        if not foundation_choices:
            logger.error("No foundation choices found from debates")
            return
        
        # Define path combinations (simplified approach)
        # In a real implementation, this would be more sophisticated
        path_definitions = []
        
        # Path 1: Default choices
        path_definitions.append({
            "name": "Primary Path",
            "description": "Path using primary foundation choices",
            "foundation_choices": foundation_choices.copy()
        })
        
        # Path 2: Alternative for first dimension
        if len(foundation_choices) >= 1:
            first_dim = list(foundation_choices.keys())[0]
            alt_choices = foundation_choices.copy()
            alt_choices[first_dim] = f"Alternative for {alt_choices[first_dim]}"
            
            path_definitions.append({
                "name": "Alternative Path 1",
                "description": f"Path with alternative choice for {first_dim}",
                "foundation_choices": alt_choices
            })
        
        # Path 3: Alternative for second dimension
        if len(foundation_choices) >= 2:
            second_dim = list(foundation_choices.keys())[1]
            alt_choices2 = foundation_choices.copy()
            alt_choices2[second_dim] = f"Alternative for {alt_choices2[second_dim]}"
            
            path_definitions.append({
                "name": "Alternative Path 2",
                "description": f"Path with alternative choice for {second_dim}",
                "foundation_choices": alt_choices2
            })
        
        # Assign paths to path exploration agents
        path_agents = self.get_agents_by_type("path")
        
        if not path_agents:
            logger.error("No path exploration agents available")
            return
        
        # Assign paths (round-robin if more paths than agents)
        for i, path_def in enumerate(path_definitions):
            agent_index = i % len(path_agents)
            agent = path_agents[agent_index]
            
            # Create path in repository
            from ideasfactory.agents.research_agents.repository import ResearchPath
            
            path = ResearchPath(
                name=path_def["name"],
                description=path_def["description"],
                foundation_choices=path_def["foundation_choices"],
                explored_by=agent.agent_id
            )
            
            await self.repository.add_research_path(path)
            
            # Assign task to agent
            path_index = len(self.repository.research_paths) - 1
            
            task_data = {
                "task_type": "explore_research_path",
                "path_index": path_index
            }
            
            # Process asynchronously
            asyncio.create_task(agent.process_task(task_data))
        
        # Continue to integration phase after paths are explored
        # In a real implementation, we would wait for path exploration to complete
        asyncio.create_task(self._schedule_integration_phase())
    
    @handle_async_errors
    async def _schedule_integration_phase(self) -> None:
        """Schedule the integration phase after path exploration."""
        # Wait for path exploration to complete (simulated)
        await asyncio.sleep(15)  # Adjust as needed
        
        # Start integration phase
        await self._start_integration_phase()
    
    @handle_async_errors
    async def _start_integration_phase(self) -> None:
        """Start the integration phase to identify cross-paradigm opportunities."""
        self.current_phase = "integration"
        self.phase_status[self.current_phase] = "in_progress"
        
        logger.info("Starting integration phase")
        
        # Assign integration tasks to integration agents
        integration_agents = self.get_agents_by_type("integration")
        
        if not integration_agents:
            logger.error("No integration agents available")
            return
        
        for agent in integration_agents:
            task_data = {
                "task_type": "identify_integration_opportunities"
            }
            
            # Process asynchronously
            asyncio.create_task(agent.process_task(task_data))
        
        # Continue to synthesis phase after integration
        asyncio.create_task(self._schedule_synthesis_phase())
    
    @handle_async_errors
    async def _schedule_synthesis_phase(self) -> None:
        """Schedule the synthesis phase after integration."""
        # Wait for integration to complete (simulated)
        await asyncio.sleep(10)  # Adjust as needed
        
        # Start synthesis phase
        await self._start_synthesis_phase()
    
    @handle_async_errors
    async def _start_synthesis_phase(self) -> None:
        """Start the synthesis phase to create the final research report."""
        self.current_phase = "synthesis"
        self.phase_status[self.current_phase] = "in_progress"
        
        logger.info("Starting synthesis phase")
        
        # Assign synthesis tasks to synthesis agents
        synthesis_agents = self.get_agents_by_type("synthesis")
        
        if not synthesis_agents:
            logger.error("No synthesis agents available")
            return
        
        for agent in synthesis_agents:
            task_data = {
                "task_type": "create_research_report"
            }
            
            # Process asynchronously
            await agent.process_task(task_data)
        
        # Mark research as complete
        self.phase_status[self.current_phase] = "completed"
        logger.info("Research workflow completed")
        
        # Save final state to session
        self.repository.save_to_session(self.session_id)