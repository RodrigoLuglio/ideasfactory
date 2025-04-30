"""
Technology Research screen for IdeasFactory.

This module implements the UI for the technology research phase, using the technology
research team to explore implementation options for the selected foundation approach.
"""

import logging
from typing import Optional, List, Dict, Any, Callable
import asyncio

from textual.app import ComposeResult
from textual.widgets import Button, Static, Markdown, Label, LoadingIndicator, MarkdownViewer
from textual.containers import VerticalScroll, Horizontal, Container
from textual.reactive import reactive
from textual import on
from textual.worker import Worker, get_current_worker

from ideasfactory.ui.screens.base_screen import BaseScreen
from ideasfactory.agents.technology_research_team import TechnologyResearchTeam, TechnologyResearchSession
from ideasfactory.utils.file_manager import load_document_content
from ideasfactory.utils.error_handler import handle_errors, handle_async_errors
from ideasfactory.utils.session_manager import SessionManager


# Configure logging
logger = logging.getLogger(__name__)


class ResearchPhaseLabel(Static):
    """A label that displays a research phase with status."""
    
    def __init__(self, phase_name: str, description: str, status: str = "pending"):
        """Initialize the research phase label.
        
        Args:
            phase_name: Name of the research phase
            description: Description of the research phase
            status: Status of the phase (pending, in_progress, completed)
        """
        self.phase_name = phase_name
        self.description = description
        self.phase_status = status
        super().__init__("")
        self.update_display()
    
    def update_status(self, status: str) -> None:
        """Update the status of the phase.
        
        Args:
            status: New status
        """
        self.phase_status = status
        self.update_display()
    
    def update_display(self) -> None:
        """Update the display based on current status."""
        status_color = {
            "pending": "gray",
            "in_progress": "yellow",
            "completed": "green"
        }.get(self.phase_status, "gray")
        
        status_symbol = {
            "pending": "○",
            "in_progress": "◔",
            "completed": "●"
        }.get(self.phase_status, "○")
        
        self.update(f"[{status_color}]{status_symbol}[/] {self.phase_name}: {self.description}")


class ResearchProgressBar(Static):
    """A progress bar for the research process."""
    
    progress = reactive(0.0)
    
    def __init__(self, total_phases: int = 5):
        """Initialize the progress bar.
        
        Args:
            total_phases: Total number of phases
        """
        self.total_phases = total_phases
        super().__init__("")
        self.update_progress_display()
    
    def update_progress(self, completed_phases: int) -> None:
        """Update the progress based on completed phases.
        
        Args:
            completed_phases: Number of completed phases
        """
        self.progress = min(1.0, completed_phases / self.total_phases)
        self.update_progress_display()
    
    def update_progress_display(self) -> None:
        """Update the progress display."""
        bar_width = 50
        completed_chars = int(bar_width * self.progress)
        remaining_chars = bar_width - completed_chars
        
        bar = f"[green]{'█' * completed_chars}[/][gray]{'█' * remaining_chars}[/]"
        percentage = f"{int(self.progress * 100)}%"
        
        self.update(f"{bar} {percentage}")


