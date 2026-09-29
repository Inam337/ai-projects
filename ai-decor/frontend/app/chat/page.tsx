'use client';

import { useEffect, useState, useRef } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useAuthStore } from '@/store/auth';
import { useChatStore } from '@/store/chat';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { 
  Send, 
  Image as ImageIcon, 
  Bot, 
  User, 
  ArrowLeft,
  Plus,
  LogOut,
  Sparkles,
  ShoppingBag,
  Settings,
  Eye
} from 'lucide-react';
import { useDropzone } from 'react-dropzone';
import Link from 'next/link';
import OnboardingFlow from '@/components/onboarding/OnboardingFlow';
import MessageRenderer from '@/components/chat/MessageRenderer';
import ImageAnalysisPanel from '@/components/chat/ImageAnalysisPanel';
import Logo from '@/components/ui/logo';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';

export default function ChatPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { isAuthenticated, logout, user } = useAuthStore();
  const { 
    currentSession, 
    messages, 
    isSending, 
    selectSession, 
    sendMessage, 
    createSession,
    loadMessages,
    isLoading,
    isLoadingSession,
    isCreatingSession,
    showOnboarding,
    completeOnboarding,
    skipOnboarding,
    currentImage,
    imageAnalysis,
    setCurrentImage,
    extractAndStoreProducts,
    products
  } = useChatStore();
  
  const [message, setMessage] = useState('');
  const [isUploading, setIsUploading] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const sessionId = searchParams.get('session');

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
      return;
    }

    console.log('Chat page useEffect triggered:', { sessionId, currentSession: !!currentSession, isCreatingSession });
    
    // Handle session loading
    if (sessionId) {
      // If we have a sessionId in URL, we need to load that session
      if (!currentSession || currentSession.id !== sessionId) {
        console.log(`Opening session from URL: ${sessionId}`);
        selectSession(sessionId);
      } else if (currentSession.id === sessionId && messages.length === 0) {
        // If we have the right session but no messages, load them
        console.log(`Loading messages for current session: ${sessionId}`);
        loadMessages();
      }
    } else if (!currentSession && !isCreatingSession) {
      console.log('Creating new session (no sessionId provided)');
      // Create new session if no session ID and no current session
      createSession();
    }
  }, [isAuthenticated, sessionId, currentSession?.id, messages.length]); // Add dependencies to check for changes

  useEffect(() => {
    scrollToBottom();
    
    // Extract products from messages
    messages.forEach((msg, index) => {
      if (msg.role === 'assistant') {
        extractAndStoreProducts(`msg-${index}`, msg.content);
      }
    });
  }, [messages, extractAndStoreProducts]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!message.trim() || isSending) return;

    const messageToSend = message.trim();
    setMessage('');

    try {
      await sendMessage(messageToSend);
    } catch (error) {
      console.error('Failed to send message:', error);
    }
  };

  const handleImageUpload = async (files: File[]) => {
    if (files.length === 0) return;

    setIsUploading(true);
    try {
      // For now, just show a message that image upload is not implemented
      // In the future, this could be integrated with the FastAPI template
      console.log('Image upload not implemented yet:', files[0]);
    } catch (error) {
      console.error('Failed to upload image:', error);
    } finally {
      setIsUploading(false);
    }
  };

  const handleLogout = () => {
    logout();
    router.push('/');
  };

  // Parse analysis response into structured data
  const parseAnalysisResponse = (text: string) => {
    try {
      // Try to parse as JSON first
      const jsonData = JSON.parse(text);
      
      console.log('Parsed JSON data:', jsonData);
      
      // Return the full API structure with imageUrl added
      return {
        ...jsonData,
        imageUrl: ''
      };
    } catch {
      // If not JSON, try to extract from text using regex
      // Extract primary color
      const primaryColorMatch = text.match(/primary.*?:?\s*(#[0-9A-Fa-f]{6}|#[0-9A-Fa-f]{3}|\w+)/i);
      const secondaryColorMatch = text.match(/secondary.*?:?\s*(#[0-9A-Fa-f]{6}|#[0-9A-Fa-f]{3}|\w+)/i);
      
      // Extract lighting
      const lightingMatch = text.match(/lighting.*?:ulti\s*([^\n,]+)/i);
      
      // Extract room type
      const roomTypeMatch = text.match(/room.*type.*?:?\s*([^\n,]+)/i);
      
      // Extract style
      const styleMatch = text.match(/style.*?:?\s*([^\n,]+)/i);
      
      return {
        wallColors: [
          primaryColorMatch?.[1] || '#6B7280',
          secondaryColorMatch?.[1] || '#E5E7EB'
        ],
        lighting: lightingMatch?.[1]?.trim() || 'Natural Light',
        roomType: roomTypeMatch?.[1]?.trim() || 'Living Room',
        styleDetected: styleMatch?.[1]?.trim() || 'Modern',
        imageUrl: ''
      };
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop: handleImageUpload,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png', '.gif', '.webp']
    },
    multiple: false
  });

  // Format onboarding data for sending to chat in a user-friendly way
  const formatOnboardingData = (data: {
    roomType: string;
    style: string;
    budget: string;
    timeline: string;
    colors: string[];
    goals: string[];
  }) => {
    const parts: string[] = [];
    
    // Start with a friendly intro
    if (data.roomType || data.style) {
      let intro = "I see you're working on";
      if (data.roomType) intro += ` a ${data.roomType}`;
      if (data.style) intro += ` with a ${data.style} style`;
      parts.push(intro + ".");
    }
    
    // Add budget and timeline if available
    if (data.budget || data.timeline) {
      let details = "";
      if (data.budget) details += `Budget: ${data.budget}`;
      if (data.budget && data.timeline) details += " • ";
      if (data.timeline) details += `Timeline: ${data.timeline}`;
      if (details) parts.push(details);
    }
    
    // Add preferences naturally
    if (data.colors.length > 0) {
      parts.push(`Color preferences: ${data.colors.join(', ')}`);
    }
    
    if (data.goals.length > 0) {
      parts.push(`Your goals: ${data.goals.join(', ').toLowerCase()}`);
    }
    
    return parts.join('\n');
  };

  // Show onboarding flow for new sessions
  if (showOnboarding && currentSession) {
    return (
      <OnboardingFlow 
        onComplete={async (data) => {
          completeOnboarding(data);
          
          // Send onboarding data to chat
          const formattedData = formatOnboardingData({
            roomType: data.roomType,
            style: data.style,
            budget: data.budget,
            timeline: data.timeline,
            colors: data.colors,
            goals: data.goals
          });
          
         
          // If image uploaded, analyze it and send to chat
          if (data.image) {
            setCurrentImage(data.image, null);
            setIsAnalyzing(true);
            
            // Automatically analyze the image and send result to chat
            try {
              const { chatApi } = await import('@/lib/api');
              const response = await chatApi.analyzeImage(data.image);
              const analysisText = response.data.text;
              console.log('Analysis text:', analysisText);
              
              // Parse and store the analysis
              if (analysisText) {
                const parsedAnalysis = parseAnalysisResponse(analysisText);
                const imageUrl = URL.createObjectURL(data.image);
                
                setCurrentImage(data.image, {
                  ...parsedAnalysis,
                  imageUrl
                });

                // Send a message to chat about the analysis
                if (parsedAnalysis.detections && parsedAnalysis.detections.length > 0) {
                  const detectionLabels = parsedAnalysis.detections.map((d: {label: string}) => d.label).join(', ');
                  const firstRec = parsedAnalysis.recommendations?.[0];
                  const theme = firstRec?.['Room Color Analysis']?.theme || 'Modern';
                  
                  await sendMessage(
                    `I've analyzed your room image! Here's what I found:\n\n` +
                    `**Detected Objects:** ${detectionLabels}\n\n` +
                    `**Design Theme:** ${theme}\n\n` +
                    `${formattedData ? `${formattedData}\n\n` : ''}` +
                    `I've prepared detailed product recommendations for your space. You can view the complete analysis in the panel on the right. Would you like me to suggest specific products or discuss any design elements?`
                  );
                }
              }
            } catch (error) {
              console.error('Failed to analyze image:', error);
              // Set mock analysis if API fails
              const mockAnalysis = {
                detections: [],
                recommendations: [],
                imageUrl: URL.createObjectURL(data.image)
              };
              setCurrentImage(data.image, mockAnalysis);
              
              // Send error message to chat
              await sendMessage(
                "I've uploaded your image, but I'm having trouble analyzing it right now. " +
                "Please try again or describe your room and I'll help you with design recommendations!"
              );
            } finally {
              setIsAnalyzing(false);
            }
          } else if (formattedData) {
            // Send onboarding data if no image was uploaded
            await sendMessage(
              `Great! I've got your preferences:\n\n${formattedData}\n\n` +
              `How can I help you with your ${data.roomType || 'design project'} today?`
            );
          }
        }}
        onSkip={skipOnboarding}
      />
    );
  }

  if (!currentSession || isCreatingSession || isLoading || isLoadingSession) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 flex items-center justify-center p-4">
        <div className="text-center max-w-md">
          <div className="relative mb-8">
            <div className="w-20 h-20 bg-gradient-to-br from-blue-500 via-purple-600 to-pink-500 rounded-2xl flex items-center justify-center shadow-xl mx-auto">
              <div className="animate-spin rounded-full h-16 w-16 border-4 border-white/30 border-t-white"></div>
            </div>
            <div className="absolute inset-0 flex items-center justify-center">
              <Sparkles className="w-8 h-8 text-white animate-pulse" />
            </div>
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            {isCreatingSession ? 'Creating new session...' : 
             isLoadingSession ? 'Opening session...' :
             isLoading ? 'Loading chat history...' : 'Loading session...'}
          </h2>
          <p className="text-gray-600">
            {isCreatingSession ? 'Preparing your design workspace' : 
             isLoadingSession ? 'Fetching your session details' :
             isLoading ? 'Retrieving your conversation history' : 'Getting everything ready...'}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white/95 backdrop-blur-sm border-b border-gray-200 px-4 py-3 sticky top-0 z-10">
        <div className={`${currentImage ? 'max-w-7xl' : 'max-w-7xl'} mx-auto flex items-center justify-between`}>
          <div className="flex items-center space-x-4">
            <Link href="/" className="text-gray-600 hover:text-gray-900">
              <ArrowLeft className="w-5 h-5" />
            </Link>
            <div className="hidden md:flex mr-3">
              <Logo size="sm" showText={false} />
            </div>
            <div>
              <h1 className="text-base md:text-lg font-semibold text-gray-900">
                {currentSession.name || 'New Design Session'}
              </h1>
              <p className="text-xs md:text-sm text-gray-500">
                Interior Design AI Assistant
              </p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            {currentImage && products.length > 0 && (
              <Button
                size="sm"
                onClick={() => router.push('/analysis')}
                className="cursor-pointer hidden md:flex bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white border-0 shadow-md hover:shadow-lg transition-all"
              >
                <Eye className="w-4 h-4 mr-2" />
                Analyze Match
              </Button>
            )}
            {products.length > 0 && (
              <Button
                size="sm"
                onClick={() => router.push('/listings')}
                className="hidden md:flex bg-blue-600 hover:bg-blue-700 text-white border-0 shadow-md hover:shadow-lg transition-all"
              >
                <ShoppingBag className="w-4 h-4 mr-2" />
                Review All ({products.length})
              </Button>
            )}
            <Button
              size="sm"
              onClick={() => createSession()}
              disabled={isCreatingSession}
              className="hidden sm:flex bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white border-0 shadow-lg"
            >
              <Plus className="w-4 h-4 mr-2" />
              {isCreatingSession ? 'Creating...' : 'New Session'}
            </Button>
            {/* User Profile Dropdown */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" className="flex items-center space-x-2 hover:bg-gray-100 rounded-full p-1">
                  <Avatar className="w-8 h-8">
                    <AvatarImage src="" />
                    <AvatarFallback className="bg-gradient-to-br from-blue-500 via-purple-600 to-pink-500 text-white">
                      {(user?.name?.charAt(0) || user?.email?.charAt(0) || 'U').toUpperCase()}
                    </AvatarFallback>
                  </Avatar>
                  <span className="hidden sm:inline text-sm font-medium text-gray-700">
                    {user?.name || user?.email?.split('@')[0]}
                  </span>
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-56">
                <DropdownMenuLabel className="flex flex-col gap-1">
                  <span className="text-sm font-semibold text-gray-900">
                    {user?.name || user?.email?.split('@')[0] || 'User'}
                  </span>
                  <span className="text-xs text-gray-500">{user?.email}</span>
                </DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem>
                  <User className="mr-2 h-4 w-4" />
                  <span>Profile</span>
                </DropdownMenuItem>
                <DropdownMenuItem>
                  <Settings className="mr-2 h-4 w-4" />
                  <span>Settings</span>
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={handleLogout} className="text-red-600 focus:text-red-600 focus:bg-red-50">
                  <LogOut className="mr-2 h-4 w-4" />
                  <span>Logout</span>
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>
      </div>

      <div className={`flex h-[calc(100vh-80px)] max-w-full ${currentImage ? 'max-w-7xl' : 'max-w-4xl'} mx-auto`}>
        {/* Chat Area */}
        <div className="flex-1 flex flex-col max-w-7xl mx-auto">
          {/* Messages */}
          <ScrollArea className="flex-1 p-4">
            <div className="space-y-4">
              {messages.length === 0 && (
                <div className="text-center py-12 px-4">
                  <div className="mx-auto w-20 h-20 bg-gradient-to-br from-blue-500 via-purple-600 to-pink-500 rounded-2xl flex items-center justify-center mb-6 shadow-lg">
                    <Bot className="w-10 h-10 text-white" />
                  </div>
                  <h3 className="text-2xl md:text-3xl font-bold text-gray-900 mb-3">
                    Welcome to your design session! 🎨
                  </h3>
                  <p className="text-gray-600 mb-6 max-w-lg mx-auto text-base">
                    I&apos;m your personal AI interior design assistant. I&apos;m here to help you create the perfect space that reflects your style and meets your needs.
                  </p>
                  <div className="bg-gradient-to-r from-blue-50 to-purple-50 border border-purple-200 rounded-xl p-5 max-w-lg mx-auto shadow-sm">
                    <p className="text-sm md:text-base text-blue-900">
                      💡 <strong>Tip:</strong> Feel free to ask me anything about interior design, furniture placement, color schemes, or home decor ideas!
                    </p>
                  </div>
                </div>
              )}

              {messages.map((msg, index) => (
                <div
                  key={index}
                  className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div className={`flex items-start space-x-2 max-w-[80%] ${msg.role === 'user' ? 'flex-row-reverse space-x-reverse' : ''}`}>
                    <Avatar className="w-8 h-8">
                      <AvatarImage src="" />
                      <AvatarFallback>
                        {msg.role === 'user' ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
                      </AvatarFallback>
                    </Avatar>
                    <div className={`rounded-2xl px-5 py-3 shadow-sm ${
                      msg.role === 'user' 
                        ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white' 
                        : 'bg-white border-2 border-gray-200'
                    }`}>
                      <MessageRenderer content={msg.content} role={msg.role} />
                    </div>
                  </div>
                </div>
              ))}
              
              {/* Thinking indicator */}
              {isSending && (
                <div className="flex justify-start">
                  <div className="flex items-start space-x-2 max-w-[80%]">
                    <Avatar className="w-8 h-8">
                      <AvatarImage src="" />
                      <AvatarFallback>
                        <Bot className="w-4 h-4" />
                      </AvatarFallback>
                    </Avatar>
                    <div className="bg-white border-2 border-purple-200 rounded-2xl px-5 py-3 shadow-sm">
                      <div className="flex items-center space-x-2">
                        <div className="flex space-x-1">
                          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                        </div>
                        <span className="text-sm text-gray-500">Thinking...</span>
                      </div>
                    </div>
                  </div>
                </div>
              )}
              
              <div ref={messagesEndRef} />
            </div>
          </ScrollArea>

          {/* Image Upload Area - Temporarily disabled */}
          {false && (
            <div className="px-4 py-2">
              <Card>
                <CardContent className="p-4">
                  <div
                    {...getRootProps()}
                    className={`border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors ${
                      isDragActive 
                        ? 'border-blue-500 bg-blue-50' 
                        : 'border-gray-300 hover:border-gray-400'
                    }`}
                  >
                    <input {...getInputProps()} />
                    <ImageIcon className="w-8 h-8 text-gray-400 mx-auto mb-2" />
                    <p className="text-sm text-gray-600">
                      {isDragActive 
                        ? 'Drop your image here...' 
                        : 'Drag & drop an image of your space, or click to select'
                      }
                    </p>
                    {isUploading && (
                      <p className="text-sm text-blue-600 mt-2">Uploading...</p>
                    )}
                  </div>
                </CardContent>
              </Card>
            </div>
          )}

          {/* Message Input */}
          <div className=" rounded-4xl bg-white backdrop-blur-sm p-4 sticky bottom-0">
            <form onSubmit={handleSendMessage} className="flex items-center space-x-2 max-w-7xl mx-auto">
              <div className="flex-1 relative">
                <Input
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  placeholder="Ask me about your interior design..."
                  className="w-full pr-12 py-6 border-2 border-gray-200 focus:border-purple-500 focus:ring-2 focus:ring-purple-200 rounded-full transition-all"
                  disabled={isSending}
                />
                {/* <div className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400">
                  <Send className="w-5 h-5" />
                </div> */}
              </div>
              <Button 
                type="submit" 
                disabled={!message.trim() || isSending}
                className="w-24 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white px-6 py-6 rounded-full shadow-lg hover:shadow-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Send className="w-5 h-5" />
              </Button>
            </form>
          </div>
        </div>

        {/* Image Analysis Panel */}
        {currentImage && (
          <ImageAnalysisPanel 
            analysisData={imageAnalysis || undefined}
            isLoading={isAnalyzing}
          />
        )}
      </div>
    </div>
  );
}
