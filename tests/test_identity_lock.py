"""Unit tests for the identity-lock merge in commit_node.py.

`merge_formula_ids` protects against silent formula loss during graduation:
newly registered IDs take positional precedence, existing IDs keep their
order and are appended only when they don't already appear. This invariant
is one line of code but underpins every Platinum graduation, so it gets
direct coverage.
"""
from scripts.maintenance.commit_node import merge_formula_ids


def test_new_only_existing_empty():
    assert merge_formula_ids(["a", "b"], []) == ["a", "b"]


def test_new_empty_existing_kept():
    assert merge_formula_ids([], ["x", "y"]) == ["x", "y"]


def test_both_empty():
    assert merge_formula_ids([], []) == []


def test_disjoint_new_takes_lead():
    # New IDs are prepended; existing IDs follow in their original order.
    assert merge_formula_ids(["a"], ["b", "c"]) == ["a", "b", "c"]


def test_overlap_deduplicates_keeping_new_position():
    # "b" appears in both. It must survive only once, at its position in new.
    assert merge_formula_ids(["a", "b"], ["b", "c"]) == ["a", "b", "c"]


def test_full_overlap_collapses_to_new():
    # Every existing entry is in new — result is just new, no duplicates.
    assert merge_formula_ids(["a", "b"], ["a", "b"]) == ["a", "b"]


def test_existing_order_preserved():
    # Existing list is appended in its original (non-alphabetic) order.
    assert merge_formula_ids(["x"], ["c", "a", "b"]) == ["x", "c", "a", "b"]


def test_non_list_existing_treated_as_empty():
    # Defends against shard entries where formula_ids is missing or malformed.
    assert merge_formula_ids(["a"], None) == ["a"]
    assert merge_formula_ids(["a"], "not-a-list") == ["a"]
    assert merge_formula_ids(["a"], {"b": 1}) == ["a"]


def test_inputs_not_mutated():
    new = ["a", "b"]
    existing = ["b", "c"]
    merge_formula_ids(new, existing)
    assert new == ["a", "b"]
    assert existing == ["b", "c"]


def test_result_is_a_fresh_list():
    # Returned list must not alias either input — mutating it must not bleed back.
    new = ["a"]
    existing = ["b"]
    result = merge_formula_ids(new, existing)
    result.append("c")
    assert new == ["a"]
    assert existing == ["b"]


def test_duplicates_within_new_are_preserved_verbatim():
    # The helper dedups across the new/existing boundary, not within new itself.
    # Production callers (register_identities) never emit duplicates in new,
    # but this documents the contract: new is pass-through.
    assert merge_formula_ids(["a", "a"], ["b"]) == ["a", "a", "b"]
