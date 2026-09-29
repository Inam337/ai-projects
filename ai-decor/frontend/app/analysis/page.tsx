'use client';

import { useEffect, useState, useMemo } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/store/auth';
import { useChatStore } from '@/store/chat';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { 
  ArrowLeft, 
  Star, 
  ExternalLink,
  Image as ImageIcon,
  Check,
  Eye
} from 'lucide-react';
import Link from 'next/link';
import Logo from '@/components/ui/logo';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { LogOut, User, Settings } from 'lucide-react';

// Extract helper functions
const getRoomType = (detections?: Array<{label: string}>) => {
  if (!detections || detections.length === 0) return 'Room';
  const labels = detections.map(d => d.label);
  if (labels.includes('bed')) return 'Bedroom';
  if (labels.includes('sofa') || labels.includes('couch')) return 'Living Room';
  if (labels.includes('refrigerator')) return 'Kitchen';
  return 'Room';
};

const getStyleTheme = (recommendations?: Array<{'Room Color Analysis'?: {theme: string}}>) => {
  return recommendations?.[0]?.['Room Color Analysis']?.theme || 'Modern';
};

const getRoomColors = (recommendations?: Array<{'Room Color Analysis'?: {codes: string[]}}>) => {
  const colors = recommendations?.[0]?.['Room Color Analysis']?.codes || [];
  return colors.map(color => {
    // Ensure color has # prefix
    return color.startsWith('#') ? color : `#${color}`;
  });
};

