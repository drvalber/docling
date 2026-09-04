import pytest
from _paths import DOCLING_ARTICLE, TRIAL
from article_infographic.extract import extract_article, parse_authors
from article_infographic.models import SectionKind


@pytest.fixture(scope="module")
def doclaynet():
    return extract_article(DOCLING_ARTICLE)


@pytest.fixture(scope="module")
def trial():
    return extract_article(TRIAL)


def test_metadata_from_docling_pdf_output(doclaynet):
    meta = doclaynet.metadata
    assert meta.title.startswith("DocLayNet: A Large Human-Annotated Dataset")
    assert meta.authors[:2] == ["Birgit Pfitzmann", "Christoph Auer"]
    assert meta.doi == "10.1145/3534678.3539043"
    assert meta.year == "2022"
    assert "layout segmentation" in meta.keywords
    assert meta.page_count == 9


def test_sections_are_classified_by_role(doclaynet):
    kinds = {s.heading: s.kind for s in doclaynet.sections}
    assert kinds["ABSTRACT"] is SectionKind.ABSTRACT
    assert kinds["1 INTRODUCTION"] is SectionKind.INTRODUCTION
    assert kinds["3 THE DOCLAYNET DATASET"] is SectionKind.METHODS
    assert kinds["5 EXPERIMENTS"] is SectionKind.RESULTS
    # Unnumbered sub-headings inherit the surrounding numbered section.
    assert kinds["Dataset Comparison"] is SectionKind.RESULTS
    assert kinds["6 CONCLUSION"] is SectionKind.CONCLUSION
    assert kinds["REFERENCES"] is SectionKind.REFERENCES


def test_tables_and_figures_are_captured(doclaynet):
    assert len(doclaynet.tables) == 5
    first = doclaynet.tables[0]
    assert first.caption.startswith("Table 1")
    assert first.headers[0] == "class label"
    assert first.rows[0][0] == "Caption"
    assert len(doclaynet.figures) == 6
    assert doclaynet.figures[0].caption.startswith("Figure 1")


def test_markdown_article_metadata_and_statistics(trial):
    meta = trial.metadata
    assert meta.authors == [
        "Ana Beatriz Moreira",
        "Carlos Eduardo Lima",
        "Fernanda Ribeiro Santos",
        "João Pedro Almeida",
    ]
    assert meta.journal == "Journal of Affective Disorders"
    assert meta.year == "2024"
    assert meta.doi == "10.1016/j.jad.2024.00001"
    kinds = {n.kind for n in trial.key_numbers}
    assert {
        "p_value",
        "ci",
        "effect_size",
        "mean_sd",
        "sample_size",
        "percentage",
    } <= kinds
    p_values = [
        n
        for n in trial.key_numbers
        if n.kind == "p_value" and n.section is SectionKind.RESULTS
    ]
    assert p_values and p_values[0].value == "p < 0.001"
    assert trial.section(SectionKind.CONCLUSION).startswith(
        "Sertraline is superior to placebo"
    )


def test_parse_authors_ignores_affiliations_and_degrees():
    block = "Maria da Silva, MD, PhD1; John A. Smith2, University of Somewhere; Dept. of Psychiatry"
    assert parse_authors(block) == ["Maria da Silva", "John A. Smith"]
