import requests
import json

def test_chat_functionality():
    print("🧪 Testing Chat Functionality...")

    # Test 1: Get users
    print("\n1. Testing user list...")
    try:
        response = requests.get("http://localhost:8000/api/users")
        if response.status_code == 200:
            users = response.json()
            print(f"✅ Found {len(users)} users")
            for user in users:
                print(f"   - {user['email']} (ID: {user['_id']})")
        else:
            print(f"❌ Failed to get users: {response.status_code}")
    except Exception as e:
        print(f"❌ Error getting users: {e}")

    # Test 2: Test login
    print("\n2. Testing login...")
    try:
        login_data = {
            "email": "symjain789@gmail.com",
            "password": "password123"
        }
        response = requests.post("http://localhost:8000/api/auth/login", json=login_data)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Login successful")
            print(f"   User ID: {data['user']['id']}")
            print(f"   Token: {data['access_token'][:20]}...")
            return data['access_token'], data['user']['id']
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Error during login: {e}")

    return None, None

def test_messages(token, user_id):
    if not token or not user_id:
        return

    print("\n3. Testing messages...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"http://localhost:8000/api/messages/{user_id}", headers=headers)
        if response.status_code == 200:
            messages = response.json()
            print(f"✅ Found {len(messages)} messages")
            for msg in messages[:3]:  # Show first 3 messages
                print(f"   - {msg['sender_id']} -> {msg['receiver_id']}: {msg['content'][:30]}...")
        else:
            print(f"❌ Failed to get messages: {response.status_code}")
    except Exception as e:
        print(f"❌ Error getting messages: {e}")

if __name__ == "__main__":
    token, user_id = test_chat_functionality()
    test_messages(token, user_id)
    print("\n🎉 Test completed!")
