"""Derive chart specifications from the numeric tables of an article.

The rules are deliberately conservative: a chart is only proposed when a table
has a clear label column plus at least one column that is mostly numeric. The
form follows the data's job (see the data-viz guidance): part-to-whole becomes
a donut, two arms per row become a dumbbell, effect sizes with confidence
intervals become a forest plot, and everything else is a horizontal bar chart.
"""

from __future__ import annotations

import math
import re

from article_infographic.models import (
    ChartKind,
    ChartSeries,
    ChartSpec,
    ExtractedTable,
)

_NUM = re.compile(
    r"^[<>≤≥~≈]?\s*[-−+]?\s*\d{1,3}(?:[ ,]\d{3})*(?:[.,]\d+)?\s*%?$|^[-−+]?\d+(?:[.,]\d+)?\s*%?$"  # noqa: RUF001
)
_CI_CELL = re.compile(
    r"^\s*([-−]?\d+(?:[.,]\d+)?)\s*[\(\[]\s*([-−]?\d+(?:[.,]\d+)?)\s*(?:to|a|,|;|–|-|—)\s*([-−]?\d+(?:[.,]\d+)?)\s*[\)\]]"  # noqa: RUF001
)
_EFFECT_HEADER = re.compile(
    r"\b(a?OR|RR|HR|IRR|SMD|MD|WMD|d|g|β|beta|coef)\b", re.IGNORECASE
)
_BEFORE_AFTER = re.compile(
    r"\b(baseline|basal|pre|pré|before|antes|week 0|t0|t1|follow|final|post|pós|after|depois|"
    r"endpoint|week \d+|month \d+|placebo|control|controle|intervention|intervenção|treatment|tratamento)\b",
    re.IGNORECASE,
)

MAX_CATEGORIES = 8
MAX_SERIES = 4


def parse_number(cell: str) -> float:
    """Parse a numeric-looking cell; ``nan`` when the cell is not a number."""
    text = cell.strip().replace("−", "-").replace(" ", "").replace(" ", "")  # noqa: RUF001
    if not text or not _NUM.match(cell.strip().replace("−", "-")):  # noqa: RUF001
        return math.nan
    text = text.lstrip("<>≤≥~≈")
    text = text.rstrip("%")
    if "," in text and "." in text:
        text = text.replace(",", "")
    elif "," in text:
        # "1,234" is thousands; "12,5" is a decimal comma.
        text = (
            text.replace(",", "")
            if re.fullmatch(r"-?\d{1,3}(,\d{3})+", text)
            else text.replace(",", ".")
        )
    try:
        value = float(text)
    except ValueError:
        return math.nan
    return value


def _column(table: ExtractedTable, idx: int) -> list[str]:
    return [row[idx] if idx < len(row) else "" for row in table.rows]


def _numeric_share(cells: list[str]) -> float:
    filled = [c for c in cells if c.strip()]
    if not filled:
        return 0.0
    return sum(1 for c in filled if not math.isnan(parse_number(c))) / len(filled)


def _label_column(table: ExtractedTable) -> int | None:
    n_cols = max((len(r) for r in table.rows), default=0)
    for idx in range(n_cols):
        cells = _column(table, idx)
        if _numeric_share(cells) < 0.3 and sum(1 for c in cells if c.strip()) >= max(
            2, len(cells) // 2
        ):
            return idx
    return None


def _header(table: ExtractedTable, idx: int) -> str:
    if idx < len(table.headers) and table.headers[idx].strip():
        return table.headers[idx].strip()
    return f"col {idx + 1}"


def _unit_from_header(header: str) -> str:
    return "%" if "%" in header else ""


def _table_ref(table: ExtractedTable, language: str) -> str:
    return f"{'Tabela' if language == 'pt' else 'Table'} {table.index}"


