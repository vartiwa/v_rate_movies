"""Web app configuration settings."""

from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = APP_DIR / "templates"
STATIC_DIR = APP_DIR / "static"

APP_TITLE = "Fandango Movie Ratings Audit & Analytics"
APP_VERSION = "1.0.0"
