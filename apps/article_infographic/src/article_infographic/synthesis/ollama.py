"""Synthesizer backed by a local Ollama server (structured JSON output).

Uses Ollama's native ``/api/chat`` endpoint with the ``format`` parameter set to
the draft's JSON schema, so any model that Ollama can constrain (qwen, llama,
gemma, mistral, ...) returns a document that validates against
``LLMInfographicDraft``. Falls back to the heuristic synthesizer on failure and
records the reason in ``InfographicSpec.warnings``.
"""

from __future__ import annotations

import json
import logging
import os

import requests
from pydantic import ValidationError

from article_infographic.models import (
    ArticleExtraction,
    InfographicSpec,
    LLMInfographicDraft,
)
from article_infographic.synthesis.common import merge_draft, system_prompt, user_prompt
from article_infographic.synthesis.heuristic import HeuristicSynthesizer

_log = logging.getLogger(__name__)

DEFAULT_MODEL = "qwen3:4b"
DEFAULT_HOST = "http://localhost:11434"


class OllamaSynthesizer:
    name = "ollama"

    def __init__(
        self,
        model: str | None = None,
        host: str | None = None,
        timeout: float = 900.0,
        num_ctx: int = 32768,
        strict: bool = False,
    ) -> None:
        self.model = model or os.environ.get("OLLAMA_MODEL", DEFAULT_MODEL)
        self.host = (host or os.environ.get("OLLAMA_HOST", DEFAULT_HOST)).rstrip("/")
        if not self.host.startswith("http"):
            self.host = f"http://{self.host}"
        self.timeout = timeout
        self.num_ctx = num_ctx
        self.strict = strict  # raise instead of falling back to the heuristic

    def draft(
        self, extraction: ArticleExtraction, language: str
    ) -> LLMInfographicDraft:
        payload = {
            "model": self.model,
            "stream": False,
            "format": LLMInfographicDraft.model_json_schema(),
            "options": {"temperature": 0.2, "num_ctx": self.num_ctx},
            "messages": [
                {"role": "system", "content": system_prompt(language)},
                {"role": "user", "content": user_prompt(extraction, language)},
            ],
        }
        response = requests.post(
            f"{self.host}/api/chat", json=payload, timeout=self.timeout
        )
        response.raise_for_status()
        content = response.json()["message"]["content"]
        return LLMInfographicDraft.model_validate_json(content)

    def synthesize(
        self, extraction: ArticleExtraction, language: str = "pt"
    ) -> InfographicSpec:
        try:
            draft = self.draft(extraction, language)
        except (
            requests.RequestException,
            ValidationError,
            KeyError,
            json.JSONDecodeError,
        ) as exc:
            if self.strict:
                raise
            _log.warning(
                "Ollama synthesis failed (%s); using the heuristic synthesizer", exc
            )
            spec = HeuristicSynthesizer().synthesize(extraction, language)
            spec.warnings.append(
                f"ollama ({self.model}) failed: {exc}; heuristic content shown"
            )
            return spec
        spec = merge_draft(draft, extraction, language, backend=f"ollama:{self.model}")
        return spec
