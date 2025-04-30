# src/ideasfactory/ui/screens/architecture_technology_selection_screen.py

import logging
from typing import Optional, List, Dict, Any
import asyncio

from textual.app import ComposeResult
from textual.widgets import Button, Static, Label, OptionList, Input, TextArea
from textual.widgets.option_list import Option
from textual.containers import Container, VerticalScroll, Horizontal
from textual.binding import Binding

from ideasfactory.ui.screens.base_screen import BaseScreen
from ideasfactory.ui.widgets.chat_widget import ChatWidget
from ideasfactory.agents.architect import Architect
from ideasfactory.utils.error_handler import handle_async_errors
from ideasfactory.utils.session_manager import SessionManager
from ideasfactory.utils.file_manager import load_document_content

# Configure logging
logger = logging.getLogger(__name__)

class ArchitectureTechnologySelectionScreen(BaseScreen):
    """Screen for selecting technologies for the project with the Architect."""
    
    BINDINGS = [
        Binding(key="r", action="review_technologies", description="Review Technologies"),
        Binding(key="s", action="specify_technologies", description="Specify Technologies"),
        Binding(key="c", action="continue_workflow", description="Continue"),
    ]
    
    def __init__(self):
        """Initialize the technology selection screen."""
        super().__init__()
        self.architect = Architect()
        self.session_manager = SessionManager()
        self.technology_report = None
        self.stack_path_reports = {}
        self.chat_widget = None
        self.selected_stack = None
        self.user_defined_stack = False
        self.technology_options = []
    
    def compose(self) -> ComposeResult:
        """Create child widgets for the screen."""
        yield Container(
            Label("Technology Selection", id="technology-title"),
            
            # Choice between research options and user-specified
            Container(
                Label("How would you like to select technologies?", id="selection-method-prompt"),
                Button("Review Research Options", id="review-options-button", variant="primary"),
                Button("Specify My Own Technologies", id="specify-technologies-button", variant="warning"),
                id="selection-method-container"
            ),
            
            # Technology options (initially hidden)
            Container(
                Label("Research Technology Stacks", id="options-title"),
                VerticalScroll(
                    OptionList(id="technology-options"),
                    id="options-scroll"
                ),
                Button("View Details", id="view-details-button", variant="primary", disabled=True),
                id="technology-options-container",
                classes="hidden"
            ),
            
            # User technology specification (initially hidden)
            Container(
                Label("Specify Your Technologies", id="user-technologies-title"),
                TextArea(id="technologies-input"),
                Button("Submit", id="submit-technologies-button", variant="success"),
                id="user-technologies-container",
                classes="hidden"
            ),
            
            # Technology details area (initially empty)
            Container(
                id="technology-details-container",
                classes="hidden"
            ),
            
            # Action buttons
            Container(
                Button("Back to Technology Research", id="back-button", variant="warning"),
                Button("Continue", id="continue-button", variant="success", disabled=True),
                id="action-buttons"
            ),
            id="technology-decision-container"
        )
    
    def on_mount(self) -> None:
        """Handle the screen's mount event."""
        super().on_mount()
        if self.session_id:
            asyncio.create_task(self._load_session_documents())
    
    @handle_async_errors
    async def _load_session_documents(self) -> None:
        """Load documents for the current session."""
        if not self.session_id:
            return
            
        # Use the centralized document loading utility
        from ideasfactory.utils.file_manager import load_document_content
        from ideasfactory.documents.document_manager import DocumentManager

        # Load project vision document
        vision_content = await load_document_content(self.session_id, "project-vision")
        project_vision = vision_content
        
        # Load PRD document
        prd_content = await load_document_content(self.session_id, "prd")
        prd_document = prd_content
        
        # Load technology research report
        technology_report = await load_document_content(self.session_id, "technology-research-report")
        if technology_report:
            self.technology_report = technology_report
            
            # Get stack reports directly from session metadata
            document_manager = DocumentManager()
            stack_path_reports = {}
            
            # Get the current session
            session_manager = SessionManager()
            current_session = session_manager.get_session(self.session_id)
            
            if current_session and "stack_path_reports" in current_session.metadata:
                # Load stack path reports from metadata references
                metadata_stack_path_reports = current_session.metadata["stack_path_reports"]
                logger.info(f"Found {len(metadata_stack_path_reports)} stack reports in session metadata")
                
                for stack_name, path in metadata_stack_path_reports.items():
                    # Load each document from its stored path
                    doc = document_manager.get_document(path)
                    if doc:
                        stack_path_reports[stack_name] = doc
                        stack_path_reports[stack_name]["filepath"] = path
                        logger.info(f"  - Loaded stack report for: {stack_name}")
            else:
                logger.info("No stack reports found in session metadata")
            
            self.stack_path_reports = stack_path_reports
            
            # Log stack reports found
            logger.info(f"Using {len(stack_path_reports)} stack reports for session {self.session_id}")
            for stack_name, report in stack_path_reports.items():
                logger.info(f"  - {stack_name}: {report.get('filepath')}")
            
            # Create an architect session if not already exists
            session = self.architect.sessions.get(self.session_id)
            if not session:
                # Load project vision and PRD
                project_vision = await load_document_content(self.session_id, "project-vision")
                prd_document = await load_document_content(self.session_id, "prd")
                technology_report = await load_document_content(self.session_id, "technology-report")
                
                # Create the architect session
                session = await self.architect.create_session(
                    self.session_id,
                    project_vision,
                    prd_document,
                    technology_report
                )
                
                # Add stack reports to architect session
                session.metadata["stack_path_reports"] = stack_path_reports
            else:
                # Update the session with the latest documents
                session.metadata["project_vision"] = project_vision 
                session.metadata["prd_document"] = prd_document
                session.metadata["technology_report"] = technology_report
                session.metadata["stack_path_reports"] = stack_path_reports
            
            # Extract technology options
            await self._extract_technology_options()
    
    @handle_async_errors
    async def _extract_technology_options(self) -> None:
        """Extract technology stack options from the technology report."""
        if not self.technology_report:
            return
        
        # Extract technology options using the architect
        options = await self.architect.extract_technology_stacks(self.session_id, self.technology_report)
        
        # Populate the option list
        option_list = self.query_one("#technology-options")
        
        # Clear existing options
        option_list.clear_options()
        
        for i, option in enumerate(options):
            # Create an Option object with text and ID
            option_obj = Option(f"{option['name']}", id=f"stack-{i}")
            option_list.add_option(option_obj)
        
        # Store the options in the screen
        self.technology_options = options
    
    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        button_id = event.button.id
        
        if button_id == "review-options-button":
            await self._show_technology_options()
        
        elif button_id == "specify-technologies-button":
            await self._show_user_technology_input()
        
        elif button_id == "view-details-button":
            await self._show_technology_details()
        
        elif button_id == "submit-technologies-button":
            await self._process_user_technologies()
        
        elif button_id == "back-button":
            self.app.action_switch_to_technology_research()
        
        elif button_id == "continue-button":
            if not self.selected_stack:
                self.notify("Please select a tech stack first", severity="error")
                return
            
            current_session = self.session_manager.get_session(self.session_id)
            document_exists = False

            # TODO check if inn the architecture folder there really is the complete architecture document or only the generic architecture document
            if current_session and "documents" in current_session.metadata:
                document_exists = current_session.metadata.get("documents", {}).get("architecture") is not None

            if not document_exists:
                await self._create_architecture_document()
                return
            
            if current_session:
                if "architecture" not in current_session.metadata:
                    current_session.metadata[""] = {}
                
                current_session.metadata["architecture"]["selected_stack"] = self.selected_stack
                current_session.metadata["user_defined_stack"] = self.user_defined_stack

                self.session_manager.update_session(self.session_id, current_session)

                self.session_manager.update_workflow_state(self.session_id, "stack_selected")

                if hasattr(self.app, "_architecture_completion_callback"):
                    await self.app._complete_architecture_completion_callback()
    
    @handle_async_errors
    async def _show_technology_options(self) -> None:
        """Show the technology options from research."""
        # Hide selection method container
        self.query_one("#selection-method-container").add_class("hidden")
        
        # Show technology options container
        self.query_one("#technology-options-container").remove_class("hidden")
    
    @handle_async_errors
    async def _show_user_technology_input(self) -> None:
        """Show the user technology input form."""
        # Hide selection method container
        self.query_one("#selection-method-container").add_class("hidden")
        
        # Show user technologies container
        self.query_one("#user-technologies-container").remove_class("hidden")
    
    async def on_option_list_option_selected(self, event) -> None:
        """Handle option selection in the technology options list."""
        self.query_one("#view-details-button").disabled = False
    
    @handle_async_errors
    async def _show_technology_details(self) -> None:
        """Show details for the selected technology stack."""
        option_list = self.query_one("#technology-options")
        selected_index = option_list.highlighted
        
        if selected_index is None or selected_index >= len(self.technology_options):
            return
        
        selected_stack = self.technology_options[selected_index]
        self.selected_stack = selected_stack
        
        # If we don't have a chat widget yet, create one
        if self.chat_widget is None:
            # Create a chat widget for interactive technology exploration
            self.chat_widget = ChatWidget(
                title=f"Technology Stack: {selected_stack['name']}",
                on_message_callback=self._handle_technology_chat,
                header_display=True,
                show_actions=True
            )
            
            details_container = self.query_one("#technology-details-container")
            details_container.remove_class("hidden")
            details_container.mount(self.chat_widget)
            
            # Add initial message with technology details
            await self.chat_widget.add_message(
                f"# {selected_stack['name']}\n\n{selected_stack['description']}\n\n" +
                "I can answer questions about this technology stack. What would you like to know?",
                is_user=False
            )
            
            # Add a button to select this stack and create the document
            # Use unique ID for each button based on stack name to avoid duplicates
            button_id = f"select-stack-button-{selected_stack.get('id', '').replace(' ', '-')}"
            self.chat_widget.add_action_button(
                "Select This Technology Stack", 
                button_id, 
                "success",
                self._create_architecture_document
            )
        else:
            # Update existing chat widget title
            self.chat_widget.update_title(f"Technology Stack: {selected_stack['name']}")
            
            # Add a new message for this stack
            await self.chat_widget.add_message(
                f"# {selected_stack['name']}\n\n{selected_stack['description']}\n\n" +
                "I can answer questions about this technology stack. What would you like to know?",
                is_user=False
            )
            
            # Remove previous action buttons and add a new one for this stack
            self.chat_widget.clear_action_buttons()
            # Use unique ID for each button based on stack name to avoid duplicates
            button_id = f"select-stack-button-{selected_stack.get('id', '').replace(' ', '-')}"
            self.chat_widget.add_action_button(
                "Select This Technology Stack", 
                button_id, 
                "success",
                self._create_architecture_document
            )
        
        # Mark that we're using a research-based stack
        self.user_defined_stack = False
    
    @handle_async_errors
    async def _handle_technology_chat(self, message: str) -> None:
        """Handle chat messages about the technology stack."""
        try:
            # Show a loading indicator
            if hasattr(self.chat_widget, "add_message"):
                await self.chat_widget.add_message("_Processing your question..._", is_user=False)
            
            # Send the query to the architect for more details
            response = await self.architect.get_stack_details(
                self.session_id, 
                self.selected_stack['name'], 
                message
            )
            
            # Remove the loading message if it exists
            if hasattr(self.chat_widget, "remove_last_message"):
                self.chat_widget.remove_last_message()
            elif hasattr(self.chat_widget, "messages") and self.chat_widget.messages:
                if self.chat_widget.messages[-1] == "_Processing your question..._":
                    self.chat_widget.messages.pop()
            
            # Add the response to the chat
            await self.chat_widget.add_message(response, is_user=False)
            
        except Exception as e:
            logger.error(f"Error handling technology chat: {str(e)}")
            await self.chat_widget.add_message(
                f"I apologize, but I encountered an error while processing your question. Please try again.",
                is_user=False
            )
    
    @handle_async_errors
    async def _process_user_technologies(self) -> None:
        """Process the user-specified technologies."""
        technologies_input = self.query_one("#technologies-input")
        technologies_text = technologies_input.text
        
        if not technologies_text.strip():
            self.app.notify("Please describe your technology choices", severity="error")
            return
        
        # Process with the architect
        result = await self.architect.process_user_technologies(
            self.session_id, 
            technologies_text
        )
        
        if result["status"] == "success":
            self.selected_stack = result["technology_stack"]
            self.user_defined_stack = True
            
            # Create a chat widget for technology refinement
            if self.chat_widget is None:
                self.chat_widget = ChatWidget(
                    title="Technology Refinement",
                    on_message_callback=self._handle_technology_refinement,
                    header_display=True,
                    show_actions=True
                )
                
                details_container = self.query_one("#technology-details-container")
                details_container.remove_class("hidden")
                details_container.mount(self.chat_widget)
            
            # Add initial message with questions to refine the technologies
            await self.chat_widget.add_message(
                "Let's refine your technology choices to ensure we capture all necessary details:\n\n" +
                result["questions"],
                is_user=False
            )
            
            # Hide the input container
            self.query_one("#user-technologies-container").add_class("hidden")
            
            # Enable the continue button
            self.query_one("#continue-button").disabled = False
    
    @handle_async_errors
    async def _handle_technology_refinement(self, message: str) -> None:
        """Handle technology refinement conversation."""
        try:
            # Show a loading indicator
            if hasattr(self.chat_widget, "add_message"):
                await self.chat_widget.add_message("_Processing your response..._", is_user=False)
            
            # Send the message to the architect
            response = await self.architect.refine_user_technologies(
                self.session_id,
                message
            )
            
            # Remove the loading message if it exists
            if hasattr(self.chat_widget, "remove_last_message"):
                self.chat_widget.remove_last_message()
            elif hasattr(self.chat_widget, "messages") and self.chat_widget.messages:
                if self.chat_widget.messages[-1] == "_Processing your response..._":
                    self.chat_widget.messages.pop()
            
            # Add the response to the chat
            await self.chat_widget.add_message(response, is_user=False)
            
            # Check if technologies are complete
            architect_session = self.architect.sessions.get(self.session_id)
            if architect_session and architect_session.metadata.get("technologies_complete", False):
                # Update our local reference to the technologies
                self.selected_stack = architect_session.metadata.get("user_technology_stack", {})
                
                # Add a complete button to create the architecture document
                self.chat_widget.add_action_button(
                    "Create Final Architecture Document", 
                    "continue", 
                    "success",
                    self._create_architecture_document
                )
                
        except Exception as e:
            logger.error(f"Error handling technology refinement: {str(e)}")
            await self.chat_widget.add_message(
                f"I apologize, but I encountered an error while processing your response. Please try again.",
                is_user=False
            )
    
    @handle_async_errors
    async def _create_architecture_document(self) -> None:
        """Create the final architecture document based on the selected technologies."""
        if not self.selected_stack:
            self.notify("No technology stack selected", severity="error")
            return
            
        # Show a notification that document creation is in progress
        self.notify("Creating final architecture document, this may take a moment...", severity="information")
        
        try:
            # Generate the architecture document
            document_content = await self.architect.create_final_architecture_document(
                self.session_id,
                self.selected_stack
            )
            
            if document_content:
                # Save the document
                from ideasfactory.documents.document_manager import DocumentManager
                document_manager = DocumentManager()
                
                document_metadata = {
                    "title": "Final Architecture Document",
                    "display_title": "Final Architecture Document",
                    "document_type": "architecture",
                    "version": "1.0.0",
                    "source": "architect"
                }
                
                # Add session_id to metadata
                document_metadata["session_id"] = self.session_id
                
                # Use create_document instead of save_document
                document_path = document_manager.create_document(
                    content=document_content,
                    document_type="architecture",
                    title="Final Architecture Document",
                    metadata=document_metadata
                )
                
                # Add document to session
                current_session = self.session_manager.get_session(self.session_id)
                if current_session:
                    if "documents" not in current_session.metadata:
                        current_session.metadata["documents"] = {}
                    
                    current_session.metadata["documents"]["architecture"] = document_path
                    self.session_manager.update_session(self.session_id, current_session)
                
                # Success notification
                self.notify("Final architecture document created successfully", severity="success")
                
                # Show the document in the document review screen
                await self._show_architecture_document(document_content)
            else:
                self.notify("Failed to create final architecture document", severity="error")
                
        except Exception as e:
            logger.error(f"Error creating final architecture document: {str(e)}")
            self.notify(f"Error creating final architecture document: {str(e)}", severity="error")
    
    @handle_async_errors
    async def _show_architecture_document(self, document_content: str) -> None:
        """Show the architecture document in the document review screen."""
        # Use the document review screen to show the document
        if hasattr(self.app, "document_review_screen"):
            from ideasfactory.ui.screens.document_review_screen import DocumentSource
            
            # Configure the document review screen
            self.app.document_review_screen.configure_for_agent(
                document_source=DocumentSource.ARCHITECT,
                session_id=self.session_id,
                document_content=document_content,
                document_title="Final Architecture Document",
                document_type="architecture",
                revision_callback=self._revise_architecture_document,
                completion_callback=self._final_architecture_completion_callback,
                back_screen="architecture_technology_selection_screen"
            )
            
            # Show the document review screen
            self.app.push_screen("document_review_screen")
        else:
            self.notify("Document review screen not available", severity="error")
    
    @handle_async_errors
    async def _revise_architecture_document(self, feedback: str) -> None:
        """Handle revision requests for the architecture document."""
        try:
            # Notify that revision is in progress
            self.notify("Revising final architecture document...", severity="information")
            
            # Get the revised document
            revised_document = await self.architect.revise_final_document(self.session_id, feedback)
            
            if revised_document:
                # Update the document
                from ideasfactory.documents.document_manager import DocumentManager
                document_manager = DocumentManager()
                
                document_metadata = {
                    "title": "Final Architecture Document",
                    "display_title": "Final Architecture Document (Revised)",
                    "document_type": "architecture",
                    "version": "1.1.0",
                    "source": "architect"
                }
                
                # Add session_id to metadata
                document_metadata["session_id"] = self.session_id
                
                # Use create_document instead of save_document
                document_path = document_manager.create_document(
                    content=revised_document,
                    document_type="architecture",
                    title="Final Architecture Document (Revised)",
                    metadata=document_metadata
                )
                
                # Update document in session
                current_session = self.session_manager.get_session(self.session_id)
                if current_session:
                    if "documents" not in current_session.metadata:
                        current_session.metadata["documents"] = {}
                    
                    current_session.metadata["documents"]["architecture"] = document_path
                    self.session_manager.update_session(self.session_id, current_session)
                
                # Success notification
                self.notify("Final architecture document revised successfully", severity="success")
                
                # Show the revised document
                await self._show_architecture_document(revised_document)
            else:
                self.notify("Failed to revise final architecture document", severity="error")
                
        except Exception as e:
            logger.error(f"Error revising final architecture document: {str(e)}")
            self.notify(f"Error revising final architecture document: {str(e)}", severity="error")
    
    @handle_async_errors
    async def _continue_to_next_phase(self) -> None:
        """Continue to the next phase of the workflow."""
        # First check if we have a stack selected
        if not self.selected_stack:
            self.notify("Please select a technology stack first", severity="error")
            return
            
        # Check if we've already created the architecture document
        current_session = self.session_manager.get_session(self.session_id)
        document_exists = False
        
        if current_session and "documents" in current_session.metadata:
            document_exists = current_session.metadata.get("documents", {}).get("architecture") is not None
        
        # If document doesn't exist, create it first
        if not document_exists:
            await self._create_architecture_document()
            return
        
        # Document exists, store technology selection in the session
        if current_session:
            if "architecture" not in current_session.metadata:
                current_session.metadata["architecture"] = {}
            
            current_session.metadata["architecture"]["selected_technologies"] = self.selected_stack
            current_session.metadata["architecture"]["user_defined_stack"] = self.user_defined_stack
            
            self.session_manager.update_session(self.session_id, current_session)
            
            # Update workflow state
            self.session_manager.update_workflow_state(self.session_id, "architecture_completed")
        
        # Go to next phase (Standards Engineer)
        if hasattr(self.app, "push_screen") and hasattr(self.app, "tasks_creation_screen"):
            self.app.push_screen("tasks_creation_screen")
        else:
            # Fallback notification if the next screen is not available
            self.notify("Tasks creation screen not available. Architecture phase completed.", severity="information")