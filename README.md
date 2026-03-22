# BuildAgent

> 一个极简内核驱动的大型语言模型 AI Agent 框架

## 项目概述

BuildAgent 是一个遵循 **12 步递进架构** 的通用 AI Agent 实现。项目的核心理念是：

> **"The minimal agent kernel is a while loop + one tool"**
>
> 极简的 Agent 内核 = while 循环 + 一个工具

通过 12 个递进步骤逐步扩展，从一个简单的 Agent Loop 演变为支持多 Agent 团队协作的完整系统。

## 架构设计哲学

BuildAgent 的架构遵循**最小化内核 + 可扩展工具**的设计哲学：

```
┌─────────────────────────────────────────────────────┐
│                    Agent Loop                       │
│  ┌─────────────────────────────────────────────┐   │
│  │  while not done:                            │   │
│  │    1. Build messages for LLM                │   │
│  │    2. Call LLM to decide next action        │   │
│  │    3. Execute tool if needed                 │   │
│  │    4. Return response                        │   │
│  └─────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
                         │
                         ▼
        ┌────────────────────────────────┐
        │        Tool Dispatch Map       │
        │  (动态注册, 按需扩展)           │
        └────────────────────────────────┘
                         │
                         ▼
        ┌────────────────────────────────┐
        │     30+ Built-in Tools         │
        │  bash, read, write, glob       │
        │  todo_*, task_*, team_*         │
        │  background_*, board_*          │
        │  worktree_*, protocol_*         │
        └────────────────────────────────┘
```

## 12 步学习路径

项目按照 12 个步骤组织，每个步骤对应一个能力层级：

### L1: 工具与执行

| 步骤 | 名称 | 核心组件 | 说明 |
|------|------|----------|------|
| s01 | Agent Loop | `agent/core/loop.py` | 核心内核：while 循环 + 工具执行 |
| s02 | Tools | `agent/core/dispatch.py` | 动态工具注册与路由 |

### L2: 规划与协调

| 步骤 | 名称 | 核心组件 | 说明 |
|------|------|----------|------|
| s03 | TodoWrite | `agent/core/todo.py` | Todo 列表管理 + Nag 提醒机制 |
| s04 | Subagents | `agent/core/subagent.py` | 子 agent 隔离执行与消息传递 |
| s05 | Skills | `agent/skills/loader.py` | 运行时技能加载（热更新） |
| s07 | Tasks | `agent/core/tasks.py` | 任务依赖管理与拓扑排序 |

### L3: 内存管理

| 步骤 | 名称 | 核心组件 | 说明 |
|------|------|----------|------|
| s06 | Compact | `agent/core/compact.py` | 三层消息压缩：微压缩 + 自动压缩 + 归档 |

### L4: 并发

| 步骤 | 名称 | 核心组件 | 说明 |
|------|------|----------|------|
| s08 | Background | `agent/core/background.py` | 后台任务 + Context Manager 支持 |

### L5: 协作

| 步骤 | 名称 | 核心组件 | 说明 |
|------|------|----------|------|
| s09 | Teams | `agent/core/teams.py` | 多 Agent 团队 + Mailbox 通信 |
| s10 | Protocols | `agent/core/protocols.py` | 团队通信协议（shutdown/plan approval） |
| s11 | Autonomous | `agent/core/autonomous.py` | 任务看板 + 自主治理（超时/重试/升级） |
| s12 | Worktree | `agent/core/worktree.py` | Git Worktree 隔离执行 |

## 核心组件详解

### 1. Agent Loop (`agent/core/loop.py`)

Agent 的核心执行引擎：

```python
class Agent:
    async def step(self) -> AgentResponse:
        """单步执行：
        1. 构建 LLM 消息
        2. 调用 LLM 决策
        3. 执行工具
        4. 返回结果
        """
```

**关键特性**：
- 支持流式 LLM 响应
- 多工具并行调用
- 消息压缩支持
- Todo Nag 提醒注入
- 技能上下文注入（Layer 1: 名称描述 / Layer 2: 完整内容）

### 2. Tool Dispatch (`agent/core/dispatch.py`)

动态工具注册与路由系统：

```python
class DispatchMap:
    def register(self, tool: Tool) -> None: ...
    def dispatch(self, tool_name: str, params: dict) -> ToolResult: ...
    @classmethod
    def from_directory(cls, tool_dir: str, ...) -> "DispatchMap": ...
```

**内置工具分类**：

| 类别 | 工具 |
|------|------|
| 文件操作 | `bash`, `read`, `write`, `glob` |
| Todo 管理 | `todo_add`, `todo_list`, `todo_done`, `todo_start` |
| 任务管理 | `task_create`, `task_update`, `task_list`, `task_depends` |
| 后台任务 | `background_run`, `background_wait`, `background_cancel` |
| 团队通信 | `team_send`, `team_broadcast`, `team_list`, `team_status` |
| 协议消息 | `protocol_shutdown_req`, `protocol_shutdown_resp`, `protocol_plan_req`, `protocol_plan_resp` |
| 任务看板 | `board_post`, `board_poll`, `board_claim`, `board_complete` |
| Git Worktree | `worktree_create`, `worktree_list`, `worktree_switch`, `worktree_destroy` |

### 3. Multi-Agent Teams (`agent/core/teams.py`)

基于 Mailbox 的多 Agent 通信机制：

```
┌──────────────────────────────────────────────────────────┐
│                    TeammateManager                        │
├──────────────────────────────────────────────────────────┤
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐    │
│  │ Agent A │  │ Agent B │  │ Agent C │  │ Agent D │    │
│  │ Mailbox │  │ Mailbox │  │ Mailbox │  │ Mailbox │    │
│  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘    │
│       │            │            │            │          │
│       └────────────┴────────────┴────────────┘          │
│                          │                               │
│                    inbox.jsonl                          │
│                    outbox.jsonl                         │
└──────────────────────────────────────────────────────────┘
```

