import requests
import json

def create_simple_user():
    # Simple user data
    user_data = {
        "email": "user@example.com",
        "username": "TestUser",
        "password": "user123",
        "role": "user"
    }

    try:
        print("Creating simple user...")
        response = requests.post(
            "http://localhost:8000/api/users/create",
            json=user_data,
            headers={"Content-Type": "application/json"}
        )

        if response.status_code == 200:
            print("✅ Simple user created successfully!")
            print(f"Email: {user_data['email']}")
            print(f"Password: {user_data['password']}")
            return True
        elif response.status_code == 400 and "already registered" in response.text:
            print("✅ User already exists!")
            print(f"Email: {user_data['email']}")
            print(f"Password: {user_data['password']}")
            return True
        else:
            print(f"❌ Failed to create user. Status: {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Error creating user: {e}")
        return False

def test_user_login():
    login_data = {
        "email": "user@example.com",
        "password": "user123"
    }

    try:
        print("\nTesting user login...")
        response = requests.post("http://localhost:8000/api/auth/login", json=login_data)
        if response.status_code == 200:
            data = response.json()
            print("✅ User login successful!")
            print(f"User ID: {data['user']['id']}")
            print(f"Role: {data['user']['role']}")
            return True
        else:
            print(f"❌ User login failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error during user login: {e}")
        return False

if __name__ == "__main__":
    if create_simple_user():
        test_user_login()
    print("\n🎉 User setup completed!")
