# Chat Application

A real-time chat application built with React, TypeScript, and Material-UI.

## Features

- User authentication (login/register)
- Real-time messaging
- User online/offline status
- Message history
- Admin dashboard
- User management
- Analytics
- First-time login password change

## Prerequisites

- Node.js (v14 or higher)
- npm or yarn
- MongoDB
- Python 3.8+ (for backend)

## Setup

1. Clone the repository:

```bash
git clone <repository-url>
cd chat-app
```

2. Install dependencies:

```bash
npm install
```

3. Create a `.env` file in the root directory with the following variables:

```
REACT_APP_API_URL=http://localhost:8000
```

4. Start the development server:

```bash
npm start
```

The application will be available at `http://localhost:3000`.

## Project Structure

```
chat-app/
├── src/
│   ├── components/         # React components
│   ├── contexts/          # React contexts
│   ├── types.ts           # TypeScript interfaces
│   ├── App.tsx           # Main application component
│   └── index.tsx         # Application entry point
├── public/               # Static files
├── package.json         # Project dependencies
└── README.md           # Project documentation
```

## Available Scripts

- `npm start` - Runs the app in development mode
- `npm test` - Launches the test runner
- `npm run build` - Builds the app for production
- `npm run eject` - Ejects from Create React App

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
