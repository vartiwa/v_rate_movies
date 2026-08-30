"""SQLite database manager and interactive SQL query runner."""

import sqlite3
from typing import Any, Dict, List, Optional
import pandas as pd

from src.data_loader import DataLoader


class DatabaseManager:
    """Manages SQLite database tables for querying movie rating datasets."""

    def __init__(self, loader: Optional[DataLoader] = None):
        self.loader = loader or DataLoader()
        self._conn: Optional[sqlite3.Connection] = None
        self._initialize_db()

    def _initialize_db(self) -> None:
        """Loads all CSV datasets into in-memory SQLite tables."""
        self._conn = sqlite3.connect(":memory:", check_same_thread=False)
        df_comp = self.loader.load_comparison()
        df_scrape = self.loader.load_scrape()
        df_after = self.loader.load_after()

        df_comp.to_sql("fandango_2015", self._conn, index=False, if_exists="replace")
        df_scrape.to_sql("fandango_scrape", self._conn, index=False, if_exists="replace")
        df_after.to_sql("movie_ratings_16_17", self._conn, index=False, if_exists="replace")

    def execute_query(self, query: str, limit: int = 100) -> Dict[str, Any]:
        """Executes a SELECT query safely against the SQLite database."""
        query_stripped = query.strip()
        if not query_stripped.upper().startswith("SELECT") and not query_stripped.upper().startswith("WITH"):
            return {
                "success": False,
                "error": "Only SELECT or WITH queries are permitted in the analytics console.",
                "columns": [],
                "rows": [],
                "row_count": 0,
            }

        try:
            df = pd.read_sql(query_stripped, self._conn)
            if len(df) > limit:
                df = df.head(limit)
            return {
                "success": True,
                "error": None,
                "columns": df.columns.tolist(),
                "rows": df.to_dict(orient="records"),
                "row_count": len(df),
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "columns": [],
                "rows": [],
                "row_count": 0,
            }

    @staticmethod
    def get_preset_queries() -> List[Dict[str, str]]:
        """Returns standard preloaded analyst queries."""
        return [
            {
                "id": "q1_avg_diff",
                "title": "Q1: Average Displayed Stars vs True Rating",
                "query": """SELECT
    ROUND(AVG(Fandango_Stars), 2) AS avg_displayed_stars,
    ROUND(AVG(Fandango_Ratingvalue), 2) AS avg_true_rating,
    ROUND(AVG(Fandango_Stars - Fandango_Ratingvalue), 2) AS avg_inflation_delta
FROM fandango_2015;""",
            },
            {
                "id": "q2_rounded_up_count",
                "title": "Q2: Count and % of Films Rounded Up",
                "query": """SELECT
    COUNT(*) AS total_films,
    SUM(CASE WHEN Fandango_Stars > Fandango_Ratingvalue THEN 1 ELSE 0 END) AS films_rounded_up,
    ROUND(100.0 * SUM(CASE WHEN Fandango_Stars > Fandango_Ratingvalue THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_rounded_up
FROM fandango_2015;""",
            },
            {
                "id": "q3_platform_comparison",
                "title": "Q3: Cross-Platform Average Ratings (Normalized 0-5)",
                "query": """SELECT
    ROUND(AVG(Fandango_Stars), 2) AS avg_fandango_stars,
    ROUND(AVG(Fandango_Ratingvalue), 2) AS avg_fandango_true,
    ROUND(AVG(RT_norm), 2) AS avg_rotten_tomatoes,
    ROUND(AVG(Metacritic_norm), 2) AS avg_metacritic,
    ROUND(AVG(IMDB_norm), 2) AS avg_imdb
FROM fandango_2015;""",
            },
            {
                "id": "q4_top_inflated_films",
                "title": "Q4: Top 10 Most Inflated Films in 2015",
                "query": """SELECT
    FILM,
    Fandango_Stars,
    Fandango_Ratingvalue,
    ROUND(Fandango_Stars - Fandango_Ratingvalue, 2) AS difference,
    RT_norm,
    Metacritic_norm,
    IMDB_norm
FROM fandango_2015
ORDER BY difference DESC, Fandango_votes DESC
LIMIT 10;""",
            },
            {
                "id": "q5_temporal_comparison",
                "title": "Q5: Average Fandango Rating 2015 vs 2016-17",
                "query": """SELECT
    '2015 (Pre-Article)' AS period,
    ROUND(AVG(Fandango_Stars), 2) AS avg_fandango_stars
FROM fandango_2015
UNION ALL
SELECT
    '2016-2017 (Post-Article)' AS period,
    ROUND(AVG(fandango), 2) AS avg_fandango_stars
FROM movie_ratings_16_17;""",
            },
        ]
