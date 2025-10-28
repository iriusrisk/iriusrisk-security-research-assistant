from dataclasses import dataclass, field
from typing import List, Dict, Optional


@dataclass
class VersionNamesResponse:
    """Version names response"""
    project: str
    versions: List[str] = field(default_factory=list)


@dataclass
class ILEError:
    """Error response"""
    message: str
    code: Optional[str] = None


# Request models
@dataclass
class CategoryRequest:
    ref: str
    name: str


@dataclass
class ComponentRequest:
    ref: str
    name: str
    desc: str
    category_ref: str
    visible: str


@dataclass
class ControlRequest:
    ref: str
    name: str
    desc: str
    state: str
    cost: str


@dataclass
class ControlUpdateRequest:
    ref: str
    name: str
    desc: str
    state: str
    cost: str


@dataclass
class LibraryRequest:
    ref: str
    name: str
    desc: str
    revision: str
    filename: str
    enabled: str


@dataclass
class LibraryUpdateRequest:
    ref: str
    name: str
    desc: str
    revision: str
    filename: str
    enabled: str


@dataclass
class MergeLibraryRequest:
    src_version: str
    src_library: str
    dst_version: str
    dst_library: str


@dataclass
class ReferenceRequest:
    name: str
    url: str


@dataclass
class ReferenceItemRequest:
    ref: str
    name: str
    url: str


@dataclass
class RelationRequest:
    risk_pattern_uuid: str
    usecase_uuid: str
    threat_uuid: str
    weakness_uuid: str
    control_uuid: str
    mitigation: str


@dataclass
class RiskPatternRequest:
    ref: str
    name: str
    desc: str


@dataclass
class RiskRatingRequest:
    confidentiality: str
    integrity: str
    availability: str
    ease_of_exploitation: str


@dataclass
class StandardRequest:
    supported_standard_ref: str
    standard_ref: str


@dataclass
class StandardItemRequest:
    ref: str
    supported_standard_ref: str
    standard_ref: str


@dataclass
class SupportedStandardRequest:
    supported_standard_ref: str
    supported_standard_name: str


@dataclass
class TestRequest:
    steps: str


@dataclass
class ThreatRequest:
    ref: str
    name: str
    desc: str


@dataclass
class ThreatUpdateRequest:
    ref: str
    name: str
    desc: str


@dataclass
class UsecaseRequest:
    ref: str
    name: str
    desc: str


@dataclass
class WeaknessRequest:
    ref: str
    name: str
    desc: str
    impact: str


@dataclass
class CopyVersionRequest:
    src_version: str
    ref: str


@dataclass
class ChangelogRequest:
    from_version: str
    to_version: str


@dataclass
class ChangelogVersionRequest:
    version: str


@dataclass
class ContentReportRequest:
    version: str
    library: str


@dataclass
class SuggestionRequest:
    text: str