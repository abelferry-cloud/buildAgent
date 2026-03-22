# s12: Worktree + Task Isolation - TODO

## 官方定义

- **行数**: ~694 行
- **工具数**: 16 个
- **核心理念**: "Each works in its own directory; tasks manage goals, worktrees manage directories, bound by ID"

## 待办事项

### ✅ 已完成
- [x] `WorktreeManager` 工作树管理（`agent/core/worktree.py`）
- [x] `GitWorktreeManager` Git worktree 操作
- [x] 目录隔离机制
- [x] Worktree 工具:
  - [x] `worktree_create` - 创建 worktree
  - [x] `worktree_list` - 列出 worktree
  - [x] `worktree_switch` - 切换 worktree
  - [x] `worktree_destroy` - 销毁 worktree
- [x] WorktreeManager 在 `main.py` 中初始化并连接到 worktree tools
- [x] Worktree tools 在 `agent/core/dispatch.py` 中注册

### 验证方式
```bash
python -c "from agent.core.worktree import WorktreeManager; print('OK')"
```
