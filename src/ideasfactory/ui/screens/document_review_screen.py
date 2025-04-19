"""
Document review screen for IdeasFactory.

This module defines the Textual screen for reviewing and revising documents.
"""

import logging
from typing import Optional

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import (
    Header, Footer, Button, Input, Static, TextArea, Label
)
from textual.containers import Vertical, Horizontal
from textual.binding import Binding

from ideasfactory.agents.business_analyst import BusinessAnalyst
from ideasfactory.documents.document_manager import DocumentManager

# Configure logging
logger = logging.getLogger(__name__)


class DocumentReviewScreen(Screen):
    """
    Screen for reviewing and revising documents.
    """
    
    BINDINGS = [
        Binding(key="ctrl+r", action="revise_document", description="Revise Document"),
        Binding(key="ctrl+s", action="save_document", description="Save Document"),
    ]
    
    def __init__(self, *args, **kwargs):
        """Initialize the document review screen."""
        super().__init__(*args, **kwargs)
        self.business_analyst = BusinessAnalyst()
        self.document_manager = DocumentManager()
        self.session_id: Optional[str] = None
        self.document_path: Optional[str] = None
    
    def compose(self) -> ComposeResult:
        """Create child widgets for the screen."""
        yield Vertical(
            Label("Document Review", id="document_header"),
            TextArea(id="document_display", classes="document"),
            Horizontal(
                TextArea(id="feedback_input"),
                Button("Revise", id="revise_button", variant="primary"),
                id="feedback_container"
            ),
            Horizontal(
                Button("Save Document", id="save_button", variant="success"),
                Button("Complete", id="complete_button", variant="warning"),
                id="action_container"
            ),
            id="document_container"
        )
    
    def on_mount(self) -> None:
        """Handle the screen's mount event."""
        pass
    
    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "revise_button":
            await self.revise_document()
        elif event.button.id == "save_button":
            await self.save_document()
        elif event.button.id == "complete_button":
            await self.complete_session()


    def set_session(self, session_id: str) -> None:
        """Set the current session ID and load the document."""
        self.session_id = session_id
        self._load_document()
    
    async def _load_document(self) -> None:
        """Load the document for the current session."""
        if not self.session_id:
            return
        
        # Get the session from the Business Analyst
        session = self.business_analyst.sessions.get(self.session_id)
        if not session or not session.document:
            self.query_one("#document_display").text = "No document available for this session."
            return
        
        # Update the document display
        self.query_one("#document_display").text = session.document
        
        # Update the header
        self.query_one("#document_header").update(f"Document Review: {session.topic}")
    
    async def revise_document(self) -> None:
        """Revise the document based on feedback."""
        if not self.session_id:
            self.notify("No active session", severity="error")
            return
        
        # Get the feedback from the input
        feedback = self.query_one("#feedback_input").text
        if not feedback:
            self.notify("Please enter feedback for revision", severity="error")
            return
        
        # Clear the input
        self.query_one("#feedback_input").text = ""
        
        # Revise the document
        document = await self.business_analyst.revise_document(self.session_id, feedback)
        
        # Update the document display
        self.query_one("#document_display").text = document
    
    async def save_document(self) -> None:
        """Save the document to the file system."""
        if not self.session_id:
            self.notify("No active session", severity="error")
            return
        
        # Get the session from the Business Analyst
        session = self.business_analyst.sessions.get(self.session_id)
        if not session or not session.document:
            self.notify("No document available for this session", severity="error")
            return
        
        # Save the document
        if not self.document_path:
            # Create a new document
            self.document_path = self.document_manager.create_document(
                content=session.document,
                document_type="project-vision",
                title=session.topic,
                metadata={"session_id": self.session_id}
            )
            self.notify(f"Document saved: {self.document_path}", severity="information")
        else:
            # Update the existing document
            success = self.document_manager.update_document(
                filepath=self.document_path,
                content=session.document,
                commit_message=f"Update project vision: {session.topic}"
            )
            if success:
                self.notify(f"Document updated: {self.document_path}", severity="information")
            else:
                self.notify("Failed to update document", severity="error")
    
    async def complete_session(self) -> None:
        """Complete the current session."""
        if not self.session_id:
            self.notify("No active session", severity="error")
            return
        
        # Complete the session
        await self.business_analyst.complete_session(self.session_id)
        
        # Save the document if not already saved
        if not self.document_path:
            await self.save_document()
        
        # Notify the user
        self.notify("Session completed", severity="information")
        
        # Clear the session ID
        self.session_id = None
        
        # Reset the UI
        self.query_one("#document_display").text = "No active session"
        self.query_one("#document_header").update("Document Review")
        
        # Switch back to the brainstorm screen
        self.app.action_switch_to_brainstorm()