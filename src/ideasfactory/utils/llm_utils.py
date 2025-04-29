"""
LLM utility module for IdeasFactory.

This module provides utilities for interacting with language models through LiteLLM.
"""

import os
import logging
from typing import Dict, List, Any, Optional, Union, Callable
from pydantic import BaseModel, Field

import litellm
from litellm import completion

from ideasfactory.utils.error_handler import handle_errors, handle_async_errors

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(filename="./litellm_log", level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Simple cost tracking callback
def log_cost_callback(kwargs, completion_response, start_time, end_time):
    """Simple callback to log costs in a readable format"""
    try:
        response_cost = kwargs.get("response_cost", 0)
        model = kwargs.get("model", "unknown_model")
        
        # Calculate time taken in seconds, handling both float and timedelta objects
        if isinstance(end_time, float) and isinstance(start_time, float):
            time_taken = end_time - start_time
        else:
            # Convert to seconds if they're timedelta objects
            time_taken = (end_time - start_time).total_seconds()
        
        # Format in a more readable way
        logger.info(f"COST: ${response_cost:.6f} | MODEL: {model} | TIME: {time_taken:.2f}s")
    except Exception as e:
        logger.error(f"Error logging cost: {str(e)}")

# Register the cost tracking callback with LiteLLM
litellm.success_callback = [log_cost_callback]

# Default model configuration
DEFAULT_MODEL = os.environ.get("IDEASFACTORY_DEFAULT_MODEL", "gpt-4o")
DEFAULT_TEMPERATURE = float(os.environ.get("IDEASFACTORY_DEFAULT_TEMPERATURE", "0.7"))
DEFAULT_MAX_TOKENS = int(os.environ.get("IDEASFACTORY_DEFAULT_MAX_TOKENS", "4000"))


class Message(BaseModel):
    """A message in a conversation."""
    role: str = Field(..., description="Role of the message sender (e.g., 'user', 'assistant', 'system')")
    content: str = Field(..., description="Content of the message")


class LLMConfig(BaseModel):
    """Configuration for LLM requests."""
    model: str = Field(DEFAULT_MODEL, description="Model identifier")
    temperature: float = Field(DEFAULT_TEMPERATURE, description="Temperature for sampling")
    max_tokens: int = Field(DEFAULT_MAX_TOKENS, description="Maximum tokens to generate")
    streaming: bool = Field(False, description="Whether to stream the response")
    additional_params: Dict[str, Any] = Field(default_factory=dict, description="Additional parameters to pass to the LLM")


class LLMResponse(BaseModel):
    """Structured response from an LLM."""
    content: str = Field(..., description="Generated content")
    finish_reason: Optional[str] = Field(None, description="Reason for finishing")
    model: str = Field(..., description="Model used for generation")
    usage: Dict[str, int] = Field(default_factory=dict, description="Token usage information")


@handle_async_errors
async def send_prompt(
    messages: List[Message],
    config: Optional[LLMConfig] = None,
    stream_callback: Optional[Callable[[str], None]] = None
) -> LLMResponse:
    """
    Send a prompt to the language model and get a response.
    
    Args:
        messages: List of messages in the conversation
        config: LLM configuration (uses default if not provided)
        stream_callback: Callback function for streaming responses
        
    Returns:
        Structured response from the LLM
    """
    # Use default config if none provided
    if config is None:
        config = LLMConfig()
    
    # Convert messages to the format expected by LiteLLM
    litellm_messages = [{"role": msg.role, "content": msg.content} for msg in messages]
    
    try:
        # Prepare parameters
        params = {
            "model": config.model,
            "messages": litellm_messages,
            "temperature": config.temperature,
            "max_tokens": config.max_tokens,
            **config.additional_params
        }
        
        # Handle streaming if requested
        if config.streaming and stream_callback is not None:
            params["stream"] = True
            response_content = ""
            
            # Process the streaming response
            for chunk in completion(**params):
                if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                    content_chunk = chunk.choices[0].delta.content
                    response_content += content_chunk
                    stream_callback(content_chunk)
            
            # Construct a response object for streaming
            return LLMResponse(
                content=response_content,
                finish_reason="stop",  # Assuming normal completion
                model=config.model,
                usage={}  # Usage stats not available with streaming
            )
        else:
            # Non-streaming response
            response = completion(**params)
            
            # Extract the response content
            content = response.choices[0].message.content if response.choices else ""
            
            # Construct and return the response object
            return LLMResponse(
                content=content,
                finish_reason=response.choices[0].finish_reason if response.choices else None,
                model=response.model,
                usage={
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                } if hasattr(response, 'usage') else {}
            )
            
    except Exception as e:
        logger.error(f"Error sending prompt to LLM: {str(e)}")
        raise


@handle_errors
def create_system_prompt(content: str) -> Message:
    """Create a system prompt message."""
    return Message(role="system", content=content)


@handle_errors
def create_user_prompt(content: str) -> Message:
    """Create a user prompt message."""
    return Message(role="user", content=content)


@handle_errors
def create_assistant_prompt(content: str) -> Message:
    """Create an assistant prompt message."""
    return Message(role="assistant", content=content)


class PromptTemplate:
    """
    A template for generating prompts with variable substitution.
    
    Example:
        template = PromptTemplate("Hello, {name}! How can I help with {topic}?")
        prompt = template.format(name="John", topic="Python")
    """
    
    def __init__(self, template: str):
        self.template = template
    
    @handle_errors
    def format(self, **kwargs) -> str:
        """Format the template with the provided values."""
        return self.template.format(**kwargs)
    
    @handle_errors
    def create_message(self, role: str, **kwargs) -> Message:
        """Create a message with the formatted template."""
        return Message(role=role, content=self.format(**kwargs))