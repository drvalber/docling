"""End-to-end pipeline: file -> extraction -> spec -> HTML."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path

from article_infographic.extract import extract_article
from article_infographic.models import ArticleExtraction, InfographicSpec
from article_infographic.render import write_html
from article_infographic.synthesis import get_synthesizer

_log = logging.getLogger(__name__)


@dataclass
class BuildResult:
    html_path: Path
    spec_path: Path
    extraction_path: Path | None
    spec: InfographicSpec
    extraction: ArticleExtraction


def build_infographic(
    source: Path,
    output_dir: Path,
    backend: str = "heuristic",
    model: str | None = None,
    host: str | None = None,
    language: str = "pt",
    keep_extraction: bool = True,
    converter=None,
) -> BuildResult:
    output_dir.mkdir(parents=True, exist_ok=True)
    stem = source.stem
    _log.info("Extracting %s with Docling", source)
    extraction = extract_article(source, converter=converter)
    _log.info(
        "Extracted %d sections, %d tables, %d figures, %d statistics",
        len(extraction.sections),
        len(extraction.tables),
        len(extraction.figures),
        len(extraction.key_numbers),
    )
    synthesizer = get_synthesizer(backend, model=model, host=host)
    _log.info("Synthesizing with backend %s", synthesizer.name)
    spec = synthesizer.synthesize(extraction, language)

    html_path = write_html(spec, output_dir / f"{stem}.infographic.html")
    spec_path = output_dir / f"{stem}.infographic.json"
    spec_path.write_text(spec.model_dump_json(indent=2), encoding="utf-8")
    extraction_path = None
    if keep_extraction:
        extraction_path = output_dir / f"{stem}.extraction.json"
        extraction_path.write_text(
            extraction.model_dump_json(indent=2), encoding="utf-8"
        )
    return BuildResult(html_path, spec_path, extraction_path, spec, extraction)


def render_from_spec(spec_path: Path, output: Path) -> Path:
    spec = InfographicSpec.model_validate(
        json.loads(spec_path.read_text(encoding="utf-8"))
    )
    return write_html(spec, output)
