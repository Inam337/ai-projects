// Generate random session names like GitHub repository names
const adjectives = [
  'cozy', 'modern', 'elegant', 'vibrant', 'serene', 'chic', 'warm', 'bright',
  'minimalist', 'rustic', 'luxurious', 'playful', 'sophisticated', 'comfortable',
  'stylish', 'inviting', 'spacious', 'intimate', 'dramatic', 'peaceful',
  'creative', 'inspiring', 'relaxing', 'energetic', 'calm', 'bold', 'subtle',
  'artistic', 'functional', 'beautiful', 'unique', 'trendy', 'classic'
];

const nouns = [
  'living', 'bedroom', 'kitchen', 'office', 'studio', 'den', 'lounge', 'space',
  'room', 'area', 'corner', 'nook', 'retreat', 'sanctuary', 'haven', 'chamber',
  'quarters', 'suite', 'apartment', 'home', 'workspace', 'zone', 'spot',
  'design', 'project', 'vision', 'concept', 'idea', 'plan'
];

const colors = [
  'blue', 'green', 'white', 'gray', 'beige', 'cream', 'navy', 'charcoal',
  'sage', 'terracotta', 'blush', 'mint', 'lavender', 'coral', 'gold', 'silver',
  'amber', 'emerald', 'crimson', 'indigo', 'rose', 'teal', 'violet', 'bronze'
];

const designStyles = [
  'scandinavian', 'industrial', 'bohemian', 'farmhouse', 'mid-century',
  'contemporary', 'traditional', 'modern', 'minimalist', 'eclectic'
];

export function generateSessionName(): string {
  const patterns = [
    // Pattern 1: color-adjective-noun
    () => {
      const color = colors[Math.floor(Math.random() * colors.length)];
      const adjective = adjectives[Math.floor(Math.random() * adjectives.length)];
      const noun = nouns[Math.floor(Math.random() * nouns.length)];
      return `${color}-${adjective}-${noun}`;
    },
    // Pattern 2: adjective-noun
    () => {
      const adjective = adjectives[Math.floor(Math.random() * adjectives.length)];
      const noun = nouns[Math.floor(Math.random() * nouns.length)];
      return `${adjective}-${noun}`;
    },
    // Pattern 3: style-noun
    () => {
      const style = designStyles[Math.floor(Math.random() * designStyles.length)];
      const noun = nouns[Math.floor(Math.random() * nouns.length)];
      return `${style}-${noun}`;
    },
    // Pattern 4: color-style
    () => {
      const color = colors[Math.floor(Math.random() * colors.length)];
      const style = designStyles[Math.floor(Math.random() * designStyles.length)];
      return `${color}-${style}`;
    }
  ];
  
  const pattern = patterns[Math.floor(Math.random() * patterns.length)];
  return pattern();
}

// Examples: "cozy-living", "blue-modern-bedroom", "serene-kitchen", "sage-elegant-space", "scandinavian-lounge", "amber-industrial"

