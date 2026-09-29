import type { Toast as ToastType } from '../types'

interface ToastProps {
  toast: ToastType
  onClose: () => void
}

export const Toast = ({ toast }: ToastProps) => {
  const bgColor = 
    toast.type === 'success' ? 'bg-green-500' :
    toast.type === 'error' ? 'bg-red-500' :
    'bg-purple-500'

  return (
    <div
      className={`px-6 py-4 rounded-lg shadow-lg text-white font-medium transform transition-all animate-slideInRight ${bgColor}`}
    >
      <div className="flex items-center gap-2">
        {toast.type === 'success' && (
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
        )}
        {toast.type === 'error' && (
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        )}
        {toast.type === 'info' && (
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        )}
        <span>{toast.message}</span>
      </div>
    </div>
  )
}

interface ToastContainerProps {
  toasts: ToastType[]
}

export const ToastContainer = ({ toasts }: ToastContainerProps) => {
  return (
    <div className="fixed top-4 right-4 z-50 space-y-2">
      {toasts.map(toast => (
        <Toast key={toast.id} toast={toast} onClose={() => {}} />
      ))}
    </div>
  )
}

