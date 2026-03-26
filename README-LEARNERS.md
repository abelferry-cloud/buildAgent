# LOOM CLI 学习者指南

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

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

- 主入口: [README.md](README.md)
- 开发者指南: [README-DEVELOPERS.md](README-DEVELOPERS.md)
- 用户指南: [README-USERS.md](README-USERS.md)
