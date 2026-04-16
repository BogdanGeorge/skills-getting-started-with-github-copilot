"""
Pytest configuration and fixtures for FastAPI backend tests.

Fixtures follow AAA (Arrange-Act-Assert) pattern by providing pre-configured
test data and client setup for endpoint testing.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def reset_activities():
    """
    Arrange: Reset activities to known initial state before each test.
    
    Clears the in-memory activities dictionary and restores with fresh data,
    ensuring test isolation and preventing cross-test contamination.
    """
    # Store original state
    original_state = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Soccer Team": {
            "description": "Competitive soccer team for all skill levels",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 22,
            "participants": []
        },
        "Swimming Club": {
            "description": "Learn and improve swimming techniques",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 16,
            "participants": []
        },
        "Art Club": {
            "description": "Explore painting, drawing, and creative expression",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 15,
            "participants": []
        },
        "Drama Club": {
            "description": "Acting, theater production, and performance arts",
            "schedule": "Mondays, 3:30 PM - 5:30 PM",
            "max_participants": 25,
            "participants": []
        },
        "Debate Team": {
            "description": "Develop public speaking and critical thinking skills",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": []
        },
        "Math Olympiad": {
            "description": "Advanced mathematics competition training",
            "schedule": "Wednesdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": []
        }
    }
    
    # Clear existing activities
    activities.clear()
    
    # Restore fresh state
    activities.update(original_state)
    
    yield
    
    # Cleanup after test
    activities.clear()
    activities.update(original_state)


@pytest.fixture
def client(reset_activities):
    """
    Arrange: Provide TestClient instance for HTTP endpoint testing.
    
    Depends on reset_activities fixture to ensure fresh state before each test.
    TestClient simulates HTTP requests without running a live server.
    """
    return TestClient(app)


@pytest.fixture
def test_emails():
    """
    Arrange: Provide common test email addresses for use in tests.
    """
    return {
        "existing_chess": "michael@mergington.edu",
        "existing_programming": "emma@mergington.edu",
        "existing_gym": "john@mergington.edu",
        "new_student": "alice@mergington.edu",
        "another_student": "bob@mergington.edu",
        "third_student": "charlie@mergington.edu",
    }


@pytest.fixture
def test_activities():
    """
    Arrange: Provide activity names for use in tests.
    """
    return {
        "valid": "Chess Club",
        "valid_empty": "Soccer Team",
        "invalid": "Nonexistent Activity",
    }
