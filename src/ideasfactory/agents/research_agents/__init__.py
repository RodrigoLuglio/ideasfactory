"""
Research agents package for IdeasFactory.

This package contains specialized research agents that work together
to conduct comprehensive dimensional research across paradigms.
"""

# Import specialized agents for easier access
from ideasfactory.agents.research_agents.base_agent import BaseResearchAgent
from ideasfactory.agents.research_agents.foundation_agent import FoundationAgent
from ideasfactory.agents.research_agents.paradigm_agent import (
    EstablishedParadigmAgent,
    MainstreamParadigmAgent,
    CuttingEdgeParadigmAgent,
    ExperimentalParadigmAgent,
    CrossParadigmAgent,
    FirstPrinciplesAgent,
)
from ideasfactory.agents.research_agents.path_agent import PathExplorationAgent
from ideasfactory.agents.research_agents.integration_agent import IntegrationAgent
from ideasfactory.agents.research_agents.synthesis_agent import SynthesisAgent
from ideasfactory.agents.research_agents.coordinator import AgentCoordinator
from ideasfactory.agents.research_agents.repository import DimensionalResearchRepository

# Import models
from ideasfactory.agents.research_agents.models import (
    ParadigmCategory,
    ResearchStatus,
    Technology,
    ParadigmFindings,
    ResearchDimension,
    ResearchPath,
    IntegrationOpportunity,
    ResearchSession,
    FoundationChoice,
    BranchResearchRequest,
    BranchResearchResult,
    ProgressUpdate,
)