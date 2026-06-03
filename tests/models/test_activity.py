import pytest
from lesson_planner.models.activity import Activity


def make_activity(**kwargs):
    defaults = dict(
        id="test_act",
        title="Test Activity",
        domain="Science",
        suggested_minutes=15,
    )
    defaults.update(kwargs)
    return Activity(**defaults)


class TestActivityCreation:
    def test_basic_creation(self):
        act = make_activity()
        assert act.id == "test_act"
        assert act.title == "Test Activity"
        assert act.domain == "Science"
        assert act.suggested_minutes == 15

    def test_defaults(self):
        act = make_activity()
        assert act.icon == ""
        assert act.description == ""
        assert act.materials == []
        assert act.energy_level == "medium"
        assert act.adaptations == []

    def test_full_creation(self):
        act = make_activity(
            icon="🔬",
            description="Fun with science",
            materials=["Beakers", "Water"],
            energy_level="high",
            adaptations=["Gloves available"],
        )
        assert act.icon == "🔬"
        assert act.materials == ["Beakers", "Water"]
        assert act.energy_level == "high"

    def test_frozen(self):
        act = make_activity()
        with pytest.raises((AttributeError, TypeError)):
            act.title = "Changed"


class TestActivityValidation:
    def test_empty_id_raises(self):
        with pytest.raises(ValueError, match="id"):
            make_activity(id="  ")

    def test_empty_title_raises(self):
        with pytest.raises(ValueError, match="title"):
            make_activity(title="")

    def test_zero_minutes_raises(self):
        with pytest.raises(ValueError, match="suggested_minutes"):
            make_activity(suggested_minutes=0)

    def test_negative_minutes_raises(self):
        with pytest.raises(ValueError, match="suggested_minutes"):
            make_activity(suggested_minutes=-5)

    def test_invalid_energy_level_raises(self):
        with pytest.raises(ValueError, match="energy_level"):
            make_activity(energy_level="turbo")

    def test_valid_energy_levels(self):
        for level in ("low", "medium", "high"):
            act = make_activity(energy_level=level)
            assert act.energy_level == level


class TestActivityEquality:
    def test_same_data_equal(self):
        a1 = make_activity()
        a2 = make_activity()
        assert a1 == a2

    def test_different_id_not_equal(self):
        a1 = make_activity(id="one")
        a2 = make_activity(id="two")
        assert a1 != a2
