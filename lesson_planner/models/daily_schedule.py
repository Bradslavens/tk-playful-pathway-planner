from dataclasses import dataclass, field
from typing import List, Optional
from datetime import time, timedelta, datetime
from .activity import Activity
from .schedule_block import ScheduleBlock


@dataclass
class DailySchedule:
    name: str = "Untitled Schedule"
    start_time: time = field(default_factory=lambda: time(8, 0))
    blocks: List[ScheduleBlock] = field(default_factory=list)

    def add_activity(self, activity: Activity, at_index: Optional[int] = None) -> ScheduleBlock:
        block = ScheduleBlock(activity=activity)
        if at_index is None:
            self.blocks.append(block)
        else:
            self.blocks.insert(at_index, block)
        return block

    def remove_block(self, index: int) -> ScheduleBlock:
        if not 0 <= index < len(self.blocks):
            raise IndexError(f"No block at index {index}")
        return self.blocks.pop(index)

    def move_block(self, from_index: int, to_index: int) -> None:
        if not 0 <= from_index < len(self.blocks):
            raise IndexError(f"No block at index {from_index}")
        if not 0 <= to_index < len(self.blocks):
            raise IndexError(f"Target index {to_index} out of range")
        block = self.blocks.pop(from_index)
        self.blocks.insert(to_index, block)

    @property
    def total_minutes(self) -> int:
        return sum(b.duration for b in self.blocks)

    def block_start_time(self, index: int) -> time:
        if not 0 <= index < len(self.blocks):
            raise IndexError(f"No block at index {index}")
        offset = sum(self.blocks[i].duration for i in range(index))
        dt = datetime.combine(datetime.today(), self.start_time) + timedelta(minutes=offset)
        return dt.time()

    def is_empty(self) -> bool:
        return len(self.blocks) == 0

    def clear(self) -> None:
        self.blocks.clear()
