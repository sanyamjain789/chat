import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material';
import Login from './components/Login';
import Register from './components/Register';
import ChangePassword from './components/ChangePassword';
import ChatInterface from './components/ChatInterface';
import AdminDashboard from './components/AdminDashboard';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { CircularProgress, Box, Typography } from '@mui/material';
import './App.css';

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

const LoadingScreen = () => (
  <Box
    display="flex"
    flexDirection="column"
    alignItems="center"
    justifyContent="center"
    minHeight="100vh"
    bgcolor="background.default"
  >
    <CircularProgress size={60} />
    <Typography variant="h6" mt={2}>
      Loading...
    </Typography>
  </Box>
);

interface PrivateRouteProps {
  children: React.ReactNode;
}

const PrivateRoute: React.FC<PrivateRouteProps> = ({ children }) => {
  const { currentUser, loading } = useAuth();

  if (loading) {
    return <LoadingScreen />;
  }

  return currentUser ? <>{children}</> : <Navigate to="/login" />;
};

const AdminRoute: React.FC<PrivateRouteProps> = ({ children }) => {
  const { currentUser, loading } = useAuth();

  if (loading) {
    return <LoadingScreen />;
  }

  return currentUser?.role === 'admin' ? <>{children}</> : <Navigate to="/chat" />;
};

const FirstLoginRoute: React.FC<PrivateRouteProps> = ({ children }) => {
  const { currentUser, loading } = useAuth();

  if (loading) {
    return <LoadingScreen />;
  }

  if (!currentUser) return <Navigate to="/login" />;
  return currentUser.isFirstLogin ? <>{children}</> : <Navigate to="/chat" />;
};

const AppRoutes: React.FC = () => {
  const { currentUser } = useAuth();

  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route
        path="/change-password"
        element={
          <FirstLoginRoute>
            <ChangePassword />
          </FirstLoginRoute>
        }
      />
      <Route
        path="/admin"
        element={
          <AdminRoute>
            <AdminDashboard />
          </AdminRoute>
        }
      />
      <Route
        path="/chat"
        element={
          <PrivateRoute>
            <ChatInterface />
          </PrivateRoute>
        }
      />
      <Route path="/" element={<Navigate to="/login" replace />} />
    </Routes>
  );
};

const App: React.FC = () => {
  const [isBackendAvailable, setIsBackendAvailable] = useState<boolean | null>(null);

  useEffect(() => {
    const checkBackend = async () => {
      try {
        const response = await fetch('http://localhost:8000/');
        if (response.ok) {
          setIsBackendAvailable(true);
        } else {
          setIsBackendAvailable(false);
        }
      } catch (error) {
        setIsBackendAvailable(false);
      }
    };

    checkBackend();
  }, []);

  if (isBackendAvailable === null) {
    return <LoadingScreen />;
  }

  if (isBackendAvailable === false) {
    return (
      <Box
        display="flex"
        flexDirection="column"
        alignItems="center"
        justifyContent="center"
        minHeight="100vh"
        bgcolor="background.default"
      >
        <Typography variant="h5" color="error" gutterBottom>
          Backend server is not available
        </Typography>
        <Typography variant="body1">
          Please make sure the backend server is running on http://localhost:8000
        </Typography>
      </Box>
    );
  }

  return (
    <ThemeProvider theme={theme}>
      <AuthProvider>
        <Router>
          <AppRoutes />
        </Router>
      </AuthProvider>
    </ThemeProvider>
  );
};

export default App;
