import pytest
from lesson_planner.models.activity import Activity
from lesson_planner.models.schedule_block import ScheduleBlock


def make_activity(minutes=20):
    return Activity(id="a1", title="Circle Time", domain="Social-Emotional", suggested_minutes=minutes)


class TestScheduleBlockDuration:
    def test_default_duration_uses_suggested(self):
        block = ScheduleBlock(activity=make_activity(20))
        assert block.duration == 20

    def test_custom_duration_overrides(self):
        block = ScheduleBlock(activity=make_activity(20), actual_minutes=30)
        assert block.duration == 30

    def test_set_duration(self):
        block = ScheduleBlock(activity=make_activity(20))
        block.set_duration(45)
        assert block.duration == 45

    def test_set_duration_zero_raises(self):
        block = ScheduleBlock(activity=make_activity(20))
        with pytest.raises(ValueError):
            block.set_duration(0)

    def test_set_duration_negative_raises(self):
        block = ScheduleBlock(activity=make_activity(20))
        with pytest.raises(ValueError):
            block.set_duration(-10)

    def test_reset_duration(self):
        block = ScheduleBlock(activity=make_activity(20), actual_minutes=99)
        block.reset_duration()
        assert block.duration == 20
        assert block.actual_minutes is None


class TestScheduleBlockActivity:
    def test_activity_accessible(self):
        act = make_activity(15)
        block = ScheduleBlock(activity=act)
        assert block.activity is act
        assert block.activity.title == "Circle Time"
