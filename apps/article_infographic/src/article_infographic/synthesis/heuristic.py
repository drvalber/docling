"""Rule-based synthesizer: no model, no network, runs anywhere.

It reads like a careful skim of the paper — statistics-bearing sentences from
the results, the authors' own conclusion sentences, the limitations they name —
and never paraphrases, so nothing is hallucinated. An LLM backend produces a
richer poster; this one is the dependable baseline and the fallback.
"""

from __future__ import annotations

import re

from article_infographic.extract import split_sentences
from article_infographic.models import (
    ArticleExtraction,
    Finding,
    FlowStep,
    InfographicSpec,
    KeyNumber,
    SectionKind,
    StatTile,
    StudyDesign,
)
from article_infographic.synthesis.common import (
    format_reference,
    short_citation,
)
from article_infographic.table_charts import charts_from_tables

_LABELS = {
    "pt": {
        "sample": "Amostra",
        "p": "Significância",
        "effect": "Tamanho de efeito",
        "ci": "Intervalo de confiança",
        "pct": "Proporção-chave",
        "pages": "Páginas",
        "tables": "Tabelas",
        "figures": "Figuras",
        "flow": [
            "Pergunta",
            "Desenho",
            "Amostra",
            "Intervenção / Análise",
            "Resultados",
            "Conclusão",
        ],
        "unknown_design": "Desenho não identificado automaticamente",
        "finding": "Achado",
    },
    "en": {
        "sample": "Sample",
        "p": "Significance",
        "effect": "Effect size",
        "ci": "Confidence interval",
        "pct": "Key proportion",
        "pages": "Pages",
        "tables": "Tables",
        "figures": "Figures",
        "flow": [
            "Question",
            "Design",
            "Sample",
            "Intervention / Analysis",
            "Results",
            "Conclusion",
        ],
        "unknown_design": "Design not identified automatically",
        "finding": "Finding",
    },
}

_DESIGNS: list[tuple[re.Pattern[str], dict[str, str]]] = [
    (
        re.compile(r"meta-?analys|metanális", re.I),
        {
            "pt": "Revisão sistemática com metanálise",
            "en": "Systematic review with meta-analysis",
        },
    ),
    (
        re.compile(r"systematic review|revisão sistemática", re.I),
        {"pt": "Revisão sistemática", "en": "Systematic review"},
    ),
    (
        re.compile(r"randomi[sz]ed|randomizad|\bRCT\b", re.I),
        {"pt": "Ensaio clínico randomizado", "en": "Randomized controlled trial"},
    ),
    (
        re.compile(r"double-?blind|duplo-?cego", re.I),
        {"pt": "Ensaio duplo-cego", "en": "Double-blind trial"},
    ),
    (
        re.compile(r"open-?label|aberto", re.I),
        {"pt": "Ensaio aberto (open-label)", "en": "Open-label trial"},
    ),
    (
        re.compile(r"case-?control|caso-?controle", re.I),
        {"pt": "Estudo caso-controle", "en": "Case-control study"},
    ),
    (
        re.compile(r"prospective cohort|coorte prospectiv", re.I),
        {"pt": "Coorte prospectiva", "en": "Prospective cohort"},
    ),
    (
        re.compile(r"retrospective|retrospectiv", re.I),
        {"pt": "Estudo retrospectivo", "en": "Retrospective study"},
    ),
    (
        re.compile(r"\bcohort\b|coorte", re.I),
        {"pt": "Estudo de coorte", "en": "Cohort study"},
    ),
    (
        re.compile(r"cross-?sectional|transversal", re.I),
        {"pt": "Estudo transversal", "en": "Cross-sectional study"},
    ),
    (
        re.compile(r"case report|relato de caso|case series|série de casos", re.I),
        {"pt": "Relato / série de casos", "en": "Case report / series"},
    ),
    (
        re.compile(r"qualitative|qualitativ", re.I),
        {"pt": "Estudo qualitativo", "en": "Qualitative study"},
    ),
    (
        re.compile(r"\bdataset\b|benchmark|corpus", re.I),
        {"pt": "Estudo de dataset / benchmark", "en": "Dataset / benchmark study"},
    ),
    (
        re.compile(r"\breview\b|revisão", re.I),
        {"pt": "Revisão narrativa", "en": "Narrative review"},
    ),
]

