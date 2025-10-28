from abc import ABC
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import uuid
from enum import Enum


@dataclass
class IRBaseElementNoUUID:
    """Base class for elements without UUID"""
    ref: str
    name: str = ""
    desc: str = ""

    def __init__(self, ref: str, name: str = "", desc: str = ""):
        self.ref = ref
        self.name = name
        self.desc = desc


@dataclass
class IRBaseElement(IRBaseElementNoUUID):
    """Base class for most IriusRisk elements with UUID"""
    uuid: str = field(default_factory=lambda: str(uuid.uuid4()))

    def __init__(self, ref: str, name: str, desc: str, uuid: Optional[str] = None):
        super().__init__(ref, name, desc)
        self.uuid = uuid if uuid else str(uuid.uuid4())


class ItemType(Enum):
    """Enum for item types"""
    THREAT = "THREAT"
    WEAKNESS_TEST = "WEAKNESS_TEST"
    CONTROL = "CONTROL"
    CONTROL_TEST = "CONTROL_TEST"