import asyncio
import motor.motor_asyncio
import bcrypt
import os
from datetime import datetime

async def create_admin():
    # MongoDB connection
    MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URL)
    db = client.chat_app
    users_collection = db.users

    # Admin user data
    admin_email = "superadmin@gmail.com"
    admin_password = "admin123@"
    admin_username = "Admin"

    # Check if admin already exists
    existing_admin = await users_collection.find_one({"email": admin_email})
    if existing_admin:
        print(f"Admin user {admin_email} already exists!")
        return

    # Hash password
    hashed_password = bcrypt.hashpw(admin_password.encode(), bcrypt.gensalt())

    # Create admin user
    admin_user = {
        "email": admin_email,
        "username": admin_username,
        "password": hashed_password,
        "role": "admin",
        "isFirstLogin": False,
        "created_at": datetime.now().isoformat(),
        "last_seen": None,
        "is_online": False
    }

    result = await users_collection.insert_one(admin_user)
    print(f"✅ Admin user created successfully!")
    print(f"Email: {admin_email}")
    print(f"Password: {admin_password}")
    print(f"User ID: {result.inserted_id}")
    print("\nYou can now login with these credentials to access the admin dashboard.")

if __name__ == "__main__":
    asyncio.run(create_admin())
