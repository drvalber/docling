import json
from pathlib import Path

from _paths import TRIAL
from article_infographic.cli import main
from article_infographic.models import ChartKind, InfographicSpec
from article_infographic.pipeline import build_infographic, render_from_spec


def test_heuristic_build_from_markdown_trial(tmp_path):
    result = build_infographic(TRIAL, tmp_path, backend="heuristic", language="pt")
    spec = result.spec
    assert spec.study_design.design == "Ensaio clínico randomizado"
    assert spec.study_design.sample_size == "n = 312"
    assert spec.study_design.intervention.startswith(
        "Patients received sertraline 50 mg"
    )
    assert spec.study_design.outcomes.startswith("The primary outcome")
    assert spec.study_design.follow_up.startswith("Follow-up visits")
    assert spec.one_sentence_summary.startswith("Sertraline is superior to placebo")
    assert spec.reference.startswith("Ana Beatriz Moreira, Carlos Eduardo Lima")
    assert spec.reference.endswith("doi:10.1016/j.jad.2024.00001")
    assert spec.citation_short == "Moreira et al. (2024)"
    assert [t.label for t in spec.stat_tiles][:2] == ["Amostra", "Significância"]
    assert spec.stat_tiles[0].value == "312"
    assert spec.key_findings and spec.key_findings[0].stat == "p < 0.001"
    assert {c.kind for c in spec.charts} == {
        ChartKind.BAR,
        ChartKind.DUMBBELL,
        ChartKind.FOREST,
    }
    assert any("dementia" in lim for lim in spec.limitations)
    assert all("Limitations include" not in item for item in spec.clinical_implications)

    html = result.html_path.read_text(encoding="utf-8")
    assert "<svg" in html and "doi.org/10.1016/j.jad.2024.00001" in html
    assert "Em uma frase" in html
    saved = InfographicSpec.model_validate(
        json.loads(result.spec_path.read_text(encoding="utf-8"))
    )
    assert saved.headline == spec.headline


def test_cli_build_and_render_round_trip(tmp_path, capsys):
    assert (
        main(
            [
                "build",
                str(TRIAL),
                "-o",
                str(tmp_path),
                "--lang",
                "en",
                "--no-extraction",
            ]
        )
        == 0
    )
    out = capsys.readouterr().out
    assert "HTML :" in out and "Extr.:" not in out
    spec_path = tmp_path / "sertraline_trial.infographic.json"
    data = json.loads(spec_path.read_text(encoding="utf-8"))
    assert data["study_design"]["design"] == "Randomized controlled trial"

    # Edit the spec by hand and re-render it.
    data["headline"] = "Edited headline"
    spec_path.write_text(json.dumps(data), encoding="utf-8")
    edited = render_from_spec(spec_path, tmp_path / "edited.html")
    html = edited.read_text(encoding="utf-8")
    assert "<title>Edited headline</title>" in html and "In one sentence" in html
