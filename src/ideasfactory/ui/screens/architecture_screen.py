# architecture_screen.py
"""
Architecture screen for IdeasFactory.

This module defines the Textual screen for architecture definition sessions.
"""

import logging
from typing import Optional, Dict, List, Any
import asyncio

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import (
    Header, Footer, Button, Static, TextArea, Label, Input, RadioButton, RadioSet
)
from textual.containers import Container, VerticalScroll, Horizontal
from textual.binding import Binding

from ideasfactory.agents.architect import Architect, ArchitecturalDecision
from ideasfactory.documents.document_manager import DocumentManager

from ideasfactory.utils.session_manager import SessionManager
from ideasfactory.utils.error_handler import handle_async_errors

# Configure logging
logger = logging.getLogger(__name__)


class ArchitectureScreen(Screen):
    """
    Screen for conducting architecture definition sessions with the Architect agent.
    """
    
    BINDINGS = [
        Binding(key="ctrl+n", action="next_decision", description="Next Decision"),
        Binding(key="ctrl+p", action="previous_decision", description="Previous Decision"),
        Binding(key="ctrl+d", action="create_document", description="Create Document"),
        Binding(key="ctrl+q", action="ask_question", description="Ask Question"),
        Binding(key="ctrl+b", action="back", description="Back"),
    ]
    
    def __init__(self, *args, **kwargs):
        """Initialize the architecture screen."""
        super().__init__(*args, **kwargs)
        self.architect = Architect()
        self.document_manager = DocumentManager()
        self.session_id: Optional[str] = None
        self.project_vision: Optional[str] = None
        self.research_report: Optional[str] = None
        self.decisions: List[ArchitecturalDecision] = []
        self.current_decision_index: int = 0
        
        # Track mount state
        self._is_mounted = False
    
    def compose(self) -> ComposeResult:
        """Create child widgets for the screen."""
        yield VerticalScroll(
            Container(
                Label("Architecture Definition", id="architecture_header"),
                
                # Documents container (for reference)
                Container(
                    Button("View Project Vision", id="view_vision_button", variant="primary"),
                    Button("View Research Report", id="view_report_button", variant="primary"),
                    id="documents_container"
                ),
                
                # Analysis container
                Container(
                    Label("Architecture Analysis", id="analysis_header"),
                    Static("Click 'Start Analysis' to begin the architecture definition process.", id="analysis_status"),
                    Button("Start Analysis", id="start_analysis_button", variant="primary"),
                    id="analysis_container"
                ),
                
                # Decision container (initially hidden)
                Container(
                    Label("Architectural Decision", id="decision_header"),
                    Static(id="decision_title", classes="title"),
                    Static(id="decision_description", classes="description"),
                    Label("Options:", id="options_label"),
                    RadioSet(id="options_radioset"),
                    Label("Rationale (optional):", id="rationale_label"),
                    Input(id="rationale_input", placeholder="Enter rationale for your decision..."),
                    Container(
                        Button("Previous", id="previous_button", variant="default"),
                        Button("Make Decision", id="make_decision_button", variant="primary"),
                        Button("Next", id="next_button", variant="default"),
                        id="decision_buttons"
                    ),
                    id="decision_container"
                ),
                
                # Question container
                Container(
                    Label("Ask a question:", id="question_header"),
                    Input(id="question_input", placeholder="Enter your question here..."),
                    Button("Ask", id="ask_button", variant="primary"),
                    Static(id="answer_display", classes="answer"),
                    id="question_container"
                ),
                
                # Action container
                Container(
                    Button("Create Architecture Document", id="create_document_button", variant="success"),
                    Button("Back to Research", id="back_button", variant="warning"),
                    id="action_container"
                ),
                
                id="architecture_container"
            ),
            id="architecture_scroll"
        )
    
    def on_mount(self) -> None:
        """Handle the screen's mount event."""
        self._is_mounted = True
        
        # Hide containers that aren't needed initially
        self.query_one("#decision_container").display = False
        
        # Disable buttons that shouldn't be clickable yet
        self.query_one("#create_document_button").disabled = True
    
    @handle_async_errors
    async def on_screen_resume(self) -> None:
        """Handle screen being resumed."""
        # Get the current session from the session manager
        session_manager = SessionManager()
        current_session = session_manager.get_current_session()
        
        if current_session:
            session_id = current_session.id
            self.session_id = session_id
            
            # Check if we have the required documents' paths in the session
            vision_path = session_manager.get_document(session_id, "project-vision")
            research_path = session_manager.get_document(session_id, "research-report")
            
            # Initialize document content variables
            vision_content = None
            research_content = None
            
            # Document manager for loading documents
            doc_manager = DocumentManager()
            
            # Load vision document if available
            if vision_path:
                vision_doc = doc_manager.get_document(vision_path)
                if vision_doc and "content" in vision_doc:
                    vision_content = vision_doc["content"]
                    self.project_vision = vision_content
            
            # Load research document if available
            if research_path:
                research_doc = doc_manager.get_document(research_path)
                if research_doc and "content" in research_doc:
                    research_content = research_doc["content"]
                    self.research_report = research_content
            
            # If paths weren't in session manager, try loading by type (fallback)
            if not vision_content:
                vision_doc = await doc_manager.get_latest_document_by_type("project-vision", session_id)
                if vision_doc and "content" in vision_doc:
                    vision_content = vision_doc["content"]
                    self.project_vision = vision_content
                    
                    # Store the path in session manager for future reference
                    if "filepath" in vision_doc:
                        session_manager.add_document(session_id, "project-vision", vision_doc["filepath"])
            
            if not research_content:
                research_doc = await doc_manager.get_latest_document_by_type("research-report", session_id)
                if research_doc and "content" in research_doc:
                    research_content = research_doc["content"]
                    self.research_report = research_content
                    
                    # Store the path in session manager for future reference
                    if "filepath" in research_doc:
                        session_manager.add_document(session_id, "research-report", research_doc["filepath"])
            
            # Check if we have all required documents
            if vision_content and research_content:
                self.query_one("#analysis_status").update("Ready to start architecture analysis.")
                self.query_one("#start_analysis_button").disabled = False
            else:
                missing = []
                if not vision_content:
                    missing.append("Project Vision")
                if not research_content:
                    missing.append("Research Report")
                
                self.query_one("#analysis_status").update(f"Missing required documents: {', '.join(missing)}")
                self.query_one("#start_analysis_button").disabled = True
                
                # Log the issue
                logger.warning(f"Missing required documents for architecture: {', '.join(missing)}")
        else:
            # No session
            self.notify("No active session found", severity="error")
            self.query_one("#analysis_status").update("No active session")
            self.query_one("#start_analysis_button").disabled = True
            logger.error("No active session when resuming architecture screen")
    
    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        button_id = event.button.id
        
        if button_id == "start_analysis_button":
            await self.start_analysis()
        elif button_id == "make_decision_button":
            await self.make_decision()
        elif button_id == "previous_button":
            await self.previous_decision()
        elif button_id == "next_button":
            await self.next_decision()
        elif button_id == "create_document_button":
            await self.create_document()
        elif button_id == "back_button":
            await self.go_back()
        elif button_id == "ask_button":
            await self.ask_question()
        elif button_id == "view_vision_button":
            await self.view_project_vision()
        elif button_id == "view_report_button":
            await self.view_research_report()
    
    def set_session(self, session_id: str) -> None:
        """Set the current session ID."""
        self.session_id = session_id
    
    def set_project_vision(self, project_vision: str) -> None:
        """Set the project vision document."""
        self.project_vision = project_vision

    def set_research_report(self, research_report: str) -> None:
        """Set the research report document."""
        self.research_report = research_report
    
    @handle_async_errors
    async def start_analysis(self) -> None:
        """Start the architecture analysis process."""
        if not self._is_mounted or not self.project_vision or not self.research_report:
            logger.error("Screen not mounted or missing required documents")
            return
        
        # Disable the start button while processing
        self.query_one("#start_analysis_button").disabled = True
        self.query_one("#analysis_status").update("Analyzing project requirements...")
        
        try:
            # Use the app's session ID if available, or generate a new one
            if hasattr(self.app, "current_session_id") and self.app.current_session_id:
                self.session_id = self.app.current_session_id
            else:
                # Generate a session ID if we don't have one
                import uuid
                self.session_id = str(uuid.uuid4())
                
                # Update the app's current session if possible
                if hasattr(self.app, "set_current_session"):
                    self.app.set_current_session(self.session_id)
            
            # Create the session
            session = await self.architect.create_session(
                self.session_id, 
                self.project_vision,
                self.research_report
            )
            
            # Start the analysis
            decisions = await self.architect.start_analysis(self.session_id)
            
            if not decisions:
                self.notify("No architectural decisions identified", severity="error")
                self.query_one("#analysis_status").update("Analysis failed to identify decisions.")
                self.query_one("#start_analysis_button").disabled = False
                return
            
            # Store the decisions and update the UI
            self.decisions = decisions
            self.current_decision_index = 0
            
            # Update the status
            self.query_one("#analysis_status").update(
                f"Analysis complete. {len(decisions)} architectural decisions identified."
            )
            
            # Show the decision container
            self.query_one("#decision_container").display = True
            
            # Display the first decision
            await self.display_current_decision()
            
        except Exception as e:
            logger.error(f"Error during architecture analysis: {str(e)}")
            self.notify("Failed to analyze architecture requirements", severity="error")
            self.query_one("#analysis_status").update("Error during analysis.")
            self.query_one("#start_analysis_button").disabled = False
    
    async def display_current_decision(self) -> None:
        """Display the current architectural decision in the UI."""
        if not self.decisions or self.current_decision_index >= len(self.decisions):
            return
        
        # Get the current decision
        decision = self.decisions[self.current_decision_index]
        
        # Update the decision display
        self.query_one("#decision_title").update(f"**{decision.title}** ({self.current_decision_index + 1}/{len(self.decisions)})")
        self.query_one("#decision_description").update(decision.description)

        # Remove all radio buttons and rebuild the radio set
        radio_set = self.query_one("#options_radioset")
        # Remove existing children
        if hasattr(radio_set, "children"):
            radio_set.remove_children()
        
        # Add options to the radio set
        for i, option in enumerate(decision.options):
            option_name = option.get("name", f"Option {i+1}")
            pros = ", ".join(option.get("pros", []))
            cons = ", ".join(option.get("cons", []))
            
            option_text = f"{option_name}"
            if pros:
                option_text += f"\nPros: {pros}"
            if cons:
                option_text += f"\nCons: {cons}"
            
            # Add recommendation indicator
            if decision.recommendation and option_name == decision.recommendation:
                option_text += "\n[Recommended]"
            
            radio_button = RadioButton(option_text, value=option_name)
            radio_set.mount(radio_button)
        
        # If a decision has already been made, select it
        if decision.completed and decision.decision:
            for button in radio_set.children:
                if decision.decision in button.label:
                    button.value = True
                    break
        
        # Set rationale if available
        if decision.rationale:
            self.query_one("#rationale_input").value = decision.rationale
        else:
            self.query_one("#rationale_input").value = ""
        
        # Update the make decision button
        make_button = self.query_one("#make_decision_button")
        make_button.label = "Update Decision" if decision.completed else "Make Decision"
        
        # Update navigation buttons
        self.query_one("#previous_button").disabled = self.current_decision_index == 0
        self.query_one("#next_button").disabled = self.current_decision_index == len(self.decisions) - 1
        
        # Check if all decisions have been made
        all_completed = all(d.completed for d in self.decisions)
        self.query_one("#create_document_button").disabled = not all_completed
    
    @handle_async_errors
    async def make_decision(self) -> None:
        """Make or update the current architectural decision."""
        if not self.session_id or not self.decisions or self.current_decision_index >= len(self.decisions):
            logger.error("Cannot make decision: invalid session or decision")
            return
        
        # Get the current decision
        decision = self.decisions[self.current_decision_index]
        
        # Get the selected option
        radio_set = self.query_one("#options_radioset")
        selected_button = None
        for button in radio_set.children:
            if button.value:
                selected_button = button
                break
        
        if not selected_button:
            self.notify("Please select an option", severity="error")
            return
        
        # Extract the option name from the button label
        option_name = selected_button.renderable.split("\n")[0].strip()
        
        # Get the rationale
        rationale = self.query_one("#rationale_input").value
        
        try:
            # Record the decision
            success = await self.architect.make_decision(
                self.session_id,
                decision.id,
                option_name,
                rationale
            )
            
            if success:
                # Update the local decision
                decision.decision = option_name
                decision.rationale = rationale
                decision.completed = True
                
                # Display a notification
                self.notify(f"Decision recorded: {option_name}", severity="success")
                
                # Check if all decisions have been made
                all_completed = all(d.completed for d in self.decisions)
                self.query_one("#create_document_button").disabled = not all_completed
                
                # Update the make decision button
                self.query_one("#make_decision_button").label = "Update Decision"
                
                # Move to the next decision if there is one and it's not yet completed
                if (self.current_decision_index < len(self.decisions) - 1 and 
                    not self.decisions[self.current_decision_index + 1].completed):
                    await self.next_decision()
            else:
                self.notify("Failed to record decision", severity="error")
                
        except Exception as e:
            logger.error(f"Error making decision: {str(e)}")
            self.notify("Failed to record decision", severity="error")
    
    async def previous_decision(self) -> None:
        """Navigate to the previous architectural decision."""
        if self.current_decision_index > 0:
            self.current_decision_index -= 1
            await self.display_current_decision()
    
    async def next_decision(self) -> None:
        """Navigate to the next architectural decision."""
        if self.current_decision_index < len(self.decisions) - 1:
            self.current_decision_index += 1
            await self.display_current_decision()
    
    async def action_previous_decision(self) -> None:
        """Handle keyboard shortcut for previous decision."""
        await self.previous_decision()
    
    async def action_next_decision(self) -> None:
        """Handle keyboard shortcut for next decision."""
        await self.next_decision()
    
    async def ask_question(self) -> None:
        """Ask a question to the Architect agent."""
        if not self.session_id:
            logger.error("Cannot ask question: no active session")
            return
        
        # Get the question from the input
        question = self.query_one("#question_input").value
        if not question:
            return
        
        # Clear the input
        self.query_one("#question_input").value = ""
        
        # Disable the ask button while processing
        ask_button = self.query_one("#ask_button")
        ask_button.disabled = True
        
        try:
            # Ask the question
            answer = await self.architect.ask_question(self.session_id, question)
            
            if answer:
                # Update the answer display
                self.query_one("#answer_display").update(f"Q: {question}\n\nA: {answer}")
            else:
                self.notify("Failed to get answer", severity="error")
                
        except Exception as e:
            logger.error(f"Error asking question: {str(e)}")
            self.notify("Failed to get answer", severity="error")
        
        finally:
            # Re-enable the ask button
            ask_button.disabled = False
    
    async def action_ask_question(self) -> None:
        """Handle keyboard shortcut for asking a question."""
        # Focus the question input
        self.query_one("#question_input").focus()
    
    @handle_async_errors
    async def create_document(self) -> None:
        """Create an architecture document based on the decisions made."""
        if not self.session_id:
            logger.error("Cannot create document: no active session")
            return
        
        # Check if all decisions have been made
        all_completed = all(d.completed for d in self.decisions)
        if not all_completed:
            self.notify("Not all decisions have been made", severity="warning")
            # We'll let the user proceed anyway if they want to
        
        # Disable the create button while processing
        create_button = self.query_one("#create_document_button")
        create_button.disabled = True
        
        try:
            # Create the document
            document = await self.architect.create_document(self.session_id)
            
            if document:
                # Use the app's method to show document review for this document
                if hasattr(self.app, "show_document_review_for_architect"):
                    await self.app.show_document_review_for_architect(self.session_id)
                else:
                    # Fallback - notify that this isn't implemented
                    self.notify("Document review integration not implemented", severity="error")
            else:
                self.notify("Failed to create architecture document", severity="error")
                
        except Exception as e:
            logger.error(f"Error creating document: {str(e)}")
            self.notify("Failed to create architecture document", severity="error")
        
        finally:
            # Re-enable the create button
            create_button.disabled = False
    
    async def action_create_document(self) -> None:
        """Handle keyboard shortcut for creating a document."""
        await self.create_document()
    
    async def go_back(self) -> None:
        """Go back to the previous screen."""
        # Use pop_screen to go back to the previous screen
        self.app.pop_screen()
    
    async def action_back(self) -> None:
        """Handle keyboard shortcut for going back."""
        await self.go_back()
    
    async def view_project_vision(self) -> None:
        """View the project vision document."""
        if not self.project_vision:
            self.notify("No project vision document available", severity="error")
            return
        
        # Create a popup or use the document review screen to display the vision
        # For now, just show a notification
        self.notify("Project vision viewing not implemented", severity="information")
    
    async def view_research_report(self) -> None:
        """View the research report."""
        if not self.research_report:
            self.notify("No research report available", severity="error")
            return
        
        # Create a popup or use the document review screen to display the report
        # For now, just show a notification
        self.notify("Research report viewing not implemented", severity="information")