**消息协议类型**：
- `DIRECT`: 点对点消息
- `BROADCAST`: 广播消息
- `SHUTDOWN_REQUEST` / `SHUTDOWN_RESPONSE`: 优雅关闭协议
- `PLAN_APPROVAL_REQUEST` / `PLAN_APPROVAL_RESPONSE`: 计划审批协议

### 4. Autonomous Governor (`agent/core/autonomous.py`)

自主治理系统，包含超时管理和自我纠错：

```python
class AutonomousGovernor:
    def should_continue(self) -> bool: ...
    def check_timeouts(self) -> list[TimeoutAction]: ...
    def self_correct(self, issue: GovernanceIssue) -> None: ...
```

**超时处理策略**：
- `RETRY`: 重试（可配置重试次数）
- `SKIP`: 跳过当前任务
- `ABORT`: 中止执行
- `ESCALATE`: 升级处理

**治理问题类型**：
- `TASK_TIMEOUT`: 任务超时
- `IDLE_TIMEOUT`: 空闲超时
- `MAX_ITERATIONS`: 最大迭代次数
- `ERROR_RATE`: 错误率过高
- `RESOURCE_EXHAUSTION`: 资源耗尽

### 5. Task Board (`agent/core/autonomous.py`)

基于文件的分布式任务协调看板：

```
┌─────────────────────────────────────────────────┐
│                 TaskBoard                        │
├─────────────────────────────────────────────────┤
│  pending ──► claimed ──► completed              │
│                    │                           │
│                    └──► failed                 │
│                                                 │
│  Priority Queue + Polling Coordination         │
└─────────────────────────────────────────────────┘
```

### 6. Message Compression (`agent/core/compact.py`)

三层消息压缩系统：

| 层级 | 名称 | 触发条件 | 方式 |
|------|------|----------|------|
| L1 | Micro-compact | 每条消息 | 去除空白字符 |
| L2 | Auto-compact | 超过阈值 | 摘要旧消息 |
| L3 | Archive | 长期会话 | 归档到文件 |

## 项目结构

```
BuildAgent/
├── agent/
│   ├── core/
│   │   ├── loop.py          # Agent 核心循环
│   │   ├── dispatch.py      # 工具调度
│   │   ├── todo.py          # Todo 管理
│   │   ├── subagent.py      # 子 agent
│   │   ├── tasks.py         # 任务管理
│   │   ├── background.py    # 后台任务
│   │   ├── teams.py         # 团队管理
│   │   ├── protocols.py     # 通信协议
│   │   ├── autonomous.py    # 自主治理
│   │   ├── worktree.py      # Git Worktree
│   │   └── compact.py       # 消息压缩
│   ├── tools/
│   │   ├── base.py          # Tool 基类
│   │   └── builtin/         # 内置工具 (30+)
│   ├── state/
│   │   ├── mailbox.py       # Mailbox 通信
│   │   ├── filestore.py     # 文件存储
│   │   └── notification.py  # 通知队列
│   ├── skills/
│   │   └── loader.py        # 技能加载器
│   ├── event/
│   │   ├── emitter.py       # 事件发射器
│   │   └── stream.py        # 事件流
│   └── llm/
│       └── client.py        # LLM 客户端
├── tests/                   # 完整测试套件 (s01-s12)
├── PLAN/                    # 12 步学习路径文档
└── config/                  # 配置文件
```

## 关键设计模式

### 1. 工具注册模式
```python
# 核心循环不变，新工具注册到 DispatchMap
dispatch = DispatchMap()
dispatch.register(BashTool())
dispatch.register(ReadTool())
dispatch.register(WriteTool())
```

### 2. Mailbox 通信模式
```python
# 基于 JSONL 文件的异步消息队列
mailbox = Mailbox("path/to/mailbox")
mailbox.send(message)
messages = mailbox.receive_all()
```

### 3. 任务看板模式
```python
# 文件化的分布式协调
board = TaskBoard("board.json")
board.post_task(title="实现功能 X", priority=1)
task = board.poll(worker="agent-1")
board.complete_task(task.id)
```

### 4. 两层技能注入
```python
# Layer 1: 技能名称和描述 (~100 tokens/skill)
# Layer 2: 通过 load_skill 工具加载完整内容
```

## 技术亮点

1. **极简内核**：核心循环只有约 100 行代码
2. **动态工具系统**：30+ 内置工具，支持按需扩展
3. **多 Agent 协作**：Mailbox 机制实现松耦合通信
4. **自主治理**：超时、重试、升级策略
5. **消息压缩**：三层压缩避免上下文溢出
6. **技能热更新**：运行时加载/更新技能
7. **Git Worktree 隔离**：安全的并行执行环境

## 安装与运行

```bash
# 安装依赖
pip install -e ".[dev]"

# 运行所有测试
pytest

# 运行单个测试
pytest tests/test_s01_agent_loop.py -v

# 指定 LLM 提供者
export LLM_PROVIDER=ollama  # 或 deepseek, openai
```

## 依赖

- Python >= 3.10
- openai >= 1.0.0
- httpx >= 0.25.0
- python-dotenv >= 1.0.0

## 参考资料

- 官方学习路径：https://learn.shareai.run/zh
- 架构理念：极简 Agent 内核设计

---

**BuildAgent** — 从 100 行代码的 while 循环到完整的多 Agent 协作系统。
