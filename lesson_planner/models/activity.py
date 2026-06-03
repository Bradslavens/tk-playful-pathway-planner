from dataclasses import dataclass, field
from typing import List


VALID_DOMAINS = {
    "Social-Emotional",
    "Language",
    "Mathematics",
    "Science",
    "Physical",
    "Arts",
    "Approaches to Learning",
}

VALID_ENERGY_LEVELS = {"low", "medium", "high"}


@dataclass(frozen=True)
class Activity:
    id: str
    title: str
    domain: str
    suggested_minutes: int
    icon: str = ""
    description: str = ""
    materials: List[str] = field(default_factory=list)
    energy_level: str = "medium"
    adaptations: List[str] = field(default_factory=list)

    def __post_init__(self):
        if not self.id.strip():
            raise ValueError("Activity id must not be empty")
        if not self.title.strip():
            raise ValueError("Activity title must not be empty")
        if self.suggested_minutes < 1:
            raise ValueError("suggested_minutes must be at least 1")
        if self.energy_level not in VALID_ENERGY_LEVELS:
            raise ValueError(f"energy_level must be one of {VALID_ENERGY_LEVELS}")
