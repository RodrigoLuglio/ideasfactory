# deep_research_screen.py - Renamed from deep_research_screen.py to prd_creation_screen.py

"""
Product Manager screen for IdeasFactory.

This module defines the Textual screen for creating Product Requirements Documents (PRDs).
"""

import logging
import asyncio
from typing import Optional

from textual.app import ComposeResult
from textual.widgets import (
    Header, Footer, Button, Static, TextArea, Label, ProgressBar, Input
)
from textual.containers import Container, VerticalScroll
from textual.binding import Binding

from ideasfactory.agents.project_manager import ProjectManager
from ideasfactory.documents.document_manager import DocumentManager
from ideasfactory.ui.screens import BaseScreen

from ideasfactory.utils.session_manager import SessionManager
from ideasfactory.utils.error_handler import handle_async_errors

# Configure logging
logger = logging.getLogger(__name__)


class PRDCreationScreen(BaseScreen):
    """
    Screen for creating Product Requirements Documents (PRDs).
    """
    
    BINDINGS = [
        Binding(key="ctrl+r", action="refresh_prd", description="Refresh PRD"),
        Binding(key="ctrl+s", action="save_prd", description="Save PRD"),
        Binding(key="ctrl+b", action="back_to_document", description="Back to Document"),
    ]
    
    def __init__(self, *args, **kwargs):
        """Initialize the Product Manager screen."""
        super().__init__(*args, **kwargs)
        self.project_manager = ProjectManager()
        self.document_manager = DocumentManager()
        self.project_vision: Optional[str] = None
        self.prd_path: Optional[str] = None
        
        # Track PRD creation stages for progress updates
        self._prd_stages = {
            "init": {"weight": 10, "status": "Initializing PRD session..."},
            "analyze_vision": {"weight": 25, "status": "Analyzing project vision..."},
            "identify_requirements": {"weight": 30, "status": "Identifying requirements..."},
            "structure_document": {"weight": 15, "status": "Structuring PRD document..."},
            "generate_prd": {"weight": 20, "status": "Generating PRD document..."}
        }
        self._current_progress = 0
    
    def compose(self) -> ComposeResult:
        """Create child widgets for the screen."""
        
        yield Container(
            Label("Product Requirements Document Creation", id="prd_header"),
            
            Container(
                Label("Project Vision Document:", id="vision_header"),
                TextArea(id="vision_display", classes="document", read_only=True),
                id="vision_container"
            ),
            
            Container(
                # Label("PRD Creation Status:", id="status_header"),
                Label("Ready to create PRD", id="prd_status"),
                Button("Create PRD", id="create_prd_button", variant="primary"),
                id="status_container"
            ),
            
            Container(
                Button("Back to Vision", id="back_button", variant="error"),
                Button("View PRD Document", id="view_prd_button", variant="success", disabled=True),
                id="results_container"
            ),
            id="prd_container"
        )
        
    
        
    
    def on_mount(self) -> None:
        """Handle the screen's mount event."""
        super().on_mount()
        
        # Load project vision if already available
        if self.project_vision:
            self._load_project_vision()
        elif self.session_id:
            # If we have a session but no vision loaded yet, create a task to load it
            asyncio.create_task(self._load_session_documents())

    @handle_async_errors
    async def _load_session_documents(self) -> None:
        """Load documents for the current session."""
        if not self.session_id:
            logger.error("Cannot load documents - no session ID")
            return
            
        # Use the centralized document loading utility
        from ideasfactory.utils.file_manager import load_document_content
        vision_content = await load_document_content(self.session_id, "project-vision")
        
        if vision_content:
            # Store the vision and load it into the UI
            self.project_vision = vision_content
            self._load_project_vision()
            
            # Enable PRD creation button
            self.query_one("#prd_status").update("Project vision loaded. Ready to create PRD.")
            self.query_one("#create_prd_button").disabled = False
            self.query_one("#create_prd_button").variant = "success"
        else:
            logger.error(f"Project vision document not found for session {self.session_id}")
            # Handle missing document
            self._handle_missing_document()
    
    @handle_async_errors
    async def on_screen_resume(self) -> None:
        """Handle screen being resumed."""
        # Call the base class implementation which handles session retrieval
        await super().on_screen_resume()
        
        # We have a session, try to load the document if not already loaded
        if self.session_id and not self.project_vision:
            await self._load_session_documents()
        elif not self.session_id:
            # No session
            self.notify("No active session found", severity="error")
            self.query_one("#research_status").update("No active session")
            self.query_one("#start_research_button").disabled = True
            
    def _handle_missing_document(self):
        """Handle the case where a required document is missing."""
        self.project_vision = None
        self._load_project_vision()
        
        # Update UI to show missing document
        self.query_one("#prd_status").update("Missing required document: Project Vision")
        self.query_one("#create_prd_button").disabled = True


    def set_project_vision(self, project_vision: str) -> None:
        """Set the project vision document."""
        self.project_vision = project_vision
        if self._is_mounted:
            self._load_project_vision()
    
    def _load_project_vision(self) -> None:
        """Load the project vision document into the UI."""
        vision_area = self.query_one("#vision_display")
        if self.project_vision:
            vision_area.text = self.project_vision
        else:
            vision_area.text = "No project vision document loaded."
    
    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "create_prd_button":
            await self.create_prd()
        elif event.button.id == "view_prd_button":
            await self.view_prd()
        elif event.button.id == "back_button":
            await self.back_to_document()
    
    def _update_progress(self, stage: str, completed: bool = True) -> None:
        """Update the progress bar based on PRD creation stages."""
        if not stage in self._prd_stages:
            return
            
        # Calculate the progress contribution of this stage
        stage_info = self._prd_stages[stage]
        stage_weight = stage_info["weight"]
        
        # For stages in progress, add half their weight
        # For completed stages, add their full weight
        if completed:
            self._current_progress += stage_weight
        else:
            self._current_progress += stage_weight / 2
        
        # Update the status label
        if stage_info["status"]:
            self.query_one("#prd_status").update(stage_info["status"])

    @handle_async_errors
    async def create_prd(self) -> None:
        """Create the Product Requirements Document."""
        logger.info(f"Starting PRD creation. Screen mounted: {self._is_mounted}, Vision length: {len(self.project_vision) if self.project_vision else 0}")
        
        if not self._is_mounted:
            logger.error("Screen not mounted")
            return
            
        if not self.project_vision:
            logger.error("No project vision available")
            self.notify("Project vision document is required for PRD creation", severity="error")
            return
        
        # Reset progress tracking
        self._current_progress = 0
        
        # Update status to show we're starting
        self.query_one("#prd_status").update("Initializing PRD creation process...")
        
        # Disable create button
        self.query_one("#create_prd_button").disabled = True
        
        try:
            # Get the session ID from session manager (single source of truth)
            session_manager = SessionManager()
            current_session = session_manager.get_current_session()
            
            if current_session:
                session_id = current_session.id
                self.session_id = session_id
            else:
                # No active session - shouldn't happen but handle gracefully
                logger.error("No active session when starting PRD creation")
                self.notify("No active session found", severity="error")
                self.query_one("#create_prd_button").disabled = False
                return
            
            # Create simple progress update function
            async def update_progress(stage, message, progress_value, completed=True):
                self.query_one("#prd_status").update(message)
                # Force a UI refresh
                self.refresh()
                # Small pause to allow UI to update
                await asyncio.sleep(0.1)
            
            # STAGE 1: Initialize PRD session
            await update_progress("init", "Initializing PRD session...", 10)
            
            logger.info(f"Creating PRD session with vision of length {len(self.project_vision)} characters")
            
            try:
                # Create the PRD session
                session = await self.project_manager.create_session(session_id, self.project_vision)
                self.session_id = session_id
                logger.info(f"PRD session created: {session_id}")
                
                # STAGE 2: Analyze project vision
                await update_progress("analyze_vision", "Analyzing project vision...", 25, completed=False)
                
                # STAGE 3: Identify requirements
                await update_progress("identify_requirements", "Identifying and categorizing requirements...", 45, completed=False)
                
                # STAGE 4: Structure document
                await update_progress("structure_document", "Structuring PRD document...", 65, completed=False)
                
                # STAGE 5: Generate PRD document
                await update_progress("generate_prd", "Generating comprehensive PRD document...", 80)
                logger.info("Creating full PRD document")
                
                # Create the actual PRD document
                prd_document = await self.project_manager.create_prd(session_id)
                logger.info(f"PRD document generated with length: {len(prd_document) if prd_document else 0}")
                
            except Exception as e:
                logger.error(f"Error in PRD creation process: {str(e)}")
                raise
            
            # Update UI for completion
            await update_progress("complete", "PRD creation completed successfully!", 100)
            
            # Enable the view PRD button
            view_button = self.query_one("#view_prd_button")
            view_button.disabled = False
            
            # Hide the create button
            self.query_one("#create_prd_button").display = False
            
            # Store the session ID for later use
            self.session_id = session_id
            
            # Update the app's PRD document storage if applicable
            if hasattr(self.app, "set_prd_document"):
                self.app.set_prd_document(prd_document)
            
            # Notify success
            self.notify("PRD document created successfully", severity="success")
            
        except Exception as e:
            logger.error(f"Error during PRD creation: {e}")
            self.notify(f"PRD creation error: {str(e)}", severity="error")
            self.query_one("#prd_status").update(f"Error during PRD creation: {str(e)}")
            # Re-enable create button
            self.query_one("#create_prd_button").disabled = False
    
    @handle_async_errors
    async def view_prd(self) -> None:
        """View the generated PRD document in the document review screen."""
        if not self.session_id:
            self.notify("No PRD session available", severity="error")
            return
            
        # Use the app's method to show document review for this document
        if hasattr(self.app, "show_document_review_for_pm"):
            await self.app.show_document_review_for_pm(self.session_id)
        else:
            # Fallback - notify that this isn't implemented
            self.notify("Document review integration not implemented", severity="error")
    
    async def back_to_document(self) -> None:
        """Go back to the document review screen."""
        # Use pop_screen to go back to the previous screen
        self.app.pop_screen()
    
    async def action_refresh_prd(self) -> None:
        """Handle keyboard shortcut for refreshing the PRD."""
        # Not fully implemented yet
        self.notify("Refresh PRD not implemented", severity="warning")
    
    async def action_save_prd(self) -> None:
        """Handle keyboard shortcut for saving the PRD."""
        # Not fully implemented yet
        self.notify("Save PRD not implemented", severity="warning")
    
    async def action_back_to_document(self) -> None:
        """Handle keyboard shortcut for going back to document review."""
        await self.back_to_document()