import { Badge } from '../common/Badge'

interface Agent {
  name: string
  status: 'idle' | 'busy' | 'offline'
}

const agents: Agent[] = [
  { name: 'Main', status: 'idle' },
  { name: 'Search', status: 'idle' },
  { name: 'Schedule', status: 'busy' },
  { name: 'Document', status: 'idle' },
  { name: 'Email', status: 'offline' },
]

export function AgentStatus() {
  const statusVariant = (status: Agent['status']) => {
    if (status === 'idle') return 'success'
    if (status === 'busy') return 'warning'
    return 'error'
  }

  const statusText = (status: Agent['status']) => {
    if (status === 'idle') return '空闲'
    if (status === 'busy') return '工作中'
    return '离线'
  }

  return (
    <div>
      <h3 className="font-semibold mb-2 text-sm">Agent 状态</h3>
      <div className="space-y-1">
        {agents.map((agent) => (
          <div key={agent.name} className="flex items-center justify-between text-sm">
            <span>{agent.name}</span>
            <Badge variant={statusVariant(agent.status)}>{statusText(agent.status)}</Badge>
          </div>
        ))}
      </div>
    </div>
  )
}
