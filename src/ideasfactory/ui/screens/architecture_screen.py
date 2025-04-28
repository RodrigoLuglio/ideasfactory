# architecture_screen.py
"""
Architecture screen for IdeasFactory.

This module defines the Textual screen for architecture definition sessions.
"""

import logging
from typing import Optional, Dict, List, Any
import asyncio

from textual.app import ComposeResult
from textual.widgets import (
    Header, Footer, Button, Static, TextArea, Label, Input, RadioButton, RadioSet
)
from textual.containers import Container, VerticalScroll, Horizontal
from textual.binding import Binding

from ideasfactory.agents.architect import Architect, ArchitecturalDecision
from ideasfactory.documents.document_manager import DocumentManager
from ideasfactory.ui.screens.document_review_screen import DocumentSource
from ideasfactory.ui.screens import BaseScreen

from ideasfactory.utils.session_manager import SessionManager
from ideasfactory.utils.error_handler import handle_async_errors

# Configure logging
logger = logging.getLogger(__name__)


class ArchitectureScreen(BaseScreen):
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
        self.project_vision: Optional[str] = None
        self.prd_document: Optional[str] = None
        self.research_report: Optional[str] = None
        self.research_requirements: Optional[str] = None
        self.decisions: List[ArchitecturalDecision] = []
        self.current_decision_index: int = 0
    
    def compose(self) -> ComposeResult:
        """Create child widgets for the screen."""
    
        yield Container(
            Label("Architecture Definition", id="architecture_header"),
            
            # Documents container (for reference)
            Container(
                Button("View Project Vision", id="view_vision_button", variant="primary"),
                Button("View PRD", id="view_prd_button", variant="primary"),
                Button("View Research Report", id="view_report_button", variant="primary"),
                Button("Reload Documents", id="reload_documents_button", variant="default"),
                id="documents_container"
            ),
            
            # Research Requirements container
            Container(
                Label("Technical Research Requirements", id="research_requirements_header"),
                Static("Create research requirements to guide the research phase.", id="research_requirements_status"),
                Button("Create Research Requirements", id="create_research_requirements_button", variant="primary"),
                Button("View Research Requirements", id="view_research_requirements_button", variant="success", disabled=True),
                id="research_requirements_container"
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
        )
        
    def on_mount(self) -> None:
        """Handle the screen's mount event."""
        super().on_mount()  # Call base class on_mount
        
        # Hide containers that aren't needed initially
        self.query_one("#decision_container").display = False
        
        # Disable buttons that shouldn't be clickable yet
        self.query_one("#create_document_button").disabled = True
        self.query_one("#view_research_requirements_button").disabled = True
        self.query_one("#start_analysis_button").disabled = True
        
        # Add header to clarify the two-phase architecture workflow
        arch_header = self.query_one("#architecture_header")
        arch_header.update("Architecture Definition (Two-Phase Workflow)")
        
        # Add phase labels to clarify current phase
        research_header = self.query_one("#research_requirements_header")
        research_header.update("Phase 1: Technical Research Requirements")
        
        analysis_header = self.query_one("#analysis_header")
        analysis_header.update("Phase 2: Architecture Design (after research)")
        
        # Load documents if session is available
        if self.session_id:
            asyncio.create_task(self._load_session_documents())
    
    @handle_async_errors
    async def _load_session_documents(self) -> None:
        """Load documents for the current session."""
        if not self.session_id:
            return
            
        # Use the centralized document loading utility
        from ideasfactory.utils.file_manager import load_document_content
        
        # Load project vision document
        vision_content = await load_document_content(self.session_id, "project-vision")
        if vision_content:
            self.project_vision = vision_content
        
        # Load PRD document
        prd_content = await load_document_content(self.session_id, "prd")
        if prd_content:
            self.prd_document = prd_content
        
        # Load research requirements document
        research_requirements_content = await load_document_content(self.session_id, "research-requirements")
        if research_requirements_content:
            self.research_requirements = research_requirements_content
            
        # Load research report document
        research_content = await load_document_content(self.session_id, "research-report")
        if research_content:
            self.research_report = research_content
            
        # Update UI based on document availability
        if self._is_mounted:
            # Update research requirements status and buttons
            if self.prd_document:
                if self.research_requirements:
                    self.query_one("#research_requirements_status").update("Research requirements document created.")
                    self.query_one("#view_research_requirements_button").disabled = False
                    self.query_one("#create_research_requirements_button").disabled = True
                else:
                    self.query_one("#research_requirements_status").update("Ready to create research requirements.")
                    self.query_one("#create_research_requirements_button").disabled = False
            else:
                self.query_one("#research_requirements_status").update("PRD required to create research requirements.")
                self.query_one("#create_research_requirements_button").disabled = True
            
            # Update analysis status and buttons - Phase 2 depends on Phase 1 completion
            if self.project_vision and self.research_report and self.research_requirements:
                self.query_one("#analysis_status").update("Ready to start Phase 2: Architecture Design (research completed)")
                self.query_one("#start_analysis_button").disabled = False
            else:
                missing = []
                if not self.project_vision:
                    missing.append("Project Vision")
                if not self.research_report:
                    missing.append("Research Report")
                if not self.research_requirements:
                    missing.append("Research Requirements (Phase 1)")
                
                if self.research_requirements:
                    phase_status = "Phase 1 completed. "
                    
                    # Add a message about research if requirements are completed but no report
                    if not self.research_report:
                        phase_status += "Please proceed to Research phase (press 's') to generate a research report. "
                else:
                    phase_status = "Phase 1 must be completed first. "
                    
                self.query_one("#analysis_status").update(f"{phase_status}Missing: {', '.join(missing)}")
                self.query_one("#start_analysis_button").disabled = True
    
    @handle_async_errors
    async def on_screen_resume(self) -> None:
        """Handle screen being resumed."""
        # Call the base class implementation which handles session retrieval
        await super().on_screen_resume()
        
        # If we have a session but no documents, try to load them
        if self.session_id and (not self.project_vision or not self.prd_document or not self.research_requirements or not self.research_report):
            await self._load_session_documents()
        elif not self.session_id:
            # No session
            self.notify("No active session found", severity="error")
            self.query_one("#analysis_status").update("No active session")
            self.query_one("#research_requirements_status").update("No active session")
            self.query_one("#start_analysis_button").disabled = True
    
    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        button_id = event.button.id
        
        if button_id == "create_research_requirements_button":
            await self.create_research_requirements()
        elif button_id == "view_research_requirements_button":
            await self.view_research_requirements()
        elif button_id == "start_analysis_button":
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
        elif button_id == "view_prd_button":
            await self.view_prd_document()
        elif button_id == "view_report_button":
            await self.view_research_report()
        elif button_id == "reload_documents_button":
            await self._load_session_documents()
    
    def set_project_vision(self, project_vision: str) -> None:
        """Set the project vision document."""
        self.project_vision = project_vision

    def set_prd_document(self, prd_document: str) -> None:
        """Set the PRD document."""
        self.prd_document = prd_document
        
    def set_research_requirements(self, research_requirements: str) -> None:
        """Set the research requirements document."""
        self.research_requirements = research_requirements

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
            # Get the session ID from session manager (single source of truth)
            session_manager = SessionManager()
            current_session = session_manager.get_current_session()
            
            if current_session:
                self.session_id = current_session.id
            else:
                # No active session - shouldn't happen but handle gracefully
                logger.error("No active session when starting architecture analysis")
                self.notify("No active session found", severity="error")
                self.query_one("#start_analysis_button").disabled = False
                return
            
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
    
    @handle_async_errors
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
    
    @handle_async_errors
    async def create_research_requirements(self) -> None:
        """Create the research requirements document."""
        if not self._is_mounted:
            return
            
        if not self.session_id:
            self.notify("No active session", severity="error")
            return
            
        if not self.prd_document:
            self.notify("PRD document is required for research requirements", severity="error")
            return
        
        # Update status to show we're working
        self.query_one("#research_requirements_status").update("Creating research requirements...")
        self.query_one("#create_research_requirements_button").disabled = True
        
        try:
            # Create architect session if we don't have one already
            architect_session = self.architect.sessions.get(self.session_id)
            if not architect_session:
                architect_session = await self.architect.create_session(
                    self.session_id,
                    self.project_vision,
                    self.prd_document,
                    self.research_report
                )
            else:
                # Update the session with the latest documents
                architect_session.project_vision = self.project_vision
                architect_session.prd_document = self.prd_document
                architect_session.research_report = self.research_report
            
            # Generate the research requirements
            self.research_requirements = await self.architect.create_research_requirements(self.session_id)
            
            if self.research_requirements:
                # Update UI to show success
                self.query_one("#research_requirements_status").update("Research requirements document created")
                self.query_one("#view_research_requirements_button").disabled = False
                
                # Notify user
                self.notify("Research requirements created successfully", severity="success")
                
                # Show the document review screen for the research requirements
                if hasattr(self.app, "show_document_review_for_research_requirements"):
                    await self.app.show_document_review_for_research_requirements(self.session_id)
            else:
                raise ValueError("Failed to create research requirements document")
                
        except Exception as e:
            logger.error(f"Error creating research requirements: {str(e)}")
            self.notify(f"Error creating research requirements: {str(e)}", severity="error")
            self.query_one("#research_requirements_status").update("Error creating research requirements")
            self.query_one("#create_research_requirements_button").disabled = False
    
    @handle_async_errors
    async def view_research_requirements(self) -> None:
        """View the research requirements document."""
        if not self.research_requirements:
            self.notify("No research requirements document available", severity="error")
            return
            
        # Show the document review screen for the research requirements
        if hasattr(self.app, "show_document_review_for_research_requirements"):
            await self.app.show_document_review_for_research_requirements(self.session_id)
        else:
            self.notify("Document review not available", severity="error")
    
    @handle_async_errors
    async def view_prd_document(self) -> None:
        """View the PRD document."""
        if not self.prd_document:
            self.notify("No PRD document available", severity="error")
            return
        
        # Show the document review screen for the PRD
        if hasattr(self.app, "show_document_review_for_pm"):
            await self.app.show_document_review_for_pm(self.session_id)
        else:
            self.notify("Document review not available", severity="error")
    
    @handle_async_errors
    async def view_project_vision(self) -> None:
        """View the project vision document."""
        if not self.project_vision:
            self.notify("No project vision document available", severity="error")
            return
        
        # Use the document review screen to display the vision
        if hasattr(self.app, "document_review_screen"):
            # Configure the document review for viewing only
            self.app.document_review_screen.configure_for_agent(
                document_source=DocumentSource.BUSINESS_ANALYST,
                session_id=self.session_id,
                document_content=self.project_vision,
                document_title="Project Vision",
                document_type="project-vision",
                revision_callback=None,  # No revision for viewing only
                completion_callback=None,
                back_screen="architecture_screen",
                next_screen=None
            )
            # Show the document review screen
            self.app.push_screen("document_review_screen")
        else:
            self.notify("Document review screen not available", severity="error")
    
    @handle_async_errors
    async def view_research_report(self) -> None:
        """View the research report."""
        if not self.research_report:
            self.notify("No research report available", severity="error")
            return
        
        # Use the document review screen to display the report
        if hasattr(self.app, "document_review_screen"):
            # Configure the document review for viewing only
            self.app.document_review_screen.configure_for_agent(
                document_source=DocumentSource.PROJECT_MANAGER,
                session_id=self.session_id,
                document_content=self.research_report,
                document_title="Research Report",
                document_type="research-report",
                revision_callback=None,  # No revision for viewing only
                completion_callback=None,
                back_screen="architecture_screen",
                next_screen=None
            )
            # Show the document review screen
            self.app.push_screen("document_review_screen")
        else:
            self.notify("Document review screen not available", severity="error")