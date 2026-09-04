"""Turn a scientific article into an ``ArticleExtraction`` using Docling.

Any format Docling can read is accepted (PDF, DOCX, HTML, Markdown, and a
previously exported DoclingDocument ``.json``). The PDF route runs the standard
Docling pipeline (layout + table structure models); the other routes are
model-free and fast.
"""

from __future__ import annotations

import logging
import re
from collections.abc import Iterable
from pathlib import Path

from docling_core.types.doc import (
    DocItemLabel,
    DoclingDocument,
    PictureItem,
    SectionHeaderItem,
    TableItem,
    TextItem,
    TitleItem,
)

from article_infographic.models import (
    ArticleExtraction,
    ArticleMetadata,
    ExtractedFigure,
    ExtractedTable,
    KeyNumber,
    Section,
    SectionKind,
)

_log = logging.getLogger(__name__)

# Heading -> section kind. Order matters: the first matching rule wins.
_KIND_RULES: list[tuple[re.Pattern[str], SectionKind]] = [
    (re.compile(r"\b(abstract|resumo|summary|sumário)"), SectionKind.ABSTRACT),
    (
        re.compile(
            r"\b(references|referências|bibliograph|acknowledg|agradecimentos|funding|"
            r"financiamento|conflict|conflito|supplement|apêndice|appendix|declaration)"
        ),
        SectionKind.REFERENCES,
    ),
    (
        re.compile(r"\b(conclus|take.?home|implication|implicaç)"),
        SectionKind.CONCLUSION,
    ),
    (re.compile(r"\b(discuss|limitation|limitaç|strengths)"), SectionKind.DISCUSSION),
    (
        re.compile(
            r"\b(results?|resultados?|findings|experiments?|evaluation|outcomes?|desfechos?)\b"
        ),
        SectionKind.RESULTS,
    ),
    (
        re.compile(
            r"\b(methods?|métodos?|materials?|materiais|participants|participantes|patients|"
            r"pacientes|procedures?|design|desenho|dataset|data|approach|model|statistic|"
            r"estatístic|measures?|instrumentos?|intervention|intervenç|sample|amostra|annotation)"
        ),
        SectionKind.METHODS,
    ),
    (
        re.compile(
            r"\b(introduc|introduç|background|contexto|related work|rationale|objectives?|"
            r"objetivos?|aims?)"
        ),
        SectionKind.INTRODUCTION,
    ),
]
# Kinds that a sub-heading may switch to; anything else inherits its parent.
_STRONG_KINDS = {
    SectionKind.ABSTRACT,
    SectionKind.REFERENCES,
    SectionKind.CONCLUSION,
    SectionKind.DISCUSSION,
}

_NUMBERED = re.compile(r"^\s*(\d+(?:\.\d+)*)\.?\s+")
_DOI = re.compile(r"\b(10\.\d{4,9}/[^\s\"<>]+)", re.IGNORECASE)
_YEAR = re.compile(r"\b(19[89]\d|20[0-4]\d)\b")
_EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
_ARXIV = re.compile(r"arXiv:\s*(\d{4}\.\d{4,5}(?:v\d+)?)", re.IGNORECASE)
_JOURNAL_LINE = re.compile(
    r"\b(journal|revista|proceedings|lancet|jama|bmj|doi|vol\.?|volume|issue|pp\.|published|"
    r"received|accepted|©|\b(19[89]\d|20[0-4]\d)\b)",
    re.IGNORECASE,
)
_KEYWORD_HEAD = re.compile(
    r"^(keywords?|palavras-chave|index terms)\s*[:.\-—]*\s*", re.IGNORECASE
)

_AFFILIATION_HINT = re.compile(
    r"(universit|institut|hospital|department|departamento|faculdade|school|college|"
    r"research|laborat|center|centre|clinic|ibm|google|microsoft|inc\.|ltd|gmbh|"
    r"switzerland|brazil|brasil|usa|united|kingdom|germany|france|italy|spain|"
    r"\d|@|corresponding|author|e-?mail|street|avenue|rua|av\.)",
    re.IGNORECASE,
)
_NAME_TOKEN = re.compile(r"^[A-ZÀ-Ý][\wÀ-ÿ'’\-]*\.?$")  # noqa: RUF001

