"""
Research screen for IdeasFactory.

This module defines the Textual screen for conducting research sessions with
the Research Team agent.
"""

import logging
import asyncio
from typing import Optional, Dict, List, Any
import json

from textual.app import ComposeResult
from textual.widgets import (
    Header, Footer, Button, Static, TextArea, Label, ProgressBar, Input,
    DataTable, RadioButton, RadioSet
)
from textual.containers import Container, VerticalScroll, Horizontal
from textual.binding import Binding

from ideasfactory.agents.research_team import ResearchTeam, ParadigmCategory
from ideasfactory.documents.document_manager import DocumentManager
from ideasfactory.ui.screens.document_review_screen import DocumentSource
from ideasfactory.ui.screens import BaseScreen

from ideasfactory.utils.session_manager import SessionManager
from ideasfactory.utils.error_handler import handle_async_errors

# Configure logging
logger = logging.getLogger(__name__)


class ResearchScreen(BaseScreen):
    """
    Screen for conducting research with the Research Team agent.
    """
    
    BINDINGS = [
        Binding(key="ctrl+n", action="next_component", description="Next Component"),
        Binding(key="ctrl+p", action="previous_component", description="Previous Component"),
        Binding(key="ctrl+r", action="research_component", description="Research Component"),
        Binding(key="ctrl+c", action="create_report", description="Create Report"),
        Binding(key="ctrl+b", action="back", description="Back"),
    ]
    
    def __init__(self, *args, **kwargs):
        """Initialize the research screen."""
        super().__init__(*args, **kwargs)
        self.research_team = ResearchTeam()
        self.document_manager = DocumentManager()
        self.project_vision: Optional[str] = None
        self.prd_document: Optional[str] = None
        self.research_requirements: Optional[str] = None
        self.components: List[Component] = []
        self.current_component_index: int = 0
        
        # Progress tracking
        self._progress_value = 0
        self._total_components = 0
    
    def compose(self) -> ComposeResult:
        """Create child widgets for the screen."""
        yield Header()
        with VerticalScroll(id="research_scroll"):
            yield Container(
                Label("Multi-Dimensional Technical Research", id="research_header"),
                
                # Documents container (for context)
                Container(
                    Label("Project Context Documents", id="context_header"),
                    Container(
                        Button("View Project Vision", id="view_vision_button", variant="primary"),
                        Button("View PRD", id="view_prd_button", variant="primary"),
                        Button("View Research Requirements", id="view_requirements_button", variant="primary"),
                        Button("Reload Documents", id="reload_documents_button", variant="default"),
                        id="context_buttons"
                    ),
                    # Add document summary display
                    Static("Select a document above to see a summary", id="context_summary"),
                    id="documents_container"
                ),
                
                # Overall research progress container
                Container(
                    Label("Research Workflow Progress", id="progress_header"),
                    ProgressBar(id="overall_progress", total=100, show_eta=False, show_percentage=True),
                    Static("Ready to start multi-dimensional research", id="research_status"),
                    Container(
                        Label("Research Approach", id="approach_label"),
                        RadioSet(
                            RadioButton("Standard Research", id="standard_research_radio"),
                            RadioButton("Specialized Agents", id="specialized_agents_radio", value=True),
                            id="research_approach"
                        ),
                        id="approach_container"
                    ),
                    Button("Start Automated Research", id="start_research_button", variant="primary"),
                    id="progress_container"
                ),
                
                # Research teams progress container
                Container(
                    Label("Research Teams Progress", id="teams_header"),
                    Container(
                        Label("Foundation Research", id="foundation_label"),
                        ProgressBar(id="foundation_progress", total=100, show_percentage=True),
                        Static("Preparing...", id="foundation_status"),
                        id="foundation_container"
                    ),
                    Container(id="branch_teams_container"),
                    Container(
                        Label("Integration Research", id="integration_label"),
                        ProgressBar(id="integration_progress", total=100, show_percentage=True),
                        Static("Waiting for branch research...", id="integration_status"),
                        id="integration_container"
                    ),
                    id="research_teams_container",
                    classes="hidden"
                ),
                
                # Summarized research status display
                Container(
                    Label("Current Research Status", id="status_header"),
                    Static("The automated research process will explore all dimensions using specialized agents working in parallel.\n\nOnce complete, a comprehensive research report will be generated that includes findings across paradigms and dimensions.", id="status_description"),
                    id="status_container"
                ),
                
                # Action container
                Container(
                    Button("View Research Report", id="create_report_button", variant="success", disabled=True),
                    Button("Back to Architecture", id="back_button", variant="warning"),
                    id="action_container"
                ),
                
                id="research_container"
            )
        yield Footer()
    
    def on_mount(self) -> None:
        """Handle the screen's mount event."""
        super().on_mount()
        
        # Initialize progress tracking attributes
        self.branch_progress = {}
        self.current_dimension_index = 0
        self.dimensions = []
        self.research_paths = []
        
        # Initially hide or disable containers
        self.query_one("#component_container").display = False
        self.query_one("#findings_container").display = False
        self.query_one("#create_report_button").disabled = True
        
        # The "hidden" class is used for containers that will be shown dynamically
        # These should not use display = False which removes them entirely
        
        # Initialize progress bars with 0 progress
        self.query_one("#overall_progress").update(progress=0)
        self.query_one("#foundation_progress").update(progress=0)
        self.query_one("#integration_progress").update(progress=0)
        
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
            
        # Update UI based on document availability
        if self._is_mounted:
            # Update research status and buttons
            if self.research_requirements:
                self.query_one("#research_status").update("Research requirements loaded. Ready to start research.")
                self.query_one("#start_research_button").disabled = False
                self.query_one("#view_requirements_button").disabled = False
            else:
                self.query_one("#research_status").update("Research requirements document required.")
                self.query_one("#start_research_button").disabled = True
                self.query_one("#view_requirements_button").disabled = True
    
    @handle_async_errors
    async def on_screen_resume(self) -> None:
        """Handle screen being resumed."""
        # Call the base class implementation which handles session retrieval
        await super().on_screen_resume()
        
        # If we have a session but no documents, try to load them
        if self.session_id and not self.research_requirements:
            await self._load_session_documents()
        elif not self.session_id:
            # No session
            self.notify("No active session found", severity="error")
            self.query_one("#research_status").update("No active session")
            self.query_one("#start_research_button").disabled = True
    
    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        button_id = event.button.id
        
        # Start research button
        if button_id == "start_research_button":
            await self.start_research()
            
        # Report and navigation
        elif button_id == "create_report_button":
            # Since the report is already generated automatically, this button
            # just displays the existing report
            report_path = await self.research_team._find_synthesis_report(self.session_id)
            if report_path:
                await self.view_research_report(report_path)
            else:
                self.notify("No research report found. Wait for research to complete.", severity="warning")
                
        elif button_id == "back_button":
            await self.go_back()
            
        # Document viewing
        elif button_id == "view_vision_button":
            await self.view_project_vision()
            await self.display_document_summary("vision")
        elif button_id == "view_prd_button":
            await self.view_prd_document()
            await self.display_document_summary("prd")
        elif button_id == "view_requirements_button":
            await self.view_research_requirements()
            await self.display_document_summary("requirements")
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
    
    @handle_async_errors
    async def start_research(self) -> None:
        """
        Start the multi-dimensional research process.
        
        This initiates a complete automated research workflow that runs from start to finish
        without requiring user interaction for each step. Progress is shown throughout.
        """
        if not self._is_mounted or not self.research_requirements:
            logger.error("Screen not mounted or missing research requirements")
            return
        
        # Disable the start button while processing
        self.query_one("#start_research_button").disabled = True
        self.query_one("#research_status").update("Initializing dimensional research session...")
        
        try:
            # Get the session ID from session manager (single source of truth)
            session_manager = SessionManager()
            current_session = session_manager.get_current_session()
            
            if current_session:
                self.session_id = current_session.id
            else:
                logger.error("No active session when starting research")
                self.notify("No active session found", severity="error")
                self.query_one("#start_research_button").disabled = False
                return
            
            # Update overall progress bar (5% for initialization)
            self.query_one("#overall_progress").update(progress=5)
            
            # Check if specialized agents approach is selected
            use_specialized_agents = self.query_one("#specialized_agents_radio").value
            
            if use_specialized_agents:
                # Use the specialized agents approach
                self.query_one("#research_status").update("Initializing specialized research agent teams...")
                
                # Start the research with specialized agents
                self.query_one("#research_teams_container").remove_class("hidden")
                
                # Show some progress indicators
                self.query_one("#overall_progress").update(progress=5)
                self.query_one("#foundation_progress").update(progress=10)
                self.query_one("#foundation_status").update("Creating specialized agent teams...")
                
                # Start animated progress indicator
                asyncio.create_task(self._animate_foundation_team_startup())
                
                # Start the specialized agents research process (runs in background)
                asyncio.create_task(self._run_specialized_agents_research())
                
                # Display will be updated by the background task
                return
            else:
                # Create the standard research session with full document context
                self.query_one("#research_status").update("Creating research session with document context...")
                session = await self.research_team.create_session(
                    self.session_id,
                    self.research_requirements,
                    self.project_vision,
                    self.prd_document
                )
            
            # Update overall progress (10% for session creation)
            self.query_one("#overall_progress").update(progress=10)
            
            # Determine whether to use dimensional or component-based research
            if hasattr(session, 'dimensions') and session.dimensions:
                # New dimensional research
                self.dimensions = session.dimensions
                self.current_dimension_index = 0
                
                # Make dimension container visible
                self.query_one("#dimension_container").remove_class("hidden")
                
                # Show research teams progress
                self.query_one("#research_teams_container").remove_class("hidden")
                
                # Update status with dimension count
                self.query_one("#research_status").update(
                    f"Research initialized. Beginning automated research on {len(self.dimensions)} dimensions..."
                )
                
                # Display the first dimension for context
                await self.display_current_dimension()
                
                # Start showing foundation team animation (runs concurrently)
                asyncio.create_task(self._animate_foundation_team_startup())
                
                # Start the automated research process
                asyncio.create_task(self._run_automated_dimensional_research())
                
            elif hasattr(session, 'components') and session.components:
                # Legacy component extraction (maintaining backward compatibility)
                self.components = session.components
                self.current_component_index = 0
                self._total_components = len(self.components)
                
                # Update the status
                self.query_one("#research_status").update(
                    f"Research initialized. Beginning automated research on {len(self.components)} components..."
                )
                
                # Show the component container
                self.query_one("#component_container").display = True
                
                # Display the first component for context
                await self.display_current_component()
                
                # Start the automated legacy research process
                asyncio.create_task(self._run_automated_component_research())
                
            else:
                # No research dimensions or components found
                self.notify("No research targets identified", severity="error")
                self.query_one("#research_status").update("No research targets found in requirements.")
                self.query_one("#start_research_button").disabled = False
                return
                
        except Exception as e:
            logger.error(f"Error during research initialization: {str(e)}")
            self.notify(f"Research initialization error: {str(e)}", severity="error")
            self.query_one("#research_status").update("Error during initialization.")
            self.query_one("#start_research_button").disabled = False
            
    @handle_async_errors        
    async def _run_automated_dimensional_research(self) -> None:
        """Run the complete dimensional research process automatically."""
        if not self.dimensions:
            return
            
        try:
            # Research each dimension in sequence
            for i, dimension in enumerate(self.dimensions):
                # Set current dimension for display
                self.current_dimension_index = i
                await self.display_current_dimension()
                
                # Create branch teams UI for this dimension
                dimension_name = getattr(dimension, "name", f"Dimension {i+1}")
                await self._create_branch_teams_ui(dimension_name)
                
                # Update status
                self.query_one("#research_status").update(f"Researching dimension: {dimension_name} ({i+1}/{len(self.dimensions)})")
                
                # Research the dimension
                updated_dimension = await self.research_team.research_dimension(self.session_id)
                
                if updated_dimension:
                    # Update local dimension with research results
                    self.dimensions[i] = updated_dimension
                    
                    # Update progress indicators
                    await self._update_dimension_research_progress(dimension_name)
                    
                    # Show success notification
                    self.notify(f"Research completed for '{dimension_name}'", severity="success")
                    
                    # Show research paths if this was a foundational dimension
                    foundational = getattr(dimension, "type", "") == "foundational"
                    if foundational:
                        self.query_one("#paths_container").remove_class("hidden")
                        await self._update_research_paths()
                else:
                    self.notify(f"Failed to research dimension: {dimension_name}", severity="warning")
                
                # Short pause between dimensions for UI updating
                await asyncio.sleep(0.5)
            
            # All dimensions have been researched - show cross-paradigm opportunities
            self.query_one("#opportunities_container").remove_class("hidden")
            await self._display_cross_paradigm_opportunities()
            
            # Show findings container
            self.query_one("#findings_container").display = True
            self.query_one("#findings_display").text = "Select a paradigm category to view findings."
            
            # Enable report generation
            self.query_one("#create_report_button").disabled = False
            
            # Update status to complete
            self.query_one("#research_status").update("Research completed successfully. Ready to generate report.")
            
            # Create research report automatically
            await asyncio.sleep(1.0)  # Small pause before starting report generation
            await self.create_research_report()
            
        except Exception as e:
            logger.error(f"Error in automated dimensional research: {str(e)}")
            self.notify(f"Research process error: {str(e)}", severity="error")
            self.query_one("#research_status").update("Error during automated research process.")
            
    @handle_async_errors        
    async def _run_automated_component_research(self) -> None:
        """Run the complete legacy component-based research process automatically."""
        if not self.components:
            return
            
        try:
            # Initialize progress tracking
            self._progress_value = 0
            self.query_one("#overall_progress").update(total=len(self.components), progress=0)
            
            # Research each component in sequence
            for i, component in enumerate(self.components):
                # Set current component for display
                self.current_component_index = i
                await self.display_current_component()
                
                # Update status
                self.query_one("#research_status").update(f"Researching component: {component.name} ({i+1}/{len(self.components)})")
                
                # Research the component
                updated_component = await self.research_team.research_component(self.session_id)
                
                if updated_component:
                    # Update local component with research results
                    self.components[i] = updated_component
                    
                    # Update progress
                    self._progress_value += 1
                    self.query_one("#overall_progress").update(progress=self._progress_value)
                    
                    # Show success notification
                    self.notify(f"Research completed for '{component.name}'", severity="success")
                else:
                    self.notify(f"Failed to research component: {component.name}", severity="warning")
                
                # Short pause between components for UI updating
                await asyncio.sleep(0.5)
            
            # Show findings container
            self.query_one("#findings_container").display = True
            self.query_one("#findings_display").text = "Select a paradigm category to view findings."
            
            # Enable report generation
            self.query_one("#create_report_button").disabled = False
            
            # Update status to complete
            self.query_one("#research_status").update("Research completed successfully. Ready to generate report.")
            
            # Create research report automatically
            await asyncio.sleep(1.0)  # Small pause before starting report generation
            await self.create_research_report()
            
        except Exception as e:
            logger.error(f"Error in automated component research: {str(e)}")
            self.notify(f"Research process error: {str(e)}", severity="error")
            self.query_one("#research_status").update("Error during automated research process.")
            
    @handle_async_errors        
    async def _run_specialized_agents_research(self) -> None:
        """Run the research process using the specialized multi-agent system.
        
        This method coordinates the UI updates while the specialized agent system
        conducts research in the background. The entire process is automated with
        a single button press.
        """
        try:
            # Initialize the branch teams display
            self._initialize_specialized_agent_branches()
            
            # Update status and progress indicators
            self.query_one("#research_status").update("Starting specialized agent research workflow...")
            self.query_one("#overall_progress").update(progress=5)
            self.query_one("#foundation_progress").update(progress=10)
            self.query_one("#foundation_status").update("Initializing specialized agent teams...")
            
            # Create a task for monitoring progress
            progress_task = asyncio.create_task(self._monitor_specialized_agents_progress())
            
            # Show a notification to indicate the research is happening in the background
            self.notify(
                "Specialized agent research started - this process runs automatically in the background",
                severity="information"
            )
            
            # Start the specialized agents research process in parallel
            research_task = asyncio.create_task(
                self.research_team.conduct_research_with_specialized_agents(self.session_id)
            )
            
            # Wait for the research process to complete
            report_path = await research_task
            
            # Cancel the progress monitoring task
            progress_task.cancel()
            try:
                await progress_task
            except asyncio.CancelledError:
                pass
            
            # Update the overall progress to show completion
            self.query_one("#overall_progress").update(progress=100)
            
            # Set all progress bars to 100%
            self.query_one("#foundation_progress").update(progress=100)
            self.query_one("#integration_progress").update(progress=100)
            
            for branch_id in self.branch_progress.keys():
                try:
                    self.query_one(f"#{branch_id}_progress").update(progress=100)
                    self.query_one(f"#{branch_id}_status").update("Research completed successfully")
                except Exception:
                    pass
            
            # Enable report viewing
            self.query_one("#create_report_button").disabled = False
            
            # Update status to complete
            if report_path:
                self.query_one("#research_status").update(
                    "Multi-agent research completed successfully. Research report generated."
                )
                
                # Show success notification
                self.notify("Research report generated successfully", severity="success")
                
                # Use the document review screen to display the report
                if hasattr(self.app, "document_review_screen"):
                    # Get the document content
                    from ideasfactory.documents.document_manager import DocumentManager
                    doc_manager = DocumentManager()
                    document = doc_manager.get_document(report_path)
                    
                    if document and "content" in document:
                        # Configure for viewing the report
                        self.app.document_review_screen.configure_for_agent(
                            document_source=DocumentSource.RESEARCH_TEAM,
                            session_id=self.session_id,
                            document_content=document["content"],
                            document_title="Multi-Agent Research Report",
                            document_type="research-report",
                            revision_callback=None,
                            completion_callback=None,
                            back_screen="research_screen",
                            next_screen=None
                        )
                        
                        # Show the document review
                        self.app.push_screen("document_review_screen")
                    else:
                        self.notify("Failed to load research report", severity="error")
                else:
                    self.notify("Document review screen not available", severity="warning")
            else:
                self.query_one("#research_status").update(
                    "Research completed, but report generation failed."
                )
                self.notify("Failed to generate research report", severity="error")
            
        except Exception as e:
            logger.error(f"Error in specialized agents research: {str(e)}")
            self.notify(f"Research process error: {str(e)}", severity="error")
            self.query_one("#research_status").update("Error during specialized agent research process.")
    
    async def _monitor_specialized_agents_progress(self) -> None:
        """Monitor the progress of the specialized agents research process.
        
        This method updates the UI with the current research phase and progress
        by querying key indicators and updating progress bars in real-time.
        """
        # Define the research phases and indicators
        phases = [
            {
                "name": "foundation",
                "status": "Conducting foundation research and debates...", 
                "progress_start": 5,
                "progress_end": 30
            },
            {
                "name": "path_definition",
                "status": "Exploring research paths based on foundation choices...", 
                "progress_start": 30,
                "progress_end": 50
            },
            {
                "name": "integration",
                "status": "Identifying cross-paradigm integration opportunities...", 
                "progress_start": 50,
                "progress_end": 75
            },
            {
                "name": "synthesis",
                "status": "Synthesizing findings into final research report...", 
                "progress_start": 75,
                "progress_end": 95
            }
        ]
        
        # Track current phase
        current_phase_index = 0
        
        try:
            while True:
                if not self._is_mounted:
                    break
                
                # Get current phase
                if current_phase_index < len(phases):
                    phase = phases[current_phase_index]
                    
                    # Update status for this phase
                    self.query_one("#research_status").update(phase["status"])
                    
                    # Calculate progress within this phase (0-100%)
                    phase_progress = 0
                    
                    # Check for phase transition indicators
                    if phase["name"] == "foundation":
                        # Foundation phase: Check repository for debates
                        from ideasfactory.agents.research_agents.repository import DimensionalResearchRepository
                        repo = DimensionalResearchRepository()
                        
                        # If debates are concluded, transition to next phase
                        if repo.debates and any(debate.status == "concluded" for debate in repo.debates):
                            current_phase_index += 1
                            phase_progress = 100
                        else:
                            # Estimate progress based on number of debates
                            if repo.debates:
                                debate_count = len(repo.debates)
                                contribution_count = sum(len(debate.contributions) for debate in repo.debates)
                                if debate_count > 0:
                                    # Each debate needs ~5 contributions to be meaningful
                                    phase_progress = min(100, int((contribution_count / (debate_count * 5)) * 100))
                            
                            # Update foundation progress bar
                            self.query_one("#foundation_progress").update(progress=phase_progress)
                            
                            # Update branch team progress bars
                            for branch_id in ["branch_established", "branch_mainstream", "branch_cutting_edge", 
                                            "branch_experimental", "branch_cross", "branch_paths"]:
                                try:
                                    self.query_one(f"#{branch_id}_progress").update(progress=int(phase_progress * 0.3))
                                    self.query_one(f"#{branch_id}_status").update("Preparing for research...")
                                except Exception:
                                    pass
                    
                    elif phase["name"] == "path_definition":
                        # Path definition phase: Check repository for research paths
                        from ideasfactory.agents.research_agents.repository import DimensionalResearchRepository
                        repo = DimensionalResearchRepository()
                        
                        # If research paths are defined, transition to next phase
                        if repo.research_paths:
                            current_phase_index += 1
                            phase_progress = 100
                            
                            # Update branch progress for path agents
                            for branch_id in ["branch_paths"]:
                                try:
                                    self.query_one(f"#{branch_id}_progress").update(progress=100)
                                    self.query_one(f"#{branch_id}_status").update("Path exploration complete!")
                                except Exception:
                                    pass
                        else:
                            # Foundation team should be done
                            self.query_one("#foundation_progress").update(progress=100)
                            self.query_one("#foundation_status").update("Foundation research complete!")
                            
                            # Update branch progress - paradigm agents should be active
                            for branch_id in ["branch_established", "branch_mainstream", "branch_cutting_edge", 
                                            "branch_experimental", "branch_cross"]:
                                try:
                                    self.query_one(f"#{branch_id}_progress").update(progress=50)
                                    self.query_one(f"#{branch_id}_status").update("Researching paradigm options...")
                                except Exception:
                                    pass
                            
                            # Path agents should be starting
                            for branch_id in ["branch_paths"]:
                                try:
                                    self.query_one(f"#{branch_id}_progress").update(progress=30)
                                    self.query_one(f"#{branch_id}_status").update("Beginning path exploration...")
                                except Exception:
                                    pass
                            
                            # Estimate phase progress at 50%
                            phase_progress = 50
                    
                    elif phase["name"] == "integration":
                        # Integration phase: Check repository for cross-paradigm opportunities
                        from ideasfactory.agents.research_agents.repository import DimensionalResearchRepository
                        repo = DimensionalResearchRepository()
                        
                        # If opportunities are identified, transition to next phase
                        if repo.opportunities:
                            current_phase_index += 1
                            phase_progress = 100
                            
                            # Update integration progress
                            self.query_one("#integration_progress").update(progress=100)
                            self.query_one("#integration_status").update("Integration analysis complete!")
                        else:
                            # Paradigm agents should be done
                            for branch_id in ["branch_established", "branch_mainstream", "branch_cutting_edge", 
                                            "branch_experimental", "branch_cross"]:
                                try:
                                    self.query_one(f"#{branch_id}_progress").update(progress=100)
                                    self.query_one(f"#{branch_id}_status").update("Paradigm research complete!")
                                except Exception:
                                    pass
                            
                            # Path agents should be done
                            for branch_id in ["branch_paths"]:
                                try:
                                    self.query_one(f"#{branch_id}_progress").update(progress=100)
                                    self.query_one(f"#{branch_id}_status").update("Path exploration complete!")
                                except Exception:
                                    pass
                            
                            # Integration progress should be active
                            self.query_one("#integration_progress").update(progress=60)
                            self.query_one("#integration_status").update("Analyzing integration opportunities...")
                            
                            # Estimate phase progress at 70%
                            phase_progress = 70
                    
                    elif phase["name"] == "synthesis":
                        # Synthesis phase: Check for generated report
                        report_path = await self.research_team._find_synthesis_report(self.session_id)
                        
                        if report_path:
                            # Report exists, we're done
                            current_phase_index += 1
                            phase_progress = 100
                        else:
                            # Report is being generated
                            # Integration should be done
                            self.query_one("#integration_progress").update(progress=100)
                            self.query_one("#integration_status").update("Integration complete, generating report...")
                            
                            # Estimate phase progress at 80%
                            phase_progress = 80
                    
                    # Calculate overall progress based on phase progress
                    progress_range = phase["progress_end"] - phase["progress_start"]
                    overall_progress = phase["progress_start"] + (phase_progress / 100 * progress_range)
                    self.query_one("#overall_progress").update(progress=int(overall_progress))
                
                # Wait before checking again
                await asyncio.sleep(1.0)
                
        except asyncio.CancelledError:
            # Task was cancelled, which is expected
            pass
        except Exception as e:
            logger.error(f"Error monitoring specialized agents progress: {str(e)}")
            # Continue running, this is a non-critical error
    
    def _initialize_specialized_agent_branches(self) -> None:
        """Initialize the branch team displays for specialized agents."""
        # Clear existing branch team displays
        branch_container = self.query_one("#branch_teams_container")
        branch_container.remove_children()
        
        # Set up specialized agent branches
        branch_types = [
            ("branch_established", "Established Paradigm Agents"),
            ("branch_mainstream", "Mainstream Paradigm Agents"),
            ("branch_cutting_edge", "Cutting-Edge Paradigm Agents"),
            ("branch_experimental", "Experimental Paradigm Agents"),
            ("branch_cross", "Cross-Paradigm Agents"),
            ("branch_paths", "Path Exploration Agents")
        ]
        
        # Add progress indicators for each branch team
        for branch_id, branch_name in branch_types:
            self.branch_progress[branch_id] = 0
            
            branch_row = Container(
                Label(branch_name, classes="branch_label"),
                ProgressBar(id=f"{branch_id}_progress", total=100, show_percentage=True),
                Static("Awaiting foundation research...", id=f"{branch_id}_status"),
                id=branch_id,
                classes="branch_row"
            )
            branch_container.mount(branch_row)
    
    # This method is replaced by the _monitor_specialized_agents_progress method
    # which tracks real progress instead of simulating it
    async def _animate_specialized_phase(self, phase: str, progress_start: int, progress_end: int) -> None:
        """Legacy method for animating phase progress (kept for compatibility)."""
        pass
    
    # This method is replaced by the _monitor_specialized_agents_progress method
    # which tracks real progress instead of simulating it
    async def _animate_foundation_team_startup(self) -> None:
        """Legacy method for foundation team animation (kept for compatibility)."""
        pass
    
    @handle_async_errors
    async def display_current_component(self) -> None:
        """Display the current component in the UI."""
        if not self.components or self.current_component_index >= len(self.components):
            return
        
        # Get the current component
        component = self.components[self.current_component_index]
        
        # Update the component display
        self.query_one("#component_name").update(f"**{component.name}** ({self.current_component_index + 1}/{len(self.components)})")
        self.query_one("#component_description").update(component.description)
        
        # Update the research button
        research_button = self.query_one("#research_button")
        if component.completed:
            research_button.label = "Re-Research Component"
            
            # Show the findings container if previously hidden
            self.query_one("#findings_container").display = True
            
            # Clear the findings display
            self.query_one("#findings_display").text = "Select a paradigm category to view findings."
        else:
            research_button.label = "Research Component"
            
            # Hide the findings container until research is done
            self.query_one("#findings_container").display = False
        
        # Update navigation buttons
        self.query_one("#previous_button").disabled = self.current_component_index == 0
        self.query_one("#next_button").disabled = self.current_component_index == len(self.components) - 1
    
    @handle_async_errors
    async def display_current_dimension(self) -> None:
        """Display the current research dimension in the UI."""
        if not self.dimensions or self.current_dimension_index >= len(self.dimensions):
            return
        
        # Get the current dimension
        dimension = self.dimensions[self.current_dimension_index]
        
        # Update the dimension display
        self.query_one("#dimension_name").update(
            f"**{dimension.name}** ({self.current_dimension_index + 1}/{len(self.dimensions)})"
        )
        self.query_one("#dimension_description").update(dimension.description)
        
        # Display dependencies if available
        if hasattr(dimension, "dependencies") and dimension.dependencies:
            deps_text = "**Dependencies:**\n\n"
            for dep in dimension.dependencies:
                deps_text += f"- {dep}\n"
            self.query_one("#dimension_map").update(deps_text)
        else:
            self.query_one("#dimension_map").update("No dependencies")
        
        # Update the research button
        research_button = self.query_one("#research_dimension_button")
        if hasattr(dimension, "completed") and dimension.completed:
            research_button.label = "Re-Research Dimension"
        else:
            research_button.label = "Research Dimension"
        
        # Update navigation buttons
        self.query_one("#prev_dimension_button").disabled = self.current_dimension_index == 0
        self.query_one("#next_dimension_button").disabled = self.current_dimension_index == len(self.dimensions) - 1

    @handle_async_errors
    async def research_current_dimension(self) -> None:
        """Research the current dimension across multiple paradigms."""
        if not self.session_id or not self.dimensions or self.current_dimension_index >= len(self.dimensions):
            logger.error("Cannot research: invalid session or dimension")
            return
        
        # Disable the research button while processing
        research_button = self.query_one("#research_dimension_button")
        research_button.disabled = True
        
        # Get dimension and update status
        dimension = self.dimensions[self.current_dimension_index]
        dimension_name = getattr(dimension, "name", f"Dimension {self.current_dimension_index+1}")
        
        self.query_one("#research_status").update(f"Researching dimension: {dimension_name}...")
        
        # Show progress animation
        research_button.label = "Researching..."
        
        # Create branch teams for this dimension (UI update)
        await self._create_branch_teams_ui(dimension_name)
        
        try:
            # Research the dimension
            updated_dimension = await self.research_team.research_dimension(self.session_id)
            
            if updated_dimension:
                # Update the local dimension with research results
                self.dimensions[self.current_dimension_index] = updated_dimension
                
                # Update progress indicators
                await self._update_dimension_research_progress(dimension_name)
                
                # Update the status
                self.query_one("#research_status").update(
                    f"Dimension '{dimension_name}' researched successfully."
                )
                
                # Show success notification
                self.notify(f"Research completed for '{dimension_name}'", severity="success")
                
                # Show findings container
                self.query_one("#findings_container").display = True
                self.query_one("#findings_display").text = "Select a paradigm category to view findings."
                
                # Show research paths if this was a foundational dimension
                foundational = getattr(dimension, "type", "") == "foundational"
                if foundational:
                    self.query_one("#paths_container").remove_class("hidden")
                    await self._update_research_paths()
                
                # Check if all dimensions have been researched
                all_completed = all(getattr(dim, "completed", False) for dim in self.dimensions)
                self.query_one("#create_report_button").disabled = not all_completed
                
                if all_completed:
                    self.query_one("#research_status").update(
                        "All dimensions researched. Ready to create research report."
                    )
                    # Show cross-paradigm opportunities
                    self.query_one("#opportunities_container").remove_class("hidden")
                    await self._display_cross_paradigm_opportunities()
            else:
                self.notify("Failed to research dimension", severity="error")
                self.query_one("#research_status").update(f"Error researching dimension: {dimension_name}")
                
        except Exception as e:
            logger.error(f"Error researching dimension: {str(e)}")
            self.notify("Failed to research dimension", severity="error")
            self.query_one("#research_status").update(f"Error during research: {str(e)}")
            
        finally:
            # Re-enable the research button
            research_button.disabled = False
            completed = getattr(dimension, "completed", False)
            research_button.label = "Re-Research Dimension" if completed else "Research Dimension"
            
            # Refresh the dimension display
            await self.display_current_dimension()
    
    async def _create_branch_teams_ui(self, dimension_name: str) -> None:
        """Create branch teams UI elements for the current dimension."""
        # Clear existing branch team displays
        branch_container = self.query_one("#branch_teams_container")
        branch_container.remove_children()
        
        # Generate 2-3 simulated branch teams
        branch_names = [
            f"Branch A: {dimension_name} Mainstream",
            f"Branch B: {dimension_name} Cutting-edge",
            f"Branch C: {dimension_name} Cross-paradigm"
        ]
        
        # Add progress indicators for each branch team
        for i, branch_name in enumerate(branch_names):
            branch_id = f"branch_{i+1}"
            self.branch_progress[branch_id] = 0
            
            branch_row = Container(
                Label(branch_name, classes="branch_label"),
                ProgressBar(id=f"{branch_id}_progress", total=100, show_percentage=True),
                Static("Preparing...", id=f"{branch_id}_status"),
                id=branch_id,
                classes="branch_row"
            )
            branch_container.mount(branch_row)
            
            # Start animation task for this branch
            asyncio.create_task(
                self._animate_branch_progress(branch_id, 
                                            delay_start=i*0.5)  # Stagger the start times
            )
    
    async def _animate_branch_progress(self, branch_id: str, delay_start: float = 0) -> None:
        """Animate a branch team's progress bar."""
        # Delay before starting
        await asyncio.sleep(delay_start)
        
        # Progress steps and messages
        progress_steps = [5, 15, 25, 40, 55, 70, 85, 95]
        messages = [
            "Initializing branch research...",
            "Analyzing dimension context...",
            "Exploring paradigm options...",
            "Gathering web search results...",
            "Processing research findings...",
            "Extracting key technologies...",
            "Analyzing integration points...",
            "Branch research completed."
        ]
        
        # Animate progress
        for i, (progress, message) in enumerate(zip(progress_steps, messages)):
            if not self._is_mounted:
                break
                
            try:
                # Update branch progress
                self.branch_progress[branch_id] = progress
                
                # Find and update the progress bar and status
                progress_bar = self.query_one(f"#{branch_id}_progress")
                status = self.query_one(f"#{branch_id}_status")
                
                progress_bar.update(progress=progress)
                status.update(message)
                
                # Also update overall progress - each branch contributes proportionally
                await self._update_overall_progress()
                
                # Random delay between 0.6 and 1.2 seconds to make it look more natural
                import random
                delay = 0.6 + random.random() * 0.6
                await asyncio.sleep(delay)
                
            except Exception as e:
                logger.error(f"Error updating branch progress: {str(e)}")
                
    async def _update_overall_progress(self) -> None:
        """Update the overall research progress based on all teams."""
        foundation_progress = self.query_one("#foundation_progress").value
        
        # Average all branch progresses
        branch_avg = 0
        if self.branch_progress:
            branch_avg = sum(self.branch_progress.values()) / len(self.branch_progress)
            
        integration_progress = self.query_one("#integration_progress").value
        
        # Weight them: 30% foundation, 50% branches, 20% integration
        weighted_progress = (
            (foundation_progress * 0.3) +
            (branch_avg * 0.5) +
            (integration_progress * 0.2)
        )
        
        # Scale to overall progress (30% to 80%)
        overall_progress = 30 + (weighted_progress / 100 * 50)
        self.query_one("#overall_progress").update(progress=int(overall_progress))
    
    async def _update_dimension_research_progress(self, dimension_name: str) -> None:
        """Update progress indicators after a dimension is researched."""
        # Update all branch progress indicators to 100%
        branch_container = self.query_one("#branch_teams_container")
        for branch_id in self.branch_progress:
            self.branch_progress[branch_id] = 100
            
            try:
                progress_bar = self.query_one(f"#{branch_id}_progress")
                status = self.query_one(f"#{branch_id}_status")
                
                progress_bar.update(progress=100)
                status.update("Research completed successfully.")
            except Exception:
                pass
        
        # Update integration progress
        integration_progress = self.query_one("#integration_progress")
        integration_status = self.query_one("#integration_status")
        
        # Calculate completion percentage based on researched dimensions
        completed_count = sum(1 for dim in self.dimensions if getattr(dim, "completed", False))
        total_dimensions = len(self.dimensions)
        
        if total_dimensions > 0:
            completion_pct = min(100, (completed_count / total_dimensions) * 100)
            integration_progress.update(progress=int(completion_pct))
            
            if completion_pct < 100:
                integration_status.update(f"Integrating results: {completed_count}/{total_dimensions} dimensions")
            else:
                integration_status.update("Integration complete!")
        
        # Update overall progress (at least 70% after a dimension is completed)
        await self._update_overall_progress()
    
    async def _update_research_paths(self) -> None:
        """Update the research paths visualization."""
        # This would normally come from actual path data
        # For now, create a sample visualization
        paths_viz = """
# Research Paths Identified

## Path 1: Traditional Approach
Foundation: Mainstream established technologies
Integration: Standard integration patterns

## Path 2: Cloud-Native Approach
Foundation: Cutting-edge cloud technologies
Integration: Microservices architecture

## Path 3: Hybrid Innovation
Foundation: Cross-paradigm combination
Integration: Custom adapters between components
        """
        
        self.query_one("#paths_visualization").update(paths_viz)
    
    async def _display_cross_paradigm_opportunities(self) -> None:
        """Display cross-paradigm opportunities in the UI."""
        # Sample opportunities (would come from actual research)
        opportunities_list = self.query_one("#opportunities_list")
        opportunities_list.remove_children()
        
        # Sample opportunities
        opportunities = [
            "Combine mainstream UI frameworks with cutting-edge backend technologies",
            "Integrate experimental data processing with established storage solutions",
            "Cross-paradigm opportunity: Custom domain language + ML-based interpretation",
            "Combine cloud infrastructure with edge computing components"
        ]
        
        # Add each opportunity to the list
        for opp in opportunities:
            opportunities_list.mount(Static(opp, classes="opportunity"))
    
    @handle_async_errors
    async def research_current_component(self) -> None:
        """Research the current component."""
        if not self.session_id or not self.components or self.current_component_index >= len(self.components):
            logger.error("Cannot research: invalid session or component")
            return
        
        # Disable the research button while processing
        research_button = self.query_one("#research_button")
        research_button.disabled = True
        
        # Update the status
        component = self.components[self.current_component_index]
        self.query_one("#research_status").update(f"Researching component: {component.name}...")
        
        # Set a spinner or indicator that research is in progress
        research_button.label = "Researching..."
        
        try:
            # Research the component
            updated_component = await self.research_team.research_component(self.session_id)
            
            if updated_component:
                # Update the local component with the research results
                self.components[self.current_component_index] = updated_component
                
                # If this component wasn't previously completed, increment progress
                if not component.completed:
                    self._progress_value += 1
                    progress_bar = self.query_one("#overall_progress")
                    progress_bar.update(progress=self._progress_value)
                
                # Update the status
                self.query_one("#research_status").update(
                    f"Component '{updated_component.name}' researched successfully."
                )
                
                # Notify success
                self.notify(f"Research completed for '{updated_component.name}'", severity="success")
                
                # Show the findings container
                self.query_one("#findings_container").display = True
                
                # Clear the findings display and prompt to select a paradigm
                self.query_one("#findings_display").text = "Select a paradigm category to view findings."
                
                # Check if all components have been researched
                all_completed = all(comp.completed for comp in self.components)
                self.query_one("#create_report_button").disabled = not all_completed
                
                # If all completed, update the status
                if all_completed:
                    self.query_one("#research_status").update(
                        "All components researched. Ready to create research report."
                    )
            else:
                self.notify("Failed to research component", severity="error")
                self.query_one("#research_status").update(f"Error researching component: {component.name}")
                
        except Exception as e:
            logger.error(f"Error researching component: {str(e)}")
            self.notify("Failed to research component", severity="error")
            self.query_one("#research_status").update(f"Error during research: {str(e)}")
            
        finally:
            # Re-enable the research button
            research_button.disabled = False
            research_button.label = "Re-Research Component" if component.completed else "Research Component"
            
            # Refresh the component display
            await self.display_current_component()
    
    @handle_async_errors
    async def previous_dimension(self) -> None:
        """Navigate to the previous dimension."""
        if self.current_dimension_index > 0:
            self.current_dimension_index -= 1
            await self.display_current_dimension()
        else:
            # Already at the first dimension
            self.notify("Already at the first dimension", severity="warning")
    
    @handle_async_errors
    async def next_dimension(self) -> None:
        """Navigate to the next dimension."""
        if self.current_dimension_index < len(self.dimensions) - 1:
            self.current_dimension_index += 1
            await self.display_current_dimension()
        else:
            # Already at the last dimension
            self.notify("Already at the last dimension", severity="warning")
    
    @handle_async_errors
    async def explore_selected_path(self) -> None:
        """Explore the selected research path."""
        # This is a placeholder for the real implementation
        # In a complete implementation, this would show details of the selected path
        self.notify("Path exploration feature coming soon", severity="information")
        self.query_one("#research_status").update("Exploring research paths...")
    
    @handle_async_errors
    async def display_document_summary(self, document_type: str) -> None:
        """Display a summary of the selected document."""
        summary = ""
        
        if document_type == "vision":
            if self.project_vision:
                summary = self._generate_vision_summary(self.project_vision)
            else:
                summary = "No vision document available"
                
        elif document_type == "prd":
            if self.prd_document:
                summary = self._generate_prd_summary(self.prd_document)
            else:
                summary = "No PRD document available"
                
        elif document_type == "requirements":
            if self.research_requirements:
                summary = self._generate_requirements_summary(self.research_requirements)
            else:
                summary = "No research requirements document available"
        
        # Update the summary display
        self.query_one("#context_summary").update(summary)
    
    def _generate_vision_summary(self, vision_document: str) -> str:
        """Generate a concise summary of the vision document."""
        # Extract first paragraph as summary (more sophisticated extraction would be better)
        paragraphs = vision_document.split('\n\n')
        
        # Filter out headings and empty paragraphs
        content_paragraphs = [p for p in paragraphs 
                             if p and not p.startswith('#') and len(p) > 20]
        
        if content_paragraphs:
            # Return the first substantial paragraph
            return f"**Vision Summary:**\n\n{content_paragraphs[0][:250]}..."
        else:
            return "**Vision document available but couldn't extract summary**"
    
    def _generate_prd_summary(self, prd_document: str) -> str:
        """Generate a concise summary of the PRD document."""
        # Count requirements or features as a simple metric
        req_count = prd_document.lower().count('requirement')
        feature_count = prd_document.lower().count('feature')
        
        # Extract title if available
        import re
        title_match = re.search(r'^#\s+(.+)$', prd_document, re.MULTILINE)
        title = title_match.group(1) if title_match else "Product Requirements Document"
        
        return f"**PRD: {title}**\n\n" \
               f"This document contains approximately {req_count} references to requirements " \
               f"and {feature_count} references to features. It provides the detailed " \
               f"product specifications needed for research and architecture design."
    
    def _generate_requirements_summary(self, requirements_document: str) -> str:
        """Generate a concise summary of the research requirements document."""
        # Count dimension or component references
        dimension_count = requirements_document.lower().count('dimension')
        component_count = requirements_document.lower().count('component')
        
        # Count paradigm references
        paradigm_count = 0
        for paradigm in ["established", "mainstream", "cutting-edge", "experimental", 
                         "cross-paradigm", "first-principles"]:
            paradigm_count += requirements_document.lower().count(paradigm)
        
        return f"**Research Requirements**\n\n" \
               f"This document outlines {dimension_count} research dimensions " \
               f"or {component_count} components to investigate across " \
               f"{paradigm_count} paradigm references. It provides the framework " \
               f"for comprehensive multi-dimensional research."
    
    @handle_async_errors
    async def previous_component(self) -> None:
        """Navigate to the previous component."""
        if self.current_component_index > 0:
            self.current_component_index -= 1
            await self.display_current_component()
        else:
            # Already at the first component
            self.notify("Already at the first component", severity="warning")
    
    async def action_previous_component(self) -> None:
        """Handle keyboard shortcut for previous component."""
        await self.previous_component()
    
    @handle_async_errors
    async def next_component(self) -> None:
        """Navigate to the next component."""
        if self.current_component_index < len(self.components) - 1:
            self.current_component_index += 1
            await self.display_current_component()
        else:
            # Already at the last component
            self.notify("Already at the last component", severity="warning")
    
    async def action_next_component(self) -> None:
        """Handle keyboard shortcut for next component."""
        await self.next_component()
    
    @handle_async_errors
    async def show_paradigm_findings(self, paradigm: str) -> None:
        """Show findings for a specific paradigm category."""
        if not self.components or self.current_component_index >= len(self.components):
            return
        
        # Get the current component
        component = self.components[self.current_component_index]
        
        if not component.completed:
            self.notify("Component not yet researched", severity="warning")
            return
        
        # Map button ID to paradigm category
        paradigm_mapping = {
            "established": ParadigmCategory.ESTABLISHED,
            "mainstream": ParadigmCategory.MAINSTREAM,
            "cutting_edge": ParadigmCategory.CUTTING_EDGE,
            "experimental": ParadigmCategory.EXPERIMENTAL,
            "cross_paradigm": ParadigmCategory.CROSS_PARADIGM,
            "first_principles": ParadigmCategory.FIRST_PRINCIPLES
        }
        
        if paradigm not in paradigm_mapping:
            self.notify(f"Unknown paradigm category: {paradigm}", severity="error")
            return
        
        paradigm_category = paradigm_mapping[paradigm]
        findings = component.paradigms.get(paradigm_category, [])
        
        # Format the findings for display
        if not findings:
            formatted_findings = f"No findings for {paradigm_category.value.replace('_', ' ').title()} approaches."
        else:
            formatted_findings = f"# {paradigm_category.value.replace('_', ' ').title()} Approaches\n\n"
            
            for i, finding in enumerate(findings, 1):
                formatted_findings += f"## {i}. {finding.get('name', 'Unnamed Approach')}\n\n"
                formatted_findings += f"{finding.get('description', 'No description provided.')}\n\n"
                
                if 'strengths' in finding and finding['strengths']:
                    formatted_findings += "### Strengths\n\n"
                    for strength in finding['strengths']:
                        formatted_findings += f"- {strength}\n"
                    formatted_findings += "\n"
                
                if 'limitations' in finding and finding['limitations']:
                    formatted_findings += "### Limitations\n\n"
                    for limitation in finding['limitations']:
                        formatted_findings += f"- {limitation}\n"
                    formatted_findings += "\n"
                
                if 'examples' in finding and finding['examples']:
                    formatted_findings += "### Examples\n\n"
                    for example in finding['examples']:
                        formatted_findings += f"- {example}\n"
                    formatted_findings += "\n"
                
                if 'implementation_complexity' in finding:
                    formatted_findings += f"### Implementation Complexity\n\n{finding['implementation_complexity']}\n\n"
                
                if 'ecosystem' in finding:
                    formatted_findings += f"### Ecosystem Support\n\n{finding['ecosystem']}\n\n"
                
                formatted_findings += "---\n\n"
        
        # Update the findings display
        self.query_one("#findings_display").text = formatted_findings
        
        # Highlight the selected paradigm button
        for button_id in ["established", "mainstream", "cutting_edge", "experimental", "cross_paradigm", "first_principles"]:
            button = self.query_one(f"#show_{button_id}_button")
            if button_id == paradigm:
                button.variant = "primary"
            else:
                button.variant = "default"
    
    @handle_async_errors
    async def view_research_report(self, report_path: str) -> None:
        """View an existing research report."""
        if not self.session_id:
            logger.error("Cannot view report: no active session")
            return
            
        try:
            # Get the document content
            from ideasfactory.documents.document_manager import DocumentManager
            doc_manager = DocumentManager()
            document = doc_manager.get_document(report_path)
            
            if document and "content" in document:
                # Configure for viewing the report
                if hasattr(self.app, "document_review_screen"):
                    self.app.document_review_screen.configure_for_agent(
                        document_source=DocumentSource.RESEARCH_TEAM,
                        session_id=self.session_id,
                        document_content=document["content"],
                        document_title="Multi-Agent Research Report",
                        document_type="research-report",
                        revision_callback=None,
                        completion_callback=None,
                        back_screen="research_screen",
                        next_screen=None
                    )
                    
                    # Show the document review
                    self.app.push_screen("document_review_screen")
                else:
                    self.notify("Document review screen not available", severity="error")
            else:
                self.notify("Failed to load research report content", severity="error")
                
        except Exception as e:
            logger.error(f"Error viewing research report: {str(e)}")
            self.notify(f"Report viewing error: {str(e)}", severity="error")
            self.query_one("#research_status").update(f"Error viewing report: {str(e)}")
    
    async def _animate_report_generation(self) -> None:
        """Animate the report generation process with visual feedback."""
        # Status messages to show during report generation
        messages = [
            "Collecting findings from all dimensions...",
            "Synthesizing research from multiple paradigms...",
            "Generating dimensional analysis...",
            "Creating cross-paradigm opportunity map...",
            "Building research visualizations...",
            "Drafting executive summary...",
            "Compiling recommendations...",
            "Formatting comprehensive report...",
            "Finalizing research report..."
        ]
        
        # Update status message every 1.2 seconds
        for i, message in enumerate(messages):
            if self._is_mounted:  # Check if screen is still mounted
                # Update integration status
                self.query_one("#integration_status").update(message)
                
                # Gradually increase integration progress (from wherever it is to 95%)
                current = self.query_one("#integration_progress").value
                target = min(95, current + (95 - current) / (len(messages) - i))
                self.query_one("#integration_progress").update(progress=int(target))
                
                # Update overall progress (90% to 98%)
                overall_progress = 90 + int((i / len(messages)) * 8)
                self.query_one("#overall_progress").update(progress=overall_progress)
                
                # Update research status occasionally
                if i % 3 == 0:
                    self.query_one("#research_status").update(f"Creating research report: {message}")
                
                # Random delay between 0.8 and 1.4 seconds to make it look more natural
                import random
                delay = 0.8 + random.random() * 0.6
                await asyncio.sleep(delay)
    
    async def action_research_component(self) -> None:
        """Handle keyboard shortcut for researching component."""
        await self.research_current_component()
    
    async def action_create_report(self) -> None:
        """Handle keyboard shortcut for creating report."""
        await self.create_research_report()
    
    async def go_back(self) -> None:
        """Go back to the previous screen."""
        # Use pop_screen to go back to the previous screen
        self.app.pop_screen()
    
    async def action_back(self) -> None:
        """Handle keyboard shortcut for going back."""
        await self.go_back()
    
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
                back_screen="research_screen",
                next_screen=None
            )
            # Show the document review screen
            self.app.push_screen("document_review_screen")
        else:
            self.notify("Document review screen not available", severity="error")
    
    @handle_async_errors
    async def view_prd_document(self) -> None:
        """View the PRD document."""
        if not self.prd_document:
            self.notify("No PRD document available", severity="error")
            return
        
        # Use the document review screen to display the PRD
        if hasattr(self.app, "document_review_screen"):
            # Configure the document review for viewing only
            self.app.document_review_screen.configure_for_agent(
                document_source=DocumentSource.PROJECT_MANAGER,
                session_id=self.session_id,
                document_content=self.prd_document,
                document_title="PRD Document",
                document_type="prd",
                revision_callback=None,  # No revision for viewing only
                completion_callback=None,
                back_screen="research_screen",
                next_screen=None
            )
            # Show the document review screen
            self.app.push_screen("document_review_screen")
        else:
            self.notify("Document review screen not available", severity="error")
    
    @handle_async_errors
    async def view_research_requirements(self) -> None:
        """View the research requirements document."""
        if not self.research_requirements:
            self.notify("No research requirements document available", severity="error")
            return
        
        # Use the document review screen to display the requirements
        if hasattr(self.app, "document_review_screen"):
            # Configure the document review for viewing only
            self.app.document_review_screen.configure_for_agent(
                document_source=DocumentSource.ARCHITECT,
                session_id=self.session_id,
                document_content=self.research_requirements,
                document_title="Technical Research Requirements",
                document_type="research-requirements",
                revision_callback=None,  # No revision for viewing only
                completion_callback=None,
                back_screen="research_screen",
                next_screen=None
            )
            # Show the document review screen
            self.app.push_screen("document_review_screen")
        else:
            self.notify("Document review screen not available", severity="error")