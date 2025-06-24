export interface User {
  _id: string;
  email: string;
  username?: string;
  role: 'admin' | 'customer';
  isFirstLogin: boolean;
  created_at: string;
  last_seen?: string;
  is_online?: boolean;
}

export interface Message {
  _id: string;
  content: string;
  sender_id: string;
  receiver_id: string;
  timestamp: string;
  status: 'sent' | 'delivered' | 'read';
  is_read: boolean;
  read_at?: string;
}

export interface ChatHistory {
  id: string;
  userId: string;
  messages: Message[];
  lastUpdated: Date;
}

export interface Analytics {
  totalMessages: number;
  averageResponseTime: number;
  userEngagement: number;
  chatLogs: Message[];
}

export interface UserStatus {
  user_id: string;
  is_online: boolean;
  last_seen: string;
}

export interface ChatAnalytics {
  total_messages: number;
  messages_today: number;
  average_response_time: number;
  active_users: number;
  popular_topics: Array<{
    topic: string;
    count: number;
  }>;
}

export interface SearchResult {
  messages: Message[];
  users: User[];
  topics: string[];
}

export interface AdminStats {
  total_users: number;
  total_messages: number;
  active_users: number;
  messages_today: number;
  average_response_time: number;
}