_NUMBER_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("p_value", re.compile(r"\b[pP]\s*[<=>≤≥]\s*0?[.,]\d+")),
    (
        "ci",
        re.compile(
            r"9[05]\s?%\s?(?:CI|IC)[,:]?\s*[\[\(]?\s*-?\d+(?:[.,]\d+)?\s*(?:to|a|,|;|–|-|—)\s*-?\d+(?:[.,]\d+)?\s*[\]\)]?"  # noqa: RUF001
        ),
    ),
    (
        "effect_size",
        re.compile(
            r"\b(?:a?OR|RR|HR|IRR|SMD|MD|NNT|NNH|d|g|β|r|R2|R²|AUC|mAP|F1|kappa|κ)\s*[=:]\s*-?\d+(?:[.,]\d+)?"
        ),
    ),
    ("mean_sd", re.compile(r"-?\d+(?:[.,]\d+)?\s?±\s?\d+(?:[.,]\d+)?")),
    ("sample_size", re.compile(r"\b[nN]\s*=\s*\d{1,3}(?:[,.]\d{3})*\b")),
    ("percentage", re.compile(r"\b\d{1,3}(?:[.,]\d+)?\s?%")),
]

_SENTENCE_SPLIT = re.compile(
    r"(?<!\bet al)(?<!\bvs)(?<!\bFig)(?<!\bTab)(?<!\be\.g)(?<!\bi\.e)(?<=[.!?])\s+(?=[A-ZÀ-Ý0-9(])"
)

_BODY_LABELS = {
    DocItemLabel.TEXT,
    DocItemLabel.PARAGRAPH,
    DocItemLabel.LIST_ITEM,
    DocItemLabel.FORMULA,
    DocItemLabel.CODE,
}
_SKIP_LABELS = {
    DocItemLabel.PAGE_HEADER,
    DocItemLabel.PAGE_FOOTER,
    DocItemLabel.FOOTNOTE,
}


def classify_heading(heading: str, level: int, current: SectionKind) -> SectionKind:
    """Map a heading to a section kind; sub-headings inherit their parent's kind."""
    stripped = _NUMBERED.sub("", heading).strip().lower()
    matched = SectionKind.OTHER
    for pattern, kind in _KIND_RULES:
        if pattern.search(stripped):
            matched = kind
            break
    in_body = current in (
        SectionKind.METHODS,
        SectionKind.RESULTS,
        SectionKind.DISCUSSION,
    )
    if level > 1 and in_body and matched not in _STRONG_KINDS:
        return current
    if matched is not SectionKind.OTHER:
        return matched
    if in_body:
        # Unlabelled body headings ("Learning curve", "Cohort B") continue the
        # surrounding narrative.
        return current
    return SectionKind.OTHER


def heading_level(heading: str, item_level: int | None, numbered_doc: bool) -> int:
    match = _NUMBERED.match(heading)
    if match:
        return match.group(1).count(".") + 1
    if numbered_doc:
        # The article numbers its main sections, so a bare heading is a sub-heading.
        return 2
    if item_level and item_level > 0:
        return item_level
    return 1


def split_sentences(text: str) -> list[str]:
    return [s.strip() for s in _SENTENCE_SPLIT.split(text) if s.strip()]


def find_key_numbers(sections: Iterable[Section], limit: int = 60) -> list[KeyNumber]:
    found: list[KeyNumber] = []
    seen: set[str] = set()
    for section in sections:
        if section.kind in (SectionKind.REFERENCES, SectionKind.OTHER):
            continue
        for sentence in split_sentences(section.text):
            for kind, pattern in _NUMBER_PATTERNS:
                for match in pattern.finditer(sentence):
                    key = (kind, match.group(0).strip(), sentence[:80])
                    if key in seen:
                        continue
                    seen.add(key)
                    found.append(
                        KeyNumber(
                            value=match.group(0).strip(),
                            kind=kind,
                            sentence=sentence[:400],
                            section=section.kind,
                        )
                    )
                    if len(found) >= limit:
                        return found
    return found


_AFFILIATION_TOKENS = re.compile(
    r"^(ibm|google|microsoft|meta|university|universidade|universidad|université|institute|"
    r"instituto|institut|hospital|department|departamento|dept\.?|faculty|faculdade|school|"
    r"college|research|laboratory|laboratório|lab|center|centre|centro|clinic|clínica|"
    r"division|divisão|unit|program|programa|group|grupo|foundation|fundação|md|phd|msc|"
    r"dr|prof|professor|dsc|frcp|mph|rn|bsc|ba|ma|mba|inc|ltd|llc|gmbh|corresponding|"
    r"author|authors|email|e-mail|and|e|y|et|of|the)$",
    re.IGNORECASE,
)
_NAME_PARTICLE = re.compile(r"^(de|da|do|dos|das|del|della|di|van|von|der|den|le|la)$")


