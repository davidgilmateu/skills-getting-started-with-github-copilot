from fastapi.testclient import TestClient

from src.app import app

client = TestClient(app)


def test_root_redirects_to_static_index_html():
    # Arrange
    expected_location = "/static/index.html"

    # Act
    response = client.get("/")

    # Assert
    assert response.status_code == 200
    assert response.url.path == expected_location


def test_get_activities_returns_activity_list():
    # Arrange

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert "Chess Club" in response.json()
    assert response.json()["Chess Club"]["description"] == "Learn strategies and compete in chess tournaments"


def test_signup_for_activity_adds_participant():
    # Arrange
    activity_name = "Art Club"
    new_email = "newstudent1@example.com"
    payload = {"email": new_email}

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params=payload)

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {new_email} for {activity_name}"}

    # Cleanup
    cleanup_response = client.delete(f"/activities/{activity_name}/participants", params={"email": new_email})
    assert cleanup_response.status_code == 200


def test_signup_for_activity_returns_400_for_duplicate_signup():
    # Arrange
    activity_name = "Drama Club"
    duplicate_email = "newstudent2@example.com"
    payload = {"email": duplicate_email}

    first_response = client.post(f"/activities/{activity_name}/signup", params=payload)
    assert first_response.status_code == 200

    # Act
    duplicate_response = client.post(f"/activities/{activity_name}/signup", params=payload)

    # Assert
    assert duplicate_response.status_code == 400
    assert duplicate_response.json()["detail"] == "Student already signed up for this activity"

    # Cleanup
    cleanup_response = client.delete(f"/activities/{activity_name}/participants", params={"email": duplicate_email})
    assert cleanup_response.status_code == 200


def test_unregister_participant_removes_existing_student():
    # Arrange
    activity_name = "Swimming"
    email_to_remove = "newstudent3@example.com"
    signup_response = client.post(f"/activities/{activity_name}/signup", params={"email": email_to_remove})
    assert signup_response.status_code == 200

    # Act
    response = client.delete(f"/activities/{activity_name}/participants", params={"email": email_to_remove})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email_to_remove} from {activity_name}"}


def test_unregister_participant_returns_404_for_missing_student():
    # Arrange
    activity_name = "Basketball Team"
    nonexistent_email = "missingstudent@example.com"

    # Act
    response = client.delete(f"/activities/{activity_name}/participants", params={"email": nonexistent_email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
