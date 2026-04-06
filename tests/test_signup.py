"""
Tests for POST /activities/{activity_name}/signup endpoint using AAA pattern.
"""

import pytest


def test_signup_valid_student(client):
    """Test successful signup for an activity."""
    # ARRANGE
    email = "newstudent@mergington.edu"
    activity = "Chess Club"
    
    # ACT
    response = client.post(
        f"/activities/{activity.replace(' ', '%20')}/signup?email={email}"
    )
    data = response.json()
    
    # ASSERT
    assert response.status_code == 200
    assert "message" in data
    assert email in data["message"]
    assert activity in data["message"]


def test_signup_adds_participant_to_list(client):
    """Test that signup adds participant to the activity's participant list."""
    # ARRANGE
    email = "testuser@mergington.edu"
    activity = "Programming Class"
    before_response = client.get("/activities")
    before = before_response.json()
    
    # ACT
    response = client.post(
        f"/activities/{activity.replace(' ', '%20')}/signup?email={email}"
    )
    after_response = client.get("/activities")
    after = after_response.json()
    
    # ASSERT
    assert email not in before[activity]["participants"]
    assert response.status_code == 200
    assert email in after[activity]["participants"]


def test_signup_duplicate_student_returns_400(client):
    """Test that signing up the same student twice returns an error."""
    # ARRANGE
    email = "duplicate@mergington.edu"
    activity = "Tennis Club"
    
    # ACT - first signup
    response1 = client.post(
        f"/activities/{activity.replace(' ', '%20')}/signup?email={email}"
    )
    # ACT - second signup (duplicate)
    response2 = client.post(
        f"/activities/{activity.replace(' ', '%20')}/signup?email={email}"
    )
    data = response2.json()
    
    # ASSERT
    assert response1.status_code == 200
    assert response2.status_code == 400
    assert "already signed up" in data["detail"].lower()


def test_signup_nonexistent_activity_returns_404(client):
    """Test that signing up for a non-existent activity returns 404."""
    # ARRANGE
    email = "student@mergington.edu"
    fake_activity = "Nonexistent Club"
    
    # ACT
    response = client.post(
        f"/activities/{fake_activity.replace(' ', '%20')}/signup?email={email}"
    )
    data = response.json()
    
    # ASSERT
    assert response.status_code == 404
    assert "not found" in data["detail"].lower()


def test_signup_multiple_different_students_same_activity(client):
    """Test that multiple different students can sign up for the same activity."""
    # ARRANGE
    activity = "Debate Team"
    students = [
        "student1@mergington.edu",
        "student2@mergington.edu",
        "student3@mergington.edu"
    ]
    
    # ACT - sign up each student
    responses = []
    for email in students:
        response = client.post(
            f"/activities/{activity.replace(' ', '%20')}/signup?email={email}"
        )
        responses.append(response)
    
    # ASSERT - all signups succeeded
    for response in responses:
        assert response.status_code == 200
    
    # ASSERT - all students are enrolled
    activities = client.get("/activities").json()
    for email in students:
        assert email in activities[activity]["participants"]


def test_signup_different_activities(client):
    """Test that one student can sign up for multiple activities."""
    # ARRANGE
    email = "multiactivity@mergington.edu"
    activities_list = ["Science Club", "Photography Club", "Drama Club"]
    
    # ACT - sign up for each activity
    responses = []
    for activity in activities_list:
        response = client.post(
            f"/activities/{activity.replace(' ', '%20')}/signup?email={email}"
        )
        responses.append(response)
    
    # ASSERT - all signups succeeded
    for response in responses:
        assert response.status_code == 200
    
    # ASSERT - student is in all activities
    all_activities = client.get("/activities").json()
    for activity in activities_list:
        assert email in all_activities[activity]["participants"]


def test_signup_response_message_format(client):
    """Test that signup response has a properly formatted message."""
    # ARRANGE
    email = "messagetest@mergington.edu"
    activity = "Programming Class"
    
    # ACT
    response = client.post(
        f"/activities/{activity.replace(' ', '%20')}/signup?email={email}"
    )
    data = response.json()
    message = data["message"]
    
    # ASSERT
    assert response.status_code == 200
    assert "message" in data
    assert isinstance(message, str)
    assert email in message
    assert activity in message
    assert "Signed up" in message or "signed up" in message.lower()


def test_signup_respects_max_participants_constraint(client):
    """Test that max_participants constraint is tracked for each activity."""
    # ARRANGE
    # (No direct action needed)
    
    # ACT
    response = client.get("/activities")
    activities = response.json()
    
    # ASSERT
    for activity_name, activity_data in activities.items():
        max_participants = activity_data["max_participants"]
        current_participants = len(activity_data["participants"])
        
        assert isinstance(max_participants, int)
        assert max_participants > 0
        assert current_participants <= max_participants
