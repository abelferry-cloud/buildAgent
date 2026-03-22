# S03: TodoWrite - 总结

## 核心理念

> Todo list with Nag Reminder - keep the agent on track

## 核心原理

S03 实现了内存中的 Todo 列表管理，并集成了 Nag Reminder（唠叨提醒）机制。当 Agent 超过3轮对话未使用 todo 工具时，系统会自动注入提醒消息。

### TodoManager 核心功能

- **添加任务** - `add(task, priority)` 创建带优先级的新任务
- **列出任务** - `list()` 返回按优先级排序的待办列表
- **完成任务** - `done(todo_id)` 标记任务已完成
- **开始任务** - `start(todo_id)` 标记任务进行中（同时只能有一个进行中任务）
- **唠叨提醒** - `should_nag()` / `get_nag_message()` 实现定时提醒

### Nag Reminder 机制

1. Agent 每次循环检查 `todo_manager.should_nag()`
2. 如果超过阈值（默认3轮）未使用 todo 工具
3. 将 `<reminder>Update your todos.</reminder>` 注入到系统提示

## 关键类/组件

| 名称 | 文件 | 职责 |
|------|------|------|
| `Todo` | `agent/core/todo.py` | Todo 数据结构，包含 id, task, priority, done, in_progress |
| `TodoManager` | `agent/core/todo.py` | Todo 列表管理器，负责增删改查和唠叨提醒 |

## 涉及的文件

### 核心文件
- `agent/core/todo.py` - TodoManager 实现

### 工具文件
- `agent/tools/builtin/todo_add.py` - `todo_add` 工具
- `agent/tools/builtin/todo_list.py` - `todo_list` 工具
- `agent/tools/builtin/todo_done.py` - `todo_done` 工具
- `agent/tools/builtin/todo_start.py` - `todo_start` 工具

## 与 main.py 的集成

```python
from agent.core.todo import TodoManager

todo_manager = TodoManager()
from agent.tools.builtin.todo_add import set_todo_manager as set_todo_add_manager
from agent.tools.builtin.todo_list import set_todo_manager as set_todo_list_manager
from agent.tools.builtin.todo_done import set_todo_manager as set_todo_done_manager
from agent.tools.builtin.todo_start import set_todo_manager as set_todo_start_manager

set_todo_add_manager(todo_manager)
set_todo_list_manager(todo_manager)
set_todo_done_manager(todo_manager)
set_todo_start_manager(todo_manager)

# 创建 Agent 时注入
agent = Agent(..., todo_manager=todo_manager)
```

## 工具列表

| 工具名 | 类 | 功能 |
|--------|-----|------|
| `todo_add` | TodoAddTool | 添加新任务 |
| `todo_list` | TodoListTool | 列出所有待办 |
| `todo_done` | TodoDoneTool | 标记任务完成 |
| `todo_start` | TodoStartTool | 标记任务进行中 |

## 架构图

```
┌─────────────────────────────────────┐
│           TodoManager               │
│  ┌───────────────────────────────┐  │
│  │ _todos: dict[str, Todo]      │  │
│  │ _nag_round: int              │  │
│  │ NAG_THRESHOLD = 3           │  │
│  └───────────────────────────────┘  │
│  add() │ list() │ done() │ start() │
└─────────────────────────────────────┘
              ▲
              │ set_todo_manager()
              │
┌─────────────┴─────────────┐
│      todo_* 工具          │
│ (set_todo_manager 注入)    │
└───────────────────────────┘
```
