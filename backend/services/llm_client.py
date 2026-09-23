"""Provider-agnostic LLM client. Nothing else in the codebase calls the Gemini SDK directly.

- generate(prompt, **kwargs) -> str
- embed(text) -> list[float]  (single text; batch via embed_many)
- 429/ResourceExhausted retried with exponential backoff, then LLMRateLimitExhausted
- GEMINI_TIER=free logs a warning (free tier may train on data — synthetic only)
- Prompts must live in backend/prompts/, never inline in business logic (use load_prompt).
"""
from __future__ import annotations
import logging
import os
import time
from pathlib import Path
import random

logger = logging.getLogger(__name__)

PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"


class LLMError(Exception):
    pass


class LLMRateLimitExhausted(LLMError):
    pass


class LLMClient:
    provider: str = "gemini"

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        embed_model: str | None = None,
        tier: str | None = None,
    ):
        from core.config import get_settings

        s = get_settings()
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", s.GEMINI_API_KEY)
        self.model = model or os.getenv("GEMINI_MODEL", s.GEMINI_MODEL)
        self.embed_model = embed_model or os.getenv("GEMINI_EMBED_MODEL", s.GEMINI_EMBED_MODEL)
        self.tier = (tier or os.getenv("GEMINI_TIER", s.GEMINI_TIER)).lower()
        if self.tier == "free":
            logger.warning(
                "GEMINI_TIER=free: use ONLY synthetic/test data. "
                "Switch to paid before processing real resumes."
            )
        self._client = None  # lazy google-genai client

    def _get_client(self):
        if self._client is None:
            if not self.api_key:
                raise LLMError("GEMINI_API_KEY not configured")
            from google import genai

            self._client = genai.Client(api_key=self.api_key)
        return self._client

    @staticmethod
    def _is_rate_limit(exc: Exception) -> bool:
        msg = f"{type(exc).__name__}: {exc}".lower()
        return (
            "429" in msg
            or "resource_exhausted" in msg
            or "rate limit" in msg
            or "quota" in msg
        )

    def _with_backoff(self, fn, *, max_retries: int = 5, base: float = 2.0):
        last: Exception | None = None
        for attempt in range(max_retries + 1):
            try:
                return fn()
            except Exception as e:  # noqa: BLE001
                if not self._is_rate_limit(e):
                    raise
                last = e
                if attempt == max_retries:
                    break
                sleep = base**attempt + random.uniform(0, 1)
                logger.warning("Gemini 429 (attempt %d/%d), sleeping %.1fs", attempt + 1, max_retries, sleep)
                time.sleep(sleep)
        raise LLMRateLimitExhausted(f"Gemini rate limit retries exhausted: {last}")

    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text. kwargs: system (str), json_mode (bool), max_tokens (int), temperature (float)."""
        client = self._get_client()
        system = kwargs.get("system", "")
        full = f"{system}\n\n{prompt}" if system else prompt
        config: dict = {}
        if kwargs.get("json_mode"):
            config["response_mime_type"] = "application/json"
        if "max_tokens" in kwargs:
            config["max_output_tokens"] = kwargs["max_tokens"]
        if "temperature" in kwargs:
            config["temperature"] = kwargs["temperature"]

        def call():
            resp = client.models.generate_content(model=self.model, contents=full, config=config or None)
            return (resp.text or "").strip()

        return self._with_backoff(call)

    def embed(self, text: str) -> list[float]:
        client = self._get_client()

        def call():
            resp = client.models.embed_content(model=self.embed_model, contents=text)
            # google-genai returns .embeddings[0].values
            emb = resp.embeddings[0]
            return list(emb.values)

        return self._with_backoff(call)

    def embed_many(self, texts: list[str]) -> list[list[float]]:
        return [self.embed(t) for t in texts]


def load_prompt(name: str, version: str = "v1", **vars) -> str:
    """Load backend/prompts/<version>/<name>.txt and format with vars. Never hardcode prompts inline."""
    path = PROMPTS_DIR / version / f"{name}.txt"
    if not path.exists():
        raise FileNotFoundError(f"Prompt template missing: {path}")
    tmpl = path.read_text(encoding="utf-8")
    return tmpl.format(**vars) if vars else tmpl
