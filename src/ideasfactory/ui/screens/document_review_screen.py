# Updated document_review_screen.py - Fix revision flow and UI feedback

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
from textual.containers import Vertical, Horizontal, Container
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
        Binding(key="ctrl+b", action="back_to_brainstorm", description="Back to Brainstorm"),
    ]
    
    def __init__(self, *args, **kwargs):
        """Initialize the document review screen."""
        super().__init__(*args, **kwargs)
        self.business_analyst = BusinessAnalyst()
        self.document_manager = DocumentManager()
        self.session_id: Optional[str] = None
        self.document_path: Optional[str] = None
        self._document_version = 0
        
        # Track mount state
        self._is_mounted = False
    
    def compose(self) -> ComposeResult:
        """Create child widgets for the screen."""
        yield Container(
            Label("Document Review", id="document_header"),
            TextArea(id="document_display", classes="document", read_only=True),
            Label("Document is read-only. Use the feedback box below to request changes.", id="document_status"),
            Container(
                Label("Request changes to the document:", id="feedback_header"),
                Input(id="feedback_input", placeholder="Enter your feedback here..."),
                Button("Revise", id="revise_button", variant="primary"),
                id="feedback_container"
            ),
            Container(
                Button("Save Document", id="save_button", variant="success"),
                Button("Back to Brainstorm", id="back_button", variant="primary"),
                Button("Complete", id="complete_button", variant="warning"),
                id="action_container"
            ),
            id="document_container"
        )
    
    def on_mount(self) -> None:
        """Handle the screen's mount event."""
        self._is_mounted = True
        # Try to load document if session is already set
        if self.session_id:
            self._load_document_async()
    
    def on_screen_resume(self) -> None:
        """Handle screen being resumed."""
        # When the screen is shown again, reload the document
        if self.session_id:
            self._load_document_async()
    
    def _load_document_async(self) -> None:
        """Asynchronously load the document."""
        self.call_later(self._load_document)
    
    def _load_document(self) -> None:
        """Load the document for the current session."""
        if not self._is_mounted or not self.session_id:
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
        
        # Reset feedback input
        self.query_one("#feedback_input").text = ""
    
    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "revise_button":
            await self.revise_document()
        elif event.button.id == "save_button":
            await self.save_document()
        elif event.button.id == "complete_button":
            await self.complete_session()
        elif event.button.id == "back_button":
            await self.back_to_brainstorm()
    
    def set_session(self, session_id: str) -> None:
        """Set the current session ID and load the document."""
        self.session_id = session_id
        if self._is_mounted:
            self._load_document_async()
    
    async def revise_document(self) -> None:
        """Revise the document based on feedback."""
        if not self._is_mounted:
            logger.error("Screen not mounted yet")
            return
            
        if not self.session_id:
            self.notify("No active session", severity="error")
            return
        
        # Get the feedback from the input
        feedback = self.query_one("#feedback_input").value
        if not feedback:
            self.notify("Please enter feedback for revision", severity="error")
            return
        
        # Disable the revise button while processing
        revise_button = self.query_one("#revise_button")
        revise_button.disabled = True
        
        # Show processing status
        self.query_one("#document_status").update("Processing revision request...")
        
        try:
            # Revise the document
            document = await self.business_analyst.revise_document(self.session_id, feedback)
            
            # Update the document display
            self.query_one("#document_display").text = document
            
            # Clear the feedback input
            self.query_one("#feedback_input").value = ""
            
            # Increment version
            self._document_version += 1
            
            # Update status
            self.query_one("#document_status").update(f"Document updated (version {self._document_version})")
            
            # Notify success
            self.notify("Document revised successfully", severity="success")
            
        except Exception as e:
            logger.error(f"Error revising document: {e}")
            self.notify("Failed to revise document", severity="error")
            self.query_one("#document_status").update("Error during revision")
        
        finally:
            # Re-enable the revise button
            revise_button.disabled = False
    
    async def save_document(self) -> None:
        """Save the document to the file system."""
        if not self._is_mounted:
            logger.error("Screen not mounted yet")
            return
            
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
    
    async def back_to_brainstorm(self) -> None:
        """Go back to the brainstorming screen."""
        # Pop this screen to return to the previous one
        self.app.pop_screen()
    
    async def action_back_to_brainstorm(self) -> None:
        """Handle keyboard shortcut for going back to brainstorm."""
        await self.back_to_brainstorm()
    
    async def complete_session(self) -> None:
        """Complete the current session and proceed to the Project Manager screen."""
        if not self._is_mounted:
            logger.error("Screen not mounted yet")
            return
            
        if not self.session_id:
            self.notify("No active session", severity="error")
            return
        
        # Check if document has been saved
        if not self.document_path:
            # Document hasn't been saved yet
            self.notify("Please save the document before completing the session", severity="warning")
            return
        
        # Complete the session
        await self.business_analyst.complete_session(self.session_id)
        
        # Get the document content to pass to the next phase
        session = self.business_analyst.sessions.get(self.session_id)
        if session and session.document:
            # Store the document in the app
            if hasattr(self.app, "set_project_vision"):
                self.app.set_project_vision(session.document)
        
        # Notify the user
        self.notify("Project vision completed, proceeding to Research phase", severity="information")
        
        # Switch to the project manager screen
        self.app.action_switch_to_project_manager()