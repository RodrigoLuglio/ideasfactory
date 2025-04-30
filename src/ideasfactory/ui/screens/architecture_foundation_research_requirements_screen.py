# architecture_screen.py
"""
Foundation Research Requirements screen for IdeasFactory.

This module defines the Textual screen for architecture definition sessions.
"""

import logging
from typing import Optional, Dict, List, Any
import asyncio

from textual.app import ComposeResult
from textual.widgets import (
    Header, Footer, Button, Static, TextArea, Label, Input, RadioButton, RadioSet
)
from textual.containers import Container, VerticalScroll, Horizontal
from textual.binding import Binding

from ideasfactory.agents.architect import Architect
from ideasfactory.documents.document_manager import DocumentManager
from ideasfactory.ui.screens.document_review_screen import DocumentSource
from ideasfactory.ui.screens import BaseScreen

from ideasfactory.utils.session_manager import SessionManager
from ideasfactory.utils.error_handler import handle_async_errors

# Configure logging
logger = logging.getLogger(__name__)


class FoundationResearchRequirementsScreen(BaseScreen):
    """
    Screen for creating architecture research requirements document with the Architect agent.
    """
    
    BINDINGS = [
        Binding(key="ctrl+d", action="create_research_requirements_document", description="Create Document"),
        Binding(key="ctrl+b", action="back", description="Back"),
    ]
    
    def __init__(self, *args, **kwargs):
        """Initialize the architecture screen."""
        super().__init__(*args, **kwargs)
        self.architect = Architect()
        self.document_manager = DocumentManager()
        self.project_vision: Optional[str] = None
        self.prd_document: Optional[str] = None
        self.foundation_research_requirements: Optional[str] = None
    
    def compose(self) -> ComposeResult:
        """Create child widgets for the screen."""
    
        yield Container(
            Label("Architecture Definition", id="architecture_header"),
            
            # Documents container (for reference)
            Container(
                Button("View Project Vision", id="view_vision_button", variant="primary"),
                Button("View PRD", id="view_prd_button", variant="primary"),
                Button("Reload Documents", id="reload_documents_button", variant="default"),
                id="documents_container"
            ),
            
            # Research Requirements container
            Container(
                Label("Technical Research Requirements", id="research_requirements_header"),
                Static("Create research requirements to guide the 1st research phase.", id="research_requirements_status"),
                Button("Create Research Requirements", id="create_research_requirements_button", variant="primary"),
                Button("View Research Requirements", id="view_research_requirements_button", variant="success", disabled=True),
                id="research_requirements_container"
            ),
            
            # Action container
            Container(
                Button("Back to PRD", id="back_button", variant="warning"),
                Button("Continue to Research 1st phase", id="go_to_research_button", variant="success"),
                id="action_container"
            ),
            
            id="architecture_container"
        )
        
    def on_mount(self) -> None:
        """Handle the screen's mount event."""
        super().on_mount()  # Call base class on_mount
        
        # Disable buttons that shouldn't be clickable yet
        self.query_one("#view_research_requirements_button").disabled = True

        # Add header to clarify the 3-phases architecture workflow
        arch_header = self.query_one("#architecture_header")
        arch_header.update("Architecture Research Requirements (Three-Phase Workflow)")
        
        # Add phase labels to clarify current phase
        research_header = self.query_one("#research_requirements_header")
        research_header.update("Phase 1: Foundations Research Requirements")
        
        # Load documents if session is available
        if self.session_id:
            asyncio.create_task(self._load_session_documents())
    
    @handle_async_errors
    async def _load_session_documents(self) -> None:
        """Load documents for the current session."""
        if not self.session_id:
            return
            
        # Use the centralized document loading utility
        from ideasfactory.utils.file_manager import load_document_content
        
        # Load project vision document
        vision_content = await load_document_content(self.session_id, "project-vision")
        if vision_content:
            self.project_vision = vision_content
        
        # Load PRD document
        prd_content = await load_document_content(self.session_id, "prd")
        if prd_content:
            self.prd_document = prd_content
        
        # Load research requirements document
        foundation_research_requirements_content = await load_document_content(self.session_id, "foundation-research-requirements")
        if foundation_research_requirements_content:
            self.foundation_research_requirements = foundation_research_requirements_content
                
        # Update UI based on document availability
        if self._is_mounted:
            # Update research requirements status and buttons
            if self.prd_document:
                if self.foundation_research_requirements:
                    self.query_one("#research_requirements_status").update("Foundation research requirements document created.")
                    self.query_one("#view_research_requirements_button").disabled = False
                    self.query_one("#create_research_requirements_button").disabled = True
                else:
                    self.query_one("#research_requirements_status").update("Ready to create foundation research requirements.")
                    self.query_one("#create_research_requirements_button").disabled = False
            else:
                self.query_one("#research_requirements_status").update("PRD required to create foundation research requirements.")
                self.query_one("#create_research_requirements_button").disabled = True
            
    @handle_async_errors
    async def on_screen_resume(self) -> None:
        """Handle screen being resumed."""
        # Call the base class implementation which handles session retrieval
        await super().on_screen_resume()
        
        # If we have a session but no documents, try to load them
        if self.session_id and (not self.project_vision or not self.prd_document or not self.foundation_research_requirements):
            await self._load_session_documents()
        elif not self.session_id:
            # No session
            self.notify("No active session found", severity="error")
            self.query_one("#research_requirements_status").update("No active session")
    
    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        button_id = event.button.id
        
        if button_id == "create_research_requirements_button":
            await self.create_foundation_research_requirements()
        elif button_id == "view_research_requirements_button":
            await self.view_foundation_research_requirements()
        elif button_id == "view_vision_button":
            await self.view_project_vision()
        elif button_id == "view_prd_button":
            await self.view_prd_document()
        elif button_id == "reload_documents_button":
            await self._load_session_documents()
    
    def set_project_vision(self, project_vision: str) -> None:
        """Set the project vision document."""
        self.project_vision = project_vision

    def set_prd_document(self, prd_document: str) -> None:
        """Set the PRD document."""
        self.prd_document = prd_document
        
    def set_foundation_research_requirements(self, foundation_research_requirements: str) -> None:
        """Set the foundation research requirements document."""
        self.foundation_research_requirements = foundation_research_requirements

    @handle_async_errors
    async def create_foundation_research_requirements(self) -> None:
        """Create the foundation research requirements document."""
        if not self._is_mounted:
            return
            
        if not self.session_id:
            self.notify("No active session", severity="error")
            return
            
        if not self.prd_document:
            self.notify("PRD document is required for foundation research requirements", severity="error")
            return
        
        # Update status to show we're working
        self.query_one("#research_requirements_status").update("Creating foundation research requirements...")
        self.query_one("#create_research_requirements_button").disabled = True
        
        try:
            # Create architect session if we don't have one already
            architect_session = self.architect.sessions.get(self.session_id)
            if not architect_session:
                architect_session = await self.architect.create_session(
                    self.session_id,
                    self.project_vision,
                    self.prd_document,
                )
            else:
                # Update the session with the latest documents
                architect_session.project_vision = self.project_vision
                architect_session.prd_document = self.prd_document
            
            # Generate the research requirements
            self.foundation_research_requirements = await self.architect.create_foundation_research_requirements(self.session_id)
            
            if self.foundation_research_requirements:
                # Update UI to show success
                self.query_one("#research_requirements_status").update("Foundation research requirements document created")
                self.query_one("#view_research_requirements_button").disabled = False
                
                # Notify user
                self.notify("Foundation research requirements created successfully", severity="success")
                
                # Show the document review screen for the research requirements
                if hasattr(self.app, "show_document_review_for_foundation_research_requirements"):
                    await self.app.show_document_review_for_foundation_research_requirements(self.session_id)
            else:
                raise ValueError("Failed to create foundation research requirements document")
                
        except Exception as e:
            logger.error(f"Error creating foundation research requirements: {str(e)}")
            self.notify(f"Error creating foudnation research requirements: {str(e)}", severity="error")
            self.query_one("#research_requirements_status").update("Error creating foundation research requirements")
            self.query_one("#create_research_requirements_button").disabled = False
    
    @handle_async_errors
    async def view_foundation_research_requirements(self) -> None:
        """View the foundation research requirements document."""
        if not self.foundation_research_requirements:
            self.notify("No foundation research requirements document available", severity="error")
            return
            
        # Show the document review screen for the research requirements
        if hasattr(self.app, "show_document_review_for_foundation_research_requirements"):
            await self.app.show_document_review_for_foundation_research_requirements(self.session_id)
        else:
            self.notify("Document review not available", severity="error")
    
    @handle_async_errors
    async def view_prd_document(self) -> None:
        """View the PRD document."""
        if not self.prd_document:
            self.notify("No PRD document available", severity="error")
            return
        
        # Show the document review screen for the PRD
        if hasattr(self.app, "show_document_review_for_pm"):
            await self.app.show_document_review_for_pm(self.session_id)
        else:
            self.notify("Document review not available", severity="error")
    
    @handle_async_errors
    async def view_project_vision(self) -> None:
        """View the project vision document."""
        if not self.project_vision:
            self.notify("No project vision document available", severity="error")
            return
        
        # Use the document review screen to display the vision
        if hasattr(self.app, "document_review_screen"):
            # Configure the document review for viewing only
            self.app.document_review_screen.configure_for_agent(
                document_source=DocumentSource.BUSINESS_ANALYST,
                session_id=self.session_id,
                document_content=self.project_vision,
                document_title="Project Vision",
                document_type="project-vision",
                revision_callback=None,  # No revision for viewing only
                completion_callback=None,
                back_screen="architecture_screen",
                next_screen=None
            )
            # Show the document review screen
            self.app.push_screen("document_review_screen")
        else:
            self.notify("Document review screen not available", severity="error")
    
    async def action_create_foundation_research_requirements_document(self) -> None:
        """Handle keyboard shortcut for creating a document."""
        await self.create_foundation_research_requirements_document()
    
    async def go_back(self) -> None:
        """Go back to the previous screen."""
        # Use pop_screen to go back to the previous screen
        self.app.pop_screen()
    
    async def action_back(self) -> None:
        """Handle keyboard shortcut for going back."""
        await self.go_back()
    