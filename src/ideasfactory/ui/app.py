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
        Binding(key="b", action="switch_to_brainstorm", description="Brainstorm"),
        Binding(key="d", action="switch_to_document", description="Document"),
    ]
    
    def __init__(self, *args, **kwargs):
        """Initialize the application."""
        super().__init__(*args, **kwargs)
        self.current_session_id: Optional[str] = None
    
    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield BrainstormScreen(id="brainstorm_screen")
        yield DocumentReviewScreen(id="document_review_screen")
        yield Footer()
    
    def on_mount(self) -> None:
        """Handle the app's mount event."""
        # Show the brainstorm screen by default
        self.action_switch_to_brainstorm()
    
    def action_switch_to_brainstorm(self) -> None:
        """Switch to the brainstorm screen."""
        self.query_one(BrainstormScreen).display = True
        self.query_one(DocumentReviewScreen).display = False
    
    def action_switch_to_document(self) -> None:
        """Switch to the document review screen."""
        self.query_one(BrainstormScreen).display = False
        self.query_one(DocumentReviewScreen).display = True
    
    def set_current_session(self, session_id: str) -> None:
        """Set the current session ID."""
        self.current_session_id = session_id
        # Update both screens with the session ID
        self.query_one(BrainstormScreen).set_session(session_id)
        self.query_one(DocumentReviewScreen).set_session(session_id)