import requests
import json

def test_user_login(email, password, expected_role):
    login_data = {
        "email": email,
        "password": password
    }

    try:
        print(f"\n🧪 Testing login for {email}...")
        response = requests.post("http://localhost:8000/api/auth/login", json=login_data)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Login successful!")
            print(f"   User ID: {data['user']['id']}")
            print(f"   Role: {data['user']['role']}")
            print(f"   Expected Role: {expected_role}")

            if data['user']['role'] == expected_role:
                print(f"   ✅ Role matches!")
            else:
                print(f"   ❌ Role mismatch!")

            return True
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error during login: {e}")
        return False

def test_all_users():
    print("🧪 Testing all users...")

    # Test users
    test_users = [
        {
            "email": "admin@example.com",
            "password": "admin123",
            "role": "admin"
        },
        {
            "email": "user@example.com",
            "password": "user123",
            "role": "user"
        },
        {
            "email": "testuser@example.com",
            "password": "test123",
            "role": "user"
        }
    ]

    success_count = 0
    for user in test_users:
        if test_user_login(user["email"], user["password"], user["role"]):
            success_count += 1

    print(f"\n🎉 Test Results: {success_count}/{len(test_users)} users working!")

    if success_count == len(test_users):
        print("✅ All users are working perfectly!")
        print("\n📋 Login Credentials:")
        for user in test_users:
            print(f"   {user['email']} / {user['password']} (Role: {user['role']})")
    else:
        print("❌ Some users still have issues.")

if __name__ == "__main__":
    test_all_users()
