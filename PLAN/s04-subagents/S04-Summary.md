# S04: Subagents - 总结

## 核心理念

> Isolated agents with message passing, not shared state

## 核心原理

S04 实现了子代理系统，每个子代理是独立的 Agent 实例，通过消息传递进行通信，而不是共享状态。

### Subagent 系统设计

- **生命周期管理** - SubagentManager 负责创建、追踪和终止子代理
- **消息传递** - 子代理之间通过 send/receive 机制通信
- **工具隔离** - 每个子代理可拥有不同的工具列表
- **Agent 注入** - 通过 `inject_agent()` 将 SubagentManager 与 Agent Loop 连接

### 核心流程

1. **Spawn** - 创建新的子代理，获得唯一 ID
2. **Send** - 向指定子代理发送消息
3. **Receive** - 从子代理接收待处理消息
4. **Terminate** - 优雅地终止子代理

## 关键类/组件

| 名称 | 文件 | 职责 |
|------|------|------|
| `Subagent` | `agent/core/subagent.py` | 子代理数据结构 |
| `SubagentManager` | `agent/core/subagent.py` | 子代理生命周期管理 |

## 涉及的文件

### 核心文件
- `agent/core/subagent.py` - SubagentManager 实现

### 工具文件
- `agent/tools/builtin/spawn.py` - SpawnTool，子代理创建工具

## 与 main.py 的集成

```python
from agent.core.subagent import SubagentManager

subagent_manager = SubagentManager()

# DispatchMap 加载时需要
dispatch = DispatchMap.from_directory("agent/tools/builtin", subagent_manager, skill_loader)

# Spawn 工具会使用 subagent_manager
# from agent.tools.builtin.spawn import SpawnTool
# dispatch.register(SpawnTool(subagent_manager))
```

## SpawnTool 参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `name` | str | 子代理名称 |
| `role` | str | 子代理角色描述 |
| `tools` | list[str] | 可用工具列表 |

## 架构图

```
┌─────────────────────────────────────────┐
│          SubagentManager               │
│  ┌─────────────────────────────────┐   │
│  │ _subagents: dict[str, Subagent] │   │
│  │ _agent: Agent (main)            │   │
│  └─────────────────────────────────┘   │
│  spawn() │ send() │ receive() │ terminate()
└─────────────────────────────────────────┘
              ▲
              │ inject_agent()
              │
┌─────────────┴─────────────┐
│        Agent Loop        │
│    (主 Agent 实例)        │
└───────────────────────────┘

┌─────────────┐    send/recv    ┌─────────────┐
│  Subagent 1 │ ◄─────────────► │  Subagent 2 │
│  (独立状态) │                 │  (独立状态) │
└─────────────┘                 └─────────────┘
```
