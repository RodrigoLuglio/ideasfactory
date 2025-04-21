# brainstorm_screen.py - Updated to use generic document review

"""
Brainstorm screen for IdeasFactory.

This module defines the Textual screen for brainstorming sessions.
"""

import logging
from typing import Optional

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import (
    Header, Footer, Button, Input, Static, TextArea, Label, Markdown
)
from textual.containers import Vertical, Horizontal, VerticalScroll, Container
from textual.binding import Binding

from ideasfactory.agents.business_analyst import BusinessAnalyst

# Configure logging
logger = logging.getLogger(__name__)

class BrainstormScreen(Screen):
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
        self.session_id: Optional[str] = None
        
        # Track mount state
        self._is_mounted = False

    def compose(self) -> ComposeResult:
        """Create child widgets for the screen."""
        # Use the Container class directly instead of relying on a generic container
        yield Container(
            Label("Start a New Brainstorming Session", id="session_header"),
            Container(
                Input(placeholder="Enter your idea topic here...", id="topic_input"),
                Button("Start Session", id="start_button", variant="primary"),
                id="start_container"
            ),
            Container(
                Label("Brainstorming Session", id="conversation_header"),
                VerticalScroll(
                    Static(id="conversation_display", classes="conversation")
                ),
                Container(
                    Input(placeholder="Type your message here...", id="message_input"),
                    Button("Send", id="send_button", variant="primary"),
                    id="message_container"
                ),
                Button("Create Document", id="create_document_button", variant="success"),
                id="conversation_container"
            ),
            id="brainstorm_container"
        )
    
    def on_mount(self) -> None:
        """Handle the screen's mount event."""
        self._is_mounted = True
        # Hide the conversation container initially
        self.query_one("#conversation_container").display = False

    async def action_start_session(self) -> None:
        """Start session action."""
        await self.start_session()
    
    async def action_send_message(self) -> None:
        """Send message action."""
        await self.send_message()
    
    async def action_create_document(self) -> None:
        """Create document action."""
        await self.create_document()

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "start_button":
            await self.start_session()
        elif event.button.id == "send_button":
            await self.send_message()
        elif event.button.id == "create_document_button":
            await self.create_document()
    
    def set_session(self, session_id: str) -> None:
        """Set the current session ID."""
        self.session_id = session_id
    
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
        
        # Use the app's session ID if available, or generate a new one
        if hasattr(self.app, "current_session_id") and self.app.current_session_id:
            session_id = self.app.current_session_id
        else:
            # Generate a session ID
            import uuid
            session_id = str(uuid.uuid4())
            
            # Update the app's current session if possible
            if hasattr(self.app, "set_current_session"):
                self.app.set_current_session(session_id)
        
        # Store the project name/topic in the app if possible
        if hasattr(self.app, "current_project_name"):
            self.app.current_project_name = topic
            
        self.session_id = session_id
        
        # Create the session
        session = await self.business_analyst.create_session(session_id, topic)
        
        # Start the brainstorming
        response = await self.business_analyst.start_brainstorming(session_id)
        
        # Update the UI
        self.query_one("#conversation_display").update(f"Topic: {topic}\n\nBA: {response}")
        
        # Show the conversation container
        self.query_one("#conversation_container").display = True
        
        # Hide the start container
        self.query_one("#start_container").display = False
        
        # Update the header
        self.query_one("#session_header").update(f"Brainstorming Session: {topic}")
    
    async def send_message(self) -> None:
        """Send a message to the Business Analyst."""
        if not self._is_mounted:
            logger.error("Screen not mounted yet")
            return
            
        if not self.session_id:
            self.notify("No active session", severity="error")
            return
        
        # Get the message from the input
        message = self.query_one("#message_input").value
        if not message:
            return
        
        # Clear the input
        self.query_one("#message_input").value = ""
        
        # Update the conversation display
        conversation = self.query_one("#conversation_display")
        current_text = conversation.renderable
        conversation.update(f"{current_text}\n\nYou: {message}")
        
        # Send the message to the Business Analyst
        response = await self.business_analyst.send_message(self.session_id, message)
        
        # Update the conversation display
        conversation = self.query_one("#conversation_display")
        current_text = conversation.renderable
        conversation.update(f"{current_text}\n\nBA: {response}")
    
    async def create_document(self) -> None:
        """Create a document from the brainstorming session."""
        if not self._is_mounted:
            logger.error("Screen not mounted yet")
            return
            
        if not self.session_id:
            self.notify("No active session", severity="error")
            return
        
        # Create the document
        document = await self.business_analyst.create_document(self.session_id)
        
        # Use the app's method to show document review for this document
        if hasattr(self.app, "show_document_review_for_ba"):
            await self.app.show_document_review_for_ba(self.session_id)
        else:
            # Fallback to old behavior
            self.app.action_switch_to_document_review()