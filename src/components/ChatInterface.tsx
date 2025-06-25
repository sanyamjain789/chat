import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import './ChatInterface.css'; // Add this for custom styles

interface User {
  _id: string; // Backend returns _id
  id?: string; // Login response returns id
  email: string;
  username: string | null;
  role: string;
  is_online: boolean;
  isFirstLogin: boolean;
}

interface Message {
  from: string;
  to: string;
  content: string;
  timestamp: string;
}

const ChatInterface: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [analysis, setAnalysis] = useState<string | null>(null);
  const [wsConnected, setWsConnected] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement | null>(null);
  const ws = useRef<WebSocket | null>(null);
  const navigate = useNavigate();

  const userId = localStorage.getItem('user_id');

  // Helper function to get the correct user ID
  const getUserId = (user: User) => {
    return user._id || user.id || '';
  };

  // Check authentication and fetch users
  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem('token');
      if (!token || !userId) {
        console.log('No token or user_id found, redirecting to login');
        navigate('/login');
        return;
      }
      try {
        const response = await axios.get('http://localhost:8000/api/users', {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        setUsers(response.data);
        setLoading(false);
      } catch (err) {
        setError('Failed to fetch users. Please try again.');
        setLoading(false);
      }
    };
    checkAuth();
  }, [navigate, userId]);

  // WebSocket connection
  useEffect(() => {
    if (userId && userId !== 'CURRENT_USER_ID' && userId !== 'undefined') {
      console.log('Connecting to WebSocket for user:', userId);
      ws.current = new WebSocket(`ws://localhost:8000/ws/chat/${userId}`);

      ws.current.onopen = () => {
        console.log('WebSocket connected');
        setWsConnected(true);
      };

      ws.current.onmessage = (event) => {
        console.log('Received message:', event.data);
        const data = JSON.parse(event.data);
        setMessages((prev) => [
          ...prev,
          {
            from: String(data.from),
            to: String(userId),
            content: data.message,
            timestamp: data.timestamp || new Date().toISOString(),
          },
        ]);
      };

      ws.current.onerror = (error) => {
        console.error('WebSocket error:', error);
        setWsConnected(false);
      };

      ws.current.onclose = () => {
        console.log('WebSocket disconnected');
        setWsConnected(false);
      };

      return () => {
        if (ws.current) {
          ws.current.close();
        }
      };
    }
  }, [userId]);

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Fetch messages when user changes
  useEffect(() => {
    if (selectedUser && userId) {
      const fetchMessages = async () => {
        const token = localStorage.getItem('token');
        try {
          const response = await axios.get(
            `http://localhost:8000/api/messages/${userId}`,
            { headers: { Authorization: `Bearer ${token}` } }
          );

          // Filter messages for this specific chat
          const selectedUserId = getUserId(selectedUser);
          const chatMessages = response.data.filter((msg: any) =>
            (msg.sender_id === userId && msg.receiver_id === selectedUserId) ||
            (msg.sender_id === selectedUserId && msg.receiver_id === userId)
          );

          // Convert to frontend format
          const formattedMessages = chatMessages.map((msg: any) => ({
            from: msg.sender_id,
            to: msg.receiver_id,
            content: msg.content,
            timestamp: msg.timestamp
          }));

          setMessages(formattedMessages);
          console.log('Fetched messages for chat:', formattedMessages);
        } catch (err) {
          console.error('Failed to fetch messages:', err);
          setMessages([]);
        }
      };
      fetchMessages();
    }
  }, [selectedUser, userId]);

  // Update analysis when user changes
  useEffect(() => {
    if (selectedUser) {
      setAnalysis('Analysis data (cached via Redis) will appear here.');
    } else {
      setAnalysis(null);
    }
  }, [selectedUser]);

  const sendMessage = () => {
    if (input.trim() && selectedUser && ws.current && wsConnected) {
      const selectedUserId = getUserId(selectedUser);
      const messageData = {
        recipient_id: selectedUserId,
        message: input,
      };

      console.log('Sending message:', messageData);
      ws.current.send(JSON.stringify(messageData));

      // Add message to local state immediately
      const newMessage = {
        from: String(userId),
        to: String(selectedUserId),
        content: input,
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, newMessage]);
      setInput("");
      console.log('Message added to state:', newMessage);
      console.log('Total messages now:', messages.length + 1);
    } else {
      console.log('Cannot send message:', {
        input: input.trim(),
        selectedUser: !!selectedUser,
        ws: !!ws.current,
        wsConnected
      });
    }
  };

  useEffect(() => {
    const handleStorageChange = (event: StorageEvent) => {
      if (event.key === 'token') {
        // Token changed in another tab
        window.location.reload(); // Or call logout()
      }
    };
    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, []);

  // Always return JSX - handle loading and error states
  if (loading) {
    return (
      <div className="d-flex align-items-center justify-content-center vh-100">
        <div className="fs-4">Loading...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="d-flex align-items-center justify-content-center vh-100">
        <div className="fs-4 text-danger">{error}</div>
      </div>
    );
  }

  if (!userId || userId === 'CURRENT_USER_ID' || userId === 'undefined') {
    return (
      <div className="d-flex align-items-center justify-content-center vh-100">
        <div className="fs-4 text-danger">Please login first</div>
      </div>
    );
  }

  const filteredUsers = users; // No filter

  return (
    <div className="container-fluid chat-bg vh-100">
      <div className="row h-100">
        {/* Left: Analysis */}
        <div className="col-2 d-flex flex-column p-0 border-end bg-white analysis-panel">
          <div className="p-3 border-bottom bg-success text-white">
            <h5 className="mb-0">Analysis</h5>
          </div>
          <div className="flex-grow-1 p-3 overflow-auto">
            <div className="bg-light p-3 rounded shadow-sm text-secondary">
              {analysis || 'Select a user to see analysis.'}
            </div>
            {/* Debug Panel */}
            <div className="mt-3 p-2 bg-warning bg-opacity-10 rounded">
              <small className="text-muted">
                <strong>Debug Info:</strong><br/>
                User ID: {userId}<br/>
                WS Connected: {wsConnected ? 'Yes' : 'No'}<br/>
                Messages: {messages.length}<br/>
                Selected User: {selectedUser ? getUserId(selectedUser) : 'None'}
              </small>
            </div>
          </div>
        </div>
        {/* Center: Chat Area */}
        <div className="col-8 d-flex flex-column p-0 chat-area">
          {/* Chat Header */}
          <div className="p-3 border-bottom d-flex align-items-center chat-header">
            {selectedUser ? (
              <>
                <div className="rounded-circle bg-success text-white d-flex align-items-center justify-content-center me-3" style={{width: 40, height: 40, fontWeight: 'bold'}}>
                  {selectedUser.username ? selectedUser.username[0].toUpperCase() : selectedUser.email[0].toUpperCase()}
                </div>
                <div>
                  <div className="fw-semibold">{selectedUser.username || selectedUser.email}</div>
                  <div className="small text-muted">
                    <span className={`me-1 badge rounded-pill ${selectedUser.is_online ? 'bg-success' : 'bg-secondary'}`}></span>
                    {selectedUser.is_online ? 'Online' : 'Offline'}
                    {wsConnected && <span className="ms-2 text-success">● Connected</span>}
                  </div>
                </div>
              </>
            ) : (
              <div className="text-muted">Select a user to start chatting</div>
            )}
          </div>
          {/* Messages */}
          <div className="flex-grow-1 p-4 overflow-auto chat-messages">
            {selectedUser ? (
              messages.length > 0 ? (
                messages.map((msg, idx) => (
                  <div
                    key={idx}
                    className={`d-flex mb-2 ${msg.from === userId ? 'justify-content-end' : 'justify-content-start'}`}
                  >
                    <div className={`px-3 py-2 rounded-4 shadow-sm ${msg.from === userId ? 'bg-success text-white' : 'bg-light text-dark'}`}
                         style={{maxWidth: '60%'}}>
                      {msg.content}
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center text-muted mt-5">No messages yet. Start chatting!</div>
              )
            ) : (
              <div className="text-center text-muted mt-5">Select a user to start chatting.</div>
            )}
            <div ref={messagesEndRef} />
          </div>
          {/* Input */}
          {selectedUser && (
            <div className="p-3 border-top bg-light d-flex align-items-center chat-input">
              <input
                className="form-control rounded-pill me-2"
                value={input}
                onChange={e => setInput(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && sendMessage()}
                placeholder="Type your message..."
              />
              <button
                className="btn btn-success rounded-pill px-4"
                onClick={sendMessage}
                disabled={!wsConnected}
              >
                Send
              </button>
            </div>
          )}
        </div>
        {/* Right: User List */}
        <div className="col-2 d-flex flex-column p-0 border-start bg-white user-list-panel">
          <div className="p-3 border-bottom bg-success text-white">
            <h5 className="mb-0">Users</h5>
          </div>
          <div className="flex-grow-1 overflow-auto">
            {filteredUsers
              .map(user => (
                <div
                  key={getUserId(user)}
                  className={`d-flex align-items-center gap-2 p-3 border-bottom user-list-item ${selectedUser && getUserId(selectedUser) === getUserId(user) ? 'bg-success bg-opacity-10' : 'hover-bg-success'}`}
                  style={{cursor: 'pointer'}}
                  onClick={() => setSelectedUser(user)}
                >
                  <div className="rounded-circle bg-success text-white d-flex align-items-center justify-content-center me-2" style={{width: 36, height: 36, fontWeight: 'bold'}}>
                    {user.username ? user.username[0].toUpperCase() : user.email[0].toUpperCase()}
                  </div>
                  <div className="flex-grow-1">
                    <div className="fw-semibold">{user.username || user.email}</div>
                    <div className="small text-muted">{user.role}</div>
                  </div>
                  <span className={`ms-2 badge rounded-pill ${user.is_online ? 'bg-success' : 'bg-secondary'}`}></span>
                </div>
              ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;
