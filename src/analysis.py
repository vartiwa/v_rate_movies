"""Analytical routines and aggregation engine for movie rating comparisons."""

from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd

from src.data_loader import DataLoader
from src.config import (
    COL_FANDANGO_STARS,
    COL_FANDANGO_ACTUAL,
    COL_RT_NORM,
    COL_METACRITIC_NORM,
    COL_IMDB_NORM,
    COL_FANDANGO_VOTES,
    COL_FANDANGO_AFTER,
    COL_RT_AFTER_NORM,
    COL_METACRITIC_AFTER_NORM,
    COL_IMDB_AFTER_NORM,
)


class RatingAnalyzer:
    """Performs aggregations, distribution calculations, and comparative analytics."""

    def __init__(self, loader: Optional[DataLoader] = None):
        self.loader = loader or DataLoader()

    def get_kpi_overview(self) -> Dict[str, Any]:
        """Calculates executive high-level metrics for dashboard cards."""
        df_comp = self.loader.load_comparison()
        df_scrape = self.loader.load_scrape(min_votes=30)
        df_after = self.loader.load_after()

        # 2015 Comparison stats
        avg_stars = float(df_comp[COL_FANDANGO_STARS].mean())
        avg_actual = float(df_comp[COL_FANDANGO_ACTUAL].mean())
        avg_diff = float((df_comp[COL_FANDANGO_STARS] - df_comp[COL_FANDANGO_ACTUAL]).mean())
        rounded_up_count = int((df_comp[COL_FANDANGO_STARS] > df_comp[COL_FANDANGO_ACTUAL]).sum())
        total_comp = len(df_comp)
        rounded_up_pct = round((rounded_up_count / total_comp) * 100, 1)

        # 2016-2017 stats
        avg_after_stars = float(df_after[COL_FANDANGO_AFTER].mean())
        temporal_change = round(avg_after_stars - avg_stars, 3)

        # Scrape stats (min 30 votes)
        scrape_rounded_pct = round(
            float((df_scrape["STARS"] > df_scrape["RATING"]).sum() / len(df_scrape) * 100), 1
        ) if len(df_scrape) > 0 else 0.0

        # Top critic disparities (Fandango Stars vs RT Norm)
        df_comp["rt_gap"] = (df_comp[COL_FANDANGO_STARS] - df_comp[COL_RT_NORM]).round(2)
        top_gaps = df_comp.sort_values(by="rt_gap", ascending=False).head(6)
        disparities = [
            {
                "film": row["FILM"],
                "fandango_stars": float(row[COL_FANDANGO_STARS]),
                "fandango_actual": float(row[COL_FANDANGO_ACTUAL]),
                "rt_raw": int(row["RottenTomatoes"]),
                "rt_norm": float(row[COL_RT_NORM]),
                "gap": float(row["rt_gap"]),
                "votes": int(row[COL_FANDANGO_VOTES]),
            }
            for _, row in top_gaps.iterrows()
        ]

        return {
            "total_2015_movies": total_comp,
            "avg_displayed_stars_2015": round(avg_stars, 3),
            "avg_actual_rating_2015": round(avg_actual, 3),
            "avg_inflation_delta": round(avg_diff, 3),
            "rounded_up_count_2015": rounded_up_count,
            "rounded_up_pct_2015": rounded_up_pct,
            "total_scrape_movies": len(df_scrape),
            "scrape_rounded_pct": scrape_rounded_pct,
            "total_2016_17_movies": len(df_after),
            "avg_displayed_stars_2016_17": round(avg_after_stars, 3),
            "temporal_change": temporal_change,
            "top_disparities": disparities,
        }

    def get_discrepancy_distribution(self) -> Dict[str, Any]:
        """Calculates frequency table and distribution of (Stars - Actual Rating)."""
        df_comp = self.loader.load_comparison()
        diffs = (df_comp[COL_FANDANGO_STARS] - df_comp[COL_FANDANGO_ACTUAL]).round(2)
        counts = diffs.value_counts().sort_index()

        breakdown = [
            {"difference": float(diff), "count": int(count), "percentage": round(count / len(df_comp) * 100, 1)}
            for diff, count in counts.items()
        ]

        return {
            "breakdown": breakdown,
            "max_discrepancy": float(diffs.max()),
            "min_discrepancy": float(diffs.min()),
            "median_discrepancy": float(diffs.median()),
            "mean_discrepancy": round(float(diffs.mean()), 3),
        }

    def get_platform_comparison(self) -> Dict[str, Any]:
        """Compares Fandango against Rotten Tomatoes, Metacritic, and IMDB with smooth KDE density."""
        df = self.loader.load_comparison()

        platforms = [
            ("Fandango (Displayed)", df[COL_FANDANGO_STARS]),
            ("Fandango (Actual HTML)", df[COL_FANDANGO_ACTUAL]),
            ("Rotten Tomatoes (Norm)", df[COL_RT_NORM]),
            ("Metacritic (Norm)", df[COL_METACRITIC_NORM]),
            ("IMDB (Norm)", df[COL_IMDB_NORM]),
        ]

        summary_table = []
        for name, series in platforms:
            summary_table.append({
                "platform": name,
                "mean": round(float(series.mean()), 3),
                "median": round(float(series.median()), 3),
                "std": round(float(series.std()), 3),
                "min": round(float(series.min()), 2),
                "max": round(float(series.max()), 2),
                "q25": round(float(series.quantile(0.25)), 2),
                "q75": round(float(series.quantile(0.75)), 2),
            })

        # Distribution histograms (binned 0 to 5 in steps of 0.5)
        bins = np.arange(0.0, 5.5, 0.5)
        bin_labels = [f"{b:.1f}-{b+0.5:.1f}" for b in bins[:-1]]

        hist_data = {"bins": bin_labels}
        for name, series in platforms:
            counts, _ = np.histogram(series, bins=bins)
            hist_data[name] = counts.tolist()

        # Smooth KDE curve points (0.0 to 5.0 in 100 evaluation points)
        eval_x = np.linspace(0.0, 5.0, 101)
        kde_curves = {"x": [round(float(x), 2) for x in eval_x]}
        for name, series in platforms:
            data_pts = series.dropna().to_numpy()
            if len(data_pts) > 1:
                # Kernel density estimation
                std = np.std(data_pts, ddof=1)
                bw = 1.06 * std * (len(data_pts) ** -0.2) if std > 0 else 0.3
                bw = max(bw, 0.15)
                # Compute gaussian kernel density manually / robustly
                u = (eval_x[:, None] - data_pts[None, :]) / bw
                dens = np.sum(np.exp(-0.5 * u**2) / (np.sqrt(2 * np.pi) * bw), axis=1) / len(data_pts)
                kde_curves[name] = [round(float(d), 4) for d in dens]
            else:
                kde_curves[name] = [0.0] * len(eval_x)

        return {
            "summary_table": summary_table,
            "histograms": hist_data,
            "kde_curves": kde_curves,
        }

    def get_temporal_comparison(self) -> Dict[str, Any]:
        """Compares 2015 ratings against 2016-2017 post-article ratings with smooth KDE curves."""
        df_2015 = self.loader.load_comparison()
        df_after = self.loader.load_after()

        series_2015_stars = df_2015[COL_FANDANGO_STARS]
        series_2015_actual = df_2015[COL_FANDANGO_ACTUAL]
        series_after_stars = df_after[COL_FANDANGO_AFTER]

        bins = np.arange(0.0, 5.5, 0.5)
        bin_labels = [f"{b:.1f}-{b+0.5:.1f}" for b in bins[:-1]]

        c_2015_stars, _ = np.histogram(series_2015_stars, bins=bins)
        c_2015_actual, _ = np.histogram(series_2015_actual, bins=bins)
        c_after_stars, _ = np.histogram(series_after_stars, bins=bins)

        # Smooth KDE curves
        eval_x = np.linspace(0.0, 5.0, 101)
        def compute_kde(s):
            pts = s.dropna().to_numpy()
            std = np.std(pts, ddof=1)
            bw = max(1.06 * std * (len(pts) ** -0.2), 0.15) if std > 0 else 0.3
            u = (eval_x[:, None] - pts[None, :]) / bw
            return [round(float(d), 4) for d in np.sum(np.exp(-0.5 * u**2) / (np.sqrt(2 * np.pi) * bw), axis=1) / len(pts)]

        return {
            "bins": bin_labels,
            "counts_2015_displayed": c_2015_stars.tolist(),
            "counts_2015_actual": c_2015_actual.tolist(),
            "counts_2016_17_displayed": c_after_stars.tolist(),
            "kde_curves": {
                "x": [round(float(x), 2) for x in eval_x],
                "kde_2015_displayed": compute_kde(series_2015_stars),
                "kde_2015_actual": compute_kde(series_2015_actual),
                "kde_2016_17_displayed": compute_kde(series_after_stars),
            },
            "metrics": {
                "2015_displayed_mean": round(float(series_2015_stars.mean()), 3),
                "2015_actual_mean": round(float(series_2015_actual.mean()), 3),
                "2016_17_displayed_mean": round(float(series_after_stars.mean()), 3),
                "displayed_drop": round(float(series_after_stars.mean() - series_2015_stars.mean()), 3),
                "actual_vs_after_delta": round(float(series_after_stars.mean() - series_2015_actual.mean()), 3),
            },
        }

    def search_movies(
        self,
        query: str = "",
        min_stars: float = 0.0,
        max_stars: float = 5.0,
        min_discrepancy: float = 0.0,
        sort_by: str = "discrepancy",
        ascending: bool = False,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Search and filter the 2015 movie comparison dataset."""
        df = self.loader.load_comparison().copy()

        if query:
            df = df[df["FILM"].str.contains(query, case=False, na=False)]

        df = df[
            (df[COL_FANDANGO_STARS] >= min_stars)
            & (df[COL_FANDANGO_STARS] <= max_stars)
            & (df["discrepancy"] >= min_discrepancy)
        ]

        if sort_by in df.columns:
            df = df.sort_values(by=sort_by, ascending=ascending)

        df_subset = df.head(limit)

        records = []
        for _, row in df_subset.iterrows():
            records.append({
                "film": row["FILM"],
                "fandango_stars": float(row[COL_FANDANGO_STARS]),
                "fandango_actual": float(row[COL_FANDANGO_ACTUAL]),
                "discrepancy": float(row["discrepancy"]),
                "rt_norm": float(row[COL_RT_NORM]),
                "metacritic_norm": float(row[COL_METACRITIC_NORM]),
                "imdb_norm": float(row[COL_IMDB_NORM]),
                "votes": int(row[COL_FANDANGO_VOTES]),
            })

        return records