def _forest_from_table(
    table: ExtractedTable, label_idx: int, language: str
) -> ChartSpec | None:
    n_cols = max((len(r) for r in table.rows), default=0)
    for idx in range(n_cols):
        if idx == label_idx:
            continue
        header = _header(table, idx)
        if not _EFFECT_HEADER.search(header):
            continue
        cells = _column(table, idx)
        matches = [_CI_CELL.match(c) for c in cells]
        if sum(1 for m in matches if m) < max(2, len(cells) // 2):
            continue
        cats, vals, lows, highs = [], [], [], []
        for row, m in zip(table.rows, matches):
            if not m:
                continue
            cats.append(row[label_idx] if label_idx < len(row) else "")
            vals.append(parse_number(m.group(1)))
            lows.append(parse_number(m.group(2)))
            highs.append(parse_number(m.group(3)))
        if len(cats) < 2:
            continue
        null = 1.0 if re.search(r"\b(a?OR|RR|HR|IRR)\b", header, re.IGNORECASE) else 0.0
        return ChartSpec(
            kind=ChartKind.FOREST,
            title=_clean_caption(table.caption, language) or header,
            categories=cats[:MAX_CATEGORIES],
            series=[
                ChartSeries(
                    name=header,
                    values=vals[:MAX_CATEGORIES],
                    lower=lows[:MAX_CATEGORIES],
                    upper=highs[:MAX_CATEGORIES],
                )
            ],
            source=_table_ref(table, language),
            null_value=null,
            note=f"{header} (IC 95%)" if language == "pt" else f"{header} (95% CI)",
        )
    return None


def _clean_caption(caption: str, language: str) -> str:
    text = re.sub(
        r"^\s*(table|tabela)\s*\d+[\.:]?\s*", "", caption, flags=re.IGNORECASE
    ).strip()
    if not text:
        return ""
    first = re.split(r"(?<=[.;])\s", text, maxsplit=1)[0]
    return first[:110].rstrip(".")


def chart_from_table(table: ExtractedTable, language: str = "pt") -> ChartSpec | None:
    if len(table.rows) < 2:
        return None
    label_idx = _label_column(table)
    if label_idx is None:
        return None
    forest = _forest_from_table(table, label_idx, language)
    if forest is not None:
        return forest

    n_cols = max((len(r) for r in table.rows), default=0)
    numeric_cols = [
        idx
        for idx in range(n_cols)
        if idx != label_idx and _numeric_share(_column(table, idx)) >= 0.7
    ]
    if not numeric_cols:
        return None

    rows = [r for r in table.rows if label_idx < len(r) and r[label_idx].strip()]
    rows = [
        r
        for r in rows
        if not re.match(
            r"^(total|all|todos|overall|mean|média)\b", r[label_idx], re.IGNORECASE
        )
    ] or rows
    rows = rows[:MAX_CATEGORIES]
    categories = [r[label_idx].strip() for r in rows]
    series: list[ChartSeries] = []
    for idx in numeric_cols[:MAX_SERIES]:
        values = [parse_number(r[idx]) if idx < len(r) else math.nan for r in rows]
        if all(math.isnan(v) for v in values):
            continue
        series.append(ChartSeries(name=_header(table, idx), values=values))
    series = _same_scale(series)
    if not series:
        return None

    unit = _unit_from_header(series[0].name)
    title = _clean_caption(table.caption, language) or (
        f"Dados da Tabela {table.index}"
        if language == "pt"
        else f"Data from Table {table.index}"
    )
    kind = ChartKind.BAR
    finite = [v for v in series[0].values if not math.isnan(v)]
    if (
        len(series) == 1
        and len(finite) >= 2
        and all(v >= 0 for v in finite)
        and 98 <= sum(finite) <= 102
    ):
        kind = ChartKind.DONUT
        unit = unit or "%"
    elif len(series) == 2 and all(_BEFORE_AFTER.search(s.name) for s in series):
        kind = ChartKind.DUMBBELL
    return ChartSpec(
        kind=kind,
        title=title,
        categories=categories,
        series=series,
        unit=unit,
        source=_table_ref(table, language),
    )


def _same_scale(series: list[ChartSeries]) -> list[ChartSeries]:
    """Keep only series that share one axis: never mix counts with percentages."""
    percent = [s for s in series if "%" in s.name]
    if percent:
        return percent[:MAX_SERIES]

    def magnitude(s: ChartSeries) -> float:
        finite = [abs(v) for v in s.values if not math.isnan(v)]
        return max(finite) if finite else 0.0

    best: list[ChartSeries] = []
    for anchor in series:
        ref = magnitude(anchor) or 1.0
        group = [s for s in series if ref / 20 <= (magnitude(s) or ref) <= ref * 20]
        if len(group) > len(best):
            best = group
    return best[:MAX_SERIES]


def charts_from_tables(
    tables: list[ExtractedTable], language: str = "pt", limit: int = 4
) -> list[ChartSpec]:
    charts: list[ChartSpec] = []
    for table in tables:
        chart = chart_from_table(table, language)
        if chart is not None:
            charts.append(chart)
        if len(charts) >= limit:
            break
    return charts
