"""
Tests for GET /activities endpoint using AAA (Arrange-Act-Assert) pattern.
"""

import pytest


def test_get_activities_returns_all_activities(client):
    """Test that GET /activities returns all 9 activities."""
    # ARRANGE
    expected_activities = {
        "Chess Club",
        "Programming Class",
        "Gym Class",
        "Basketball Team",
        "Tennis Club",
        "Drama Club",
        "Photography Club",
        "Debate Team",
        "Science Club"
    }
    
    # ACT
    response = client.get("/activities")
    activities = response.json()
    
    # ASSERT
    assert response.status_code == 200
    assert len(activities) == 9
    assert set(activities.keys()) == expected_activities


def test_activity_has_required_fields(client):
    """Test that each activity has all required fields."""
    # ARRANGE
    required_fields = {"description", "schedule", "max_participants", "participants"}
    
    # ACT
    response = client.get("/activities")
    activities = response.json()
    
    # ASSERT
    for activity_name, activity_data in activities.items():
        assert isinstance(activity_data, dict), f"{activity_name} should be a dict"
        assert required_fields.issubset(activity_data.keys()), \
            f"{activity_name} missing required fields. Has: {activity_data.keys()}"


def test_activity_data_types(client):
    """Test that activity data has correct types."""
    # ARRANGE
    # (No setup needed)
    
    # ACT
    response = client.get("/activities")
    activities = response.json()
    
    # ASSERT
    for activity_name, activity_data in activities.items():
        assert isinstance(activity_data["description"], str), \
            f"{activity_name} description should be string"
        assert isinstance(activity_data["schedule"], str), \
            f"{activity_name} schedule should be string"
        assert isinstance(activity_data["max_participants"], int), \
            f"{activity_name} max_participants should be int"
        assert isinstance(activity_data["participants"], list), \
            f"{activity_name} participants should be list"
        
        for participant in activity_data["participants"]:
            assert isinstance(participant, str), \
                f"{activity_name} participant should be string"


def test_activities_have_valid_participants_count(client):
    """Test that participants count never exceeds max_participants."""
    # ARRANGE
    # (No setup needed)
    
    # ACT
    response = client.get("/activities")
    activities = response.json()
    
    # ASSERT
    for activity_name, activity_data in activities.items():
        participants_count = len(activity_data["participants"])
        max_participants = activity_data["max_participants"]
        
        assert participants_count <= max_participants, \
            f"{activity_name} has more participants than max allowed"
        assert max_participants > 0, \
            f"{activity_name} max_participants should be greater than 0"


def test_chess_club_has_initial_participants(client, sample_activities):
    """Test that Chess Club has some initial participants."""
    # ARRANGE
    expected_participants = {"michael@mergington.edu", "daniel@mergington.edu"}
    
    # ACT
    chess_club = sample_activities.get("Chess Club")
    
    # ASSERT
    assert chess_club is not None
    assert len(chess_club["participants"]) > 0
    assert expected_participants.issubset(set(chess_club["participants"]))


def test_all_activities_have_descriptions(client):
    """Test that all activities have non-empty descriptions."""
    # ARRANGE
    min_description_length = 5
    
    # ACT
    response = client.get("/activities")
    activities = response.json()
    
    # ASSERT
    for activity_name, activity_data in activities.items():
        assert activity_data["description"], \
            f"{activity_name} should have a description"
        assert len(activity_data["description"]) > min_description_length, \
            f"{activity_name} description seems too short"
