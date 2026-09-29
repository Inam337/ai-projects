import { TEXT, COLOR_CLASSES } from '../common/app-constants'

interface PageHeaderProps {
  title?: string
  subtitle?: string
  showBackButton?: boolean
  onBackClick?: () => void
}

export const PageHeader = ({ 
  showBackButton = false,
  onBackClick
}: PageHeaderProps) => {
  return (
    <div className="mb-4 animate-fadeInDown">
      {showBackButton && onBackClick && (
        <div className="flex justify-start mb-3">
          <button
            onClick={onBackClick}
            className="group flex items-center gap-2 px-4 py-2 rounded-lg bg-white border border-purple-200 hover:border-purple-400 shadow-sm hover:shadow-md transition-all duration-200 hover:bg-gradient-to-r hover:from-purple-50 hover:to-green-50"
          >
            <svg className="w-4 h-4 text-purple-600 transform group-hover:-translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            <span className={`text-sm font-medium ${COLOR_CLASSES.textGradient} group-hover:from-purple-700 group-hover:to-green-600 transition-all`}>
              {TEXT.backToSearch}
            </span>
          </button>
        </div>
      )}
    </div>
  )
}

