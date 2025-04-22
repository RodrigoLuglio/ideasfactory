# deep_research_screen.py - Updated to use generic document review

"""
Project Manager screen for IdeasFactory.

This module defines the Textual screen for conducting research and producing PRDs/research reports.
"""

import logging
import asyncio
from typing import Optional

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import (
    Header, Footer, Button, Static, TextArea, Label, ProgressBar, Input
)
from textual.containers import Container, VerticalScroll
from textual.binding import Binding

from ideasfactory.agents.project_manager import ProjectManager
from ideasfactory.documents.document_manager import DocumentManager

from ideasfactory.utils.session_manager import SessionManager
from ideasfactory.utils.error_handler import handle_async_errors

# Configure logging
logger = logging.getLogger(__name__)


class DeepResearchScreen(Screen):
    """
    Screen for conducting research and producing PRDs/research reports.
    """
    
    BINDINGS = [
        Binding(key="ctrl+r", action="refresh_research", description="Refresh Research"),
        Binding(key="ctrl+s", action="save_report", description="Save Report"),
        Binding(key="ctrl+b", action="back_to_document", description="Back to Document"),
    ]
    
    def __init__(self, *args, **kwargs):
        """Initialize the Project Manager screen."""
        super().__init__(*args, **kwargs)
        self.project_manager = ProjectManager()
        self.document_manager = DocumentManager()
        self.session_id: Optional[str] = None
        self.project_vision: Optional[str] = None
        self.report_path: Optional[str] = None
        
        # Track mount state
        self._is_mounted = False
        # Track research stages for progress updates
        self._research_stages = {
            "init": {"weight": 5, "status": "Initializing research session..."},
            "analyze_needs": {"weight": 15, "status": "Analyzing research needs..."},
            "search": {"weight": 30, "status": "Performing web searches..."},
            "scrape": {"weight": 20, "status": "Gathering detailed information..."},
            "categorize": {"weight": 10, "status": "Categorizing research findings..."},
            "report": {"weight": 20, "status": "Generating research report..."}
        }
        self._current_progress = 0
    
    def compose(self) -> ComposeResult:
        """Create child widgets for the screen."""
        yield VerticalScroll(
            Container(
                Label("Project Research & Analysis", id="research_header"),
                
                Container(
                    Label("Project Vision Document:", id="vision_header"),
                    TextArea(id="vision_display", classes="document", read_only=True),
                    id="vision_container"
                ),
                
                Container(
                    Label("Research Status:", id="status_header"),
                    ProgressBar(id="research_progress", total=100, show_eta=False, show_percentage=True),
                    Label("Ready to start research", id="research_status"),
                    Button("Start Research", id="start_research_button", variant="primary"),
                    id="status_container"
                ),
                
                # The results container - will be replaced with document review screen navigation
                Container(
                    Button("View Research Report", id="view_report_button", variant="success", disabled=True),
                    Button("Back to Vision", id="back_button", variant="primary"),
                    id="results_container"
                ),
                
                id="research_container"
            ),
            id="research_scroll"
        )
    
    def on_mount(self) -> None:
        """Handle the screen's mount event."""
        self._is_mounted = True
        
        # Show the progress bar but set it to 0
        progress_bar = self.query_one("#research_progress")
        progress_bar.update(progress=0)
        
        # Try to load project vision if available
        self._load_project_vision()

    async def on_screen_resume(self) -> None:
        """Handle screen being resumed."""
        # Get the current session from the session manager
        session_manager = SessionManager()
        current_session = session_manager.get_current_session()
        
        if current_session:
            session_id = current_session.id
            
            # Check if we have the project vision document path in the session
            vision_path = session_manager.get_document(session_id, "project-vision")
            
            if vision_path:
                # Load the document directly
                doc_manager = DocumentManager()
                document = doc_manager.get_document(vision_path)
                
                if document and "content" in document:
                    self.project_vision = document["content"]
                    self._load_project_vision()
                    
                    # Update UI to show we're ready for research
                    self.query_one("#research_status").update("Project vision loaded. Ready to start research.")
                    self.query_one("#start_research_button").disabled = False
                    
                    # Make the button more prominent
                    self.query_one("#start_research_button").variant = "success"
                else:
                    # Could not load document content
                    self.notify("Could not load project vision content", severity="error")
                    self._handle_missing_document()
            else:
                # Try loading from document manager by type (fallback method)
                doc_manager = DocumentManager()
                document = await doc_manager.get_latest_document_by_type("project-vision", session_id)
                
                if document and "content" in document:
                    self.project_vision = document["content"]
                    self._load_project_vision()
                    
                    # Store the path in session manager for future reference
                    if "filepath" in document:
                        session_manager.add_document(session_id, "project-vision", document["filepath"])
                    
                    # Update UI appropriately
                    self.query_one("#research_status").update("Project vision loaded. Ready to start research.")
                    self.query_one("#start_research_button").disabled = False
                else:
                    # Vision document not found
                    self._handle_missing_document()
        else:
            # No session
            self.notify("No active session found", severity="error")
            self.query_one("#research_status").update("No active session")
            self.query_one("#start_research_button").disabled = True
            
    def _handle_missing_document(self):
        """Handle the case where a required document is missing."""
        self.project_vision = None
        self._load_project_vision()
        
        # Update UI to show missing document
        self.query_one("#research_status").update("Missing required document: Project Vision")
        self.query_one("#start_research_button").disabled = True


    def set_project_vision(self, project_vision: str) -> None:
        """Set the project vision document."""
        self.project_vision = project_vision
        if self._is_mounted:
            self._load_project_vision()
    
    def _load_project_vision(self) -> None:
        """Load the project vision document."""
        # This would be loaded from the document manager
        if self.project_vision:
            self.query_one("#vision_display").text = self.project_vision
        else:
            self.query_one("#vision_display").text = "No project vision document loaded."
    
    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "start_research_button":
            await self.start_research()
        elif event.button.id == "view_report_button":
            await self.view_report()
        elif event.button.id == "back_button":
            await self.back_to_document()
    
    def _update_progress(self, stage: str, completed: bool = True) -> None:
        """Update the progress bar based on research stages."""
        if not stage in self._research_stages:
            return
            
        # Calculate the progress contribution of this stage
        stage_info = self._research_stages[stage]
        stage_weight = stage_info["weight"]
        
        # For stages in progress, add half their weight
        # For completed stages, add their full weight
        if completed:
            self._current_progress += stage_weight
        else:
            self._current_progress += stage_weight / 2
            
        # Update the progress bar
        progress_bar = self.query_one("#research_progress")
        progress_bar.update(progress=min(self._current_progress, 100))
        
        # Update the status label
        if stage_info["status"]:
            self.query_one("#research_status").update(stage_info["status"])

    @handle_async_errors
    async def start_research(self) -> None:
        """Start the research process."""
        if not self._is_mounted or not self.project_vision:
            logger.error("Screen not mounted or no project vision")
            return
        
        # Reset progress tracking
        self._current_progress = 0
        progress_bar = self.query_one("#research_progress")
        progress_bar.update(progress=0)
        
        # Disable start button
        self.query_one("#start_research_button").disabled = True
        
        try:
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
            
            # Create simple progress update function
            async def update_progress(stage, message, progress_value, completed=True):
                self.query_one("#research_status").update(message)
                progress_bar = self.query_one("#research_progress")
                progress_bar.update(progress=progress_value)
                # Force a UI refresh
                self.refresh()
                # Small pause to allow UI to update
                await asyncio.sleep(0.1)
            
            # STAGE 1: Initialize research session
            await update_progress("init", "Initializing research session...", 5)
            
            # Create the research session
            session = await self.project_manager.create_session(session_id, self.project_vision)
            self.session_id = session_id
            
            # STAGE 2: Analyze research needs
            await update_progress("analyze_needs", "Analyzing research needs...", 15)
            
            # Let's directly handle each stage without monkey patching
            search_queries = await self.project_manager._analyze_research_needs(session_id)
            
            # STAGE 3: Perform web searches
            await update_progress("search", "Performing web searches...", 30)
            
            # Simplified search process
            all_search_results = []
            for i, query in enumerate(search_queries):
                await update_progress(
                    "search", 
                    f"Searching ({i+1}/{len(search_queries)}): {query[:30]}...", 
                    30 + (i * 10 // len(search_queries))
                )
                results = await self.project_manager._perform_web_search(session_id, query)
                all_search_results.extend(results)
            
            # STAGE 4: Gather detailed information
            await update_progress("scrape", "Gathering detailed information...", 50)
            
            # STAGE 5: Generate research report
            await update_progress("report", "Generating comprehensive research report...", 75)
            
            # Conduct the actual research (this will handle the remaining steps)
            report = await self.project_manager.conduct_research(session_id)
            
            # Update UI for completion
            await update_progress("complete", "Research completed successfully!", 100)
            
            # Enable the view report button
            view_button = self.query_one("#view_report_button")
            view_button.disabled = False
            
            # Hide the start button
            self.query_one("#start_research_button").display = False
            
            # Store the session ID for later use
            self.session_id = session_id
            
            # Update the app's research report storage if applicable
            if hasattr(self.app, "set_research_report"):
                self.app.set_research_report(report)
            
            # Notify success
            self.notify("Research completed successfully", severity="success")
            
        except Exception as e:
            logger.error(f"Error during research: {e}")
            self.notify(f"Research error: {str(e)}", severity="error")
            self.query_one("#research_status").update(f"Error during research: {str(e)}")
            # Re-enable start button
            self.query_one("#start_research_button").disabled = False
    
    @handle_async_errors
    async def view_report(self) -> None:
        """View the generated research report in the document review screen."""
        if not self.session_id:
            self.notify("No research session available", severity="error")
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
    
    async def action_back_to_document(self) -> None:
        """Handle keyboard shortcut for going back to document review."""
        await self.back_to_document()