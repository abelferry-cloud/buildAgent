# LOOM CLI 交互模式实施计划

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**目标：** 支持通过 `.env` 文件管理 API Key，并将单次对话改为可交互的多轮 REPL 会话。

**架构：** 在 `main.py` 中添加 `.env` 加载逻辑和 REPL 循环，Agent 实例在整个会话中复用，保持上下文。

**技术栈：** Python 标准库 + `python-dotenv`

---

## Chunk 1: 环境与依赖配置

### 创建 `.env.example`

**Files:**
- Create: `D:\IDEA_Projects\LOOM-CLI\.env.example`

- [ ] **Step 1: 创建模板文件**

```env
# DeepSeek API Key
DEEPSEEK_API_KEY=your_api_key_here
```

---

### 创建 `.env` 文件

**Files:**
- Create: `D:\IDEA_Projects\LOOM-CLI\.env`

- [ ] **Step 1: 创建 `.env` 文件**

```env
DEEPSEEK_API_KEY=sk-4bd79a43012d48f580dc18879a6dd4af
```

---

### 检查并更新 `.gitignore`

**Files:**
- Create: `D:\IDEA_Projects\LOOM-CLI\.gitignore`

- [ ] **Step 1: 创建 `.gitignore`（项目无此文件）**

```
.env
__pycache__/
*.pyc
```

---

## Chunk 2: 修改 `main.py` — REPL 循环

**Files:**
- Modify: `D:\IDEA_Projects\LOOM-CLI\main.py`

- [ ] **Step 1: 重写 `main.py`**

```python
"""CLI entry point for the LOOM CLI with DeepSeek."""

import argparse
import os
import sys

from dotenv import load_dotenv

from agent.core.loop import Agent
from agent.core.dispatch import DispatchMap
from agent.llm import DeepSeekClient

# Load .env file if present
load_dotenv()


def get_api_key_from_env():
    """Get API key from .env file (load_dotenv already loaded it)."""
    return os.getenv("DEEPSEEK_API_KEY", "")


def main():
    parser = argparse.ArgumentParser(description="LOOM CLI with DeepSeek")
    parser.add_argument("--api-key", help="DeepSeek API key (optional, can use .env)")
    parser.add_argument("--model", default="deepseek-chat", help="Model name")
    parser.add_argument("--api-base", default="https://api.deepseek.com/v1", help="API base URL")
    args = parser.parse_args()

    # Resolve API key: CLI arg > .env > env var
    api_key = args.api_key or get_api_key_from_env()
    if not api_key:
        print("Error: No API key provided. Set DEEPSEEK_API_KEY in .env or pass --api-key")
        sys.exit(1)

    # Initialize LLM client
    llm_client = DeepSeekClient(
        api_key=api_key,
        model=args.model,
        api_base=args.api_base,
    )

    # Load tools
    dispatch = DispatchMap.from_directory("agent/tools/builtin")
    tools = dispatch.list_tools()

    # Create agent (one instance, reused across sessions)
    agent = Agent(
        tools=tools,
        model=args.model,
        system_prompt="You are a helpful coding assistant.",
    )
    agent.set_llm_client(llm_client)

    print("欢迎使用 LOOM CLI（DeepSeek驱动）！输入 exit 或 quit 退出。")

    session_count = 0
    while True:
        try:
            user_input = input(f"[Session #{session_count + 1}] > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再见！")
            break

        if not user_input:
            continue

        # Check exit condition
        if user_input.lower() in ("exit", "quit"):
            print("再见！")
            break

        session_count += 1

        # Run agent with user input
        result = agent.run(user_input)
        print(result)
        print()  # 空行分隔


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: 测试 REPL 模式**

```bash
cd D:\IDEA_Projects\LOOM-CLI
python main.py
```

预期：
```
欢迎使用 LOOM CLI（DeepSeek驱动）！输入 exit 或 quit 退出。
[Session #1] > 你好
[AI 回复...]
[Session #2] > 帮我写一个快速排序
[AI 回复...]
[Session #3] > exit
再见！
```

- [ ] **Step 3: 测试 API Key 加载（无参数）**

```bash
python main.py
```
预期：正常启动并加载 `.env` 中的 API Key。

- [ ] **Step 4: 测试命令行参数优先**

```bash
python main.py --api-key "sk-test"
```
预期：使用命令行参数中的 key，不使用 `.env` 中的 key。
