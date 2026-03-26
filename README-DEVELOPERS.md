# LOOM CLI 开发者指南

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**本指南面向 AI Agent 开发者，深度解析 LOOM CLI 的架构设计与扩展方法。**

---

## 目录

- [架构概览](#架构概览)
- [12 步代码详解](#12-步代码详解)
- [核心模块设计](#核心模块设计)
- [扩展开发指南](#扩展开发指南)
- [测试与贡献](#测试与贡献)

---

## 架构概览

### 五大架构层次

| 层次 | 名称 | 包含步骤 | 核心职责 |
|------|------|----------|----------|
| L1 | Tools & Execution | s01, s02 | 工具调度与执行 |
| L2 | Planning & Coordination | s03, s04, s05, s07 | 规划与任务协调 |
| L3 | Memory Management | s06 | 消息压缩与归档 |
| L4 | Concurrency | s08 | 后台任务处理 |
| L5 | Collaboration | s09, s10, s11, s12 | 多 Agent 协作 |

### 核心设计理念

> "The minimal agent kernel is a while loop + one tool"

每一步都在前一步基础上增加能力，但保持核心架构简洁。

---

## 12 步代码详解

| 步骤 | 名称 | 代码位置 | 核心功能 |
|------|------|----------|----------|
| s01 | Agent Loop | `agent/core/loop.py` | While 循环内核 |
| s02 | Tools | `agent/core/dispatch.py` | 工具调度映射 |
| s03 | TodoWrite | `agent/core/todo.py` | Todo 列表管理 |
| s04 | Subagents | `agent/core/subagent.py` | 子 Agent 派生 |
| s05 | Skills | `agent/skills/loader.py` | 运行时 Skill 加载 |
| s06 | Compact | `agent/core/compact.py` | 三层消息压缩 |
| s07 | Tasks | `agent/core/tasks.py` | 任务依赖图 |
| s08 | Background | `agent/core/background.py` | 后台任务处理 |
| s09 | Teams | `agent/core/teams.py` | 多 Agent 团队 |
| s10 | Protocols | `agent/core/protocols.py` | 团队协作协议 |
| s11 | Autonomous | `agent/core/autonomous.py` | 自主 Agent 治理 |
| s12 | Worktree | `agent/core/worktree.py` | Git Worktree 隔离 |

---

## 核心模块设计

### Agent Loop (`agent/core/loop.py`)

核心 While 循环内核：
1. 构建 LLM 消息
2. 调用 LLM 决策下一步
3. 执行工具（如有）
4. 返回响应

### 工具系统 (`agent/tools/`)

- **Base**: `agent/tools/base.py` 定义 `Tool`（ABC）、`ToolCall`、`ToolResult`
- **Dispatch**: `agent/core/dispatch.py` 的 `DispatchMap` 按名称路由工具调用
- **Builtin Tools**: 内置工具集（bash, read, write, glob, task_*, todo_*, team_*, board_*, background_*, worktree_*, event_*, spawn）

### 状态管理 (`agent/state/`)

- **Mailbox**: 文件-based inbox/outbox（JSONL）
- **FileStore**: 通用文件-based KV 存储
- **NotificationQueue**: 队列-based 通知系统

### 多 Agent 协作 (`agent/core/teams.py`)

- **SubagentManager**: 隔离执行的子代理
- **TeammateManager**: 邮箱-based 多代理协调
- **TaskBoard**: 文件轮询协调

---

## 扩展开发指南

### 添加新工具

**重要:** 工具在 `agent/core/dispatch.py` 的 `DispatchMap.from_directory()` 方法中注册。

1. 在 `agent/tools/builtin/` 创建 `my_tool.py`
2. 继承 `Tool` 基类，实现 `execute()` 方法
3. 在 `agent/core/dispatch.py` 的 `from_directory()` 方法中添加 import 和 `dispatch.register(MyTool())`

```python
from agent.tools.base import Tool, ToolResult

class MyTool(Tool):
    name = "my_tool"
    description = "我的工具描述"

    async def execute(self, **kwargs) -> ToolResult:
        # 实现逻辑
        return ToolResult(content="result")
```

### 添加新 Skill

在 `agent/skills/` 目录创建 Skill 文件，运行时自动加载（热重载支持）。

---

## 测试与贡献

```bash
# 运行所有测试
pytest

# 运行单个测试文件
pytest tests/test_filename.py

# 安装开发依赖
pip install -e ".[dev]"
```

### 贡献流程

1. Fork 项目
2. 创建功能分支
3. 编写测试
4. 提交 Pull Request
5. 代码审查后合并

---

## 相关文档

- 主入口: [README.md](README.md)
- 学习路径: [README-LEARNERS.md](README-LEARNERS.md)
- 用户指南: [README-USERS.md](README-USERS.md)
