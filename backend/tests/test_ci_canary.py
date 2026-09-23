"""TEMPORARY canary: proves CI fails on a broken test (Phase 0 Prompt 5 DoD).
Reverted immediately after CI goes red. Do NOT extend this file."""


def test_ci_canary_deliberately_broken():
    assert False, "canary: CI must fail on this commit"
