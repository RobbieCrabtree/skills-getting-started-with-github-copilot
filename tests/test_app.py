import pytest
from fastapi.testclient import TestClient
from src.app import app, activities
import copy

@pytest.fixture(autouse=True)
def reset_activities():
    # Arrange: Save original state and restore after test
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(copy.deepcopy(original))

def test_root_redirect():
    # Arrange
    client = TestClient(app)
    # Act
    response = client.get("/", allow_redirects=False)
    # Assert
    assert response.status_code in (302, 307)
    assert "/static/index.html" in response.headers["location"]

def test_get_activities():
    # Arrange
    client = TestClient(app)
    # Act
    response = client.get("/activities")
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data

def test_signup_for_activity_success():
    # Arrange
    client = TestClient(app)
    email = "newstudent@mergington.edu"
    activity = "Chess Club"
    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")
    # Assert
    assert response.status_code == 200
    assert email in activities[activity]["participants"]
    assert response.json()["message"].startswith("Signed up")

def test_signup_duplicate():
    # Arrange
    client = TestClient(app)
    activity = "Chess Club"
    email = activities[activity]["participants"][0]
    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")
    # Assert
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]

def test_signup_nonexistent_activity():
    # Arrange
    client = TestClient(app)
    email = "student@mergington.edu"
    # Act
    response = client.post(f"/activities/Nonexistent/signup?email={email}")
    # Assert
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]

def test_remove_participant_success():
    # Arrange
    client = TestClient(app)
    activity = "Chess Club"
    email = activities[activity]["participants"][0]
    # Act
    response = client.delete(f"/activities/{activity}/signup?email={email}")
    # Assert
    assert response.status_code == 200
    assert email not in activities[activity]["participants"]
    assert response.json()["message"].startswith("Removed")

def test_remove_nonexistent_participant():
    # Arrange
    client = TestClient(app)
    activity = "Chess Club"
    email = "notregistered@mergington.edu"
    # Act
    response = client.delete(f"/activities/{activity}/signup?email={email}")
    # Assert
    assert response.status_code == 404
    assert "not registered" in response.json()["detail"]

def test_remove_from_nonexistent_activity():
    # Arrange
    client = TestClient(app)
    email = "student@mergington.edu"
    # Act
    response = client.delete(f"/activities/Nonexistent/signup?email={email}")
    # Assert
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]
