"""Save and load DailySchedule to/from JSON files."""
import json
from datetime import time
from pathlib import Path
from typing import Optional

from lesson_planner.models.daily_schedule import DailySchedule
from lesson_planner.data.activity_library import ActivityLibrary

FILE_EXTENSION = ".pathway"


def save_schedule(schedule: DailySchedule, path: Path) -> None:
    data = {
        "name": schedule.name,
        "start_time": schedule.start_time.strftime("%H:%M"),
        "blocks": [
            {
                "activity_id": block.activity.id,
                "actual_minutes": block.actual_minutes,
            }
            for block in schedule.blocks
        ],
    }
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def load_schedule(path: Path, library: ActivityLibrary) -> DailySchedule:
    raw = json.loads(path.read_text(encoding="utf-8"))

    h, m = (int(x) for x in raw.get("start_time", "08:00").split(":"))
    schedule = DailySchedule(
        name=raw.get("name", path.stem),
        start_time=time(h, m),
    )

    missing = []
    for entry in raw.get("blocks", []):
        activity = library.by_id(entry["activity_id"])
        if activity is None:
            missing.append(entry["activity_id"])
            continue
        block = schedule.add_activity(activity)
        if entry.get("actual_minutes") is not None:
            block.set_duration(entry["actual_minutes"])

    if missing:
        raise ValueError(
            f"Schedule references unknown activity IDs: {', '.join(missing)}"
        )

    return schedule
