from fastapi import FastAPI, HTTPException, Depends, status, Body, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime, timedelta
import motor.motor_asyncio
from bson import ObjectId
import bcrypt
from jose import jwt, JWTError
import logging
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import os
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Chat Application API",
    description="Backend API for the chat application with admin and customer features",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection
try:
    MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URL)
    db = client.chat_app
    users_collection = db.users
    messages_collection = db.messages
    logger.info("Successfully connected to MongoDB")
except Exception as e:
    logger.error(f"Failed to connect to MongoDB: {e}")
    raise

# WebSocket active connections
active_connections: Dict[str, WebSocket] = {}

# JWT settings
SECRET_KEY = "your-secret-key"  # In production, use environment variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Models
class User(BaseModel):
    email: str
    password: str
    username: Optional[str] = None
    role: str = "customer"
    isFirstLogin: bool = True
    created_at: str = datetime.now().isoformat()
    last_seen: Optional[str] = None
    is_online: bool = False

class UserResponse(BaseModel):
    _id: str
    email: str
    username: Optional[str] = None
    role: str
    isFirstLogin: bool
    created_at: str
    last_seen: Optional[str]
    is_online: bool

class Message(BaseModel):
    sender_id: str
    receiver_id: str
    content: str
    timestamp: str = datetime.now().isoformat()
    status: str = "sent"
    is_read: bool = False
    read_at: Optional[str] = None

class AdminStats(BaseModel):
    total_users: int
    total_messages: int
    active_users: int
    messages_today: int
    average_response_time: float

# Helper functions
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = await users_collection.find_one({"_id": ObjectId(user_id)})
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Routes
@app.get("/")
async def root():
    return JSONResponse(
        content={
            "message": "Welcome to Chat Application API",
            "version": "1.0.0",
            "docs_url": "/docs",
            "redoc_url": "/redoc"
        }
    )

