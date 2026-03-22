# BuildAgent 12 步学习路径

## 概述

BuildAgent 是一个通用 AI Agent，遵循 12 步学习路径架构。每一步代表一个递进的能力层级，从简单的 Agent Loop 到复杂的多 Agent 团队协作。

## 12 步总览

| 步骤 | 名称 | 代码位置 | 状态 |
|------|------|----------|------|
| [s01](./s01-agent-loop/) | Agent Loop | `agent/core/loop.py` | ✅ 完成（已测试） |
| [s02](./s02-tools/) | Tools | `agent/core/dispatch.py` | ✅ 完成（已测试） |
| [s03](./s03-todowrite/) | TodoWrite | `agent/core/todo.py` | ✅ 完成（已测试） |
| [s04](./s04-subagents/) | Subagents | `agent/core/subagent.py` | ✅ 完成（已测试） |
| [s05](./s05-skills/) | Skills | `agent/skills/loader.py` | ✅ 完成（已测试） |
| [s06](./s06-compact/) | Compact | `agent/core/compact.py` | ❌ 未完成 |
| [s07](./s07-tasks/) | Tasks | `agent/core/tasks.py` | ❌ 未完成 |
| [s08](./s08-background/) | Background Tasks | `agent/core/background.py` | ❌ 未完成 |
| [s09](./s09-teams/) | Agent Teams | `agent/core/teams.py` | ❌ 未完成 |
| [s10](./s10-protocols/) | Team Protocols | `agent/core/protocols.py` | ❌ 未完成 |
| [s11](./s11-autonomous/) | Autonomous Agents | `agent/core/autonomous.py` | ❌ 未完成 |
| [s12](./s12-worktree/) | Worktree + Isolation | `agent/core/worktree.py` | ❌ 未完成 |

## 五大架构层次

| 层次 | 名称 | 包含步骤 |
|------|------|----------|
| L1 | Tools & Execution | s01, s02 |
| L2 | Planning & Coordination | s03, s04, s05, s07 |
| L3 | Memory Management | s06 |
| L4 | Concurrency | s08 |
| L5 | Collaboration | s09, s10, s11, s12 |

## 核心理念

> "The minimal agent kernel is a while loop + one tool"

每一步都在前一步的基础上增加能力，但保持核心架构的简洁。

## 官方网站

参考文档: https://learn.shareai.run/zh
