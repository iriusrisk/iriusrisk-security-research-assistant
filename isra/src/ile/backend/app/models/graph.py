from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class Node:
    """Graph node"""
    id: str
    name: str
    color: Optional[str] = None


@dataclass
class Link:
    """Graph link"""
    source: str
    target: str
    color: Optional[str] = None


@dataclass
class Graph:
    """Graph structure"""
    nodes: List[Node] = field(default_factory=list)
    links: List[Link] = field(default_factory=list)


@dataclass
class GraphList:
    """List of graphs"""
    graphs: List[Graph] = field(default_factory=list)


@dataclass
class IRNode(Node):
    """IriusRisk specific node"""
    node_type: str = ""


@dataclass
class RuleNode(Node):
    """Rule node"""
    rule_name: str = ""


@dataclass
class Change:
    """Change item"""
    type: str
    description: str


@dataclass
class ChangelogItem:
    """Changelog item"""
    item: str
    changes: List[Change] = field(default_factory=list)


@dataclass
class ChangelogReport:
    """Changelog report"""
    items: List[ChangelogItem] = field(default_factory=list)


@dataclass
class LibrarySummary:
    """Library summary"""
    ref: str
    name: str
    num_components: int = 0
    num_risk_patterns: int = 0


@dataclass
class LibrarySummariesResponse:
    """Library summaries response"""
    summaries: List[LibrarySummary] = field(default_factory=list)