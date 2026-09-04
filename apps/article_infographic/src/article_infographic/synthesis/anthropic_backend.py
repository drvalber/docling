"""Synthesizer backed by the Claude API (official ``anthropic`` SDK).

Requires ``pip install anthropic`` and credentials resolved by the SDK
(``ANTHROPIC_API_KEY`` or an ``ant auth login`` profile). The draft is obtained
with structured outputs (``client.messages.parse``), so the response is
validated against ``LLMInfographicDraft`` before any rendering happens.
"""

from __future__ import annotations

import logging
import os

from article_infographic.models import (
    ArticleExtraction,
    InfographicSpec,
    LLMInfographicDraft,
)
from article_infographic.synthesis.common import merge_draft, system_prompt, user_prompt
from article_infographic.synthesis.heuristic import HeuristicSynthesizer

_log = logging.getLogger(__name__)

DEFAULT_MODEL = "claude-opus-5"


class AnthropicSynthesizer:
    name = "anthropic"

    def __init__(self, model: str | None = None, strict: bool = False) -> None:
        self.model = model or os.environ.get("ANTHROPIC_MODEL", DEFAULT_MODEL)
        self.strict = strict

    def draft(
        self, extraction: ArticleExtraction, language: str
    ) -> LLMInfographicDraft:
        import anthropic

        client = anthropic.Anthropic()
        response = client.messages.parse(
            model=self.model,
            max_tokens=16000,
            thinking={"type": "adaptive"},
            system=system_prompt(language),
            messages=[{"role": "user", "content": user_prompt(extraction, language)}],
            output_format=LLMInfographicDraft,
        )
        if response.stop_reason == "refusal":
            details = response.stop_details.explanation if response.stop_details else ""
            raise RuntimeError(
                f"Claude declined the request: {details or 'no explanation'}"
            )
        if response.parsed_output is None:
            raise RuntimeError("Claude returned no structured output")
        return response.parsed_output

    def synthesize(
        self, extraction: ArticleExtraction, language: str = "pt"
    ) -> InfographicSpec:
        try:
            draft = self.draft(extraction, language)
        except Exception as exc:  # SDK errors, refusals, missing credentials
            if self.strict:
                raise
            _log.warning(
                "Anthropic synthesis failed (%s); using the heuristic synthesizer", exc
            )
            spec = HeuristicSynthesizer().synthesize(extraction, language)
            spec.warnings.append(
                f"anthropic ({self.model}) failed: {exc}; heuristic content shown"
            )
            return spec
        return merge_draft(
            draft, extraction, language, backend=f"anthropic:{self.model}"
        )
