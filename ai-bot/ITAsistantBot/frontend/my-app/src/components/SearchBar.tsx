import { useRef, useEffect, useCallback, memo, useImperativeHandle, forwardRef } from 'react'
import { PLACEHOLDERS, COLOR_CLASSES } from '../common/app-constants'

interface SearchBarProps {
  value: string
  onChange: (value: string) => void
  autoFocus?: boolean
}

export interface SearchBarRef {
  focus: () => void
}

const SearchBarComponent = forwardRef<SearchBarRef, SearchBarProps>(({ value, onChange, autoFocus = false }, ref) => {
  const inputRef = useRef<HTMLInputElement>(null)

  useImperativeHandle(ref, () => ({
    focus: () => {
      inputRef.current?.focus()
      // Maintain cursor position at the end
      if (inputRef.current) {
        const length = inputRef.current.value.length
        inputRef.current.setSelectionRange(length, length)
      }
    }
  }))

  useEffect(() => {
    const handleKeyPress = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault()
        inputRef.current?.focus()
      }
    }

    window.addEventListener('keydown', handleKeyPress)
    return () => window.removeEventListener('keydown', handleKeyPress)
  }, [])

  // Auto-focus when autoFocus prop changes to true
  useEffect(() => {
    if (autoFocus && inputRef.current) {
      // Use requestAnimationFrame to ensure DOM is ready
      requestAnimationFrame(() => {
        inputRef.current?.focus()
        // Maintain cursor position at the end
        const length = inputRef.current?.value.length || 0
        inputRef.current?.setSelectionRange(length, length)
      })
    }
  }, [autoFocus])

  const handleChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    // Directly call onChange - React's controlled input handles cursor position naturally
    onChange(e.target.value)
  }, [onChange])

  const handleClear = useCallback((e: React.MouseEvent<HTMLButtonElement>) => {
    e.preventDefault()
    e.stopPropagation()
    onChange('')
    // Focus after clearing
    setTimeout(() => {
      inputRef.current?.focus()
    }, 0)
  }, [onChange])

  return (
    <div className="mb-4 backdrop:animate-fadeIn">
      <div className="relative max-w-4xl mx-auto">
        <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none z-10">
          <svg className="w-6 h-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>
        <input
          ref={inputRef}
          type="text"
          placeholder={PLACEHOLDERS.search}
          value={value}
          onChange={handleChange}
          className={`w-full pl-12 pr-12 py-4 text-lg border-2 border-gray-300 rounded-xl focus:outline-none ${COLOR_CLASSES.borderFocus} transition-all shadow-sm hover:shadow-md hover:border-purple-300 relative z-0 bg-white`}
          autoComplete="off"
          id="search-input"
        />
        {value && (
          <button
            type="button"
            onClick={handleClear}
            className="absolute inset-y-0 right-0 pr-4 flex items-center text-gray-400 hover:text-gray-600 z-20 transition-colors"
            aria-label="Clear search"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        )}
      </div>
    </div>
  )
})

SearchBarComponent.displayName = 'SearchBar'

// Custom comparison function for memo to prevent unnecessary re-renders
const arePropsEqual = (prevProps: SearchBarProps, nextProps: SearchBarProps) => {
  return prevProps.value === nextProps.value && prevProps.onChange === nextProps.onChange && prevProps.autoFocus === nextProps.autoFocus
}

export const SearchBar = memo(SearchBarComponent, arePropsEqual)

