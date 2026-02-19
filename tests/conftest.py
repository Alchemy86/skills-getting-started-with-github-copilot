"""
Pytest configuration and shared fixtures for API tests.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """
    Fixture that provides a TestClient for the FastAPI app.
    """
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """
    Fixture that resets the activities database to its initial state
    before each test and restores it after.
    
    This is necessary because the activities dict is global and mutable,
    so tests that modify it (signup/unregister) would affect other tests.
    """
    # Store the original state
    original_activities = {
        name: {
            "description": activity["description"],
            "schedule": activity["schedule"],
            "max_participants": activity["max_participants"],
            "participants": activity["participants"].copy()
        }
        for name, activity in activities.items()
    }
    
    # Yield control to the test
    yield
    
    # Restore the original state after test
    activities.clear()
    activities.update(original_activities)
