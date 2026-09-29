'use client';

import { useRouter } from 'next/navigation';
import { useChatStore } from '@/store/chat';
import { Button } from '@/components/ui/button';
import { 
  ArrowLeft, 
  Star, 
  ExternalLink,
  ShoppingBag,
  Image as ImageIcon
} from 'lucide-react';
import Link from 'next/link';
import Logo from '@/components/ui/logo';
import { useAuthStore } from '@/store/auth';
import { useEffect, useState } from 'react';

export default function ListingsPage() {
  const router = useRouter();
  const { isAuthenticated } = useAuthStore();
  const { products } = useChatStore();
  const [imageErrors, setImageErrors] = useState<Set<string>>(new Set());

  const handleImageError = (productId: string) => {
    setImageErrors(prev => new Set(prev).add(productId));
  };

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, router]);

  const handleImageClick = (imageUrl: string) => {
    if (imageUrl) {
      window.open(imageUrl, '_blank');
    }
  };

  const handleAddReview = (productId: string) => {
    // TODO: Implement review functionality
    alert('Add review functionality will be implemented here for product: ' + productId);
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
            <Link href="/chat" className="text-gray-400 hover:text-gray-600 transition-colors">
              <ArrowLeft className="w-5 h-5" />
            </Link>
            <div className="hidden md:flex mr-3">
              <Logo size="sm" showText={false} />
            </div>
            <div>
              <h1 className="text-base md:text-lg font-bold text-gray-900">
                Product Listings
              </h1>
              <p className="text-xs md:text-sm text-gray-500">
                All recommended products from your chat
              </p>
            </div>
          </div>
          <Button
            size="sm"
            onClick={() => router.push('/chat')}
            className="hidden sm:flex bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white border-0 shadow-md"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Chat
          </Button>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-6">
        {products.length > 0 ? (
          <>
            {/* Products Table */}
            <div className="bg-white rounded-2xl shadow-lg overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gradient-to-r from-blue-600 to-blue-700 text-white">
                    <tr>
                      <th className="px-6 py-4 text-left text-sm font-semibold">Image</th>
                      <th className="px-6 py-4 text-left text-sm font-semibold">Product Name</th>
                      <th className="px-6 py-4 text-left text-sm font-semibold">Description</th>
                      <th className="px-6 py-4 text-center text-sm font-semibold">Price</th>
                      <th className="px-6 py-4 text-center text-sm font-semibold">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {products.map((product, index) => (
                      <tr 
                        key={product.id}
                        className={`border-b border-gray-100 hover:bg-blue-50/50 transition-colors ${
                          index % 2 === 0 ? 'bg-white' : 'bg-gray-50/30'
                        }`}
                      >
                        <td className="px-6 py-4">
                          {product.image && !imageErrors.has(product.id) ? (
                            <div 
                              className="relative group cursor-pointer" 
                              onClick={() => handleImageClick(product.image || '')}
                            >
                              <img
                                src={product.image}
                                alt={product.name}
                                className="w-12 h-12 object-cover rounded-lg border-2 border-gray-200 hover:border-blue-500 transition-all group-hover:shadow-lg"
                                onError={() => handleImageError(product.id)}
                                loading="lazy"
                              />
                              {/* <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-20 transition-all rounded-lg flex items-center justify-center">
                                <ExternalLink className="w-4 h-4 text-white opacity-0 group-hover:opacity-100 transition-opacity" />
                              </div> */}
                            </div>
                          ) : (
                            <div className="w-12 h-12 bg-gray-100 border-2 border-gray-200 rounded-lg flex items-center justify-center">
                              <ImageIcon className="w-6 h-6 text-gray-400" />
                            </div>
                          )}
                        </td>
                        <td className="px-6 py-4">
                          <div className="font-semibold text-gray-900">{product.name}</div>
                        </td>
                        <td className="px-6 py-4">
                          <p className="text-sm text-gray-600 max-w-md">{product.description}</p>
                        </td>
                        <td className="px-6 py-4 text-center">
                          {product.price && (
                            <span className="text-sm font-medium text-blue-600">
                              {product.price}
                            </span>
                          )}
                          {!product.price && (
                            <span className="text-xs text-gray-400 italic">N/A</span>
                          )}
                        </td>
                        <td className="px-6 py-4 text-center">
                          <Button
                            size="sm"
                            onClick={() => handleAddReview(product.id)}
                            className="bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white"
                          >
                            <Star className="w-4 h-4 mr-1" />
                            Review
                          </Button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Review All Button */}
            <div className="mt-6 flex justify-center">
              <Button
                size="lg"
                className="bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white px-8 py-3 rounded-full shadow-lg"
                onClick={() => {
                  // Show all reviews modal or navigate to reviews page
                  alert('Review all functionality will be implemented here');
                }}
              >
                <Star className="w-5 h-5 mr-2" />
                Review All Products
              </Button>
            </div>
          </>
        ) : (
          <div className="bg-white rounded-2xl shadow-lg p-12 text-center">
            <ShoppingBag className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              No Products Yet
            </h3>
            <p className="text-gray-500 mb-6">
              Start chatting with your AI assistant to get product recommendations!
            </p>
            <Button
              onClick={() => router.push('/chat')}
              className="bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white"
            >
              Go to Chat
            </Button>
          </div>
        )}
      </div>
    </div>
  );
}

