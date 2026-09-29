'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { 
  ArrowLeft, 
  Star, 
  Search, 
  ExternalLink,
  Filter,
  ShoppingBag
} from 'lucide-react';
import Link from 'next/link';
import Logo from '@/components/ui/logo';
import { useAuthStore } from '@/store/auth';

interface Product {
  id: string;
  name: string;
  image: string;
  size?: string;
  description: string;
  rating: number;
  price: number;
  category: string;
}

// Mock data - in production, this would come from your API
const mockProducts: Product[] = [
  {
    id: '1',
    name: 'GLORY RUGS Modern Red Area Rug',
    image: '/placeholder-rug.jpg',
    size: '4x6',
    description: 'Features a modern design with grey swirls. Perfect for living rooms and bedrooms.',
    rating: 4.5,
    price: 129.99,
    category: 'Rugs'
  },
  {
    id: '2',
    name: 'Cozy Home Throw Pillow Set',
    image: '/placeholder-pillows.jpg',
    size: '18x18 inches',
    description: 'Set of 4 decorative throw pillows in various patterns and textures.',
    rating: 4.8,
    price: 49.99,
    category: 'Pillows'
  },
  {
    id: '3',
    name: 'Vintage Wooden Coffee Table',
    image: '/placeholder-table.jpg',
    size: '48x24 inches',
    description: 'Handcrafted wooden coffee table with elegant vintage design.',
    rating: 4.7,
    price: 299.99,
    category: 'Furniture'
  }
];

export default function ProductsPage() {
  const router = useRouter();
  const { isAuthenticated } = useAuthStore();
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All');

  const categories = ['All', ...Array.from(new Set(mockProducts.map(p => p.category)))];

  const filteredProducts = mockProducts.filter(product => {
    const matchesSearch = product.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         product.description.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = selectedCategory === 'All' || product.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  const handleImageClick = (imageUrl: string, productName: string) => {
    window.open(imageUrl, '_blank');
  };

  if (!isAuthenticated) {
    router.push('/login');
    return null;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50">
      {/* Header */}
      <div className="bg-white/95 backdrop-blur-sm border-b border-gray-200 px-4 py-3 sticky top-0 z-10 shadow-sm">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Link href="/" className="text-gray-400 hover:text-gray-600 transition-colors">
              <ArrowLeft className="w-5 h-5" />
            </Link>
            <div className="hidden md:flex mr-3">
              <Logo size="sm" showText={false} />
            </div>
            <div>
              <h1 className="text-base md:text-lg font-bold text-gray-900">
                Product Recommendations
              </h1>
              <p className="text-xs md:text-sm text-gray-500">
                View all recommended products
              </p>
            </div>
          </div>
          <Button
            size="sm"
            onClick={() => router.push('/')}
            className="hidden sm:flex bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white border-0 shadow-md"
          >
            <ShoppingBag className="w-4 h-4 mr-2" />
            Continue Shopping
          </Button>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-6">
        {/* Search and Filter */}
        <div className="mb-6 space-y-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <Input
              type="text"
              placeholder="Search products by name or description..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10 py-3 rounded-full border-2 border-gray-200 focus:border-purple-500 focus:ring-2 focus:ring-purple-200"
            />
          </div>

          <div className="flex items-center space-x-2 overflow-x-auto pb-2">
            <Filter className="w-4 h-4 text-gray-500 flex-shrink-0" />
            {categories.map((category) => (
              <button
                key={category}
                onClick={() => setSelectedCategory(category)}
                className={`px-4 py-2 rounded-full text-sm font-medium whitespace-nowrap transition-all ${
                  selectedCategory === category
                    ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-md'
                    : 'bg-white border border-gray-300 text-gray-700 hover:border-purple-300'
                }`}
              >
                {category}
              </button>
            ))}
          </div>
        </div>

        {/* Products Table/List */}
        <div className="bg-white rounded-2xl shadow-lg overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gradient-to-r from-blue-600 to-purple-600 text-white">
                <tr>
                  <th className="px-6 py-4 text-left text-sm font-semibold">Image</th>
                  <th className="px-6 py-4 text-left text-sm font-semibold">Product</th>
                  <th className="px-6 py-4 text-left text-sm font-semibold">Description</th>
                  <th className="px-6 py-4 text-center text-sm font-semibold">Size</th>
                  <th className="px-6 py-4 text-center text-sm font-semibold">Rating</th>
                  <th className="px-6 py-4 text-center text-sm font-semibold">Price</th>
                  <th className="px-6 py-4 text-center text-sm font-semibold">Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredProducts.map((product, index) => (
                  <tr 
                    key={product.id} 
                    className={`border-b border-gray-100 hover:bg-blue-50/50 transition-colors ${
                      index % 2 === 0 ? 'bg-white' : 'bg-gray-50/30'
                    }`}
                  >
                    <td className="px-6 py-4">
                      <div className="relative group cursor-pointer" onClick={() => handleImageClick(product.image, product.name)}>
                        <img
                          src={product.image}
                          alt={product.name}
                          className="w-12 h-12 object-cover rounded-lg border-2 border-gray-200 hover:border-purple-500 transition-all group-hover:shadow-lg"
                          onError={(e) => {
                            const target = e.target as HTMLImageElement;
                            target.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="48" height="48"%3E%3Crect width="48" height="48" fill="%23e5e7eb"/%3E%3Ctext x="50%25" y="50%25" dominant-baseline="middle" text-anchor="middle" fill="%239ca3af" font-size="12"%3ENo Image%3C/text%3E%3C/svg%3E';
                          }}
                        />
                        <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-20 transition-all rounded-lg flex items-center justify-center">
                          <ExternalLink className="w-4 h-4 text-white opacity-0 group-hover:opacity-100 transition-opacity" />
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="font-semibold text-gray-900">{product.name}</div>
                      <div className="text-xs text-purple-600 mt-1">{product.category}</div>
                    </td>
                    <td className="px-6 py-4">
                      <p className="text-sm text-gray-600 max-w-xs">{product.description}</p>
                    </td>
                    <td className="px-6 py-4 text-center">
                      {product.size && (
                        <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                          {product.size}
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-4 text-center">
                      <div className="flex items-center justify-center space-x-1">
                        <Star className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                        <span className="text-sm font-medium text-gray-900">{product.rating}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-center">
                      <span className="text-lg font-bold text-purple-600">${product.price.toFixed(2)}</span>
                    </td>
                    <td className="px-6 py-4 text-center">
                      <Button
                        size="sm"
                        onClick={() => {
                          // Add review functionality
                          alert('Add review functionality will be implemented here');
                        }}
                        className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white"
                      >
                        Add Review
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {filteredProducts.length === 0 && (
            <div className="text-center py-12">
              <ShoppingBag className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <p className="text-gray-500 text-lg">No products found matching your search.</p>
            </div>
          )}
        </div>

        {/* Review All Button */}
        <div className="mt-6 flex justify-center">
          <Button
            size="lg"
            className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white px-8 py-3 rounded-full shadow-lg"
            onClick={() => {
              // Show all reviews modal or navigate to reviews page
              alert('Review all functionality will be implemented here');
            }}
          >
            <Star className="w-5 h-5 mr-2" />
            Review All Products
          </Button>
        </div>
      </div>
    </div>
  );
}

