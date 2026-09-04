"""Pydantic models shared across extraction, synthesis and rendering.

Two contracts live here:

* ``ArticleExtraction`` is what the Docling-based extractor produces from a PDF.
* ``InfographicSpec`` is what a synthesizer (heuristic or LLM) produces and what
  the renderer consumes. It is also the file format for ``--spec`` round trips,
  so a spec can be hand-edited and re-rendered.
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Extraction side
# ---------------------------------------------------------------------------


class SectionKind(str, Enum):
    """Canonical role of a section inside a scientific article."""

    ABSTRACT = "abstract"
    INTRODUCTION = "introduction"
    METHODS = "methods"
    RESULTS = "results"
    DISCUSSION = "discussion"
    CONCLUSION = "conclusion"
    REFERENCES = "references"
    OTHER = "other"


class ArticleMetadata(BaseModel):
    title: str = ""
    authors: list[str] = Field(default_factory=list)
    journal: str = ""
    year: str = ""
    doi: str = ""
    keywords: list[str] = Field(default_factory=list)
    source_file: str = ""
    page_count: int = 0


class Section(BaseModel):
    heading: str
    kind: SectionKind = SectionKind.OTHER
    text: str = ""
    level: int = 1


class ExtractedTable(BaseModel):
    index: int
    caption: str = ""
    headers: list[str] = Field(default_factory=list)
    rows: list[list[str]] = Field(default_factory=list)
    page: int | None = None


class ExtractedFigure(BaseModel):
    index: int
    caption: str = ""
    page: int | None = None


class KeyNumber(BaseModel):
    """A statistic found in the running text, with its sentence for context."""

    value: str
    kind: str  # p_value | percentage | sample_size | effect_size | ci | mean_sd | other
    sentence: str
    section: SectionKind = SectionKind.OTHER


class ArticleExtraction(BaseModel):
    metadata: ArticleMetadata
    sections: list[Section] = Field(default_factory=list)
    tables: list[ExtractedTable] = Field(default_factory=list)
    figures: list[ExtractedFigure] = Field(default_factory=list)
    key_numbers: list[KeyNumber] = Field(default_factory=list)
    word_count: int = 0

    def section(self, kind: SectionKind) -> str:
        """Concatenated text of every section of the given kind."""
        return "\n\n".join(s.text for s in self.sections if s.kind == kind and s.text)


# ---------------------------------------------------------------------------
# Infographic side
# ---------------------------------------------------------------------------


class ChartKind(str, Enum):
    BAR = "bar"  # one or more series, categorical x
    DONUT = "donut"  # part-to-whole, single series
    DUMBBELL = "dumbbell"  # before/after or two-arm comparison per category
    FOREST = "forest"  # effect sizes with confidence intervals


class ChartSeries(BaseModel):
    name: str
    values: list[float]
    lower: list[float] | None = None  # forest only: CI lower bounds
    upper: list[float] | None = None  # forest only: CI upper bounds


class ChartSpec(BaseModel):
    kind: ChartKind
    title: str
    categories: list[str]
    series: list[ChartSeries]
    unit: str = ""
    source: str = ""  # e.g. "Tabela 2" / "Table 2"
    note: str = ""
    null_value: float | None = None  # forest: line of no effect (1 for OR/RR, 0 for MD)


class StatTile(BaseModel):
    value: str
    label: str
    context: str = ""


class Finding(BaseModel):
    title: str
    detail: str
    stat: str = ""


class StudyDesign(BaseModel):
    design: str = ""
    population: str = ""
    sample_size: str = ""
    intervention: str = ""
    comparator: str = ""
    outcomes: str = ""
    follow_up: str = ""
    setting: str = ""


class FlowStep(BaseModel):
    label: str
    detail: str = ""


class MechanismNode(BaseModel):
    """One box of a mechanism / concept diagram (A -> B -> C)."""

    label: str
    detail: str = ""


class InfographicSpec(BaseModel):
    """Everything the renderer needs. Language of the free text is ``language``."""

    language: str = "pt"
    headline: str
    subtitle: str = ""
    one_sentence_summary: str = ""
    reference: str = ""
    citation_short: str = ""
    metadata: ArticleMetadata = Field(default_factory=ArticleMetadata)
    stat_tiles: list[StatTile] = Field(default_factory=list)
    study_design: StudyDesign = Field(default_factory=StudyDesign)
    flow: list[FlowStep] = Field(default_factory=list)
    mechanism: list[MechanismNode] = Field(default_factory=list)
    key_findings: list[Finding] = Field(default_factory=list)
    charts: list[ChartSpec] = Field(default_factory=list)
    takeaways: list[str] = Field(default_factory=list)
    clinical_implications: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    glossary: dict[str, str] = Field(default_factory=dict)
    keywords: list[str] = Field(default_factory=list)
    generated_by: str = "heuristic"
    warnings: list[str] = Field(default_factory=list)


class LLMInfographicDraft(BaseModel):
    """Schema handed to an LLM. Deliberately smaller than ``InfographicSpec``.

    Metadata, provenance and table-derived charts are filled by code; the model
    only writes the interpretive content. Every list is bounded so the result
    fits on one poster.
    """

    headline: str = Field(description="Short, informative headline (max 12 words).")
    subtitle: str = Field(description="One line framing the study question.")
    one_sentence_summary: str = Field(
        description="The whole study in one sentence a clinician can quote."
    )
    stat_tiles: list[StatTile] = Field(
        description="3 to 5 headline numbers (sample size, effect size, p, NNT...)."
    )
    study_design: StudyDesign
    flow: list[FlowStep] = Field(
        description="4 to 7 steps of the study pipeline (recruitment to analysis)."
    )
    mechanism: list[MechanismNode] = Field(
        description="3 to 6 nodes of the central mechanism or concept chain; empty if not applicable."
    )
    key_findings: list[Finding] = Field(
        description="3 to 6 findings with their statistic."
    )
    charts: list[ChartSpec] = Field(
        description="Up to 3 charts built ONLY from numbers stated in the article."
    )
    takeaways: list[str] = Field(description="3 to 5 take-home messages.")
    clinical_implications: list[str] = Field(
        description="2 to 4 practice implications."
    )
    limitations: list[str] = Field(
        description="2 to 4 limitations named by the authors."
    )
    glossary: dict[str, str] = Field(
        description="Up to 6 technical terms with a one-line definition."
    )
    keywords: list[str] = Field(description="Up to 8 keywords.")
