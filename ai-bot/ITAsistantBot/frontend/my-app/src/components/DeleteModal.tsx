import { TEXT, COLOR_CLASSES } from '../common/app-constants'

interface DeleteModalProps {
  onConfirm: () => void
  onCancel: () => void
}

export const DeleteModal = ({ onConfirm, onCancel }: DeleteModalProps) => {
  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 animate-fadeIn" onClick={onCancel}>
      <div className={`${COLOR_CLASSES.bgCard} rounded-xl shadow-2xl p-6 max-w-md mx-4 transform animate-scaleIn`} onClick={(e) => e.stopPropagation()}>
        <h3 className={`text-xl font-bold ${COLOR_CLASSES.textPrimary} mb-2`}>{TEXT.deleteSolution}?</h3>
        <p className={`${COLOR_CLASSES.textSecondary} mb-6`}>Are you sure you want to delete this solution? This action cannot be undone.</p>
        <div className="flex gap-3">
          <button
            onClick={onConfirm}
            className={`flex-1 px-4 py-2 ${COLOR_CLASSES.buttonDanger} text-white rounded-lg transition-colors font-medium`}
          >
            Delete
          </button>
          <button
            onClick={onCancel}
            className={`flex-1 px-4 py-2 ${COLOR_CLASSES.buttonSecondary} ${COLOR_CLASSES.textPrimary} rounded-lg transition-colors font-medium`}
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  )
}

