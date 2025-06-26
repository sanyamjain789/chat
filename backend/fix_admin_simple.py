import requests
import json

def delete_and_recreate_admin():
    print("🔧 Fixing admin user...")

    # First, let's check what users exist
    try:
        response = requests.get("http://localhost:8000/api/users")
        if response.status_code == 200:
            users = response.json()
            admin_user = None
            for user in users:
                if user['email'] == 'superadmin@gmail.com':
                    admin_user = user
                    break

            if admin_user:
                print(f"Found admin user with ID: {admin_user['_id']}")
                print("Admin user exists but may have missing password field.")
            else:
                print("Admin user not found, will create new one.")
        else:
            print(f"Failed to get users: {response.status_code}")
    except Exception as e:
        print(f"Error checking users: {e}")

    # Create a new admin user with proper password
    admin_data = {
        "email": "superadmin@gmail.com",
        "username": "Admin",
        "password": "admin123@",
        "role": "admin"
    }

    try:
        print("\nCreating new admin user...")
        response = requests.post(
            "http://localhost:8000/api/users/create",
            json=admin_data,
            headers={"Content-Type": "application/json"}
        )

        if response.status_code == 200:
            print("✅ Admin user created successfully!")
            print(f"Email: {admin_data['email']}")
            print(f"Password: {admin_data['password']}")
            print("You can now login with these credentials.")
        elif response.status_code == 400 and "already registered" in response.text:
            print("⚠️ Admin user already exists. Let's test the login...")
            test_admin_login()
        else:
            print(f"❌ Failed to create admin user. Status: {response.status_code}")
            print(f"Response: {response.text}")

    except Exception as e:
        print(f"❌ Error creating admin user: {e}")

def test_admin_login():
    login_data = {
        "email": "superadmin@gmail.com",
        "password": "admin123@"
    }

    try:
        print("\nTesting admin login...")
        response = requests.post("http://localhost:8000/api/auth/login", json=login_data)
        if response.status_code == 200:
            data = response.json()
            print("✅ Admin login successful!")
            print(f"User ID: {data['user']['id']}")
            print(f"Role: {data['user']['role']}")
            print("You can now access the admin dashboard.")
        else:
            print(f"❌ Admin login failed: {response.status_code}")
            print(f"Response: {response.text}")
            print("\nThe admin user exists but has password issues.")
            print("You may need to manually update the database.")
    except Exception as e:
        print(f"❌ Error during admin login: {e}")

if __name__ == "__main__":
    delete_and_recreate_admin()
    print("\n🎉 Admin fix completed!")
