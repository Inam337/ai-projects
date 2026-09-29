'use client';

import { ExternalLink, Image as ImageIcon } from 'lucide-react';
import { useState } from 'react';

export interface Product {
  id: string;
  name: string;
  description: string;
  price?: string;
  image?: string;
  rating?: string;
  link?: string;
  size?: string;
}

interface ProductListingProps {
  products: Product[];
}

export default function ProductListing({ products }: ProductListingProps) {
  const [imageErrors, setImageErrors] = useState<Set<string>>(new Set());
  
  // Debug log to see what data we're receiving
  console.log('ProductListing received products:', products);

  // Check if image URL is valid
  const isValidImageUrl = (url?: string): boolean => {
    if (!url || url.trim() === '') return false;
    // Check if it's a valid URL format
    try {
      new URL(url);
      return true;
    } catch {
      // Check if it's a relative path
      return url.startsWith('/') || url.startsWith('./');
    }
  };

  const handleImageClick = (product: Product) => {
    if (isValidImageUrl(product.image)) {
      window.open(product.image, '_blank');
    }
  };

  const handleImageError = (productId: string) => {
    setImageErrors(prev => new Set(prev).add(productId));
  };


  return (
    <div className="my-4 space-y-3">
      <div className="flex items-center gap-2 mb-3">
        <div className="w-6 h-6 bg-amber-600 rounded flex items-center justify-center">
          <span className="text-white text-xs font-bold">📦</span>
        </div>
        <div className="text-sm font-semibold text-gray-900">
          Product Recommendations
        </div>
      </div>
      <div className="space-y-3">
        {products.map((product, index) => {
          const hasImageError = imageErrors.has(product.id);
          const shouldShowImage = isValidImageUrl(product.image) && !hasImageError;
          
          return (
            <div
              key={product.id || index}
              className="border border-gray-200 rounded-lg p-4 hover:border-gray-300 hover:shadow-sm transition-all bg-white"
            >
              {/* Header: Title and Image */}
              <div className="flex items-center justify-between gap-3 mb-3">
                {/* Title on left */}
                <div className="flex-1">
                  <div className="font-semibold text-gray-900 text-sm leading-tight">
                    {index + 1}. {product.name}
                  </div>
                </div>

                {/* Image on right */}
                <div className="shrink-0">
                  <div
                    className={`relative group ${shouldShowImage ? 'cursor-pointer' : ''}`}
                    onClick={() => shouldShowImage && handleImageClick(product)}
                  >
                    {shouldShowImage ? (
                      <img
                        src={product.image}
                        alt={product.name}
                        className="w-20 h-20 object-cover p-2 border-2 border-gray-200"
                        onError={() => handleImageError(product.id)}
                        loading="lazy"
                      />
                    ) : (
                      <div className="w-16 h-16 bg-gray-200   flex items-center justify-center">
                        <ImageIcon className="w-6 h-6 text-gray-400" />
                      </div>
                    )}
                  </div>
                </div>
              </div>

              {/* Details - if available */}
              {(product.size || product.description || product.price) && (
                <div className="mb-3 text-xs text-gray-600 space-y-1">
                  {product.size && (
                    <div><strong>Size:</strong> {product.size}</div>
                  )}
                  {product.description && (
                    <div><strong>Description:</strong> {product.description}</div>
                  )}
                  {product.price && (
                    <div><strong>Price:</strong> {product.price}</div>
                  )}
                </div>
              )}

              {/* Link at bottom */}
              {product.link && (
                <div className="text-center flex justify-start items-start">
                  <a
                    href={product.link}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center p-2 bg-gradient-to-r from-purple-500 to-pink-600 hover:from-pink-600 hover:to-purple-700 text-white rounded-md hover:text-white text-xs font-medium transition-all break-all"
                  >
                    View Product
                    <ExternalLink className="w-3 h-3 ml-1" />
                  </a>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
