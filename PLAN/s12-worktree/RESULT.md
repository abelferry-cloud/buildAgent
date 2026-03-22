# s12: Worktree + Task Isolation - 实现效果

## 核心功能

### WorktreeManager（agent/core/worktree.py）

```python
class WorktreeManager:
    """Git worktree 管理器，实现目录级隔离"""

    def __init__(self, base_dir: str = "."):
        self.base_dir = base_dir

    def add(self, name: str, branch: str, create: bool = False) -> dict:
        """创建新的 worktree"""
        result = subprocess.run(
            ["git", "worktree", "add",
             f"{self.base_dir}/{name}",
             branch] + (["-b"] if create else []),
            capture_output=True,
            text=True
        )
        return {"success": result.returncode == 0, "output": result.stdout}

    def list(self) -> list[dict]:
        """列出所有 worktree"""
        result = subprocess.run(
            ["git", "worktree", "list", "--porcelain"],
            capture_output=True,
            text=True
        )
        return self._parse_worktree_list(result.stdout)

    def remove(self, name: str) -> dict:
        """移除 worktree"""
        result = subprocess.run(
            ["git", "worktree", "remove", name],
            capture_output=True,
            text=True
        )
        return {"success": result.returncode == 0, "output": result.stdout}
```

### 内置 Worktree 工具

| 工具 | 功能 |
|------|------|
| `worktree_add` | 创建 worktree |
| `worktree_remove` | 移除 worktree |
| `worktree_list` | 列出 worktree |
| `worktree_status` | 查看状态 |

## 关键设计

- **目录隔离**: 每个任务/代理在独立目录工作
- **ID 绑定**: 任务 ID 与 worktree 路径关联
- **并行执行**: 支持多个 worktree 同时工作

```
worktrees/
├── task-123/      # 任务 123 的工作目录
├── task-456/      # 任务 456 的工作目录
└── agent-alpha/   # agent-alpha 的工作目录
```
