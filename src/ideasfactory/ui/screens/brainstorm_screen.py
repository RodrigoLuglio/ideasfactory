# brainstorm_screen.py - Updated to use enhanced ChatWidget

"""
Brainstorm screen for IdeasFactory.

This module defines the Textual screen for brainstorming sessions with an enhanced chat interface.
"""

import logging
import asyncio
from typing import Optional

from textual.app import ComposeResult
from textual.widgets import (
    Header, Footer, Button, Input, Static, TextArea, Label, Markdown
)
from textual.containers import Vertical, Horizontal, VerticalScroll, Container
from textual.binding import Binding

from ideasfactory.agents.business_analyst import BusinessAnalyst
from ideasfactory.ui.screens import BaseScreen
from ideasfactory.ui.widgets.chat_widget import ChatWidget

from ideasfactory.utils.error_handler import handle_errors, handle_async_errors
from ideasfactory.utils.session_manager import SessionManager

# Configure logging
logger = logging.getLogger(__name__)

class BrainstormScreen(BaseScreen):
    """
    Screen for conducting brainstorming sessions with the Business Analyst.
    """
    
    BINDINGS = [
        ("ctrl+s", "start_session", "Start Session"),
        ("enter", "send_message", "Send Message"),
        ("ctrl+d", "create_document", "Create Document"),
    ]
    
    def __init__(self, *args, **kwargs):
        """Initialize the brainstorm screen."""
        super().__init__(*args, **kwargs)
        self.business_analyst = BusinessAnalyst()
        self.chat_widget = None

    def compose(self) -> ComposeResult:
        """Create child widgets for the screen."""
        yield Container(
            Label("Start a New Brainstorming Session", id="session_header"),
            Container(
                Input(placeholder="Enter your idea topic here...", id="topic_input"),
                Button("Start Session", id="start_button", variant="primary"),
                id="start_container"
            ),
            # The ChatWidget will be mounted here dynamically after session starts
            id="brainstorm_container"
        )
    
    def on_mount(self) -> None:
        """Handle the screen's mount event."""
        super().on_mount()
        # No additional setup needed with the new approach
    
    async def action_start_session(self) -> None:
        """Start session action."""
        await self.start_session()
    
    async def action_send_message(self) -> None:
        """Send message action."""
        # This is now handled by the ChatWidget directly
        pass
    
    async def action_create_document(self) -> None:
        """Create document action."""
        await self.create_document()

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "start_button":
            await self.start_session()
    
    async def _load_session_documents(self) -> None:
        """
        Load documents for the current session.
        
        For brainstorm screen, we don't need to load documents automatically.
        """
        pass
    
    @handle_async_errors
    async def start_session(self) -> None:
        """Start a new brainstorming session."""
        if not self._is_mounted:
            logger.error("Screen not mounted yet")
            return
            
        # Get the topic from the input
        topic = self.query_one("#topic_input").value
        if not topic:
            # Show an error message
            self.notify("Please enter a topic for the brainstorming session", severity="error")
            return
        
        # Create a session through the session manager
        session_id = self.session_manager.create_session(topic)
        self.session_id = session_id
        
        # Update the app's current session if possible
        if hasattr(self.app, "set_current_session"):
            self.app.set_current_session(session_id)
        
        # Create the session
        session = await self.business_analyst.create_session(session_id, topic)
        
        # Hide the start container
        self.query_one("#start_container").display = False
        
        # Update the header
        self.query_one("#session_header").update(f"Brainstorming Session")
        
        # Create and mount the chat widget
        self.chat_widget = ChatWidget(
            title=f"Brainstorming: {topic}",
            on_message_callback=self.handle_chat_message
        )
        self.query_one("#brainstorm_container").mount(self.chat_widget)
        
        # Start the brainstorming in the background to avoid blocking
        asyncio.create_task(self.initialize_brainstorming(session_id))
    
    @handle_async_errors
    async def initialize_brainstorming(self, session_id: str) -> None:
        """Start the brainstorming in the background to avoid blocking."""
        # Small delay to ensure chat widget is fully mounted
        await asyncio.sleep(0.2)
        
        # Add document creation button
        if self.chat_widget:
            self.chat_widget.add_action_button(
                label="Create Project Vision Document", 
                id="create_document_button", 
                variant="success",
                callback=self.create_document
            )
        
        # Start the brainstorming
        response = await self.business_analyst.start_brainstorming(session_id)
        
        # Add the initial agent message
        if response and self.chat_widget:
            await self.chat_widget.add_message(response, is_user=False)
    
    @handle_async_errors
    async def handle_chat_message(self, message: str) -> None:
        """Handle messages from the chat widget."""
        if not self.session_id:
            self.notify("No active session", severity="error")
            return
        
        # Send the message to the Business Analyst
        response = await self.business_analyst.send_message(self.session_id, message)
        
        # Add the agent's response to the chat
        if response and self.chat_widget:
            await self.chat_widget.add_message(response, is_user=False)
    
    @handle_async_errors
    async def create_document(self) -> None:
        """Create a document from the brainstorming session."""
        if not self._is_mounted or not self.session_id:
            logger.error("Cannot create document: not mounted or no session")
            return
        
        # Show creating message in the chat if we have a chat widget
        if self.chat_widget:
            await self.chat_widget.add_message("Creating document from our conversation...", is_user=False)
        
        # Create the document
        document = await self.business_analyst.create_document(self.session_id)
        
        # Use the app's method to show document review for this document
        if hasattr(self.app, "show_document_review_for_ba"):
            await self.app.show_document_review_for_ba(self.session_id)
        else:
            # Fallback to old behavior
            self.app.action_switch_to_document_review()