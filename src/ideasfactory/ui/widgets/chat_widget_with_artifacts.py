# src/ideasfactory/ui/widgets/enhanced_chat_widget.py

"""
Enhanced chat widget with support for structured information display.
"""

import logging
from typing import Optional, Dict, Any, List, Callable, Union
import asyncio

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Button, TextArea, Static, Label, RichLog, OptionList, MarkdownViewer
from textual.reactive import reactive

from ideasfactory.utils.error_handler import handle_errors, handle_async_errors

logger = logging.getLogger(__name__)

class ChatArtifact(Container):
    """Container for displaying rich artifacts in chat."""
    
    def __init__(self, artifact_type: str, content: str, **kwargs):
        """Initialize the chat artifact."""
        super().__init__(**kwargs)
        self.artifact_type = artifact_type
        self.content = content
    
    def compose(self) -> ComposeResult:
        """Create child widgets for the artifact."""
        yield Static(f"--- {self.artifact_type} ---", classes="artifact-header")
        
        if self.artifact_type == "markdown":
            yield MarkdownViewer(self.content, classes="artifact-content")
        elif self.artifact_type == "option-list":
            option_list = OptionList(classes="artifact-content")
            for option in self.content.split('\n'):
                if option.strip():
                    option_list.add_option(option.strip())
            yield option_list
        elif self.artifact_type == "table":
            # Simple table rendering
            yield Static(self.content, classes="artifact-content")
        else:
            # Default to static text
            yield Static(self.content, classes="artifact-content")

class EnhancedChatWidget(ChatWidget):
    """Enhanced chat widget with support for structured artifacts."""
    
    def __init__(self, **kwargs):
        """Initialize the enhanced chat widget."""
        super().__init__(**kwargs)
    
    @handle_async_errors
    async def add_artifact(self, artifact_type: str, content: str) -> None:
        """Add a rich artifact to the chat."""
        try:
            # Create the artifact container
            artifact = ChatArtifact(artifact_type, content)
            
            # Add it to the message list
            message_list = self.query_one("#message-list")
            message_list.mount(artifact)
            
            # Scroll to the bottom
            message_list.scroll_end()
            
        except Exception as e:
            logger.error(f"Error adding artifact to chat: {str(e)}")
    
    @handle_async_errors
    async def add_option_selection(self, title: str, options: List[str], callback: Callable[[int], None]) -> None:
        """Add an option selection widget to the chat."""
        try:
            # Create a container
            container = Container(classes="option-selection")
            
            # Add title
            container.mount(Label(title, classes="option-title"))
            
            # Add options
            option_list = OptionList(classes="option-list")
            for option in options:
                option_list.add_option(option)
            
            # Set callback for selection
            async def on_selection(event):
                if callback:
                    callback(event.option_index)
            
            option_list.on_option_list_option_selected = on_selection
            
            container.mount(option_list)
            
            # Add to message list
            message_list = self.query_one("#message-list")
            message_list.mount(container)
            
            # Scroll to the bottom
            message_list.scroll_end()
            
        except Exception as e:
            logger.error(f"Error adding option selection to chat: {str(e)}")