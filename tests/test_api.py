"""Integration tests for FastAPI REST API endpoints and SQL execution."""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "fandango-analytics"


def test_overview_endpoint():
    response = client.get("/api/overview")
    assert response.status_code == 200
    data = response.json()
    assert "avg_displayed_stars_2015" in data
    assert "rounded_up_pct_2015" in data
    assert data["total_2015_movies"] == 146


def test_platforms_endpoint():
    response = client.get("/api/platforms")
    assert response.status_code == 200
    data = response.json()
    assert "summary_table" in data
    assert "histograms" in data
    assert len(data["summary_table"]) == 5


def test_discrepancies_endpoint():
    response = client.get("/api/discrepancies")
    assert response.status_code == 200
    data = response.json()
    assert "breakdown" in data
    assert data["max_discrepancy"] == 0.5


def test_temporal_endpoint():
    response = client.get("/api/temporal")
    assert response.status_code == 200
    data = response.json()
    assert "bins" in data
    assert "metrics" in data


def test_stats_endpoint():
    response = client.get("/api/stats")
    assert response.status_code == 200
    data = response.json()
    assert "inflation_test" in data
    assert "temporal_test" in data
    assert data["inflation_test"]["is_statistically_significant"] is True


def test_movies_endpoint():
    response = client.get("/api/movies?query=Avengers")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert "Avengers" in data[0]["film"]


def test_sql_execution_select():
    payload = {"query": "SELECT COUNT(*) AS total FROM fandango_2015;"}
    response = client.post("/api/sql", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["rows"][0]["total"] == 146


def test_sql_execution_forbidden_query():
    payload = {"query": "DROP TABLE fandango_2015;"}
    response = client.post("/api/sql", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False
    assert "Only SELECT or WITH queries are permitted" in data["error"]


def test_presets_endpoint():
    response = client.get("/api/presets")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 3
