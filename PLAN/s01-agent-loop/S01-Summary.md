# S01: Agent Loop - 总结

## 核心理念

> "The minimal agent kernel is a while loop + one tool"

## 核心原理

S01 是 BuildAgent 的核心内核，实现了最基本的 Agent Loop 模式。Agent 通过一个 while 循环持续运行，每次循环包含以下步骤：

1. **构建消息** - 将对话历史组织成 LLM 可处理的格式
2. **LLM 决策** - 调用 LLM 决定下一步行动（思考或执行工具）
3. **工具执行** - 如果 LLM 决定执行工具，通过 DispatchMap 路由到对应工具
4. **返回结果** - 将工具执行结果返回给 LLM，继续下一轮循环

### 关键设计

- **流式输出支持** - `_llm_step()` 支持流式 LLM 调用
- **工具调用解析** - `_parse_tool_calls()` 能处理 JSON 代码块和原始 JSON 格式的工具调用
- **Nag Reminder** - 超过3轮未使用 todo 工具时，自动提醒用户更新任务列表

## 关键类/组件

| 名称 | 文件 | 职责 |
|------|------|------|
| `Message` | `agent/core/loop.py` | 消息数据结构，包含 role, content, tool_calls 等 |
| `AgentResponse` | `agent/core/loop.py` | Agent 步骤执行结果封装 |
| `Agent` | `agent/core/loop.py` | 核心 Agent 类，实现 while loop 内核 |

## 涉及的文件

### 核心文件
- `agent/core/loop.py` - Agent Loop 核心实现
- `main.py` - 入口文件，创建并运行 Agent

### 工具基类
- `agent/tools/base.py` - Tool ABC 和 ToolCall/ToolResult 定义

## 与 main.py 的集成

```python
from agent.core.loop import Agent

agent = Agent(
    tools=tools,
    model=args.model,
    system_prompt="You are a helpful coding assistant.",
    todo_manager=todo_manager,
    skill_loader=skill_loader,
)
agent.set_llm_client(llm_client)

# 运行 Agent
result = await agent.run(user_input)
```

## 架构图

```
用户输入
    │
    ▼
┌─────────────────┐
│   Agent.run()   │
│  (async loop)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  _llm_step()   │ ◄──── LLM API (DeepSeek)
│  (决策)         │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│_parse_tool_calls│
│  (解析工具调用)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ execute_tool()  │ ────► DispatchMap.dispatch()
│  (执行工具)      │      (s02: Tools)
└────────┬────────┘
         │
         ▼
      返回结果
```
