import { Message } from '../../stores/chatStore'

interface ChatMessageProps {
  message: Message
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === 'user'

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`max-w-[70%] rounded-lg px-4 py-2 ${
          isUser
            ? 'bg-blue-500 text-white'
            : 'bg-gray-100 text-gray-900'
        }`}
      >
        {message.agent && !isUser && (
          <div className="text-xs opacity-70 mb-1">{message.agent}</div>
        )}
        <div>{message.content}</div>
      </div>
    </div>
  )
}