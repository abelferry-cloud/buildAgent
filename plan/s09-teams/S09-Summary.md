# S09: Agent Teams - 总结

## 核心理念

> Multi-agent team coordination with mailbox-based communication

## 核心原理

S09 实现了多代理团队协调系统，代理被组织成团队，通过邮箱机制进行消息传递。

### 团队架构

- **团队身份** - 每个团队有唯一 ID（如 "main"）
- **邮箱通信** - 基于文件的邮箱系统（inbox.jsonl / outbox.jsonl）
- **状态管理** - 跟踪队友状态（IDLE / BUSY / OFFLINE）
- **消息类型** - 支持 DIRECT / BROADCAST / REQUEST / RESPONSE

### Mailbox 机制

- **Inbox** - 接收其他代理的消息
- **Outbox** - 发送消息到其他代理
- **持久化** - JSONL 格式，支持消息追溯

## 关键类/组件

| 名称 | 文件 | 职责 |
|------|------|------|
| `TeammateStatus` | `agent/core/teams.py` | 队友状态枚举 |
| `AgentConfig` | `agent/core/teams.py` | 代理配置（model, system_prompt, tools） |
| `TeammateInfo` | `agent/core/teams.py` | 队友信息 |
| `TeammateManager` | `agent/core/teams.py` | 团队管理器 |
| `Mailbox` | `agent/state/mailbox.py` | 邮箱实现 |

## 涉及的文件

### 核心文件
- `agent/core/teams.py` - TeammateManager 实现
- `agent/state/mailbox.py` - Mailbox 邮箱实现

### 工具文件
- `agent/tools/builtin/team_send.py` - TeamSendTool
- `agent/tools/builtin/team_broadcast.py` - TeamBroadcastTool
- `agent/tools/builtin/team_list.py` - TeamListTool
- `agent/tools/builtin/team_status.py` - TeamStatusTool

## 与 main.py 的集成

```python
from agent.core.teams import TeammateManager

teammate_manager = TeammateManager(team_id="main", mailbox_dir=".mailbox")
from agent.tools.builtin.team_send import set_teammate_manager as set_team_send_manager
from agent.tools.builtin.team_broadcast import set_teammate_manager as set_team_broadcast_manager
from agent.tools.builtin.team_list import set_teammate_manager as set_team_list_manager
from agent.tools.builtin.team_status import set_teammate_manager as set_team_status_manager

set_team_send_manager(teammate_manager)
set_team_broadcast_manager(teammate_manager)
set_team_list_manager(teammate_manager)
set_team_status_manager(teammate_manager)
```

## 工具列表

| 工具名 | 类 | 功能 |
|--------|-----|------|
| `team_send` | TeamSendTool | 向指定队友发送私信 |
| `team_broadcast` | TeamBroadcastTool | 向所有队友广播消息 |
| `team_list` | TeamListTool | 列出所有队友 |
| `team_status` | TeamStatusTool | 获取/设置队友状态 |

## 架构图

```
┌─────────────────────────────────────────┐
│        TeammateManager                  │
│  ┌───────────────────────────────────┐  │
│  │ _team_id: str                     │  │
│  │ _mailbox_dir: str                 │  │
│  │ _teammates: dict[str, TeammateInfo]│  │
│  │ _mailbox: Mailbox                 │  │
│  └───────────────────────────────────┘  │
│  send_message() │ broadcast() │ list_teammates()
└─────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│         Mailbox (agent/state/)          │
│  ┌───────────────────────────────────┐  │
│  │ inbox.jsonl   (接收消息)           │  │
│  │ outbox.jsonl  (发送消息)          │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘

消息流转:
Agent A  ─── send_message() ───►  Agent B
              │
              ▼
           Mailbox
              │
              ▼
         inbox.jsonl
```

## 消息类型

| 类型 | 说明 |
|------|------|
| `DIRECT` | 点对点私信 |
| `BROADCAST` | 广播给所有队友 |
| `REQUEST` | 请求（期待响应） |
| `RESPONSE` | 响应（回复请求） |
