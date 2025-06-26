import asyncio
import motor.motor_asyncio
import bcrypt
from datetime import datetime

async def init_admin():
    # MongoDB connection
    client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.chat_app
    users_collection = db.users

    # Admin credentials
    admin_email = "superadmin@gmail.com"
    admin_password = "admin123@"  # You can change this password

    # Check if admin already exists
    admin = await users_collection.find_one({"email": admin_email})
    if admin:
        print("Admin user already exists")
        return

    # Create admin user
    hashed_password = bcrypt.hashpw(admin_password.encode(), bcrypt.gensalt())
    admin_user = {
        "email": admin_email,
        "password": hashed_password,
        "username": "Admin",
        "role": "admin",
        "isFirstLogin": False,
        "created_at": datetime.now().isoformat(),
        "last_seen": None,
        "is_online": False
    }

    result = await users_collection.insert_one(admin_user)
    print(f"Admin user created successfully!")
    print(f"Email: {admin_email}")
    print(f"Password: {admin_password}")
    print(f"Please change these credentials after first login for security.")

if __name__ == "__main__":
    asyncio.run(init_admin())
