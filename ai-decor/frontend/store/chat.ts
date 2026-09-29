import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { authApi, chatApi } from '@/lib/api';
import { Session, Message, SessionResponse, ChatResponse } from '@/types';
import { generateSessionName } from '@/lib/session-names';

interface OnboardingData {
  image: File | null;
  roomType: string;
  style: string;
  budget: string;
  timeline: string;
  colors: string[];
  goals: string[];
}

interface ImageAnalysisData {
  detections?: Array<{
    label: string;
    conf: number;
    box: number[];
    crop_path?: string;
  }>;
  recommendations?: Array<{
    'Room Color Analysis'?: {
      codes: string[];
      theme: string;
    };
    'Room Lightening Analysis'?: string;
    object?: string;
    position?: string;
    reference_color?: string;
    justification?: string;
    trend_analysis?: string;
  }>;
  annotated_image_b64?: string;
  audio_path?: string | null;
  roomType?: string;
  styleDetected?: string;
  imageUrl: string;
}

interface Product {
  id: string;
  name: string;
  description: string;
  price?: string;
  image?: string;
  rating?: string;
  link?: string;
  messageId: string;
  timestamp: string;
}

interface ChatState {
  sessions: Session[];
  currentSession: Session | null;
  messages: Message[];
  isLoading: boolean;
  isSending: boolean;
  isLoadingSession: boolean;
  error: string | null;
  isCreatingSession: boolean;
  showOnboarding: boolean;
  onboardingData: OnboardingData | null;
  currentImage: File | null;
  imageAnalysis: ImageAnalysisData | null;
  products: Product[];
  
  // Actions
  fetchSessions: () => Promise<void>;
  createSession: (name?: string) => Promise<Session>;
  selectSession: (sessionId: string) => Promise<void>;
  sendMessage: (message: string) => Promise<void>;
  sendMessageWithoutStore: (message: string) => Promise<Message[]>;
  loadMessages: () => Promise<void>;
  clearMessages: () => Promise<void>;
  deleteSession: (sessionId: string) => Promise<void>;
  clearCurrentSession: () => void;
  clearError: () => void;
  completeOnboarding: (data: OnboardingData) => void;
  skipOnboarding: () => void;
  setCurrentImage: (image: File | null, analysis: ImageAnalysisData | null) => void;
  extractAndStoreProducts: (messageId: string, content: string) => void;
  clearProducts: () => void;
}

