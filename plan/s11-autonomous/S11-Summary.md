# S11: Autonomous Agents - 总结

## 核心理念

> Task board for polling-based coordination with self-governance

## 核心原理

S11 实现了任务看板系统，支持轮询协调和自主治理。

### TaskBoard 功能

- **发布任务** - `post_task()` 向看板添加任务
- **轮询任务** - `poll()` 获取最高优先级任务（原子性 claim）
- **认领任务** - `claim_task()` 指定 ID 认领
- **完成任务** - `complete_task()` 标记完成
- **状态过滤** - 按状态/worker 筛选任务

### AutonomousGovernor 治理

- **超时检测** - 检测任务超时、空闲超时、最大迭代数
- **行动执行** - 支持 RETRY / SKIP / ABORT / ESCALATE
- **自我修正** - `self_correct()` 尝试自动恢复

## 关键类/组件

| 名称 | 文件 | 职责 |
|------|------|------|
| `BoardTask` | `agent/core/autonomous.py` | 看板上任务的数据结构 |
| `BoardState` | `agent/core/autonomous.py` | 看板状态统计 |
| `TaskBoard` | `agent/core/autonomous.py` | 轮询式任务协调板 |
| `AutonomousGovernor` | `agent/core/autonomous.py` | 超时/治理逻辑 |

## 涉及的文件

### 核心文件
- `agent/core/autonomous.py` - TaskBoard 和 AutonomousGovernor

### 工具文件
- `agent/tools/builtin/board_post.py` - BoardPostTool
- `agent/tools/builtin/board_poll.py` - BoardPollTool
- `agent/tools/builtin/board_claim.py` - BoardClaimTool
- `agent/tools/builtin/board_complete.py` - BoardCompleteTool

## 与 main.py 的集成

```python
from agent.core.autonomous import TaskBoard

task_board = TaskBoard(board_file=".taskboard.json")
from agent.tools.builtin.board_post import set_board as set_board_post
from agent.tools.builtin.board_poll import set_board as set_board_poll
from agent.tools.builtin.board_claim import set_board as set_board_claim
from agent.tools.builtin.board_complete import set_board as set_board_complete

set_board_post(task_board)
set_board_poll(task_board)
set_board_claim(task_board)
set_board_complete(task_board)
```

## 工具列表

| 工具名 | 类 | 功能 |
|--------|-----|------|
| `board_post` | BoardPostTool | 向看板发布新任务 |
| `board_poll` | BoardPollTool | 轮询获取最高优先级任务（原子认领） |
| `board_claim` | BoardClaimTool | 认领指定 ID 的任务 |
| `board_complete` | BoardCompleteTool | 标记任务完成 |

## 架构图

```
┌─────────────────────────────────────────┐
│           TaskBoard                     │
│  ┌───────────────────────────────────┐  │
│  │ _board_file: str                 │  │
│  │ _tasks: dict[str, BoardTask]     │  │
│  │ _file_lock: FileLock             │  │
│  └───────────────────────────────────┘  │
│  post_task() │ poll() │ claim_task() │
│  complete_task() │ fail_task()        │
└─────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│        .taskboard.json (持久化)         │
│  ┌───────────────────────────────────┐  │
│  │ {                                 │  │
│  │   "tasks": [...],                 │  │
│  │   "version": 1                   │  │
│  │ }                                 │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘

轮询流程 (poll):
  Worker A ─── poll() ───► TaskBoard
                         ├──► 返回最高优先级 pending 任务
                         └──► atomically claim 该任务

多 Worker 协调:
  Worker A ─── poll() ──┐
  Worker B ─── poll() ──┼──► TaskBoard (原子操作)
  Worker C ─── poll() ──┘     └──► 只有一个能成功 claim
```

## BoardTask 数据结构

```python
@dataclass
class BoardTask:
    id: str
    title: str
    description: str
    priority: int
    status: TaskStatus  # PENDING / CLAIMED / COMPLETED / FAILED
    worker: str | None   # 认领者
    created_at: float
    updated_at: float
    completed_at: float | None
    result: str | None   # 完成结果
```
