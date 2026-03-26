interface Notification {
  id: string
  message: string
  time: string
  read: boolean
}

const mockNotifications: Notification[] = [
  { id: '1', message: '会议将在 10 分钟后开始', time: '10:00', read: false },
  { id: '2', message: '邮件已发送成功', time: '09:30', read: true },
]

export function NotificationCenter() {
  return (
    <div className="mb-4">
      <h3 className="font-semibold mb-2 text-sm">通知中心</h3>
      <div className="space-y-2">
        {mockNotifications.map((n) => (
          <div
            key={n.id}
            className={`text-sm p-2 rounded ${
              n.read ? 'text-gray-500' : 'bg-blue-50 text-blue-700'
            }`}
          >
            <div>{n.message}</div>
            <div className="text-xs opacity-60">{n.time}</div>
          </div>
        ))}
      </div>
    </div>
  )
}
