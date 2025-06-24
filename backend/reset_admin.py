import asyncio
import motor.motor_asyncio
import bcrypt
from datetime import datetime

async def reset_admin():
    # MongoDB connection
    client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.chat_app
    users_collection = db.users

    # Admin credentials
    admin_email = "admin@example.com"
    admin_password = "Admin@123"

    # Delete existing admin user
    result = await users_collection.delete_one({"email": admin_email})
    if result.deleted_count > 0:
        print("Existing admin user deleted successfully")

    # Create new admin user
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
    print("\nNew admin user created successfully!")
    print("----------------------------------------")
    print(f"Email: {admin_email}")
    print(f"Password: {admin_password}")
    print("----------------------------------------")
    print("Please use these credentials to login.")
    print("Remember to change the password after first login for security.")

if __name__ == "__main__":
    asyncio.run(reset_admin())
