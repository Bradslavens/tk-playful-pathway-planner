import pytest
import json
from pathlib import Path
from lesson_planner.data.activity_library import ActivityLibrary


class TestActivityLibraryLoad:
    def test_loads_all_seed_activities(self):
        lib = ActivityLibrary()
        assert len(lib.all) == 16

    def test_activities_are_activity_objects(self):
        from lesson_planner.models.activity import Activity
        lib = ActivityLibrary()
        for act in lib.all:
            assert isinstance(act, Activity)

    def test_known_activity_present(self):
        lib = ActivityLibrary()
        ids = [a.id for a in lib.all]
        assert "morning_greeting" in ids

    def test_all_returns_copy(self):
        lib = ActivityLibrary()
        first = lib.all
        first.clear()
        assert len(lib.all) == 16

    def test_loads_from_custom_path(self, tmp_path):
        data = [
            {"id": "custom_1", "title": "Custom Activity", "domain": "Arts",
             "suggested_minutes": 10, "energy_level": "low"}
        ]
        p = tmp_path / "custom.json"
        p.write_text(json.dumps(data), encoding="utf-8")
        lib = ActivityLibrary(seed_path=p)
        assert len(lib.all) == 1
        assert lib.all[0].id == "custom_1"


class TestActivityLibraryByDomain:
    def test_by_domain_returns_only_matching(self):
        lib = ActivityLibrary()
        results = lib.by_domain("Science")
        assert all(a.domain == "Science" for a in results)
        assert len(results) > 0

    def test_by_domain_unknown_returns_empty(self):
        lib = ActivityLibrary()
        assert lib.by_domain("Underwater Basket Weaving") == []

    def test_by_domain_social_emotional(self):
        lib = ActivityLibrary()
        results = lib.by_domain("Social-Emotional")
        assert len(results) >= 2


class TestActivityLibrarySearch:
    def test_search_by_title_keyword(self):
        lib = ActivityLibrary()
        results = lib.search("story")
        assert any("story" in a.title.lower() or "story" in a.description.lower() for a in results)

    def test_search_case_insensitive(self):
        lib = ActivityLibrary()
        lower = lib.search("morning")
        upper = lib.search("MORNING")
        assert len(lower) == len(upper)

    def test_search_empty_returns_all(self):
        lib = ActivityLibrary()
        assert len(lib.search("")) == 16

    def test_search_whitespace_returns_all(self):
        lib = ActivityLibrary()
        assert len(lib.search("   ")) == 16

    def test_search_no_match_returns_empty(self):
        lib = ActivityLibrary()
        assert lib.search("zzznomatch") == []


class TestActivityLibraryById:
    def test_by_id_found(self):
        lib = ActivityLibrary()
        act = lib.by_id("morning_greeting")
        assert act is not None
        assert act.id == "morning_greeting"

    def test_by_id_not_found_returns_none(self):
        lib = ActivityLibrary()
        assert lib.by_id("does_not_exist") is None


class TestActivityLibraryDomains:
    def test_domains_returns_list(self):
        lib = ActivityLibrary()
        domains = lib.domains
        assert isinstance(domains, list)
        assert len(domains) > 0

    def test_domains_no_duplicates(self):
        lib = ActivityLibrary()
        domains = lib.domains
        assert len(domains) == len(set(domains))

    def test_known_domains_present(self):
        lib = ActivityLibrary()
        domains = lib.domains
        assert "Science" in domains
        assert "Language" in domains
        assert "Social-Emotional" in domains
