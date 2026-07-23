"""Unit tests for the CTA self-heal logic in sync_backlog.py.

Two seams worth locking down:

- scan_disk_standards(): the authoritative reader that maps shard slugs to
  their on-disk standard. The "single source of truth" claim from CLAUDE.md
  rests on this function.
- self_heal_backlog(disk_state): reconciles expansion_backlog.json against
  the disk truth. Regressions here are exactly the kind that produce the
  dashboard drift documented in the project evaluation.
"""
import json
import time

import pytest

from scripts.maintenance.sync_backlog import (
    dedupe_backlog,
    scan_disk_standards,
    self_heal_backlog,
)


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------

def write_shard(workspace, filename, contents):
    (workspace / "app" / "config" / "content" / filename).write_text(json.dumps(contents))


def write_backlog(workspace, entries):
    (workspace / "subfiles" / "expansion_backlog.json").write_text(json.dumps(entries))


def read_backlog(workspace):
    return json.loads((workspace / "subfiles" / "expansion_backlog.json").read_text())


def node(standard="platinum", title="X"):
    return {"title": title, "standard": standard, "content": "<p>x</p>"}


# -----------------------------------------------------------------------------
# scan_disk_standards
# -----------------------------------------------------------------------------

def test_scan_extracts_subtopic_metadata(backlog_workspace):
    write_shard(backlog_workspace, "test_shard.json", {
        "node-a": node("platinum", title="Node A"),
        "node-b": node("legacy", title="Node B"),
    })
    result = scan_disk_standards()
    assert result["node-a"]["standard"] == "platinum"
    assert result["node-a"]["shard"] == "test_shard.json"
    assert result["node-a"]["title"] == "Node A"
    assert result["node-b"]["standard"] == "legacy"


def test_scan_defaults_missing_standard_to_legacy(backlog_workspace):
    write_shard(backlog_workspace, "test_shard.json", {
        "no-standard": {"title": "X", "content": "<p>x</p>"},
    })
    result = scan_disk_standards()
    assert result["no-standard"]["standard"] == "legacy"


def test_scan_excludes_index_files(backlog_workspace):
    # Files in the exclusion list must not contribute slugs to disk_state.
    write_shard(backlog_workspace, "categories.json", {"category-a": node("platinum")})
    write_shard(backlog_workspace, "formulas.json", {"formula-1": {"equation": "x"}})
    write_shard(backlog_workspace, "search_index.json", {"search-a": "shard.json"})
    write_shard(backlog_workspace, "entities.json", {"einstein": {"name": "E"}})
    write_shard(backlog_workspace, "constants.json", {"c": {"value": 1}})
    write_shard(backlog_workspace, "real_shard.json", {"real-node": node("platinum")})
    result = scan_disk_standards()
    assert set(result.keys()) == {"real-node"}


def test_scan_tolerates_malformed_shard(backlog_workspace):
    # An unreadable JSON shard prints a warning but doesn't crash the scan.
    write_shard(backlog_workspace, "good.json", {"node-a": node("platinum")})
    (backlog_workspace / "app" / "config" / "content" / "bad.json").write_text("{ not valid json")
    result = scan_disk_standards()
    assert "node-a" in result


def test_scan_missing_content_dir_exits(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)  # no app/config/content/ at all
    with pytest.raises(SystemExit):
        scan_disk_standards()


# -----------------------------------------------------------------------------
# self_heal_backlog
# -----------------------------------------------------------------------------

def test_heal_promotes_pending_to_completed_when_disk_is_platinum(backlog_workspace):
    disk = {"node-a": {"standard": "platinum", "shard": "s.json", "title": "X"}}
    write_backlog(backlog_workspace, [{"suggested_slug": "node-a", "status": "pending"}])
    healed, total = self_heal_backlog(disk)
    assert (healed, total) == (1, 1)
    assert read_backlog(backlog_workspace)[0]["status"] == "completed"


def test_heal_demotes_completed_to_pending_when_disk_is_legacy(backlog_workspace):
    disk = {"node-a": {"standard": "legacy", "shard": "s.json", "title": "X"}}
    write_backlog(backlog_workspace, [{"suggested_slug": "node-a", "status": "completed"}])
    healed, total = self_heal_backlog(disk)
    assert (healed, total) == (1, 1)
    assert read_backlog(backlog_workspace)[0]["status"] == "pending"


