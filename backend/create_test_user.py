import requests
import json

def create_test_user():
    # Test user data
    test_user = {
        "email": "testuser@example.com",
        "username": "TestUser",
        "password": "test123",
        "role": "user"
    }

    try:
        print("Creating test user...")
        response = requests.post(
            "http://localhost:8000/api/users/create",
            json=test_user,
            headers={"Content-Type": "application/json"}
        )

        if response.status_code == 200:
            print("✅ Test user created successfully!")
            print(f"Email: {test_user['email']}")
            print(f"Password: {test_user['password']}")
            return True
        else:
            print(f"❌ Failed to create test user. Status: {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Error creating test user: {e}")
        return False

def test_login():
    login_data = {
        "email": "testuser@example.com",
        "password": "test123"
    }

    try:
        print("\nTesting login with test user...")
        response = requests.post("http://localhost:8000/api/auth/login", json=login_data)
        if response.status_code == 200:
            data = response.json()
            print("✅ Login successful!")
            print(f"User ID: {data['user']['id']}")
            print(f"Token: {data['access_token'][:20]}...")
            return data['access_token'], data['user']['id']
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None, None
    except Exception as e:
        print(f"❌ Error during login: {e}")
        return None, None

if __name__ == "__main__":
    if create_test_user():
        test_login()
    print("\n🎉 Test user setup completed!")
