"""
Research screen for IdeasFactory.

This module implements the UI for the research phase, using the foundational
research team to explore implementation options across multiple paradigms.
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
from ideasfactory.agents.research_team import FoundationalResearchTeam, FoundationalResearchSession
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


class ResearchScreen(BaseScreen):
    """
    Screen for the research phase of IdeasFactory.
    
    This screen allows users to start and monitor the foundational
    research process, which explores implementation options across
    multiple paradigms.
    """
    
    BINDINGS = [
        ("escape", "app.pop_screen", "Back"),
        ("r", "start_research", "Start Research"),
        ("v", "view_results", "View Results"),
        ("a", "go_to_architecture", "Go to Architecture"),
        ("d", "view_requirements", "View Requirements"),
    ]
    
    def __init__(self):
        """Initialize the research screen."""
        super().__init__()
        self.research_team = FoundationalResearchTeam()
        self.session_manager = SessionManager()
        
        # UI state tracking
        self.session_id: Optional[str] = None
        self.research_requirements: Optional[str] = None
        self.current_phase: str = "foundation_discovery"
        self.research_progress: Dict[str, str] = {
            "foundation_discovery": "pending",
            "foundation_exploration": "pending",
            "path_creation": "pending",
            "integration_exploration": "pending",
            "research_synthesis": "pending"
        }
        self.research_report_path: Optional[str] = None
        self.research_is_running = False
    
    def compose(self) -> ComposeResult:
        """Create child widgets for the screen."""

        yield Container(
            Label("Multi-paradigm Foundational Research", id="research-title"),

            Markdown("", id="preview-content"),
                        
            Button("View Research Requirements Document", id="view-requirements"),
                        
            Container(
                Label("Research Status", classes="section-header"),
                ResearchProgressBar(total_phases=5),
                
                VerticalScroll(
                    ResearchPhaseLabel(
                        "Foundation Discovery", 
                        "Discover potential foundation approaches for the project",
                        "pending"
                    ),
                    ResearchPhaseLabel(
                        "Foundation Exploration", 
                        "Explore each foundation across paradigm spectrum",
                        "pending"
                    ),
                    ResearchPhaseLabel(
                        "Path Creation", 
                        "Generate implementation paths based on foundation choices",
                        "pending"
                    ),
                    ResearchPhaseLabel(
                        "Integration Exploration", 
                        "Identify cross-foundation opportunities",
                        "pending"
                    ),
                    ResearchPhaseLabel(
                        "Research Synthesis", 
                        "Create comprehensive research report",
                        "pending"
                    ),
                    id="research-phases"
                ),

                id="research-status"
            ),
            Button("Start Research", id="start-research"),

            Container(
                Button("View Report", id="view-report", disabled=True),
                Button("Continue to Foundation Selection", id="go-to-architecture", disabled=True),
                
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
        logger.info(f"Research screen resumed with session ID: {self.session_id}")
        
        # If we have a session but no documents, try to load them
        if self.session_id and not self.research_requirements:
            logger.info("No research requirements loaded, attempting to load documents")
            await self._load_session_documents()
    
    @handle_errors
    def set_session(self, session_id: str) -> None:
        """Set the current session ID.
        
        Args:
            session_id: Session ID to set
        """
        # Follow the standard BaseScreen pattern
        super().set_session(session_id)
        logger.info(f"Research screen session set to: {session_id}")
    
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
            
            # Get document path directly from session manager for debugging
            requirements_path = self.session_manager.get_document(self.session_id, "research-requirements")
            logger.info(f"Research requirements path from session manager: {requirements_path}")
            
            # Load research requirements document - explicitly map to technical-research-requirements.md
            logger.info(f"Attempting to load research requirements from session {self.session_id}")
            research_requirements_content = await load_document_content(self.session_id, "research-requirements")
            
            if research_requirements_content:
                logger.info(f"Successfully loaded research requirements - Length: {len(research_requirements_content)}")
                self.research_requirements = research_requirements_content
                if self._is_mounted:
                    with self.app.batch_update():
                        self.query_one("#preview-content", Markdown).update(self.research_requirements)
            else:
                logger.error(f"Failed to load research requirements for session {self.session_id}")
                session_data = self.session_manager.get_session(self.session_id)
                if session_data and 'documents' in session_data:
                    logger.info(f"Documents in session: {session_data.get('documents', {})}")
            
            # Load research report if it exists
            logger.info("Attempting to load research report")
            research_report_content = await load_document_content(self.session_id, "research-report")
            if research_report_content:
                logger.info(f"Successfully loaded research report - Length: {len(research_report_content)}")
                # Store the report path for future reference
                self.research_report_path = self.session_manager.get_document(self.session_id, "research-report")
                
                if self._is_mounted:
                    self.query_one("#view-report", Button).disabled = False
                    self.query_one("#go-to-architecture", Button).disabled = False
                    
                    # Update progress to show completion
                    for phase in self.research_progress:
                        self.research_progress[phase] = "completed"
                    self.update_phase_display()
            else:
                logger.info("No research report available yet")
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
        if self.research_report_path:
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
        
        if not self.research_requirements:
            self.app.notify("No research requirements available", severity="error")
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
        logger.info(f"Started research worker: {worker}")
    
    async def _run_research_worker(self) -> None:
        """Run the research process in a background worker.
        
        Note: The research process uses Worker (unlike other screens) because
        it involves a multi-phase, long-running process that would otherwise block
        the UI. Each phase (foundation discovery, exploration, path creation, etc.)
        can take significant time, so background processing is necessary.
        """
        worker = get_current_worker()
        
        try:
            # Initialize tracking variables
            research_completed = False
            
            # Start each phase of research
            session = await self.research_team.create_session(self.session_id, self.research_requirements)
            if not session:
                self.app.notify("Failed to create research session", severity="error")
                return
            
            # Initialize research agents
            self.update_phase_progress("foundation_discovery", "in_progress")
            await self.research_team.initialize_research_agents(self.session_id)
            
            # Phase 1: Foundation Discovery
            if worker.is_cancelled:
                return
                
            foundations_result = await self.research_team.discover_project_foundations(self.session_id)
            if foundations_result["status"] == "success":
                self.update_phase_progress("foundation_discovery", "completed")
                self.update_phase_progress("foundation_exploration", "in_progress")
                
                # Phase 2: Foundation Exploration
                if worker.is_cancelled:
                    return
                    
                exploration_result = await self.research_team.explore_foundation_approaches(self.session_id)
                if exploration_result["status"] == "success":
                    self.update_phase_progress("foundation_exploration", "completed")
                    self.update_phase_progress("path_creation", "in_progress")
                    
                    # Phase 3: Path Creation
                    if worker.is_cancelled:
                        return
                        
                    await self.research_team.generate_research_paths(self.session_id)
                    path_result = await self.research_team.start_path_research(self.session_id)
                    
                    if path_result["status"] == "success":
                        self.update_phase_progress("path_creation", "completed")
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
                                
                            self.research_report_path = await self.research_team.create_research_report(self.session_id)
                            
                            if self.research_report_path:
                                self.update_phase_progress("research_synthesis", "completed")
                                research_completed = True
            
            # Update UI based on completion
            if research_completed:
                self.app.notify("Research completed successfully", severity="success")
                self.query_one("#view-report", Button).disabled = False
            else:
                self.app.notify("Research process did not complete successfully", severity="warning")
        
        except Exception as e:
            logger.error(f"Error in research process: {str(e)}")
            self.app.notify(f"Error in research process: {str(e)}", severity="error")
        
        finally:
            # Reset UI state
            self.research_is_running = False
            self.query_one("#research-loading", LoadingIndicator).add_class("hidden")
            self.query_one("#start-research", Button).disabled = False
    
    @on(Button.Pressed, "#view-requirements")
    @handle_errors
    def handle_view_requirements(self) -> None:
        """Handle the view requirements button press."""
        if not self.research_requirements:
            self.app.notify("No research requirements available", severity="warning")
            return
        
        # Show requirements in preview
        preview = Markdown(self.research_requirements)
        self.query_one("#preview-content", Static).update(preview)
    
    @on(Button.Pressed, "#view-report")
    def handle_view_report(self) -> None:
        """Handle the view report button press by starting worker."""
        if not self.research_report_path:
            self.app.notify("No research report available", severity="warning")
            return
        
        # Use document review if available
        if hasattr(self.app, "show_document_review_for_research_report"):
            self.app.show_document_review_for_research_report(self.session_id)
        else:
            # Fallback to in-place preview using a worker
            worker = self.run_worker(self._load_report_worker, exit_on_error=True)
            logger.info(f"Started report loading worker: {worker}")
    
    async def _load_report_worker(self) -> None:
        """Load the research report in a background worker.
        
        Note: This uses a background worker to be consistent with the research process
        and to maintain responsiveness when loading potentially large research reports.
        """
        worker = get_current_worker()
        
        # Show loading indicator
        self.query_one("#research-loading", LoadingIndicator).remove_class("hidden")
        
        try:
            # Load and show report in preview
            report_content = await load_document_content(self.session_id, "research-report")
            
            if worker.is_cancelled:
                return
                
            if report_content:
                # Use batch_update to prevent flicker during update
                with self.app.batch_update():
                    preview = Markdown(report_content)
                    self.query_one("#preview-content", Static).update(preview)
            else:
                self.app.notify("Failed to load research report", severity="error")
        except Exception as e:
            logger.error(f"Error loading report: {str(e)}")
            self.app.notify(f"Error loading report: {str(e)}", severity="error")
        finally:
            # Hide loading indicator
            self.query_one("#research-loading", LoadingIndicator).add_class("hidden")
            
    @on(Button.Pressed, "#go-to-architecture")
    def handle_go_to_architecture(self) -> None:
        """Handle going to architecture screen."""
        self.action_go_to_architecture()
    
    def action_go_to_architecture(self) -> None:
        """Navigate to the foundation selection screen (Architect 2nd pass)."""
        # Check if we completed research before proceeding
        if not self.research_report_path:
            self.app.notify("Please complete research before moving to foundation selection", severity="warning")
            return
            
        # Let the app handle workflow state transitions for consistency
        # Switch to the foundation selection screen
        if hasattr(self.app, "action_switch_to_foundation_selection"):
            self.app.action_switch_to_foundation_selection()
        else:
            # Fallback to architecture screen if foundation selection is not available
            self.app.notify("Foundation selection screen not available", severity="warning")
    
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
            logger.info("Started research via keyboard shortcut")
    
    @handle_errors
    def action_view_results(self) -> None:
        """Action to view the research results."""
        if self.research_report_path:
            self.handle_view_report()
    
    @handle_errors
    def action_view_requirements(self) -> None:
        """Action to view the research requirements."""
        if self.research_requirements:
            self.handle_view_requirements()