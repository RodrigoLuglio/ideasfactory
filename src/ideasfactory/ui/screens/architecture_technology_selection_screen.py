# src/ideasfactory/ui/screens/technology_selection_screen.py

import logging
from typing import Optional, List, Dict, Any
import asyncio

from textual.app import ComposeResult
from textual.widgets import Button, Static, Label, OptionList, Input, TextArea, RadioSet, RadioButton
from textual.containers import Container, VerticalScroll, Horizontal
from textual.binding import Binding

from ideasfactory.ui.screens.base_screen import BaseScreen
from ideasfactory.ui.widgets.chat_widget import ChatWidget
from ideasfactory.agents.architect import Architect
from ideasfactory.utils.error_handler import handle_async_errors
from ideasfactory.utils.session_manager import SessionManager

# Configure logging
logger = logging.getLogger(__name__)

class TechnologySelectionScreen(BaseScreen):
    """Screen for selecting technologies based on the chosen foundation."""
    
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
        self.chat_widget = None
        self.selected_foundation = None
        self.technology_categories = []
        self.selected_technologies = {}
        self.user_defined_technologies = False
    
    def compose(self) -> ComposeResult:
        """Create child widgets for the screen."""
        yield Container(
            Label("Technology Stack Selection", id="technology-title"),
            
            # Foundation summary
            Container(
                Label("Selected Foundation Approach:", id="foundation-summary-label"),
                Static(id="foundation-summary"),
                id="foundation-summary-container"
            ),
            
            # Choice between research options and user-specified
            Container(
                Label("How would you like to select technologies?", id="selection-method-prompt"),
                Button("Review Technology Options", id="review-options-button", variant="primary"),
                Button("Specify My Own Technologies", id="specify-technologies-button", variant="warning"),
                id="selection-method-container"
            ),
            
            # Technology categories (initially hidden)
            Container(
                Label("Technology Categories", id="categories-title"),
                VerticalScroll(
                    id="categories-container"
                ),
                id="technology-selection-container",
                classes="hidden"
            ),
            
            # User technology specification (initially hidden)
            Container(
                Label("Specify Your Technologies", id="user-technologies-title"),
                TextArea(id="technologies-input", placeholder="Describe your technology choices..."),
                Button("Submit", id="submit-technologies-button", variant="success"),
                id="user-technologies-container",
                classes="hidden"
            ),
            
            # Technology details area (for chat-based interaction)
            Container(
                id="technology-details-container",
                classes="hidden"
            ),
            
            # Action buttons
            Container(
                Button("Back to Foundation Selection", id="back-button", variant="warning"),
                Button("Create Architecture Document", id="create-document-button", variant="success", disabled=True),
                id="action-buttons"
            )
        )
    
    def on_mount(self) -> None:
        """Handle the screen's mount event."""
        super().on_mount()
        if self.session_id:
            asyncio.create_task(self._load_session_data())
    
    @handle_async_errors
    async def _load_session_data(self) -> None:
        """Load session data including the selected foundation."""
        if not self.session_id:
            return
        
        # Get the session
        current_session = self.session_manager.get_session(self.session_id)
        
        if current_session and "architecture" in current_session.metadata:
            arch_metadata = current_session.metadata["architecture"]
            
            # Load the selected foundation
            if "selected_foundation" in arch_metadata:
                self.selected_foundation = arch_metadata["selected_foundation"]
                self.user_defined_foundation = arch_metadata.get("user_defined_foundation", False)
                
                # Update foundation summary
                foundation_summary = self.query_one("#foundation-summary")
                foundation_summary.update(f"**{self.selected_foundation['name']}**\n{self.selected_foundation['description'][:150]}...")
                
                # Load technology categories based on the foundation
                await self._load_technology_categories()
    
    @handle_async_errors
    async def _load_technology_categories(self) -> None:
        """Load technology categories based on the selected foundation."""
        if not self.selected_foundation:
            return
        
        # Get technology categories from the architect
        categories = await self.architect.get_technology_categories(
            self.session_id,
            self.selected_foundation["id"]
        )
        
        self.technology_categories = categories
    
    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        button_id = event.button.id
        
        if button_id == "review-options-button":
            await self._show_technology_options()
        
        elif button_id == "specify-technologies-button":
            await self._show_user_technology_input()
        
        elif button_id == "submit-technologies-button":
            await self._process_user_technologies()
        
        elif button_id == "back-button":
            self.app.pop_screen()
        
        elif button_id == "create-document-button":
            await self._create_architecture_document()
        
        elif button_id.startswith("category-"):
            category_id = button_id.replace("category-", "")
            await self._show_technology_selection(category_id)
    
    @handle_async_errors
    async def _show_technology_options(self) -> None:
        """Show the technology options for selection."""
        # Hide selection method container
        self.query_one("#selection-method-container").add_class("hidden")
        
        # Show technology selection container
        self.query_one("#technology-selection-container").remove_class("hidden")
        
        # Create buttons for each technology category
        categories_container = self.query_one("#categories-container")
        
        for i, category in enumerate(self.technology_categories):
            # Create a container for this category
            category_button = Button(
                f"{category['name']}", 
                id=f"category-{i}",
                variant="primary"
            )
            categories_container.mount(category_button)
    
    @handle_async_errors
    async def _show_technology_selection(self, category_id: str) -> None:
        """Show technology selection for a specific category."""
        category_index = int(category_id)
        
        if category_index >= len(self.technology_categories):
            return
            
        category = self.technology_categories[category_index]
        
        # Create a dialog for selecting technologies in this category
        # If we don't have a chat widget yet, create one
        if self.chat_widget is None:
            self.chat_widget = ChatWidget(
                title=f"Technology Selection: {category['name']}",
                on_message_callback=self._handle_technology_chat,
                header_display=True,
                show_actions=True
            )
            
            details_container = self.query_one("#technology-details-container")
            details_container.remove_class("hidden")
            details_container.mount(self.chat_widget)
        
        # Load technology options for this category
        options = await self.architect.get_technology_options(
            self.session_id,
            self.selected_foundation["id"],
            category["id"]
        )
        
        # Present options in the chat
        option_text = f"# {category['name']} Options\n\n"
        option_text += f"{category['description']}\n\n"
        option_text += "Please select one of the following options:\n\n"
        
        for i, option in enumerate(options):
            option_text += f"**{i+1}. {option['name']}**: {option['description'][:100]}...\n\n"
        
        option_text += "\nYou can ask for more details about any option by typing its number or name."
        
        # Store the current category and options
        self.current_category = category
        self.current_options = options
        
        # Add the message
        await self.chat_widget.add_message(option_text, is_user=False)
    
    @handle_async_errors
    async def _handle_technology_chat(self, message: str) -> None:
        """Handle chat messages about technologies."""
        # Check if the message is a selection
        try:
            # Check if the message is a number
            option_num = int(message.strip())
            
            if 1 <= option_num <= len(self.current_options):
                # This is a selection
                selected_option = self.current_options[option_num - 1]
                
                # Store the selection
                if "id" not in self.current_category:
                    self.current_category["id"] = f"category-{self.technology_categories.index(self.current_category)}"
                
                self.selected_technologies[self.current_category["id"]] = selected_option
                
                # Confirm the selection
                confirmation = f"You've selected **{selected_option['name']}** for {self.current_category['name']}.\n\n"
                
                # Check if all categories have selections
                if len(self.selected_technologies) == len(self.technology_categories):
                    confirmation += "You've now selected technologies for all categories. You can continue to the architecture document creation."
                    # Enable the create document button
                    self.query_one("#create-document-button").disabled = False
                else:
                    # Count how many are left
                    remaining = len(self.technology_categories) - len(self.selected_technologies)
                    confirmation += f"You still need to select technologies for {remaining} more categories."
                
                await self.chat_widget.add_message(confirmation, is_user=False)
                return
        except ValueError:
            # Not a number selection, continue with normal flow
            pass
        
        # Get more details about the option
        response = await self.architect.get_technology_option_details(
            self.session_id,
            self.current_category["id"],
            message
        )
        
        await self.chat_widget.add_message(response, is_user=False)
    
    @handle_async_errors
    async def _show_user_technology_input(self) -> None:
        """Show the user technology input form."""
        # Hide selection method container
        self.query_one("#selection-method-container").add_class("hidden")
        
        # Show user technologies container
        self.query_one("#user-technologies-container").remove_class("hidden")
    
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
            self.selected_foundation["id"],
            technologies_text
        )
        
        if result["status"] == "success":
            self.selected_technologies = result["technologies"]
            self.user_defined_technologies = True
            
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
            
            # Enable the create document button
            self.query_one("#create-document-button").disabled = False
    
    @handle_async_errors
    async def _handle_technology_refinement(self, message: str) -> None:
        """Handle technology refinement conversation."""
        # Send the message to the architect
        response = await self.architect.refine_user_technologies(
            self.session_id,
            message
        )
        
        # Add the response to the chat
        await self.chat_widget.add_message(response, is_user=False)
    
    @handle_async_errors
    async def _create_architecture_document(self) -> None:
        """Create the architecture document."""
        # Store the selected technologies in the session
        current_session = self.session_manager.get_session(self.session_id)
        
        if current_session:
            if "architecture" not in current_session.metadata:
                current_session.metadata["architecture"] = {}
            
            current_session.metadata["architecture"]["selected_technologies"] = self.selected_technologies
            current_session.metadata["architecture"]["user_defined_technologies"] = self.user_defined_technologies
            
            self.session_manager.update_session(self.session_id, current_session)
            
            # Update workflow state
            self.session_manager.update_workflow_state(self.session_id, "technologies_selected")
        
        # Create the architecture document
        document = await self.architect.create_architecture_document(
            self.session_id,
            self.selected_foundation,
            self.selected_technologies
        )
        
        if document:
            # Show the document in the document review screen
            if hasattr(self.app, "show_document_review_for_architect"):
                await self.app.show_document_review_for_architect(self.session_id)
            else:
                self.app.notify("Architecture document created but review not available", severity="warning")