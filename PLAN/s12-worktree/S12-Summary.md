# S12: Worktree + Isolation - 总结

## 核心理念

> "Each works in its own directory; tasks manage goals, worktrees manage directories, bound by ID"

## 核心原理

S12 实现了工作树生命周期管理系统，提供目录级别的隔离。

### 两种工作树模式

1. **WorktreeManager** - 基础工作树管理
   - 目录隔离
   - 状态持久化
   - 暂停/恢复

2. **GitWorktreeManager** - Git 工作树集成
   - 真正的 Git worktree
   - `git worktree add -b`
   - `git worktree remove`
   - 非 Git 仓库时回退到普通目录

### 生命周期

- **CREATING** → **ACTIVE** → **SUSPENDED** / **DESTROYING** → **DESTROYED**

## 关键类/组件

| 名称 | 文件 | 职责 |
|------|------|------|
| `WorktreeState` | `agent/core/worktree.py` | 状态枚举 |
| `WorktreeConfig` | `agent/core/worktree.py` | 配置（branch, tools, memory, cpu） |
| `Worktree` | `agent/core/worktree.py` | 工作树数据结构 |
| `WorktreeManager` | `agent/core/worktree.py` | 基础工作树管理 |
| `GitWorktreeManager` | `agent/core/worktree.py` | Git 工作树集成 |

## 涉及的文件

### 核心文件
- `agent/core/worktree.py` - WorktreeManager 和 GitWorktreeManager

### 工具文件
- `agent/tools/builtin/worktree_create.py` - WorktreeCreateTool
- `agent/tools/builtin/worktree_list.py` - WorktreeListTool
- `agent/tools/builtin/worktree_switch.py` - WorktreeSwitchTool
- `agent/tools/builtin/worktree_destroy.py` - WorktreeDestroyTool

## 与 main.py 的集成

```python
from agent.core.worktree import WorktreeManager

worktree_manager = WorktreeManager(base_dir=".worktrees")
from agent.tools.builtin.worktree_create import set_worktree_manager as set_wm_create
from agent.tools.builtin.worktree_list import set_worktree_manager as set_wm_list
from agent.tools.builtin.worktree_switch import set_worktree_manager as set_wm_switch
from agent.tools.builtin.worktree_destroy import set_worktree_manager as set_wm_destroy

set_wm_create(worktree_manager)
set_wm_list(worktree_manager)
set_wm_switch(worktree_manager)
set_wm_destroy(worktree_manager)
```

## 工具列表

| 工具名 | 类 | 功能 |
|--------|-----|------|
| `worktree_create` | WorktreeCreateTool | 创建新工作树 |
| `worktree_list` | WorktreeListTool | 列出所有工作树 |
| `worktree_switch` | WorktreeSwitchTool | 切换活动上下文 |
| `worktree_destroy` | WorktreeDestroyTool | 销毁工作树 |

## WorktreeConfig 数据结构

```python
@dataclass
class WorktreeConfig:
    branch: str | None          # Git 分支名
    tools: list[str] | None    # 可用工具列表
    memory_limit_mb: int | None # 内存限制
    cpu_limit_percent: int | None # CPU 限制
```

## 架构图

```
┌─────────────────────────────────────────┐
│        WorktreeManager                  │
│  ┌───────────────────────────────────┐  │
│  │ _base_dir: str                    │  │
│  │ _worktrees: dict[str, Worktree]   │  │
│  │ _active: str | None               │  │
│  │ _state_file: str                  │  │
│  └───────────────────────────────────┘  │
│  create_worktree() │ switch_worktree() │
│  suspend_worktree() │ resume_worktree()│
└─────────────────────────────────────────┘
              │
              ▼ (GitWorktreeManager extends)
┌─────────────────────────────────────────┐
│       GitWorktreeManager                │
│  ┌───────────────────────────────────┐  │
│  │ create_worktree() ─ git worktree add│
│  │ destroy_worktree() ─ git worktree remove│
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│           .worktrees/                   │
│  ┌───────────────────────────────────┐  │
│  │ worktree_name_1/                 │  │
│  │   ├── .worktree_info.json        │  │
│  │   └── (isolated files)           │  │
│  │ worktree_name_2/                 │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘

隔离级别:
┌─────────────────────────────────────────┐
│     主工作目录 (main)                    │
│  ├── .worktrees/                        │
│  │   ├── feature_a/  (worktree 1)       │
│  │   └── feature_b/  (worktree 2)       │
│  └── (独立文件)                          │
└─────────────────────────────────────────┘
```

## 状态转换

```
create_worktree()
       │
       ▼
    [CREATING] ──完成──► [ACTIVE]
                          │
       ┌──────────────────┼──────────────────┐
       │                  │                  │
       ▼                  ▼                  ▼
suspend_worktree()   switch_worktree()  destroy_worktree()
       │                  │                  │
       ▼                  │                  ▼
  [SUSPENDED] ──resume──► [ACTIVE] ──────► [DESTROYING] ──► [DESTROYED]
```
