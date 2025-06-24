import asyncio
import motor.motor_asyncio
import bcrypt
import os
from datetime import datetime

async def fix_admin_password():
    # MongoDB connection
    MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URL)
    db = client.chat_app
    users_collection = db.users

    # Admin user data
    admin_email = "admin@example.com"
    admin_password = "admin123"

    # Check if admin exists
    existing_admin = await users_collection.find_one({"email": admin_email})
    if not existing_admin:
        print(f"❌ Admin user {admin_email} not found!")
        return

    print(f"Found admin user: {existing_admin['email']}")

    # Hash password
    hashed_password = bcrypt.hashpw(admin_password.encode(), bcrypt.gensalt())

    # Update admin user with password
    result = await users_collection.update_one(
        {"email": admin_email},
        {
            "$set": {
                "password": hashed_password,
                "username": "Admin",
                "role": "admin",
                "isFirstLogin": False,
                "is_online": False
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

if __name__ == "__main__":
    asyncio.run(fix_admin_password())