_LIMIT = re.compile(
    r"limitation|limitaç|caveat|\bbias\b|viés|small sample|amostra pequena|generali[sz]|underpowered|not powered|confound",
    re.I,
)
_CLINICAL = re.compile(
    r"clinic|clínic|practice|prática|implication|implicaç|recommend|should|deve|may help|pode ajudar|suggest|sugere|treatment|tratamento|patients|pacientes",
    re.I,
)
_POPULATION = re.compile(
    r"participants|participantes|patients|pacientes|subjects|sujeitos|adults|adultos|children|crianças|women|men|individuals|indivíduos|documents|pages|records",
    re.I,
)
_INTERVENTION = [
    re.compile(
        r"\breceived\b|receberam|treated with|tratad[oa]s? com|administered|administrad|\bdose",
        re.I,
    ),
    re.compile(r"randomi[sz]ed to|alocad|intervention|intervenç|trained|treinad", re.I),
]
_COMPARATOR = [
    re.compile(
        r"placebo|control group|grupo[- ]controle|sham|usual care|cuidado usual|waitlist",
        re.I,
    ),
    re.compile(r"versus|\bvs\.?|compared with|comparad|baseline", re.I),
]
_OUTCOME = [
    re.compile(r"primary (?:outcome|endpoint)|desfecho primário|main outcome", re.I),
    re.compile(
        r"outcome measure|secondary outcome|desfecho secundário|measured by|avaliad[oa]s? (?:por|pel)",
        re.I,
    ),
    re.compile(r"\bscore|escala|mAP|accuracy|acurácia", re.I),
]
_FOLLOWUP = [
    re.compile(r"follow-?up|seguimento", re.I),
    re.compile(r"\d+\s*(?:weeks?|semanas?|months?|meses|years?|anos)\b", re.I),
]
_SETTING = re.compile(
    r"hospital|clinic|clínica|outpatient|ambulat|community|comunidade|university|universidade|multicent|centers?|centros?|sites?",
    re.I,
)


def _first_sentence(text: str, patterns, max_len: int = 220) -> str:
    """First sentence matching the strongest pattern; weaker patterns are fallbacks."""
    if isinstance(patterns, re.Pattern):
        patterns = [patterns]
    sentences = split_sentences(text)
    for pattern in patterns:
        for sentence in sentences:
            if pattern.search(sentence):
                return _trim(sentence, max_len)
    return ""


def _trim(sentence: str, max_len: int) -> str:
    sentence = re.sub(r"\s+", " ", sentence).strip()
    if len(sentence) <= max_len:
        return sentence
    cut = sentence[:max_len].rsplit(" ", 1)[0]
    return cut + "…"


def _sample_size(numbers: list[KeyNumber]) -> str:
    best = 0
    for num in numbers:
        if num.kind != "sample_size":
            continue
        digits = re.sub(r"[^\d]", "", num.value)
        if digits and int(digits) > best:
            best = int(digits)
    return f"n = {best:,}".replace(",", ".") if best else ""


