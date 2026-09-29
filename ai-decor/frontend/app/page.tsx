'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/store/auth';
import { useChatStore } from '@/store/chat';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Plus, MessageSquare, Sparkles, LogOut, ArrowRight, PlayCircle, User, Settings, Menu } from 'lucide-react';
import Link from 'next/link';
import SessionActions from '@/components/chat/SessionActions';
import Logo from '@/components/ui/logo';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';

export default function HomePage() {
  const router = useRouter();
  const { isAuthenticated, user, initializeAuth, logout } = useAuthStore();
  const { sessions, fetchSessions, createSession, isLoading, isCreatingSession } = useChatStore();

  useEffect(() => {
    initializeAuth();
    if (isAuthenticated) {
      fetchSessions();
    }
  }, [isAuthenticated, fetchSessions, initializeAuth]);

  const handleNewSession = async () => {
    if (isCreatingSession) return; // Prevent multiple clicks

    try {
      await createSession();
      router.push('/chat');
    } catch (error) {
      console.error('Failed to create session:', error);
    }
  };

  const handleLogout = () => {
    logout();
    router.push('/');
  };

  const features = [
    {
      icon: <Sparkles className="w-6 h-6" />,
      title: 'AI-Powered Design',
      description: 'Get instant design recommendations, color palettes, and style suggestions tailored to your taste'
    },
    {
      icon: <MessageSquare className="w-6 h-6" />,
      title: 'Smart Conversations',
      description: 'Chat with your AI designer to explore ideas and refine your vision in real-time'
    },
    {
      icon: <Plus className="w-6 h-6" />,
      title: 'Budget-Conscious',
      description: 'Get cost-effective solutions tailored to your budget'
    }
  ];

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50">
        {/* Header */}
        <header className="sticky top-0 z-10 bg-white/80 backdrop-blur-lg border-b border-gray-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between h-16">
              <Logo showText={true} />
              <div className="flex items-center space-x-4">
                <Link href="/login">
                  <Button variant="ghost" className="hidden sm:flex text-gray-700 hover:text-gray-900 hover:bg-gray-100">
                    Sign In
                  </Button>
                </Link>
                <Link href="/register">
                  <Button className="hidden sm:flex bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white shadow-lg">
                    Get Started
                  </Button>
                </Link>
              </div>
            </div>
          </div>
        </header>

        {/* Hero Section */}
        <section className="py-12 sm:py-16 lg:py-20">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center">
              <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-gray-900 mb-6">
                Design Your Dream Space with AI
              </h1>
              <p className="text-lg sm:text-xl text-gray-600 max-w-3xl mx-auto mb-8">
                Get instant design recommendations, color palettes, and style suggestions tailored to your taste and budget
              </p>
              <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-12">
                <Link href="/register">
                  <Button size="lg" className="w-full sm:w-auto bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white shadow-lg">
                    Get Started Free
                    <ArrowRight className="w-5 h-5 ml-2" />
                  </Button>
                </Link>
                <Button size="lg" variant="outline" className="w-full sm:w-auto">
                  <PlayCircle className="w-5 h-5 mr-2" />
                  Try Demo
                </Button>
              </div>

              <div className="rounded-2xl bg-gradient-to-br from-blue-100 to-purple-100 p-8 shadow-2xl max-w-7xl mx-auto">
                <div className="aspect-video bg-white/50 rounded-lg flex items-center justify-center">
                  <img src="/images/1.png" alt="Hero Image"
                   className="w-full h-full object-cover rounded-lg" />
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Features Section */}
        <section className="py-16 bg-white">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-12">
              <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
                Everything You Need to Design Your Dream Space
              </h2>
              <p className="text-lg text-gray-600">
                Powered by advanced AI to bring your vision to life
              </p>
            </div>
            <div className="grid md:grid-cols-3 gap-8">
              {features.map((feature, index) => (
                <Card key={index} className="text-center hover:shadow-xl transition-shadow">
                  <CardHeader>
                    <div className="mx-auto w-16 h-16 bg-gradient-to-br from-blue-500 via-purple-600 to-pink-500 rounded-2xl flex items-center justify-center mb-4 text-white">
                      {feature.icon}
                    </div>
                    <CardTitle>{feature.title}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <CardDescription className="text-base">
                      {feature.description}
                    </CardDescription>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="py-16 bg-gradient-to-r from-blue-600 to-purple-600 text-white">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
            <h2 className="text-3xl sm:text-4xl font-bold mb-4">
              Ready to Transform Your Space?
            </h2>
            <p className="text-xl text-blue-100 mb-8">
              Join thousands of users creating beautiful interiors with AI
            </p>
            <Link href="/register">
              <Button size="lg" className="bg-white text-blue-600 hover:bg-gray-100 shadow-xl">
                Get Started Free
                <ArrowRight className="w-5 h-5 ml-2" />
              </Button>
            </Link>
          </div>
        </section>

        {/* Footer */}
        <footer className="bg-white border-t border-gray-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <div className="flex items-center justify-center">
              <Logo showText={true} />
            </div>
            <p className="text-center text-gray-600 mt-4">
              © 2024 Visioneer. All rights reserved.
            </p>
          </div>
        </footer>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-lg border-b border-gray-200 sticky top-0 z-10 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <Logo showText={true} />
            
            <div className="flex items-center space-x-4">
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" className="flex items-center space-x-2 hover:bg-gray-100 rounded-full">
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
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">
            Welcome back, {user?.name || user?.email?.split('@')[0] || 'User'}! 👋
          </h1>
          <p className="text-gray-600 mt-2">
            Continue your interior design journey or start a new project
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <Card className={`cursor-pointer hover:shadow-xl transition-all border-2 border-dashed border-purple-300 hover:border-purple-500 ${isCreatingSession ? 'opacity-50 cursor-not-allowed' : ''}`} onClick={handleNewSession}>
            <CardHeader>
              <div className="flex items-center space-x-2">
                <div className="w-10 h-10 bg-gradient-to-br from-blue-500 via-purple-600 to-pink-500 rounded-xl flex items-center justify-center">
                  <Plus className="w-6 h-6 text-white" />
                </div>
                <CardTitle className="text-lg text-gray-900">New Design Session</CardTitle>
              </div>
              <CardDescription className="mt-2">
                Start a new interior design project with AI assistance
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex items-center text-sm text-purple-600 font-medium">
                <MessageSquare className="w-4 h-4 mr-2" />
                AI-powered conversations
              </div>
            </CardContent>
          </Card>

          {sessions.map((session) => (
            <Card
              key={session.id}
              className="hover:shadow-xl transition-all border border-gray-200"
            >
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div
                    className="flex-1 cursor-pointer"
                    onClick={() => router.push(`/chat?session=${session.id}`)}
                  >
                    <CardTitle className="text-lg truncate">
                      {session.name}
                    </CardTitle>
                    <CardDescription>
                      Chat session
                    </CardDescription>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className="text-xs text-gray-500">
                      {new Date(session.created_at).toLocaleDateString()}
                    </span>
                    <SessionActions session={session} />
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div
                  className="flex items-center text-sm text-gray-500 cursor-pointer"
                  onClick={() => router.push(`/chat?session=${session.id}`)}
                >
                  <MessageSquare className="w-4 h-4 mr-1" />
                  <span>Active session</span>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {sessions.length === 0 && !isLoading && (
          <div className="text-center py-12">
            <div className="mx-auto w-20 h-20 bg-gradient-to-br from-blue-500 via-purple-600 to-pink-500 rounded-2xl flex items-center justify-center mb-6 shadow-lg">
              <MessageSquare className="w-10 h-10 text-white" />
            </div>
            <h3 className="text-2xl font-bold text-gray-900 mb-2">No sessions yet</h3>
            <p className="text-gray-600 mb-6 max-w-md mx-auto">Start your first interior design project and let AI help you create something amazing</p>
            <Button onClick={handleNewSession} disabled={isCreatingSession} size="lg" className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white shadow-lg">
              <Plus className="w-5 h-5 mr-2" />
              {isCreatingSession ? 'Creating...' : 'Create New Session'}
            </Button>
          </div>
        )}
      </div>
    </div>
  );
}