import pytest
from datetime import time
from lesson_planner.models.activity import Activity
from lesson_planner.models.daily_schedule import DailySchedule


def make_activity(id="a1", title="Circle Time", minutes=10):
    return Activity(id=id, title=title, domain="Social-Emotional", suggested_minutes=minutes)


class TestDailyScheduleBasics:
    def test_default_name(self):
        s = DailySchedule()
        assert s.name == "Untitled Schedule"

    def test_custom_name(self):
        s = DailySchedule(name="Monday Plan")
        assert s.name == "Monday Plan"

    def test_starts_empty(self):
        s = DailySchedule()
        assert s.is_empty()
        assert s.total_minutes == 0

    def test_default_start_time(self):
        s = DailySchedule()
        assert s.start_time == time(8, 0)

    def test_custom_start_time(self):
        s = DailySchedule(start_time=time(9, 30))
        assert s.start_time == time(9, 30)


class TestAddActivity:
    def test_add_appends(self):
        s = DailySchedule()
        act = make_activity()
        block = s.add_activity(act)
        assert len(s.blocks) == 1
        assert s.blocks[0] is block
        assert block.activity is act

    def test_add_multiple_in_order(self):
        s = DailySchedule()
        a1 = make_activity("a1", "First")
        a2 = make_activity("a2", "Second")
        s.add_activity(a1)
        s.add_activity(a2)
        assert s.blocks[0].activity is a1
        assert s.blocks[1].activity is a2

    def test_add_at_index(self):
        s = DailySchedule()
        a1 = make_activity("a1", "First")
        a2 = make_activity("a2", "Second")
        a3 = make_activity("a3", "Inserted")
        s.add_activity(a1)
        s.add_activity(a2)
        s.add_activity(a3, at_index=1)
        assert s.blocks[0].activity is a1
        assert s.blocks[1].activity is a3
        assert s.blocks[2].activity is a2

    def test_add_at_index_zero(self):
        s = DailySchedule()
        a1 = make_activity("a1", "First")
        a2 = make_activity("a2", "Prepended")
        s.add_activity(a1)
        s.add_activity(a2, at_index=0)
        assert s.blocks[0].activity is a2


class TestRemoveBlock:
    def test_remove_only_block(self):
        s = DailySchedule()
        s.add_activity(make_activity())
        removed = s.remove_block(0)
        assert s.is_empty()
        assert removed.activity.id == "a1"

    def test_remove_middle_block(self):
        s = DailySchedule()
        a1 = make_activity("a1", "First")
        a2 = make_activity("a2", "Second")
        a3 = make_activity("a3", "Third")
        s.add_activity(a1)
        s.add_activity(a2)
        s.add_activity(a3)
        s.remove_block(1)
        assert len(s.blocks) == 2
        assert s.blocks[0].activity is a1
        assert s.blocks[1].activity is a3

    def test_remove_invalid_index_raises(self):
        s = DailySchedule()
        with pytest.raises(IndexError):
            s.remove_block(0)


class TestMoveBlock:
    def test_move_forward(self):
        s = DailySchedule()
        a1 = make_activity("a1", "First")
        a2 = make_activity("a2", "Second")
        a3 = make_activity("a3", "Third")
        s.add_activity(a1)
        s.add_activity(a2)
        s.add_activity(a3)
        s.move_block(0, 2)
        assert s.blocks[0].activity is a2
        assert s.blocks[1].activity is a3
        assert s.blocks[2].activity is a1

    def test_move_backward(self):
        s = DailySchedule()
        a1 = make_activity("a1", "First")
        a2 = make_activity("a2", "Second")
        a3 = make_activity("a3", "Third")
        s.add_activity(a1)
        s.add_activity(a2)
        s.add_activity(a3)
        s.move_block(2, 0)
        assert s.blocks[0].activity is a3
        assert s.blocks[1].activity is a1
        assert s.blocks[2].activity is a2

    def test_move_invalid_from_raises(self):
        s = DailySchedule()
        s.add_activity(make_activity())
        with pytest.raises(IndexError):
            s.move_block(5, 0)

    def test_move_invalid_to_raises(self):
        s = DailySchedule()
        s.add_activity(make_activity("a1", "First"))
        s.add_activity(make_activity("a2", "Second"))
        with pytest.raises(IndexError):
            s.move_block(0, 10)


class TestTotalMinutes:
    def test_total_minutes_empty(self):
        assert DailySchedule().total_minutes == 0

    def test_total_minutes_sums_durations(self):
        s = DailySchedule()
        s.add_activity(make_activity("a1", "A", minutes=10))
        s.add_activity(make_activity("a2", "B", minutes=20))
        s.add_activity(make_activity("a3", "C", minutes=15))
        assert s.total_minutes == 45

    def test_total_uses_actual_minutes_when_set(self):
        s = DailySchedule()
        block = s.add_activity(make_activity("a1", "A", minutes=10))
        block.set_duration(25)
        assert s.total_minutes == 25


class TestBlockStartTime:
    def test_first_block_starts_at_schedule_start(self):
        s = DailySchedule(start_time=time(8, 0))
        s.add_activity(make_activity("a1", "A", minutes=10))
        assert s.block_start_time(0) == time(8, 0)

    def test_second_block_offset(self):
        s = DailySchedule(start_time=time(8, 0))
        s.add_activity(make_activity("a1", "A", minutes=10))
        s.add_activity(make_activity("a2", "B", minutes=20))
        assert s.block_start_time(1) == time(8, 10)

    def test_third_block_offset(self):
        s = DailySchedule(start_time=time(9, 0))
        s.add_activity(make_activity("a1", "A", minutes=15))
        s.add_activity(make_activity("a2", "B", minutes=20))
        s.add_activity(make_activity("a3", "C", minutes=10))
        assert s.block_start_time(2) == time(9, 35)

    def test_invalid_index_raises(self):
        s = DailySchedule()
        with pytest.raises(IndexError):
            s.block_start_time(0)


class TestClear:
    def test_clear_empties_schedule(self):
        s = DailySchedule()
        s.add_activity(make_activity("a1", "A"))
        s.add_activity(make_activity("a2", "B"))
        s.clear()
        assert s.is_empty()
