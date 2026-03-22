# s07: Tasks - TODO

## 官方定义

- **行数**: ~207 行
- **工具数**: 8 个
- **核心理念**: "A file-based task graph with ordering, parallelism, and dependencies"

## 待办事项

### ✅ 已完成
- [x] `TaskManager` 任务依赖图（`agent/core/tasks.py`）
- [x] 任务创建、依赖管理
- [x] 拓扑排序执行
- [x] 内置工具:
  - [x] `task_create`
  - [x] `task_update`
  - [x] `task_list`
  - [x] `task_depends`
- [x] TaskManager 在 `main.py` 中初始化并连接到 task tools
- [x] Task tools 在 `agent/core/dispatch.py` 中注册

### 验证方式
```bash
python -c "from agent.core.tasks import TaskManager; tm = TaskManager('.test_state'); print('OK')"
python -c "from agent.tools.builtin.task_create import TaskCreateTool; print('OK')"
```
