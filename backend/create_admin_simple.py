import requests
import json

def create_admin():
    # Admin user data
    admin_data = {
        "email": "admin@example.com",
        "username": "Admin",
        "password": "admin123",
        "role": "admin"
    }

    try:
        print("Creating admin user...")
        response = requests.post(
            "http://localhost:8000/api/users/create",
            json=admin_data,
            headers={"Content-Type": "application/json"}
        )

        if response.status_code == 200:
            print("✅ Admin user created successfully!")
            print(f"Email: {admin_data['email']}")
            print(f"Password: {admin_data['password']}")
            print("\nYou can now login with these credentials to access the admin dashboard.")
        else:
            print(f"❌ Failed to create admin user. Status: {response.status_code}")
            print(f"Response: {response.text}")

    except Exception as e:
        print(f"❌ Error creating admin user: {e}")

if __name__ == "__main__":
    create_admin()
