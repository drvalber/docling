"""Inline-SVG chart rendering for ``ChartSpec`` objects.

Every chart is self-contained SVG that reads colours from CSS custom properties
(``--series-1`` ... ``--series-8``, ``--ink``, ``--grid`` ...) so light and dark
themes swap in one place. Marks follow the data-viz house rules: thin bars with
rounded data-ends, a surface gap between adjacent fills, at least 8px markers,
a legend whenever there are two or more series, and a native ``<title>`` per
mark for hover.
"""

from __future__ import annotations

import math
from html import escape

from article_infographic.models import ChartKind, ChartSpec

_FONT = 'font-family="system-ui, -apple-system, Segoe UI, sans-serif"'
_MAX_SERIES = 8


def _fmt(value: float, unit: str = "") -> str:
    if math.isnan(value):
        return "–"  # noqa: RUF001
    if abs(value) >= 1000:
        text = f"{value:,.0f}"
    elif float(value).is_integer():
        text = f"{int(value)}"
    else:
        text = f"{value:.2f}".rstrip("0").rstrip(".")
    return f"{text}{unit}" if unit in ("%",) else (f"{text} {unit}".strip())


def _text_width(text: str, size: float) -> float:
    return len(text) * size * 0.56


def _nice_max(value: float) -> float:
    if value <= 0:
        return 1.0
    magnitude = 10 ** math.floor(math.log10(value))
    for step in (1, 2, 2.5, 5, 10):
        if value <= step * magnitude:
            return step * magnitude
    return 10 * magnitude


def _nice_ticks(vmin: float, vmax: float, count: int = 5) -> list[float]:
    """Round tick positions covering [vmin, vmax]."""
    span = (vmax - vmin) or 1.0
    raw = span / max(count - 1, 1)
    magnitude = 10 ** math.floor(math.log10(raw))
    step = next(s * magnitude for s in (1, 2, 2.5, 5, 10) if raw <= s * magnitude)
    start = math.floor(vmin / step) * step
    ticks = []
    value = start
    while value <= vmax + step * 0.01:
        ticks.append(round(value, 6))
        value += step
    return ticks


def _clip(text: str, limit: int) -> str:
    return text if len(text) <= limit else text[: limit - 1] + "…"


def _legend(names: list[str], x: float, y: float) -> str:
    parts = []
    cursor = x
    for i, name in enumerate(names[:_MAX_SERIES]):
        parts.append(
            f'<rect x="{cursor:.1f}" y="{y - 9:.1f}" width="12" height="12" rx="3" '
            f'fill="var(--series-{i + 1})"/>'
            f'<text x="{cursor + 17:.1f}" y="{y + 1:.1f}" font-size="12" fill="var(--ink-2)" {_FONT}>'
            f"{escape(name)}</text>"
        )
        cursor += 17 + _text_width(name, 12) + 18
    return "".join(parts)


def _wrap(svg_body: str, width: float, height: float, title: str) -> str:
    return (
        f'<svg class="chart" viewBox="0 0 {width:.0f} {height:.0f}" role="img" '
        f'aria-label="{escape(title)}" xmlns="http://www.w3.org/2000/svg">'
        f"{svg_body}</svg>"
    )


def render_chart(spec: ChartSpec) -> str:
    spec = _sanitize(spec)
    if not spec.categories or not spec.series:
        return ""
    if spec.kind is ChartKind.DONUT:
        return _donut(spec)
    if spec.kind is ChartKind.DUMBBELL and len(spec.series) >= 2:
        return _dumbbell(spec)
    if spec.kind is ChartKind.FOREST:
        return _forest(spec)
    return _bars(spec)


def _sanitize(spec: ChartSpec) -> ChartSpec:
    """Align series lengths with categories and drop empty series."""
    n = len(spec.categories)
    series = []
    for s in spec.series[:_MAX_SERIES]:
        values = [float(v) if v is not None else math.nan for v in s.values[:n]]
        values += [math.nan] * (n - len(values))
        if all(math.isnan(v) for v in values):
            continue
        lower = upper = None
        if s.lower is not None and s.upper is not None:
            lower = [float(v) for v in s.lower[:n]] + [math.nan] * (
                n - len(s.lower[:n])
            )
            upper = [float(v) for v in s.upper[:n]] + [math.nan] * (
                n - len(s.upper[:n])
            )
        series.append(
            s.model_copy(update={"values": values, "lower": lower, "upper": upper})
        )
    return spec.model_copy(update={"series": series})


# ---------------------------------------------------------------------------
# Horizontal (grouped) bars
# ---------------------------------------------------------------------------


