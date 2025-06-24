import pymongo
import bcrypt
import os
from datetime import datetime

def fix_admin_password():
    print("🔧 Fixing admin user password directly in MongoDB...")

    # MongoDB connection
    MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    client = pymongo.MongoClient(MONGODB_URL)
    db = client.chat_app
    users_collection = db.users

    # Admin user data
    admin_email = "admin@example.com"
    admin_password = "admin123"

    # Check if admin exists
    existing_admin = users_collection.find_one({"email": admin_email})
    if not existing_admin:
        print(f"❌ Admin user {admin_email} not found!")
        return

    print(f"Found admin user: {existing_admin['email']}")
    print(f"Current fields: {list(existing_admin.keys())}")

    # Hash password
    hashed_password = bcrypt.hashpw(admin_password.encode(), bcrypt.gensalt())

    # Update admin user with password
    result = users_collection.update_one(
        {"email": admin_email},
        {
            "$set": {
                "password": hashed_password,
                "username": "Admin",
                "role": "admin",
                "isFirstLogin": False,
                "is_online": False,
                "created_at": existing_admin.get("created_at", datetime.now().isoformat())
            }
        }
    )

    if result.modified_count > 0:
        print("✅ Admin password updated successfully!")
        print(f"Email: {admin_email}")
        print(f"Password: {admin_password}")
        print("You can now login with these credentials.")
    else:
        print("❌ Failed to update admin password.")

    # Verify the update
    updated_admin = users_collection.find_one({"email": admin_email})
    if updated_admin and "password" in updated_admin:
        print("✅ Verification: Admin user now has password field.")
    else:
        print("❌ Verification failed: Admin user still missing password field.")

if __name__ == "__main__":
    fix_admin_password()
    print("\n🎉 Admin fix completed!")
