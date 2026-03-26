import { Badge } from '../common/Badge'

interface Task {
  id: string
  title: string
  status: 'pending' | 'in_progress' | 'done'
}

const mockTasks: Task[] = [
  { id: '1', title: '完成报告', status: 'in_progress' },
  { id: '2', title: '回复邮件', status: 'pending' },
  { id: '3', title: '安排会议', status: 'done' },
]

export function TaskList() {
  const statusVariant = (status: Task['status']) => {
    if (status === 'done') return 'success'
    if (status === 'in_progress') return 'warning'
    return 'default'
  }

  return (
    <div className="mb-4">
      <h3 className="font-semibold mb-2 text-sm">任务列表</h3>
      <div className="space-y-2">
        {mockTasks.map((task) => (
          <div key={task.id} className="flex items-center gap-2 text-sm">
            <span className={task.status === 'done' ? 'line-through text-gray-400' : ''}>
              {task.title}
            </span>
            <Badge variant={statusVariant(task.status)}>
              {task.status === 'done' ? '完成' : task.status === 'in_progress' ? '进行中' : '待办'}
            </Badge>
          </div>
        ))}
      </div>
    </div>
  )
}
