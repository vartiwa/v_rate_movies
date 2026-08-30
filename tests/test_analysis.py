"""Unit tests for analytical computations and aggregations."""

import pytest
from src.data_loader import DataLoader
from src.analysis import RatingAnalyzer


@pytest.fixture
def analyzer():
    return RatingAnalyzer(DataLoader())


def test_kpi_overview_values(analyzer):
    kpis = analyzer.get_kpi_overview()
    assert kpis["total_2015_movies"] == 146
    assert kpis["avg_displayed_stars_2015"] == pytest.approx(4.09, abs=0.01)
    assert kpis["avg_actual_rating_2015"] == pytest.approx(3.85, abs=0.01)
    assert kpis["avg_inflation_delta"] == pytest.approx(0.24, abs=0.01)
    assert kpis["rounded_up_count_2015"] == 130
    assert kpis["rounded_up_pct_2015"] == pytest.approx(89.0, abs=0.1)
    assert kpis["avg_displayed_stars_2016_17"] == pytest.approx(3.89, abs=0.01)


def test_discrepancy_distribution(analyzer):
    dist = analyzer.get_discrepancy_distribution()
    assert dist["max_discrepancy"] == 0.5
    assert dist["min_discrepancy"] == 0.0
    assert len(dist["breakdown"]) == 6  # 0.0, 0.1, 0.2, 0.3, 0.4, 0.5
    total_pct = sum(item["percentage"] for item in dist["breakdown"])
    assert 99.0 <= total_pct <= 101.0


def test_platform_comparison(analyzer):
    comp = analyzer.get_platform_comparison()
    summary = {row["platform"]: row for row in comp["summary_table"]}

    assert "Fandango (Displayed)" in summary
    assert "Fandango (Actual HTML)" in summary
    assert "Rotten Tomatoes (Norm)" in summary
    assert "Metacritic (Norm)" in summary
    assert "IMDB (Norm)" in summary

    # Fandango Displayed is highest
    fandango_mean = summary["Fandango (Displayed)"]["mean"]
    rt_mean = summary["Rotten Tomatoes (Norm)"]["mean"]
    meta_mean = summary["Metacritic (Norm)"]["mean"]
    imdb_mean = summary["IMDB (Norm)"]["mean"]

    assert fandango_mean > rt_mean
    assert fandango_mean > meta_mean
    assert fandango_mean > imdb_mean


def test_temporal_comparison(analyzer):
    temporal = analyzer.get_temporal_comparison()
    metrics = temporal["metrics"]
    assert metrics["2015_displayed_mean"] > metrics["2016_17_displayed_mean"]
    assert len(temporal["bins"]) == len(temporal["counts_2015_displayed"])


def test_search_movies(analyzer):
    results = analyzer.search_movies(query="Avengers")
    assert len(results) >= 1
    assert "Avengers" in results[0]["film"]

    filtered = analyzer.search_movies(min_discrepancy=0.5)
    assert len(filtered) == 13
    for m in filtered:
        assert m["discrepancy"] == 0.5
