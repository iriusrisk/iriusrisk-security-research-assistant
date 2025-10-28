from abc import ABC
from typing import Dict, List, Optional
import uuid
from enum import Enum
from pydantic import BaseModel, Field


class IRBaseElementNoUUID(BaseModel):
    """Base class for elements without UUID"""
    ref: str
    name: str = ""
    desc: str = ""


class IRBaseElement(IRBaseElementNoUUID):
    """Base class for most IriusRisk elements with UUID"""
    uuid: str = Field(default_factory=lambda: str(uuid.uuid4()))


class ItemType(Enum):
    """Enum for item types"""
    THREAT = "THREAT"
    WEAKNESS_TEST = "WEAKNESS_TEST"
    CONTROL = "CONTROL"
    CONTROL_TEST = "CONTROL_TEST"