# deep_research_screen.py - Updated to use generic document review

"""
Project Manager screen for IdeasFactory.

This module defines the Textual screen for conducting research and producing PRDs/research reports.
"""

import logging
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

    def on_screen_resume(self) -> None:
        """Handle screen being resumed."""
        # When the screen is shown again, reload project vision if available
        if hasattr(self.app, "current_project_vision") and self.app.current_project_vision:
            self.set_project_vision(self.app.current_project_vision)
            # Show a notification that we're ready to proceed
            self.notify("Project vision loaded. Ready to conduct research.", severity="information")
            
    def set_project_vision(self, project_vision: str) -> None:
        """Set the project vision document."""
        self.project_vision = project_vision
        if self._is_mounted:
            self._load_project_vision()
            # Make the research button prominent since we have a vision document
            if hasattr(self, "start_research_button"):
                button = self.query_one("#start_research_button")
                button.variant = "success"
    
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
    
    async def start_research(self) -> None:
        """Start the research process."""
        if not self._is_mounted or not self.project_vision:
            logger.error("Screen not mounted or no project vision")
            return
        
        # Reset progress tracking
        self._current_progress = 0
        progress_bar = self.query_one("#research_progress")
        progress_bar.update(progress=0)
        
        # Update status for initial stage
        self._update_progress("init", False)
        
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
            
            # Create the research session
            session = await self.project_manager.create_session(session_id, self.project_vision)
            self.session_id = session_id
            
            # Mark initialization as complete and start analysis
            self._update_progress("init", True)
            self._update_progress("analyze_needs", False)
            
            # Hook into the research process for progress updates
            
            # Monkey patch the project manager methods to provide progress updates
            original_analyze_needs = self.project_manager._analyze_research_needs
            original_perform_search = self.project_manager._perform_web_search
            original_scrape_webpage = self.project_manager._scrape_web_page
            
            # Create wrapped methods with progress tracking
            async def wrapped_analyze_needs(*args, **kwargs):
                result = await original_analyze_needs(*args, **kwargs)
                self._update_progress("analyze_needs", True)
                self._update_progress("search", False)
                return result
                
            async def wrapped_search(*args, **kwargs):
                result = await original_perform_search(*args, **kwargs)
                self._update_progress("search", True)
                self._update_progress("scrape", False)
                return result
                
            async def wrapped_scrape(*args, **kwargs):
                result = await original_scrape_webpage(*args, **kwargs)
                # Only mark as complete after the last scrape
                return result
            
            # Apply the monkey patches
            self.project_manager._analyze_research_needs = wrapped_analyze_needs
            self.project_manager._perform_web_search = wrapped_search
            self.project_manager._scrape_web_page = wrapped_scrape
            
            # Conduct research (this will use our patched methods)
            self._update_progress("scrape", False)
            report = await self.project_manager.conduct_research(session_id)
            
            # Update for final stages
            self._update_progress("scrape", True)
            self._update_progress("categorize", True)
            self._update_progress("report", True)
            
            # Restore original methods
            self.project_manager._analyze_research_needs = original_analyze_needs
            self.project_manager._perform_web_search = original_perform_search
            self.project_manager._scrape_web_page = original_scrape_webpage
            
            # Enable the view report button
            view_button = self.query_one("#view_report_button")
            view_button.disabled = False
            
            # Hide the start button
            self.query_one("#start_research_button").display = False
            
            # Ensure progress is 100%
            progress_bar.update(progress=100)
            self.query_one("#research_status").update("Research completed")
            
            # Store the session ID for later use
            self.session_id = session_id
            
            # Update the app's research report storage
            if hasattr(self.app, "set_research_report"):
                self.app.set_research_report(report)
            
            # Notify success
            self.notify("Research completed successfully", severity="success")
            
        except Exception as e:
            logger.error(f"Error during research: {e}")
            self.notify("Failed to complete research", severity="error")
            self.query_one("#research_status").update("Error during research")
            # Re-enable start button
            self.query_one("#start_research_button").disabled = False
    
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