class HeuristicSynthesizer:
    name = "heuristic"

    def synthesize(
        self, extraction: ArticleExtraction, language: str = "pt"
    ) -> InfographicSpec:
        labels = _LABELS.get(language, _LABELS["en"])
        meta = extraction.metadata
        abstract = extraction.section(SectionKind.ABSTRACT)
        methods = extraction.section(SectionKind.METHODS)
        results = extraction.section(SectionKind.RESULTS)
        discussion = extraction.section(SectionKind.DISCUSSION)
        conclusion = extraction.section(SectionKind.CONCLUSION)
        intro = extraction.section(SectionKind.INTRODUCTION)
        design_text = " ".join([abstract[:3000], methods[:3000], meta.title])

        design = labels["unknown_design"]
        for pattern, names in _DESIGNS:
            if pattern.search(design_text):
                design = names.get(language, names["en"])
                break

        sample = _sample_size(extraction.key_numbers)
        study = StudyDesign(
            design=design,
            population=_first_sentence(methods or abstract, _POPULATION),
            sample_size=sample,
            intervention=_first_sentence(methods or abstract, _INTERVENTION),
            comparator=_first_sentence(methods or abstract, _COMPARATOR),
            outcomes=_first_sentence(methods or abstract, _OUTCOME),
            follow_up=_first_sentence(methods, _FOLLOWUP, 140),
            setting=_first_sentence(methods, _SETTING, 140),
        )

        summary = ""
        for text in (conclusion, abstract):
            sentences = split_sentences(text)
            if sentences:
                summary = _trim(
                    sentences[-1] if text is abstract else sentences[0], 260
                )
                break

        findings = self._findings(extraction, labels)
        tiles = self._tiles(extraction, labels)
        flow = [
            FlowStep(
                label=labels["flow"][0],
                detail=_trim(
                    split_sentences(intro or abstract)[-1]
                    if (intro or abstract)
                    else "",
                    160,
                ),
            ),
            FlowStep(label=labels["flow"][1], detail=design),
            FlowStep(label=labels["flow"][2], detail=sample or study.population[:120]),
            FlowStep(
                label=labels["flow"][3],
                detail=study.intervention[:160] or study.outcomes[:160],
            ),
            FlowStep(
                label=labels["flow"][4],
                detail=findings[0].detail[:160] if findings else "",
            ),
            FlowStep(label=labels["flow"][5], detail=summary[:160]),
        ]
        flow = [step for step in flow if step.detail]

        takeaways = [_trim(s, 200) for s in split_sentences(conclusion)[:4]]
        if not takeaways:
            takeaways = [_trim(s, 200) for s in split_sentences(abstract)[-3:]]
        tail = split_sentences(discussion + "\n" + conclusion)
        limitations = [_trim(s, 200) for s in tail if _LIMIT.search(s)][:4]
        implications = [
            _trim(s, 200)
            for s in tail
            if _CLINICAL.search(s) and not _LIMIT.search(s) and s not in takeaways
        ][:4]

        warnings = []
        if not abstract:
            warnings.append(
                "abstract not found" if language == "en" else "resumo não localizado"
            )
        if not results:
            warnings.append(
                "results section not found"
                if language == "en"
                else "seção de resultados não localizada"
            )

        return InfographicSpec(
            language=language,
            headline=_trim(meta.title, 120) or extraction.metadata.source_file,
            subtitle=" · ".join(p for p in (design, meta.journal, meta.year) if p),
            one_sentence_summary=summary,
            reference=format_reference(meta),
            citation_short=short_citation(meta),
            metadata=meta,
            stat_tiles=tiles,
            study_design=study,
            flow=flow,
            key_findings=findings,
            charts=charts_from_tables(extraction.tables, language, limit=4),
            takeaways=takeaways,
            clinical_implications=implications,
            limitations=limitations,
            keywords=meta.keywords[:8],
            generated_by=self.name,
            warnings=warnings,
        )

    @staticmethod
    def _findings(extraction: ArticleExtraction, labels: dict) -> list[Finding]:
        findings: list[Finding] = []
        seen: set[str] = set()
        priority = {
            "p_value": 0,
            "effect_size": 1,
            "ci": 2,
            "mean_sd": 3,
            "percentage": 4,
            "sample_size": 6,
        }
        candidates = sorted(
            (
                n
                for n in extraction.key_numbers
                if n.section
                in (SectionKind.RESULTS, SectionKind.ABSTRACT, SectionKind.CONCLUSION)
            ),
            key=lambda n: (
                0 if n.section is SectionKind.RESULTS else 1,
                priority.get(n.kind, 5),
            ),
        )
        for num in candidates:
            key = num.sentence[:60]
            if key in seen:
                continue
            seen.add(key)
            words = num.sentence.split()
            title = " ".join(words[:9]) + ("…" if len(words) > 9 else "")
            findings.append(
                Finding(title=title, detail=_trim(num.sentence, 260), stat=num.value)
            )
            if len(findings) >= 5:
                break
        return findings

    @staticmethod
    def _tiles(extraction: ArticleExtraction, labels: dict) -> list[StatTile]:
        tiles: list[StatTile] = []
        sample = _sample_size(extraction.key_numbers)
        if sample:
            tiles.append(
                StatTile(value=sample.replace("n = ", ""), label=labels["sample"])
            )
        for kind, label in (
            ("p_value", labels["p"]),
            ("effect_size", labels["effect"]),
            ("ci", labels["ci"]),
            ("percentage", labels["pct"]),
        ):
            for num in extraction.key_numbers:
                if num.kind == kind and num.section is SectionKind.RESULTS:
                    tiles.append(
                        StatTile(
                            value=num.value,
                            label=label,
                            context=_trim(num.sentence, 90),
                        )
                    )
                    break
            if len(tiles) >= 4:
                break
        if len(tiles) < 3:
            meta = extraction.metadata
            if meta.page_count:
                tiles.append(
                    StatTile(value=str(meta.page_count), label=labels["pages"])
                )
            if extraction.tables:
                tiles.append(
                    StatTile(value=str(len(extraction.tables)), label=labels["tables"])
                )
            if extraction.figures:
                tiles.append(
                    StatTile(
                        value=str(len(extraction.figures)), label=labels["figures"]
                    )
                )
        return tiles[:5]
