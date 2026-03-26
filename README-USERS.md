# LOOM CLI 用户指南

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

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

- 主入口: [README.md](README.md)
- 开发者指南: [README-DEVELOPERS.md](README-DEVELOPERS.md)
- 学习者指南: [README-LEARNERS.md](README-LEARNERS.md)