@app.post("/api/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        logger.info(f"Login attempt for email: {form_data.username}")

        # Find user
        user = await users_collection.find_one({"email": form_data.username})
        if not user:
            logger.warning(f"Login failed: User not found for email {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        # Verify password
        hashed_pw = user["password"]
        if isinstance(hashed_pw, str):
            hashed_pw = hashed_pw.encode()
        if not bcrypt.checkpw(form_data.password.encode(), hashed_pw):
            logger.warning(f"Login failed: Invalid password for email {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        # Create token
        access_token = create_access_token(data={"sub": str(user["_id"])})

        # Update last seen
        await users_collection.update_one(
            {"_id": user["_id"]},
            {
                "$set": {
                    "last_seen": datetime.now().isoformat(),
                    "is_online": True
                }
            }
        )

        logger.info(f"Login successful for email: {form_data.username}")

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": str(user["_id"]),
                "email": user["email"],
                "username": user.get("username"),
                "role": user.get("role", "customer"),
                "isFirstLogin": user.get("isFirstLogin", True),
                "created_at": user.get("created_at"),
                "last_seen": user.get("last_seen"),
                "is_online": user.get("is_online", False)
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during login"
        )

@app.post("/api/admin/create")
async def create_customer(user: User, current_user: dict = Depends(get_current_user)):
    try:
        if current_user.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Admin access required")

        if await users_collection.find_one({"email": user.email}):
            raise HTTPException(status_code=400, detail="Email already registered")

        hashed_password = bcrypt.hashpw(user.password.encode(), bcrypt.gensalt())
        user_dict = user.dict()
        user_dict["password"] = hashed_password
        result = await users_collection.insert_one(user_dict)

        return {
            "_id": str(result.inserted_id),
            "email": user.email,
            "username": user.username,
            "role": user.role,
            "isFirstLogin": user.isFirstLogin,
            "created_at": user.created_at
        }
    except Exception as e:
        logger.error(f"Create customer error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/admin/users")
async def get_users(current_user: dict = Depends(get_current_user)):
    try:
        if current_user.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Admin access required")

        users = []
        async for user in users_collection.find({"role": "customer"}):
            users.append({
                "_id": str(user["_id"]),
                "email": user["email"],
                "username": user.get("username"),
                "created_at": user.get("created_at"),
                "last_seen": user.get("last_seen"),
                "is_online": user.get("is_online", False)
            })
        return users
    except Exception as e:
        logger.error(f"Get users error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/admin/stats")
async def get_admin_stats(current_user: dict = Depends(get_current_user)):
    try:
        if current_user.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Admin access required")

        total_users = await users_collection.count_documents({"role": "customer"})
        total_messages = await messages_collection.count_documents({})

        yesterday = datetime.now() - timedelta(days=1)
        active_users = len(await messages_collection.distinct("sender_id", {"timestamp": {"$gte": yesterday.isoformat()}}))

        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        messages_today = await messages_collection.count_documents({"timestamp": {"$gte": today.isoformat()}})

        messages = await messages_collection.find().sort("timestamp", -1).limit(1000).to_list(length=1000)
        response_times = []
        for i in range(1, len(messages)):
            if messages[i-1]["sender_id"] != messages[i]["sender_id"]:
                time_diff = datetime.fromisoformat(messages[i-1]["timestamp"]) - datetime.fromisoformat(messages[i]["timestamp"])
                response_times.append(time_diff.total_seconds())

        avg_response_time = sum(response_times) / len(response_times) if response_times else 0

        return AdminStats(
            total_users=total_users,
            total_messages=total_messages,
            active_users=active_users,
            messages_today=messages_today,
            average_response_time=avg_response_time
        )
    except Exception as e:
        logger.error(f"Get stats error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/users/change-password")
async def change_password(new_password: str, current_user: dict = Depends(get_current_user)):
    try:
        hashed_password = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt())
        await users_collection.update_one(
            {"_id": current_user["_id"]},
            {
                "$set": {
                    "password": hashed_password,
                    "isFirstLogin": False
                }
            }
        )
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Change password error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/messages/{user_id}")
async def get_messages(user_id: str, current_user: dict = Depends(get_current_user)):
    try:
        messages = []
        async for message in messages_collection.find({
            "$or": [
                {"sender_id": user_id},
                {"receiver_id": user_id}
            ]
        }):
            messages.append({
                "_id": str(message["_id"]),
                "sender_id": message["sender_id"],
                "receiver_id": message["receiver_id"],
                "content": message["content"],
                "timestamp": message["timestamp"],
                "status": message["status"],
                "is_read": message["is_read"],
                "read_at": message.get("read_at")
            })
        return messages
    except Exception as e:
        logger.error(f"Get messages error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/messages/send")
async def send_message(message: Message, current_user: dict = Depends(get_current_user)):
    try:
        message_dict = message.dict()
        result = await messages_collection.insert_one(message_dict)
        message_dict["_id"] = str(result.inserted_id)
        return message_dict
    except Exception as e:
        logger.error(f"Send message error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/messages/read")
async def mark_messages_as_read(sender_id: str, receiver_id: str, current_user: dict = Depends(get_current_user)):
    try:
        await messages_collection.update_many(
            {
                "sender_id": sender_id,
                "receiver_id": receiver_id,
                "is_read": False
            },
            {
                "$set": {
                    "is_read": True,
                    "read_at": datetime.now().isoformat(),
                    "status": "read"
                }
            }
        )
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Mark messages as read error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/users/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    try:
        return {
            "_id": str(current_user["_id"]),
            "email": current_user["email"],
            "username": current_user.get("username"),
            "role": current_user.get("role", "customer"),
            "isFirstLogin": current_user.get("isFirstLogin", True),
            "created_at": current_user.get("created_at"),
            "last_seen": current_user.get("last_seen"),
            "is_online": current_user.get("is_online", False)
        }
    except Exception as e:
        logger.error(f"Get current user info error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/users/create")
async def create_user(user: User = Body(...)):
    if await users_collection.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = bcrypt.hashpw(user.password.encode(), bcrypt.gensalt())
    user_dict = user.dict()
    user_dict["password"] = hashed_password
    result = await users_collection.insert_one(user_dict)
    return {"_id": str(result.inserted_id), "email": user.email}

@app.post("/api/auth/login")
async def login(data: dict = Body(...)):
    email = data.get("email")
    password = data.get("password")
    user = await users_collection.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Fix password checking
    hashed_pw = user["password"]
    if isinstance(hashed_pw, str):
        hashed_pw = hashed_pw.encode()
    if not bcrypt.checkpw(password.encode(), hashed_pw):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Generate and return a token here if you use JWT, or just return user info
    access_token = create_access_token(data={"sub": str(user["_id"])})

    # Update last seen
    await users_collection.update_one(
        {"_id": user["_id"]},
        {
            "$set": {
                "last_seen": datetime.now().isoformat(),
                "is_online": True
            }
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": str(user["_id"]),
            "email": user["email"],
            "username": user.get("username"),
            "role": user.get("role", "customer"),
            "isFirstLogin": user.get("isFirstLogin", True),
            "created_at": user.get("created_at"),
            "last_seen": user.get("last_seen"),
            "is_online": user.get("is_online", False)
        }
    }

@app.websocket("/ws/chat/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    try:
        await websocket.accept()
        active_connections[user_id] = websocket
        logger.info(f"WebSocket connected for user: {user_id}")

        # Update user status to online
        await users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"is_online": True}}
        )

        while True:
            try:
                data = await websocket.receive_json()
                recipient_id = data.get("recipient_id")
                message = data.get("message")

                if recipient_id and message:
                    # Save message to database
                    message_doc = {
                        "sender_id": user_id,
                        "receiver_id": recipient_id,
                        "content": message,
                        "timestamp": datetime.now().isoformat(),
                        "status": "sent",
                        "is_read": False
                    }
                    await messages_collection.insert_one(message_doc)
                    logger.info(f"Message saved to database: {user_id} -> {recipient_id}")

                    # Send to recipient if online
                    if recipient_id in active_connections:
                        try:
                            await active_connections[recipient_id].send_json({
                                "from": user_id,
                                "message": message,
                                "timestamp": message_doc["timestamp"]
                            })
                            logger.info(f"Message sent from {user_id} to {recipient_id}")
                        except Exception as e:
                            logger.error(f"Failed to send message to {recipient_id}: {e}")
                            # Remove broken connection
                            if recipient_id in active_connections:
                                del active_connections[recipient_id]
                    else:
                        logger.info(f"Recipient {recipient_id} not online")
                else:
                    logger.warning(f"Invalid message format from {user_id}: {data}")
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON from {user_id}: {e}")
            except Exception as e:
                logger.error(f"Error processing message from {user_id}: {e}")
                break

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for user: {user_id}")
    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {e}")
    finally:
        # Clean up
        if user_id in active_connections:
            del active_connections[user_id]

        # Update user status to offline
        try:
            await users_collection.update_one(
                {"_id": ObjectId(user_id)},
                {
                    "$set": {
                        "is_online": False,
                        "last_seen": datetime.now().isoformat()
                    }
                }
            )
        except Exception as e:
            logger.error(f"Failed to update user status for {user_id}: {e}")

@app.get("/api/users")
async def get_all_users():
    users = []
    async for user in users_collection.find({}, {"password": 0}):  # Exclude password
        users.append({
            "_id": str(user["_id"]),
            "email": user["email"],
            "username": user.get("username"),
            "role": user.get("role", "customer"),
            "created_at": user.get("created_at"),
            "last_seen": user.get("last_seen"),
            "is_online": user.get("is_online", False)
        })
    return users

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )
