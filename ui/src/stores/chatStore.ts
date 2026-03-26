import { create } from 'zustand'

export interface Message {
  id: string
  role: 'user' | 'assistant' | 'agent'
  content: string
  agent?: string
  timestamp: number
}

interface ChatState {
  messages: Message[]
  addMessage: (msg: Omit<Message, 'id' | 'timestamp'>) => void
  clearMessages: () => void
}

export const useChatStore = create<ChatState>((set) => ({
  messages: [],
  addMessage: (msg) => set((state) => ({
    messages: [...state.messages, {
      ...msg,
      id: crypto.randomUUID(),
      timestamp: Date.now(),
    }]
  })),
  clearMessages: () => set({ messages: [] }),
}))