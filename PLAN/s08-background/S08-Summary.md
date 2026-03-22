# S08: Background Tasks - 总结

## 核心理念

> Async job execution with status tracking and daemon thread event loop

## 核心原理

S08 实现了后台任务执行系统，通过守护线程运行独立的 asyncio 事件循环来管理异步任务。

### 核心机制

- **守护线程** - BackgroundManager 在初始化时启动一个守护线程
- **独立事件循环** - 守护线程运行自己的 asyncio 事件循环
- **线程池执行** - 同步函数通过线程池执行
- **状态追踪** - 每个后台任务有独立的状态（RUNNING, COMPLETED, FAILED, CANCELLED）
- **通知队列** - 使用 NotificationQueue 传递任务事件

### 异步执行流程

1. **run_in_background()** - 接收协程引用，创建后台任务
2. **守护线程** - 在独立事件循环中调度协程执行
3. **状态更新** - STARTED → COMPLETED/FAILED
4. **通知** - 通过 NotificationQueue 发送事件

## 关键类/组件

| 名称 | 文件 | 职责 |
|------|------|------|
| `JobStatus` | `agent/core/background.py` | 任务状态枚举 |
| `BackgroundJob` | `agent/core/background.py` | 后台任务数据结构 |
| `BackgroundManager` | `agent/core/background.py` | 后台任务管理器 |

## 涉及的文件

### 核心文件
- `agent/core/background.py` - BackgroundManager 实现

### 工具文件
- `agent/tools/builtin/background_run.py` - BackgroundRunTool
- `agent/tools/builtin/background_wait.py` - BackgroundWaitTool
- `agent/tools/builtin/background_cancel.py` - BackgroundCancelTool

### 状态管理
- `agent/state/notification.py` - NotificationQueue 通知队列

## 与 main.py 的集成

```python
from agent.core.background import BackgroundManager

background_manager = BackgroundManager()
from agent.tools.builtin.background_run import set_background_manager as set_bg_run
from agent.tools.builtin.background_wait import set_background_manager as set_bg_wait
from agent.tools.builtin.background_cancel import set_background_manager as set_bg_cancel

set_bg_run(background_manager)
set_bg_wait(background_manager)
set_bg_cancel(background_manager)
```

## 工具列表

| 工具名 | 类 | 功能 |
|--------|-----|------|
| `background_run` | BackgroundRunTool | 启动后台任务（name, coro_ref） |
| `background_wait` | BackgroundWaitTool | 等待任务完成（job_id, timeout?） |
| `background_cancel` | BackgroundCancelTool | 取消运行中的任务 |

## 架构图

```
┌─────────────────────────────────────────┐
│        BackgroundManager                │
│  ┌─────────────────────────────────┐   │
│  │ _loop: asyncio.new_event_loop() │   │
│  │ _thread: daemon thread         │   │
│  │ _jobs: dict[str, BackgroundJob] │   │
│  │ _notifications: NotificationQueue│  │
│  └─────────────────────────────────┘   │
│  run_in_background_sync() │ wait()     │
└─────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│         Daemon Thread                   │
│  ┌─────────────────────────────────┐   │
│  │  asyncio event loop            │   │
│  │  (running forever)             │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│       Thread Pool Executor              │
│  ┌─────────────────────────────────┐   │
│  │  sync_func_1  │  sync_func_2    │   │
│  │  (in threads) │  (in threads)   │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

## 状态转换

```
创建任务
    │
    ▼
[RUNNING] ─── cancel() ───► [CANCELLED]
    │
    ├── complete() ───► [COMPLETED]
    │
    └── exception ───► [FAILED]
```
