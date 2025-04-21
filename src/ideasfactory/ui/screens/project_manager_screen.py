# project_manager_screen.py - Project Manager screen for IdeasFactory

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
from textual.containers import Container
from textual.binding import Binding

from ideasfactory.agents.project_manager import ProjectManager
from ideasfactory.documents.document_manager import DocumentManager

# Configure logging
logger = logging.getLogger(__name__)


class ProjectManagerScreen(Screen):
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
    
    def compose(self) -> ComposeResult:
        """Create child widgets for the screen."""
        yield Container(
            Label("Project Research & Analysis", id="research_header"),
            
            Container(
                Label("Project Vision Document:", id="vision_header"),
                TextArea(id="vision_display", classes="document", read_only=True),
                id="vision_container"
            ),
            
            Container(
                Label("Research Status:", id="status_header"),
                ProgressBar(id="research_progress", show_eta=False, show_percentage=True),
                Label("Ready to start research", id="research_status"),
                Button("Start Research", id="start_research_button", variant="primary"),
                id="status_container"
            ),
            
            Container(
                Label("Research Report:", id="report_header"),
                TextArea(id="report_display", classes="document", read_only=True),
                id="report_container"
            ),
            
            Container(
                Label("Request changes to the report:", id="feedback_header"),
                Input(id="feedback_input", placeholder="Enter your feedback here..."),
                Button("Revise Report", id="revise_button", variant="primary"),
                id="feedback_container"
            ),
            
            Container(
                Button("Save Report", id="save_button", variant="success"),
                Button("Back to Vision", id="back_button", variant="primary"),
                Button("Proceed to Architecture", id="proceed_button", variant="warning"),
                id="action_container"
            ),
            
            id="pm_container"
        )
    
    def on_mount(self) -> None:
        """Handle the screen's mount event."""
        self._is_mounted = True
        
        # Initially hide the report and feedback containers
        self.query_one("#report_container").display = False
        self.query_one("#feedback_container").display = False
        self.query_one("#proceed_button").display = False
        
        # Hide the progress bar initially
        self.query_one("#research_progress").display = False
        
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
        # For now, we'll use a placeholder mechanism
        if self.project_vision:
            self.query_one("#vision_display").text = self.project_vision
        else:
            self.query_one("#vision_display").text = "No project vision document loaded."
    
    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "start_research_button":
            await self.start_research()
        elif event.button.id == "revise_button":
            await self.revise_report()
        elif event.button.id == "save_button":
            await self.save_report()
        elif event.button.id == "back_button":
            await self.back_to_document()
        elif event.button.id == "proceed_button":
            await self.proceed_to_architecture()
    
    def set_project_vision(self, project_vision: str) -> None:
        """Set the project vision document."""
        self.project_vision = project_vision
        if self._is_mounted:
            self._load_project_vision()
    
    async def start_research(self) -> None:
        """Start the research process."""
        if not self._is_mounted or not self.project_vision:
            logger.error("Screen not mounted or no project vision")
            return
        
        # Show progress bar and update status
        progress_bar = self.query_one("#research_progress")
        progress_bar.display = True
        progress_bar.update(progress=0)
        
        self.query_one("#research_status").update("Initializing research session...")
        
        # Disable start button
        self.query_one("#start_research_button").disabled = True
        
        try:
            # Generate a session ID
            import uuid
            session_id = str(uuid.uuid4())
            
            # Create the research session
            session = await self.project_manager.create_session(session_id, self.project_vision)
            self.session_id = session_id
            
            # Update progress
            progress_bar.update(progress=20)
            self.query_one("#research_status").update("Conducting market analysis...")
            
            # Conduct research
            report = await self.project_manager.conduct_research(session_id)
            
            # Update progress
            progress_bar.update(progress=100)
            self.query_one("#research_status").update("Research completed")
            
            # Show the report and feedback containers
            self.query_one("#report_display").text = report
            self.query_one("#report_container").display = True
            self.query_one("#feedback_container").display = True
            self.query_one("#proceed_button").display = True
            
            # Hide the start button
            self.query_one("#start_research_button").display = False
            
            # Notify success
            self.notify("Research completed successfully", severity="success")
            
        except Exception as e:
            logger.error(f"Error during research: {e}")
            self.notify("Failed to complete research", severity="error")
            self.query_one("#research_status").update("Error during research")
            # Re-enable start button
            self.query_one("#start_research_button").disabled = False
        
        finally:
            # Hide progress bar after a short delay
            self.call_later(self._hide_progress_bar, delay=2)
    
    def _hide_progress_bar(self) -> None:
        """Hide the progress bar."""
        self.query_one("#research_progress").display = False
    
    async def revise_report(self) -> None:
        """Revise the research report based on feedback."""
        if not self._is_mounted or not self.session_id:
            logger.error("Screen not mounted or no active session")
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
        self.query_one("#research_status").update("Processing revision request...")
        
        try:
            # Revise the report
            report = await self.project_manager.revise_report(self.session_id, feedback)
            
            # Update the report display
            self.query_one("#report_display").text = report
            
            # Clear the feedback input
            self.query_one("#feedback_input").value = ""
            
            # Update status
            self.query_one("#research_status").update("Report updated successfully")
            
            # Notify success
            self.notify("Report revised successfully", severity="success")
            
        except Exception as e:
            logger.error(f"Error revising report: {e}")
            self.notify("Failed to revise report", severity="error")
            self.query_one("#research_status").update("Error during revision")
        
        finally:
            # Re-enable the revise button
            revise_button.disabled = False
    
    async def save_report(self) -> None:
        """Save the research report to the file system."""
        if not self._is_mounted or not self.session_id:
            logger.error("Screen not mounted or no active session")
            return
        
        # Get the session from the Project Manager
        session = self.project_manager.sessions.get(self.session_id)
        if not session or not session.research_report:
            self.notify("No report available for this session", severity="error")
            return
        
        # Save the report
        if not self.report_path:
            # Create a new document
            self.report_path = self.document_manager.create_document(
                content=session.research_report,
                document_type="research-report",
                title=f"Project Research Report",
                metadata={"session_id": self.session_id}
            )
            self.notify(f"Report saved: {self.report_path}", severity="information")
        else:
            # Update the existing document
            success = self.document_manager.update_document(
                filepath=self.report_path,
                content=session.research_report,
                commit_message="Update project research report"
            )
            if success:
                self.notify(f"Report updated: {self.report_path}", severity="information")
            else:
                self.notify("Failed to update report", severity="error")
    
    async def back_to_document(self) -> None:
        """Go back to the document review screen."""
        # Use pop_screen to go back to the previous screen
        self.app.pop_screen()
    
    async def action_back_to_document(self) -> None:
        """Handle keyboard shortcut for going back to document review."""
        await self.back_to_document()
    
    async def proceed_to_architecture(self) -> None:
        """Proceed to the architecture phase."""
        if not self._is_mounted or not self.session_id:
            logger.error("Screen not mounted or no active session")
            return
        
        # Save the report first if not already saved
        if not self.report_path:
            await self.save_report()
        
        # TODO: Switch to architecture screen (not implemented yet)
        self.notify("Architecture phase not yet implemented", severity="warning")