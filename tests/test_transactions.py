from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


# Register a test user and get JWT token
def get_token():
    username = "testuser123"

    register_response = client.post(
        "/auth/register",
        json={
            "username": username,
            "email": "testuser123@gmail.com",
            "password": "12345678"
        }
    )

    # If user already exists, that's okay.
    # We can still log in.
    login_response = client.post(
        "/auth/login",
        data={
            "username": username,
            "password": "12345678"
        }
    )

    assert login_response.status_code == 200

    return login_response.json()["access_token"]


# Get all transactions
def test_get_transactions():
    token = get_token()

    response = client.get(
        "/transactions",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200


# Get specific transaction
def test_get_specific_transaction():
    token = get_token()

    # First create a transaction
    create_response = client.post(
        "/transactions",
        json={
            "title": "Test Food",
            "amount": 300,
            "type": "expense",
            "category": "Food",
            "date": "2026-10-06"
        },
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert create_response.status_code == 200

    transaction_id = create_response.json()["id"]

    response = client.get(
        f"/transactions/{transaction_id}",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200


# Create transaction
def test_create_transaction():
    token = get_token()

    response = client.post(
        "/transactions",
        json={
            "title": "Bus Fare",
            "amount": 100,
            "type": "expense",
            "category": "Transport",
            "date": "2026-10-06"
        },
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200
    assert response.json()["title"] == "Bus Fare"
    assert response.json()["amount"] == 100


# Update transaction
def test_update_transaction():
    token = get_token()

    # First create a transaction
    create_response = client.post(
        "/transactions",
        json={
            "title": "Old Title",
            "amount": 200,
            "type": "expense",
            "category": "Food",
            "date": "2026-10-06"
        },
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert create_response.status_code == 200

    transaction_id = create_response.json()["id"]

    # Update the transaction
    response = client.put(
        f"/transactions/{transaction_id}",
        json={
            "title": "New Title",
            "amount": 500
        },
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200
    assert response.json()["title"] == "New Title"
    assert response.json()["amount"] == 500


# Delete transaction
def test_delete_transaction():
    token = get_token()

    # First create a transaction
    create_response = client.post(
        "/transactions",
        json={
            "title": "Delete Me",
            "amount": 150,
            "type": "expense",
            "category": "Other",
            "date": "2026-10-06"
        },
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert create_response.status_code == 200

    transaction_id = create_response.json()["id"]

    # Delete the transaction
    response = client.delete(
        f"/transactions/{transaction_id}",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Transaction deleted successfully"