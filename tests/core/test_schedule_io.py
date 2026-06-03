import json
import pytest
from datetime import time
from pathlib import Path

from lesson_planner.data.activity_library import ActivityLibrary
from lesson_planner.data.schedule_io import save_schedule, load_schedule, FILE_EXTENSION
from lesson_planner.models.daily_schedule import DailySchedule


@pytest.fixture
def library():
    return ActivityLibrary()


@pytest.fixture
def sample_schedule(library):
    s = DailySchedule(name="Test Day", start_time=time(8, 30))
    s.add_activity(library.by_id("morning_greeting"))
    block = s.add_activity(library.by_id("story_time"))
    block.set_duration(20)
    s.add_activity(library.by_id("outdoor_gross_motor"))
    return s


class TestSaveSchedule:
    def test_creates_file(self, tmp_path, sample_schedule):
        p = tmp_path / "day.pathway"
        save_schedule(sample_schedule, p)
        assert p.exists()

    def test_file_is_valid_json(self, tmp_path, sample_schedule):
        p = tmp_path / "day.pathway"
        save_schedule(sample_schedule, p)
        data = json.loads(p.read_text())
        assert isinstance(data, dict)

    def test_saves_name(self, tmp_path, sample_schedule):
        p = tmp_path / "day.pathway"
        save_schedule(sample_schedule, p)
        data = json.loads(p.read_text())
        assert data["name"] == "Test Day"

    def test_saves_start_time(self, tmp_path, sample_schedule):
        p = tmp_path / "day.pathway"
        save_schedule(sample_schedule, p)
        data = json.loads(p.read_text())
        assert data["start_time"] == "08:30"

    def test_saves_correct_block_count(self, tmp_path, sample_schedule):
        p = tmp_path / "day.pathway"
        save_schedule(sample_schedule, p)
        data = json.loads(p.read_text())
        assert len(data["blocks"]) == 3

    def test_saves_activity_ids(self, tmp_path, sample_schedule):
        p = tmp_path / "day.pathway"
        save_schedule(sample_schedule, p)
        data = json.loads(p.read_text())
        ids = [b["activity_id"] for b in data["blocks"]]
        assert ids == ["morning_greeting", "story_time", "outdoor_gross_motor"]

    def test_saves_null_when_using_default_duration(self, tmp_path, sample_schedule):
        p = tmp_path / "day.pathway"
        save_schedule(sample_schedule, p)
        data = json.loads(p.read_text())
        assert data["blocks"][0]["actual_minutes"] is None

    def test_saves_overridden_duration(self, tmp_path, sample_schedule):
        p = tmp_path / "day.pathway"
        save_schedule(sample_schedule, p)
        data = json.loads(p.read_text())
        assert data["blocks"][1]["actual_minutes"] == 20

    def test_empty_schedule_saves_empty_blocks(self, tmp_path, library):
        s = DailySchedule(name="Empty")
        p = tmp_path / "empty.pathway"
        save_schedule(s, p)
        data = json.loads(p.read_text())
        assert data["blocks"] == []


class TestLoadSchedule:
    def test_roundtrip(self, tmp_path, library, sample_schedule):
        p = tmp_path / "day.pathway"
        save_schedule(sample_schedule, p)
        loaded = load_schedule(p, library)
        assert loaded.name == sample_schedule.name
        assert loaded.start_time == sample_schedule.start_time
        assert len(loaded.blocks) == len(sample_schedule.blocks)

    def test_roundtrip_activity_ids(self, tmp_path, library, sample_schedule):
        p = tmp_path / "day.pathway"
        save_schedule(sample_schedule, p)
        loaded = load_schedule(p, library)
        original_ids = [b.activity.id for b in sample_schedule.blocks]
        loaded_ids = [b.activity.id for b in loaded.blocks]
        assert loaded_ids == original_ids

    def test_roundtrip_preserves_duration_override(self, tmp_path, library, sample_schedule):
        p = tmp_path / "day.pathway"
        save_schedule(sample_schedule, p)
        loaded = load_schedule(p, library)
        assert loaded.blocks[1].actual_minutes == 20
        assert loaded.blocks[1].duration == 20

    def test_roundtrip_null_duration_uses_suggested(self, tmp_path, library, sample_schedule):
        p = tmp_path / "day.pathway"
        save_schedule(sample_schedule, p)
        loaded = load_schedule(p, library)
        assert loaded.blocks[0].actual_minutes is None
        assert loaded.blocks[0].duration == loaded.blocks[0].activity.suggested_minutes

    def test_unknown_activity_id_raises(self, tmp_path, library):
        p = tmp_path / "bad.pathway"
        p.write_text(json.dumps({
            "name": "Bad",
            "start_time": "08:00",
            "blocks": [{"activity_id": "does_not_exist", "actual_minutes": None}]
        }), encoding="utf-8")
        with pytest.raises(ValueError, match="does_not_exist"):
            load_schedule(p, library)

    def test_missing_name_uses_filename(self, tmp_path, library):
        p = tmp_path / "monday.pathway"
        p.write_text(json.dumps({
            "start_time": "09:00",
            "blocks": []
        }), encoding="utf-8")
        loaded = load_schedule(p, library)
        assert loaded.name == "monday"

    def test_default_start_time_when_missing(self, tmp_path, library):
        p = tmp_path / "x.pathway"
        p.write_text(json.dumps({"name": "X", "blocks": []}), encoding="utf-8")
        loaded = load_schedule(p, library)
        assert loaded.start_time == time(8, 0)
