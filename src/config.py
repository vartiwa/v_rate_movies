"""Configuration constants and paths for Fandango Rating Analysis."""

from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR

# CSV File paths
FILE_COMPARISON = DATA_DIR / "fandango_score_comparison.csv"
FILE_SCRAPE = DATA_DIR / "fandango_scrape.csv"
FILE_AFTER = DATA_DIR / "movie_ratings_16_17.csv"

# Rating Scale Limits
RATING_MIN = 0.0
RATING_MAX = 5.0

# 2015 Comparison Columns
COL_FILM_2015 = "FILM"
COL_FANDANGO_STARS = "Fandango_Stars"
COL_FANDANGO_ACTUAL = "Fandango_Ratingvalue"
COL_RT_NORM = "RT_norm"
COL_METACRITIC_NORM = "Metacritic_norm"
COL_IMDB_NORM = "IMDB_norm"
COL_FANDANGO_VOTES = "Fandango_votes"
COL_FANDANGO_DIFF = "Fandango_Difference"

# 2016-2017 After Columns
COL_FILM_AFTER = "movie"
COL_YEAR_AFTER = "year"
COL_FANDANGO_AFTER = "fandango"
COL_RT_AFTER_NORM = "nr_tmeter"
COL_METACRITIC_AFTER_NORM = "nr_metascore"
COL_IMDB_AFTER_NORM = "nr_imdb"

# App Server Settings
DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 8000
