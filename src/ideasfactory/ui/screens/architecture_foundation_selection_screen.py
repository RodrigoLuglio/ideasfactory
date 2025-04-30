# src/ideasfactory/ui/screens/architecture_foundation_selection_screen.py

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

class ArchitectureFoundationSelectionScreen(BaseScreen):
    """Screen for selecting the foundation approach for the project with the Architect."""
    
    BINDINGS = [
        Binding(key="r", action="review_foundations", description="Review Foundations"),
        Binding(key="s", action="specify_foundation", description="Specify Foundation"),
        Binding(key="c", action="continue_workflow", description="Continue"),
    ]
    
    def __init__(self):
        """Initialize the foundation selection screen."""
        super().__init__()
        self.architect = Architect()
        self.session_manager = SessionManager()
        self.foundation_report = None
        self.foundation_path_reports = []
        self.chat_widget = None
        self.selected_foundation = None
        self.user_defined_foundation = False
        self.foundation_options = []
    
    def compose(self) -> ComposeResult:
        """Create child widgets for the screen."""
        yield Container(
            Label("Foundation Selection", id="foundation-title"),
            
            # Choice between research options and user-specified
            Container(
                Label("How would you like to select the foundation approach?", id="selection-method-prompt"),
                Button("Review Research Options", id="review-options-button", variant="primary"),
                Button("Specify My Own Foundation", id="specify-foundation-button", variant="warning"),
                id="selection-method-container"
            ),
            
            # Foundation options (initially hidden)
            Container(
                Label("Research Foundation Options", id="options-title"),
                VerticalScroll(
                    OptionList(id="foundation-options"),
                    id="options-scroll"
                ),
                Button("View Details", id="view-details-button", variant="primary", disabled=True),
                id="foundation-options-container",
                classes="hidden"
            ),
            
            # User foundation specification (initially hidden)
            Container(
                Label("Specify Your Foundation Approach", id="user-foundation-title"),
                TextArea(id="foundation-input"),
                Button("Submit", id="submit-foundation-button", variant="success"),
                id="user-foundation-container",
                classes="hidden"
            ),
            
            # Foundation details area (initially empty)
            Container(
                id="foundation-details-container",
                classes="hidden"
            ),
            
            # Action buttons
            Container(
                Button("Back to Research", id="back-button", variant="warning"),
                Button("Continue", id="continue-button", variant="success", disabled=True),
                id="action-buttons"
            ),
            id="foundation-decision-container"
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
        
        # Load research report
        foundation_report = await load_document_content(self.session_id, "foundation-research-report")
        if foundation_report:
            self.foundation_report = foundation_report
            
            # Get path reports directly from session metadata
            document_manager = DocumentManager()
            foundation_path_reports = {}
            
            # Get the current session
            current_session = self.session_manager.get_session(self.session_id)
            
            if current_session and "foundation_path_reports" in current_session.metadata:
                # Load foundation path reports from metadata references
                metadata_foundation_path_reports = current_session.metadata["foundation_path_reports"]
                logger.info(f"Found {len(metadata_foundation_path_reports)} foundation path reports in session metadata")
                
                for foundation_name, path in metadata_foundation_path_reports.items():
                    # Load each document from its stored path
                    doc = document_manager.get_document(path)
                    if doc:
                        foundation_path_reports[foundation_name] = doc
                        foundation_path_reports[foundation_name]["filepath"] = path
                        logger.info(f"  - Loaded foundation path report for: {foundation_name}")
            else:
                logger.info("No foundation path reports found in session metadata")
            
            self.foundation_path_reports = foundation_path_reports
            
            # Log foundation path reports found
            logger.info(f"Using {len(foundation_path_reports)} foundation path reports for session {self.session_id}")
            for path_name, report in foundation_path_reports.items():
                logger.info(f"  - {path_name}: {report.get('filepath')}")
            
            # Create an architect session if not already exists
            session = self.architect.sessions.get(self.session_id)
            if not session:
                # Load project vision and PRD
                project_vision = await load_document_content(self.session_id, "project-vision")
                prd_document = await load_document_content(self.session_id, "prd")
                foundation_report = await load_document_content(self.session_id, "foundation-research-report")
                
                # Create the architect session
                session = await self.architect.create_session(
                    self.session_id,
                    project_vision,
                    prd_document,
                    foundation_report
                )
                
                # Add path reports to architect session
                session.foundation_path_reports = foundation_path_reports
            else:
                # Update the session with the latest documents
                session.metadata["project_vision"] = project_vision 
                session.metadata["prd_document"] = prd_document
                session.metadata["foundation_report"] = foundation_report
                session.metadata["foundation_path_reports"] = foundation_path_reports
            
            # Extract foundation options
            await self._extract_foundation_options()
    
    @handle_async_errors
    async def _extract_foundation_options(self) -> None:
        """Extract foundation options from the research report."""
        if not self.foundation_report:
            return
        
        # Extract foundation options using the architect
        options = await self.architect.extract_foundation_options(self.session_id, self.foundation_report)
        
        # Populate the option list
        option_list = self.query_one("#foundation-options")
        
        # Clear existing options
        # The OptionList doesn't have a clear() method, so we need to clear it manually
        option_list.clear_options()
        
        for i, option in enumerate(options):
            # Create an Option object with text and ID
            option_obj = Option(f"{option['name']}", id=f"foundation-{i}")
            option_list.add_option(option_obj)
        
        # Store the options in the screen
        self.foundation_options = options
    
    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        button_id = event.button.id
        
        if button_id == "review-options-button":
            await self._show_foundation_options()
        
        elif button_id == "specify-foundation-button":
            await self._show_user_foundation_input()
        
        elif button_id == "view-details-button":
            await self._show_foundation_details()
        
        elif button_id == "submit-foundation-button":
            await self._process_user_foundation()
        
        elif button_id == "back-button":
            self.app.action_switch_to_foundation_research()
        
        elif button_id == "continue-button":
            # First check if we have a foundation selected
            if not self.selected_foundation:
                self.notify("Please select a foundation approach first", severity="error")
                return
                
            # Check if we've already created the architecture document
            current_session = self.session_manager.get_session(self.session_id)
            document_exists = False
            
            if current_session and "documents" in current_session.metadata:
                document_exists = current_session.metadata.get("documents", {}).get("generic-architecture") is not None
            
            # If document doesn't exist, create it first
            if not document_exists:
                await self._create_architecture_document()
                return
            
            # Document exists, store foundation selection in the session
            if current_session:
                if "architecture" not in current_session.metadata:
                    current_session.metadata["architecture"] = {}
                
                current_session.metadata["architecture"]["selected_foundation"] = self.selected_foundation
                current_session.metadata["architecture"]["user_defined_foundation"] = self.user_defined_foundation
                
                self.session_manager.update_session(self.session_id, current_session)
                
                # Update workflow state
                self.session_manager.update_workflow_state(self.session_id, "foundation_selected")
                
                # Generate technology research requirements via app method which will handle document review
                if hasattr(self.app, "_generic_architecture_completion_callback"):
                    await self.app._generic_architecture_completion_callback()
    
    @handle_async_errors
    async def _show_foundation_options(self) -> None:
        """Show the foundation options from research."""
        # Hide selection method container
        self.query_one("#selection-method-container").add_class("hidden")
        
        # Show foundation options container
        self.query_one("#foundation-options-container").remove_class("hidden")
    
    @handle_async_errors
    async def _show_user_foundation_input(self) -> None:
        """Show the user foundation input form."""
        # Hide selection method container
        self.query_one("#selection-method-container").add_class("hidden")
        
        # Show user foundation container
        self.query_one("#user-foundation-container").remove_class("hidden")
    
    async def on_option_list_option_selected(self, event) -> None:
        """Handle option selection in the foundation options list."""
        self.query_one("#view-details-button").disabled = False
    
    @handle_async_errors
    async def _show_foundation_details(self) -> None:
        """Show details for the selected foundation."""
        option_list = self.query_one("#foundation-options")
        selected_index = option_list.highlighted
        
        if selected_index is None or selected_index >= len(self.foundation_options):
            return
        
        selected_foundation = self.foundation_options[selected_index]
        self.selected_foundation = selected_foundation
        
        # If we don't have a chat widget yet, create one
        if self.chat_widget is None:
            # Create a chat widget for interactive foundation exploration
            self.chat_widget = ChatWidget(
                title=f"Foundation Details: {selected_foundation['name']}",
                on_message_callback=self._handle_foundation_chat,
                header_display=True,
                show_actions=True
            )
            
            details_container = self.query_one("#foundation-details-container")
            details_container.remove_class("hidden")
            details_container.mount(self.chat_widget)
            
            # Add initial message with foundation details
            await self.chat_widget.add_message(
                f"# {selected_foundation['name']}\n\n{selected_foundation['description']}\n\n" +
                "I can answer questions about this foundation approach. What would you like to know?",
                is_user=False
            )
            
            # Add a button to select this foundation and create the document
            # Use unique ID for each button based on foundation name to avoid duplicates
            button_id = f"select-foundation-button-{selected_foundation.get('id', '').replace(' ', '-')}"
            self.chat_widget.add_action_button(
                "Select This Foundation", 
                button_id, 
                "success",
                self._create_architecture_document
            )
        else:
            # Update existing chat widget title
            self.chat_widget.update_title(f"Foundation Details: {selected_foundation['name']}")
            
            # Add a new message for this foundation
            await self.chat_widget.add_message(
                f"# {selected_foundation['name']}\n\n{selected_foundation['description']}\n\n" +
                "I can answer questions about this foundation approach. What would you like to know?",
                is_user=False
            )
            
            # Remove previous action buttons and add a new one for this foundation
            self.chat_widget.clear_action_buttons()
            # Use unique ID for each button based on foundation name to avoid duplicates
            button_id = f"select-foundation-button-{selected_foundation.get('id', '').replace(' ', '-')}"
            self.chat_widget.add_action_button(
                "Select This Foundation", 
                button_id, 
                "success",
                self._create_architecture_document
            )
        
        # Mark that we're using a research-based foundation
        self.user_defined_foundation = False
    
    @handle_async_errors
    async def _handle_foundation_chat(self, message: str) -> None:
        """Handle chat messages about the foundation."""
        try:
            # Show a loading indicator
            if hasattr(self.chat_widget, "add_message"):
                await self.chat_widget.add_message("_Processing your question..._", is_user=False)
            
            # Send the query to the architect for more details
            response = await self.architect.get_foundation_details(
                self.session_id, 
                self.selected_foundation['name'], 
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
            logger.error(f"Error handling foundation chat: {str(e)}")
            await self.chat_widget.add_message(
                f"I apologize, but I encountered an error while processing your question. Please try again.",
                is_user=False
            )
    
    @handle_async_errors
    async def _process_user_foundation(self) -> None:
        """Process the user-specified foundation."""
        foundation_input = self.query_one("#foundation-input")
        foundation_text = foundation_input.text
        
        if not foundation_text.strip():
            self.app.notify("Please describe your foundation approach", severity="error")
            return
        
        # Process with the architect
        result = await self.architect.process_user_foundation(
            self.session_id, 
            foundation_text
        )
        
        if result["status"] == "success":
            self.selected_foundation = result["foundation"]
            self.user_defined_foundation = True
            
            # Create a chat widget for foundation refinement
            if self.chat_widget is None:
                self.chat_widget = ChatWidget(
                    title="Foundation Refinement",
                    on_message_callback=self._handle_foundation_refinement,
                    header_display=True,
                    show_actions=True
                )
                
                details_container = self.query_one("#foundation-details-container")
                details_container.remove_class("hidden")
                details_container.mount(self.chat_widget)
            
            # Add initial message with questions to refine the foundation
            await self.chat_widget.add_message(
                "Let's refine your foundation approach to ensure we capture all necessary details:\n\n" +
                result["questions"],
                is_user=False
            )
            
            # Hide the input container
            self.query_one("#user-foundation-container").add_class("hidden")
            
            # Enable the continue button
            self.query_one("#continue-button").disabled = False
    
    @handle_async_errors
    async def _handle_foundation_refinement(self, message: str) -> None:
        """Handle foundation refinement conversation."""
        try:
            if hasattr(self.chat_widget, "add_message"):
                await self.chat_widget.add_message("_Processing your response.._", is_user=False)

            # Send the message to the architect
            response = await self.architect.refine_user_foundation(
                self.session_id,
                self.selected_foundation["id"],
                message
            )
            
            if hasattr(self.chat_widget, "remove_last_message"):
                self.chat_widget.remove_last_message()
            elif hasattr(self.chat_widget, "messages") and self.chat_widget.messages:
                if self.chat_widget.messages[-1] == "_Processing your response..._":
                    self.chat_widget.messages.pop()

            # Add the response to the chat
            await self.chat_widget.add_message(response, is_user=False)

            architect_session = self.architect.sessions.get(self.session_id)
            if architect_session and architect_session.metadata.get("foundation_complete", False):
                self.selected_foundation = architect_session.metadata.get("user_foundation", {})

                self.chat_widget.add_action_button(
                    "Create Generic Architecture Document"
                    "continue",
                    "success",
                    self._create_architecture_document
                )

        except Exception as e:
            logger.error(f"Error handling foundation refinement: {str(e)}")
            await self.chat_widget.add_message(
                f"I apologize, but I encoutered an error while processing your response. Please try again.",
                is_user=False
            )
    
    @handle_async_errors
    async def _create_architecture_document(self) -> None:
        """Create the generic architecture document based on the selected foundation."""
        if not self.selected_foundation:
            self.notify("No foundation selected", severity="error")
            return
            
        # Show a notification that document creation is in progress
        self.notify("Creating generic architecture document, this may take a moment...", severity="information")
        
        try:
            # Ensure architecture metadata structure exists in the session
            current_session = self.session_manager.get_session(self.session_id)
            if current_session and "architecture" not in current_session.metadata:
                current_session.metadata["architecture"] = {}
            
            # Store selected foundation in metadata
            current_session.metadata["architecture"]["selected_foundation"] = self.selected_foundation
            current_session.metadata["architecture"]["user_defined_foundation"] = self.user_defined_foundation
            self.session_manager.update_session(self.session_id, current_session)

            # Generate the architecture document
            document_content = await self.architect.create_generic_architecture_document(
                self.session_id,
                self.selected_foundation
            )
            
            if document_content:
                # Save the document
                from ideasfactory.documents.document_manager import DocumentManager
                document_manager = DocumentManager()
                
                document_metadata = {
                    "title": "Generic Architecture Document",
                    "display_title": "Generic Architecture Document",
                    "document_type": "generic-architecture",
                    "version": "1.0.0",
                    "source": "architect"
                }
                
                # Add session_id to metadata
                document_metadata["session_id"] = self.session_id
                
                # Use create_document instead of save_document
                document_path = document_manager.create_document(
                    content=document_content,
                    document_type="generic-architecture",
                    title="Generic Architecture Document",
                    metadata=document_metadata
                )
                
                # Add document to session
                current_session = self.session_manager.get_session(self.session_id)
                if current_session:
                    if "documents" not in current_session.metadata:
                        current_session.metadata["documents"] = {}
                    
                    current_session.metadata["documents"]["generic-architecture"] = document_path
                    self.session_manager.update_session(self.session_id, current_session)
                
                # Success notification
                self.notify("Generic architecture document created successfully", severity="success")
                
                # Show the document in the document review screen
                await self._show_architecture_document(document_content)
            else:
                self.notify("Failed to create architecture document", severity="error")
                
        except Exception as e:
            logger.error(f"Error creating generic architecture document: {str(e)}")
            self.notify(f"Error creating generic architecture document: {str(e)}", severity="error")
    
    @handle_async_errors
    async def _show_architecture_document(self, document_content: str) -> None:
        """Show the generic architecture document in the document review screen."""
        # Use the document review screen to show the document
        if hasattr(self.app, "document_review_screen"):
            from ideasfactory.ui.screens.document_review_screen import DocumentSource
            
            # Configure the document review screen
            self.app.document_review_screen.configure_for_agent(
                document_source=DocumentSource.ARCHITECT,
                session_id=self.session_id,
                document_content=document_content,
                document_title="Generic Architecture Document",
                document_type="generic-architecture",
                revision_callback=self._revise_architecture_document,
                completion_callback=self.app._generic_architecture_completion_callback,
                back_screen="foundation_selection_screen"
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
            self.notify("Revising generic architecture document...", severity="information")
            
            # Get the revised document
            revised_document = await self.architect.revise_document(self.session_id, feedback)
            
            if revised_document:
                # Update the document
                from ideasfactory.documents.document_manager import DocumentManager
                document_manager = DocumentManager()
                
                document_metadata = {
                    "title": "Generic Architecture Document",
                    "display_title": "Generic Architecture Document (Revised)",
                    "document_type": "generic-architecture",
                    "version": "1.1.0",
                    "source": "architect"
                }
                
                # Add session_id to metadata
                document_metadata["session_id"] = self.session_id
                
                # Use create_document instead of save_document
                document_path = document_manager.create_document(
                    content=revised_document,
                    document_type="generic-architecture",
                    title="Generic Architecture Document (Revised)",
                    metadata=document_metadata
                )
                
                # Update document in session
                current_session = self.session_manager.get_session(self.session_id)
                if current_session:
                    if "documents" not in current_session.metadata:
                        current_session.metadata["documents"] = {}
                    
                    current_session.metadata["documents"]["generic-architecture"] = document_path
                    self.session_manager.update_session(self.session_id, current_session)
                
                # Success notification
                self.notify("Generic architecture document revised successfully", severity="success")
                
                # Show the revised document
                await self._show_architecture_document(revised_document)
            else:
                self.notify("Failed to revise generic architecture document", severity="error")
                
        except Exception as e:
            logger.error(f"Error revising generic architecture document: {str(e)}")
            self.notify(f"Error revising generic architecture document: {str(e)}", severity="error")
    
    @handle_async_errors
    async def _continue_to_technology_selection(self) -> None:
        """Continue to the technology selection screen."""
        # First check if we have a foundation selected
        if not self.selected_foundation:
            self.notify("Please select a foundation approach first", severity="error")
            return
            
        # Check if we've already created the architecture document
        current_session = self.session_manager.get_session(self.session_id)
        document_exists = False
        
        if current_session and "documents" in current_session.metadata:
            document_exists = current_session.metadata.get("documents", {}).get("generic-architecture") is not None
        
        # If document doesn't exist, create it first
        if not document_exists:
            await self._create_architecture_document()
            return
        
        # Document exists, store foundation selection in the session
        if current_session:
            if "generic-architecture" not in current_session.metadata:
                current_session.metadata["generic-architecture"] = {}
            
            current_session.metadata["generic-architecture"]["selected_foundation"] = self.selected_foundation
            current_session.metadata["generic-architecture"]["user_defined_foundation"] = self.user_defined_foundation
            
            self.session_manager.update_session(self.session_id, current_session)
            
            # Update workflow state
            self.session_manager.update_workflow_state(self.session_id, "foundation_selected")
        
        # Go to technology research requirements screen
        if hasattr(self.app, "push_screen") and hasattr(self.app, "architecture_technology_research_requirements_screen"):
            self.app.push_screen("technology_research_requirements_screen")
        else:
            # Fallback notification if the technology research requirements screen is not available
            self.notify("Technology research requirements screen not available.", severity="information")
            