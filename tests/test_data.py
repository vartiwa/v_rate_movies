"""Unit tests for dataset loading and data integrity validation."""

import pytest
import pandas as pd
from src.data_loader import DataLoader
from src.config import (
    COL_FANDANGO_STARS,
    COL_FANDANGO_ACTUAL,
    COL_RT_NORM,
    COL_METACRITIC_NORM,
    COL_IMDB_NORM,
)


@pytest.fixture
def loader():
    return DataLoader()


def test_load_comparison_dataset(loader):
    df = loader.load_comparison()
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 146
    assert df.isnull().sum().sum() == 0
    assert "discrepancy" in df.columns
    assert "is_rounded_up" in df.columns


def test_load_scrape_dataset(loader):
    df = loader.load_scrape()
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 510
    assert df.isnull().sum().sum() == 0

    df_filtered = loader.load_scrape(min_votes=30)
    assert len(df_filtered) < len(df)
    assert (df_filtered["VOTES"] >= 30).all()


def test_load_after_dataset(loader):
    df = loader.load_after()
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 214
    assert df.isnull().sum().sum() == 0
    assert "fandango" in df.columns


def test_data_ranges(loader):
    df = loader.load_comparison()
    for col in [COL_FANDANGO_STARS, COL_FANDANGO_ACTUAL, COL_RT_NORM, COL_METACRITIC_NORM, COL_IMDB_NORM]:
        assert (df[col] >= 0.0).all()
        assert (df[col] <= 5.0).all()


def test_data_validation_report(loader):
    result = loader.validate_comparison_data()
    assert result.is_valid is True
    assert result.missing_values == 0
    assert result.out_of_bounds_count == 0
    assert result.row_count == 146
