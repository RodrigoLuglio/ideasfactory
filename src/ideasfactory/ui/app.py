# app.py - Updated to include Architect integration

"""
Main application for IdeasFactory.

This module defines the main Textual application for IdeasFactory.
"""

import os
import sys
import logging
from typing import Optional, Dict, Any

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer
from textual.binding import Binding
from textual.screen import Screen

from ideasfactory.ui.screens.brainstorm_screen import BrainstormScreen
from ideasfactory.ui.screens.document_review_screen import DocumentReviewScreen, DocumentSource
from ideasfactory.ui.screens.deep_reasearch_screen import DeepResearchScreen
from ideasfactory.ui.screens.architecture_screen import ArchitectureScreen
from ideasfactory.agents.business_analyst import BusinessAnalyst
from ideasfactory.agents.project_manager import ProjectManager
from ideasfactory.agents.architect import Architect

# Configure logging
logger = logging.getLogger(__name__)


class IdeasFactoryApp(App):
    """
    Main application for IdeasFactory.
    """
    
    TITLE = "IdeasFactory"
    SUB_TITLE = "Agile AI Driven Documentation for Complex Projects"
    CSS_PATH = "app.tcss"
    BINDINGS = [
        Binding(key="q", action="quit", description="Quit"),
        Binding(key="b", action="action_switch_to_brainstorm", description="Brainstorm"),
        Binding(key="d", action="action_switch_to_document_review", description="Document Review"),
        Binding(key="r", action="action_switch_to_deep_research", description="Research"),
        Binding(key="a", action="action_switch_to_architecture", description="Architecture"),
    ]
    
    def __init__(self, *args, **kwargs):
        """Initialize the application."""
        super().__init__(*args, **kwargs)
        self.current_session_id: Optional[str] = None
        self.current_project_name: Optional[str] = None
        self.current_project_vision: Optional[str] = None
        self.current_research_report: Optional[str] = None
        self.current_architecture_document: Optional[str] = None
        self.brainstorm_screen = None
        self.document_review_screen = None
        self.deep_research_screen = None
        self.architecture_screen = None
        self.business_analyst = BusinessAnalyst()
        self.project_manager = ProjectManager()
        self.architect = Architect()
        
        # Generate a session ID for the entire workflow
        import uuid
        self.current_session_id = str(uuid.uuid4())
    
    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Footer()
    
    def on_mount(self) -> None:
        """Handle the app's mount event."""
        # Create screens first before installing them
        self.brainstorm_screen = BrainstormScreen()
        self.document_review_screen = DocumentReviewScreen()
        self.deep_research_screen = DeepResearchScreen()
        self.architecture_screen = ArchitectureScreen()
        
        # Install screens
        self.install_screen(self.brainstorm_screen, name="brainstorm_screen")
        self.install_screen(self.document_review_screen, name="document_review_screen")
        self.install_screen(self.deep_research_screen, name="deep_research_screen")
        self.install_screen(self.architecture_screen, name="architecture_screen")
        
        # Show the brainstorm screen by default
        self.push_screen("brainstorm_screen")
    
    def action_switch_to_brainstorm(self) -> None:
        """Switch to the brainstorm screen."""
        try:
            # Safely switch to screen using push_screen instead of switch_screen
            if self.screen.name != "brainstorm_screen":
                self.push_screen("brainstorm_screen")
        except Exception as e:
            logger.error(f"Error switching to brainstorm screen: {e}")
    
    def action_switch_to_document_review(self) -> None:
        """Switch to the document review screen."""
        try:
            # Safely switch to screen using push_screen instead of switch_screen
            if self.screen.name != "document_review_screen":
                self.push_screen("document_review_screen")
        except Exception as e:
            logger.error(f"Error switching to document screen: {e}")
    
    def action_switch_to_deep_research(self) -> None:
        """Switch to the deep research screen."""
        try:
            # Safely switch to screen using push_screen instead of switch_screen
            if self.screen.name != "deep_research_screen":
                self.push_screen("deep_research_screen")
        except Exception as e:
            logger.error(f"Error switching to deep research screen: {e}")
    
    def action_switch_to_architecture(self) -> None:
        """Switch to the architecture screen."""
        try:
            # Safely switch to screen using push_screen instead of switch_screen
            if self.screen.name != "architecture_screen":
                self.push_screen("architecture_screen")
        except Exception as e:
            logger.error(f"Error switching to architecture screen: {e}")
    
    def set_current_session(self, session_id: str) -> None:
        """Set the current session ID."""
        self.current_session_id = session_id
        
        # Update screens with the session ID
        if self.brainstorm_screen:
            self.brainstorm_screen.set_session(session_id)
        if self.architecture_screen:
            self.architecture_screen.set_session(session_id)
    
    def set_project_vision(self, project_vision: str) -> None:
        """Set the current project vision document."""
        self.current_project_vision = project_vision
        
        # Update screens with the vision
        if self.deep_research_screen:
            self.deep_research_screen.set_project_vision(project_vision)
        if self.architecture_screen:
            self.architecture_screen.set_project_vision(project_vision)
    
    def set_research_report(self, research_report: str) -> None:
        """Set the current research report document."""
        self.current_research_report = research_report
        
        # Update the architecture screen with the research report
        if self.architecture_screen:
            self.architecture_screen.set_research_report(research_report)
    
    def set_architecture_document(self, architecture_document: str) -> None:
        """Set the current architecture document."""
        self.current_architecture_document = architecture_document
    
    async def show_document_review_for_ba(self, session_id: str) -> None:
        """Show document review screen for the Business Analyst document."""
        # Get the session from the Business Analyst
        session = self.business_analyst.sessions.get(session_id)
        if not session or not session.document:
            self.notify("No document available for this session", severity="error")
            return
        
        # Configure the document review screen for the BA document
        self.document_review_screen.configure_for_agent(
            document_source=DocumentSource.BUSINESS_ANALYST,
            session_id=session_id,
            document_content=session.document,
            document_title=session.topic,
            document_type="project-vision",
            revision_callback=self._ba_revision_callback,
            completion_callback=self._ba_completion_callback,
            back_screen="brainstorm_screen",
            next_screen="deep_research_screen"
        )
        
        # Switch to the document review screen
        self.action_switch_to_document_review()
    
    async def show_document_review_for_pm(self, session_id: str) -> None:
        """Show document review screen for the Project Manager document."""
        # Get the session from the Project Manager
        session = self.project_manager.sessions.get(session_id)
        if not session or not session.research_report:
            self.notify("No research report available for this session", severity="error")
            return
        
        # Configure the document review screen for the PM document
        self.document_review_screen.configure_for_agent(
            document_source=DocumentSource.PROJECT_MANAGER,
            session_id=session_id,
            document_content=session.research_report,
            document_title="Project Research Report",
            document_type="research-report",
            revision_callback=self._pm_revision_callback,
            completion_callback=self._pm_completion_callback,
            back_screen="deep_research_screen",
            next_screen="architecture_screen"
        )
        
        # Switch to the document review screen
        self.action_switch_to_document_review()
    
    async def show_document_review_for_architect(self, session_id: str) -> None:
        """Show document review screen for the Architect document."""
        # Get the session from the Architect
        session = self.architect.sessions.get(session_id)
        if not session or not session.architecture_document:
            self.notify("No architecture document available for this session", severity="error")
            return
        
        # Configure the document review screen for the Architect document
        self.document_review_screen.configure_for_agent(
            document_source=DocumentSource.ARCHITECT,
            session_id=session_id,
            document_content=session.architecture_document,
            document_title="Architecture Document",
            document_type="architecture",
            revision_callback=self._architect_revision_callback,
            completion_callback=self._architect_completion_callback,
            back_screen="architecture_screen",
            next_screen=None  # Product Owner screen not yet implemented
        )
        
        # Switch to the document review screen
        self.action_switch_to_document_review()
    
    async def _ba_revision_callback(self, session_id: str, feedback: str) -> str:
        """Callback for Business Analyst document revisions."""
        # Revise the document using the BA agent
        document = await self.business_analyst.revise_document(session_id, feedback)
        
        # Update the app's project vision
        self.current_project_vision = document
        
        return document
    
    async def _pm_revision_callback(self, session_id: str, feedback: str) -> str:
        """Callback for Project Manager document revisions."""
        # Revise the report using the PM agent
        report = await self.project_manager.revise_report(session_id, feedback)
        
        # Update the app's research report
        self.current_research_report = report
        
        return report
    
    async def _architect_revision_callback(self, session_id: str, feedback: str) -> str:
        """Callback for Architect document revisions."""
        # Revise the document using the Architect agent
        document = await self.architect.revise_document(session_id, feedback)
        
        # Update the app's architecture document
        self.current_architecture_document = document
        
        return document
    
    async def _ba_completion_callback(self) -> None:
        """Callback when Business Analyst document is completed."""
        # Complete the BA session
        if self.current_session_id:
            await self.business_analyst.complete_session(self.current_session_id)
    
    async def _pm_completion_callback(self) -> None:
        """Callback when Project Manager document is completed."""
        # No specific completion action required for PM yet
        pass
    
    async def _architect_completion_callback(self) -> None:
        """Callback when Architect document is completed."""
        # Complete the Architect session
        if self.current_session_id:
            await self.architect.complete_session(self.current_session_id)