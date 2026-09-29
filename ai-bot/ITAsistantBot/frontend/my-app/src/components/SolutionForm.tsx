import { useMemo } from 'react'
import type { FormData } from '../types'
import { RichTextEditor } from './RichTextEditor'
import { TagInput } from './TagInput'
import { TEXT, PLACEHOLDERS, VALIDATION, COLOR_CLASSES } from '../common/app-constants'

interface SolutionFormProps {
  formData: FormData
  onChange: (data: FormData) => void
  onSubmit: (e: React.FormEvent) => void
  onCancel: () => void
  isSubmitting: boolean
  isEditing: boolean
}

export const SolutionForm = ({ 
  formData, 
  onChange, 
  onSubmit, 
  onCancel, 
  isSubmitting,
  isEditing 
}: SolutionFormProps) => {
  // Derive tags from formData.triggers
  const tags = useMemo(() => {
    return formData.triggers ? formData.triggers.split(',').map(t => t.trim()).filter(t => t.length > 0) : []
  }, [formData.triggers])

  const handleChange = (field: keyof FormData, value: string) => {
    onChange({ ...formData, [field]: value })
  }

  const handleTagsChange = (newTags: string[]) => {
    onChange({ ...formData, triggers: newTags.join(', ') })
  }

  return (
    <div className={`max-w-3xl mx-auto mb-8 ${COLOR_CLASSES.bgCard} rounded-xl shadow-lg p-6 border border-gray-200 animate-slideDown`}>
      <h2 className={`text-2xl font-bold ${COLOR_CLASSES.textPrimary} mb-6 flex items-center gap-2`}>
        <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
        </svg>
        {isEditing ? TEXT.editSolution : TEXT.addSolution}
      </h2>
      <form onSubmit={onSubmit} className="space-y-4">
        <div>
          <label className={`block text-sm font-medium ${COLOR_CLASSES.textPrimary} mb-1`}>
            Title <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            value={formData.title}
            onChange={(e) => handleChange('title', e.target.value)}
            className={`w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none ${COLOR_CLASSES.inputFocus} transition-all`}
            placeholder={PLACEHOLDERS.title}
            required
          />
        </div>

        <div>
          <label className={`block text-sm font-medium ${COLOR_CLASSES.textPrimary} mb-1`}>
            {TEXT.problemStatement} <span className="text-red-500">*</span>
          </label>
          <textarea
            value={formData.problem_statement}
            onChange={(e) => handleChange('problem_statement', e.target.value)}
            className={`w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none ${COLOR_CLASSES.inputFocus} transition-all resize-none`}
            rows={3}
            placeholder={PLACEHOLDERS.problem}
            required
          />
        </div>

        <div>
          <label className={`block text-sm font-medium ${COLOR_CLASSES.textPrimary} mb-1`}>
            {TEXT.solutionStepsLabel} <span className="text-red-500">*</span>
          </label>
          <RichTextEditor
            value={formData.description}
            onChange={(value) => handleChange('description', value)}
            placeholder={PLACEHOLDERS.solution}
            rows={6}
          />
        </div>

        <div>
          <label className={`block text-sm font-medium ${COLOR_CLASSES.textPrimary} mb-1`}>
            {TEXT.triggerKeywords} <span className="text-red-500">*</span>
          </label>
          <TagInput
            value={tags}
            onChange={handleTagsChange}
            placeholder={PLACEHOLDERS.tags}
          />
          {tags.length === 0 && (
            <p className="text-xs text-red-500 mt-1">{VALIDATION.tagsRequired}</p>
          )}
        </div>

        <div>
          <label className={`block text-sm font-medium ${COLOR_CLASSES.textPrimary} mb-1`}>
            {TEXT.nextStep} <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            value={formData.next_step}
            onChange={(e) => handleChange('next_step', e.target.value)}
            className={`w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none ${COLOR_CLASSES.inputFocus} transition-all`}
            placeholder={PLACEHOLDERS.nextStep}
            required
          />
        </div>

        <div className="flex gap-3 pt-4">
          <button
            type="submit"
            disabled={isSubmitting}
            className={`flex-1 px-6 py-3 ${COLOR_CLASSES.buttonPrimary} text-white rounded-lg transition-all font-medium shadow-md hover:shadow-lg transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none flex items-center justify-center gap-2`}
          >
            {isSubmitting ? (
              <>
                <svg className="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                {isEditing ? 'Updating...' : 'Adding...'}
              </>
            ) : (
              isEditing ? 'Update Solution' : 'Add Solution'
            )}
          </button>
          <button
            type="button"
            onClick={onCancel}
            className={`px-6 py-3 ${COLOR_CLASSES.buttonSecondary} ${COLOR_CLASSES.textPrimary} rounded-lg transition-colors font-medium`}
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  )
}

