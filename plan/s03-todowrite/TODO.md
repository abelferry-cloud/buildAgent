# s03: TodoWrite - TODO

## 官方定义

- **行数**: ~176 行
- **工具数**: 5 个
- **核心理念**: "An agent without a plan drifts; list the steps first, then execute"

## 待办事项

### ✅ 已完成
- [x] `TodoManager` 类实现（`agent/core/todo.py`）
- [x] `todo_add` 工具 - 添加待办
- [x] `todo_list` 工具 - 列出待办
- [x] `todo_done` 工具 - 标记完成
- [x] `todo_start` 工具 - 标记进行中

### ✅ 已完成
- [x] **Nag Reminder 机制**: 连续 3 轮不调用 `todo` 工具时注入 `<reminder>Update your todos.</reminder>`
- [x] 强制 `in_progress` 任务只能有一个
- [x] `rounds_since_todo` 计数器实现

### 验证方式
```bash
python main.py
```

试试这些 prompt (英文 prompt 对 LLM 效果更好, 也可以用中文):

- Refactor the file hello.py: add type hints, docstrings, and a main guard
- Create a Python package with __init__.py, utils.py, and tests/test_utils.py
- Review all Python files and fix any style issues
