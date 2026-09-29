// Theme Colors - Light Green and Purple
export const THEME_COLORS = {
  // Purple shades
  purple: {
    50: '#faf5ff',
    100: '#f3e8ff',
    200: '#e9d5ff',
    300: '#d8b4fe',
    400: '#c084fc',
    500: '#a855f7',
    600: '#9333ea',
    700: '#7e22ce',
    800: '#6b21a8',
    900: '#581c87',
  },
  // Light Green shades
  green: {
    50: '#f0fdf4',
    100: '#dcfce7',
    200: '#bbf7d0',
    300: '#86efac',
    400: '#4ade80',
    500: '#22c55e',
    600: '#16a34a',
    700: '#15803d',
    800: '#166534',
    900: '#14532d',
  },
  // Neutral colors
  gray: {
    50: '#f9fafb',
    100: '#f3f4f6',
    200: '#e5e7eb',
    300: '#d1d5db',
    400: '#9ca3af',
    500: '#6b7280',
    600: '#4b5563',
    700: '#374151',
    800: '#1f2937',
    900: '#111827',
  },
  // Status colors
  success: '#22c55e',
  error: '#ef4444',
  info: '#3b82f6',
  warning: '#f59e0b',
}

// Gradient combinations
export const GRADIENTS = {
  primary: 'from-purple-600 via-purple-500 to-green-500',
  primaryHover: 'from-purple-700 via-purple-600 to-green-600',
  background: 'from-slate-50 via-green-50/30 to-purple-50/30',
  card: 'from-purple-50/50 via-green-50/30 to-purple-50/50',
  header: 'from-purple-600 via-purple-500 to-green-500',
  badge: 'from-purple-100 via-green-50 to-purple-100',
  step: 'from-purple-600 via-purple-500 to-green-500',
}

// Component-specific color classes
export const COLOR_CLASSES = {
  // Buttons
  buttonPrimary: 'bg-gradient-to-r from-purple-600 via-purple-500 to-green-500 hover:from-purple-700 hover:via-purple-600 hover:to-green-600',
  buttonSecondary: 'bg-gray-200 hover:bg-gray-300',
  buttonDanger: 'bg-red-600 hover:bg-red-700',
  
  // Text
  textPrimary: 'text-gray-800',
  textSecondary: 'text-gray-600',
  textGradient: 'bg-gradient-to-r from-purple-600 via-purple-500 to-green-500 bg-clip-text text-transparent',
  
  // Borders
  borderPrimary: 'border-purple-300 hover:border-purple-400',
  borderFocus: 'border-purple-500 focus:ring-purple-200',
  
  // Backgrounds
  bgCard: 'bg-white',
  bgGradient: 'bg-gradient-to-br from-slate-50 via-green-50/30 to-purple-50/30',
  
  // Badges/Tags
  badge: 'px-2 py-1 bg-gradient-to-r from-purple-100 via-green-50 to-purple-100 text-purple-700 border border-purple-200 rounded-md text-xs font-medium hover:border-purple-400 transition-colors',
  
  // Inputs
  inputFocus: 'focus:ring-2 focus:ring-purple-500 focus:border-transparent',
}

// Animation delays
export const ANIMATION_DELAYS = {
  card: 50,
  step: 100,
}

// Text constants
export const TEXT = {
  appTitle: 'IT Assistant Bot',
  appSubtitle: 'Find solutions to your IT problems quickly and easily',
  addSolution: 'Add New Solution',
  editSolution: 'Edit Solution',
  deleteSolution: 'Delete Solution',
  backToSearch: 'Back to Search',
  solutionSteps: 'Solution Steps',
  relatedKeywords: 'Related Keywords',
  nextStep: 'Next Step / Verification',
  triggerKeywords: 'Trigger Keywords',
  problemStatement: 'Problem Statement',
  solutionStepsLabel: 'Solution Steps',
}

// Placeholders
export const PLACEHOLDERS = {
  title: 'e.g., Display not showing or extending in Teams meeting',
  problem: 'Describe the problem...',
  solution: 'Format: 1) First step. 2) Second step. 3) Third step.',
  tags: 'Type and press Enter to add keywords',
  tagsMore: 'Add more tags...',
  nextStep: 'What should the user do to verify the solution worked?',
  search: 'Search by title, keywords, or problem description... (Ctrl+K)',
}

// Validation messages
export const VALIDATION = {
  titleRequired: 'Title is required',
  problemRequired: 'Problem statement is required',
  solutionRequired: 'Solution steps are required',
  tagsRequired: 'At least one keyword is required',
  nextStepRequired: 'Next step is required',
}

// Toast messages
export const TOAST_MESSAGES = {
  solutionAdded: 'Solution added successfully',
  solutionUpdated: 'Solution updated successfully',
  solutionDeleted: 'Solution deleted successfully',
  error: 'An error occurred. Please try again.',
}

