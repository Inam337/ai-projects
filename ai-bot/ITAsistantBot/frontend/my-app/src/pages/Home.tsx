import { useState, useMemo, useEffect, useRef } from 'react'
import botData from '../bot.json'
import type { BotSolution, FormData } from '../types'
import { loadSolutions, saveSolutions } from '../utils/storage'
import { useToast } from '../hooks/useToast'
import { Header } from '../components/Header'
import { SearchBar, type SearchBarRef } from '../components/SearchBar'
import { SolutionCard } from '../components/SolutionCard'
import { SolutionForm } from '../components/SolutionForm'
import { DeleteModal } from '../components/DeleteModal'
import { ToastContainer } from '../components/Toast'
import { COLOR_CLASSES } from '../common/app-constants'

export const Home = () => {
  const { toasts, showToast } = useToast()
  const [searchQuery, setSearchQuery] = useState('')
  const [showForm, setShowForm] = useState(false)
  const [editingIndex, setEditingIndex] = useState<number | null>(null)
  const [showDeleteConfirm, setShowDeleteConfirm] = useState<number | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [extraSolutions, setExtraSolutions] = useState<BotSolution[]>(loadSolutions)
  const searchBarRef = useRef<SearchBarRef>(null)
  const wasEmptyRef = useRef(true)
  const [formData, setFormData] = useState<FormData>({
    title: '',
    problem_statement: '',
    description: '',
    triggers: '',
    next_step: ''
  })

  const solutions = useMemo(() => {
    return [...(botData as BotSolution[]), ...extraSolutions]
  }, [extraSolutions])

  const filteredSolutions = useMemo(() => {
    if (!searchQuery.trim()) {
      return []
    }

    const query = searchQuery.toLowerCase()
    return solutions.filter(solution => {
      const titleMatch = solution.title.toLowerCase().includes(query)
      const triggerMatch = solution.action.trigger.some(trigger => 
        trigger.toLowerCase().includes(query)
      )
      const problemMatch = solution.problem_statement.toLowerCase().includes(query)
      return titleMatch || triggerMatch || problemMatch
    })
  }, [searchQuery, solutions])

  const handleFormSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSubmitting(true)

    const newSolution: BotSolution = {
      title: formData.title.trim(),
      problem_statement: formData.problem_statement.trim(),
      description: formData.description.trim(),
      action: {
        trigger: formData.triggers.split(',').map(t => t.trim()).filter(t => t.length > 0),
        next_step: formData.next_step.trim()
      }
    }

    if (!newSolution.title || !newSolution.problem_statement || !newSolution.description || newSolution.action.trigger.length === 0) {
      showToast('Please fill in all required fields', 'error')
      setIsSubmitting(false)
      return
    }

    try {
      // Update localStorage first
      if (editingIndex !== null) {
        const updated = [...extraSolutions]
        updated[editingIndex] = newSolution
        setExtraSolutions(updated)
        saveSolutions(updated)
      } else {
        const updated = [...extraSolutions, newSolution]
        setExtraSolutions(updated)
        saveSolutions(updated)
      }

      // Prepare all solutions for backend
      let allSolutions: BotSolution[]
      if (editingIndex !== null) {
        // When editing, use the updated extraSolutions
        const updated = [...extraSolutions]
        updated[editingIndex] = newSolution
        allSolutions = [...(botData as BotSolution[]), ...updated]
      } else {
        // When adding new, include the new solution
        allSolutions = [...(botData as BotSolution[]), ...extraSolutions, newSolution]
      }

      // Send to backend API
      const response = await fetch('http://localhost:3001/api/bot', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(allSolutions),
      })

      if (!response.ok) {
        throw new Error('Failed to save to backend')
      }

      await response.json()
      
      if (editingIndex !== null) {
        showToast('Solution updated successfully and saved to backend!', 'success')
        setEditingIndex(null)
      } else {
        showToast('Solution added successfully and saved to backend!', 'success')
      }
    } catch (error) {
      console.error('Error saving to backend:', error)
      // Still show success for localStorage save
      if (editingIndex !== null) {
        showToast('Solution updated (saved locally only - backend unavailable)', 'info')
        setEditingIndex(null)
      } else {
        showToast('Solution added (saved locally only - backend unavailable)', 'info')
      }
    }

    setFormData({
      title: '',
      problem_statement: '',
      description: '',
      triggers: '',
      next_step: ''
    })
    setShowForm(false)
    setIsSubmitting(false)
  }

  const handleEdit = (index: number) => {
    const solution = extraSolutions[index]
    setFormData({
      title: solution.title,
      problem_statement: solution.problem_statement,
      description: solution.description,
      triggers: solution.action.trigger.join(', '),
      next_step: solution.action.next_step
    })
    setEditingIndex(index)
    setShowForm(true)
  }

  const handleDelete = (index: number) => {
    const updated = extraSolutions.filter((_, i) => i !== index)
    setExtraSolutions(updated)
    saveSolutions(updated)
    setShowDeleteConfirm(null)
    showToast('Solution deleted successfully!', 'success')
  }


  const cancelForm = () => {
    setShowForm(false)
    setEditingIndex(null)
    setFormData({
      title: '',
      problem_statement: '',
      description: '',
      triggers: '',
      next_step: ''
    })
  }

  useEffect(() => {
    const handleKeyPress = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && showForm) {
        cancelForm()
      }
    }
    window.addEventListener('keydown', handleKeyPress)
    return () => window.removeEventListener('keydown', handleKeyPress)
  }, [showForm])

  // Maintain focus when transitioning from empty to non-empty search
  useEffect(() => {
    const isEmpty = !searchQuery.trim()
    const wasEmpty = wasEmptyRef.current
    
    // If we just transitioned from empty to non-empty, maintain focus
    if (wasEmpty && !isEmpty && searchBarRef.current) {
      // Use double requestAnimationFrame to ensure DOM update and layout are complete
      requestAnimationFrame(() => {
        requestAnimationFrame(() => {
          searchBarRef.current?.focus()
        })
      })
    }
    
    wasEmptyRef.current = isEmpty
  }, [searchQuery])

  return (
    <div className={`min-h-screen ${COLOR_CLASSES.bgGradient} overflow-x-hidden`}>
      <ToastContainer toasts={toasts} />
      
      <Header
        onAddClick={() => {
          if (!showForm) {
            setShowForm(true)
          }
        }}
      />
      
      <div className="container mx-auto px-4 py-4 max-w-6xl pt-20">

        {showForm && (
          <div className="animate-fadeInDown">
            <SolutionForm
              formData={formData}
              onChange={setFormData}
              onSubmit={handleFormSubmit}
              onCancel={cancelForm}
              isSubmitting={isSubmitting}
              isEditing={editingIndex !== null}
            />
          </div>
        )}

        {!showForm && (
          <div className="flex flex-col h-full">
            {!searchQuery.trim() ? (
              <div className="flex flex-col lg:flex-col items-start lg:items-center justify-center gap-2 lg:gap-2 mb-2">
                {/* Left Section - Search Interface */}
                <div className="flex w-full animate-fadeInLeft justify-center flex-col items-center">
                  <div className="relative mb-2">
                    <div className="absolute inset-0 bg-gradient-to-r from-purple-400/20 to-green-400/20 rounded-full blur-3xl animate-pulse"></div>
                    <div className="relative">
                      <svg className="w-16 h-16 mx-auto text-purple-500 drop-shadow-lg" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                      </svg>
                    </div>
                  </div>
                  
                  <h2 className="text-3xl lg:text-4xl font-bold mb-0 text-center lg:text-left">
                    <span className="bg-gradient-to-r from-purple-600 to-purple-500 bg-clip-text text-transparent">Start searching for</span>{' '}
                    <span className="bg-gradient-to-r from-green-500 to-green-600 bg-clip-text text-transparent">IT solutions</span>
                  </h2>
                  
                  <p className="text-gray-600 mb-6 text-center lg:text-left text-lg leading-relaxed">
                    Enter keywords, problem descriptions, or solution titles in the search bar below
                  </p>
                  
                  <div className="mb-1">
                    <SearchBar ref={searchBarRef} value={searchQuery} onChange={setSearchQuery} />
                  </div>
                  
                  <div className="flex justify-center lg:justify-start">
                    <div className="inline-flex items-center gap-2 px-4 py-2 mb-4 bg-white/70 backdrop-blur-sm rounded-lg border border-purple-100 shadow-sm">
                      <kbd className="px-2.5 py-1 bg-gray-100 rounded text-xs font-mono text-gray-700 shadow-sm font-semibold">Ctrl+K</kbd>
                      <span className="text-sm text-gray-600">to focus search</span>
                    </div>
                  </div>
                </div>

                {/* Right Section - How It Works Card */}
                <div className={`${COLOR_CLASSES.bgCard} rounded-2xl shadow-xl p-6 lg:p-8 border border-purple-100  w-full transform transition-all duration-300 hover:shadow-2xl hover:scale-[1.02] animate-fadeInRight`}>
                  <div className="flex items-center gap-3 mb-1">
                    <div className="w-8 h-8 bg-gradient-to-r from-purple-600 via-purple-500 to-green-500 rounded-xl flex items-center justify-center shadow-lg transform hover:rotate-12 transition-transform duration-300">
                      <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                      </svg>
                    </div>
                    <h3 className="text-lg font-bold">
                      <span className="bg-gradient-to-r from-purple-600 to-purple-500 bg-clip-text text-transparent">How It</span>{' '}
                      <span className="bg-gradient-to-r from-green-500 to-green-600 bg-clip-text text-transparent">Works</span>
                    </h3>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="flex flex-col items-center text-center group cursor-default p-3 rounded-lg hover:bg-purple-50/50 transition-colors duration-200">
                      <div className="w-10 h-10 bg-gradient-to-r from-purple-100 to-purple-50 text-purple-600 rounded-full flex items-center justify-center text-sm font-bold mb-3 shadow-sm group-hover:scale-110 group-hover:shadow-md transition-all duration-200">
                        1
                      </div>
                      <h4 className="font-bold text-gray-800 mb-2 text-sm">Search Solutions</h4>
                      <p className="text-xs text-gray-600 leading-relaxed">Type keywords, problem descriptions, or solution titles in the search bar to find relevant IT solutions.</p>
                    </div>

                    <div className="flex flex-col items-center text-center group cursor-default p-3 rounded-lg hover:bg-green-50/50 transition-colors duration-200">
                      <div className="w-10 h-10 bg-gradient-to-r from-green-100 to-green-50 text-green-600 rounded-full flex items-center justify-center text-sm font-bold mb-3 shadow-sm group-hover:scale-110 group-hover:shadow-md transition-all duration-200">
                        2
                      </div>
                      <h4 className="font-bold text-gray-800 mb-2 text-sm">View Details</h4>
                      <p className="text-xs text-gray-600 leading-relaxed">Click on any solution card to view detailed step-by-step instructions and related keywords.</p>
                    </div>

                    <div className="flex flex-col items-center text-center group cursor-default p-3 rounded-lg hover:bg-purple-50/50 transition-colors duration-200">
                      <div className="w-10 h-10 bg-gradient-to-r from-purple-100 to-purple-50 text-purple-600 rounded-full flex items-center justify-center text-sm font-bold mb-3 shadow-sm group-hover:scale-110 group-hover:shadow-md transition-all duration-200">
                        3
                      </div>
                      <h4 className="font-bold text-gray-800 mb-2 text-sm">Add Your Own</h4>
                      <p className="text-xs text-gray-600 leading-relaxed">Click "Add New Solution" to contribute your own IT solutions and help others in your team.</p>
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <>
                <div className="mb-6 animate-fadeInDown">
                  <SearchBar ref={searchBarRef} value={searchQuery} onChange={setSearchQuery} autoFocus={true} />
                </div>

                {searchQuery && filteredSolutions.length > 0 && (
                  <div className="text-center mb-6 animate-fadeInDown">
                    <div className="inline-flex items-center gap-2 px-5 py-2.5 bg-white/90 backdrop-blur-sm rounded-full shadow-md border border-purple-100">
                      <svg className="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      <p className="text-gray-700 font-medium">
                        Found <span className="font-bold text-purple-600">{filteredSolutions.length}</span> solution{filteredSolutions.length !== 1 ? 's' : ''}
                      </p>
                    </div>
                  </div>
                )}

                {filteredSolutions.length > 0 ? (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pb-6">
                    {filteredSolutions.map((solution, index) => {
                      const isCustom = extraSolutions.includes(solution)
                      const customIndex = isCustom ? extraSolutions.indexOf(solution) : -1
                      // Find the index in the full solutions array
                      const fullIndex = solutions.indexOf(solution)
                      
                      return (
                        <div
                          key={index}
                          className="animate-fadeInUp"
                          style={{ 
                            animationDelay: `${index * 100}ms`,
                            animationFillMode: 'both'
                          }}
                        >
                          <SolutionCard
                            solution={solution}
                            solutionIndex={fullIndex}
                            index={index}
                            isCustom={isCustom}
                            onEdit={isCustom && customIndex !== -1 ? () => handleEdit(customIndex) : undefined}
                            onDelete={isCustom && customIndex !== -1 ? () => setShowDeleteConfirm(customIndex) : undefined}
                          />
                        </div>
                      )
                    })}
                  </div>
                ) : (
                  <div className="flex items-center justify-center py-16 animate-fadeIn">
                    <div className="text-center max-w-md">
                      <div className="relative inline-block mb-6">
                        <div className="absolute inset-0 bg-purple-200 rounded-full blur-2xl opacity-30 animate-pulse"></div>
                        <svg className="relative w-28 h-28 text-gray-300 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                      </div>
                      <h3 className="text-2xl font-bold text-gray-700 mb-3">No solutions found</h3>
                      <p className="text-gray-500 mb-6 text-lg">Try a different search term or check your spelling</p>
                      <button
                        onClick={() => setSearchQuery('')}
                        className="inline-flex items-center gap-2 px-5 py-2.5 text-sm font-medium text-white bg-gradient-to-r from-purple-600 via-purple-500 to-green-500 hover:from-purple-700 hover:via-purple-600 hover:to-green-600 rounded-lg transition-all shadow-md hover:shadow-lg transform hover:scale-105"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                        Clear search
                      </button>
                    </div>
                  </div>
                )}
              </>
            )}
          </div>
          
        )}

        {showDeleteConfirm !== null && (
          <DeleteModal
            onConfirm={() => handleDelete(showDeleteConfirm)}
            onCancel={() => setShowDeleteConfirm(null)}
          />
        )}
      </div>
    </div>
  )
}

