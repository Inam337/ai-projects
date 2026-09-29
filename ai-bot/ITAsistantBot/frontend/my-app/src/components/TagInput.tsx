import { useState, useRef } from 'react'
import type { KeyboardEvent } from 'react'
import { PLACEHOLDERS, COLOR_CLASSES } from '../common/app-constants'

interface TagInputProps {
  value: string[]
  onChange: (tags: string[]) => void
  placeholder?: string
}

export const TagInput = ({ value, onChange, placeholder = PLACEHOLDERS.tags }: TagInputProps) => {
  const [inputValue, setInputValue] = useState('')
  const inputRef = useRef<HTMLInputElement>(null)
  const [isFocused, setIsFocused] = useState(false)
  const [showTooltip, setShowTooltip] = useState(false)

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && inputValue.trim()) {
      e.preventDefault()
      const newTag = inputValue.trim()
      if (!value.includes(newTag)) {
        onChange([...value, newTag])
      }
      setInputValue('')
    } else if (e.key === 'Backspace' && !inputValue && value.length > 0) {
      onChange(value.slice(0, -1))
    } else if (e.key === 'Escape') {
      setInputValue('')
      inputRef.current?.blur()
    }
  }

  const removeTag = (tagToRemove: string) => {
    onChange(value.filter(tag => tag !== tagToRemove))
  }

  const handlePaste = (e: React.ClipboardEvent<HTMLInputElement>) => {
    e.preventDefault()
    const pastedText = e.clipboardData.getData('text')
    const tags = pastedText.split(',').map(t => t.trim()).filter(t => t.length > 0)
    const newTags = [...value, ...tags.filter(tag => !value.includes(tag))]
    onChange(newTags)
    setInputValue('')
  }

  return (
    <div className={`w-full min-h-[48px] px-3 py-2 border-2 rounded-lg transition-all ${isFocused ? COLOR_CLASSES.borderFocus : 'border-gray-300'} bg-white`}>
      <div className="flex flex-wrap gap-2 items-center">
        {value.map((tag, index) => (
          <span
            key={index}
            className="inline-flex items-center gap-1.5 px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-sm font-medium"
          >
            {tag}
            <button
              type="button"
              onClick={() => removeTag(tag)}
              className="hover:bg-purple-200 rounded-full p-0.5 transition-colors"
              aria-label={`Remove ${tag}`}
            >
              <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </span>
        ))}
        <input
          ref={inputRef}
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyDown={handleKeyDown}
          onPaste={handlePaste}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
          placeholder={value.length === 0 ? placeholder : PLACEHOLDERS.tagsMore}
          className="flex-1 min-w-[120px] outline-none text-sm py-1"
        />
        <div className="relative">
          <button
            type="button"
            onMouseEnter={() => setShowTooltip(true)}
            onMouseLeave={() => setShowTooltip(false)}
            onFocus={() => setShowTooltip(true)}
            onBlur={() => setShowTooltip(false)}
            className="p-1 text-gray-400 hover:text-purple-600 transition-colors rounded-full hover:bg-purple-50 focus:outline-none focus:ring-2 focus:ring-purple-200"
            aria-label="Tag input hints"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </button>
          {showTooltip && (
            <div className="absolute right-0 bottom-full mb-2 w-64 p-3 bg-gray-900 text-white text-xs rounded-lg shadow-xl z-50 animate-fadeIn">
              <div className="space-y-1.5">
                <p className="font-semibold mb-2">Keyboard Shortcuts:</p>
                <div className="flex items-center gap-2">
                  <kbd className="px-1.5 py-0.5 bg-gray-700 rounded text-xs font-mono">Enter</kbd>
                  <span>to add tag</span>
                </div>
                <div className="flex items-center gap-2">
                  <kbd className="px-1.5 py-0.5 bg-gray-700 rounded text-xs font-mono">Backspace</kbd>
                  <span>to remove last tag</span>
                </div>
                <div className="flex items-center gap-2">
                  <kbd className="px-1.5 py-0.5 bg-gray-700 rounded text-xs font-mono">Escape</kbd>
                  <span>to clear input</span>
                </div>
                <p className="text-gray-300 text-[10px] mt-2 pt-2 border-t border-gray-700">
                  You can also paste comma-separated values
                </p>
              </div>
              {/* Tooltip arrow */}
              <div className="absolute top-full right-4 w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-gray-900"></div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

