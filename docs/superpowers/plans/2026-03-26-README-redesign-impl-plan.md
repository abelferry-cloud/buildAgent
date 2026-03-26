# README 重写实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将现有单一 README.md 拆分为四个独立文件，分别面向开发者、学习者和普通用户。

**Architecture:** 重写 README.md 作为综合入口，创建 README-DEVELOPERS.md、README-LEARNERS.md、README-USERS.md 三个专项文档。所有文件使用统一风格，中文表述，表格/代码块辅助说明。

**Tech Stack:** Markdown 文档，无需代码。

---

## 文件概览

| 文件 | 操作 | 核心内容 |
|------|------|----------|
| README.md | 重写 | 项目简介 + 特性概览 + 导航链接 |
| README-DEVELOPERS.md | 新建 | 架构层次 + 12步详解 + 扩展开发 |
| README-LEARNERS.md | 新建 | 12步路径 + 学习目标 + 练习建议 |
| README-USERS.md | 新建 | 安装配置 + 工具速查 + 场景示例 |

---

## Task 1: 重写 README.md（综合入口）

**文件:**
- 读取: `README.md`（现有内容备份参考）
- 写入: `README.md`（重写版本）

- [ ] **Step 1: 提取现有 ASCII art Logo**

从现有 README.md 提取 ASCII art 备用。

- [ ] **Step 2: 编写新 README.md 结构**

```markdown
# LOOM CLI

[ASCII Art Logo — 复用现有]

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**通用 AI Agent 框架，遵循 12 步递进学习路径**

> "The minimal agent kernel is a while loop + one tool"

---

## 一句话介绍

LOOM CLI 是一个模块化的通用 AI Agent 框架，从简单的 Agent Loop 到复杂的多 Agent 团队协作，循序渐进地构建完整的人工智能代理能力。

---

## 特性概览

- **12 步递进架构** — 从基础循环到多 Agent 协作
- **35+ 内置工具** — 文件操作、任务管理、团队协作
- **运行时 Skill 加载** — 支持热重载的自定义 Skill
- **消息压缩系统** — 三层压缩有效管理上下文
- **多 Agent 协作** — 团队、看板、工作树隔离
- **五大架构层次** — Tools/Planning/Memory/Concurrency/Collaboration

---

## 快速导航

| 读者类型 | 文档 |
|----------|------|
| 开发者 | [README-DEVELOPERS.md](README-DEVELOPERS.md) |
| 学习者 | [README-LEARNERS.md](README-LEARNERS.md) |
| 普通用户 | [README-USERS.md](README-USERS.md) |

---

## 安装前置

- Python >= 3.10
- DeepSeek API Key

```bash
pip install -e ".[dev]"
```

详细安装说明见 [README-USERS.md](README-USERS.md#安装指南)

---

## 参考资源

- 官方网站: https://learn.shareai.run/zh
- 项目文档: [PLAN/](PLAN/)
```

- [ ] **Step 3: 验证格式并提交**

检查表格渲染、链接有效性，提交。

---

## Task 2: 创建 README-DEVELOPERS.md（开发者指南）

**文件:**
- 读取: `CLAUDE.md`（架构参考）、`PLAN/README.md`（12步参考）
- 写入: `README-DEVELOPERS.md`（新建）

- [ ] **Step 1: 编写 README-DEVELOPERS.md**

```markdown
# README-DEVELOPERS.md

# LOOM CLI 开发者指南

[徽章行]

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

- 主入口: [README.md](../README.md)
- 学习路径: [README-LEARNERS.md](./README-LEARNERS.md)
- 用户指南: [README-USERS.md](./README-USERS.md)
```

- [ ] **Step 2: 提交**

---

## Task 3: 创建 README-LEARNERS.md（学习者指南）

**文件:**
- 读取: `PLAN/README.md`、`PLAN/s*/README.md`（各步详情）
- 写入: `README-LEARNERS.md`（新建）

- [ ] **Step 1: 编写 README-LEARNERS.md**

