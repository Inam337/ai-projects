import type { BotSolution } from '../types'

export const STORAGE_KEY = 'bot-solutions-extra'

export const loadSolutions = (): BotSolution[] => {
  try {
    const stored = localStorage.getItem(STORAGE_KEY)
    if (stored) {
      return JSON.parse(stored)
    }
  } catch (e) {
    console.error('Error loading stored solutions:', e)
  }
  return []
}

export const saveSolutions = (solutions: BotSolution[]): void => {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(solutions))
}

