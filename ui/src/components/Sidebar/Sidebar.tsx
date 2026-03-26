import { TaskList } from './TaskList'
import { NotificationCenter } from './NotificationCenter'
import { AgentStatus } from './AgentStatus'

export function Sidebar() {
  return (
    <div className="h-full overflow-y-auto p-4">
      <h2 className="font-bold mb-4">助手面板</h2>
      <TaskList />
      <NotificationCenter />
      <AgentStatus />
    </div>
  )
}
