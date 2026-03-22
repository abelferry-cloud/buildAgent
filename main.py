"""CLI entry point for the BuildAgent with DeepSeek."""

import argparse
import asyncio
import os
import sys

from dotenv import load_dotenv

from agent.core.loop import Agent
from agent.core.dispatch import DispatchMap
from agent.llm import DeepSeekClient

# Load .env file if present (override existing env vars to ensure .env takes precedence)
load_dotenv(override=True)


def get_api_key_from_env():
    """Get API key from .env file (load_dotenv already loaded it)."""
    return os.getenv("DEEPSEEK_API_KEY", "")


async def main():
    parser = argparse.ArgumentParser(description="BuildAgent with DeepSeek")
    parser.add_argument("--api-key", help="DeepSeek API key (optional, can use .env)")
    parser.add_argument("--model", default="deepseek-chat", help="Model name")
    parser.add_argument("--api-base", default="https://api.deepseek.com", help="API base URL")
    args = parser.parse_args()

    # Resolve API key: CLI arg > .env > env var
    api_key = args.api_key or get_api_key_from_env()
    print(f"[DEBUG] API Key loaded: {api_key[:10]}..." if api_key else "[DEBUG] No API key loaded")
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

    print("欢迎使用 BuildAgent（DeepSeek驱动）！输入 exit 或 quit 退出。")

    session_count = 0
    try:
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

            # Run agent with user input (async)
            result = await agent.run(user_input)
            print(result)
            print()  # 空行分隔
    finally:
        # Clean up async client
        await llm_client.close()


if __name__ == "__main__":
    asyncio.run(main())
