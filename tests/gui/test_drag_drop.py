"""Drag-and-drop behaviour for the timeline.

These tests exercise the *receiving* side of drag-and-drop — the part that lives
in our code — by dispatching real QDropEvent / QDragEnterEvent objects through
the actual widget handlers. The OS-level pointer grab inside QDrag.exec() is
Qt's responsibility and isn't simulated here.

The headline test is `test_drop_multiple_activities_in_sequence`, which locks in
the bug report: "after the first activity is dropped, I can't add another one."
"""
import pytest
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QPointF, QPoint, QEvent
from PySide6.QtGui import QDropEvent, QDragEnterEvent, QMouseEvent, QDrag

from lesson_planner.data.activity_library import ActivityLibrary
from lesson_planner.models.daily_schedule import DailySchedule
from lesson_planner.gui.timeline_panel import TimelinePanel, DropZone
from lesson_planner.gui.widgets.timeline_card import TimelineCard
from lesson_planner.gui.widgets.library_card import (
    LibraryCard,
    make_activity_mime,
    activity_id_from_mime,
    MIME_TYPE,
)


# ── Fixtures ──────────────────────────────────────────────────────────────────
@pytest.fixture(scope="module")
def qapp():
    import sys
    return QApplication.instance() or QApplication(sys.argv)


@pytest.fixture
def library():
    return ActivityLibrary()


@pytest.fixture
def activity_ids(library):
    return [a.id for a in library.all]


@pytest.fixture
def panel(qapp, library):
    return TimelinePanel(DailySchedule(), library)


# ── Helpers ───────────────────────────────────────────────────────────────────
def _settle(qapp):
    """Let deferred (QTimer.singleShot) refreshes run."""
    for _ in range(5):
        qapp.processEvents()


def _drop_library_activity(widget, activity_id, *, at_bottom=False):
    """Dispatch a library drag-enter + drop carrying `activity_id` onto `widget`."""
    mime = make_activity_mime(activity_id)
    y = widget.height() * 0.75 if at_bottom else widget.height() * 0.25
    pos = QPointF(widget.width() / 2, y)

    enter = QDragEnterEvent(
        pos.toPoint(), Qt.CopyAction, mime, Qt.LeftButton, Qt.NoModifier
    )
    widget.dragEnterEvent(enter)
    assert enter.isAccepted(), "drop target rejected the library drag"

    drop = QDropEvent(pos, Qt.CopyAction, mime, Qt.LeftButton, Qt.NoModifier)
    widget.dropEvent(drop)
    return drop


def _drop_targets(panel):
    return panel._content.findChildren(DropZone)


def _cards(panel):
    return panel._content.findChildren(TimelineCard)


def _placeholder_zone(panel):
    return next(z for z in _drop_targets(panel) if z._placeholder)


def _tail_zone(panel):
    """The big expanding drop zone that fills the area below the last card."""
    return next(z for z in _drop_targets(panel) if z._expand)


# ── Mime contract ───────────────────────────────────────────────────────────--
def test_mime_round_trips_activity_id(qapp):
    mime = make_activity_mime("story_time")
    assert mime.hasFormat(MIME_TYPE)
    assert activity_id_from_mime(mime) == "story_time"


def test_activity_id_from_unrelated_mime_is_none(qapp):
    from PySide6.QtCore import QMimeData
    plain = QMimeData()
    plain.setText("hello")
    assert activity_id_from_mime(plain) is None


# ── Single drop ────────────────────────────────────────────────────────────--
def test_empty_schedule_shows_a_drop_target(panel):
    # The empty state must itself be a drop target (not an inert label),
    # otherwise the very first activity has nowhere to land.
    assert _placeholder_zone(panel) is not None


def test_drop_single_activity_onto_empty_schedule(qapp, panel, activity_ids):
    _drop_library_activity(_placeholder_zone(panel), activity_ids[0])
    _settle(qapp)

    assert len(panel._schedule.blocks) == 1
    assert panel._schedule.blocks[0].activity.id == activity_ids[0]
    assert len(_cards(panel)) == 1


