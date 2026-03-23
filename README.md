# BuildAgent

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-passing-brightgreen.svg)]()

**通用 AI Agent 框架，遵循 12 步递进学习路径**

> "The minimal agent kernel is a while loop + one tool"

BuildAgent 是一个通用 AI Agent 框架，采用模块化架构设计，从简单的 Agent Loop 到复杂的多 Agent 团队协作，循序渐进地构建完整的人工智能代理能力。

---

## 目录

- [特性](#特性)
- [架构概览](#架构概览)
- [安装指南](#安装指南)
- [快速开始](#快速开始)
- [使用示例](#使用示例)
- [TODO-List](#todo-list)
- [参考内容](#参考内容)
- [许可证](#许可证)

---

## 特性

- **12 步递进架构**：从基础循环到多 Agent 协作，循序渐进
- **40+ 内置工具**：文件操作、任务管理、团队协作、后台任务等
- **4 个内置 Skill**：commit、deploy、review-pr、test
- **运行时 Skill 加载**：支持热重载的自定义 Skill 系统
- **消息压缩**：三层压缩系统，有效管理上下文长度
- **多 Agent 协作**：支持团队协作、任务看板、工作树隔离

---

## 架构概览

### 五大架构层次

| 层次 | 名称 | 包含步骤 |
|------|------|----------|
| L1 | Tools & Execution | s01, s02 |
| L2 | Planning & Coordination | s03, s04, s05, s07 |
| L3 | Memory Management | s06 |
| L4 | Concurrency | s08 |
| L5 | Collaboration | s09, s10, s11, s12 |

### 12 步总览

| 步骤 | 名称 | 代码位置 | 描述 |
|------|------|----------|------|
| s01 | Agent Loop | `agent/core/loop.py` | 核心 While 循环 |
| s02 | Tools | `agent/core/dispatch.py` | 工具调度系统 |
| s03 | TodoWrite | `agent/core/todo.py` | Todo 列表管理 |
| s04 | Subagents | `agent/core/subagent.py` | 子 Agent 派生 |
| s05 | Skills | `agent/skills/loader.py` | 运行时 Skill 加载 |
| s06 | Compact | `agent/core/compact.py` | 消息压缩系统 |
| s07 | Tasks | `agent/core/tasks.py` | 任务管理系统 |
| s08 | Background | `agent/core/background.py` | 后台任务处理 |
| s09 | Teams | `agent/core/teams.py` | 多 Agent 协作 |
| s10 | Protocols | `agent/core/protocols.py` | 团队协议 |
| s11 | Autonomous | `agent/core/autonomous.py` | 自主 Agent 治理 |
| s12 | Worktree | `agent/core/worktree.py` | Git Worktree 隔离 |

---

## 安装指南

### 前置依赖

- Python >= 3.10
- DeepSeek API Key

### 安装步骤

1. 克隆项目
```bash
git clone <repository-url>
cd BuildAgent
```

2. 创建虚拟环境（推荐）
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
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

或在环境变量中设置：
```bash
export DEEPSEEK_API_KEY=your_api_key_here  # Linux/Mac
set DEEPSEEK_API_KEY=your_api_key_here     # Windows
```

---

## 快速开始

```bash
# 启动交互式 REPL
python main.py

# 或使用简洁模式
python agent.py
```

---

## 使用示例

### 基础示例：greet.py

一个简单的问候函数示例：

**greet.py**
```python
def greet(name):
    """Return a greeting message.
    ...
    """
    return f"Hello, {name}!"

if __name__ == "__main__":
    print(greet("World"))
```

> 完整代码见项目根目录 [greet.py](greet.py)

---

## TODO-List

### 短期目标

- [ ] 增加更多内置 Skill（如代码审查、文档生成）
- [ ] 完善测试覆盖率
- [ ] 优化消息压缩算法

### 中期目标

- [ ] 实现前端可视化界面
- [ ] 支持更多 LLM Provider（Claude、Gemini 等）
- [ ] 增加更多协议支持

### 长期目标

- [ ] Web 可视化 Agent 协作界面
- [ ] 云端部署支持
- [ ] 企业级安全认证集成

---

## 参考内容

- 官方网站：https://learn.shareai.run/zh
- 官方文档：https://learn.shareai.run/zh/s01/

---

## 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。
