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
        Binding(key="d", action="action_switch_to_document", description="Document"),
    ]
    
    def __init__(self, *args, **kwargs):
        """Initialize the application."""
        super().__init__(*args, **kwargs)
        self.current_session_id: Optional[str] = None
        self.brainstorm_screen = None
        self.document_screen = None
    
    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Footer()
    
    def on_mount(self) -> None:
        """Handle the app's mount event."""
        # Create screens first before installing them
        self.brainstorm_screen = BrainstormScreen()
        self.document_screen = DocumentReviewScreen()
        
        # Install screens
        self.install_screen(self.brainstorm_screen, name="brainstorm_screen")
        self.install_screen(self.document_screen, name="document_review_screen")
        
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
    
    def action_switch_to_document(self) -> None:
        """Switch to the document review screen."""
        try:
            # Safely switch to screen using push_screen instead of switch_screen
            if self.screen.name != "document_review_screen":
                self.push_screen("document_review_screen")
        except Exception as e:
            logger.error(f"Error switching to document screen: {e}")
    
    def set_current_session(self, session_id: str) -> None:
        """Set the current session ID."""
        self.current_session_id = session_id
        
        # Update both screens with the session ID without querying them
        if self.brainstorm_screen:
            self.brainstorm_screen.set_session(session_id)
        if self.document_screen:
            self.document_screen.set_session(session_id)