```markdown
# README-LEARNERS.md

# LOOM CLI 学习者指南

[徽章行]

**本指南帮助你通过 LOOM CLI 项目学习 AI Agent 开发，沿着 12 步递进路径逐步深入。**

---

## 目录

- [学习路径概览](#学习路径概览)
- [12 步详解](#12-步详解)
- [学习建议](#学习建议)
- [配合官方文档](#配合官方文档)

---

## 学习路径概览

LOOM CLI 采用 12 步递进架构，每一步代表一个递进的能力层级。

| 层次 | 步骤 | 名称 | 难度 |
|------|------|------|------|
| L1 | s01-s02 | Tools & Execution | 入门 |
| L2 | s03-s07 | Planning & Coordination | 基础 |
| L3 | s06 | Memory Management | 进阶 |
| L4 | s08 | Concurrency | 进阶 |
| L5 | s09-s12 | Collaboration | 高阶 |

**推荐学习顺序:** 按 s01 → s12 顺序学习，每步完成后再进入下一步。

---

## 12 步详解

### s01: Agent Loop（Agent 循环）

**学习目标:** 理解 Agent 的核心 while 循环机制

**核心概念:**
- 消息构建
- LLM 决策调用
- 工具执行
- 响应返回

**代码位置:** `agent/core/loop.py`

**练习建议:** 修改循环逻辑，观察 Agent 行为变化。

---

### s02: Tools（工具系统）

**学习目标:** 掌握工具的定义、注册与调度

**核心概念:**
- Tool 基类
- ToolCall / ToolResult
- DispatchMap 路由

**代码位置:** `agent/tools/base.py`、`agent/core/dispatch.py`

**练习建议:** 添加一个新工具，理解注册流程。

---

### s03: TodoWrite（Todo 管理）

**学习目标:** 学习状态管理与持久化

**核心概念:**
- Todo 列表结构
- 状态变更追踪

**代码位置:** `agent/core/todo.py`

---

### s04: Subagents（子代理）

**学习目标:** 理解代理派生与隔离执行

**核心概念:**
- Subagent 创建
- 消息传递
- 隔离环境

**代码位置:** `agent/core/subagent.py`

---

### s05: Skills（技能系统）

**学习目标:** 掌握运行时 Skill 加载机制

**核心概念:**
- Skill 加载器
- 热重载
- Skill 接口

**代码位置:** `agent/skills/loader.py`

---

### s06: Compact（消息压缩）

**学习目标:** 理解上下文管理与压缩

**核心概念:**
- Micro-compact（ whitespace 移除）
- Auto-compact（摘要旧消息）
- Archive（归档到文件）

**代码位置:** `agent/core/compact.py`

---

### s07: Tasks（任务管理）

**学习目标:** 掌握任务依赖图管理

**核心概念:**
- 任务创建
- 依赖声明
- 拓扑排序

**代码位置:** `agent/core/tasks.py`

---

### s08: Background（后台任务）

**学习目标:** 理解并发与后台处理

**核心概念:**
- 后台任务提交
- 任务等待
- 任务取消

**代码位置:** `agent/core/background.py`

---

### s09: Teams（多代理团队）

**学习目标:** 掌握多代理协调机制

**核心概念:**
- TeammateManager
- 邮箱通信
- 团队角色

**代码位置:** `agent/core/teams.py`

---

### s10: Protocols（团队协议）

**学习目标:** 理解协作协议设计

**核心概念:**
- 协议定义
- 消息格式
- 协调流程

**代码位置:** `agent/core/protocols.py`

---

### s11: Autonomous（自主代理）

**学习目标:** 掌握自主代理治理

**核心概念:**
- TaskBoard 文件轮询
- 超时重试
- 升级机制

**代码位置:** `agent/core/autonomous.py`

---

### s12: Worktree（工作树隔离）

**学习目标:** 理解 Git Worktree 在 Agent 隔离中的应用

**核心概念:**
- Worktree 创建
- 分支切换
- 资源隔离

**代码位置:** `agent/core/worktree.py`

---

## 学习建议

1. **循序渐进** — 不要跳步，每步理解透彻后再继续
2. **动手实践** — 每步都尝试修改代码，观察变化
3. **配合测试** — 运行现有测试，理解预期行为
4. **阅读官方文档** — 配合 https://learn.shareai.run/zh 学习

---

## 配合官方文档

官方网站提供 12 步的详细学习内容：

- 主站: https://learn.shareai.run/zh
- 各步文档: https://learn.shareai.run/zh/sXX/（XX 为步骤号）

**建议:** 先阅读官方文档理解概念，再通过 LOOM CLI 代码加深理解。

---

## 相关文档

- 主入口: [README.md](../README.md)
- 开发者指南: [README-DEVELOPERS.md](./README-DEVELOPERS.md)
- 用户指南: [README-USERS.md](./README-USERS.md)
```

