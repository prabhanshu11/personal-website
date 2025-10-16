"""Basic tests for the FastHTML application."""

import pytest
from website.app import app


def test_health_endpoint():
    """Test health check endpoint returns correct status."""
    client = app.client
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "prabhanshu-website"


def test_home_page():
    """Test home page loads successfully."""
    client = app.client
    response = client.get("/")
    assert response.status_code == 200
    assert b"Prabhanshu" in response.content


def test_about_page():
    """Test about page loads successfully."""
    client = app.client
    response = client.get("/about")
    assert response.status_code == 200
    assert b"About Me" in response.content


def test_404_page():
    """Test 404 page for non-existent routes."""
    client = app.client
    response = client.get("/nonexistent-page")
    assert response.status_code == 404
    assert b"404" in response.content