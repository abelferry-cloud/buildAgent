# BuildAgent

一个遵循 12 步递进架构的通用 AI Agent。

## 概述

BuildAgent 实现了一个极简的 Agent 内核（"while loop + one tool"），通过 12 个递进步骤逐步扩展为完整的多 Agent 协作系统。

## 架构

12 步学习路径构建了 5 大架构层次：

| 层次 | 名称 | 包含步骤 |
|------|------|----------|
| L1 | 工具与执行 | s01, s02 |
| L2 | 规划与协调 | s03, s04, s05, s07 |
| L3 | 内存管理 | s06 |
| L4 | 并发 | s08 |
| L5 | 协作 | s09, s10, s11, s12 |

### 12 个步骤

| 步骤 | 名称 | 核心组件 |
|------|------|----------|
| s01 | Agent Loop | `agent/core/loop.py` |
| s02 | Tools | `agent/core/dispatch.py` |
| s03 | TodoWrite | `agent/core/todo.py` |
| s04 | Subagents | `agent/core/subagent.py` |
| s05 | Skills | `agent/skills/loader.py` |
| s06 | Compact | `agent/core/compact.py` |
| s07 | Tasks | `agent/core/tasks.py` |
| s08 | Background Tasks | `agent/core/background.py` |
| s09 | Agent Teams | `agent/core/teams.py` |
| s10 | Team Protocols | `agent/core/protocols.py` |
| s11 | Autonomous Agents | `agent/core/autonomous.py` |
| s12 | Worktree + Isolation | `agent/core/worktree.py` |

## 安装

```bash
pip install -e ".[dev]"
```

## 使用

```bash
# 运行所有测试
pytest

# 运行单个测试文件
pytest tests/test_s01_agent_loop.py

# 以详细模式运行
pytest -v
```

## 项目结构

```
BuildAgent/
├── agent/
│   ├── core/          # 核心组件（loop、dispatch 等）
│   ├── tools/         # 工具系统及内置工具
│   ├── state/         # 状态管理（mailbox、file store）
│   ├── skills/        # 技能加载系统
│   ├── event/         # 事件发射器和流
│   ├── protocols/     # 团队通信协议
│   └── llm/           # LLM 集成
├── config/            # 配置
├── tests/             # 测试套件（s01-s12）
└── PLAN/              # 12 步学习路径文档
```

## 文档

官方文档：https://learn.shareai.run/zh

## 环境要求

- Python >= 3.10
- openai >= 1.0.0
- httpx >= 0.25.0
- python-dotenv >= 1.0.0
