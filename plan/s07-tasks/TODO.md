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
python main.py
```


试试这些 prompt (英文 prompt 对 LLM 效果更好, 也可以用中文):

Create 3 tasks: "Setup project", "Write code", "Write tests". Make them depend on each other in order.
List all tasks and show the dependency graph
Complete task 1 and then list tasks to see task 2 unblocked
Create a task board for refactoring: parse -> transform -> emit -> test, where transform and emit can run in parallel after parse