import { TEXT, COLOR_CLASSES } from '../common/app-constants'

interface HeaderProps {
  onAddClick: () => void
}

export const Header = ({ onAddClick }: HeaderProps) => {
  return (
    <header className="fixed top-0 left-0 right-0 z-30 bg-white/95 backdrop-blur-sm shadow-md border-b border-gray-200/50">
      <div className="container mx-auto px-4 max-w-6xl">
        <div className="flex items-center justify-between h-16">
          {/* Logo and Title on the left */}
          <div className="flex items-center gap-3">
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-br from-purple-500 via-purple-500 to-green-500 rounded-xl blur-md opacity-50"></div>
              <div className="relative w-12 h-12 bg-gradient-to-br from-purple-600 via-purple-500 to-green-500 rounded-xl flex items-center justify-center shadow-lg transform hover:scale-105 transition-transform duration-300">
                <svg className="w-7 h-7 text-white drop-shadow-lg" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
              </div>
            </div>
            <div className="relative">
              <h1 className={`text-2xl font-extrabold ${COLOR_CLASSES.textGradient}`}>
                {TEXT.appTitle}
              </h1>
            </div>
          </div>

          {/* Add New Solution button on the right */}
          <button
            onClick={onAddClick}
            className={`group relative px-4 py-2 ${COLOR_CLASSES.buttonPrimary} text-white rounded-lg transition-all duration-300 font-semibold flex items-center gap-2 shadow-lg hover:shadow-xl transform hover:scale-105 overflow-hidden`}
          >
            {/* Animated gradient overlay */}
            <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-1000"></div>
            
            {/* Button content */}
            <div className="relative flex items-center gap-2">
              <svg className="w-4 h-4 transform group-hover:rotate-90 transition-transform duration-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M12 4v16m8-8H4" />
              </svg>
              <span className="text-sm">{TEXT.addSolution}</span>
            </div>
          </button>
        </div>
      </div>
    </header>
  )
}