def test_heal_no_change_when_already_aligned(backlog_workspace):
    disk = {"node-a": {"standard": "platinum", "shard": "s.json", "title": "X"}}
    write_backlog(backlog_workspace, [{"suggested_slug": "node-a", "status": "completed"}])
    healed, total = self_heal_backlog(disk)
    assert (healed, total) == (0, 1)


def test_heal_skips_slugs_not_on_disk(backlog_workspace):
    # No truth to align against — entry is left at its existing value.
    disk = {}
    write_backlog(backlog_workspace, [{"suggested_slug": "phantom", "status": "pending"}])
    healed, total = self_heal_backlog(disk)
    assert (healed, total) == (0, 1)
    assert read_backlog(backlog_workspace)[0]["status"] == "pending"


def test_heal_handles_mixed_entries(backlog_workspace):
    disk = {
        "a": {"standard": "platinum", "shard": "s.json", "title": "A"},
        "b": {"standard": "legacy", "shard": "s.json", "title": "B"},
        "c": {"standard": "platinum", "shard": "s.json", "title": "C"},
    }
    write_backlog(backlog_workspace, [
        {"suggested_slug": "a", "status": "pending"},     # wrong → flip
        {"suggested_slug": "b", "status": "pending"},     # right → keep
        {"suggested_slug": "c", "status": "completed"},   # right → keep
        {"suggested_slug": "d", "status": "pending"},     # not on disk → keep
    ])
    healed, total = self_heal_backlog(disk)
    assert (healed, total) == (1, 4)
    final = read_backlog(backlog_workspace)
    assert [e["status"] for e in final] == ["completed", "pending", "completed", "pending"]


def test_heal_missing_backlog_returns_zero_zero(backlog_workspace):
    disk = {"node-a": {"standard": "platinum", "shard": "s.json", "title": "X"}}
    healed, total = self_heal_backlog(disk)
    assert (healed, total) == (0, 0)


def test_heal_does_not_rewrite_when_no_changes_needed(backlog_workspace):
    # mtime invariant: if nothing heals, the file is not touched.
    disk = {"node-a": {"standard": "platinum", "shard": "s.json", "title": "X"}}
    write_backlog(backlog_workspace, [{"suggested_slug": "node-a", "status": "completed"}])
    backlog_path = backlog_workspace / "subfiles" / "expansion_backlog.json"
    before = backlog_path.stat().st_mtime_ns
    time.sleep(0.01)  # leave room for mtime to tick if a write occurred
    self_heal_backlog(disk)
    assert backlog_path.stat().st_mtime_ns == before


def test_heal_entry_without_suggested_slug_is_untouched(backlog_workspace):
    # entry.get("suggested_slug") returns None → not in disk_state → no flip.
    disk = {"node-a": {"standard": "platinum", "shard": "s.json", "title": "X"}}
    write_backlog(backlog_workspace, [{"title": "orphan entry", "status": "pending"}])
    healed, total = self_heal_backlog(disk)
    assert (healed, total) == (0, 1)


# -----------------------------------------------------------------------------
# dedupe_backlog (pure function)
# -----------------------------------------------------------------------------

def test_dedupe_empty_list_returns_empty():
    assert dedupe_backlog([]) == []


def test_dedupe_pass_through_when_all_unique():
    entries = [
        {"suggested_slug": "a", "status": "pending"},
        {"suggested_slug": "b", "status": "completed"},
    ]
    result = dedupe_backlog(entries)
    assert result == entries
    assert result is not entries  # fresh list


def test_dedupe_collapses_same_status_duplicates():
    entries = [
        {"suggested_slug": "a", "status": "pending", "term": "First"},
        {"suggested_slug": "a", "status": "pending", "term": "Second"},
    ]
    result = dedupe_backlog(entries)
    assert len(result) == 1
    # First-appearance metadata is preserved.
    assert result[0]["term"] == "First"


def test_dedupe_promotes_status_when_any_duplicate_is_completed():
    entries = [
        {"suggested_slug": "a", "status": "pending", "term": "Primary"},
        {"suggested_slug": "a", "status": "completed", "term": "Variant"},
    ]
    result = dedupe_backlog(entries)
    assert len(result) == 1
    assert result[0]["status"] == "completed"
    # Survivor keeps the first entry's other fields; only status is promoted.
    assert result[0]["term"] == "Primary"


