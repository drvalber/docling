"""Render an ``InfographicSpec`` into a self-contained HTML poster."""

from __future__ import annotations

import datetime as dt
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from article_infographic.charts import chart_table_html, render_chart
from article_infographic.models import InfographicSpec

_TEMPLATE_DIR = Path(__file__).parent / "templates"

_UI = {
    "pt": {
        "in_one_sentence": "Em uma frase",
        "design": "Desenho do estudo",
        "population": "População",
        "sample": "Amostra",
        "intervention": "Intervenção / Exposição",
        "comparator": "Comparador",
        "outcomes": "Desfechos",
        "follow_up": "Seguimento",
        "setting": "Contexto",
        "flow": "Fluxo do estudo",
        "mechanism": "Mecanismo / conceito central",
        "findings": "Principais achados",
        "charts": "Dados em gráficos",
        "data_table": "Ver dados",
        "takeaways": "Mensagens para levar",
        "clinical": "Implicações clínicas",
        "limitations": "Limitações",
        "glossary": "Glossário",
        "reference": "Referência",
        "keywords": "Palavras-chave",
        "source": "Fonte",
        "generated": "Infográfico gerado automaticamente em",
        "backend": "síntese",
        "disclaimer": "Resumo automatizado para apoio ao estudo. Confira os valores no artigo original antes de citar ou aplicar clinicamente.",
        "print": "Imprimir / PDF",
        "theme": "Tema",
        "warnings": "Avisos",
        "authors": "Autores",
        "pages": "páginas",
    },
    "en": {
        "in_one_sentence": "In one sentence",
        "design": "Study design",
        "population": "Population",
        "sample": "Sample",
        "intervention": "Intervention / Exposure",
        "comparator": "Comparator",
        "outcomes": "Outcomes",
        "follow_up": "Follow-up",
        "setting": "Setting",
        "flow": "Study flow",
        "mechanism": "Mechanism / central concept",
        "findings": "Key findings",
        "charts": "Data in charts",
        "data_table": "Show data",
        "takeaways": "Take-home messages",
        "clinical": "Clinical implications",
        "limitations": "Limitations",
        "glossary": "Glossary",
        "reference": "Reference",
        "keywords": "Keywords",
        "source": "Source",
        "generated": "Infographic generated automatically on",
        "backend": "synthesis",
        "disclaimer": "Automated summary for study support. Check every value against the original article before citing or applying it clinically.",
        "print": "Print / PDF",
        "theme": "Theme",
        "warnings": "Warnings",
        "authors": "Authors",
        "pages": "pages",
    },
}


def _environment() -> Environment:
    env = Environment(
        loader=FileSystemLoader(_TEMPLATE_DIR),
        autoescape=select_autoescape(["html", "j2"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    return env


def render_html(spec: InfographicSpec) -> str:
    env = _environment()
    template = env.get_template("infographic.html.j2")
    ui = _UI.get(spec.language, _UI["en"])
    charts = []
    for chart in spec.charts:
        svg = render_chart(chart)
        if not svg:
            continue
        charts.append({"spec": chart, "svg": svg, "table": chart_table_html(chart)})
    design = spec.study_design
    pico = [
        (ui["design"], design.design),
        (ui["population"], design.population),
        (ui["sample"], design.sample_size),
        (ui["intervention"], design.intervention),
        (ui["comparator"], design.comparator),
        (ui["outcomes"], design.outcomes),
        (ui["follow_up"], design.follow_up),
        (ui["setting"], design.setting),
    ]
    seen: set[str] = set()
    deduped = []
    for label, value in pico:
        if value and value not in seen:
            seen.add(value)
            deduped.append((label, value))
    pico = deduped
    return template.render(
        spec=spec,
        ui=ui,
        charts=charts,
        pico=pico,
        generated_at=dt.datetime.now().strftime("%Y-%m-%d %H:%M"),
        doi_url=f"https://doi.org/{spec.metadata.doi}" if spec.metadata.doi else "",
    )


def write_html(spec: InfographicSpec, output: Path) -> Path:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render_html(spec), encoding="utf-8")
    return output
