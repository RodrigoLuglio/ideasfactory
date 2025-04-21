# document_review_screen.py - Generic document review screen for all agents

"""
Document review screen for IdeasFactory.

This module defines a generic Textual screen for reviewing and revising documents
from any agent in the workflow.
"""

import logging
from typing import Optional, Dict, Any, Callable, Tuple
from enum import Enum

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import (
    Header, Footer, Button, Input, Static, TextArea, Label
)
from textual.containers import Vertical, Horizontal, Container, VerticalScroll
from textual.binding import Binding

from ideasfactory.agents.business_analyst import BusinessAnalyst
from ideasfactory.agents.project_manager import ProjectManager
from ideasfactory.documents.document_manager import DocumentManager

# Configure logging
logger = logging.getLogger(__name__)


class DocumentSource(str, Enum):
    """Enum for document sources/origins."""
    BUSINESS_ANALYST = "business_analyst"
    PROJECT_MANAGER = "project_manager"
    ARCHITECT = "architect"
    PRODUCT_OWNER = "product_owner"
    STANDARDS_ENGINEER = "standards_engineer"
    SCRUM_MASTER = "scrum_master"


class DocumentReviewScreen(Screen):
    """
    Generic screen for reviewing and revising documents from any agent.
    """
    
    BINDINGS = [
        Binding(key="ctrl+r", action="revise_document", description="Revise Document"),
        Binding(key="ctrl+s", action="save_document", description="Save Document"),
        Binding(key="ctrl+b", action="back", description="Back"),
        Binding(key="ctrl+p", action="proceed", description="Proceed"),
    ]
    
    def __init__(self, *args, **kwargs):
        """Initialize the document review screen."""
        super().__init__(*args, **kwargs)
        self.business_analyst = BusinessAnalyst()
        self.project_manager = ProjectManager()
        self.document_manager = DocumentManager()
        
        # Session, document, and metadata tracking
        self.session_id: Optional[str] = None
        self.document_path: Optional[str] = None
        self.document_source: Optional[DocumentSource] = None
        self.document_type: Optional[str] = None
        self.document_title: Optional[str] = None
        self.document_content: Optional[str] = None
        self._document_version = 0
        
        # Callback functions
        self._revision_callback: Optional[Callable[[str, str], str]] = None
        self._completion_callback: Optional[Callable[[], None]] = None
        
        # Navigation info
        self._back_screen: Optional[str] = None
        self._next_screen: Optional[str] = None
        
        # Track mount state
        self._is_mounted = False
    
    def compose(self) -> ComposeResult:
        """Create child widgets for the screen."""
        yield VerticalScroll(
            Container(
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
                    Button("Back", id="back_button", variant="primary"),
                    Button("Proceed", id="proceed_button", variant="warning"),
                    id="action_container"
                ),
                id="document_container"
            ),
            id="document_scroll"
        )
    
    def on_mount(self) -> None:
        """Handle the screen's mount event."""
        self._is_mounted = True
        # Load document if we have session and document info already set
        if self.document_content:
            self._display_document()
    
    def on_screen_resume(self) -> None:
        """Handle screen being resumed."""
        # When the screen is shown again, reload the document if available
        if self.document_content:
            self._display_document()
    
    def configure_for_agent(
        self,
        document_source: DocumentSource,
        session_id: str,
        document_content: str,
        document_title: str,
        document_type: str,
        revision_callback: Callable[[str, str], str],
        completion_callback: Optional[Callable[[], None]] = None,
        back_screen: Optional[str] = None,
        next_screen: Optional[str] = None
    ) -> None:
        """
        Configure the review screen for a specific agent's document.
        
        Args:
            document_source: Source agent of the document
            session_id: Session ID for the document
            document_content: Content of the document to review
            document_title: Title of the document
            document_type: Type of document (for storage)
            revision_callback: Function to call when requesting revisions (takes session_id and feedback)
            completion_callback: Function to call when completing the review
            back_screen: Screen to return to when going back
            next_screen: Screen to go to when proceeding
        """
        self.document_source = document_source
        self.session_id = session_id
        self.document_content = document_content
        self.document_title = document_title
        self.document_type = document_type
        self._revision_callback = revision_callback
        self._completion_callback = completion_callback
        self._back_screen = back_screen
        self._next_screen = next_screen
        
        # Reset document version counter
        self._document_version = 0
        
        # Reset document path
        self.document_path = None
        
        # Update the document display if we're already mounted
        if self._is_mounted:
            self._display_document()
    
    def _display_document(self) -> None:
        """Display the current document in the UI."""
        if not self._is_mounted or not self.document_content:
            return
        
        # Update the document display
        self.query_one("#document_display").text = self.document_content
        
        # Update the header with the document title
        self.query_one("#document_header").update(f"Document Review: {self.document_title}")
        
        # Reset feedback input
        self.query_one("#feedback_input").value = ""
        
        # Update button labels based on the document source
        if self.document_source == DocumentSource.BUSINESS_ANALYST:
            self.query_one("#back_button").label = "Back to Brainstorm"
            self.query_one("#proceed_button").label = "Continue to Research"
        elif self.document_source == DocumentSource.PROJECT_MANAGER:
            self.query_one("#back_button").label = "Back to Research"
            self.query_one("#proceed_button").label = "Continue to Architecture"
        # Add more mappings for other agents as they're implemented
    
    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "revise_button":
            await self.revise_document()
        elif event.button.id == "save_button":
            await self.save_document()
        elif event.button.id == "proceed_button":
            await self.proceed()
        elif event.button.id == "back_button":
            await self.go_back()
    
    async def revise_document(self) -> None:
        """Revise the document based on feedback."""
        if not self._is_mounted or not self.session_id or not self._revision_callback:
            logger.error("Cannot revise: screen not mounted, no session, or no revision callback")
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
            # Call the appropriate revision function based on document source
            revised_content = await self._revision_callback(self.session_id, feedback)
            
            # Update the stored document content
            self.document_content = revised_content
            
            # Update the document display
            self.query_one("#document_display").text = revised_content
            
            # Clear the feedback input
            self.query_one("#feedback_input").value = ""
            
            # Increment version
            self._document_version += 1
            
            # Update status
            self.query_one("#document_status").update(f"Document updated (version {self._document_version})")
            
            # Notify success
            self.notify("Document revised successfully", severity="success")
            
            # Scroll to top of document to see changes
            document_scroll = self.query_one("#document_scroll")
            document_scroll.scroll_home(animate=False)
            
        except Exception as e:
            logger.error(f"Error revising document: {str(e)}")
            self.notify("Failed to revise document", severity="error")
            self.query_one("#document_status").update("Error during revision")
        
        finally:
            # Re-enable the revise button
            revise_button.disabled = False
    
    async def save_document(self) -> None:
        """Save the document to the file system."""
        if not self._is_mounted or not self.session_id or not self.document_content:
            logger.error("Cannot save: screen not mounted, no session, or no document content")
            return
        
        # Save the document
        if not self.document_path:
            # Create a new document
            self.document_path = self.document_manager.create_document(
                content=self.document_content,
                document_type=self.document_type,
                title=self.document_title,
                metadata={
                    "session_id": self.session_id,
                    "source": self.document_source.value if self.document_source else "unknown",
                    "version": str(self._document_version)
                }
            )
            self.notify(f"Document saved: {self.document_path}", severity="information")
        else:
            # Update the existing document
            success = self.document_manager.update_document(
                filepath=self.document_path,
                content=self.document_content,
                metadata={"version": str(self._document_version)},
                commit_message=f"Update {self.document_type}: {self.document_title}"
            )
            if success:
                self.notify(f"Document updated: {self.document_path}", severity="information")
            else:
                self.notify("Failed to update document", severity="error")
    
    async def go_back(self) -> None:
        """Go back to the previous screen."""
        if self._back_screen:
            self.app.push_screen(self._back_screen)
        else:
            # Default behavior: pop this screen to return to the previous one
            self.app.pop_screen()
    
    async def action_back(self) -> None:
        """Handle keyboard shortcut for going back."""
        await self.go_back()
    
    async def proceed(self) -> None:
        """Complete the current session and proceed to the next step."""
        if not self._is_mounted or not self.session_id:
            logger.error("Cannot proceed: screen not mounted or no session")
            return
        
        # Check if document has been saved
        if not self.document_path:
            # Document hasn't been saved yet
            self.notify("Please save the document before proceeding", severity="warning")
            return
        
        # Call the completion callback if provided
        if self._completion_callback:
            await self._completion_callback()
        
        # Navigate to the next screen if specified
        if self._next_screen:
            self.app.push_screen(self._next_screen)
        else:
            # Default behavior depends on the document source
            if self.document_source == DocumentSource.BUSINESS_ANALYST:
                self.app.action_switch_to_deep_research()
            elif self.document_source == DocumentSource.PROJECT_MANAGER:
                # This would go to the architecture screen once implemented
                self.notify("Architecture phase not yet implemented", severity="warning")
    
    async def action_proceed(self) -> None:
        """Handle keyboard shortcut for proceeding."""
        await self.proceed()