# README 重写设计方案

## 概述

将现有的单一 README.md 拆分为四个独立的 README 文件，分别针对开发者、学习者和普通用户，同时保留一个综合入口文件。

## 文件结构

```
README.md              # 综合入口
README-DEVELOPERS.md   # 开发者指南
README-LEARNERS.md      # 学习者指南
README-USERS.md         # 用户指南
```

## 设计决策

### 1. 文件命名与定位

| 文件 | 目标读者 | 核心定位 |
|------|----------|----------|
| README.md | 所有访问者 | 项目门面：简介 + 导航 |
| README-DEVELOPERS.md | AI Agent 开发者 | 架构深度 + 扩展开发 |
| README-LEARNERS.md | 学习者 | 12 步路径 + 练习指南 |
| README-USERS.md | CLI 用户 | 命令速查 + 使用场景 |

### 2. 内容分层策略

**README.md（综合入口）**
- ASCII art Logo（保留现有）
- 一句话项目描述
- 核心特性（6 项要点）
- 快速导航徽章/链接
- 安装前置说明
- 简洁的目录索引

**README-DEVELOPERS.md（开发者指南）**
- 五大架构层次详解
- 12 步代码位置与职责
- 核心模块说明：
  - Agent Loop (`agent/core/loop.py`)
  - 工具系统 (`agent/tools/`)
  - 多 Agent 协作 (`agent/core/teams.py`)
  - 状态管理 (`agent/state/`)
- 扩展开发指南
- 测试与贡献流程

**README-LEARNERS.md（学习者指南）**
- 12 步学习路径总览
- 每步详细说明：
  - 学习目标
  - 核心概念
  - 练习建议
- 学习顺序推荐
- 与官方文档配合方式
- 学习资源链接

**README-USERS.md（用户指南）**
- 安装与配置（详细步骤）
- 交互模式 vs 简洁模式
- 40+ 内置工具速查表
- 常用场景示例：
  - 文件操作
  - 任务管理
  - 团队协作
  - 后台任务

### 3. 风格规范

- **语言**：统一使用中文
- **格式**：适当使用表格、代码块、徽章
- **基调**：专业清晰，不过度装饰
- **导航**：README.md 作为入口，详细内容引导至各专属文档

## 待产出文件

1. `README.md` — 重写为综合入口
2. `README-DEVELOPERS.md` — 新建
3. `README-LEARNERS.md` — 新建
4. `README-USERS.md` — 新建

## 实施步骤

1. 重写 `README.md` 为简洁的综合入口
2. 创建 `README-DEVELOPERS.md`
3. 创建 `README-LEARNERS.md`
4. 创建 `README-USERS.md`