def _bars(spec: ChartSpec) -> str:
    n_cat = len(spec.categories)
    n_ser = len(spec.series)
    bar_h = 14 if n_ser == 1 else 10
    gap = 2
    group_h = n_ser * bar_h + (n_ser - 1) * gap + 14
    label_w = min(180, max(_text_width(_clip(c, 28), 12) for c in spec.categories) + 12)
    width = 640
    left = label_w + 8
    top = 36 if n_ser > 1 else 14
    plot_w = width - left - 70
    height = top + n_cat * group_h + 28

    all_values = [v for s in spec.series for v in s.values if not math.isnan(v)]
    vmax = _nice_max(max([*all_values, 0]))
    vmin = min([*all_values, 0])
    if vmin < 0:
        vmin = -_nice_max(-vmin)
    span = vmax - vmin or 1.0

    def sx(v: float) -> float:
        return left + (v - vmin) / span * plot_w

    body = []
    # gridlines + axis ticks
    ticks = 4
    for i in range(ticks + 1):
        v = vmin + span * i / ticks
        x = sx(v)
        body.append(
            f'<line x1="{x:.1f}" y1="{top - 4}" x2="{x:.1f}" y2="{height - 26}" '
            f'stroke="var(--grid)" stroke-width="1"/>'
            f'<text x="{x:.1f}" y="{height - 10}" font-size="11" text-anchor="middle" '
            f'fill="var(--ink-3)" {_FONT}>{_fmt(v, spec.unit)}</text>'
        )
    body.append(
        f'<line x1="{sx(0):.1f}" y1="{top - 4}" x2="{sx(0):.1f}" y2="{height - 26}" '
        f'stroke="var(--axis)" stroke-width="1.5"/>'
    )
    label_values = n_cat * n_ser <= 12
    for ci, category in enumerate(spec.categories):
        gy = top + ci * group_h
        body.append(
            f'<text x="{left - 8:.1f}" y="{gy + (group_h - 14) / 2 + 4:.1f}" font-size="12" '
            f'text-anchor="end" fill="var(--ink-2)" {_FONT}>{escape(_clip(category, 28))}</text>'
        )
        for si, s in enumerate(spec.series):
            v = s.values[ci]
            if math.isnan(v):
                continue
            y = gy + si * (bar_h + gap)
            x0, x1 = sorted((sx(0), sx(v)))
            w = max(x1 - x0, 1.5)
            # Rounded only on the data end: anchor the bar on the baseline.
            rx = 4 if w > 8 else 0
            body.append(
                f'<rect class="mark" x="{x0:.1f}" y="{y:.1f}" width="{w:.1f}" height="{bar_h}" '
                f'rx="{rx}" fill="var(--series-{si + 1})" stroke="var(--surface)" stroke-width="2">'
                f"<title>{escape(category)} · {escape(s.name)}: {_fmt(v, spec.unit)}</title></rect>"
            )
            if label_values:
                lx = x1 + 6 if v >= 0 else x0 - 6
                anchor = "start" if v >= 0 else "end"
                body.append(
                    f'<text x="{lx:.1f}" y="{y + bar_h - 3:.1f}" font-size="11" text-anchor="{anchor}" '
                    f'fill="var(--ink-2)" {_FONT}>{_fmt(v, spec.unit)}</text>'
                )
    if n_ser > 1:
        body.append(_legend([s.name for s in spec.series], left, 16))
    return _wrap("".join(body), width, height, spec.title)


# ---------------------------------------------------------------------------
# Donut (part-to-whole)
# ---------------------------------------------------------------------------


