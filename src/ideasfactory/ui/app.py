# Updated app.py - Main application with Project Manager integration

"""
Main application for IdeasFactory.

This module defines the main Textual application for IdeasFactory.
"""

import os
import sys
import logging
from typing import Optional

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer
from textual.binding import Binding
from textual.screen import Screen

from ideasfactory.ui.screens.brainstorm_screen import BrainstormScreen
from ideasfactory.ui.screens.document_review_screen import DocumentReviewScreen
from ideasfactory.ui.screens.deep_reasearch_screen import DeepResearchScreen

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
    ]
    
    def __init__(self, *args, **kwargs):
        """Initialize the application."""
        super().__init__(*args, **kwargs)
        self.current_session_id: Optional[str] = None
        self.current_project_vision: Optional[str] = None
        self.brainstorm_screen = None
        self.document_review_screen = None
        self.deep_research_screen = None
    
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
        
        # Install screens
        self.install_screen(self.brainstorm_screen, name="brainstorm_screen")
        self.install_screen(self.document_review_screen, name="document_review_screen")
        self.install_screen(self.deep_research_screen, name="deep_research_screen")
        
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
    
    def set_current_session(self, session_id: str) -> None:
        """Set the current session ID."""
        self.current_session_id = session_id
        
        # Update screens with the session ID
        if self.brainstorm_screen:
            self.brainstorm_screen.set_session(session_id)
        if self.document_review_screen:
            self.document_review_screen.set_session(session_id)
    
    def set_project_vision(self, project_vision: str) -> None:
        """Set the current project vision document."""
        self.current_project_vision = project_vision
        
        # Update the project manager screen with the vision
        if self.deep_research_screen:
            self.deep_research_screen.set_project_vision(project_vision)