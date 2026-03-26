import { ChatWindow } from './components/Chat/ChatWindow'
import { Sidebar } from './components/Sidebar/Sidebar'
import { useWebSocket } from './hooks/useWebSocket'

function App() {
  const { sendMessage } = useWebSocket('ws://localhost:8000/ws/user1')

  return (
    <div className="flex h-screen">
      <div className="flex-1">
        <ChatWindow onSend={sendMessage} />
      </div>
      <div className="w-80 border-l">
        <Sidebar />
      </div>
    </div>
  )
}

export default App