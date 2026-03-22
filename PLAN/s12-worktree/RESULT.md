# s12: Worktree + Task Isolation - 实现效果

## 核心功能

### WorktreeManager（agent/core/worktree.py）

```python
class WorktreeManager:
    """管理工作树生命周期，提供目录级隔离"""

    def __init__(self, base_dir: str):
        self._base_dir = base_dir
        self._worktrees: dict[str, Worktree] = {}

    def create_worktree(self, name: str, config: WorktreeConfig | None = None) -> Worktree:
        """创建新的 worktree"""

    def get_worktree(self, name: str) -> Worktree | None:
        """获取 worktree"""

    def list_worktrees(self) -> list[Worktree]:
        """列出所有 worktree"""

    def destroy_worktree(self, name: str) -> None:
        """销毁 worktree"""

    def switch_worktree(self, name: str) -> None:
        """切换到另一个 worktree"""

    def suspend_worktree(self, name: str) -> None:
        """暂停 worktree"""

    def resume_worktree(self, name: str) -> None:
        """恢复 worktree"""
```

### GitWorktreeManager

```python
class GitWorktreeManager(WorktreeManager):
    """扩展的 worktree 管理器，支持 git worktree 集成"""

    def create_worktree(self, name: str, config: WorktreeConfig | None = None) -> Worktree:
        """创建 git worktree（完整的 git 隔离）"""
```

### 内置 Worktree 工具

| 工具 | 功能 |
|------|------|
| `worktree_create` | 创建 worktree |
| `worktree_list` | 列出 worktree |
| `worktree_switch` | 切换 worktree |
| `worktree_destroy` | 销毁 worktree |

## 集成

### main.py 初始化

```python
from agent.core.worktree import WorktreeManager

# Initialize WorktreeManager and wire it to worktree tools (s12: Worktree + Isolation)
worktree_manager = WorktreeManager(base_dir=".worktrees")
from agent.tools.builtin.worktree_create import set_worktree_manager as set_wm_create
# ... set for all worktree tools
```

### dispatch.py 注册

```python
# Import and register worktree tools (s12: Worktree + Isolation)
from agent.tools.builtin.worktree_create import WorktreeCreateTool
from agent.tools.builtin.worktree_list import WorktreeListTool
from agent.tools.builtin.worktree_switch import WorktreeSwitchTool
from agent.tools.builtin.worktree_destroy import WorktreeDestroyTool

dispatch.register(WorktreeCreateTool())
dispatch.register(WorktreeListTool())
dispatch.register(WorktreeSwitchTool())
dispatch.register(WorktreeDestroyTool())
```

## 验证

```bash
python -c "from agent.core.worktree import WorktreeManager; print('OK')"
python -c "from agent.tools.builtin.worktree_create import WorktreeCreateTool; print('OK')"
```
