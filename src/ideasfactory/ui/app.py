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
from ideasfactory.ui.screens.architecture_foundation_research_requirements_screen import FoundationResearchRequirementsScreen
from ideasfactory.ui.screens.architecture_foundation_selection_screen import ArchitectureFoundationSelectionScreen
from ideasfactory.ui.screens.architecture_technology_research_requirements_screen import TechnologyResearchRequirementsScreen
from ideasfactory.ui.screens.architecture_technology_selection_screen import ArchitectureTechnologySelectionScreen
from ideasfactory.ui.screens.foundation_research_screen import FoundationResearchScreen
from ideasfactory.ui.screens.technology_research_screen import TechnologyResearchScreen
from ideasfactory.agents.business_analyst import BusinessAnalyst
from ideasfactory.agents.project_manager import ProjectManager
from ideasfactory.agents.architect import Architect
from ideasfactory.agents.foundation_research_team import FoundationResearchTeam
from ideasfactory.agents.technology_research_team import TechnologyResearchTeam

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
        Binding(key="p", action="action_switch_to_prd_creation", description="PRD Creation"),
        Binding(key="w", action="action_switch_to_foundation_research_requirements", description="Foundation Research Requirements"),
        Binding(key="e", action="action_switch_to_foundation_research", description="Foundation Research"),
        Binding(key="f", action="action_switch_to_foundation_selection", description="Foundation Selection"),
        Binding(key="s", action="action_switch_to_technology_research_requirements", description="Technology Research Requirements"),
        Binding(key="d", action="action_switch_to_technology_research", description="Technology Research"),
        Binding(key="t", action="action_switch_to_technology_selection", description="Technology Selection"),
        # TODO Add screen bindings as they are created
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
        self.research_team = FoundationResearchTeam()
        self.technology_research_team = TechnologyResearchTeam()
        
        # TODO Add screens as they are created
        # Initialize screens
        self.brainstorm_screen = None
        self.document_review_screen = None
        self.prd_creation_screen = None
        self.architecture_foundation_research_requirements_screen = None
        self.foundation_research_screen = None
        self.architecture_foundation_selection_screen = None
        self.architecture_technology_research_requirements_screen = None
        self.technology_research_screen = None
        self.architecture_technology_selection_screen = None

    # Add get_current_session method that all screens can use
    def get_current_session_id(self) -> Optional[str]:
        """Get the current session ID."""
        return self.session_manager.current_session_id
    
    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Footer()
    
    # TODO Add the screens initialization as they are created
    def on_mount(self) -> None:
        """Handle the app's mount event."""
        # Create screens first before installing them
        self.brainstorm_screen = BrainstormScreen()
        self.document_review_screen = DocumentReviewScreen()
        self.prd_creation_screen = PRDCreationScreen()
        self.architecture_foundation_research_requirements_screen = FoundationResearchRequirementsScreen()
        self.foundation_research_screen = FoundationResearchScreen()
        self.architecture_foundation_selection_screen = ArchitectureFoundationSelectionScreen()
        self.architecture_technology_research_requirements_screen = TechnologyResearchRequirementsScreen()
        self.technology_research_screen = TechnologyResearchScreen()
        self.architecture_technology_selection_screen = ArchitectureTechnologySelectionScreen()
        
        # TODO Install screens as we implement them
        # Install screens
        self.install_screen(self.brainstorm_screen, name="brainstorm_screen")
        self.install_screen(self.document_review_screen, name="document_review_screen")
        self.install_screen(self.prd_creation_screen, name="prd_creation_screen")
        self.install_screen(self.architecture_foundation_research_requirements_screen, name="foundation_research_requirements_screen")
        self.install_screen(self.foundation_research_screen, name="foundation_research_screen")
        self.install_screen(self.architecture_foundation_selection_screen, name="foundation_selection_screen")
        self.install_screen(self.architecture_technology_research_requirements_screen, name="technology_research_requirements_screen")
        self.install_screen(self.technology_research_screen, name="technology_research_screen")
        self.install_screen(self.architecture_technology_selection_screen, name="technology_selection_screen")
        
        # Show the brainstorm screen by default
        self.push_screen("brainstorm_screen")

    def show_status(self, message: str, severity: str = "information") -> None:
        """Show a status message in the application."""
        self.notify(message, severity=severity)
        # You could also update a status bar or other UI element here
    
    # TODO Add actions to switch to screens as we implement them

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
    def action_switch_to_foundation_research_requirements(self) -> None:
        """Switch to the foundation research requirements screen."""
        try:
            # Safely switch to screen using push_screen instead of switch_screen
            if self.screen.name != "foundation_research_requirements_screen":
                self.push_screen("foundation_research_requirements_screen")
        except Exception as e:
            logger.error(f"Error switching to foundation_research_requirements screen: {e}")
            self.notify(f"Error switching screens: {str(e)}", severity="error")
            
    @handle_errors
    def action_switch_to_foundation_research(self) -> None:
        """Switch to the foundation research screen."""
        try:
            # Safely switch to screen using push_screen instead of switch_screen
            if self.screen.name != "foundation_research_screen":
                self.push_screen("foundation_research_screen")
        except Exception as e:
            logger.error(f"Error switching to foundation research screen: {e}")
            self.notify(f"Error switching screens: {str(e)}", severity="error")
            
    @handle_errors
    def action_switch_to_foundation_selection(self) -> None:
        """Switch to the Foundation Selection screen."""
        try:
            # Safely switch to screen using push_screen
            if self.screen.name != "foundation_selection_screen":
                self.push_screen("foundation_selection_screen")
                
                # Set the session for the screen
                current_session_id = self.get_current_session_id()
                if current_session_id:
                    self.architecture_foundation_selection_screen.set_session(current_session_id)
                    
        except Exception as e:
            logger.error(f"Error switching to foundation selection screen: {e}")
            self.notify(f"Error switching screens: {str(e)}", severity="error")
    
    @handle_errors
    def action_switch_to_technology_research_requirements(self) -> None:
        """Switch to the Technology Research Requirements screen."""
        try:
            # Safely switch to screen using push_screen
            if self.screen.name != "technology_research_requirements_screen":
                self.push_screen("technology_research_requirements_screen")
                
                # Set the session for the screen
                current_session_id = self.get_current_session_id()
                if current_session_id:
                    self.architecture_technology_research_requirements_screen.set_session(current_session_id)
                    
        except Exception as e:
            logger.error(f"Error switching to technology research requirements screen: {e}")
            self.notify(f"Error switching screens: {str(e)}", severity="error")

    @handle_errors
    def action_switch_to_technology_research(self) -> None:
        """Switch to the Technology Research screen."""
        try:
            # Safely switch to screen using push_screen
            if self.screen.name != "technology_research_screen":
                self.push_screen("technology_research_screen")
                
                # Set the session for the screen
                current_session_id = self.get_current_session_id()
                if current_session_id:
                    self.technology_research_screen.set_session(current_session_id)
                    
        except Exception as e:
            logger.error(f"Error switching to technology research screen: {e}")
            self.notify(f"Error switching screens: {str(e)}", severity="error")
    
    @handle_errors
    def action_switch_to_technology_selection(self) -> None:
        """Switch to the Technology Selection screen."""
        try:
            # Safely switch to screen using push_screen
            if self.screen.name != "technology_selection_screen":
                self.push_screen("technology_selection_screen")
                
                # Set the session for the screen
                current_session_id = self.get_current_session_id()
                if current_session_id:
                    self.architecture_technology_selection_screen.set_session(current_session_id)
                    
        except Exception as e:
            logger.error(f"Error switching to technology selection screen: {e}")
            self.notify(f"Error switching screens: {str(e)}", severity="error")


    # Property to access current session ID
    @property
    def current_session_id(self) -> Optional[str]:
        return self.session_manager.current_session_id
    

    # TODO Add the screens as we implement them
    @handle_errors
    def set_current_session(self, session_id: str) -> None:
        """Set the current session ID."""
        if self.session_manager.set_current_session(session_id):
            # Update all screens with the session ID
            if self.brainstorm_screen:
                self.brainstorm_screen.set_session(session_id)
            if self.prd_creation_screen:
                self.prd_creation_screen.set_session(session_id)
            if self.architecture_foundation_research_requirements_screen:
                self.architecture_foundation_research_requirements_screen.set_session(session_id)
            if self.document_review_screen:
                self.document_review_screen.set_session(session_id)
            if self.foundation_research_screen:
                self.foundation_research_screen.set_session(session_id)
            if self.architecture_foundation_selection_screen:
                self.architecture_foundation_selection_screen.set_session(session_id)
            if self.architecture_technology_research_requirements_screen:
                self.architecture_technology_research_requirements_screen.set_session(session_id) 
            if self.technology_research_screen:
                self.technology_research_screen.set_session(session_id)
            if self.architecture_technology_selection_screen:
                self.architecture_technology_selection_screen.set_session(session_id)
            
    
    @handle_async_errors
    async def _document_completion_handler(self, document_type: str, next_screen: str = None) -> None:
        """
        Generic handler for document completion that ensures consistent workflow transitions.
        
        Args:
            document_type: Type of document being completed
            next_screen: Screen to navigate to after completion (if not provided, determined by document type)
        """
        if not self.current_session_id:
            return
            
        try:
            # 1. Update workflow state
            state_key = f"{document_type.replace('-', '_')}_completed"
            self.session_manager.update_workflow_state(self.current_session_id, state_key)
            
            # 2. Send success notification
            document_title = document_type.replace('-', ' ').title()
            self.notify(f"{document_title} completed successfully", severity="success")
            
            # 3. Determine next screen if not provided
            if not next_screen:
                if document_type == "foundation-research-requirements":
                    next_screen = "foundation_research_screen"
                elif document_type == "generic-architecture":
                    next_screen = "technology_research_requirements_screen"
                elif document_type == "technology-research-requirements":
                    next_screen = "technology_research_screen"
                elif document_type == "foundation-research-report":
                    next_screen = "foundation_selection_screen"
                elif document_type == "technology-research-report":
                    next_screen = "technology_selection_screen"
                    
            # 4. Navigate to next screen if specified
            if next_screen:
                # Set session on the next screen
                next_screen_attr = f"{next_screen}"
                if hasattr(self, next_screen_attr):
                    screen_instance = getattr(self, next_screen_attr)
                    if hasattr(screen_instance, "set_session"):
                        screen_instance.set_session(self.current_session_id)
                
                # Navigate to next screen
                self.push_screen(next_screen)
                
                # Notify about next step
                if next_screen == "technology_research_requirements_screen":
                    self.notify("Continue to create technology research requirements", severity="information")
                    
        except Exception as e:
            logger.error(f"Error in document completion handler for {document_type}: {str(e)}")
            self.notify(f"Error completing {document_type.replace('-', ' ')}: {str(e)}", severity="error")
    
    @handle_async_errors
    async def _document_revision_handler(
        self, 
        session_id: str, 
        feedback: str,
        document_type: str,
        agent_type: str,
        revision_method: str = None
    ) -> str:
        """
        Generic handler for document revisions to ensure consistent behavior.
        
        Args:
            session_id: Current session ID
            feedback: User's feedback for the revision
            document_type: Type of document being revised
            agent_type: Type of agent handling the revision
            revision_method: Optional specific revision method to call on the agent
            
        Returns:
            Revised document content
        """
        try:
            # 1. Get the original document
            from ideasfactory.utils.file_manager import load_document_content
            original_content = await load_document_content(session_id, document_type)
            
            if not original_content:
                self.notify(f"No {document_type} document found for revision", severity="error")
                return f"Error: Original {document_type} document not found"
                
            # 2. Get the appropriate agent
            agent = None
            if agent_type == "architect":
                agent = self.architect
            elif agent_type == "foundation_research":
                agent = self.research_team
            elif agent_type == "technology_research":
                agent = self.technology_research_team
            elif agent_type == "business_analyst":
                agent = self.business_analyst
            elif agent_type == "project_manager":
                agent = self.project_manager
                
            if not agent:
                self.notify(f"Agent {agent_type} not found", severity="error")
                return original_content
                
            # 3. Document type to method mapping - default mapping when revision_method is not specified
            document_method_map = {
                # Architect document mappings
                "foundation-research-requirements": "revise_foundation_research_requirements",
                "technology-research-requirements": "revise_technology_research_requirements",
                "generic-architecture": "revise_generic_architecture_document",
                "architecture": "revise_final_architecture_document",
                
                # Research team mappings
                "foundation-research-report": "revise_report",
                "technology-research-report": "revise_report",
                
                # Business Analyst mappings
                "project-vision": "revise_document",
                
                # Project Manager mappings
                "prd": "revise_prd"
            }
            
            # 4. Call the appropriate revision method
            revised_content = original_content
            
            method_to_use = revision_method
            if not method_to_use:
                # Use the mapping if no specific method was provided
                method_to_use = document_method_map.get(document_type)
                
            if method_to_use:
                # Use the determined method if available
                if hasattr(agent, method_to_use):
                    method = getattr(agent, method_to_use)
                    logger.info(f"Using revision method '{method_to_use}' for document type: {document_type}")
                    revised_content = await method(session_id, feedback)
                else:
                    logger.warning(f"Revision method '{method_to_use}' not found on {agent_type}, falling back to generic")
                    # Fall back to revise_document
                    if hasattr(agent, "revise_document"):
                        revised_content = await agent.revise_document(session_id, feedback)
                    else:
                        self.notify(f"No revision method available for {agent_type}", severity="error")
            else:
                # No mapping found, try generic method
                logger.warning(f"No method mapping found for document type: {document_type}")
                if hasattr(agent, "revise_document"):
                    revised_content = await agent.revise_document(session_id, feedback)
                else:
                    self.notify(f"No revision method available for {agent_type}", severity="error")
            
            return revised_content
        except Exception as e:
            logger.error(f"Error revising {document_type}: {str(e)}")
            return f"Error revising document: {str(e)}"

    # -----------------------------------------------------------------------------------
    # Brainstorm
    # -----------------------------------------------------------------------------------
    
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
    async def _ba_revision_callback(self, session_id: str, feedback: str) -> str:
        """Callback for Business Analyst document revisions."""
        return await self._document_revision_handler(
            session_id=session_id,
            feedback=feedback,
            document_type="project-vision",
            agent_type="business_analyst"
        )
    
    @handle_async_errors
    async def _ba_completion_callback(self) -> None:
        """Callback when Business Analyst document is completed."""
        if self.current_session_id:
            # Complete the BA session
            await self.business_analyst.complete_session(self.current_session_id)
            await self._document_completion_handler("project-vision", "prd_creation_screen")

    # -----------------------------------------------------------------------------------
    # Project Requirements Document
    # -----------------------------------------------------------------------------------

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
            next_screen="foundation_research_requirements_screen"
        )
        
        # Update workflow state in session manager
        self.session_manager.update_workflow_state(session_id, "prd_completed")
        
        # Switch to the document review screen
        self.action_switch_to_document_review()

    @handle_async_errors
    async def _pm_revision_callback(self, session_id: str, feedback: str) -> str:
        """Callback for Project Manager document revisions."""
        return await self._document_revision_handler(
            session_id=session_id,
            feedback=feedback,
            document_type="prd",
            agent_type="project_manager"
        )

    @handle_async_errors
    async def _pm_completion_callback(self) -> None:
        """Callback when Project Manager document is completed."""
        # Complete the PM session
        if self.current_session_id:
            # No specific completion method for PM yet
            await self._document_completion_handler("prd", "foundation_research_requirements_screen")


    # -----------------------------------------------------------------------------------
    # Foundation Research Requirements
    # -----------------------------------------------------------------------------------

    @handle_async_errors
    async def show_document_review_for_foundation_research_requirements(self, session_id: str) -> None:
        """Show document review screen for the foundation research requirements document."""
        # Get the session from the Architect
        session = self.architect.sessions.get(session_id)
        if not session or not session.foundation_research_requirements:
            self.notify("No research requirements document available for this session", severity="error")
            return
        
        # Configure the document review screen for the research requirements document
        self.document_review_screen.configure_for_agent(
            document_source=DocumentSource.ARCHITECT,
            session_id=session_id,
            document_content=session.foundation_research_requirements,
            document_title="Technical Research Requirements",
            document_type="foundation-research-requirements",
            revision_callback=self._foundation_research_requirements_revision_callback,
            completion_callback=self._foundation_research_requirements_completion_callback,
            back_screen="foundation_research_requirements_screen",
            next_screen="foundation_research_screen"  # Go to research screen after review
        )
        
        # Update workflow state in session manager
        self.session_manager.update_workflow_state(session_id, "foundation_research_requirements_completed")
        
        # Switch to the document review screen
        self.action_switch_to_document_review()
    
    @handle_async_errors
    async def _foundation_research_requirements_revision_callback(self, session_id: str, feedback: str) -> str:
        """Callback for foundation research requirements document revisions."""
        return await self._document_revision_handler(
            session_id=session_id,
            feedback=feedback,
            document_type="foundation-research-requirements",
            agent_type="architect"
        )
    
    @handle_async_errors
    async def _foundation_research_requirements_completion_callback(self) -> None:
        """Callback when Foundation Research Requirements document is completed."""
        await self._document_completion_handler("foundation-research-requirements", "foundation_research_screen")
    
    # -----------------------------------------------------------------------------------
    # Foundation Research Report
    # -----------------------------------------------------------------------------------

    @handle_async_errors
    async def show_document_review_for_foundation_research_report(self, session_id: str) -> None:
        """Show document review screen for the Research Team report."""
        # Use the centralized document loading utility directly (same pattern as other screens)
        from ideasfactory.utils.file_manager import load_document_content
        report_content = await load_document_content(session_id, "foundation-research-report")
        
        if not report_content:
            self.notify("No research report available for this session", severity="error")
            return
        
        # Configure the document review screen for the research report
        self.document_review_screen.configure_for_agent(
            document_source=DocumentSource.RESEARCH_TEAM,
            session_id=session_id,
            document_content=report_content,
            document_title="Multi-paradigm Research Report",
            document_type="foundation-research-report",
            revision_callback=self._research_report_revision_callback,
            completion_callback=self._research_report_completion_callback,
            back_screen="foundation_research_screen",
            next_screen="foundation_selection_screen"  # Go back to architecture for final phase
        )
        
        # Update workflow state in session manager
        self.session_manager.update_workflow_state(session_id, "foundation_research_report_completed")
        
        # Switch to the document review screen
        self.action_switch_to_document_review()

    @handle_async_errors
    async def _research_report_revision_callback(self, session_id: str, feedback: str) -> str:
        """Callback for Research Team report revisions."""
        return await self._document_revision_handler(
            session_id=session_id,
            feedback=feedback,
            document_type="foundation-research-report",
            agent_type="foundation_research"
        )
    
    @handle_async_errors
    async def _research_report_completion_callback(self) -> None:
        """Callback when Research Team report is completed."""
        if self.current_session_id:
            try:
                # Complete the session in the agent
                await self.research_team.complete_session(self.current_session_id)
                
                # Use the generic handler for the rest
                await self._document_completion_handler("foundation-research-report", "foundation_selection_screen")
            except Exception as e:
                logger.error(f"Error completing research session: {str(e)}")
                self.notify("Error marking research session as complete", severity="error")

    # -----------------------------------------------------------------------------------
    # Generic Architecture
    # -----------------------------------------------------------------------------------

    @handle_async_errors
    async def show_document_review_for_generic_architecture(self, session_id: str) -> None:
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
            document_title="Generic Architecture Document",
            document_type="generic-architecture",
            revision_callback=self._generic_architecture_revision_callback,
            completion_callback=self._generic_architecture_completion_callback,
            back_screen="foundation_selection_screen",
            next_screen="technology_research_requirements_screen"  # Fixed typo in screen name
        )
        
        # Update workflow state in session manager
        self.session_manager.update_workflow_state(session_id, "generic_architecture_document_completed")
        
        # Switch to the document review screen
        self.action_switch_to_document_review()

    @handle_async_errors
    async def _generic_architecture_revision_callback(self, session_id: str, feedback: str) -> str:
        """Callback for Generic Architecture document revisions."""
        return await self._document_revision_handler(
            session_id=session_id,
            feedback=feedback, 
            document_type="generic-architecture",
            agent_type="architect"
        )
    
    @handle_async_errors
    async def _generic_architecture_completion_callback(self) -> None:
        """Callback when generic Architecture document (from foundation selection) is completed."""
        await self._document_completion_handler("generic-architecture", "technology_research_requirements_screen")
    
    # -----------------------------------------------------------------------------------
    # Technology Research Requirements
    # -----------------------------------------------------------------------------------

    @handle_async_errors
    async def show_document_review_for_technology_research_requirements(self, session_id: str) -> None:
        """Show document review screen for the technology research requirements."""
        # Load the technology research requirements document
        from ideasfactory.utils.file_manager import load_document_content
        tech_requirements = await load_document_content(session_id, "technology-research-requirements")
        
        if not tech_requirements:
            self.notify("No technology research requirements document available", severity="error")
            return
        
        # Configure the document review screen
        self.document_review_screen.configure_for_agent(
            document_source=DocumentSource.ARCHITECT,
            session_id=session_id,
            document_content=tech_requirements,
            document_title="Technology Research Requirements",
            document_type="technology-research-requirements",
            revision_callback=self._technology_requirements_revision_callback,
            completion_callback=self._technology_requirements_completion_callback,
            back_screen="technology_research_requirements_screen",
            next_screen="technology_research_screen"
        )
        
        # Update workflow state
        self.session_manager.update_workflow_state(session_id, "technology_requirements_created")
        
        # Switch to the document review screen
        self.action_switch_to_document_review()

    @handle_async_errors
    async def _technology_requirements_revision_callback(self, session_id: str, feedback: str) -> str:
        """Callback for technology research requirements document revisions."""
        return await self._document_revision_handler(
            session_id=session_id,
            feedback=feedback,
            document_type="technology-research-requirements",
            agent_type="architect"
        )
    
    @handle_async_errors
    async def _technology_requirements_completion_callback(self) -> None:
        """Callback when Technology Research Requirements document is completed."""
        await self._document_completion_handler("technology-research-requirements", "technology_research_screen")

    # -----------------------------------------------------------------------------------
    # Technology Research Report
    # -----------------------------------------------------------------------------------

    @handle_async_errors
    async def show_document_review_for_technology_research_report(self, session_id: str) -> None:
        """Show document review screen for the Technology Research Team report."""
        # Use the centralized document loading utility directly (same pattern as foundation research)
        from ideasfactory.utils.file_manager import load_document_content
        report_content = await load_document_content(session_id, "technology-research-report")
        
        if not report_content:
            self.notify("No technology research report available for this session", severity="error")
            return
        
        # Configure the document review screen for the technology research report
        self.document_review_screen.configure_for_agent(
            document_source=DocumentSource.RESEARCH_TEAM,
            session_id=session_id,
            document_content=report_content,
            document_title="Technology Research Report",
            document_type="technology-research-report",
            revision_callback=self._technology_research_report_revision_callback,
            completion_callback=self._technology_research_report_completion_callback,
            back_screen="technology_research_screen",
            next_screen="technology_selection_screen"  # Go to technology selection screen
        )

    @handle_async_errors
    async def _technology_research_report_revision_callback(self, session_id: str, feedback: str) -> str:
        """Callback for Technology Research Team report revisions."""
        return await self._document_revision_handler(
            session_id=session_id,
            feedback=feedback,
            document_type="technology-research-report",
            agent_type="technology_research"
        )
    
    @handle_async_errors
    async def _technology_research_report_completion_callback(self) -> None:
        """Callback when Technology Research Team report is completed."""
        if self.current_session_id:
            try:
                # Complete the session in the agent
                await self.technology_research_team.complete_session(self.current_session_id)
                
                # Use the generic handler for the rest
                await self._document_completion_handler("technology-research-report", "technology_selection_screen") 
            except Exception as e:
                logger.error(f"Error completing technology research session: {str(e)}")
                self.notify("Error marking technology research session as complete", severity="error")
        
        # Update workflow state in session manager
        self.session_manager.update_workflow_state(self.current_session_id, "technology_research_report_completed")
        
        # Switch to the document review screen
        self.action_switch_to_document_review()

    # -----------------------------------------------------------------------------------
    # Project Architecture 
    # -----------------------------------------------------------------------------------

    @handle_async_errors
    async def show_document_review_for_final_architecture(self, session_id: str) -> None:
        """Show document review screen for the final Architecture document after technology selection."""
        # Get the session from the Architect
        session = self.architect.sessions.get(session_id)
        if not session or not session.final_architecture_document:
            self.notify("No final architecture document available for this session", severity="error")
            return
        
        # Configure the document review screen for the Architect document
        self.document_review_screen.configure_for_agent(
            document_source=DocumentSource.ARCHITECT,
            session_id=session_id,
            document_content=session.final_architecture_document,
            document_title="Complete Architecture Document",
            document_type="architecture",
            revision_callback=self._final_architecture_revision_callback,
            completion_callback=self._final_architecture_completion_callback,
            back_screen="technology_selection_screen",
            next_screen=None  # Standards Engineer screen not yet implemented
        )
        
        # Update workflow state in session manager
        self.session_manager.update_workflow_state(session_id, "final_architecture_completed")
        
        # Switch to the document review screen
        self.action_switch_to_document_review()
    
    @handle_async_errors
    async def _final_architecture_revision_callback(self, session_id: str, feedback: str) -> str:
        """Callback for final Architecture document revisions."""
        return await self._document_revision_handler(
            session_id=session_id,
            feedback=feedback, 
            document_type="architecture",
            agent_type="architect",
            revision_method="revise_final_architecture_document"
        )
    
    @handle_async_errors
    async def _final_architecture_completion_callback(self) -> None:
        """Callback when final Architecture document is completed."""
        if self.current_session_id:
            # Complete the Architect session
            await self.architect.complete_session(self.current_session_id)
            
            # Use the generic handler but add the extra notification
            await self._document_completion_handler("architecture")
            
            # Add workflow completion notification
            self.notify("Workflow completed successfully!", severity="success")

    # @handle_async_errors
    # async def _architect_revision_callback(self, session_id: str, feedback: str) -> str:
    #     """Callback for Architect document revisions."""
    #     return await self._document_revision_handler(
    #         session_id=session_id,
    #         feedback=feedback, 
    #         document_type="architecture",
    #         agent_type="architect"
    #     )
    
    # @handle_async_errors
    # async def _architect_completion_callback(self) -> None:
    #     """Callback when Architect document is completed."""
    #     if self.current_session_id:
    #         await self.architect.complete_session(self.current_session_id)
    #         self.notify("Architecture document completed", severity="success")


    # -----------------------------------------------------------------------------------
    # Task List Document
    # -----------------------------------------------------------------------------------
    
    # -----------------------------------------------------------------------------------
    # Standards and Patterns Document
    # -----------------------------------------------------------------------------------
    
    # -----------------------------------------------------------------------------------
    # Epics and Stories
    # -----------------------------------------------------------------------------------
    