def parse_authors(block: str) -> list[str]:
    """Best-effort author names from the text between the title and the abstract.

    Names are runs of two to four capitalised tokens; affiliation words, degrees
    and e-mail addresses break a run.
    """
    block = _EMAIL.sub(" | ", block)
    block = re.sub(r"[\d\*†‡§¶#]+", " ", block)
    names: list[str] = []
    run: list[str] = []

    def flush() -> None:
        if 2 <= len(run) <= 4:
            name = " ".join(run)
            if name not in names:
                names.append(name)
        run.clear()

    for raw in re.split(r"\s+", block):
        token = raw.strip(",;|()[]")
        if (
            not token
            or raw.strip() in {"|", ",", ";"}
            or _AFFILIATION_TOKENS.match(token)
        ):
            flush()
            continue
        if _NAME_TOKEN.match(token) and not _AFFILIATION_HINT.search(token):
            run.append(token)
        elif run and _NAME_PARTICLE.match(token):
            run.append(token)  # "Maria da Silva", "Ludwig van Beethoven"
        else:
            flush()
        if raw.endswith((",", ";")):
            flush()
    flush()
    return names[:15]


def _is_probably_title(text: str) -> bool:
    words = text.split()
    return 3 <= len(words) <= 40 and not _NUMBERED.match(text)


def extract_from_document(
    doc: DoclingDocument, source_file: str = ""
) -> ArticleExtraction:
    """Walk a DoclingDocument and build the extraction contract."""
    sections: list[Section] = []
    tables: list[ExtractedTable] = []
    figures: list[ExtractedFigure] = []
    marginalia: list[str] = []
    title = ""
    preamble: list[str] = []  # text between title and first section
    keywords: list[str] = []
    current = Section(heading="", kind=SectionKind.OTHER, level=0)
    seen_first_heading = False
    numbered_doc = False

    for item, _level in doc.iterate_items(with_groups=False, traverse_pictures=False):
        if isinstance(item, TitleItem) or (
            isinstance(item, TextItem) and item.label == DocItemLabel.TITLE
        ):
            if not title:
                title = item.text.strip()
            continue
        if isinstance(item, SectionHeaderItem):
            text = item.text.strip()
            if not title and not seen_first_heading and _is_probably_title(text):
                title = text
                continue
            seen_first_heading = True
            if _KEYWORD_HEAD.match(text):
                current = Section(heading=text, kind=SectionKind.OTHER, level=9)
                continue
            numbered_doc = numbered_doc or bool(_NUMBERED.match(text))
            level = heading_level(text, item.level, numbered_doc)
            kind = classify_heading(text, level, current.kind)
            if current.text.strip() or current.heading:
                sections.append(current)
            current = Section(heading=text, kind=kind, level=level)
            continue
        if isinstance(item, TableItem):
            tables.append(_table_from_item(item, doc, len(tables) + 1))
            continue
        if isinstance(item, PictureItem):
            figures.append(
                ExtractedFigure(
                    index=len(figures) + 1,
                    caption=item.caption_text(doc).strip(),
                    page=item.prov[0].page_no if item.prov else None,
                )
            )
            continue
        if not isinstance(item, TextItem):
            continue
        text = item.text.strip()
        if not text:
            continue
        if item.label in _SKIP_LABELS:
            marginalia.append(text)
            continue
        if item.label == DocItemLabel.CAPTION:
            continue
        if item.label not in _BODY_LABELS:
            continue
        if current.level == 9:  # keyword block
            keywords.extend(_split_keywords(text))
            continue
        if _KEYWORD_HEAD.match(text):
            keywords.extend(_split_keywords(_KEYWORD_HEAD.sub("", text)))
            continue
        if not seen_first_heading and title:
            preamble.append(text)
            continue
        current.text = f"{current.text}\n{text}".strip() if current.text else text

    if current.text.strip() or current.heading:
        sections.append(current)

    # An article whose abstract precedes any heading keeps it in the preamble.
    if preamble and not any(s.kind == SectionKind.ABSTRACT for s in sections):
        long_paragraphs = [p for p in preamble if len(p.split()) > 60]
        if long_paragraphs:
            sections.insert(
                0,
                Section(
                    heading="Abstract",
                    kind=SectionKind.ABSTRACT,
                    text="\n".join(long_paragraphs),
                ),
            )
            preamble = [p for p in preamble if p not in long_paragraphs]

    all_text = "\n".join([title, *preamble, *marginalia, *(s.text for s in sections)])
    author_lines = [p for p in preamble if not _JOURNAL_LINE.search(p)]
    journal_lines = [p for p in preamble if _JOURNAL_LINE.search(p)]
    metadata = ArticleMetadata(
        title=title or doc.name,
        authors=parse_authors("\n".join(author_lines)),
        journal=_guess_journal(journal_lines + marginalia, all_text),
        year=_guess_year(marginalia, all_text),
        doi=_first(_DOI, all_text),
        keywords=keywords[:12],
        source_file=source_file,
        page_count=len(doc.pages),
    )
    body_sections = [s for s in sections if s.kind != SectionKind.REFERENCES]
    extraction = ArticleExtraction(
        metadata=metadata,
        sections=sections,
        tables=tables,
        figures=figures,
        key_numbers=find_key_numbers(body_sections),
        word_count=sum(len(s.text.split()) for s in body_sections),
    )
    return extraction


