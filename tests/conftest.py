"""
Shared pytest fixtures for testing the Mergington High School Activities API.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """
    Provide a TestClient for the FastAPI app.
    Each test gets a fresh client with the app's in-memory data.
    """
    return TestClient(app)


@pytest.fixture
def sample_activities(client):
    """
    Helper fixture to retrieve the current activities from the API.
    Useful for tests that need to verify the initial state.
    """
    response = client.get("/activities")
    return response.json()