# ── Multiple drops (the regression that was reported) ─────────────────────────
def test_drop_multiple_activities_in_sequence(qapp, panel, activity_ids):
    ids = activity_ids[:3]

    # 1st: onto the empty placeholder
    _drop_library_activity(_placeholder_zone(panel), ids[0])
    _settle(qapp)
    assert len(panel._schedule.blocks) == 1

    # 2nd: onto the trailing thin drop zone (append to end)
    trailing = [z for z in _drop_targets(panel) if not z._placeholder][-1]
    _drop_library_activity(trailing, ids[1])
    _settle(qapp)
    assert len(panel._schedule.blocks) == 2

    # 3rd: directly onto an existing timeline card
    _drop_library_activity(_cards(panel)[0], ids[2])
    _settle(qapp)

    blocks = panel._schedule.blocks
    assert len(blocks) == 3, "could not add a third activity"
    assert len(_cards(panel)) == 3
    # Every dropped activity is present.
    assert {b.activity.id for b in blocks} == set(ids)


def test_empty_space_below_cards_is_a_drop_target(qapp, panel, activity_ids):
    # Regression: once the first card appears, the rest of the timeline must
    # still accept drops (append), instead of being dead space that bounces
    # every drop after the first.
    _drop_library_activity(_placeholder_zone(panel), activity_ids[0])
    _settle(qapp)

    tail = _tail_zone(panel)  # raises if no expanding catch-all exists
    _drop_library_activity(tail, activity_ids[1])
    _settle(qapp)

    ids = [b.activity.id for b in panel._schedule.blocks]
    assert ids == [activity_ids[0], activity_ids[1]]


def test_drop_many_activities_does_not_drift(qapp, panel, activity_ids):
    # Stress: drop five activities one after another.
    for i, act_id in enumerate(activity_ids[:5]):
        target = _placeholder_zone(panel) if i == 0 else _cards(panel)[-1]
        _drop_library_activity(target, act_id, at_bottom=True)
        _settle(qapp)
        assert len(panel._schedule.blocks) == i + 1, f"drop #{i + 1} did not register"

    assert len(_cards(panel)) == 5


# ── Drag *initiation* from a library card ─────────────────────────────────────
def _press(card, x=5, y=5):
    p = QPointF(x, y)
    card.mousePressEvent(
        QMouseEvent(QEvent.MouseButtonPress, p, p, Qt.LeftButton, Qt.LeftButton, Qt.NoModifier)
    )


def _move(card, x=80, y=80):
    p = QPointF(x, y)
    card.mouseMoveEvent(
        QMouseEvent(QEvent.MouseMove, p, p, Qt.NoButton, Qt.LeftButton, Qt.NoModifier)
    )


@pytest.fixture
def captured_drags(monkeypatch):
    """Stub QDrag.exec (which blocks on a real pointer grab) and record each drag."""
    drags = []

    def fake_exec(self, *args, **kwargs):
        drags.append(activity_id_from_mime(self.mimeData()))
        return Qt.CopyAction

    monkeypatch.setattr(QDrag, "exec", fake_exec)
    return drags


def test_library_card_starts_a_drag_with_its_activity(qapp, library, captured_drags):
    act = library.all[0]
    card = LibraryCard(act)
    _press(card)
    _move(card)
    assert captured_drags == [act.id]


def test_tiny_movement_does_not_start_a_drag(qapp, library, captured_drags):
    card = LibraryCard(library.all[0])
    _press(card, 10, 10)
    _move(card, 11, 11)  # within the drag threshold → just a click, not a drag
    assert captured_drags == []


def test_library_card_can_start_multiple_drags(qapp, library, captured_drags):
    """Regression: a card (and the library) must be draggable more than once."""
    cards = [LibraryCard(a) for a in library.all[:3]]
    for card in cards:
        _press(card)
        _move(card)

    # Each card initiated its own drag — not just the first one.
    assert captured_drags == [c.activity.id for c in cards]


# ── Insert position when dropping onto a card ─────────────────────────────────
def test_drop_on_card_top_inserts_before(qapp, panel, activity_ids):
    a, b = activity_ids[0], activity_ids[1]
    _drop_library_activity(_placeholder_zone(panel), a)
    _settle(qapp)

    _drop_library_activity(_cards(panel)[0], b, at_bottom=False)  # top half
    _settle(qapp)

    ids = [blk.activity.id for blk in panel._schedule.blocks]
    assert ids == [b, a]


def test_drop_on_card_bottom_inserts_after(qapp, panel, activity_ids):
    a, b = activity_ids[0], activity_ids[1]
    _drop_library_activity(_placeholder_zone(panel), a)
    _settle(qapp)

    _drop_library_activity(_cards(panel)[0], b, at_bottom=True)  # bottom half
    _settle(qapp)

    ids = [blk.activity.id for blk in panel._schedule.blocks]
    assert ids == [a, b]
