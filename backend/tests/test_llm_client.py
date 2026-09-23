"""Phase 0 Prompt 2 DoD: generate()+embed() hit the real Gemini API; 429 triggers backoff, not crash.

Run: GEMINI_API_KEY=... pytest backend/tests/test_llm_client.py -v
Live tests are skipped without a key. The backoff unit test always runs (simulated 429).
"""
import os
import pytest

from backend.services.llm_client import LLMClient, LLMRateLimitExhausted, load_prompt

NEEDS_KEY = not os.getenv("GEMINI_API_KEY")


def test_load_prompt_versions():
    p = load_prompt("structured_extraction", version="v1", resume_text="hello")
    assert "hello" in p


def test_backoff_retries_then_raises():
    c = LLMClient(api_key="dummy", tier="free")
    calls = {"n": 0}

    def flaky():
        calls["n"] += 1
        raise Exception("429 Resource exhausted")

    # speed up: monkeypatch sleep
    import backend.services.llm_client as m

    m.time.sleep = lambda s: None
    with pytest.raises(LLMRateLimitExhausted):
        c._with_backoff(flaky, max_retries=2, base=0.01)
    assert calls["n"] == 3


@pytest.mark.skipif(NEEDS_KEY, reason="needs GEMINI_API_KEY")
def test_live_generate_and_embed():
    c = LLMClient()
    out = c.generate("Reply with exactly: ok")
    assert isinstance(out, str) and len(out) > 0
    vec = c.embed("hello world")
    assert isinstance(vec, list) and len(vec) > 100