def _split_keywords(text: str) -> list[str]:
    return [k.strip(" .;") for k in re.split(r"[;,·•]", text) if k.strip(" .;")]


def _first(pattern: re.Pattern[str], text: str) -> str:
    match = pattern.search(text)
    return match.group(1).rstrip(".,;") if match else ""


def _guess_year(marginalia: list[str], all_text: str) -> str:
    for chunk in marginalia:
        year = _first(_YEAR, chunk)
        if year:
            return year
    arxiv = _first(_ARXIV, all_text)
    if arxiv:
        return f"20{arxiv[:2]}"
    return _first(_YEAR, all_text[:4000])


def _guess_journal(candidates: list[str], all_text: str) -> str:
    arxiv = _first(_ARXIV, all_text)
    if arxiv:
        return f"arXiv:{arxiv}"
    for chunk in candidates:
        cleaned = re.sub(r"\s+", " ", chunk).strip()
        if not (8 <= len(cleaned) <= 160) or not re.search(r"[A-Za-z]{4}", cleaned):
            continue
        if re.search(
            r"journal|revista|proceedings|lancet|jama|bmj|psychiatry|medicine|conference|\bvol\b|doi",
            cleaned,
            re.IGNORECASE,
        ):
            # Keep the journal name only: drop the year, DOI and volume/page trail.
            name = re.split(
                r"[.;,]?\s*(?:\b(?:19[89]\d|20[0-4]\d)\b|doi|https?://|\bvol)",
                cleaned,
                maxsplit=1,
                flags=re.IGNORECASE,
            )[0]
            name = name.strip(" .;,:")
            if len(name) >= 4:
                return name
    return ""


def _table_from_item(
    item: TableItem, doc: DoclingDocument, index: int
) -> ExtractedTable:
    headers: list[str] = []
    rows: list[list[str]] = []
    try:
        df = item.export_to_dataframe(doc)
        headers = [
            " / ".join(str(part) for part in col if str(part) and str(part) != "nan")
            if isinstance(col, tuple)
            else str(col)
            for col in df.columns
        ]
        for _, row in df.iterrows():
            rows.append(
                ["" if str(v) == "nan" else str(v).strip() for v in row.tolist()]
            )
    except Exception as exc:  # export_to_dataframe is lenient but not bulletproof
        _log.warning("Table %s could not be exported as a dataframe: %s", index, exc)
        for row in item.data.grid:
            rows.append([cell.text.strip() for cell in row])
        if rows:
            headers, rows = rows[0], rows[1:]
    return ExtractedTable(
        index=index,
        caption=item.caption_text(doc).strip(),
        headers=headers,
        rows=rows,
        page=item.prov[0].page_no if item.prov else None,
    )


def load_document(path: Path, converter=None) -> DoclingDocument:
    """Load a DoclingDocument from a JSON export or by converting the file."""
    if path.suffix.lower() == ".json":
        return DoclingDocument.load_from_json(path)
    if converter is None:
        from docling.document_converter import DocumentConverter

        converter = DocumentConverter()
    result = converter.convert(path)
    return result.document


def extract_article(path: Path, converter=None) -> ArticleExtraction:
    doc = load_document(path, converter)
    return extract_from_document(doc, source_file=path.name)
