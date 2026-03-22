# s03: TodoWrite - TODO

## 官方定义

- **行数**: ~176 行
- **工具数**: 5 个
- **核心理念**: "An agent without a plan drifts; list the steps first, then execute"

## 待办事项

### ❌ 未完成
- [ ] `TodoManager` 类实现
- [ ] `todo_add` 工具 - 添加待办
- [ ] `todo_list` 工具 - 列出待办
- [ ] `todo_done` 工具 - 标记完成

### 🔴 高优先级
- [ ] **Nag Reminder 机制**: 连续 3 轮不调用 `todo` 工具时注入 `<reminder>Update your todos.</reminder>`
- [ ] 强制 `in_progress` 任务只能有一个
- [ ] `rounds_since_todo` 计数器实现

### 验证方式
```bash
python -c "from agent.core.todo import TodoManager; tm = TodoManager(); print('OK')"
```