export const useChatStore = create<ChatState>()(
  persist(
    (set, get) => ({
      sessions: [],
      currentSession: null,
      messages: [],
      isLoading: false,
      isSending: false,
      isLoadingSession: false,
      error: null,
      isCreatingSession: false,
      showOnboarding: false,
      onboardingData: null,
      currentImage: null,
      imageAnalysis: null,
      products: [],

      fetchSessions: async () => {
        set({ isLoading: true, error: null });
        try {
          const response = await authApi.getSessions();
          const sessions: Session[] = response.data.map((sessionData: SessionResponse) => ({
            id: sessionData.session_id,
            name: sessionData.name,
            user_id: 0, // Will be set by backend
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
            token: sessionData.token.access_token, // Store the session token
          }));
          
          set({ sessions, isLoading: false });
        } catch (error: unknown) {
          const errorMessage = (error as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Failed to load sessions';
          set({ 
            isLoading: false,
            error: errorMessage
          });
          throw error;
        }
      },

      createSession: async (name?: string) => {
        const { isCreatingSession } = get();
        if (isCreatingSession) {
          // Prevent multiple simultaneous session creation
          return get().currentSession!;
        }

        set({ isCreatingSession: true, error: null });
        try {
          const response = await authApi.createSession();
          const sessionData = response.data;
          
          // Store the session token for chat operations FIRST
          localStorage.setItem('session_token', sessionData.token.access_token);
          
          // Use the name from backend (already generated) or fallback to provided name
          const sessionName = sessionData.name || name || 'New Session';
          
          const newSession: Session = {
            id: sessionData.session_id,
            name: sessionName,
            user_id: 0, // Will be set by backend
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
            token: sessionData.token.access_token, // Store the session token
          };
          
          set((state) => ({
            sessions: [newSession, ...state.sessions],
            currentSession: newSession,
            messages: [], // Clear messages for new session
            isCreatingSession: false,
            showOnboarding: true, // Show onboarding for new sessions
          }));
          
          return newSession;
        } catch (error: unknown) {
          const errorMessage = (error as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Failed to create session';
          set({ 
            isCreatingSession: false,
            error: errorMessage
          });
          throw error;
        }
      },

      selectSession: async (sessionId: string) => {
        console.log(`selectSession called with sessionId: ${sessionId}`);
        set({ isLoadingSession: true, error: null });
        try {
          // First try to find session in the sessions list
          let session = get().sessions.find(s => s.id === sessionId);
          console.log(`Found session in list:`, session);
          
          if (!session) {
            // If session not found in list, we need to load sessions first
            console.log('Session not found in list, loading sessions first...');
            await get().fetchSessions();
            
            // Try again after loading sessions
            session = get().sessions.find(s => s.id === sessionId);
            console.log(`Found session after loading sessions:`, session);
          }
          
          if (session) {
            // Use the session's specific token for chat operations
            if (session.token) {
              localStorage.setItem('session_token', session.token);
              console.log('Session token set in localStorage');
            }
            
            set({ currentSession: session, messages: [] }); // Clear messages first
            
            // Always load messages when opening a session (whether new or existing)
            // This ensures chat history is visible immediately
            console.log(`Loading chat history for session: ${session.name}`);
            await get().loadMessages();
            console.log(`Chat history loaded for session: ${session.name}`);
          } else {
            console.error(`Session not found after loading sessions: ${sessionId}`);
            console.log('Available sessions:', get().sessions.map(s => ({ id: s.id, name: s.name })));
            throw new Error(`Session ${sessionId} not found`);
          }
          
          set({ isLoadingSession: false });
        } catch (error: unknown) {
          console.error('selectSession error:', error);
          const errorMessage = (error as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Failed to select session';
          set({ 
            isLoadingSession: false,
            error: errorMessage
          });
          throw error;
        }
      },

      sendMessage: async (message: string) => {
        const { currentSession, messages } = get();
        if (!currentSession) return;

        set({ isSending: true, error: null });
        
        // Add user message immediately to UI
        const userMessage: Message = {
          role: 'user',
          content: message,
        };
        
        // Update UI with user message immediately
        set({ messages: [...messages, userMessage] });

        try {
          // Send only the new user message to backend
          // This endpoint returns ONLY the new AI response, not full conversation
          console.log('Sending message and expecting only new AI response...');
          const response = await chatApi.sendMessage([userMessage]);
          
          // Append only the new AI response to existing messages
          // The response contains only the new AI message, not the full conversation
          set({
            messages: [...messages, userMessage, ...response.data.messages],
            isSending: false,
          });
          console.log(`Added ${response.data.messages.length} new AI response(s) to conversation`);
        } catch (error: unknown) {
          console.error('Chat API Error:', error);
          const errorMessage = (error as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Failed to send message';
          set({ 
            isSending: false,
            error: errorMessage
          });
          throw error;
        }
      },

      // Send message without storing in state (no localStorage persistence)
      // This sends the message to backend for context but doesn't update UI
      sendMessageWithoutStore: async (message: string): Promise<Message[]> => {
        const { currentSession, messages } = get();
        if (!currentSession) {
          throw new Error('No active session');
        }

        const userMessage: Message = {
          role: 'user',
          content: message,
        };

        try {
          // Send with full conversation history so backend maintains context
          // Backend will add this to its session history, but we won't update local state
          const fullConversation = [...messages, userMessage];
          console.log('Sending message to backend (without storing locally)...', {
            messageLength: message.length,
            conversationHistoryLength: messages.length,
            totalMessages: fullConversation.length
          });
          
          const response = await chatApi.sendMessage(fullConversation);
          
          // Backend receives the message and maintains context in session
          // But we don't update local messages array or persist anything
          console.log(`Message sent to backend successfully. Backend has context. Received ${response.data.messages.length} response(s) - NOT storing locally`);
          
          // Return response for potential use, but don't store in state
          return response.data.messages;
        } catch (error: unknown) {
          console.error('Chat API Error (without store):', error);
          const errorMessage = (error as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Failed to send message';
          throw new Error(errorMessage);
        }
      },

      loadMessages: async () => {
        set({ isLoading: true, error: null });
        try {
          // Use session context endpoint to get FULL chat history
          // This is only called when opening a session, not on every message
          console.log('Loading full chat history for session...');
          const response = await chatApi.getSessionContext();
          set({
            messages: response.data.messages,
            isLoading: false,
          });
          console.log(`Loaded ${response.data.messages.length} messages from full chat history`);
        } catch (error: unknown) {
          const errorMessage = (error as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Failed to load messages';
          set({ 
            isLoading: false,
            error: errorMessage
          });
          throw error;
        }
      },

      clearMessages: async () => {
        set({ isLoading: true, error: null });
        try {
          await chatApi.clearHistory();
          set({
            messages: [],
            isLoading: false,
          });
        } catch (error: unknown) {
          const errorMessage = (error as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Failed to clear messages';
          set({ 
            isLoading: false,
            error: errorMessage
          });
          throw error;
        }
      },

      deleteSession: async (sessionId: string) => {
        set({ isLoading: true, error: null });
        try {
          console.log(`Deleting session: ${sessionId}`);
          await authApi.deleteSession(sessionId);
          console.log(`Session ${sessionId} deleted successfully`);
          
          // Remove from sessions list and handle current session
          set((state) => {
            const updatedSessions = state.sessions.filter(s => s.id !== sessionId);
            const isCurrentSession = state.currentSession?.id === sessionId;
            
            // If deleting current session, switch to another session or clear
            let newCurrentSession = state.currentSession;
            let newMessages = state.messages;
            
            if (isCurrentSession) {
              newCurrentSession = updatedSessions.length > 0 ? updatedSessions[0] : null;
              newMessages = [];
              
              // If switching to another session, set its token
              if (newCurrentSession?.token) {
                localStorage.setItem('session_token', newCurrentSession.token);
              } else {
                localStorage.removeItem('session_token');
              }
            }
            
            return {
              sessions: updatedSessions,
              currentSession: newCurrentSession,
              messages: newMessages,
              isLoading: false,
            };
          });
        } catch (error: unknown) {
          const errorMessage = (error as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Failed to delete session';
          set({ 
            isLoading: false,
            error: errorMessage
          });
          throw error;
        }
      },

      clearCurrentSession: () => {
        set({
          currentSession: null,
          messages: [],
        });
      },

      clearError: () => set({ error: null }),

      completeOnboarding: (data: OnboardingData) => {
        set({ 
          showOnboarding: false, 
          onboardingData: data 
        });
        
        // Mock sending context to API (not implemented yet)
        console.log('Onboarding completed with data:', data);
        
        // In the future, this would send the data to the backend
        // await chatApi.sendContext(data);
      },

      skipOnboarding: () => {
        set({ 
          showOnboarding: false, 
          onboardingData: null 
        });
      },

      setCurrentImage: (image: File | null, analysis: ImageAnalysisData | null) => {
        set({ currentImage: image, imageAnalysis: analysis });
      },

      extractAndStoreProducts: (messageId: string, content: string) => {
        const products: Product[] = [];
        const productRegex = /(\d+)\.\s*\*\*([^*]+)\*\*\s*[^\n]*\n/g;
        let match;
        
        while ((match = productRegex.exec(content)) !== null) {
          const startIdx = match.index;
          const endIdx = content.indexOf('\n\n', startIdx);
          const productBlock = content.substring(startIdx, endIdx !== -1 ? endIdx : content.length);
          
          const name = match[2].trim();
          const descriptionMatch = productBlock.match(/Description:\s*([^\n]+)/i);
          const priceMatch = productBlock.match(/Price:\s*([^\n]+)/i);
          
          // Extract image from markdown image links
          const imageMatch = productBlock.match(/!\[([^\]]*)\]\(([^)]+)\)/);
          const productImage = imageMatch?.[2] || '';
          
          // Extract store link from regular markdown links
          let productLink = '';
          const allLinks = productBlock.match(/\[([^\]]+)\]\(([^)]+)\)/g) || [];
          
          for (const linkMatch of allLinks) {
            const fullMatch = linkMatch.match(/\[([^\]]+)\]\(([^)]+)\)/);
            if (fullMatch) {
              const linkUrl = fullMatch[2].trim();
              // Skip image URLs by checking file extension
              const isImageUrl = /\.(jpg|jpeg|png|gif|webp|svg|jfif|bmp)(\?|$|[/#])/i.test(linkUrl);
              // Only accept HTTP/HTTPS links that are not images
              if (linkUrl.startsWith('http') && !isImageUrl) {
                productLink = linkUrl;
                break; // Take first valid store link
              }
            }
          }
          
          if (name) {
            products.push({
              id: `${messageId}-product-${startIdx}`,
              messageId,
              timestamp: new Date().toISOString(),
              name,
              description: descriptionMatch?.[1]?.trim() || '',
              price: priceMatch?.[1]?.trim() || '',
              image: productImage,
              link: productLink,
            });
          }
        }

        if (products.length > 0) {
          set((state) => ({ products: [...state.products, ...products] }));
        }
      },

      clearProducts: () => {
        set({ products: [] });
      },
    }),
    {
      name: 'chat-storage',
      partialize: (state) => ({
        sessions: state.sessions,
        currentSession: state.currentSession,
      }),
    }
  )
);
