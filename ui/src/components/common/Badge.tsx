interface BadgeProps {
  variant?: 'success' | 'warning' | 'error' | 'default'
  children: React.ReactNode
}

export function Badge({ variant = 'default', children }: BadgeProps) {
  const colors = {
    success: 'bg-green-100 text-green-800',
    warning: 'bg-yellow-100 text-yellow-800',
    error: 'bg-red-100 text-red-800',
    default: 'bg-gray-100 text-gray-800',
  }

  return (
    <span className={`px-2 py-0.5 rounded text-xs ${colors[variant]}`}>
      {children}
    </span>
  )
}
