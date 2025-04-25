"""
Dimensional research repository for specialized research teams.

This module defines the DimensionalResearchRepository class that
serves as a shared knowledge store for all research agents.
"""

import logging
import json
from typing import Dict, List, Any, Optional, Set, TypeVar, Generic
from enum import Enum
from pathlib import Path
import asyncio
from datetime import datetime

from pydantic import BaseModel, Field

from ideasfactory.utils.error_handler import handle_errors, handle_async_errors
from ideasfactory.utils.session_manager import SessionManager


# Configure logging
logger = logging.getLogger(__name__)


class RepositoryEventType(str, Enum):
    """Types of events in the repository."""
    DIMENSION_ADDED = "dimension_added"
    DIMENSION_UPDATED = "dimension_updated"
    FOUNDATION_CHOICE_ADDED = "foundation_choice_added" 
    PATH_ADDED = "path_added"
    PATH_UPDATED = "path_updated"
    OPPORTUNITY_ADDED = "opportunity_added"
    OPPORTUNITY_UPDATED = "opportunity_updated"
    AGENT_FINDING_ADDED = "agent_finding_added"
    DEBATE_STARTED = "debate_started"
    DEBATE_CONTRIBUTION_ADDED = "debate_contribution_added"
    DEBATE_CONCLUDED = "debate_concluded"


class RepositoryEvent(BaseModel):
    """Event in the repository for notifications."""
    
    type: RepositoryEventType
    data: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.now)


class ResearchDimension(BaseModel):
    """Research dimension information."""
    
    name: str
    description: str
    research_areas: List[Dict[str, str]] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)
    foundation_impact: str = "Medium"  # "High", "Medium", "Low"
    agent_findings: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    paradigm_findings: Dict[str, List[Dict[str, Any]]] = Field(default_factory=dict)
    completed: bool = False


class FoundationChoice(BaseModel):
    """Foundation choice for a dimension."""
    
    dimension: str
    choice: str
    rationale: str
    chosen_by: str  # Agent ID
    paradigm: str  # ParadigmCategory value
    implications: List[Dict[str, str]] = Field(default_factory=list)
    score: float = 0.0


class ResearchPath(BaseModel):
    """Research path based on foundation choices."""
    
    name: str
    description: str
    foundation_choices: Dict[str, str]  # dimension -> choice
    dimensions: List[Dict[str, Any]] = Field(default_factory=list)
    technologies: List[Dict[str, Any]] = Field(default_factory=list)
    trade_offs: List[Dict[str, Any]] = Field(default_factory=list)
    characteristics: Dict[str, Any] = Field(default_factory=dict)
    overall_score: float = 0.0
    explored_by: Optional[str] = None  # Agent ID


class CrossParadigmOpportunity(BaseModel):
    """Cross-paradigm opportunity."""
    
    name: str
    description: str
    paradigm1: Dict[str, Any]
    paradigm2: Dict[str, Any]
    potential_score: float
    integration_complexity: str  # "Low", "Medium", "High"
    benefits: List[str] = Field(default_factory=list)
    challenges: List[str] = Field(default_factory=list)
    implementation_approach: str = ""
    identified_by: Optional[str] = None  # Agent ID


class DebateStatus(str, Enum):
    """Status of a debate."""
    ACTIVE = "active"
    CONCLUDED = "concluded"


class DebateContribution(BaseModel):
    """Contribution to a debate."""
    
    agent_id: str
    agent_type: str
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)
    
    
class Debate(BaseModel):
    """Structured debate among agents."""
    
    topic: str
    description: str
    status: DebateStatus = DebateStatus.ACTIVE
    contributions: List[DebateContribution] = Field(default_factory=list)
    conclusion: Optional[str] = None
    started_at: datetime = Field(default_factory=datetime.now)
    concluded_at: Optional[datetime] = None


