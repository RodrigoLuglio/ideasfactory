# app.py - Updated to include Research Team integration

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
from ideasfactory.ui.screens.prd_creation_screen import PRDCreationScreen
from ideasfactory.ui.screens.architecture_screen import ArchitectureScreen
from ideasfactory.ui.screens.architecture_foundation_selection_screen import ArchitectureFoundationSelectionScreen
from ideasfactory.ui.screens.research_screen import ResearchScreen
from ideasfactory.agents.business_analyst import BusinessAnalyst
from ideasfactory.agents.project_manager import ProjectManager
from ideasfactory.agents.architect import Architect
from ideasfactory.agents.research_team import FoundationalResearchTeam

from ideasfactory.utils.session_manager import SessionManager
from ideasfactory.utils.error_handler import handle_async_errors, safe_execute_async, handle_errors

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
        Binding(key="r", action="action_switch_to_prd_creation", description="PRD Creation"),
        Binding(key="a", action="action_switch_to_architecture", description="Architecture"),
        Binding(key="s", action="action_switch_to_research", description="Research"),
    ]
    
    def __init__(self, *args, **kwargs):
        """Initialize the application."""
        super().__init__(*args, **kwargs)
        # Use the SessionManager as the central repository for session data
        self.session_manager = SessionManager()
        
        # Create agents
        self.business_analyst = BusinessAnalyst()
        self.project_manager = ProjectManager()
        self.architect = Architect()
        self.research_team = FoundationalResearchTeam()
        
        # Initialize screens
        self.brainstorm_screen = None
        self.document_review_screen = None
        self.prd_creation_screen = None
        self.architecture_screen = None
        self.architecture_foundation_selection_screen = None
        self.research_screen = None

    # Add get_current_session method that all screens can use
    def get_current_session_id(self) -> Optional[str]:
        """Get the current session ID."""
        return self.session_manager.current_session_id
    
    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Footer()
    
    def on_mount(self) -> None:
        """Handle the app's mount event."""
        # Create screens first before installing them
        self.brainstorm_screen = BrainstormScreen()
        self.document_review_screen = DocumentReviewScreen()
        self.prd_creation_screen = PRDCreationScreen()
        self.architecture_screen = ArchitectureScreen()
        self.architecture_foundation_selection_screen = ArchitectureFoundationSelectionScreen()
        self.research_screen = ResearchScreen()
        
        # Install screens
        self.install_screen(self.brainstorm_screen, name="brainstorm_screen")
        self.install_screen(self.document_review_screen, name="document_review_screen")
        self.install_screen(self.prd_creation_screen, name="prd_creation_screen")
        self.install_screen(self.architecture_screen, name="architecture_screen")
        self.install_screen(self.architecture_foundation_selection_screen, name="architecture_foundation_selection_screen")
        self.install_screen(self.research_screen, name="research_screen")
        
        # Show the brainstorm screen by default
        self.push_screen("brainstorm_screen")

    def show_status(self, message: str, severity: str = "information") -> None:
        """Show a status message in the application."""
        self.notify(message, severity=severity)
        # You could also update a status bar or other UI element here
    
    @handle_errors
    def action_switch_to_brainstorm(self) -> None:
        """Switch to the brainstorm screen."""
        try:
            # Safely switch to screen using push_screen instead of switch_screen
            if self.screen.name != "brainstorm_screen":
                self.push_screen("brainstorm_screen")
        except Exception as e:
            logger.error(f"Error switching to brainstorm screen: {e}")
            self.notify(f"Error switching screens: {str(e)}", severity="error")
    
    @handle_errors
    def action_switch_to_document_review(self) -> None:
        """Switch to the document review screen."""
        try:
            # Safely switch to screen using push_screen instead of switch_screen
            if self.screen.name != "document_review_screen":
                self.push_screen("document_review_screen")
        except Exception as e:
            logger.error(f"Error switching to document screen: {e}")
            self.notify(f"Error switching screens: {str(e)}", severity="error")
    
    @handle_errors
    def action_switch_to_prd_creation(self) -> None:
        """Switch to the PRD creation screen."""
        try:
            # Safely switch to screen using push_screen instead of switch_screen
            if self.screen.name != "prd_creation_screen":
                self.push_screen("prd_creation_screen")
        except Exception as e:
            logger.error(f"Error switching to PRD creation screen: {e}")
            self.notify(f"Error switching screens: {str(e)}", severity="error")
    
    @handle_errors
    def action_switch_to_architecture(self) -> None:
        """Switch to the architecture screen."""
        try:
            # Safely switch to screen using push_screen instead of switch_screen
            if self.screen.name != "architecture_screen":
                self.push_screen("architecture_screen")
        except Exception as e:
            logger.error(f"Error switching to architecture screen: {e}")
            self.notify(f"Error switching screens: {str(e)}", severity="error")
            
    @handle_errors
    def action_switch_to_research(self) -> None:
        """Switch to the research screen."""
        try:
            # Safely switch to screen using push_screen instead of switch_screen
            if self.screen.name != "research_screen":
                self.push_screen("research_screen")
        except Exception as e:
            logger.error(f"Error switching to research screen: {e}")
            self.notify(f"Error switching screens: {str(e)}", severity="error")
            
    @handle_errors
    def action_switch_to_foundation_selection(self) -> None:
        """Switch to the Foundation Selection screen."""
        try:
            # Safely switch to screen using push_screen
            if self.screen.name != "architecture_foundation_selection_screen":
                self.push_screen("architecture_foundation_selection_screen")
                
                # Set the session for the screen
                current_session_id = self.get_current_session_id()
                if current_session_id:
                    self.architecture_foundation_selection_screen.set_session(current_session_id)
                    
        except Exception as e:
            logger.error(f"Error switching to foundation selection screen: {e}")
            self.notify(f"Error switching screens: {str(e)}", severity="error")
    
    # Property to access current session ID
    @property
    def current_session_id(self) -> Optional[str]:
        return self.session_manager.current_session_id
    
    @handle_errors
    def set_current_session(self, session_id: str) -> None:
        """Set the current session ID."""
        if self.session_manager.set_current_session(session_id):
            # Update all screens with the session ID
            if self.brainstorm_screen:
                self.brainstorm_screen.set_session(session_id)
            if self.prd_creation_screen:
                self.prd_creation_screen.set_session(session_id)
            if self.architecture_screen:
                self.architecture_screen.set_session(session_id)
            if self.document_review_screen:
                self.document_review_screen.set_session(session_id)
            if self.research_screen:
                self.research_screen.set_session(session_id)
    
    
    @handle_async_errors
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
            next_screen="prd_creation_screen"
        )
        
        # Update workflow state in session manager
        self.session_manager.update_workflow_state(session_id, "project_vision_completed")
        
        # Switch to the document review screen
        self.action_switch_to_document_review()

    @handle_async_errors
    async def show_document_review_for_pm(self, session_id: str) -> None:
        """Show document review screen for the Project Manager document."""
        # Get the session from the Project Manager
        session = self.project_manager.sessions.get(session_id)
        if not session or not session.prd_document:
            self.notify("No PRD document available for this session", severity="error")
            return
        
        # Configure the document review screen for the PM document
        self.document_review_screen.configure_for_agent(
            document_source=DocumentSource.PROJECT_MANAGER,
            session_id=session_id,
            document_content=session.prd_document,
            document_title="Product Requirements Document",
            document_type="prd",
            revision_callback=self._pm_revision_callback,
            completion_callback=self._pm_completion_callback,
            back_screen="prd_creation_screen",
            next_screen="architecture_screen"
        )
        
        # Update workflow state in session manager
        self.session_manager.update_workflow_state(session_id, "prd_completed")
        
        # Switch to the document review screen
        self.action_switch_to_document_review()

    @handle_async_errors
    async def show_document_review_for_research_requirements(self, session_id: str) -> None:
        """Show document review screen for the Architect's research requirements document."""
        # Get the session from the Architect
        session = self.architect.sessions.get(session_id)
        if not session or not session.research_requirements:
            self.notify("No research requirements document available for this session", severity="error")
            return
        
        # Configure the document review screen for the research requirements document
        self.document_review_screen.configure_for_agent(
            document_source=DocumentSource.ARCHITECT,
            session_id=session_id,
            document_content=session.research_requirements,
            document_title="Technical Research Requirements",
            document_type="research-requirements",
            revision_callback=self._research_requirements_revision_callback,
            completion_callback=self._research_requirements_completion_callback,
            back_screen="architecture_screen",
            next_screen="research_screen"  # Go to research screen after review
        )
        
        # Update workflow state in session manager
        self.session_manager.update_workflow_state(session_id, "research_requirements_completed")
        
        # Switch to the document review screen
        self.action_switch_to_document_review()
    
    @handle_async_errors
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
        
        # Update workflow state in session manager
        self.session_manager.update_workflow_state(session_id, "architecture_document_completed")
        
        # Switch to the document review screen
        self.action_switch_to_document_review()


    @handle_async_errors
    async def _ba_revision_callback(self, session_id: str, feedback: str) -> str:
        """Callback for Business Analyst document revisions."""
        # Revise the document using the BA agent
        document = await self.business_analyst.revise_document(session_id, feedback)
        return document

    @handle_async_errors
    async def _pm_revision_callback(self, session_id: str, feedback: str) -> str:
        """Callback for Project Manager document revisions."""
        # Revise the PRD using the PM agent
        prd = await self.project_manager.revise_prd(session_id, feedback)
        return prd
    
    @handle_async_errors
    async def _research_requirements_revision_callback(self, session_id: str, feedback: str) -> str:
        """Callback for research requirements document revisions."""
        # Revise the research requirements using the Architect agent
        document = await self.architect.revise_research_requirements(session_id, feedback)
        return document
        
    @handle_async_errors
    async def _architect_revision_callback(self, session_id: str, feedback: str) -> str:
        """Callback for Architect document revisions."""
        # Revise the document using the Architect agent
        document = await self.architect.revise_document(session_id, feedback)
        return document
    
    @handle_async_errors
    async def _ba_completion_callback(self) -> None:
        """Callback when Business Analyst document is completed."""
        # Complete the BA session
        if self.current_session_id:
            await self.business_analyst.complete_session(self.current_session_id)
            self.notify("Project vision document completed", severity="success")

    @handle_async_errors
    async def _pm_completion_callback(self) -> None:
        """Callback when Project Manager document is completed."""
        # Complete the PM session
        if self.current_session_id:
            # No specific completion method for PM yet, but we could add one
            self.notify("Product Requirements Document completed", severity="success")
    
    @handle_async_errors
    async def _research_requirements_completion_callback(self) -> None:
        """Callback when Research Requirements document is completed."""
        if self.current_session_id:
            self.notify("Technical Research Requirements completed", severity="success")
            
            # Set workflow state
            self.session_manager.update_workflow_state(self.current_session_id, "research_requirements_completed")
            
            # Update research screen with the session before showing it
            if self.research_screen:
                self.research_screen.set_session(self.current_session_id)
            
            # After completing the research requirements, go to the research screen
            self.push_screen("research_screen")
    
    @handle_async_errors
    async def _architect_completion_callback(self) -> None:
        """Callback when Architect document is completed."""
        # Complete the Architect session
        if self.current_session_id:
            await self.architect.complete_session(self.current_session_id)
            self.notify("Architecture document completed", severity="success")
    
    @handle_async_errors
    async def show_document_review_for_research_report(self, session_id: str) -> None:
        """Show document review screen for the Research Team report."""
        # Use the centralized document loading utility directly (same pattern as other screens)
        from ideasfactory.utils.file_manager import load_document_content
        report_content = await load_document_content(session_id, "research-report")
        
        if not report_content:
            self.notify("No research report available for this session", severity="error")
            return
        
        # Configure the document review screen for the research report
        self.document_review_screen.configure_for_agent(
            document_source=DocumentSource.RESEARCH_TEAM,
            session_id=session_id,
            document_content=report_content,
            document_title="Multi-paradigm Research Report",
            document_type="research-report",
            revision_callback=self._research_report_revision_callback,
            completion_callback=self._research_report_completion_callback,
            back_screen="research_screen",
            next_screen="architecture_screen"  # Go back to architecture for final phase
        )
        
        # Update workflow state in session manager
        self.session_manager.update_workflow_state(session_id, "research_report_completed")
        
        # Switch to the document review screen
        self.action_switch_to_document_review()
    
    @handle_async_errors
    async def _research_report_revision_callback(self, session_id: str, feedback: str) -> str:
        """Callback for Research Team report revisions."""
        # Revise the report using the Research Team agent
        try:
            report = await self.research_team.revise_report(session_id, feedback)
            return report
        except Exception as e:
            logger.error(f"Error revising research report: {str(e)}")
            # Return the original content if revision fails
            report_path = self.session_manager.get_document(session_id, "research-report")
            if report_path:
                from ideasfactory.utils.file_manager import load_document_content
                report_content = await load_document_content(report_path)
                if report_content:
                    return report_content
            return "Error revising report"
    
    @handle_async_errors
    async def _research_report_completion_callback(self) -> None:
        """Callback when Research Team report is completed."""
        if self.current_session_id:
            try:
                await self.research_team.complete_session(self.current_session_id)
                self.notify("Research report completed", severity="success")
                
                # Update workflow state and move to architecture screen
                self.session_manager.update_workflow_state(self.current_session_id, "research_completed")
                
                # After reviewing research report, prompt to go to architecture
                self.notify("Continue to Architecture phase by pressing 'a'", severity="information")
            except Exception as e:
                logger.error(f"Error completing research session: {str(e)}")
                self.notify("Error marking research session as complete", severity="error")