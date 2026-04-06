"""
Tests for POST /activities/{activity_name}/unregister endpoint using AAA pattern.
"""

import pytest


def test_unregister_valid_participant(client):
    """Test successful unregistration of a participant."""
    # ARRANGE
    email = "toremove@mergington.edu"
    activity = "Basketball Team"
    
    # Set up: sign up the student first
    client.post(
        f"/activities/{activity.replace(' ', '%20')}/signup?email={email}"
    )
    before = client.get("/activities").json()
    assert email in before[activity]["participants"]
    
    # ACT
    response = client.post(
        f"/activities/{activity.replace(' ', '%20')}/unregister?email={email}"
    )
    data = response.json()
    
    # ASSERT
    assert response.status_code == 200
    assert "message" in data
    assert email in data["message"]
    assert activity in data["message"]


def test_unregister_removes_participant_from_list(client):
    """Test that unregister actually removes the participant."""
    # ARRANGE
    email = "removetest@mergington.edu"
    activity = "Tennis Club"
    
    # Set up: sign up first
    client.post(
        f"/activities/{activity.replace(' ', '%20')}/signup?email={email}"
    )
    
    # ACT
    response = client.post(
        f"/activities/{activity.replace(' ', '%20')}/unregister?email={email}"
    )
    after = client.get("/activities").json()
    
    # ASSERT
    assert response.status_code == 200
    assert email not in after[activity]["participants"]


def test_unregister_not_signed_up_returns_400(client):
    """Test that unregistering a student who isn't signed up returns 400."""
    # ARRANGE
    email = "notsignedup@mergington.edu"
    activity = "Science Club"
    # (No sign up - student is not registered)
    
    # ACT
    response = client.post(
        f"/activities/{activity.replace(' ', '%20')}/unregister?email={email}"
    )
    data = response.json()
    
    # ASSERT
    assert response.status_code == 400
    assert "not signed up" in data["detail"].lower()


def test_unregister_nonexistent_activity_returns_404(client):
    """Test that unregistering from non-existent activity returns 404."""
    # ARRANGE
    email = "someone@mergington.edu"
    fake_activity = "Fake Club"
    
    # ACT
    response = client.post(
        f"/activities/{fake_activity.replace(' ', '%20')}/unregister?email={email}"
    )
    data = response.json()
    
    # ASSERT
    assert response.status_code == 404
    assert "not found" in data["detail"].lower()


def test_unregister_response_message_format(client):
    """Test that unregister response has properly formatted message."""
    # ARRANGE
    email = "msgtest@mergington.edu"
    activity = "Drama Club"
    
    # Set up: sign up first
    client.post(
        f"/activities/{activity.replace(' ', '%20')}/signup?email={email}"
    )
    
    # ACT
    response = client.post(
        f"/activities/{activity.replace(' ', '%20')}/unregister?email={email}"
    )
    data = response.json()
    message = data["message"]
    
    # ASSERT
    assert response.status_code == 200
    assert "message" in data
    assert isinstance(message, str)
    assert email in message
    assert activity in message
    assert "Unregistered" in message or "unregistered" in message.lower()


def test_unregister_can_resignup_after_unregister(client):
    """Test that a student can sign up again after being unregistered."""
    # ARRANGE
    email = "resignup@mergington.edu"
    activity = "Photography Club"
    
    # ACT - sign up
    response1 = client.post(
        f"/activities/{activity.replace(' ', '%20')}/signup?email={email}"
    )
    # ACT - unregister
    response2 = client.post(
        f"/activities/{activity.replace(' ', '%20')}/unregister?email={email}"
    )
    # ACT - sign up again
    response3 = client.post(
        f"/activities/{activity.replace(' ', '%20')}/signup?email={email}"
    )
    activities = client.get("/activities").json()
    
    # ASSERT
    assert response1.status_code == 200
    assert response2.status_code == 200
    assert response3.status_code == 200
    assert email in activities[activity]["participants"]


def test_unregister_one_doesnt_affect_others(client):
    """Test that unregistering one student doesn't affect others."""
    # ARRANGE
    activity = "Programming Class"
    email1 = "student1@mergington.edu"
    email2 = "student2@mergington.edu"
    
    # Set up: sign up both students
    client.post(f"/activities/{activity.replace(' ', '%20')}/signup?email={email1}")
    client.post(f"/activities/{activity.replace(' ', '%20')}/signup?email={email2}")
    
    # ACT - unregister first student
    response = client.post(
        f"/activities/{activity.replace(' ', '%20')}/unregister?email={email1}"
    )
    activities = client.get("/activities").json()
    
    # ASSERT
    assert response.status_code == 200
    assert email1 not in activities[activity]["participants"]
    assert email2 in activities[activity]["participants"]


def test_unregister_then_unregister_again_fails(client):
    """Test that unregistering twice returns error on second attempt."""
    # ARRANGE
    email = "double@mergington.edu"
    activity = "Debate Team"
    
    # Set up: sign up
    client.post(f"/activities/{activity.replace(' ', '%20')}/signup?email={email}")
    
    # ACT - first unregister
    response1 = client.post(
        f"/activities/{activity.replace(' ', '%20')}/unregister?email={email}"
    )
    # ACT - second unregister (should fail)
    response2 = client.post(
        f"/activities/{activity.replace(' ', '%20')}/unregister?email={email}"
    )
    data = response2.json()
    
    # ASSERT
    assert response1.status_code == 200
    assert response2.status_code == 400
    assert "not signed up" in data["detail"].lower()
