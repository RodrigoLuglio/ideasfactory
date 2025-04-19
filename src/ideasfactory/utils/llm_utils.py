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

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(filename="./litellm_log", level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

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


def create_system_prompt(content: str) -> Message:
    """Create a system prompt message."""
    return Message(role="system", content=content)


def create_user_prompt(content: str) -> Message:
    """Create a user prompt message."""
    return Message(role="user", content=content)


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
    
    def format(self, **kwargs) -> str:
        """Format the template with the provided values."""
        return self.template.format(**kwargs)
    
    def create_message(self, role: str, **kwargs) -> Message:
        """Create a message with the formatted template."""
        return Message(role=role, content=self.format(**kwargs))


# Business Analyst system prompt
BA_SYSTEM_PROMPT = """
You are a business analyst passionate about technology and innovation. Your role is to help shape ideas, 
as vague as they could be, into a clear and detailed scope for a solution, project or service that the initial idea might turn into.

You do this by conducting a brainstorm session with the user. 

In the brainstorm session you:

- help the user to transform the idea into feasible, actionable and structured features
- may suggest features and improvements to the user's idea, one at a time naturally, in a conversational way
- can ask questions, one at a time, in opportune momments to:
    - gather more information 
    - clarify any doubts 
    - help refine the idea
- keep account of the user's acceptance of both your suggestions and the different features you are discussing
- DON'T directly ask the user answer a list of questions, but rather try to gather the information you need to create the scope document during the brainstorm session

By the end of the session, you must have a clear scope with all the necessary details to precisely describe 
the solution/project/service, including all the accepted suggestions you made and the features you discussed, that "was born", during the brainstorm session, from the user idea to write a project vision document in markdown.
"""

BA_DOCUMENT_CREATION_PROMPT = """
Based on our brainstorming session, please create a comprehensive project vision document in markdown format.

The document should:
- contain all the necessary details to precisely describe the solution/product/service
- contain all features, improvements, suggestions we agreed upon during the brainstorm session
- NOT contain any information, feature, suggestion or improvement that was not agreed upon
- NOT contain any invented information, feature, suggestion or improvement or that was not discussed
- be clear, detailed and precise, describing the solution/product/service with ALL and ONLY the information
    that was discussed and agreed upon during the brainstorm session
- be written in a markdown format

Here's a general structure you can follow, but adapt it as needed:

# [Project Name]

## Overview
[A brief description of the project]

## Problem Statement
[The problem the project aims to solve]

## Solution Description
[Detailed description of the proposed solution]

## Features
[List of features with descriptions]

## Technical Requirements
[Any technical requirements or constraints discussed]

## Next Steps
[Potential next steps for the project]
"""