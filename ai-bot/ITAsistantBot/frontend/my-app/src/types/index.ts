export interface BotSolution {
  title: string
  problem_statement: string
  description: string
  action: {
    trigger: string[]
    next_step: string
  }
}

export interface Toast {
  id: number
  message: string
  type: 'success' | 'error' | 'info'
}

export interface FormData {
  title: string
  problem_statement: string
  description: string
  triggers: string
  next_step: string
}

