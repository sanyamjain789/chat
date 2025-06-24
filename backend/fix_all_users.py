import pymongo
import bcrypt
import os
from datetime import datetime

def fix_all_users():
    print("🔧 Fixing all users with missing passwords...")

    # MongoDB connection
    MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    client = pymongo.MongoClient(MONGODB_URL)
    db = client.chat_app
    users_collection = db.users

    # Users to fix
    users_to_fix = [
        {
            "email": "user@example.com",
            "password": "user123",
            "username": "TestUser",
            "role": "user"
        },
        {
            "email": "testuser@example.com",
            "password": "test123",
            "username": "TestUser2",
            "role": "user"
        }
    ]

    for user_data in users_to_fix:
        email = user_data["email"]

        # Check if user exists
        existing_user = users_collection.find_one({"email": email})
        if not existing_user:
            print(f"❌ User {email} not found!")
            continue

        print(f"Found user: {existing_user['email']}")
        print(f"Current fields: {list(existing_user.keys())}")

        # Hash password
        hashed_password = bcrypt.hashpw(user_data["password"].encode(), bcrypt.gensalt())

        # Update user with password
        result = users_collection.update_one(
            {"email": email},
            {
                "$set": {
                    "password": hashed_password,
                    "username": user_data["username"],
                    "role": user_data["role"],
                    "isFirstLogin": False,
                    "is_online": False,
                    "created_at": existing_user.get("created_at", datetime.now().isoformat())
                }
            }
        )

        if result.modified_count > 0:
            print(f"✅ User {email} password updated successfully!")
            print(f"Password: {user_data['password']}")
        else:
            print(f"❌ Failed to update user {email} password.")

        # Verify the update
        updated_user = users_collection.find_one({"email": email})
        if updated_user and "password" in updated_user:
            print(f"✅ Verification: User {email} now has password field.")
        else:
            print(f"❌ Verification failed: User {email} still missing password field.")

        print("-" * 50)

if __name__ == "__main__":
    fix_all_users()
    print("\n�� All users fixed!")
