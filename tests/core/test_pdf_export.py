"""Tests for PDF export — verify it produces a valid, non-empty PDF file."""
import os
import pytest
from datetime import time
from pathlib import Path

from PySide6.QtWidgets import QApplication

from lesson_planner.data.activity_library import ActivityLibrary
from lesson_planner.export.pdf_export import export_pdf
from lesson_planner.models.daily_schedule import DailySchedule


@pytest.fixture(scope="module")
def qapp():
    import sys
    app = QApplication.instance() or QApplication(sys.argv)
    return app


@pytest.fixture
def library():
    return ActivityLibrary()


@pytest.fixture
def full_schedule(library):
    s = DailySchedule(name="Monday Morning", start_time=time(8, 0))
    for act_id in [
        "morning_greeting", "story_time", "outdoor_gross_motor",
        "art_studio", "free_choice", "pattern_math",
    ]:
        s.add_activity(library.by_id(act_id))
    return s


class TestPdfExport:
    def test_creates_file(self, qapp, tmp_path, full_schedule):
        p = tmp_path / "schedule.pdf"
        export_pdf(full_schedule, p)
        assert p.exists()

    def test_file_is_not_empty(self, qapp, tmp_path, full_schedule):
        p = tmp_path / "schedule.pdf"
        export_pdf(full_schedule, p)
        assert p.stat().st_size > 1000  # real PDF is at least ~1 KB

    def test_file_starts_with_pdf_header(self, qapp, tmp_path, full_schedule):
        p = tmp_path / "schedule.pdf"
        export_pdf(full_schedule, p)
        header = p.read_bytes()[:5]
        assert header == b"%PDF-"

    def test_empty_schedule_exports(self, qapp, tmp_path, library):
        s = DailySchedule(name="Empty Day")
        p = tmp_path / "empty.pdf"
        export_pdf(s, p)
        assert p.exists()
        assert p.stat().st_size > 1000

    def test_single_activity_exports(self, qapp, tmp_path, library):
        s = DailySchedule(name="Short Day", start_time=time(9, 30))
        s.add_activity(library.by_id("morning_greeting"))
        p = tmp_path / "single.pdf"
        export_pdf(s, p)
        assert p.read_bytes()[:5] == b"%PDF-"

    def test_custom_duration_included(self, qapp, tmp_path, library):
        s = DailySchedule(name="Custom Day")
        block = s.add_activity(library.by_id("story_time"))
        block.set_duration(30)
        p = tmp_path / "custom.pdf"
        export_pdf(s, p)  # should not raise
        assert p.exists()

    def test_all_domains_export(self, qapp, tmp_path, library):
        s = DailySchedule(name="All Domains")
        for act in library.all:
            s.add_activity(act)
        p = tmp_path / "all_domains.pdf"
        export_pdf(s, p)
        assert p.stat().st_size > 5000  # 16 activities = larger file
