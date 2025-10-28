from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class Node(BaseModel):
    """Graph node"""
    id: str
    name: str
    color: Optional[str] = None


class Link(BaseModel):
    """Graph link"""
    source: str
    target: str
    color: Optional[str] = None


class Graph(BaseModel):
    """Graph structure"""
    nodes: List[Node] = Field(default_factory=list)
    links: List[Link] = Field(default_factory=list)


class GraphList(BaseModel):
    """List of graphs"""
    graphs: List[Graph] = Field(default_factory=list)


class IRNode(Node):
    """IriusRisk specific node"""
    node_type: str = ""


class RuleNode(Node):
    """Rule node"""
    rule_name: str = ""


class Change(BaseModel):
    """Change item"""
    type: str
    description: str


class ChangelogItem(BaseModel):
    """Changelog item"""
    item: str
    changes: List[Change] = Field(default_factory=list)


class ChangelogReport(BaseModel):
    """Changelog report"""
    items: List[ChangelogItem] = Field(default_factory=list)


class LibrarySummary(BaseModel):
    """Library summary"""
    ref: str
    name: str
    num_components: int = 0
    num_risk_patterns: int = 0


class LibrarySummariesResponse(BaseModel):
    """Library summaries response"""
    summaries: List[LibrarySummary] = Field(default_factory=list)