def _donut(spec: ChartSpec) -> str:
    series = spec.series[0]
    pairs = [
        (c, v)
        for c, v in zip(spec.categories, series.values)
        if not math.isnan(v) and v > 0
    ]
    if not pairs:
        return ""
    if len(pairs) > _MAX_SERIES:
        head = pairs[: _MAX_SERIES - 1]
        pairs = [
            *head,
            (
                "Outros" if spec.title else "Other",
                sum(v for _, v in pairs[_MAX_SERIES - 1 :]),
            ),
        ]
    total = sum(v for _, v in pairs)
    width, height = 640, 240
    cx, cy, r, ring = 130, 120, 92, 26
    body = []
    angle = -math.pi / 2
    for i, (label, value) in enumerate(pairs):
        frac = value / total
        a0, a1 = angle, angle + frac * 2 * math.pi
        angle = a1
        if frac >= 0.999:
            body.append(
                f'<circle cx="{cx}" cy="{cy}" r="{r - ring / 2}" fill="none" stroke="var(--series-1)" '
                f'stroke-width="{ring}"/>'
            )
            continue
        large = 1 if (a1 - a0) > math.pi else 0
        x0, y0 = cx + r * math.cos(a0), cy + r * math.sin(a0)
        x1, y1 = cx + r * math.cos(a1), cy + r * math.sin(a1)
        ri = r - ring
        xi0, yi0 = cx + ri * math.cos(a1), cy + ri * math.sin(a1)
        xi1, yi1 = cx + ri * math.cos(a0), cy + ri * math.sin(a0)
        path = (
            f"M{x0:.2f},{y0:.2f} A{r},{r} 0 {large} 1 {x1:.2f},{y1:.2f} "
            f"L{xi0:.2f},{yi0:.2f} A{ri},{ri} 0 {large} 0 {xi1:.2f},{yi1:.2f} Z"
        )
        pct = f"{frac * 100:.1f}".rstrip("0").rstrip(".")
        body.append(
            f'<path class="mark" d="{path}" fill="var(--series-{i + 1})" stroke="var(--surface)" '
            f'stroke-width="2"><title>{escape(label)}: {_fmt(value, spec.unit)} ({pct}%)</title></path>'
        )
    body.append(
        f'<text x="{cx}" y="{cy + 6}" font-size="20" font-weight="600" text-anchor="middle" '
        f'fill="var(--ink)" {_FONT}>{_fmt(total, spec.unit)}</text>'
    )
    # Legend with values, stacked to the right of the ring
    ly = 40
    for i, (label, value) in enumerate(pairs):
        pct = f"{value / total * 100:.0f}"
        body.append(
            f'<rect x="270" y="{ly - 10}" width="12" height="12" rx="3" fill="var(--series-{i + 1})"/>'
            f'<text x="290" y="{ly}" font-size="12" fill="var(--ink-2)" {_FONT}>'
            f"{escape(_clip(label, 34))}</text>"
            f'<text x="{width - 20}" y="{ly}" font-size="12" text-anchor="end" fill="var(--ink-2)" '
            f"{_FONT}>{_fmt(value, spec.unit)} · {pct}%</text>"
        )
        ly += 22
    height = max(height, ly + 10)
    return _wrap("".join(body), width, height, spec.title)


# ---------------------------------------------------------------------------
# Dumbbell (two arms per category)
# ---------------------------------------------------------------------------


def _dumbbell(spec: ChartSpec) -> str:
    a, b = spec.series[0], spec.series[1]
    n_cat = len(spec.categories)
    row_h = 30
    label_w = min(180, max(_text_width(_clip(c, 28), 12) for c in spec.categories) + 12)
    width = 640
    left = label_w + 8
    top = 40
    plot_w = width - left - 40
    height = top + n_cat * row_h + 24
    values = [v for v in a.values + b.values if not math.isnan(v)]
    vmax = _nice_max(max([*values, 0]))
    vmin = min([*values, 0])
    span = (vmax - vmin) or 1.0

    def sx(v: float) -> float:
        return left + (v - vmin) / span * plot_w

    body = [_legend([a.name, b.name], left, 16)]
    for i in range(5):
        v = vmin + span * i / 4
        body.append(
            f'<line x1="{sx(v):.1f}" y1="{top - 6}" x2="{sx(v):.1f}" y2="{height - 22}" '
            f'stroke="var(--grid)"/>'
            f'<text x="{sx(v):.1f}" y="{height - 6}" font-size="11" text-anchor="middle" '
            f'fill="var(--ink-3)" {_FONT}>{_fmt(v, spec.unit)}</text>'
        )
    for ci, category in enumerate(spec.categories):
        y = top + ci * row_h + row_h / 2
        va, vb = a.values[ci], b.values[ci]
        body.append(
            f'<text x="{left - 8:.1f}" y="{y + 4:.1f}" font-size="12" text-anchor="end" '
            f'fill="var(--ink-2)" {_FONT}>{escape(_clip(category, 28))}</text>'
        )
        if math.isnan(va) or math.isnan(vb):
            continue
        body.append(
            f'<line x1="{sx(va):.1f}" y1="{y:.1f}" x2="{sx(vb):.1f}" y2="{y:.1f}" '
            f'stroke="var(--ink-3)" stroke-width="2"/>'
        )
        for si, (s, v) in enumerate(((a, va), (b, vb))):
            body.append(
                f'<circle class="mark" cx="{sx(v):.1f}" cy="{y:.1f}" r="6" fill="var(--series-{si + 1})" '
                f'stroke="var(--surface)" stroke-width="2"><title>{escape(category)} · '
                f"{escape(s.name)}: {_fmt(v, spec.unit)}</title></circle>"
            )
        delta = vb - va
        sign = "+" if delta > 0 else ""
        body.append(
            f'<text x="{max(sx(va), sx(vb)) + 10:.1f}" y="{y + 4:.1f}" font-size="11" '
            f'fill="var(--ink-2)" {_FONT}>{sign}{_fmt(delta, spec.unit)}</text>'
        )
    return _wrap("".join(body), width, height, spec.title)


