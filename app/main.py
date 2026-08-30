"""FastAPI Application Server for Fandango Rating Analytics."""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from src.config import DEFAULT_HOST, DEFAULT_PORT
from src.data_loader import DataLoader
from src.analysis import RatingAnalyzer
from src.statistics import StatisticalEngine
from src.database import DatabaseManager
from app.config import TEMPLATES_DIR, STATIC_DIR, APP_TITLE, APP_VERSION

app = FastAPI(
    title=APP_TITLE,
    version=APP_VERSION,
    description="Interactive data analytics platform investigating Fandango movie rating bias and post-article shifts.",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
os.makedirs(STATIC_DIR / "css", exist_ok=True)
os.makedirs(STATIC_DIR / "js", exist_ok=True)
os.makedirs(TEMPLATES_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Instantiate singletons
loader = DataLoader()
analyzer = RatingAnalyzer(loader)
stats_engine = StatisticalEngine(loader)
db_manager = DatabaseManager(loader)


class SQLRequest(BaseModel):
    query: str
    limit: Optional[int] = 100


@app.get("/", response_class=HTMLResponse)
async def serve_index():
    """Serves the interactive web application dashboard."""
    index_file = TEMPLATES_DIR / "index.html"
    if not index_file.exists():
        raise HTTPException(status_code=404, detail="Dashboard template not found.")
    return FileResponse(str(index_file))


@app.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint for container health probes."""
    return {"status": "healthy", "service": "fandango-analytics", "version": APP_VERSION}


@app.get("/api/overview")
async def get_overview() -> Dict[str, Any]:
    """Returns high-level summary KPIs and metrics."""
    return analyzer.get_kpi_overview()


@app.get("/api/platforms")
async def get_platforms() -> Dict[str, Any]:
    """Returns cross-platform comparison statistics and distribution histograms."""
    return analyzer.get_platform_comparison()


@app.get("/api/discrepancies")
async def get_discrepancies() -> Dict[str, Any]:
    """Returns discrepancy distribution and rounding table."""
    return analyzer.get_discrepancy_distribution()


@app.get("/api/temporal")
async def get_temporal() -> Dict[str, Any]:
    """Returns before vs after (2015 vs 2016-17) comparative distributions."""
    return analyzer.get_temporal_comparison()


@app.get("/api/stats")
async def get_stats() -> Dict[str, Any]:
    """Returns formal hypothesis tests, p-values, and effect size metrics."""
    return {
        "inflation_test": stats_engine.test_inflation_significance(),
        "temporal_test": stats_engine.test_temporal_shift_significance(),
    }


@app.get("/api/movies")
async def get_movies(
    query: str = Query("", description="Movie title search filter"),
    min_stars: float = Query(0.0, description="Minimum displayed stars"),
    max_stars: float = Query(5.0, description="Maximum displayed stars"),
    min_discrepancy: float = Query(0.0, description="Minimum discrepancy"),
    sort_by: str = Query("discrepancy", description="Column to sort by"),
    ascending: bool = Query(False, description="Ascending sort flag"),
    limit: int = Query(100, description="Max records to return"),
) -> List[Dict[str, Any]]:
    """Search and filter movies from the comparison dataset."""
    return analyzer.search_movies(
        query=query,
        min_stars=min_stars,
        max_stars=max_stars,
        min_discrepancy=min_discrepancy,
        sort_by=sort_by,
        ascending=ascending,
        limit=limit,
    )


@app.post("/api/sql")
async def execute_sql(req: SQLRequest) -> Dict[str, Any]:
    """Execute arbitrary read-only SELECT query against SQLite database."""
    return db_manager.execute_query(req.query, limit=req.limit or 100)


@app.get("/api/presets")
async def get_preset_queries() -> List[Dict[str, str]]:
    """Returns preset analyst SQL queries."""
    return db_manager.get_preset_queries()


def start():
    """CLI / script launcher."""
    import uvicorn
    uvicorn.run("app.main:app", host=DEFAULT_HOST, port=DEFAULT_PORT, reload=False)


if __name__ == "__main__":
    start()
