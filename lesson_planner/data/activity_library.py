import json
from pathlib import Path
from typing import List, Optional
from lesson_planner.models.activity import Activity


_DEFAULT_SEED = Path(__file__).parent / "seed_activities.json"


def _activity_from_dict(d: dict) -> Activity:
    return Activity(
        id=d["id"],
        title=d["title"],
        domain=d["domain"],
        suggested_minutes=d["suggested_minutes"],
        icon=d.get("icon", ""),
        description=d.get("description", ""),
        materials=list(d.get("materials", [])),
        energy_level=d.get("energy_level", "medium"),
        adaptations=list(d.get("adaptations", [])),
    )


class ActivityLibrary:
    def __init__(self, seed_path: Path = _DEFAULT_SEED):
        with open(seed_path, encoding="utf-8") as f:
            raw = json.load(f)
        self._activities: List[Activity] = [_activity_from_dict(d) for d in raw]

    @property
    def all(self) -> List[Activity]:
        return list(self._activities)

    def by_domain(self, domain: str) -> List[Activity]:
        return [a for a in self._activities if a.domain == domain]

    def search(self, query: str) -> List[Activity]:
        q = query.strip().lower()
        if not q:
            return self.all
        return [a for a in self._activities if q in a.title.lower() or q in a.description.lower()]

    def by_id(self, activity_id: str) -> Optional[Activity]:
        return next((a for a in self._activities if a.id == activity_id), None)

    @property
    def domains(self) -> List[str]:
        seen = []
        for a in self._activities:
            if a.domain not in seen:
                seen.append(a.domain)
        return seen
