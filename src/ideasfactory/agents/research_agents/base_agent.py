"""
Base research agent for specialized research teams.

This module defines the BaseResearchAgent class that all specialized
research agents inherit from, providing common functionality.
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional, Callable
from abc import ABC, abstractmethod
import uuid

from pydantic import BaseModel, Field

from ideasfactory.utils.error_handler import handle_errors, handle_async_errors
from ideasfactory.utils.llm_utils import generate_content
from ideasfactory.utils.session_manager import SessionManager


# Configure logging
logger = logging.getLogger(__name__)


class AgentMessage(BaseModel):
    """Message sent between agents."""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    sender_id: str
    recipient_id: Optional[str] = None  # None for broadcast
    message_type: str  # "request", "response", "broadcast", "debate"
    content: Dict[str, Any]
    timestamp: float = Field(default_factory=lambda: asyncio.get_event_loop().time())
    reply_to: Optional[str] = None  # ID of message this is replying to


class BaseResearchAgent(ABC):
    """
    Base class for all research agents in the specialized research teams.
    
    This abstract class provides common functionality for all specialized
    research agents, including communication, session management, and
    interaction with the shared knowledge repository.
    """
    
    def __init__(self, agent_id: str, coordinator: Any = None, repository: Any = None):
        """Initialize the research agent.
        
        Args:
            agent_id: Unique identifier for this agent
            coordinator: Agent coordinator for communication
            repository: Shared knowledge repository
        """
        self.agent_id = agent_id
        self.coordinator = coordinator
        self.repository = repository
        self.session_manager = SessionManager()
        self.message_queue: List[AgentMessage] = []
        self.message_handlers: Dict[str, Callable] = {}
        self.last_prompt_used: Optional[str] = None
        
    @property
    @abstractmethod
    def system_prompt(self) -> str:
        """Get the system prompt for this agent."""
        pass
        
    @property
    @abstractmethod
    def agent_type(self) -> str:
        """Get the type of this agent."""
        pass
    
    @handle_errors
    def register_message_handler(self, message_type: str, handler: Callable) -> None:
        """Register a handler for a specific message type.
        
        Args:
            message_type: Type of message to handle
            handler: Function to call when message is received
        """
        self.message_handlers[message_type] = handler
        
    @handle_async_errors
    async def send_message(self, 
                          recipient_id: Optional[str], 
                          message_type: str, 
                          content: Dict[str, Any],
                          reply_to: Optional[str] = None) -> str:
        """Send a message to another agent via the coordinator.
        
        Args:
            recipient_id: ID of recipient agent, or None for broadcast
            message_type: Type of message being sent
            content: Message content as dictionary
            reply_to: Optional ID of message this is replying to
            
        Returns:
            ID of the sent message
        """
        if self.coordinator is None:
            logger.warning(f"Agent {self.agent_id} attempted to send message without coordinator")
            return ""
            
        message = AgentMessage(
            sender_id=self.agent_id,
            recipient_id=recipient_id,
            message_type=message_type,
            content=content,
            reply_to=reply_to
        )
        
        await self.coordinator.deliver_message(message)
        return message.id
        
    @handle_async_errors
    async def receive_message(self, message: AgentMessage) -> None:
        """Receive a message from another agent.
        
        Args:
            message: Message received
        """
        logger.debug(f"Agent {self.agent_id} received message of type {message.message_type}")
        
        # Store message in queue
        self.message_queue.append(message)
        
        # Process immediately if handler exists
        if message.message_type in self.message_handlers:
            await self.message_handlers[message.message_type](message)
        else:
            logger.debug(f"No handler for message type {message.message_type}")
    
    @handle_async_errors
    async def process_message_queue(self) -> None:
        """Process all messages in the queue."""
        # Create a copy to avoid issues with modifying during iteration
        messages = self.message_queue.copy()
        self.message_queue = []
        
        for message in messages:
            if message.message_type in self.message_handlers:
                await self.message_handlers[message.message_type](message)
            else:
                # Put back in queue if no handler
                self.message_queue.append(message)
    
    @handle_async_errors
    async def generate_content(self, 
                              prompt: str, 
                              context: Optional[Dict[str, Any]] = None,
                              with_system_prompt: bool = True) -> str:
        """Generate content using the LLM.
        
        Args:
            prompt: Prompt for content generation
            context: Additional context to include
            with_system_prompt: Whether to include the agent's system prompt
            
        Returns:
            Generated content
        """
        # Build the effective prompt
        effective_prompt = ""
        
        if with_system_prompt:
            effective_prompt = f"{self.system_prompt}\n\n"
            
        effective_prompt += prompt
        
        # Add context if provided
        if context:
            context_str = "\n\nContext:\n"
            for key, value in context.items():
                context_str += f"\n## {key}\n{value}\n"
            effective_prompt += context_str
            
        # Store for debugging
        self.last_prompt_used = effective_prompt
        
        # Generate content
        try:
            content = await generate_content(effective_prompt)
            return content
        except Exception as e:
            logger.error(f"Error generating content: {str(e)}")
            return f"Error generating content: {str(e)}"
    
    @abstractmethod
    async def initialize(self, session_id: str) -> bool:
        """Initialize the agent with session context.
        
        Args:
            session_id: Session ID to initialize with
            
        Returns:
            True if initialization successful
        """
        pass
    
    @abstractmethod
    async def process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a research task.
        
        Args:
            task_data: Task data including type and parameters
            
        Returns:
            Task results
        """
        pass