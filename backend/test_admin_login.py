import requests
import json

def test_admin_login():
    login_data = {
        "email": "superadmin@gmail.com",
        "password": "admin123@"
    }

    try:
        print("🧪 Testing admin login...")
        response = requests.post("http://localhost:8000/api/auth/login", json=login_data)
        if response.status_code == 200:
            data = response.json()
            print("✅ Admin login successful!")
            print(f"User ID: {data['user']['id']}")
            print(f"Email: {data['user']['email']}")
            print(f"Role: {data['user']['role']}")
            print(f"Token: {data['access_token'][:20]}...")
            print("\n🎉 You can now login to the admin dashboard!")
            return data['access_token'], data['user']['id']
        else:
            print(f"❌ Admin login failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None, None
    except Exception as e:
        print(f"❌ Error during admin login: {e}")
        return None, None

def test_admin_access(token, user_id):
    if not token or not user_id:
        return

    try:
        print("\n🧪 Testing admin access...")
        headers = {"Authorization": f"Bearer {token}"}

        # Test admin users endpoint
        response = requests.get("http://localhost:8000/api/admin/users", headers=headers)
        if response.status_code == 200:
            users = response.json()
            print(f"✅ Admin access successful! Found {len(users)} users")
            print("You can now access the admin dashboard.")
        else:
            print(f"❌ Admin access failed: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Error testing admin access: {e}")

if __name__ == "__main__":
    token, user_id = test_admin_login()
    test_admin_access(token, user_id)
    print("\n🎉 Admin testing completed!")
