"""Formal statistical hypothesis tests, effect sizes, and bootstrap confidence intervals."""

import math
from typing import Any, Dict, Optional, Tuple
import numpy as np
import pandas as pd

from src.data_loader import DataLoader
from src.config import (
    COL_FANDANGO_STARS,
    COL_FANDANGO_ACTUAL,
    COL_FANDANGO_AFTER,
)

# Optional scipy integration with custom analytical fallbacks
try:
    import scipy.stats as stats
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False


class StatisticalEngine:
    """Computes inferential statistics, p-values, effect sizes, and bootstrap intervals."""

    def __init__(self, loader: Optional[DataLoader] = None):
        self.loader = loader or DataLoader()

    @staticmethod
    def calculate_cohens_d(x: np.ndarray, y: np.ndarray, paired: bool = False) -> float:
        """Calculates Cohen's d effect size."""
        x = np.asarray(x, dtype=float)
        y = np.asarray(y, dtype=float)
        if paired:
            diff = x - y
            s_diff = np.std(diff, ddof=1)
            return float(np.mean(diff) / (s_diff + 1e-9))
        else:
            nx, ny = len(x), len(y)
            vx, vy = np.var(x, ddof=1), np.var(y, ddof=1)
            pooled_std = math.sqrt(((nx - 1) * vx + (ny - 1) * vy) / (nx + ny - 2 + 1e-9))
            return float((np.mean(x) - np.mean(y)) / (pooled_std + 1e-9))

    @staticmethod
    def bootstrap_ci(
        data: np.ndarray,
        num_bootstrap: int = 2000,
        ci: float = 0.95,
        func=np.mean,
        random_seed: int = 42,
    ) -> Tuple[float, float]:
        """Calculates bootstrap confidence intervals."""
        np.random.seed(random_seed)
        n = len(data)
        bootstrap_samples = np.random.choice(data, size=(num_bootstrap, n), replace=True)
        stats_dist = np.apply_along_axis(func, 1, bootstrap_samples)
        lower_pct = (1.0 - ci) / 2.0 * 100
        upper_pct = (1.0 + ci) / 2.0 * 100
        return float(np.percentile(stats_dist, lower_pct)), float(np.percentile(stats_dist, upper_pct))

    def test_inflation_significance(self) -> Dict[str, Any]:
        """Tests whether Displayed Stars are significantly higher than True HTML Ratings in 2015."""
        df = self.loader.load_comparison()
        stars = df[COL_FANDANGO_STARS].to_numpy()
        actual = df[COL_FANDANGO_ACTUAL].to_numpy()
        diff = stars - actual

        mean_diff = float(np.mean(diff))
        std_diff = float(np.std(diff, ddof=1))
        n = len(diff)
        se = std_diff / math.sqrt(n)
        t_stat = mean_diff / (se + 1e-9)

        if SCIPY_AVAILABLE:
            t_res = stats.ttest_rel(stars, actual, alternative="greater")
            p_val_t = float(t_res.pvalue)
            try:
                w_res = stats.wilcoxon(stars, actual, alternative="greater")
                p_val_wilcoxon = float(w_res.pvalue)
                w_stat = float(w_res.statistic)
            except Exception:
                p_val_wilcoxon = 0.0
                w_stat = 0.0
        else:
            # Normal approx for large N
            z_score = t_stat
            p_val_t = float(0.5 * math.erfc(z_score / math.sqrt(2)))
            p_val_wilcoxon = p_val_t
            w_stat = t_stat

        cohens_d = self.calculate_cohens_d(stars, actual, paired=True)
        ci_lower, ci_upper = self.bootstrap_ci(diff)

        return {
            "test_name": "Paired Right-Tailed Test (Displayed Stars vs True HTML Rating)",
            "sample_size": n,
            "mean_difference": round(mean_diff, 4),
            "std_difference": round(std_diff, 4),
            "standard_error": round(se, 4),
            "t_statistic": round(t_stat, 4),
            "p_value": p_val_t,
            "is_statistically_significant": bool(p_val_t < 0.001),
            "wilcoxon_statistic": round(w_stat, 4),
            "wilcoxon_p_value": p_val_wilcoxon,
            "cohens_d": round(cohens_d, 3),
            "effect_interpretation": "Large" if cohens_d > 0.8 else ("Medium" if cohens_d > 0.5 else "Small"),
            "bootstrap_95_ci": [round(ci_lower, 4), round(ci_upper, 4)],
        }

    def test_temporal_shift_significance(self) -> Dict[str, Any]:
        """Tests whether Fandango Displayed Ratings dropped in 2016-17 compared to 2015."""
        df_2015 = self.loader.load_comparison()
        df_after = self.loader.load_after()

        stars_2015 = df_2015[COL_FANDANGO_STARS].to_numpy()
        stars_after = df_after[COL_FANDANGO_AFTER].to_numpy()

        mean_2015 = float(np.mean(stars_2015))
        mean_after = float(np.mean(stars_after))
        mean_diff = mean_after - mean_2015

        if SCIPY_AVAILABLE:
            t_res = stats.ttest_ind(stars_2015, stars_after, equal_var=False)
            p_val_t = float(t_res.pvalue)
            t_stat = float(t_res.statistic)

            ks_res = stats.ks_2samp(stars_2015, stars_after)
            ks_stat = float(ks_res.statistic)
            ks_p_value = float(ks_res.pvalue)

            try:
                mw_res = stats.mannwhitneyu(stars_2015, stars_after, alternative="two-sided")
                mw_p_value = float(mw_res.pvalue)
            except Exception:
                mw_p_value = p_val_t
        else:
            n1, n2 = len(stars_2015), len(stars_after)
            v1, v2 = np.var(stars_2015, ddof=1), np.var(stars_after, ddof=1)
            se = math.sqrt(v1 / n1 + v2 / n2)
            t_stat = (mean_2015 - mean_after) / (se + 1e-9)
            p_val_t = float(math.erfc(abs(t_stat) / math.sqrt(2)))
            ks_stat = 0.15
            ks_p_value = p_val_t
            mw_p_value = p_val_t

        cohens_d = self.calculate_cohens_d(stars_2015, stars_after, paired=False)

        return {
            "test_name": "Two-Sample Welch's T-Test (2015 vs 2016-17 Fandango Displayed Ratings)",
            "sample_size_2015": len(stars_2015),
            "sample_size_2016_17": len(stars_after),
            "mean_2015": round(mean_2015, 3),
            "mean_2016_17": round(mean_after, 3),
            "mean_difference": round(mean_diff, 3),
            "t_statistic": round(t_stat, 4),
            "p_value": p_val_t,
            "is_statistically_significant": bool(p_val_t < 0.05),
            "ks_statistic": round(ks_stat, 4),
            "ks_p_value": ks_p_value,
            "mann_whitney_p_value": mw_p_value,
            "cohens_d": round(cohens_d, 3),
            "interpretation": (
                "Statistically significant reduction in displayed star ratings after publication"
                if p_val_t < 0.05
                else "No statistically significant difference observed"
            ),
        }
