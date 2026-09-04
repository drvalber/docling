"""Pieces shared by every synthesizer: reference formatting, prompt text and
the merge of an LLM draft with code-derived content."""

from __future__ import annotations

import re

from article_infographic.models import (
    ArticleExtraction,
    ArticleMetadata,
    InfographicSpec,
    LLMInfographicDraft,
    SectionKind,
)
from article_infographic.table_charts import charts_from_tables

MAX_CHARS_PER_SECTION = {
    SectionKind.ABSTRACT: 4000,
    SectionKind.INTRODUCTION: 3500,
    SectionKind.METHODS: 6000,
    SectionKind.RESULTS: 9000,
    SectionKind.DISCUSSION: 6000,
    SectionKind.CONCLUSION: 3000,
    SectionKind.OTHER: 1500,
}
MAX_TABLE_ROWS = 14


def format_reference(meta: ArticleMetadata) -> str:
    """Vancouver-like reference line built from whatever metadata exists."""
    parts: list[str] = []
    if meta.authors:
        authors = meta.authors[:6]
        suffix = ", et al." if len(meta.authors) > 6 else "."
        parts.append(", ".join(authors) + suffix)
    if meta.title:
        parts.append(meta.title.rstrip(".") + ".")
    if meta.journal:
        parts.append(meta.journal.rstrip(".") + ".")
    if meta.year:
        parts.append(f"{meta.year}.")
    if meta.doi:
        parts.append(f"doi:{meta.doi}")
    return " ".join(parts)


def short_citation(meta: ArticleMetadata) -> str:
    if meta.authors:
        first = meta.authors[0].split()[-1]
        who = first if len(meta.authors) == 1 else f"{first} et al."
    else:
        who = (meta.title[:40] + "…") if len(meta.title) > 40 else meta.title
    return f"{who} ({meta.year})" if meta.year else who


def condensed_article(extraction: ArticleExtraction) -> str:
    """Plain-text digest of the extraction sized for an LLM prompt."""
    meta = extraction.metadata
    lines = [
        f"TITLE: {meta.title}",
        f"AUTHORS: {', '.join(meta.authors) or 'unknown'}",
        f"JOURNAL: {meta.journal or 'unknown'}  YEAR: {meta.year or 'unknown'}  DOI: {meta.doi or 'unknown'}",
        f"KEYWORDS: {', '.join(meta.keywords) or 'none'}",
        "",
    ]
    for section in extraction.sections:
        if section.kind is SectionKind.REFERENCES or not section.text.strip():
            continue
        budget = MAX_CHARS_PER_SECTION.get(section.kind, 1500)
        text = re.sub(r"\s+", " ", section.text)
        if len(text) > budget:
            text = text[:budget] + " […]"
        lines.append(
            f"## {section.heading or section.kind.value.upper()} [{section.kind.value}]"
        )
        lines.append(text)
        lines.append("")
    for table in extraction.tables:
        lines.append(f"## TABLE {table.index}: {table.caption}")
        lines.append(" | ".join(table.headers))
        for row in table.rows[:MAX_TABLE_ROWS]:
            lines.append(" | ".join(row))
        if len(table.rows) > MAX_TABLE_ROWS:
            lines.append(f"… ({len(table.rows) - MAX_TABLE_ROWS} more rows)")
        lines.append("")
    for figure in extraction.figures:
        if figure.caption:
            lines.append(f"FIGURE {figure.index}: {figure.caption}")
    return "\n".join(lines)


def system_prompt(language: str) -> str:
    lang_name = {"pt": "Brazilian Portuguese", "en": "English", "es": "Spanish"}.get(
        language, language
    )
    return (
        "You are a medical-scientific editor who turns research articles into one-page "
        "infographics for clinicians. Work only from the article text supplied by the user: "
        "never invent numbers, sample sizes, effect sizes or conclusions. When a number is "
        "missing, leave the field empty rather than guessing. Charts must use only values "
        "that appear verbatim in the article or its tables, with categories and series that "
        "share one scale; prefer results over descriptive statistics. Keep every field concise "
        f"enough for a poster. Write all free text in {lang_name}, keeping drug names, scales "
        "and statistical notation as in the original."
    )


def user_prompt(extraction: ArticleExtraction, language: str) -> str:
    return (
        "Produce the infographic content for the article below. Fill the JSON schema you were "
        "given. Tie each key finding to its statistic (p-value, CI, effect size) when the "
        "article reports one, describe the study design in PICO terms, and list the limitations "
        "the authors themselves acknowledge.\n\n"
        f"<article>\n{condensed_article(extraction)}\n</article>"
    )


def merge_draft(
    draft: LLMInfographicDraft,
    extraction: ArticleExtraction,
    language: str,
    backend: str,
) -> InfographicSpec:
    """Combine the model's interpretive content with code-derived facts."""
    meta = extraction.metadata
    charts = list(draft.charts[:3])
    if len(charts) < 3:
        # Table-derived charts fill the remaining slots (they are exact by construction).
        existing = {c.title.lower() for c in charts}
        for chart in charts_from_tables(extraction.tables, language, limit=4):
            if chart.title.lower() not in existing:
                charts.append(chart)
            if len(charts) >= 4:
                break
    return InfographicSpec(
        language=language,
        headline=draft.headline or meta.title,
        subtitle=draft.subtitle,
        one_sentence_summary=draft.one_sentence_summary,
        reference=format_reference(meta),
        citation_short=short_citation(meta),
        metadata=meta,
        stat_tiles=draft.stat_tiles[:5],
        study_design=draft.study_design,
        flow=draft.flow[:7],
        mechanism=draft.mechanism[:6],
        key_findings=draft.key_findings[:6],
        charts=charts,
        takeaways=draft.takeaways[:5],
        clinical_implications=draft.clinical_implications[:4],
        limitations=draft.limitations[:4],
        glossary=dict(list(draft.glossary.items())[:6]),
        keywords=draft.keywords[:8] or meta.keywords[:8],
        generated_by=backend,
    )
