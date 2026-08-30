"""Unit tests for statistical hypothesis tests and inferential computations."""

import pytest
import numpy as np
from src.data_loader import DataLoader
from src.statistics import StatisticalEngine


@pytest.fixture
def stats_engine():
    return StatisticalEngine(DataLoader())


def test_cohens_d_calculation(stats_engine):
    x = np.array([4.0, 4.5, 5.0, 4.0, 4.5])
    y = np.array([3.5, 4.0, 4.5, 3.5, 4.0])
    d_paired = stats_engine.calculate_cohens_d(x, y, paired=True)
    assert d_paired > 0.0


def test_bootstrap_ci(stats_engine):
    data = np.random.normal(loc=0.24, scale=0.1, size=100)
    low, high = stats_engine.bootstrap_ci(data, num_bootstrap=500)
    assert low < high
    assert low > 0.0


def test_inflation_significance_test(stats_engine):
    res = stats_engine.test_inflation_significance()
    assert res["is_statistically_significant"] is True
    assert res["p_value"] < 0.001
    assert res["t_statistic"] > 5.0
    assert res["mean_difference"] > 0.20
    assert len(res["bootstrap_95_ci"]) == 2
    assert res["bootstrap_95_ci"][0] > 0.0


def test_temporal_shift_test(stats_engine):
    res = stats_engine.test_temporal_shift_significance()
    assert "mean_2015" in res
    assert "mean_2016_17" in res
    assert res["mean_difference"] < 0.0  # 2016-17 is lower than 2015
