# s12: Worktree + Task Isolation - TODO

## 官方定义

- **行数**: ~694 行
- **工具数**: 16 个
- **核心理念**: "Each works in its own directory; tasks manage goals, worktrees manage directories, bound by ID"

## 待办事项

### ❌ 未完成
- [ ] `WorktreeManager` 工作树管理（`agent/core/worktree.py`）
- [ ] Git worktree 操作
- [ ] 目录隔离机制
- [ ] Worktree 工具:
  - [ ] `worktree_add`
  - [ ] `worktree_remove`
  - [ ] `worktree_list`
  - [ ] `worktree_status`

### 验证方式
```bash
python -c "from agent.core.worktree import WorktreeManager; print('OK')"
```
