from __future__ import annotations

from typing import Protocol

from article_infographic.models import ArticleExtraction, InfographicSpec

BACKENDS = ("heuristic", "ollama", "anthropic")


class Synthesizer(Protocol):
    name: str

    def synthesize(
        self, extraction: ArticleExtraction, language: str
    ) -> InfographicSpec: ...


def get_synthesizer(
    backend: str, model: str | None = None, host: str | None = None
) -> Synthesizer:
    """Factory used by the CLI and the web app."""
    if backend == "heuristic":
        from article_infographic.synthesis.heuristic import HeuristicSynthesizer

        return HeuristicSynthesizer()
    if backend == "ollama":
        from article_infographic.synthesis.ollama import OllamaSynthesizer

        return OllamaSynthesizer(model=model, host=host)
    if backend == "anthropic":
        from article_infographic.synthesis.anthropic_backend import AnthropicSynthesizer

        return AnthropicSynthesizer(model=model)
    raise ValueError(f"Unknown backend {backend!r}; choose one of {BACKENDS}")
