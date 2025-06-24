# Real-time Chat Application

This is a real-time chat application built with React, FastAPI, MongoDB, Redis, and AWS Bedrock.

## Features

- User authentication with email/password
- Admin dashboard for customer management
- Real-time chat interface
- Message history
- Search and analytics
- AWS Bedrock integration for AI responses
- Redis caching for improved performance

## Prerequisites

- Node.js and npm
- Python 3.8+
- MongoDB Atlas account
- Redis server
- AWS account with Bedrock access
- Firebase project

## Frontend Setup

1. Navigate to the frontend directory:

```bash
cd chat-app
```

2. Install dependencies:

```bash
npm install
```

3. Create a `.env` file in the frontend directory with your Firebase configuration:

```
REACT_APP_FIREBASE_API_KEY=your-api-key
REACT_APP_FIREBASE_AUTH_DOMAIN=your-auth-domain
REACT_APP_FIREBASE_PROJECT_ID=your-project-id
REACT_APP_FIREBASE_STORAGE_BUCKET=your-storage-bucket
REACT_APP_FIREBASE_MESSAGING_SENDER_ID=your-messaging-sender-id
REACT_APP_FIREBASE_APP_ID=your-app-id
```

4. Start the development server:

```bash
npm start
```

## Backend Setup

1. Navigate to the backend directory:

```bash
cd backend
```

2. Create a virtual environment:

```bash
python -m venv venv
```

3. Activate the virtual environment:

- Windows:

```bash
.\venv\Scripts\activate
```

- Unix/MacOS:

```bash
source venv/bin/activate
```

4. Install dependencies:

```bash
pip install -r requirements.txt
```

5. Create a `.env` file in the backend directory with your configuration:

```
MONGODB_URL=your-mongodb-atlas-url
REDIS_HOST=your-redis-host
REDIS_PORT=6379
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_REGION=us-east-1
```

6. Start the backend server:

```bash
uvicorn main:app --reload
```

## Project Structure

```
.
├── chat-app/                 # Frontend React application
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── contexts/        # React contexts
│   │   ├── types/          # TypeScript types
│   │   └── config/         # Configuration files
│   └── package.json
│
└── backend/                 # FastAPI backend
    ├── main.py             # Main application file
    ├── requirements.txt    # Python dependencies
    └── .env               # Environment variables
```

## API Endpoints

### Authentication

- POST /api/users - Create a new user
- GET /api/users/{email} - Get user details

### Chat

- POST /api/messages - Send a message
- GET /api/messages/{user_id} - Get user messages

### Analytics

- GET /api/analytics/{user_id} - Get user analytics

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request
