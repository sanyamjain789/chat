export interface User {
  _id: string;
  email: string;
  username?: string;
  role: 'user' | 'admin';
  is_online: boolean;
  last_seen: string;
  isFirstLogin: boolean;
}

export interface Message {
  _id: string;
  sender_id: string;
  receiver_id: string;
  content: string;
  timestamp: string;
  is_read: boolean;
  status: 'sent' | 'delivered' | 'read';
}
