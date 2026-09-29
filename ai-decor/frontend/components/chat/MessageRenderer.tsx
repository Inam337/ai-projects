'use client';

import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeSanitize from 'rehype-sanitize';
import { ExternalLink, Image as ImageIcon } from 'lucide-react';
import ProductListing, { Product } from './ProductListing';

interface MessageRendererProps {
  content: string;
  role: 'user' | 'assistant' | 'system';
}

function parseProducts(content: string): { products: Product[], cleanedContent: string } {
  const products: Product[] = [];
  let cleanedContent = content;
  
  // Pattern to match numbered product listings
  const productRegex = /(\d+)\.\s*\*\*([^*]+)\*\*\s*[^\n]*\n/g;
  let match;
  const productRanges: Array<{ start: number, end: number }> = [];
  
  // Find all products
  while ((match = productRegex.exec(content)) !== null) {
    const startIdx = match.index;
    const endIdx = content.indexOf('\n\n', startIdx);
    const actualEnd = endIdx !== -1 ? endIdx : content.length;
    
    productRanges.push({ start: startIdx, end: actualEnd });
    
    const productBlock = content.substring(startIdx, actualEnd);
    const name = match[2].trim();
    
    // Try both formats: **Size:** and - **Size:**
    const sizeMatch = productBlock.match(/(?:^|\n)[-\*]*\s*\*\*Size:\*\*\s*([^\n]+)/i) || 
                      productBlock.match(/\*\*Size:\*\*\s*([^\n]+)/i);
    const descriptionMatch = productBlock.match(/(?:^|\n)[-\*]*\s*\*\*Description:\*\*\s*([^\n]+)/i) || 
                             productBlock.match(/\*\*Description:\*\*\s*([^\n]+)/i);
    const priceMatch = productBlock.match(/(?:^|\n)[-\*]*\s*\*\*Price:\*\*\s*([^\n]+)/i) || 
                       productBlock.match(/\*\*Price:\*\*\s*([^\n]+)/i);
    const imageMatch = productBlock.match(/!\[([^\]]*)\]\(([^)]+)\)/);
    const linkMatch = productBlock.match(/(?:View on|Link to)\s+\[([^\]]+)\]\(([^)]+)\)/i) ||
                      productBlock.match(/Link:\s*\[([^\]]+)\]\(([^)]+)\)/i) ||
                      productBlock.match(/\[([^\]]+)\]\(([^)]+)\)/);
    
    if (name) {
      products.push({
        id: `product-${startIdx}`,
        name,
        size: sizeMatch?.[1]?.trim() || '',
        description: descriptionMatch?.[1]?.trim() || '',
        price: priceMatch?.[1]?.trim() || '',
        image: imageMatch?.[2] || '',
        link: linkMatch?.[2] || '',
      });
    }
  }
  
  // Remove product sections from content to avoid duplication
  if (products.length > 0) {
    // Remove product blocks from content in reverse order to preserve indices
    let modifiedContent = content;
    for (let i = productRanges.length - 1; i >= 0; i--) {
      const { start, end } = productRanges[i];
      modifiedContent = modifiedContent.substring(0, start) + modifiedContent.substring(end);
    }
    cleanedContent = modifiedContent.trim();
  }
  
  return { products, cleanedContent };
}

