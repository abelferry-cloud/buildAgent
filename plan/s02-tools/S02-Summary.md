# S02: Tools (Dispatch Map) - 总结

## 核心理念

> "The loop stays the same; new tools register into the dispatch map"

## 核心原理

S02 实现了工具的动态注册和路由分发机制。核心是 `DispatchMap` 类，它维护了工具名称到工具实例的映射。

### 工具注册流程

1. **定义工具** - 创建继承自 `Tool` ABC 的类
2. **实现 execute()** - 编写工具的具体逻辑
3. **注册工具** - 调用 `dispatch.register(tool_instance)`
4. **工具分发** - 通过 `dispatch.dispatch(tool_name, params)` 执行

### DispatchMap 核心方法

- `register(tool)` - 按名称注册工具
- `dispatch(tool_name, params)` - 根据名称和参数执行工具
- `list_tools()` / `list_tool_names()` - 列出所有工具
- `get_tool(name)` / `has_tool(name)` - 查询工具
- `from_directory()` - 从目录自动加载所有内置工具

## 关键类/组件

| 名称 | 文件 | 职责 |
|------|------|------|
| `Tool` | `agent/tools/base.py` | 工具抽象基类，定义 name, description, execute() |
| `ToolCall` | `agent/tools/base.py` | 工具调用数据结构 |
| `ToolResult` | `agent/tools/base.py` | 工具执行结果 |
| `DispatchMap` | `agent/core/dispatch.py` | 工具注册与分发中心 |

## 涉及的文件

### 核心文件
- `agent/core/dispatch.py` - DispatchMap 实现
- `agent/tools/base.py` - Tool 基类定义

### 内置工具
- `agent/tools/builtin/bash.py` - BashTool，执行 shell 命令
- `agent/tools/builtin/read.py` - ReadTool，读取文件
- `agent/tools/builtin/write.py` - WriteTool，写入文件
- `agent/tools/builtin/glob.py` - GlobTool，文件模式匹配

## 与 main.py 的集成

```python
from agent.core.dispatch import DispatchMap

dispatch = DispatchMap.from_directory("agent/tools/builtin", subagent_manager, skill_loader)
tools = dispatch.list_tools()

# 分发工具调用
result = dispatch.dispatch("bash", {"command": "ls -la"})
```

## 架构图

```
┌─────────────────────────────────────────┐
│              DispatchMap                │
│  ┌─────────────────────────────────┐   │
│  │  _tools: dict[str, Tool]       │   │
│  │  "bash"   -> BashTool()        │   │
│  │  "read"   -> ReadTool()        │   │
│  │  "write"  -> WriteTool()       │   │
│  │  "glob"   -> GlobTool()        │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
            ▲              │
            │ register    │ dispatch
            │              ▼
┌───────────────────┐  ┌─────────────────┐
│   Tool subclasses │  │  execute_tool() │
│   (继承 Tool ABC)  │  │  (loop.py)      │
└───────────────────┘  └─────────────────┘
```
