Prompts are versioned templates — never hardcode prompt strings in business logic.
Use services.llm_client.load_prompt(name, version="v1", **vars).

backend/prompts/
  v1/
    structured_extraction.txt   (Phase 1 — resume JSON extraction, extract-only)
    ats_explanation.txt         (Phase 1 — plain-language per-category explanation)
    factcheck.txt               (Phase 3 — post-generation fabrication diff)
    rewrite_bullet.txt          (Phase 3 — STAR rewrite, no invented metrics)
  README.md (this file)