- [ ] **Step 2: 提交**

---

## Task 4: 创建 README-USERS.md（用户指南）

**文件:**
- 读取: `pyproject.toml`（依赖）、`agent/tools/builtin/`（工具列表，从 `agent/core/dispatch.py` 获取工具完整列表）
- 写入: `README-USERS.md`（新建）

- [ ] **Step 1: 收集内置工具列表**

从 `agent/core/dispatch.py` 的 `from_directory()` 方法获取完整工具列表（实际约 35 个工具）。

**注意:** README 中工具数量应如实描述为"35+ 内置工具"，而非"40+"。

- [ ] **Step 2: 编写 README-USERS.md**

```markdown
# README-USERS.md

# LOOM CLI 用户指南

[徽章行]

**本指南帮助普通用户快速上手使用 LOOM CLI。**

---

## 目录

- [安装指南](#安装指南)
- [快速开始](#快速开始)
- [交互模式 vs 简洁模式](#交互模式-vs-简洁模式)
- [工具速查](#工具速查)
- [使用场景](#使用场景)

---

## 安装指南

### 前置依赖

- Python >= 3.10
- DeepSeek API Key

### 安装步骤

1. 克隆项目
```bash
git clone <repository-url>
cd LOOM-CLI
```

2. 创建虚拟环境（推荐）
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# 或
source venv/bin/activate  # Linux/Mac
```

3. 安装依赖
```bash
pip install -e ".[dev]"
```

4. 配置 API Key

创建 `.env` 文件：
```bash
DEEPSEEK_API_KEY=your_api_key_here
```

---

## 快速开始

### 交互模式（完整功能）

```bash
python main.py
```

### 简洁模式

```bash
python agent.py
```

### 常用命令

| 命令 | 说明 |
|------|------|
| `python main.py` | 启动交互式 REPL |
| `python agent.py` | 简洁模式启动 |
| `pytest` | 运行所有测试 |
| `pip install -e ".[dev]"` | 安装开发依赖 |

---

## 交互模式 vs 简洁模式

| 特性 | 交互模式 (`main.py`) | 简洁模式 (`agent.py`) |
|------|----------------------|----------------------|
| 完整功能 | ✅ | ✅ |
| ASCII art Logo | ✅ | ❌ |
| Rich 输出美化 | ✅ | ❌ |
| 状态显示 | ✅ | ❌ |
| 详细日志 | ✅ | ❌ |

**推荐:** 日常使用交互模式，开发调试用简洁模式。

启动后你会看到 ASCII art Logo，然后可以输入自然语言指令。

**示例会话：**
```
> 分析一下当前目录下的文件结构
> 创建一个新任务
> 帮我写一个 hello world 函数
```

---

## 工具速查

### 文件操作（4 个）

| 工具 | 说明 |
|------|------|
| bash | 执行 Bash 命令 |
| read | 读取文件内容 |
| write | 写入文件内容 |
| glob | 文件模式匹配 |

### 任务管理（4 个）

| 工具 | 说明 |
|------|------|
| task_create | 创建新任务 |
| task_update | 更新任务状态 |
| task_list | 列出所有任务 |
| task_depends | 设置任务依赖 |

