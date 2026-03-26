import { useChatStore } from '../../stores/chatStore'
import { ChatMessage } from './ChatMessage'
import { ChatInput } from './ChatInput'

interface ChatWindowProps {
  onSend: (message: string) => void
}

export function ChatWindow({ onSend }: ChatWindowProps) {
  const messages = useChatStore((s) => s.messages)

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg) => (
          <ChatMessage key={msg.id} message={msg} />
        ))}
      </div>
      <ChatInput onSend={onSend} />
    </div>
  )
}