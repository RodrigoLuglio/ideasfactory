"""
Research models for specialized research agents.

This module defines the data models used by the specialized research agents.
"""

import enum
from datetime import datetime
from typing import Dict, List, Any, Optional, Set, Union

from pydantic import BaseModel, Field


class ParadigmCategory(str, enum.Enum):
    """Categories of technology paradigms."""
    
    ESTABLISHED = "established"
    MAINSTREAM = "mainstream"
    CUTTING_EDGE = "cutting_edge"
    EXPERIMENTAL = "experimental"
    CROSS_PARADIGM = "cross_paradigm"
    FIRST_PRINCIPLES = "first_principles"


class ResearchStatus(str, enum.Enum):
    """Status of a research task or component."""
    
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class Technology(BaseModel):
    """A technology option within a paradigm."""
    
    name: str
    description: str
    strengths: List[str] = Field(default_factory=list)
    limitations: List[str] = Field(default_factory=list)
    examples: List[str] = Field(default_factory=list)
    implementation_complexity: str = ""
    ecosystem: str = ""
    maturity: str = ""
    relevance_score: float = 0.0


class ParadigmFindings(BaseModel):
    """Research findings for a specific paradigm category."""
    
    category: ParadigmCategory
    technologies: List[Technology] = Field(default_factory=list)
    approach_summary: str = ""
    integration_points: List[str] = Field(default_factory=list)
    paradigm_risks: List[str] = Field(default_factory=list)
    completion_status: ResearchStatus = ResearchStatus.PENDING


class ResearchDimension(BaseModel):
    """A dimension or aspect of the research requirements."""
    
    id: str
    name: str
    description: str
    type: str  # "foundation", "feature", "integration", etc.
    dependencies: List[str] = Field(default_factory=list)
    importance: int = 5  # 1-10 scale
    complexity: int = 5  # 1-10 scale
    completed: bool = False
    status: ResearchStatus = ResearchStatus.PENDING
    findings: Dict[ParadigmCategory, ParadigmFindings] = Field(default_factory=dict)


class ResearchPath(BaseModel):
    """A potential implementation path based on foundation choices."""
    
    id: str
    name: str
    description: str
    foundation_choices: Dict[str, str]  # dimension_id -> technology_name
    compatible_technologies: Dict[str, List[Technology]] = Field(default_factory=dict)
    advantages: List[str] = Field(default_factory=list)
    disadvantages: List[str] = Field(default_factory=list)
    risk_level: int = 5  # 1-10 scale
    innovation_level: int = 5  # 1-10 scale
    implementation_complexity: int = 5  # 1-10 scale


class IntegrationOpportunity(BaseModel):
    """An opportunity to integrate across paradigms."""
    
    id: str
    name: str
    description: str
    involved_dimensions: List[str] = Field(default_factory=list)
    involved_technologies: List[str] = Field(default_factory=list)
    benefits: List[str] = Field(default_factory=list)
    challenges: List[str] = Field(default_factory=list)
    innovation_level: int = 5  # 1-10 scale


class ResearchSession(BaseModel):
    """Session state for specialized research team."""
    
    id: str
    project_vision: str = ""
    prd_content: str = ""
    foundation_research_requirements: str = ""
    
    dimensions: List[ResearchDimension] = Field(default_factory=list)
    foundation_dimensions: List[str] = Field(default_factory=list)  # IDs of foundation dimensions
    
    research_paths: List[ResearchPath] = Field(default_factory=list)
    integration_opportunities: List[IntegrationOpportunity] = Field(default_factory=list)
    
    # Progress tracking
    foundation_research_complete: bool = False
    paradigm_research_complete: bool = False
    path_research_complete: bool = False
    integration_research_complete: bool = False
    synthesis_complete: bool = False
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    research_report_path: Optional[str] = None


class FoundationChoice(BaseModel):
    """A choice for a foundation dimension that forms the basis of a path."""
    
    dimension_id: str
    dimension_name: str
    technology_name: str
    technology_description: str
    paradigm_category: ParadigmCategory


class BranchResearchRequest(BaseModel):
    """Request to research a dimension across paradigm branches."""
    
    dimension_id: str
    foundation_choices: List[FoundationChoice] = Field(default_factory=list)
    priority: int = 5


class BranchResearchResult(BaseModel):
    """Results from researching a dimension across paradigm branches."""
    
    dimension_id: str
    findings: Dict[ParadigmCategory, ParadigmFindings]
    research_notes: str = ""


class ProgressUpdate(BaseModel):
    """Progress update for a research task."""
    
    task_id: str
    task_type: str
    progress_percentage: float
    status: ResearchStatus
    message: str = ""
    timestamp: datetime = Field(default_factory=datetime.now)