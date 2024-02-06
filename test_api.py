from fastapi.testclient import TestClient
from main import app
from manage import SECRET_KEY, ALGORITHM
from jose import jwt
import pytest

client = TestClient(app)

# Global variables
global_user = None
global_token = None
global_note_id = None

def create_test_user():
    global global_user
    response = client.post(
        "/register",
        json={"username": "testuser", "email": "testuser@gmail.com", "password": "test"},
    )
    assert response.status_code == 200
    global_user = response.json()
    return global_user

def delete_test_user():
    global global_user, global_token
    response = client.delete(
        f"/user/{global_user['id']}",
        headers={"Authorization": f"Bearer {global_token}"}
    )
    assert response.status_code == 200
    global_user = None

@pytest.fixture(scope="session", autouse=True)
def setup_and_teardown():
    global global_token
    # Setup
    create_test_user()
    test_user_data = {"sub": global_user["username"]}
    global_token = jwt.encode(test_user_data, SECRET_KEY, algorithm=ALGORITHM)
    yield
    # Teardown
    delete_test_user()

def test_create_item():
    global global_token, global_user, global_note_id
    response = client.post(
        "/notes/create",
        headers={"Authorization": f"Bearer {global_token}"},
        json={"title": "Item Name", "content": "A very nice Item", "user_id": global_user["id"]},
    )
    data = response.json()
    global_note_id = data["id"]
    assert response.status_code == 200

def test_update_item():
    global global_token, global_user, global_note_id
    response = client.post(
        "/notes/update",
        headers={"Authorization": f"Bearer {global_token}"},
        json={"title":"Updated Title", "content":"Updated content", "post_id": global_note_id}
    )
    assert response.status_code == 200

def test_delete_item():
    global global_token, global_note_id
    response = client.delete(
        f"/notes/delete/{global_note_id}", 
        headers={"Authorization": f"Bearer {global_token}"},
    )
    assert response.status_code == 200
