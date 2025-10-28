from dataclasses import dataclass, field
from typing import List, Dict
from .base import IRBaseElement


@dataclass
class IRProjectReport(IRBaseElement):
    """Project report"""
    version_reports: List['IRVersionReport'] = field(default_factory=list)


@dataclass
class IRVersionReport:
    """Version report"""
    version: str
    num_libraries: int = 0
    num_risk_patterns: int = 0
    num_usecases: int = 0
    num_threats: int = 0
    num_weaknesses: int = 0
    num_controls: int = 0
    num_references: int = 0
    num_standards: int = 0
    num_categories: int = 0
    num_components: int = 0
    num_rules: int = 0
    library_reports: List['IRLibraryReport'] = field(default_factory=list)


@dataclass
class IRLibraryReport:
    """Library report"""
    library_ref: str
    library_name: str
    library_desc: str
    revision: str
    enabled: str
    library_filename: str
    num_component_definitions: int = 0
    num_risk_patterns: int = 0
    num_rules: int = 0
    num_usecases: int = 0
    num_threats: int = 0


@dataclass
class IRMitigationItem:
    """Mitigation item"""
    ref: str
    mitigation: str


@dataclass
class IRMitigationRiskPattern:
    """Mitigation risk pattern"""
    risk_pattern_ref: str
    mitigation_items: List[IRMitigationItem] = field(default_factory=list)


@dataclass
class IRMitigationReport:
    """Mitigation report"""
    risk_patterns: List[IRMitigationRiskPattern] = field(default_factory=list)


@dataclass
class IRSuggestions:
    """Suggestions"""
    suggestions: List[str] = field(default_factory=list)


@dataclass
class IRTestReport:
    """Test report"""
    tests: List[str] = field(default_factory=list)