# In src/ideasfactory/ui/widgets/chat_widget.py

"""
Enhanced chat widget for IdeasFactory UI.
"""

import logging
import asyncio
from typing import Optional, Dict, Any, List, Callable, Union
from asyncio import create_task

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Button, TextArea, Static, Label, RichLog
from textual.reactive import reactive
from textual.css.query import NoMatches
from rich.style import Style
from rich.console import Console


from ideasfactory.utils.error_handler import handle_errors, handle_async_errors

# Configure logging
logger = logging.getLogger(__name__)

class EnhancedChatInput(Container):
    """Enhanced input area for the chat with multiline support."""
    
    def __init__(self, on_message_callback: Optional[Callable[[str], None]] = None, **kwargs):
        """Initialize the chat input."""
        super().__init__(**kwargs)
        self.on_message_callback = on_message_callback
    
    def compose(self) -> ComposeResult:
        """Create child widgets for the input."""
        yield TextArea(id="input-area")
        
        with Horizontal():
            yield Button("Send", id="send-button", variant="primary")
    
    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "send-button":
            await self.send_message()
    
    async def on_key(self, event) -> None:
        """Handle key events."""
        # Allow Ctrl+Enter to send message
        if event.key == "ctrl+enter":
            await self.send_message()
    
    @handle_async_errors
    async def send_message(self) -> None:
        """Send the message and clear the input."""
        try:
            input_area = self.query_one("#input-area", TextArea)
            message = input_area.text.strip()
            
            if message:
                # Clear the input area
                input_area.text = ""
                
                # Call the callback if provided
                if self.on_message_callback:
                    await self.on_message_callback(message)
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")

class ChatActions(Container):
    """Container for chat action buttons."""

class ChatWidget(Container):
    """Reusable chat widget with support for rich artifacts."""
    
    def __init__(
        self,
        title: str = "Chat Session",
        on_message_callback: Optional[Callable[[str], None]] = None, 
        header_display: bool = True,
        show_actions: bool = True,
        **kwargs
    ):
        """Initialize the chat widget."""
        super().__init__(**kwargs)
        self.title = title
        self._message_callback = on_message_callback
        self.header_display = header_display
        self.show_actions = show_actions
        
        # FIXED: Renamed to avoid conflict with Textual's internal _message_queue
        # Message queue for messages added before widget is fully mounted
        self._pending_messages = []
        self._is_mounted = False
        
    def compose(self) -> ComposeResult:
        """Create child widgets for the chat."""
        # Chat header (optional)
        if self.header_display:
            yield Label(self.title, id="chat-header")
        
        # Message list in a rich log
        yield RichLog(id="message-list", auto_scroll=True, markup=True, wrap=True)
        
        # Input area at the bottom
        yield EnhancedChatInput(on_message_callback=self.handle_message_sent)
        
        # Actions container (optional)
        if self.show_actions:
            yield ChatActions()
    
    def on_mount(self) -> None:
        """Handle the widget being mounted."""
        logger.info("ChatWidget mounted")
        self._is_mounted = True
        
        # Process any queued messages
        if self._pending_messages:
            # Use create_task to process after current event handler completes
            asyncio.create_task(self._process_pending_messages())
    
    @handle_async_errors
    async def _process_pending_messages(self) -> None:
        """Process messages queued before widget was fully mounted."""
        # Small delay to ensure components are ready
        await asyncio.sleep(0.1)
        
        logger.info(f"Processing {len(self._pending_messages)} queued messages")
        
        for msg in self._pending_messages:
            await self._add_message_impl(
                content=msg["content"],
                is_user=msg["is_user"]
            )
        
        # Clear the queue
        self._pending_messages = []
    
    @handle_async_errors
    async def handle_message_sent(self, message: str) -> None:
        """Handle messages from the input area."""
        # Add user message to the chat
        await self.add_message(message, is_user=True)
        
        # Call the callback if provided
        if self._message_callback:
            await self._message_callback(message)
    
    @handle_async_errors
    async def add_message(self, content: str, is_user: bool = False) -> None:
        """Add a new message to the chat."""
        if not self._is_mounted:
            # Queue the message if widget isn't mounted yet
            logger.info(f"Queuing message: {content[:20]}...")
            self._pending_messages.append({
                "content": content,
                "is_user": is_user
            })
            return
        
        # If mounted, add the message directly
        await self._add_message_impl(content, is_user)
    
    @handle_async_errors
    async def _add_message_impl(self, content: str, is_user: bool = False) -> None:
        """Internal implementation to add a message to the chat."""
        try:
            # Get the message list (RichLog)
            message_list = self.query_one(RichLog)
            
            # Format the message with appropriate styling
            # Determine sender
            if is_user:
                # User message style
                sender_style = Style(bold=True)
                sender = f"[{sender_style}]You:[{sender_style}]"
                content_style = Style(bold=False)
                message_style = Style(color="grey66")
            else:
                # Agent message style
                sender_style = Style(bold=True)
                sender = f"[{sender_style}]Agent:[{sender_style}]"
                content_style = Style(bold=False)
                message_style = Style(color="grey93")


            # Create a formatted message with Rich markup
            formatted_message = f"\n[{message_style}]{sender}\n[{content_style}]{content}[{content_style}][{message_style}]\n"
            
            # Write to the RichLog
            message_list.write(formatted_message)
            
        except NoMatches as e:
            logger.error(f"Error finding message list: {str(e)}")
        except Exception as e:
            logger.error(f"Error adding message to chat: {str(e)}")
    
    def add_action_button(self, label: str, id: str, variant: str = "primary", callback: Optional[Callable] = None) -> None:
        """Add an action button to the chat."""
        if not self.show_actions:
            logger.warning("Cannot add action button: actions are disabled")
            return
            
        try:
            # Find the actions container
            actions = self.query_one(ChatActions)
            
            # Create and mount the button
            button = Button(label, id=id, variant=variant)
            actions.mount(button)
            
            # Store callback
            if callback:
                # Will be called by the on_button_pressed handler
                button.callback = callback
                
        except NoMatches:
            logger.error("Actions container not found")
        except Exception as e:
            logger.error(f"Error adding action button: {str(e)}")
            
    def clear_action_buttons(self) -> None:
        """Remove all action buttons from the chat widget."""
        if not self.show_actions:
            return
            
        try:
            # Find the actions container
            actions = self.query_one(ChatActions)
            
            # Remove all buttons
            for button in actions.query("Button"):
                button.remove()
                
        except NoMatches:
            logger.error("Actions container not found")
        except Exception as e:
            logger.error(f"Error clearing action buttons: {str(e)}")
            
    def update_title(self, new_title: str) -> None:
        """Update the chat widget's title and header."""
        self.title = new_title
        
        if not self.header_display:
            return
            
        try:
            # Find and update the header label
            header = self.query_one("#chat-header", Label)
            header.update(new_title)
        except NoMatches:
            logger.error("Chat header not found")
        except Exception as e:
            logger.error(f"Error updating chat header: {str(e)}")
    
    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        # Check if button has a callback
        if hasattr(event.button, "callback") and event.button.callback is not None:
            # Call the callback
            if asyncio.iscoroutinefunction(event.button.callback):
                await event.button.callback()
            else:
                event.button.callback()