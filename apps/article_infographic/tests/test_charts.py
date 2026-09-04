from article_infographic.charts import chart_table_html, render_chart
from article_infographic.models import ChartKind, ChartSeries, ChartSpec, ExtractedTable
from article_infographic.table_charts import chart_from_table, parse_number


def _table(headers, rows, caption="Table 1: Outcomes", index=1):
    return ExtractedTable(index=index, caption=caption, headers=headers, rows=rows)


def test_parse_number_handles_percent_thousands_and_decimal_comma():
    assert parse_number("58%") == 58
    assert parse_number("1,234") == 1234
    assert parse_number("12,5") == 12.5
    assert parse_number("−4.1") == -4.1  # noqa: RUF001
    assert parse_number("84-89") != parse_number("84-89")  # nan
    assert parse_number("Text") != parse_number("Text")


def test_two_arm_table_becomes_grouped_bars():
    chart = chart_from_table(
        _table(
            ["Outcome", "Sertraline", "Placebo"],
            [["Response (%)", "58", "34"], ["Remission (%)", "41", "22"]],
        )
    )
    assert chart is not None
    assert chart.kind is ChartKind.BAR
    assert chart.title == "Outcomes"
    assert [s.name for s in chart.series] == ["Sertraline", "Placebo"]
    assert chart.series[0].values == [58, 41]
    assert chart.source == "Tabela 1"


def test_baseline_and_follow_up_columns_become_dumbbell():
    chart = chart_from_table(
        _table(
            ["Group", "Baseline", "Week 12"],
            [["Sertraline", "21.4", "11.6"], ["Placebo", "21.1", "15.4"]],
        )
    )
    assert chart is not None and chart.kind is ChartKind.DUMBBELL


def test_percentages_summing_to_100_become_donut():
    chart = chart_from_table(
        _table(["Diagnosis", "%"], [["MDD", "60"], ["Bipolar", "25"], ["Other", "15"]]),
        language="en",
    )
    assert chart is not None and chart.kind is ChartKind.DONUT
    assert chart.unit == "%"


def test_effect_size_with_ci_becomes_forest_plot():
    chart = chart_from_table(
        _table(
            ["Outcome", "OR (95% CI)"],
            [["Response", "2.7 (1.6 to 4.5)"], ["Remission", "2.5 (1.5–4.2)"]],  # noqa: RUF001
        )
    )
    assert chart is not None and chart.kind is ChartKind.FOREST
    assert chart.null_value == 1.0
    assert chart.series[0].values == [2.7, 2.5]
    assert chart.series[0].lower == [1.6, 1.5]
    assert chart.series[0].upper == [4.5, 4.2]


def test_counts_and_percentages_are_not_mixed_on_one_axis():
    chart = chart_from_table(
        _table(
            ["Label", "Count", "% Train", "% Test"],
            [["A", "22524", "2.04", "1.77"], ["B", "6318", "0.6", "0.31"]],
        )
    )
    assert chart is not None
    assert [s.name for s in chart.series] == ["% Train", "% Test"]


def test_table_without_numeric_column_yields_no_chart():
    assert (
        chart_from_table(
            _table(["Class-count", "11"], [["Caption", "Text"], ["Footnote", "Text"]])
        )
        is None
    )


def test_render_chart_produces_svg_with_hover_titles_and_legend():
    spec = ChartSpec(
        kind=ChartKind.BAR,
        title="Response",
        categories=["Sertraline", "Placebo"],
        series=[
            ChartSeries(name="Week 12", values=[58, 34]),
            ChartSeries(name="Week 4", values=[30, 20]),
        ],
        unit="%",
    )
    svg = render_chart(spec)
    assert svg.startswith("<svg") and 'aria-label="Response"' in svg
    assert svg.count("<title>") == 4
    assert "Sertraline · Week 12: 58%" in svg
    assert "var(--series-2)" in svg  # second series uses the second categorical slot
    table = chart_table_html(spec)
    assert "<th>Week 12</th>" in table and "58%" in table


def test_render_chart_with_mismatched_series_lengths_does_not_fail():
    spec = ChartSpec(
        kind=ChartKind.DONUT,
        title="Share",
        categories=["A", "B", "C"],
        series=[ChartSeries(name="s", values=[50, 50])],
    )
    svg = render_chart(spec)
    assert svg.count("<path") == 2