class DimensionalResearchRepository:
    """
    Shared knowledge repository for dimensional research.
    
    This class serves as a centralized store for all research findings,
    allowing agents to share knowledge and build on each others' work.
    """
    
    _instance = None
    
    def __new__(cls):
        """Ensure singleton pattern for the repository."""
        if cls._instance is None:
            cls._instance = super(DimensionalResearchRepository, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the repository."""
        if self._initialized:
            return
        
        self._initialized = True
        self.session_manager = SessionManager()
        
        # Data structures for the repository
        self.dimensions: Dict[str, ResearchDimension] = {}
        self.foundation_choices: List[FoundationChoice] = []
        self.research_paths: List[ResearchPath] = []
        self.opportunities: List[CrossParadigmOpportunity] = []
        self.debates: List[Debate] = []
        
        # Event management
        self.event_listeners: Dict[RepositoryEventType, List[callable]] = {}
        self.event_history: List[RepositoryEvent] = []
        
        # Lock for thread safety
        self._lock = asyncio.Lock()
    
    @handle_errors
    def register_event_listener(self, event_type: RepositoryEventType, callback: callable) -> None:
        """Register a callback for a specific event type.
        
        Args:
            event_type: Type of event to listen for
            callback: Function to call when event occurs
        """
        if event_type not in self.event_listeners:
            self.event_listeners[event_type] = []
        
        self.event_listeners[event_type].append(callback)
    
    @handle_async_errors
    async def notify_event(self, event: RepositoryEvent) -> None:
        """Notify all registered listeners of an event.
        
        Args:
            event: Event that occurred
        """
        # Add to history
        self.event_history.append(event)
        
        # Notify listeners
        if event.type in self.event_listeners:
            for callback in self.event_listeners[event.type]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(event)
                    else:
                        callback(event)
                except Exception as e:
                    logger.error(f"Error in event listener: {str(e)}")
    
    @handle_async_errors
    async def add_dimension(self, dimension: ResearchDimension) -> None:
        """Add a research dimension to the repository.
        
        Args:
            dimension: Dimension to add
        """
        async with self._lock:
            self.dimensions[dimension.name] = dimension
            
            # Notify event
            await self.notify_event(RepositoryEvent(
                type=RepositoryEventType.DIMENSION_ADDED,
                data={"dimension": dimension.dict()}
            ))
    
    @handle_async_errors
    async def update_dimension(self, dimension_name: str, updates: Dict[str, Any]) -> None:
        """Update a research dimension with new information.
        
        Args:
            dimension_name: Name of dimension to update
            updates: Dictionary of fields to update
        """
        async with self._lock:
            if dimension_name not in self.dimensions:
                logger.error(f"Dimension {dimension_name} not found in repository")
                return
            
            dimension = self.dimensions[dimension_name]
            
            # Update fields
            for key, value in updates.items():
                if hasattr(dimension, key):
                    setattr(dimension, key, value)
            
            # Notify event
            await self.notify_event(RepositoryEvent(
                type=RepositoryEventType.DIMENSION_UPDATED,
                data={"dimension_name": dimension_name, "updates": updates}
            ))
    
    @handle_async_errors
    async def add_agent_finding(self, 
                               dimension_name: str, 
                               agent_id: str, 
                               finding: Dict[str, Any]) -> None:
        """Add an agent's finding about a dimension.
        
        Args:
            dimension_name: Name of dimension
            agent_id: ID of agent making the finding
            finding: Finding data
        """
        async with self._lock:
            if dimension_name not in self.dimensions:
                logger.error(f"Dimension {dimension_name} not found in repository")
                return
            
            # Add finding
            dimension = self.dimensions[dimension_name]
            dimension.agent_findings[agent_id] = finding
            
            # Notify event
            await self.notify_event(RepositoryEvent(
                type=RepositoryEventType.AGENT_FINDING_ADDED,
                data={
                    "dimension_name": dimension_name, 
                    "agent_id": agent_id,
                    "finding": finding
                }
            ))
    
    @handle_async_errors
    async def add_foundation_choice(self, choice: FoundationChoice) -> None:
        """Add a foundation choice to the repository.
        
        Args:
            choice: Foundation choice to add
        """
        async with self._lock:
            self.foundation_choices.append(choice)
            
            # Notify event
            await self.notify_event(RepositoryEvent(
                type=RepositoryEventType.FOUNDATION_CHOICE_ADDED,
                data={"choice": choice.dict()}
            ))
    
    @handle_async_errors
    async def add_research_path(self, path: ResearchPath) -> None:
        """Add a research path to the repository.
        
        Args:
            path: Research path to add
        """
        async with self._lock:
            self.research_paths.append(path)
            
            # Notify event
            await self.notify_event(RepositoryEvent(
                type=RepositoryEventType.PATH_ADDED,
                data={"path": path.dict()}
            ))
    
    @handle_async_errors
    async def update_research_path(self, path_index: int, updates: Dict[str, Any]) -> None:
        """Update a research path with new information.
        
        Args:
            path_index: Index of path to update
            updates: Dictionary of fields to update
        """
        async with self._lock:
            if path_index < 0 or path_index >= len(self.research_paths):
                logger.error(f"Path index {path_index} out of range")
                return
            
            path = self.research_paths[path_index]
            
            # Update fields
            for key, value in updates.items():
                if hasattr(path, key):
                    setattr(path, key, value)
            
            # Notify event
            await self.notify_event(RepositoryEvent(
                type=RepositoryEventType.PATH_UPDATED,
                data={"path_index": path_index, "updates": updates}
            ))
    
    @handle_async_errors
    async def add_opportunity(self, opportunity: CrossParadigmOpportunity) -> None:
        """Add a cross-paradigm opportunity to the repository.
        
        Args:
            opportunity: Opportunity to add
        """
        async with self._lock:
            self.opportunities.append(opportunity)
            
            # Notify event
            await self.notify_event(RepositoryEvent(
                type=RepositoryEventType.OPPORTUNITY_ADDED,
                data={"opportunity": opportunity.dict()}
            ))
    
    @handle_async_errors
    async def update_opportunity(self, opportunity_index: int, updates: Dict[str, Any]) -> None:
        """Update a cross-paradigm opportunity with new information.
        
        Args:
            opportunity_index: Index of opportunity to update
            updates: Dictionary of fields to update
        """
        async with self._lock:
            if opportunity_index < 0 or opportunity_index >= len(self.opportunities):
                logger.error(f"Opportunity index {opportunity_index} out of range")
                return
            
            opportunity = self.opportunities[opportunity_index]
            
            # Update fields
            for key, value in updates.items():
                if hasattr(opportunity, key):
                    setattr(opportunity, key, value)
            
            # Notify event
            await self.notify_event(RepositoryEvent(
                type=RepositoryEventType.OPPORTUNITY_UPDATED,
                data={"opportunity_index": opportunity_index, "updates": updates}
            ))
    
    @handle_async_errors
    async def start_debate(self, topic: str, description: str) -> Debate:
        """Start a new debate among agents.
        
        Args:
            topic: Topic of debate
            description: Description of the debate
            
        Returns:
            The created debate
        """
        async with self._lock:
            debate = Debate(
                topic=topic,
                description=description
            )
            
            self.debates.append(debate)
            
            # Notify event
            await self.notify_event(RepositoryEvent(
                type=RepositoryEventType.DEBATE_STARTED,
                data={"debate": debate.dict()}
            ))
            
            return debate
    
    @handle_async_errors
    async def add_debate_contribution(self, 
                                    debate_index: int, 
                                    agent_id: str,
                                    agent_type: str,
                                    content: str) -> None:
        """Add a contribution to a debate.
        
        Args:
            debate_index: Index of debate
            agent_id: ID of contributing agent
            agent_type: Type of contributing agent
            content: Content of contribution
        """
        async with self._lock:
            if debate_index < 0 or debate_index >= len(self.debates):
                logger.error(f"Debate index {debate_index} out of range")
                return
            
            debate = self.debates[debate_index]
            
            if debate.status != DebateStatus.ACTIVE:
                logger.error(f"Cannot contribute to concluded debate")
                return
            
            # Add contribution
            contribution = DebateContribution(
                agent_id=agent_id,
                agent_type=agent_type,
                content=content
            )
            
            debate.contributions.append(contribution)
            
            # Notify event
            await self.notify_event(RepositoryEvent(
                type=RepositoryEventType.DEBATE_CONTRIBUTION_ADDED,
                data={
                    "debate_index": debate_index,
                    "contribution": contribution.dict()
                }
            ))
    
    @handle_async_errors
    async def conclude_debate(self, debate_index: int, conclusion: str) -> None:
        """Conclude a debate with a final conclusion.
        
        Args:
            debate_index: Index of debate
            conclusion: Final conclusion of the debate
        """
        async with self._lock:
            if debate_index < 0 or debate_index >= len(self.debates):
                logger.error(f"Debate index {debate_index} out of range")
                return
            
            debate = self.debates[debate_index]
            
            # Update debate
            debate.status = DebateStatus.CONCLUDED
            debate.conclusion = conclusion
            debate.concluded_at = datetime.now()
            
            # Notify event
            await self.notify_event(RepositoryEvent(
                type=RepositoryEventType.DEBATE_CONCLUDED,
                data={
                    "debate_index": debate_index,
                    "conclusion": conclusion
                }
            ))
    
    @handle_errors
    def get_dimension(self, dimension_name: str) -> Optional[ResearchDimension]:
        """Get a dimension by name.
        
        Args:
            dimension_name: Name of dimension
            
        Returns:
            Dimension or None if not found
        """
        return self.dimensions.get(dimension_name)
    
    @handle_errors
    def get_foundation_dimensions(self) -> List[ResearchDimension]:
        """Get all foundation dimensions (those with no dependencies).
        
        Returns:
            List of foundation dimensions
        """
        return [dim for dim in self.dimensions.values() if not dim.dependencies]
    
    @handle_errors
    def get_dependent_dimensions(self, dimension_name: str) -> List[ResearchDimension]:
        """Get dimensions that depend on a given dimension.
        
        Args:
            dimension_name: Name of dimension
            
        Returns:
            List of dimensions that depend on the given dimension
        """
        return [
            dim for dim in self.dimensions.values() 
            if dimension_name in dim.dependencies
        ]
    
    @handle_errors
    def get_foundation_choices_for_dimension(self, dimension_name: str) -> List[FoundationChoice]:
        """Get all foundation choices for a dimension.
        
        Args:
            dimension_name: Name of dimension
            
        Returns:
            List of foundation choices for the dimension
        """
        return [
            choice for choice in self.foundation_choices 
            if choice.dimension == dimension_name
        ]
    
    @handle_errors
    def get_paths_with_foundation_choice(self, 
                                       dimension_name: str, 
                                       choice: str) -> List[ResearchPath]:
        """Get all research paths that use a specific foundation choice.
        
        Args:
            dimension_name: Name of dimension
            choice: Choice value
            
        Returns:
            List of paths using the foundation choice
        """
        return [
            path for path in self.research_paths
            if path.foundation_choices.get(dimension_name) == choice
        ]
    
    @handle_errors
    def save_to_session(self, session_id: str) -> bool:
        """Save repository state to the session.
        
        Args:
            session_id: Session ID
            
        Returns:
            True if saved successfully
        """
        try:
            # Convert to dictionaries
            repo_data = {
                "dimensions": {k: v.dict() for k, v in self.dimensions.items()},
                "foundation_choices": [c.dict() for c in self.foundation_choices],
                "research_paths": [p.dict() for p in self.research_paths],
                "opportunities": [o.dict() for o in self.opportunities],
                "debates": [d.dict() for d in self.debates]
            }
            
            # Store in session metadata
            session = self.session_manager.get_session(session_id)
            if session:
                if "metadata" not in session:
                    session["metadata"] = {}
                
                session["metadata"]["dimensional_research_repository"] = repo_data
                self.session_manager.update_session(session_id, session)
                
                logger.info(f"Saved repository to session {session_id}")
                return True
            else:
                logger.error(f"Session {session_id} not found")
                return False
                
        except Exception as e:
            logger.error(f"Error saving repository to session: {str(e)}")
            return False
    
    @handle_errors
    def load_from_session(self, session_id: str) -> bool:
        """Load repository state from the session.
        
        Args:
            session_id: Session ID
            
        Returns:
            True if loaded successfully
        """
        try:
            session = self.session_manager.get_session(session_id)
            if not session or "metadata" not in session:
                logger.info(f"No existing repository data in session {session_id}, initializing new repository")
                # Return true but with empty repository - this is initialization case
                return True
                
            metadata = session["metadata"]
            if "dimensional_research_repository" not in metadata:
                logger.info(f"No repository data in session {session_id}, initializing new repository")
                return True
                
            repo_data = metadata["dimensional_research_repository"]
            
            # Load dimensions
            self.dimensions = {}
            for name, data in repo_data.get("dimensions", {}).items():
                self.dimensions[name] = ResearchDimension(**data)
                
            # Load foundation choices
            self.foundation_choices = []
            for data in repo_data.get("foundation_choices", []):
                self.foundation_choices.append(FoundationChoice(**data))
                
            # Load research paths
            self.research_paths = []
            for data in repo_data.get("research_paths", []):
                self.research_paths.append(ResearchPath(**data))
                
            # Load opportunities
            self.opportunities = []
            for data in repo_data.get("opportunities", []):
                self.opportunities.append(CrossParadigmOpportunity(**data))
                
            # Load debates
            self.debates = []
            for data in repo_data.get("debates", []):
                self.debates.append(Debate(**data))
                
            logger.info(f"Loaded repository from session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading repository from session: {str(e)}")
            # Create a fresh repository rather than failing
            self.dimensions = {}
            self.foundation_choices = []
            self.research_paths = []
            self.opportunities = []
            self.debates = []
            return True