### Todo 管理（4 个）

| 工具 | 说明 |
|------|------|
| todo_add | 添加 Todo |
| todo_list | 列出 Todos |
| todo_done | 标记完成 |
| todo_start | 开始 Todo |

### 团队协作（4 个）

| 工具 | 说明 |
|------|------|
| team_send | 发送消息给队友 |
| team_broadcast | 广播消息 |
| team_list | 列出团队成员 |
| team_status | 查看成员状态 |

### 任务看板（4 个）

| 工具 | 说明 |
|------|------|
| board_post | 发布任务到看板 |
| board_poll | 轮询看板 |
| board_claim | 认领任务 |
| board_complete | 完成任务 |

### 后台任务（3 个）

| 工具 | 说明 |
|------|------|
| background_run | 后台运行任务 |
| background_wait | 等待任务完成 |
| background_cancel | 取消任务 |

### 工作树（4 个）

| 工具 | 说明 |
|------|------|
| worktree_create | 创建工作树 |
| worktree_list | 列出工作树 |
| worktree_switch | 切换工作树 |
| worktree_destroy | 销毁工作树 |

### 事件（2 个）

| 工具 | 说明 |
|------|------|
| event_subscribe | 订阅事件 |
| event_list | 列出事件 |

### 子代理 & 协议（6 个）

| 工具 | 说明 |
|------|------|
| spawn | 派生子代理 |
| load_skill | 加载 Skill |
| protocol_shutdown_req | 关闭请求协议 |
| protocol_shutdown_resp | 关闭响应协议 |
| protocol_plan_req | 计划请求协议 |
| protocol_plan_resp | 计划响应协议 |

**共计: 35+ 内置工具**

---

## 使用场景

### 场景 1: 文件操作

```
> 分析当前项目的结构
> 帮我读取 main.py 的内容
> 创建一个新文件 hello.py
```

### 场景 2: 任务管理

```
> 创建一个实现登录功能的任务
> 再创建一个相关的测试任务
> 设置测试任务依赖登录任务
> 查看当前所有任务
```

### 场景 3: 团队协作

```
> 启动一个子代理来分析代码
> 给团队成员发送消息
> 查看团队状态
```

### 场景 4: 后台任务

```
> 在后台运行性能测试
> 等待测试完成
> 取消一个正在运行的任务
```

---

## 相关文档

- 主入口: [README.md](../README.md)
- 开发者指南: [README-DEVELOPERS.md](./README-DEVELOPERS.md)
- 学习者指南: [README-LEARNERS.md](./README-LEARNERS.md)
```

- [ ] **Step 3: 验证并提交**

---

## 验收标准

1. 四个 README 文件均存在且格式正确
2. README.md 作为入口包含导航到其他三个文档
3. 每个文档针对其目标读者，内容完整
4. 链接有效，无死链
5. 表格渲染正确
```

- [ ] **Step 3: 提交计划文档**

---

## Task 5: 实施与验收

**前置:** Task 1-4 全部完成

- [ ] **Step 1: 运行验收检查**

1. 确认四个文件都存在
```bash
ls -la README.md README-DEVELOPERS.md README-LEARNERS.md README-USERS.md
```

2. 验证 README.md 链接到其他三个文档
```bash
grep -c "README-DEVELOPERS.md\|README-LEARNERS.md\|README-USERS.md" README.md
```
预期: 每个文件名至少出现 1 次

3. 检查表格格式（确认表格用 | 分隔，行数正确）

4. 验证工具数量（README-DEVELOPERS.md 和 README-USERS.md 都应列出 ~35 个工具）

5. 验证无死链接（README.md 中的链接都指向存在的文件）

- [ ] **Step 2: 最终提交**

将所有更改一起提交：
```bash
git add README.md README-DEVELOPERS.md README-LEARNERS.md README-USERS.md
git commit -m "docs: split README into four targeted documents for developers, learners, and users"
```