# ---------------------------------------------------------------------------
# Forest plot (effect sizes with confidence intervals)
# ---------------------------------------------------------------------------


def _forest(spec: ChartSpec) -> str:
    s = spec.series[0]
    n_cat = len(spec.categories)
    row_h = 30
    label_w = min(200, max(_text_width(_clip(c, 30), 12) for c in spec.categories) + 12)
    width = 640
    left = label_w + 8
    top = 24
    plot_w = width - left - 150
    height = top + n_cat * row_h + 26
    lows = s.lower or s.values
    highs = s.upper or s.values
    finite = [v for v in list(s.values) + list(lows) + list(highs) if not math.isnan(v)]
    if not finite:
        return ""
    null = (
        spec.null_value
        if spec.null_value is not None
        else (1.0 if min(finite) > 0 else 0.0)
    )
    vmin, vmax = min([*finite, null]), max([*finite, null])
    pad = (vmax - vmin) * 0.1 or 0.5
    vmin, vmax = vmin - pad, vmax + pad
    span = vmax - vmin

    def sx(v: float) -> float:
        return left + (v - vmin) / span * plot_w

    body = [
        f'<line x1="{sx(null):.1f}" y1="{top - 8}" x2="{sx(null):.1f}" y2="{height - 22}" '
        f'stroke="var(--axis)" stroke-width="1.5" stroke-dasharray="4 3"/>'
    ]
    for v in _nice_ticks(vmin, vmax):
        if v < vmin or v > vmax:
            continue
        body.append(
            f'<line x1="{sx(v):.1f}" y1="{top - 8}" x2="{sx(v):.1f}" y2="{height - 22}" stroke="var(--grid)"/>'
            f'<text x="{sx(v):.1f}" y="{height - 6}" font-size="11" text-anchor="middle" '
            f'fill="var(--ink-3)" {_FONT}>{_fmt(v)}</text>'
        )
    for ci, category in enumerate(spec.categories):
        y = top + ci * row_h + row_h / 2
        v, lo, hi = s.values[ci], lows[ci], highs[ci]
        body.append(
            f'<text x="{left - 8:.1f}" y="{y + 4:.1f}" font-size="12" text-anchor="end" '
            f'fill="var(--ink-2)" {_FONT}>{escape(_clip(category, 30))}</text>'
        )
        if math.isnan(v):
            continue
        if not math.isnan(lo) and not math.isnan(hi):
            body.append(
                f'<line x1="{sx(lo):.1f}" y1="{y:.1f}" x2="{sx(hi):.1f}" y2="{y:.1f}" '
                f'stroke="var(--series-1)" stroke-width="2"/>'
            )
            ci_text = f" ({_fmt(lo)} – {_fmt(hi)})"  # noqa: RUF001
        else:
            ci_text = ""
        body.append(
            f'<rect class="mark" x="{sx(v) - 5:.1f}" y="{y - 5:.1f}" width="10" height="10" '
            f'fill="var(--series-1)" stroke="var(--surface)" stroke-width="2">'
            f"<title>{escape(category)}: {_fmt(v)}{ci_text}</title></rect>"
            f'<text x="{left + plot_w + 12:.1f}" y="{y + 4:.1f}" font-size="11" fill="var(--ink-2)" '
            f"{_FONT}>{_fmt(v)}{ci_text}</text>"
        )
    return _wrap("".join(body), width, height, spec.title)


def chart_table_html(spec: ChartSpec) -> str:
    """Accessible table view of the chart data (shown in a collapsible block)."""
    head = "".join(f"<th>{escape(s.name)}</th>" for s in spec.series)
    rows = []
    for ci, category in enumerate(spec.categories):
        cells = "".join(
            f"<td>{_fmt(s.values[ci], spec.unit) if ci < len(s.values) else ''}</td>"
            for s in spec.series
        )
        rows.append(f"<tr><th scope='row'>{escape(category)}</th>{cells}</tr>")
    return f"<table class='data'><thead><tr><th></th>{head}</tr></thead><tbody>{''.join(rows)}</tbody></table>"
