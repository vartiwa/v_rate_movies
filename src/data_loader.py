"""Data loading, cleaning, and validation module."""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional, Tuple
import pandas as pd
import numpy as np

from src.config import (
    FILE_COMPARISON,
    FILE_SCRAPE,
    FILE_AFTER,
    RATING_MIN,
    RATING_MAX,
    COL_FANDANGO_STARS,
    COL_FANDANGO_ACTUAL,
    COL_RT_NORM,
    COL_METACRITIC_NORM,
    COL_IMDB_NORM,
)


@dataclass
class DatasetValidationResult:
    is_valid: bool
    row_count: int
    column_count: int
    missing_values: int
    out_of_bounds_count: int
    details: Dict[str, str]


class DataLoader:
    """Handles loading, validating, and caching Fandango and platform rating datasets."""

    def __init__(
        self,
        comparison_path: Optional[Path] = None,
        scrape_path: Optional[Path] = None,
        after_path: Optional[Path] = None,
    ):
        self.comparison_path = comparison_path or FILE_COMPARISON
        self.scrape_path = scrape_path or FILE_SCRAPE
        self.after_path = after_path or FILE_AFTER

        self._df_comparison: Optional[pd.DataFrame] = None
        self._df_scrape: Optional[pd.DataFrame] = None
        self._df_after: Optional[pd.DataFrame] = None

    def load_comparison(self, force_reload: bool = False) -> pd.DataFrame:
        """Load and clean 2015 Fandango score comparison dataset."""
        if self._df_comparison is not None and not force_reload:
            return self._df_comparison

        df = pd.read_csv(self.comparison_path)

        # Derived metrics
        df["discrepancy"] = (df[COL_FANDANGO_STARS] - df[COL_FANDANGO_ACTUAL]).round(2)
        df["is_rounded_up"] = df[COL_FANDANGO_STARS] > df[COL_FANDANGO_ACTUAL]
        df["year"] = df["FILM"].str.extract(r"\((\d{4})\)").astype(float)

        self._df_comparison = df
        return self._df_comparison

    def load_scrape(self, min_votes: int = 0, force_reload: bool = False) -> pd.DataFrame:
        """Load and clean Fandango scraped HTML ratings dataset."""
        if self._df_scrape is not None and not force_reload:
            df = self._df_scrape
        else:
            df = pd.read_csv(self.scrape_path)
            df["discrepancy"] = (df["STARS"] - df["RATING"]).round(2)
            df["is_rounded_up"] = df["STARS"] > df["RATING"]
            extracted_years = df["FILM"].str.extract(r"\((\d{4})\)")[0]
            df["year"] = pd.to_numeric(extracted_years, errors="coerce").fillna(2015).astype(int)
            self._df_scrape = df

        if min_votes > 0:
            return df[df["VOTES"] >= min_votes].copy()
        return df

    def load_after(self, force_reload: bool = False) -> pd.DataFrame:
        """Load and clean 2016-2017 post-article movie ratings dataset."""
        if self._df_after is not None and not force_reload:
            return self._df_after

        df = pd.read_csv(self.after_path)
        self._df_after = df
        return self._df_after

    def validate_comparison_data(self) -> DatasetValidationResult:
        """Perform comprehensive data validation checks on comparison dataset."""
        df = self.load_comparison()
        missing = int(df.isnull().sum().sum())

        # Check rating ranges for normalized columns
        norm_cols = [
            COL_FANDANGO_STARS,
            COL_FANDANGO_ACTUAL,
            COL_RT_NORM,
            COL_METACRITIC_NORM,
            COL_IMDB_NORM,
        ]
        out_of_bounds = 0
        for col in norm_cols:
            out_of_bounds += int(((df[col] < RATING_MIN) | (df[col] > RATING_MAX)).sum())

        details = {
            "comparison_rows": str(len(df)),
            "comparison_cols": str(df.shape[1]),
            "min_stars": str(df[COL_FANDANGO_STARS].min()),
            "max_stars": str(df[COL_FANDANGO_STARS].max()),
        }

        is_valid = (missing == 0) and (out_of_bounds == 0)
        return DatasetValidationResult(
            is_valid=is_valid,
            row_count=len(df),
            column_count=df.shape[1],
            missing_values=missing,
            out_of_bounds_count=out_of_bounds,
            details=details,
        )

    def get_all_datasets(self) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Convenience method to load all 3 datasets at once."""
        return self.load_comparison(), self.load_scrape(), self.load_after()
