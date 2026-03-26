import { useEffect, useRef, useCallback } from 'react'
import { useChatStore } from '../stores/chatStore'

export function useWebSocket(url: string) {
  const ws = useRef<WebSocket | null>(null)
  const addMessage = useChatStore((s) => s.addMessage)

  const connect = useCallback(() => {
    ws.current = new WebSocket(url)

    ws.current.onmessage = (event) => {
      const data = JSON.parse(event.data)
      if (data.type === 'response') {
        addMessage({
          role: data.agent === 'user' ? 'user' : 'assistant',
          content: data.content,
          agent: data.agent,
        })
      }
    }

    ws.current.onclose = () => {
      // Auto reconnect after 3 seconds
      setTimeout(connect, 3000)
    }
  }, [url, addMessage])

  useEffect(() => {
    connect()
    return () => {
      ws.current?.close()
    }
  }, [connect])

  const sendMessage = useCallback((content: string) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify({ type: 'message', content }))
    }
  }, [])

  return { sendMessage }
}