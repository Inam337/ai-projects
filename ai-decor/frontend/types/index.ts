// User types
export interface User {
  id: number;
  email: string;
  name?: string;
  created_at: string;
}

export interface UserCreate {
  email: string;
  password: string;
}

export interface UserLogin {
  email: string;
  password: string;
}

// Auth types
export interface Token {
  access_token: string;
  token_type: string;
  expires_at: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_at: string;
}

export interface UserResponse {
  id: number;
  email: string;
  token: Token;
}

// Session types
export interface Session {
  id: string;
  name: string;
  user_id: number;
  created_at: string;
  updated_at: string;
  token?: string; // Session-specific token for chat operations
}

export interface SessionResponse {
  session_id: string;
  name: string;
  token: Token;
}

// Chat types
export interface Message {
  role: 'user' | 'assistant' | 'system';
  content: string;
}

export interface ChatRequest {
  messages: Message[];
}

export interface ChatResponse {
  messages: Message[];
}

export interface StreamResponse {
  content: string;
  done: boolean;
}

// Legacy types for backward compatibility
export interface ChatSession {
  id: string;
  name: string;
  user_id: number;
  created_at: string;
  updated_at: string;
}

export interface ChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  expires_at: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterCredentials {
  email: string;
  password: string;
}