export default function MessageRenderer({ content, role }: MessageRendererProps) {
  // For user messages, just render as plain text with basic formatting
  if (role === 'user') {
    return (
      <p className="text-sm text-white leading-relaxed whitespace-pre-wrap">
        {content}
      </p>
    );
  }

  // Custom components for better rendering
  const components = {
    // Render images with proper styling
    img: ({ src, alt, ...props }: React.ComponentProps<'img'>) => (
      <div className="my-4">
        <div className="relative group">
          <img
            src={src}
            alt={alt}
            className="rounded-lg shadow-md max-w-full h-auto cursor-pointer hover:shadow-lg"
            onError={(e) => {
              const target = e.target as HTMLImageElement;
              target.style.display = 'none';
              const fallback = target.nextElementSibling as HTMLElement;
              if (fallback) fallback.style.display = 'block';
            }}
            width={100}
            height={100}
            {...props}
          />
          <div className="hidden bg-gray-100 border border-gray-300 rounded-lg p-4 text-center text-gray-500">
            <ImageIcon className="w-8 h-8 mx-auto mb-2 text-gray-400" />
            <p className="text-sm">Image could not be loaded</p>
            <a 
              href={typeof src === 'string' ? src : undefined} 
              target="_blank" 
              rel="noopener noreferrer"
              className="text-blue-600 hover:text-blue-800 text-xs underline mt-2 inline-block"
            >
              View original
            </a>
          </div>
          {/* <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-10 transition-all rounded-lg flex items-center justify-center">
            <ImageIcon className="w-6 h-6 text-white opacity-0 group-hover:opacity-100 transition-opacity" />
          </div> */}
        </div>
        {alt && (
          <p className="text-sm text-gray-600 mt-2 text-center italic">{alt}</p>
        )}
      </div>
    ),
    
    // Render links with external link icon
    a: ({ href, children, ...props }: React.ComponentProps<'a'>) => (
      <a
        href={href}
        target="_blank"
        rel="noopener noreferrer"
        className="inline-flex items-center text-blue-600 hover:text-blue-800 underline decoration-2 underline-offset-2 hover:decoration-blue-800 transition-colors"
        {...props}
      >
        {children}
        <ExternalLink className="w-3 h-3 ml-1" />
      </a>
    ),
    
    // Style headings
    h1: ({ children, ...props }: React.ComponentProps<'h1'>) => (
      <h1 className="text-2xl font-bold text-gray-900 mt-6 mb-4 first:mt-0" {...props}>
        {children}
      </h1>
    ),
    h2: ({ children, ...props }: React.ComponentProps<'h2'>) => (
      <h2 className="text-xl font-semibold text-gray-900 mt-5 mb-3 first:mt-0" {...props}>
        {children}
      </h2>
    ),
    h3: ({ children, ...props }: React.ComponentProps<'h3'>) => (
      <h3 className="text-lg font-medium text-gray-900 mt-4 mb-2 first:mt-0" {...props}>
        {children}
      </h3>
    ),
    
    // Style paragraphs
    p: ({ children, ...props }: React.ComponentProps<'p'>) => (
      <p className="text-gray-700 leading-relaxed mb-3 last:mb-0" {...props}>
        {children}
      </p>
    ),
    
    // Style lists
    ul: ({ children, ...props }: React.ComponentProps<'ul'>) => (
      <ul className=" list-inside space-y-2 mb-4 text-gray-700 list-none" {...props}>
        {children}
      </ul>
    ),
    ol: ({ children, ...props }: React.ComponentProps<'ol'>) => (
      <ol className="list-decimal list-inside space-y-2 mb-4 text-gray-700" {...props}>
        {children}
      </ol>
    ),
    li: ({ children, ...props }: React.ComponentProps<'li'>) => (
      <li className="leading-relaxed" {...props}>
        {children}
      </li>
    ),
    
    // Style code blocks
    code: ({ children, className, ...props }: React.ComponentProps<'code'>) => {
      const isInline = !className;
      if (isInline) {
        return (
          <code className="bg-gray-100 text-gray-800 px-2 py-1 rounded text-sm font-mono" {...props}>
            {children}
          </code>
        );
      }
      return (
        <code className="block bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto text-sm font-mono" {...props}>
          {children}
        </code>
      );
    },
    
    // Style blockquotes
    blockquote: ({ children, ...props }: React.ComponentProps<'blockquote'>) => (
      <blockquote className="border-l-4 border-blue-500 pl-4 py-2 bg-blue-50 text-gray-700 italic my-4" {...props}>
        {children}
      </blockquote>
    ),
    
    // Style strong/bold text
    strong: ({ children, ...props }: React.ComponentProps<'strong'>) => (
      <strong className="font-semibold text-gray-900" {...props}>
        {children}
      </strong>
    ),
    
    // Style emphasis/italic text
    em: ({ children, ...props }: React.ComponentProps<'em'>) => (
      <em className="italic text-gray-800" {...props}>
        {children}
      </em>
    ),
  };

  const parseResult = parseProducts(content);
  const hasProducts = parseResult.products.length > 0;
  
  // Debug logging
  if (hasProducts) {
    console.log('Parsed products:', parseResult.products);
    console.log('Original content:', content);
  }

  return (
    <div>
      {/* Render product listings if any */}
      {hasProducts && <ProductListing products={parseResult.products} />}
      
      {/* Render the cleaned content without product listings */}
      {parseResult.cleanedContent && (
        <div className="prose prose-sm max-w-none prose-gray">
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            rehypePlugins={[rehypeSanitize]}
            components={components}
          >
            {parseResult.cleanedContent}
          </ReactMarkdown>
        </div>
      )}
    </div>
  );
}