def test_dedupe_promotes_status_regardless_of_order():
    # Same as above but completed appears first — survivor stays completed.
    entries = [
        {"suggested_slug": "a", "status": "completed", "term": "Primary"},
        {"suggested_slug": "a", "status": "pending", "term": "Variant"},
    ]
    result = dedupe_backlog(entries)
    assert result[0]["status"] == "completed"
    assert result[0]["term"] == "Primary"


def test_dedupe_preserves_first_appearance_order():
    entries = [
        {"suggested_slug": "z", "status": "pending"},
        {"suggested_slug": "a", "status": "pending"},
        {"suggested_slug": "m", "status": "pending"},
    ]
    result = dedupe_backlog(entries)
    assert [e["suggested_slug"] for e in result] == ["z", "a", "m"]


def test_dedupe_preserves_entries_without_suggested_slug():
    entries = [
        {"suggested_slug": "a", "status": "pending"},
        {"title": "orphan with no slug", "status": "pending"},
        {"suggested_slug": "a", "status": "pending"},  # dup of first
        {"suggested_slug": "b", "status": "pending"},
    ]
    result = dedupe_backlog(entries)
    assert len(result) == 3  # a, orphan, b
    slugs_or_orphan = [e.get("suggested_slug", "<orphan>") for e in result]
    assert slugs_or_orphan == ["a", "<orphan>", "b"]


def test_dedupe_does_not_mutate_input():
    entries = [
        {"suggested_slug": "a", "status": "pending"},
        {"suggested_slug": "a", "status": "completed"},
    ]
    snapshot = [dict(e) for e in entries]
    dedupe_backlog(entries)
    assert entries == snapshot
    # And the entries themselves weren't mutated either.
    assert entries[0] == {"suggested_slug": "a", "status": "pending"}


def test_dedupe_idempotent():
    entries = [
        {"suggested_slug": "a", "status": "pending"},
        {"suggested_slug": "a", "status": "completed"},
        {"suggested_slug": "b", "status": "pending"},
    ]
    once = dedupe_backlog(entries)
    twice = dedupe_backlog(once)
    assert once == twice


def test_dedupe_collapses_three_way_duplicates():
    entries = [
        {"suggested_slug": "a", "status": "pending"},
        {"suggested_slug": "a", "status": "pending"},
        {"suggested_slug": "a", "status": "completed"},
    ]
    result = dedupe_backlog(entries)
    assert len(result) == 1
    assert result[0]["status"] == "completed"


# -----------------------------------------------------------------------------
# self_heal_backlog integration with dedupe
# -----------------------------------------------------------------------------

def test_heal_dedupes_and_rewrites_file_when_duplicates_present(backlog_workspace):
    disk = {}  # no heal flips needed; only dedupe causes the rewrite
    write_backlog(backlog_workspace, [
        {"suggested_slug": "a", "status": "pending"},
        {"suggested_slug": "a", "status": "pending"},
        {"suggested_slug": "b", "status": "pending"},
    ])
    healed, total = self_heal_backlog(disk)
    assert healed == 0
    assert total == 2  # post-dedupe count
    on_disk = read_backlog(backlog_workspace)
    assert len(on_disk) == 2


def test_heal_dedupe_promotes_pending_to_completed_via_duplicate(backlog_workspace):
    # The two-conflicting-status case from the real backlog: the dedupe pass
    # promotes the survivor to completed before the heal loop runs.
    disk = {}
    write_backlog(backlog_workspace, [
        {"suggested_slug": "a", "status": "pending", "term": "Primary"},
        {"suggested_slug": "a", "status": "completed", "term": "Variant"},
    ])
    self_heal_backlog(disk)
    on_disk = read_backlog(backlog_workspace)
    assert len(on_disk) == 1
    assert on_disk[0]["status"] == "completed"
    assert on_disk[0]["term"] == "Primary"


def test_heal_keys_off_suggested_slug_not_slug(backlog_workspace):
    # The schema uses "suggested_slug"; a refactor that silently switches to
    # "slug" would break self-healing. Verify a stray "slug" alias is ignored.
    disk = {"target-node": {"standard": "platinum", "shard": "s.json", "title": "X"}}
    write_backlog(backlog_workspace, [
        {"slug": "target-node", "suggested_slug": "other-node", "status": "pending"},
    ])
    healed, total = self_heal_backlog(disk)
    # "other-node" isn't on disk → no flip. If the function read "slug" instead,
    # it would match "target-node" and flip to completed.
    assert (healed, total) == (0, 1)
    assert read_backlog(backlog_workspace)[0]["status"] == "pending"
