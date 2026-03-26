import { Badge } from '../common/Badge'
import { useChatStore, AgentStatus as AgentStatusType } from '../../stores/chatStore'

export function AgentStatus() {
  const agentStatus = useChatStore((s) => s.agentStatus)

  const statusVariant = (status: AgentStatusType['status']) => {
    if (status === 'idle') return 'success'
    if (status === 'busy') return 'warning'
    return 'error'
  }

  const statusText = (status: AgentStatusType['status']) => {
    if (status === 'idle') return '空闲'
    if (status === 'busy') return '工作中'
    return '离线'
  }

  const displayAgents = agentStatus.length > 0 ? agentStatus : [
    { name: 'Main', status: 'idle' as const },
    { name: 'Search', status: 'idle' as const },
    { name: 'Schedule', status: 'idle' as const },
    { name: 'Document', status: 'idle' as const },
    { name: 'Email', status: 'offline' as const },
  ]

  return (
    <div>
      <h3 className="font-semibold mb-2 text-sm">Agent 状态</h3>
      <div className="space-y-1">
        {displayAgents.map((agent) => (
          <div key={agent.name} className="flex items-center justify-between text-sm">
            <span>{agent.name}</span>
            <Badge variant={statusVariant(agent.status)}>{statusText(agent.status)}</Badge>
          </div>
        ))}
      </div>
    </div>
  )
}
