import { useState, useEffect } from 'react'
import { useLocation, useNavigate, useParams } from 'react-router-dom'
import botData from '../bot.json'
import type { BotSolution, FormData } from '../types'
import { loadSolutions, saveSolutions } from '../utils/storage'
import { useToast } from '../hooks/useToast'
import { SolutionDetail } from '../components/SolutionDetail'
import { SolutionForm } from '../components/SolutionForm'
import { DeleteModal } from '../components/DeleteModal'
import { ToastContainer } from '../components/Toast'
import { PageHeader } from '../components/PageHeader'
import { Header } from '../components/Header'
import { COLOR_CLASSES } from '../common/app-constants'

export const SolutionDetailPage = () => {
  const location = useLocation()
  const navigate = useNavigate()
  const { index } = useParams()
  const { toasts, showToast } = useToast()
  
  const [solution, setSolution] = useState<BotSolution | null>(null)
  const [isCustom, setIsCustom] = useState(false)
  const [showForm, setShowForm] = useState(false)
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [extraSolutions, setExtraSolutions] = useState(loadSolutions)
  const [formData, setFormData] = useState<FormData>({
    title: '',
    problem_statement: '',
    description: '',
    triggers: '',
    next_step: ''
  })

  useEffect(() => {
    // Get solution from location state or find by index
    if (location.state?.solution) {
      setSolution(location.state.solution)
      setIsCustom(location.state.isCustom || false)
    } else if (index !== undefined) {
      const allSolutions = [...(botData as BotSolution[]), ...extraSolutions]
      const solutionIndex = parseInt(index)
      if (solutionIndex >= 0 && solutionIndex < allSolutions.length) {
        const foundSolution = allSolutions[solutionIndex]
        setSolution(foundSolution)
        setIsCustom(extraSolutions.includes(foundSolution))
      } else {
        navigate('/')
      }
    } else {
      navigate('/')
    }
  }, [index, location.state, navigate, extraSolutions])

  useEffect(() => {
    const handleKeyPress = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && showForm) {
        setShowForm(false)
        setFormData({
          title: '',
          problem_statement: '',
          description: '',
          triggers: '',
          next_step: ''
        })
      }
    }
    window.addEventListener('keydown', handleKeyPress)
    return () => window.removeEventListener('keydown', handleKeyPress)
  }, [showForm])

  if (!solution) {
    return null
  }

  const solutionIndex = isCustom ? extraSolutions.indexOf(solution) : -1

  const handleFormSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (solutionIndex === -1) return

    setIsSubmitting(true)
    await new Promise(resolve => setTimeout(resolve, 300))

    const updatedSolution: BotSolution = {
      title: formData.title.trim(),
      problem_statement: formData.problem_statement.trim(),
      description: formData.description.trim(),
      action: {
        trigger: formData.triggers.split(',').map(t => t.trim()).filter(t => t.length > 0),
        next_step: formData.next_step.trim()
      }
    }

    if (!updatedSolution.title || !updatedSolution.problem_statement || !updatedSolution.description || updatedSolution.action.trigger.length === 0) {
      showToast('Please fill in all required fields', 'error')
      setIsSubmitting(false)
      return
    }

    const updated = [...extraSolutions]
    updated[solutionIndex] = updatedSolution
    setExtraSolutions(updated)
    saveSolutions(updated)
    setSolution(updatedSolution)
    setShowForm(false)
    showToast('Solution updated successfully!', 'success')
    setIsSubmitting(false)
  }

  const handleEdit = () => {
    setFormData({
      title: solution.title,
      problem_statement: solution.problem_statement,
      description: solution.description,
      triggers: solution.action.trigger.join(', '),
      next_step: solution.action.next_step
    })
    setShowForm(true)
  }

  const handleDelete = () => {
    if (solutionIndex === -1) return
    const updated = extraSolutions.filter((_, i) => i !== solutionIndex)
    setExtraSolutions(updated)
    saveSolutions(updated)
    setShowDeleteConfirm(false)
    showToast('Solution deleted successfully!', 'success')
    navigate('/')
  }

  const cancelForm = () => {
    setShowForm(false)
    setFormData({
      title: '',
      problem_statement: '',
      description: '',
      triggers: '',
      next_step: ''
    })
  }

  if (showForm) {
    return (
      <div className={`min-h-screen ${COLOR_CLASSES.bgGradient}`}>
        <ToastContainer toasts={toasts} />
        <Header onAddClick={() => navigate('/')} />
        <div className="container mx-auto px-4 py-8 max-w-6xl pt-24">
          <PageHeader 
            showBackButton={true}
            onBackClick={() => setShowForm(false)}
          />
          <div className="max-w-3xl mx-auto">
            <SolutionForm
              formData={formData}
              onChange={setFormData}
              onSubmit={handleFormSubmit}
              onCancel={cancelForm}
              isSubmitting={isSubmitting}
              isEditing={true}
            />
          </div>
        </div>
      </div>
    )
  }

  return (
    <>
      <ToastContainer toasts={toasts} />
      <Header onAddClick={() => navigate('/')} />
      <SolutionDetail
        solution={solution}
        isCustom={isCustom}
        onEdit={isCustom && solutionIndex !== -1 ? handleEdit : undefined}
        onDelete={isCustom && solutionIndex !== -1 ? () => setShowDeleteConfirm(true) : undefined}
      />
      {showDeleteConfirm && (
        <DeleteModal
          onConfirm={handleDelete}
          onCancel={() => setShowDeleteConfirm(false)}
        />
      )}
    </>
  )
}

