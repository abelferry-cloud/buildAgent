# s07: Tasks - TODO

## 官方定义

- **行数**: ~207 行
- **工具数**: 8 个
- **核心理念**: "A file-based task graph with ordering, parallelism, and dependencies"

## 待办事项

### ❌ 未完成
- [ ] `TaskGraph` 任务依赖图（`agent/core/tasks.py`）
- [ ] 任务创建、依赖管理
- [ ] 拓扑排序执行
- [ ] 内置工具:
  - [ ] `task_create`
  - [ ] `task_update`
  - [ ] `task_list`
  - [ ] `task_depends`

### 验证方式
```bash
python -c "from agent.core.tasks import TaskGraph; tg = TaskGraph(); print('OK')"
```
