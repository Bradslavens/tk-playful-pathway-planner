from dataclasses import dataclass, field
from typing import Optional
from .activity import Activity


@dataclass
class ScheduleBlock:
    activity: Activity
    actual_minutes: Optional[int] = None  # None means use activity.suggested_minutes

    @property
    def duration(self) -> int:
        return self.actual_minutes if self.actual_minutes is not None else self.activity.suggested_minutes

    def set_duration(self, minutes: int) -> None:
        if minutes < 1:
            raise ValueError("Duration must be at least 1 minute")
        self.actual_minutes = minutes

    def reset_duration(self) -> None:
        self.actual_minutes = None
