import { create } from 'zustand'

export interface Message {
  id: string
  role: 'user' | 'assistant' | 'agent'
  content: string
  agent?: string
  timestamp: number
}

export interface AgentStatus {
  name: string
  status: 'idle' | 'busy' | 'offline'
}

interface ChatState {
  messages: Message[]
  agentStatus: AgentStatus[]
  addMessage: (msg: Omit<Message, 'id' | 'timestamp'>) => void
  clearMessages: () => void
  setAgentStatus: (agents: AgentStatus[]) => void
}

export const useChatStore = create<ChatState>((set) => ({
  messages: [],
  agentStatus: [],
  addMessage: (msg) => set((state) => ({
    messages: [...state.messages, {
      ...msg,
      id: crypto.randomUUID(),
      timestamp: Date.now(),
    }]
  })),
  clearMessages: () => set({ messages: [] }),
  setAgentStatus: (agents) => set({ agentStatus: agents }),
}))