class TechnologyResearchScreen(BaseScreen):
    """
    Screen for the technology research phase of IdeasFactory.
    
    This screen allows users to start and monitor the technology
    research process, which explores implementation options for
    the selected foundation approach.
    """
    
    BINDINGS = [
        ("escape", "app.pop_screen", "Back"),
        ("r", "start_research", "Start Research"),
        ("v", "view_results", "View Results"),
        ("a", "go_to_architecture", "Go to Architecture"),
        ("t", "view_requirements", "View Requirements"),
    ]
    
    def __init__(self):
        """Initialize the technology research screen."""
        super().__init__()
        self.research_team = TechnologyResearchTeam()
        self.session_manager = SessionManager()
        
        # UI state tracking
        self.session_id: Optional[str] = None
        self.technology_requirements: Optional[str] = None
        self.generic_architecture: Optional[str] = None
        self.foundation_approach: Optional[Dict[str, Any]] = None
        self.current_phase: str = "technology_discovery"
        self.research_progress: Dict[str, str] = {
            "technology_discovery": "pending",
            "technology_exploration": "pending",
            "stack_creation": "pending",
            "integration_exploration": "pending",
            "research_synthesis": "pending"
        }
        self.technology_report_path: Optional[str] = None
        self.research_is_running = False
    
    def compose(self) -> ComposeResult:
        """Create child widgets for the screen."""

        yield Container(
            Label("Technology Stack Research", id="research-title"),

            Markdown("", id="preview-content"),
                        
            Button("View Technology Requirements Document", id="view-requirements"),
            Button("View Generic Architecture Document", id="view-architecture"),
            Button("View Selected Foundation", id="view-foundation"),
                        
            Container(
                Label("Research Status", classes="section-header"),
                ResearchProgressBar(total_phases=5),
                
                VerticalScroll(
                    ResearchPhaseLabel(
                        "Technology Discovery", 
                        "Discover potential technologies for each component",
                        "pending"
                    ),
                    ResearchPhaseLabel(
                        "Technology Exploration", 
                        "Explore key technologies across paradigm spectrum",
                        "pending"
                    ),
                    ResearchPhaseLabel(
                        "Stack Creation", 
                        "Generate technology stacks for the selected foundation",
                        "pending"
                    ),
                    ResearchPhaseLabel(
                        "Integration Exploration", 
                        "Identify cross-technology integration patterns",
                        "pending"
                    ),
                    ResearchPhaseLabel(
                        "Research Synthesis", 
                        "Create comprehensive technology report",
                        "pending"
                    ),
                    id="research-phases"
                ),

                id="research-status"
            ),
            Button("Start Technology Research", id="start-research"),

            Container(
                Button("View Technology Report", id="view-report", disabled=True),
                Button("Continue to Technology Selection", id="go-to-architecture", disabled=True),
                
                id="research-actions"
            ),
            LoadingIndicator(id="research-loading", classes="hidden"),
        
            id="research-container"
        )
    
    
    def on_mount(self) -> None:
        """Handle the mount event to initialize the screen."""
        super().on_mount()
        # Add screen styles
        self.styles.align = ("center", "middle")
        self.update_phase_display()
        
    @handle_async_errors
    async def on_screen_resume(self) -> None:
        """Handle screen being resumed."""
        # Call the base class implementation which handles session retrieval
        await super().on_screen_resume()
        
        # Make sure we log this event for debugging
        logger.info(f"Technology research screen resumed with session ID: {self.session_id}")
        
        # If we have a session but no documents, try to load them
        if self.session_id and not self.technology_requirements:
            logger.info("No technology requirements loaded, attempting to load documents")
            await self._load_session_documents()
    
    @handle_errors
    def set_session(self, session_id: str) -> None:
        """Set the current session ID.
        
        Args:
            session_id: Session ID to set
        """
        # Follow the standard BaseScreen pattern
        super().set_session(session_id)
        logger.info(f"Technology research screen session set to: {session_id}")
    
    @handle_async_errors
    async def _load_session_documents(self) -> None:
        """Load documents for the current session following BaseScreen pattern."""
        if not self.session_id:
            return
            
        # Show loading indicator
        if self._is_mounted:
            self.query_one("#research-loading", LoadingIndicator).remove_class("hidden")
        
        try:
            # Use the centralized document loading utility
            from ideasfactory.utils.file_manager import load_document_content
            
            # Load technology requirements document
            technology_requirements_content = await load_document_content(self.session_id, "technology-requirements")
            if technology_requirements_content:
                logger.info(f"Successfully loaded technology requirements - Length: {len(technology_requirements_content)}")
                self.technology_requirements = technology_requirements_content
            else:
                logger.error(f"Failed to load technology requirements for session {self.session_id}")
            
            # Load generic architecture document
            generic_architecture_content = await load_document_content(self.session_id, "architecture")
            if generic_architecture_content:
                logger.info(f"Successfully loaded generic architecture - Length: {len(generic_architecture_content)}")
                self.generic_architecture = generic_architecture_content
            else:
                logger.error(f"Failed to load generic architecture for session {self.session_id}")
            
            # Load foundation approach from session metadata
            session_data = self.session_manager.get_session(self.session_id)
            if session_data and "architecture" in session_data.metadata and "selected_foundation" in session_data.metadata["architecture"]:
                self.foundation_approach = session_data.metadata["architecture"]["selected_foundation"]
                logger.info(f"Found selected foundation: {self.foundation_approach.get('name', 'Unknown')}")
            else:
                logger.error(f"Failed to load selected foundation for session {self.session_id}")
                
            # Update UI with document information
            if self._is_mounted:
                if self.technology_requirements:
                    self.query_one("#preview-content", Markdown).update(self.technology_requirements)
            
            # Load technology report if it exists
            technology_report_content = await load_document_content(self.session_id, "technology-research-report")
            if technology_report_content:
                logger.info(f"Successfully loaded technology report - Length: {len(technology_report_content)}")
                # Store the report path for future reference
                self.technology_report_path = self.session_manager.get_document(self.session_id, "technology-research-report")
                
                if self._is_mounted:
                    self.query_one("#view-report", Button).disabled = False
                    self.query_one("#go-to-architecture", Button).disabled = False
                    
                    # Update progress to show completion
                    for phase in self.research_progress:
                        self.research_progress[phase] = "completed"
                    self.update_phase_display()
            else:
                logger.info("No technology report available yet")
        except Exception as e:
            logger.error(f"Error loading session documents: {str(e)}")
            if self._is_mounted:
                self.app.notify(f"Error loading session documents: {str(e)}", severity="error")
        finally:
            # Hide loading indicator
            if self._is_mounted:
                self.query_one("#research-loading", LoadingIndicator).add_class("hidden")
    
    @handle_errors
    def update_phase_display(self) -> None:
        """Update the display of all research phases."""
        # Update phase labels
        phase_widgets = self.query_one("#research-phases").query(ResearchPhaseLabel)
        phases = list(self.research_progress.keys())
        
        for i, widget in enumerate(phase_widgets):
            if i < len(phases):
                phase = phases[i]
                widget.update_status(self.research_progress[phase])
        
        # Update progress bar
        completed_count = sum(1 for status in self.research_progress.values() if status == "completed")
        self.query_one(ResearchProgressBar).update_progress(completed_count)
        
        # Update button states
        if self.technology_report_path:
            self.query_one("#view-report", Button).disabled = False
            self.query_one("#go-to-architecture", Button).disabled = False
        else:
            self.query_one("#view-report", Button).disabled = True
            self.query_one("#go-to-architecture", Button).disabled = True
    
    @on(Button.Pressed, "#start-research")
    def handle_start_research(self) -> None:
        """Handle the start research button press by starting worker."""
        if not self.session_id:
            self.app.notify("No active session", severity="error")
            return
        
        if not self.technology_requirements or not self.generic_architecture or not self.foundation_approach:
            self.app.notify("Missing required documents for technology research", severity="error")
            return
        
        if self.research_is_running:
            self.app.notify("Research is already running", severity="warning")
            return
        
        # Start research process
        self.research_is_running = True
        self.query_one("#research-loading", LoadingIndicator).remove_class("hidden")
        self.query_one("#start-research", Button).disabled = True
        
        # Run the research process in a worker
        worker = self.run_worker(self._run_research_worker, exit_on_error=True)
        logger.info(f"Started technology research worker: {worker}")
    
    async def _run_research_worker(self) -> None:
        """Run the technology research process in a background worker."""
        worker = get_current_worker()
        
        try:
            # Initialize tracking variables
            research_completed = False
            
            # Start technology research
            session = await self.research_team.create_session(
                self.session_id, 
                self.technology_requirements,
                self.generic_architecture,
                self.foundation_approach
            )
            
            if not session:
                self.app.notify("Failed to create technology research session", severity="error")
                return
            
            # Initialize research agents
            self.update_phase_progress("technology_discovery", "in_progress")
            await self.research_team.initialize_research_agents(self.session_id)
            
            # Phase 1: Technology Discovery
            if worker.is_cancelled:
                return
                
            discovery_result = await self.research_team.discover_component_technologies(self.session_id)
            if discovery_result["status"] == "success":
                self.update_phase_progress("technology_discovery", "completed")
                self.update_phase_progress("technology_exploration", "in_progress")
                
                # Phase 2: Technology Exploration
                if worker.is_cancelled:
                    return
                    
                exploration_result = await self.research_team.explore_technology_options(self.session_id)
                if exploration_result["status"] == "success":
                    self.update_phase_progress("technology_exploration", "completed")
                    self.update_phase_progress("stack_creation", "in_progress")
                    
                    # Phase 3: Stack Creation
                    if worker.is_cancelled:
                        return
                        
                    await self.research_team.generate_technology_stacks(self.session_id)
                    stack_result = await self.research_team.start_stack_research(self.session_id)
                    
                    if stack_result["status"] == "success":
                        self.update_phase_progress("stack_creation", "completed")
                        self.update_phase_progress("integration_exploration", "in_progress")
                        
                        # Phase 4: Integration Exploration
                        if worker.is_cancelled:
                            return
                            
                        integration_result = await self.research_team.start_integration_research(self.session_id)
                        
                        if integration_result["status"] == "success":
                            self.update_phase_progress("integration_exploration", "completed")
                            self.update_phase_progress("research_synthesis", "in_progress")
                            
                            # Phase 5: Research Synthesis
                            if worker.is_cancelled:
                                return
                                
                            self.technology_report_path = await self.research_team.create_technology_report(self.session_id)
                            
                            if self.technology_report_path:
                                self.update_phase_progress("research_synthesis", "completed")
                                research_completed = True
            
            # Update UI based on completion
            if research_completed:
                self.app.notify("Technology research completed successfully", severity="success")
                self.query_one("#view-report", Button).disabled = False
                self.query_one("#go-to-architecture", Button).disabled = False
                
                # Show technology research report in document review
                if hasattr(self.app, "show_document_review_for_technology_research_report"):
                    await self.app.show_document_review_for_technology_research_report(self.session_id)
            else:
                self.app.notify("Technology research process did not complete successfully", severity="warning")
        
        except Exception as e:
            logger.error(f"Error in technology research process: {str(e)}")
            self.app.notify(f"Error in technology research process: {str(e)}", severity="error")
        
        finally:
            # Reset UI state
            self.research_is_running = False
            self.query_one("#research-loading", LoadingIndicator).add_class("hidden")
            self.query_one("#start-research", Button).disabled = False
    
    @on(Button.Pressed, "#view-requirements")
    @handle_errors
    def handle_view_requirements(self) -> None:
        """Handle the view requirements button press."""
        if not self.technology_requirements:
            self.app.notify("No technology requirements available", severity="warning")
            return
        
        # Show requirements in preview
        preview = Markdown(self.technology_requirements)
        self.query_one("#preview-content", Static).update(preview)
    
    @on(Button.Pressed, "#view-architecture")
    @handle_errors
    def handle_view_architecture(self) -> None:
        """Handle the view architecture button press."""
        if not self.generic_architecture:
            self.app.notify("No generic architecture available", severity="warning")
            return
        
        # Show architecture in preview
        preview = Markdown(self.generic_architecture)
        self.query_one("#preview-content", Static).update(preview)
    
    @on(Button.Pressed, "#view-foundation")
    @handle_errors
    def handle_view_foundation(self) -> None:
        """Handle the view foundation button press."""
        if not self.foundation_approach:
            self.app.notify("No foundation approach available", severity="warning")
            return
        
        # Show foundation in preview
        foundation_text = f"# {self.foundation_approach.get('name', 'Selected Foundation')}\n\n"
        foundation_text += self.foundation_approach.get('description', 'No description available')
        
        # Add other foundation details
        for key, value in self.foundation_approach.items():
            if key not in ('name', 'description') and not isinstance(value, dict) and not isinstance(value, list):
                foundation_text += f"\n\n## {key.replace('_', ' ').title()}\n{value}"
        
        preview = Markdown(foundation_text)
        self.query_one("#preview-content", Static).update(preview)
    
    @on(Button.Pressed, "#view-report")
    @handle_async_errors
    async def handle_view_report(self) -> None:
        """Handle the view report button press by starting worker."""
        if not self.technology_report_path:
            self.app.notify("No technology report available", severity="warning")
            return
        
        # Use document review if available
        if hasattr(self.app, "show_document_review_for_technology_research_report"):
            await self.app.show_document_review_for_technology_research_report(self.session_id)
        else:
            # Fallback to in-place preview using a worker
            worker = self.run_worker(self._load_report_worker, exit_on_error=True)
            logger.info(f"Started report loading worker: {worker}")
    
    async def _load_report_worker(self) -> None:
        """Load the technology report in a background worker."""
        worker = get_current_worker()
        
        # Show loading indicator
        self.query_one("#research-loading", LoadingIndicator).remove_class("hidden")
        
        try:
            # Load and show report in preview
            report_content = await load_document_content(self.session_id, "technology-research-report")
            
            if worker.is_cancelled:
                return
                
            if report_content:
                # Use batch_update to prevent flicker during update
                with self.app.batch_update():
                    preview = Markdown(report_content)
                    self.query_one("#preview-content", Static).update(preview)
            else:
                self.app.notify("Failed to load technology report", severity="error")
        except Exception as e:
            logger.error(f"Error loading report: {str(e)}")
            self.app.notify(f"Error loading report: {str(e)}", severity="error")
        finally:
            # Hide loading indicator
            self.query_one("#research-loading", LoadingIndicator).add_class("hidden")
            
    @on(Button.Pressed, "#go-to-architecture")
    @handle_errors
    def handle_go_to_architecture(self) -> None:
        """Handle going to architecture screen."""
        self.action_go_to_architecture()
    
    @handle_errors
    def action_go_to_architecture(self) -> None:
        """Navigate to the technology selection screen (Architect 3rd pass)."""
        # Check if we completed research before proceeding
        if not self.technology_report_path:
            self.app.notify("Please complete technology research before moving to technology selection", severity="warning")
            return
            
        # Let the app handle workflow state transitions for consistency
        # Switch to the technology selection screen
        if hasattr(self.app, "action_switch_to_technology_selection"):
            self.app.action_switch_to_technology_selection()
        else:
            # Fallback to architecture screen if technology selection is not available
            self.app.notify("Technology selection screen not available", severity="warning")
    
    @handle_errors
    def update_phase_progress(self, phase: str, status: str) -> None:
        """Update the progress of a research phase.
        
        Args:
            phase: Phase to update
            status: New status
        """
        if phase in self.research_progress:
            self.research_progress[phase] = status
            self.update_phase_display()
    
    @handle_errors
    def action_start_research(self) -> None:
        """Action to start the research process."""
        if not self.research_is_running:
            self.handle_start_research()
            logger.info("Started technology research via keyboard shortcut")
    
    @handle_errors
    def action_view_results(self) -> None:
        """Action to view the research results."""
        if self.technology_report_path:
            self.handle_view_report()
    
    @handle_errors
    def action_view_requirements(self) -> None:
        """Action to view the technology requirements."""
        if self.technology_requirements:
            self.handle_view_requirements()