export default function AnalysisPage() {
  const router = useRouter();
  const { isAuthenticated, user, logout } = useAuthStore();
  const { currentImage, imageAnalysis, products } = useChatStore();
  const [selectedProduct, setSelectedProduct] = useState<number | null>(null);
  const [imageErrors, setImageErrors] = useState<Set<string>>(new Set());

  // Handle authentication redirect
  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, router]);

  // Create image URL from current image or analysis
  const imageUrl = useMemo(() => {
    if (currentImage) {
      return URL.createObjectURL(currentImage);
    } else if (imageAnalysis?.imageUrl) {
      return imageAnalysis.imageUrl;
    }
    return '';
  }, [currentImage, imageAnalysis]);

  const handleLogout = () => {
    logout();
    router.push('/');
  };

  const handleImageError = (productId: string) => {
    setImageErrors(prev => new Set(prev).add(productId));
  };

  const handleProductClick = (productUrl: string) => {
    if (productUrl) {
      window.open(productUrl, '_blank');
    }
  };

  const getCompatibilityScore = (product: { name: string }) => {
    if (!imageAnalysis) return 85;
    const firstRec = imageAnalysis.recommendations?.[0];
    const theme = firstRec?.['Room Color Analysis']?.theme || '';
    const styleMatch = theme ? (product.name.toLowerCase().includes(theme.toLowerCase().split(' ')[0]) ? 20 : 0) : 0;
    // Use a fixed score to avoid random() in render
    return Math.min(100, 75 + styleMatch + 5);
  };

  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-blue-50 to-blue-50">
      {/* Header */}
      <div className="bg-white/95 backdrop-blur-sm border-b border-gray-200 px-4 py-3 sticky top-0 z-10 shadow-sm">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Link href="/chat" className="text-gray-600 hover:text-gray-900">
              <ArrowLeft className="w-5 h-5" />
            </Link>
            <div className="hidden md:flex mr-3">
              <Logo size="sm" showText={false} />
            </div>
            <div>
              <h1 className="text-base md:text-lg font-bold text-gray-900">
                Room Analysis & Product Comparison
              </h1>
              <p className="text-xs md:text-sm text-gray-500">
                Compare your space with recommended products
              </p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <Button
              size="sm"
              onClick={() => router.push('/chat')}
              className="hidden sm:flex bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white border-0 shadow-md"
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Chat
            </Button>
            
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" className="flex items-center space-x-2 hover:bg-gray-100 rounded-full p-1">
                  <Avatar className="w-8 h-8">
                    <AvatarImage src="" />
                    <AvatarFallback className="bg-gradient-to-br from-blue-500 via-blue-600 to-blue-500 text-white">
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

      <div className="max-w-7xl mx-auto px-4 py-6">
        {/* Image and Analysis Section */}
        <div className="grid lg:grid-cols-2 gap-6 mb-6">
          {/* Uploaded Image */}
          <Card className="bg-white shadow-lg">
            <CardHeader>
              <CardTitle className="flex items-center">
                <Eye className="w-5 h-5 mr-2 text-blue-600" />
                Your Room Image
              </CardTitle>
              <CardDescription>
                Analyze this space to find the perfect products
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="aspect-video bg-gray-100 rounded-lg overflow-hidden flex items-center justify-center">
                {imageUrl ? (
                  <img
                    src={imageUrl}
                    alt="Your room"
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <div className="text-center">
                    <ImageIcon className="w-16 h-16 text-gray-400 mx-auto mb-2" />
                    <p className="text-gray-500">No image uploaded</p>
                  </div>
                )}
              </div>

              {imageAnalysis && (
                <div className="mt-4 p-4 bg-blue-50 rounded-lg">
                  <h3 className="font-semibold text-sm text-gray-900 mb-2">Room Analysis</h3>
                  <div className="grid grid-cols-1 gap-2 text-xs">
                    <div>
                      <span className="text-gray-600">Room Type:</span>
                      <span className="ml-2 font-medium text-gray-900">{getRoomType(imageAnalysis.detections)}</span>
                    </div>
                    <div>
                      <span className="text-gray-600">Style:</span>
                      <span className="ml-2 font-medium text-gray-900">{getStyleTheme(imageAnalysis.recommendations)}</span>
                    </div>
                    <div>
                      <span className="text-gray-600">Objects:</span>
                      <span className="ml-2 font-medium text-gray-900">
                        {imageAnalysis.detections?.length || 0} detected
                      </span>
                    </div>
                    <div>
                      <span className="text-gray-600">Colors:</span>
                      {getRoomColors(imageAnalysis.recommendations).length > 0 ? (
                        <div className="flex items-center gap-1.5 mt-1 flex-wrap">
                          {getRoomColors(imageAnalysis.recommendations).map((color, idx) => (
                            <div
                              key={idx}
                              className="w-6 h-6 rounded-md border-2 border-white shadow-sm hover:scale-110 transition-transform cursor-pointer"
                              style={{ backgroundColor: color }}
                              title={color}
                            />
                          ))}
                        </div>
                      ) : (
                        <span className="ml-2 text-xs text-gray-400 italic">No colors detected</span>
                      )}
                    </div>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Recommendations Summary */}
          <Card className="bg-white shadow-lg">
            <CardHeader>
              <CardTitle className="flex items-center">
                <Star className="w-5 h-5 mr-2 text-amber-500" />
                AI Recommendations
              </CardTitle>
              <CardDescription>
                Products matched to your room style
              </CardDescription>
            </CardHeader>
            <CardContent className='overflow-y-auto max-h-[500px]'>
              {imageAnalysis?.recommendations && imageAnalysis.recommendations.length > 0 ? (
                <div className="space-y-4">
                  {imageAnalysis.recommendations.map((rec, index) => {
                    const roomColorAnalysis = rec['Room Color Analysis'];
                    const roomLighteningAnalysis = rec['Room Lightening Analysis'];
                    
                    return (
                      <div key={index} className="space-y-3">
                        {roomColorAnalysis && (
                          <div className="bg-gradient-to-r from-blue-50 to-blue-100 rounded-lg p-4 border-l-4 border-blue-600">
                            <h4 className="font-semibold text-gray-900 mb-2 flex items-center">
                              🎨 Color Theme
                            </h4>
                            <p className="text-sm text-gray-700 mb-3 italic">
                              {roomColorAnalysis.theme}
                            </p>
                            {roomColorAnalysis.codes && roomColorAnalysis.codes.length > 0 && (
                              <div className="flex items-center gap-2 flex-wrap">
                                {roomColorAnalysis.codes.map((color: string, idx: number) => {
                                  const hexColor = color.startsWith('#') ? color : `#${color}`;
                                  return (
                                    <div
                                      key={idx}
                                      className="w-10 h-10 rounded-lg border-2 border-white shadow-md"
                                      style={{ backgroundColor: hexColor }}
                                      title={hexColor}
                                    />
                                  );
                                })}
                              </div>
                            )}
                          </div>
                        )}
                        
                        {roomLighteningAnalysis && (
                          <div className="bg-gradient-to-r from-amber-50 to-amber-100 rounded-lg p-4 border-l-4 border-amber-600">
                            <h4 className="font-semibold text-gray-900 mb-2 flex items-center">
                              💡 Lighting Analysis
                            </h4>
                            <p className="text-sm text-gray-700 leading-relaxed">
                              {roomLighteningAnalysis}
                            </p>
                          </div>
                        )}
                        
                        {rec.object && (
                          <div className="bg-gradient-to-r from-purple-50 to-purple-100 rounded-lg p-4 border-l-4 border-purple-600">
                            <h4 className="font-semibold text-gray-900 mb-1">✨ Object Recommendation</h4>
                            <p className="text-sm font-medium text-gray-800 mb-2">{rec.object}</p>
                            {rec.position && (
                              <p className="text-xs text-gray-600 mb-1">
                                <span className="font-semibold">Position:</span> {rec.position}
                              </p>
                            )}
                            {rec.justification && (
                              <p className="text-xs text-gray-700 mt-2 leading-relaxed">
                                {rec.justification}
                              </p>
                            )}
                            {rec.trend_analysis && (
                              <div className="mt-2 pt-2 border-t border-purple-200">
                                <p className="text-xs font-semibold text-purple-700 mb-1">📊 Trend Analysis</p>
                                <p className="text-xs text-gray-600 leading-relaxed">
                                  {rec.trend_analysis}
                                </p>
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              ) : (
                <div className="space-y-4">
                  <div className="bg-gradient-to-r from-blue-50 to-blue-100 rounded-lg p-4 border-l-4 border-blue-600">
                    <h4 className="font-semibold text-gray-900 mb-1">Color Harmony</h4>
                    <p className="text-sm text-gray-700">
                      Based on your {getStyleTheme(imageAnalysis?.recommendations) || 'modern'} style, we recommend products with complementary colors.
                    </p>
                  </div>
                  
                  <div className="bg-gradient-to-r from-purple-50 to-purple-100 rounded-lg p-4 border-l-4 border-purple-600">
                    <h4 className="font-semibold text-gray-900 mb-1">Style Consistency</h4>
                    <p className="text-sm text-gray-700">
                      All recommended products align with your room&apos;s aesthetic.
                    </p>
                  </div>
                  
                  <div className="bg-gradient-to-r from-green-50 to-green-100 rounded-lg p-4 border-l-4 border-green-600">
                    <h4 className="font-semibold text-gray-900 mb-1">Perfect Fit</h4>
                    <p className="text-sm text-gray-700">
                      Each product complements your {getRoomType(imageAnalysis?.detections)} layout.
                    </p>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Product Comparison Grid */}
        {products.length > 0 ? (
          <Card className="bg-white shadow-lg">
            <CardHeader>
              <CardTitle>Recommended Products ({products.length})</CardTitle>
              <CardDescription>
                Click on products to compare with your space
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                {products.map((product, index) => {
                  const compatibility = getCompatibilityScore(product);
                  const hasError = imageErrors.has(product.id);
                  
                  return (
                    <Card
                      key={product.id}
                      className={`hover:shadow-xl transition-all cursor-pointer border-2 ${
                        selectedProduct === index ? 'border-blue-500 shadow-lg' : 'border-gray-200'
                      }`}
                      onClick={() => setSelectedProduct(selectedProduct === index ? null : index)}
                    >
                      <CardContent className="p-0">
                        <div className="aspect-square bg-gray-100 flex items-center justify-center relative">
                          {product.image && !hasError ? (
                            <img
                              src={product.image}
                              alt={product.name}
                              className="w-full h-full object-cover"
                              onError={() => handleImageError(product.id)}
                            />
                          ) : (
                            <ImageIcon className="w-16 h-16 text-gray-400" />
                          )}
                          
                          <div className="absolute top-2 right-2 bg-green-500 text-white px-2 py-1 rounded-full text-xs font-semibold flex items-center">
                            <Check className="w-3 h-3 mr-1" />
                            {compatibility}% Match
                          </div>
                        </div>
                        
                        <div className="p-4">
                          <h3 className="font-semibold text-sm text-gray-900 mb-1 line-clamp-2">
                            {index + 1}. {product.name}
                          </h3>
                          {product.description && (
                            <p className="text-xs text-gray-600 mb-2 line-clamp-2">
                              {product.description}
                            </p>
                          )}
                          
                          {product.price && (
                            <div className="text-sm font-bold text-blue-600 mb-3">
                              {product.price}
                            </div>
                          )}
                          
                          <div className="flex gap-2">
                            {product.link && (
                              <Button
                                size="sm"
                                className="flex-1 bg-blue-600 hover:bg-blue-700 text-white text-xs"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleProductClick(product.link!);
                                }}
                              >
                                <ExternalLink className="w-3 h-3 mr-1" />
                                View
                              </Button>
                            )}
                            <Button
                              size="sm"
                              variant="outline"
                              className="text-xs"
                              onClick={(e) => {
                                e.stopPropagation();
                              }}
                            >
                              <Star className="w-3 h-3" />
                            </Button>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  );
                })}
              </div>
            </CardContent>
          </Card>
        ) : (
          <Card className="bg-white shadow-lg">
            <CardContent className="p-12 text-center">
              <Star className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-gray-900 mb-2">No Products Yet</h3>
              <p className="text-gray-500 mb-6">
                Start chatting with your AI assistant to get product recommendations!
              </p>
              <Button
                onClick={() => router.push('/chat')}
                className="bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white"
              >
                Go to Chat
              </Button>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}

