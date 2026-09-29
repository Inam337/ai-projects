'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import Logo from '@/components/ui/logo';
import {
    Sparkles,
    Palette,
    Home,
    Lightbulb,
    TrendingUp,
    ArrowRight,
    Check,
    PlayCircle
} from 'lucide-react';

export default function HomePage() {
    const router = useRouter();
    const [isLoading, setIsLoading] = useState(false);

    const handleTryDemo = () => {
        setIsLoading(true);
        // Navigate to demo/guest mode
        setTimeout(() => {
            router.push('/login');
            setIsLoading(false);
        }, 500);
    };

    const features = [
        {
            icon: <Sparkles className="w-6 h-6" />,
            title: 'AI-Powered Design',
            description: 'Get intelligent design recommendations powered by advanced AI'
        },
        {
            icon: <Palette className="w-6 h-6" />,
            title: 'Color Analysis',
            description: 'Analyze room colors and get perfect palette suggestions'
        },
        {
            icon: <Home className="w-6 h-6" />,
            title: 'Room Planning',
            description: 'Plan and visualize your space with smart layout suggestions'
        },
        {
            icon: <Lightbulb className="w-6 h-6" />,
            title: 'Style Recommendations',
            description: 'Discover styles that match your taste and preferences'
        },
        {
            icon: <TrendingUp className="w-6 h-6" />,
            title: 'Budget Planning',
            description: 'Get cost-effective solutions tailored to your budget'
        }
    ];

    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50">
            {/* Header */}
            <header className="sticky top-0 z-10 bg-white/80 backdrop-blur-lg border-b border-gray-200">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex items-center justify-between h-16">
                        <Logo showText={true} />
                        <div className="flex items-center space-x-4">
                            <Link href="/login">
                                <Button variant="ghost" className="hidden sm:flex">
                                    Sign In
                                </Button>
                            </Link>
                            <Link href="/register">
                                <Button className="hidden sm:flex bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white shadow-lg">
                                    Get Started
                                </Button>
                            </Link>
                            <Link href="/login">
                                <Button size="sm" className="sm:hidden">
                                    Sign In
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
                        <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-gray-900 mb-4">
                            Transform Your Space with
                            <span className="block bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 bg-clip-text text-transparent">
                                AI Interior Design
                            </span>
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
                            <Button
                                size="lg"
                                variant="outline"
                                className="w-full sm:w-auto"
                                onClick={handleTryDemo}
                                disabled={isLoading}
                            >
                                <PlayCircle className="w-5 h-5 mr-2" />
                                {isLoading ? 'Loading...' : 'Try Demo'}
                            </Button>
                        </div>

                        {/* Hero Image Placeholder */}
                        <div className="relative max-w-4xl mx-auto">
                            <div className="rounded-2xl bg-gradient-to-br from-blue-100 to-purple-100 p-8 shadow-2xl">
                                <div className="aspect-video bg-white/50 rounded-lg flex items-center justify-center">
                                    <Sparkles className="w-24 h-24 text-purple-600" />
                                </div>
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
                        <p className="text-lg text-gray-600 max-w-2xl mx-auto">
                            Our AI-powered platform makes interior design accessible, affordable, and effortless
                        </p>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {features.map((feature, index) => (
                            <Card key={index} className="border-2 hover:border-purple-300 transition-colors">
                                <CardContent className="p-6">
                                    <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center text-white mb-4">
                                        {feature.icon}
                                    </div>
                                    <h3 className="text-xl font-semibold text-gray-900 mb-2">
                                        {feature.title}
                                    </h3>
                                    <p className="text-gray-600">
                                        {feature.description}
                                    </p>
                                </CardContent>
                            </Card>
                        ))}
                    </div>
                </div>
            </section>

            {/* How It Works Section */}
            <section className="py-16 bg-gray-50">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="text-center mb-12">
                        <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
                            How It Works
                        </h2>
                        <p className="text-lg text-gray-600">
                            Get started in three simple steps
                        </p>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                        {[
                            {
                                step: '1',
                                title: 'Upload Your Space',
                                description: 'Take a photo of your room and our AI will analyze colors, lighting, and style'
                            },
                            {
                                step: '2',
                                title: 'Set Your Preferences',
                                description: 'Tell us about your style, budget, and goals for personalized recommendations'
                            },
                            {
                                step: '3',
                                title: 'Get Design Ideas',
                                description: 'Receive instant suggestions and chat with our AI assistant for expert advice'
                            }
                        ].map((item, index) => (
                            <div key={index} className="relative">
                                <div className="text-center">
                                    <div className="w-16 h-16 bg-gradient-to-br from-blue-600 to-purple-600 rounded-full flex items-center justify-center text-white text-2xl font-bold mx-auto mb-4">
                                        {item.step}
                                    </div>
                                    <h3 className="text-xl font-semibold text-gray-900 mb-2">
                                        {item.title}
                                    </h3>
                                    <p className="text-gray-600">
                                        {item.description}
                                    </p>
                                </div>
                                {index < 2 && (
                                    <div className="hidden md:block absolute top-8 left-full w-full">
                                        <ArrowRight className="w-6 h-6 text-gray-400 mx-auto" />
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* CTA Section */}
            <section className="py-16 bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600">
                <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
                    <h2 className="text-3xl sm:text-4xl font-bold text-white mb-4">
                        Ready to Transform Your Space?
                    </h2>
                    <p className="text-lg text-white/90 mb-8">
                        Join thousands of users creating beautiful interiors with AI assistance
                    </p>
                    <Link href="/register">
                        <Button size="lg" variant="secondary" className="text-lg px-8">
                            Start Your Design Journey
                            <ArrowRight className="w-5 h-5 ml-2" />
                        </Button>
                    </Link>
                </div>
            </section>

            {/* Footer */}
            <footer className="bg-gray-900 text-white py-12">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
                        <div>
                            <Logo showText={true} />
                            <p className="mt-4 text-gray-400">
                                AI-powered interior design made simple and accessible.
                            </p>
                        </div>
                        <div>
                            <h4 className="font-semibold mb-4">Product</h4>
                            <ul className="space-y-2 text-gray-400">
                                <li><Link href="/" className="hover:text-white">Features</Link></li>
                                <li><Link href="/" className="hover:text-white">Pricing</Link></li>
                                <li><Link href="/" className="hover:text-white">Demo</Link></li>
                            </ul>
                        </div>
                        <div>
                            <h4 className="font-semibold mb-4">Company</h4>
                            <ul className="space-y-2 text-gray-400">
                                <li><Link href="/" className="hover:text-white">About</Link></li>
                                <li><Link href="/" className="hover:text-white">Contact</Link></li>
                                <li><Link href="/" className="hover:text-white">Careers</Link></li>
                            </ul>
                        </div>
                        <div>
                            <h4 className="font-semibold mb-4">Legal</h4>
                            <ul className="space-y-2 text-gray-400">
                                <li><Link href="/" className="hover:text-white">Privacy</Link></li>
                                <li><Link href="/" className="hover:text-white">Terms</Link></li>
                            </ul>
                        </div>
                    </div>
                    <div className="border-t border-gray-800 mt-8 pt-8 text-center text-gray-400">
                        <p>&copy; 2025 Visioneer. All rights reserved.</p>
                    </div>
                </div>
            </footer>
        </div>
    );
}
