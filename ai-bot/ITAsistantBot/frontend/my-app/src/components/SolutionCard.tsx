import type { BotSolution } from '../types'
import { useNavigate } from 'react-router-dom'
import { COLOR_CLASSES, ANIMATION_DELAYS } from '../common/app-constants'

interface SolutionCardProps {
  solution: BotSolution
  solutionIndex: number
  isCustom: boolean
  index: number
  onEdit?: () => void
  onDelete?: () => void
}

export const SolutionCard = ({ solution, solutionIndex, isCustom, index, onEdit, onDelete }: SolutionCardProps) => {
  const navigate = useNavigate()

  const handleClick = () => {
    navigate(`/solution/${solutionIndex}`, { state: { solution, isCustom } })
  }

  return (
    <div
      onClick={handleClick}
      className={`${COLOR_CLASSES.bgCard} rounded-xl shadow-md hover:shadow-xl transition-all duration-300 cursor-pointer overflow-hidden border border-gray-100 ${COLOR_CLASSES.borderPrimary} group transform hover:scale-[1.02]`}
      style={{ animationDelay: `${index * ANIMATION_DELAYS.card}ms` }}
    >
      <div className="p-6">
        <div className="flex items-start justify-between mb-3">
          <h2 className={`text-xl font-bold ${COLOR_CLASSES.textGradient} group-hover:from-purple-700 group-hover:via-purple-600 group-hover:to-green-600 transition-all flex-1`}>
            {solution.title}
          </h2>
          <div className="flex items-center gap-2">
            {isCustom && onEdit && onDelete && (
              <div className="flex gap-1">
                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    onEdit()
                  }}
                  className="p-1.5 text-gray-400 hover:text-purple-600 transition-colors"
                  title="Edit"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                  </svg>
                </button>
                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    onDelete()
                  }}
                  className="p-1.5 text-gray-400 hover:text-red-600 transition-colors"
                  title="Delete"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
              </div>
            )}
            <svg className="w-5 h-5 text-gray-400 group-hover:text-purple-600 transition-colors flex-shrink-0 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </div>
        </div>
        <p className={`${COLOR_CLASSES.textSecondary} mb-4 line-clamp-2`}>
          {solution.problem_statement}
        </p>
        <div className="flex flex-wrap gap-2">
          {solution.action.trigger.slice(0, 3).map((trigger, idx) => (
            <span
              key={idx}
              className={COLOR_CLASSES.badge}
            >
              {trigger}
            </span>
          ))}
          {solution.action.trigger.length > 3 && (
            <span className="px-2 py-1 bg-gray-100 text-gray-600 rounded-md text-xs font-medium">
              +{solution.action.trigger.length - 3} more
            </span>
          )}
        </div>
      </div>
    </div>
  )
}

