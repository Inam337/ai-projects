import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  // For chat endpoints, use session token; for auth endpoints, use user token
  const isChatEndpoint = config.url?.startsWith('/chatbot/');
  const tokenKey = isChatEndpoint ? 'session_token' : 'auth_token';
  const token = localStorage.getItem(tokenKey);
  
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear both tokens on auth error
      localStorage.removeItem('auth_token');
      localStorage.removeItem('session_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth endpoints
export const authApi = {
  register: (email: string, password: string) =>
    api.post('/auth/register', { email, password }),
  
  login: (username: string, password: string) =>
    api.post('/auth/login', new URLSearchParams({
      username,
      password,
      grant_type: 'password'
    }), {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    }),
  
  createSession: () =>
    api.post('/auth/session'),
  
  getSessions: () =>
    api.get('/auth/sessions'),
  
  updateSessionName: (sessionId: string, name: string) =>
    api.patch(`/auth/session/${sessionId}/name`, new URLSearchParams({ name }), {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    }),
  
  deleteSession: (sessionId: string) =>
    api.delete(`/auth/session/${sessionId}`),
};

// Chat endpoints
export const chatApi = {
  sendMessage: (messages: Array<{ role: string; content: string }>) =>
    api.post('/chatbot/chat', { messages }),
  
  sendMessageStream: (messages: Array<{ role: string; content: string }>) =>
    api.post('/chatbot/chat/stream', { messages }, {
      responseType: 'stream'
    }),
  
  getMessages: () =>
    api.get('/chatbot/messages'),
  
  getSessionContext: () =>
    api.get('/chatbot/session/context'),
  
  clearHistory: () =>
    api.delete('/chatbot/messages'),
  
  analyzeImage: async (imageFile: File) => {
    try {
      const formData = new FormData();
      // 'image_file' must match your FastAPI parameter name
      formData.append('image_file', imageFile, imageFile.name);
      formData.append('instruction', '');
      formData.append('produce_audio', '');
      
      console.log('Sending image to analyze API...');
      const response = await fetch('http://localhost:8002/analyze', {
        method: 'POST',
        body: formData,
        headers: {
          // Don't set Content-Type, let browser set it with boundary
        }
      });
      
      console.log('Analyze API response status:', response.status);
      
      if (!response.ok) {
        let errorText = 'Unknown error';
        try {
          errorText = await response.text();
        } catch (e) {
          console.error('Could not read error response:', e);
        }
        console.error('Image analysis failed:', {
          status: response.status,
          statusText: response.statusText,
          error: errorText
        });
        throw new Error(`Failed to analyze image: ${response.status} ${response.statusText} - ${errorText}`);
      }
      
      const text = await response.text();
      console.log('Image analysis success, received text length:', text.length);
      return { data: { text } };
    } catch (error) {
      console.error('Image analysis error:', error);
      throw error;
    }
  },
};

export default api;
